# -*- coding: utf-8 -*-
__author__ = "gezhaoqiang"
__date__ = "2026/8/28"

# core/chapter_generator.py
import os
import json
import re
import yaml
from typing import Dict, Any, Optional, List
from infrastructure.llm_client import LLMClient
from infrastructure.file_manager import FileManager
from core.setting_builder import SettingBuilder
from core.outline_generator import OutlineGenerator
from memory.state_tracker import StateTracker
from memory.vector_retriever import VectorRetriever
from memory.db_manager import DatabaseManager
from orchestration.context_assembler import ContextAssembler


class ChapterGenerator:
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.llm = LLMClient()
        self.file_manager = FileManager()
        self.setting_builder = SettingBuilder()
        self.outline_generator = OutlineGenerator()

        # --- 原有记忆模块（保留，逐步迁移） ---
        self.state_tracker = StateTracker(project_name)
        self.vector_retriever = VectorRetriever(project_name)

        # --- 新增记忆模块（结构化存储） ---
        self.db = DatabaseManager(project_name)
        self.assembler = ContextAssembler(project_name)

        # 加载提示词
        self.outline_prompt = self._load_prompt("chapter_outline.yaml")
        self.draft_prompt = self._load_prompt("chapter_draft.yaml")

        # 加载项目和设定数据
        self.setting = self.setting_builder.load_existing_setting(project_name)
        self.outline = self.outline_generator.load_existing_outline(project_name)

        if not self.setting or not self.outline:
            raise FileNotFoundError(f"项目 {project_name} 的设定或大纲不完整，请先运行设定和目录生成器。")

    def _load_prompt(self, filename: str) -> Dict[str, str]:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        prompt_path = os.path.join(base_dir, "config", "prompts", filename)
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _clean_json_response(self, raw_text: str) -> str:
        """清洗 LLM 返回的文本，提取纯 JSON"""
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', raw_text, re.DOTALL)
        if json_match:
            return json_match.group(1).strip()
        brace_match = re.search(r'(\{.*\})', raw_text, re.DOTALL)
        if brace_match:
            return brace_match.group(1).strip()
        return raw_text.strip()

    def _format_context_for_prompt(self, context: Dict) -> str:
        """将组装好的上下文 dict 格式化为 LLM 可读的文本块"""
        lines = []
        # 世界观
        lines.append("【世界观设定】")
        lines.append(context.get('world_rules', '')[:500])
        lines.append("")

        # 角色状态
        lines.append("【角色当前状态】")
        for name, info in context.get('characters', {}).items():
            profile = info.get('profile', {})
            state = info.get('current_state', {})
            desc = f"{name}: {profile.get('personality', '')} | 当前状态: {state.get('status', '正常')}"
            lines.append(f"- {desc}")
        lines.append("")

        # 活跃伏笔
        lines.append("【待回收伏笔】")
        for p in context.get('active_promises', []):
            lines.append(f"- {p['description']} (埋于第{p['planted_chapter']}章)")
        lines.append("")

        # 近期事实（简要）
        lines.append("【近期重要事实】")
        for f in context.get('recent_facts', [])[-5:]:
            lines.append(f"- {f['entity']} 的 {f['attribute']} 为 {f['value']} (第{f['chapter']}章)")
        lines.append("")

        return "\n".join(lines)

    def _extract_facts_from_chapter(self, content: str, chapter_num: int) -> List[Dict]:
        """使用 LLM 提取本章中的关键事实，返回列表 [{'entity':, 'attribute':, 'value':}]"""
        prompt = f"""
        请从以下小说章节中提取关键事实（角色属性、事件结果、重要物品获得等）。
        只提取明确陈述的事实，不要推断。
        输出格式为 JSON 数组，每个元素包含 entity, attribute, value 三个字段。
        如果没有事实，输出空数组 []。

        章节内容（截取前 3000 字符）：
        {content[:3000]}

        输出 JSON（只输出 JSON 数组，不要其他文字）：
        """
        try:
            response = self.llm.generate(prompt, system_prompt="你是一位严谨的信息提取助手。", temperature=0.1)
            print(f"   [调试] 事实提取 LLM 原始响应:\n{response[:200]}...")
            cleaned = self._clean_json_response(response)
            facts = json.loads(cleaned)
            if isinstance(facts, list):
                # 验证每个元素是否包含必要字段
                valid_facts = []
                for f in facts:
                    if all(k in f for k in ('entity', 'attribute', 'value')):
                        valid_facts.append(f)
                    else:
                        print(f"   ⚠️ 跳过格式错误的事实: {f}")
                return valid_facts
            else:
                print("   ⚠️ 返回的不是数组，尝试将其转换为单个事实...")
                if isinstance(facts, dict):
                    return [facts]  # 如果返回的是单个对象，包装为列表
                return []
        except json.JSONDecodeError as e:
            print(f"   ❌ JSON 解析失败: {e}")
            print(f"   原始响应片段: {response[:300]}")
            return []
        except Exception as e:
            print(f"   ❌ 事实提取异常: {e}")
            return []

    def _extract_promises_from_chapter(self, content: str, chapter_num: int) -> List[Dict]:
        """提取本章中埋下的新伏笔/承诺，返回列表 [{'description':, 'expected_chapter': (可选)}]"""
        prompt = f"""
        请从以下小说章节中识别出任何新出现的承诺、誓言、未解之谜或伏笔。
        这些通常是角色立下的目标、提出的疑问、或暗示未来会发生的事情。
        只提取明确表达的新承诺，不要重复已有的。
        输出 JSON 数组，每个元素包含 description（必须）和 expected_chapter（如果明确提到预计回收章节，否则填 null）。
        如果没有，输出空数组 []。

        章节内容（截取前 3000 字符）：
        {content[:3000]}

        输出 JSON（只输出 JSON 数组，不要其他文字）：
        """
        try:
            response = self.llm.generate(prompt, system_prompt="你是一位敏锐的情节分析师。", temperature=0.1)
            print(f"   [调试] 承诺提取 LLM 原始响应:\n{response[:200]}...")
            cleaned = self._clean_json_response(response)
            promises = json.loads(cleaned)
            if isinstance(promises, list):
                # 确保每个元素都有 description
                valid = [p for p in promises if 'description' in p and p['description'].strip()]
                return valid
            else:
                if isinstance(promises, dict) and 'description' in promises:
                    return [promises]
                return []
        except json.JSONDecodeError as e:
            print(f"   ❌ JSON 解析失败: {e}")
            print(f"   原始响应片段: {response[:300]}")
            return []
        except Exception as e:
            print(f"   ❌ 承诺提取异常: {e}")
            return []

    def generate_chapter(self, chapter_num: int, user_guidance: str = "") -> Dict[str, Any]:
        """
        生成指定章节的完整流程。
        :param chapter_num: 章节号（从1开始）
        :param user_guidance: 用户对本章的额外指导（可选）
        :return: 包含草稿文本和元数据的字典
        """
        print(f"\n✍️ 开始生成第 {chapter_num} 章...")

        # 1. 获取本章大纲信息
        chapters = self.outline.get('chapters', [])
        if chapter_num > len(chapters):
            raise ValueError(f"大纲只有 {len(chapters)} 章，无法生成第 {chapter_num} 章。")

        chapter_meta = chapters[chapter_num - 1]
        title = chapter_meta['title']
        summary = chapter_meta['summary']

        # 2. 获取组装后的上下文（新记忆系统）
        context = self.assembler.assemble(chapter_num)
        state_context = self._format_context_for_prompt(context)
        historical_context = "\n".join(context.get('previous_summaries', [])) if context.get(
            'previous_summaries') else "（暂无前情提要）"

        # 3. （可选）仍保留旧版向量检索作为补充
        vector_context = self.vector_retriever.get_retrieved_context_prompt(
            query=f"第{chapter_num}章：{summary}",
            top_k=2
        )
        if vector_context and "（暂无相关历史章节可参考）" not in vector_context:
            historical_context += f"\n\n【向量检索补充】\n{vector_context}"

        # 4. 准备设定 JSON 字符串
        setting_json = json.dumps(self.setting, ensure_ascii=False, indent=2)

        # ====== 阶段一：生成场景大纲 ======
        print("   📝 阶段 1/2：构思场景大纲...")
        outline_prompt_text = self.outline_prompt['user_prompt_template'].format(
            setting=setting_json,
            chapter_num=chapter_num,
            chapter_title=title,
            chapter_summary=summary,
            state_context=state_context,
            historical_context=historical_context
        )
        system_prompt = self.outline_prompt['system_prompt']

        try:
            raw_outline = self.llm.generate(
                prompt=outline_prompt_text,
                system_prompt=system_prompt,
                temperature=0.7
            )
            cleaned_outline = self._clean_json_response(raw_outline)
            scenes_data = json.loads(cleaned_outline)
        except Exception as e:
            print(f"   ❌ 场景大纲生成失败: {e}")
            raise

        # ====== 阶段二：生成正文 ======
        print("   ✍️ 阶段 2/2：扩写正文...")
        scene_outline_text = json.dumps(scenes_data, ensure_ascii=False, indent=2)
        style = self.setting.get('style', '生动细腻')
        total_words = self.setting.get('word_count', 100000)
        target_words = total_words // len(chapters) if len(chapters) > 0 else 3000

        # 获取待回收伏笔（从数据库获取最新列表）
        pending_promises = self.db.get_active_promises()
        foreshadowing_list = [f"[伏笔#{p['id']}] {p['description']}" for p in pending_promises]
        foreshadowing_text = "\n".join(foreshadowing_list) if foreshadowing_list else "（暂无待回收伏笔）"

        draft_prompt_text = self.draft_prompt['user_prompt_template'].format(
            setting=setting_json,
            scene_outline=scene_outline_text,
            state_context=state_context,
            foreshadowing=foreshadowing_text,
            target_words=target_words,
            style=style
        )
        system_prompt_draft = self.draft_prompt['system_prompt']

        try:
            draft_content = self.llm.generate(
                prompt=draft_prompt_text,
                system_prompt=system_prompt_draft,
                temperature=0.85,
                max_tokens=4096
            )
        except Exception as e:
            print(f"   ❌ 正文生成失败: {e}")
            raise

        # ====== 保存草稿 ======
        filename = f"chapter_{chapter_num}.txt"
        self.file_manager.save_text(self.project_name, f"chapters/{filename}", draft_content)
        print(f"   💾 草稿已保存至 data/{self.project_name}/chapters/{filename}")

        # 保存场景大纲（调试用）
        self.file_manager.save_json(
            self.project_name,
            f"scene_outline_{chapter_num}.json",
            scenes_data
        )

        return {
            "chapter_num": chapter_num,
            "title": title,
            "summary": summary,
            "content": draft_content,
            "scenes": scenes_data,
            "file_path": f"data/{self.project_name}/chapters/{filename}"
        }

    def finalize_chapter(self, chapter_num: int, content: str = None):
        """
        用户确认章节无误后，更新记忆层（包括新旧两套系统）。
        """
        print(f"\n🔒 正在定稿第 {chapter_num} 章，更新长期记忆...")

        if content is None:
            content = self.file_manager.load_text(
                self.project_name,
                f"chapters/chapter_{chapter_num}.txt"
            )
            if not content:
                print("   ❌ 未找到章节内容，请先生成。")
                return

        # ----- 更新旧版记忆（StateTracker + VectorRetriever）-----
        # 1. 生成摘要
        print("   📋 生成章节摘要...")
        summary_prompt = f"请用一句话（50字以内）概括以下章节的核心事件：\n\n{content[:2000]}"
        summary = self.llm.generate(summary_prompt, system_prompt="你是一位图书编辑，擅长提炼核心内容。", temperature=0.5)

        # 2. 更新剧情节点
        self.state_tracker.add_plot_point(chapter_num, summary, is_major=(chapter_num % 5 == 0))

        # 3. 向量化入库
        key_events = content[:500].replace('\n', ' ')
        self.vector_retriever.add_chapter_summary(chapter_num, summary, key_events)

        # 4. 尝试更新角色状态（旧系统）
        print("   🧑‍🤝‍🧑 更新角色状态（旧系统）...")
        state_update_prompt = f"""
        根据本章内容，提取角色状态的变更（仅提取有明显变化的角色）。
        第{chapter_num}章内容摘要：{summary}
        原始内容片段：{content[:1500]}

        输出严格的 JSON，key 为角色名，value 为状态变更描述（如："境界提升至筑基期"、"身受重伤"）。
        如果没有明显变化，输出空对象 {{}}。
        """
        try:
            raw_update = self.llm.generate(state_update_prompt, system_prompt="你是小说数据分析师。", temperature=0.3)
            clean_update = self._clean_json_response(raw_update)
            updates = json.loads(clean_update)
            for name, desc in updates.items():
                self.state_tracker.update_character(name, {"status_update": desc})
        except:
            print("   ⚠️ 角色状态自动更新失败（旧系统），请稍后手动更新。")

        # ----- 更新新记忆系统（SQLite）-----
        print("   💾 写入结构化记忆数据库...")

        # 提取事实
        facts = self._extract_facts_from_chapter(content, chapter_num)
        if facts:
            for fact in facts:
                self.db.insert_fact(
                    entity=fact.get('entity'),
                    attribute=fact.get('attribute'),
                    value=fact.get('value'),
                    chapter=chapter_num
                )
            print(f"      ✅ 已记录 {len(facts)} 条事实。")
            # 打印前两条示例
            for f in facts[:2]:
                print(f"         - {f['entity']} 的 {f['attribute']} = {f['value']}")
        else:
            print("      ℹ️ 未提取到明确事实（可能本章为过渡章节，事实较少）。")

        # 提取新承诺
        promises = self._extract_promises_from_chapter(content, chapter_num)
        if promises:
            for promise in promises:
                self.db.upsert_promise(
                    description=promise.get('description'),
                    planted_chapter=chapter_num,
                    expected_chapter=promise.get('expected_chapter')
                )
            print(f"      ✅ 已记录 {len(promises)} 条新伏笔/承诺。")
            for p in promises[:2]:
                print(f"         - {p['description']}")
        else:
            print("      ℹ️ 未检测到新承诺（可能本章没有埋下新的伏笔）。")

        # 更新角色档案（从设定和当前状态）
        # 可从 setting 中提取所有角色名，然后更新动态状态
        # 这里简单处理：从设定中获取主角和配角
        protagonist = self.setting.get('protagonist', {}).get('name')
        if protagonist:
            # 获取旧系统的状态作为动态状态
            old_state = self.state_tracker.get_character(protagonist)
            self.db.upsert_character(
                name=protagonist,
                profile=self.setting.get('protagonist', {}),
                state=old_state,
                chapter=chapter_num
            )
        for sup in self.setting.get('supporting_characters', []):
            name = sup.get('name')
            if name:
                old_state = self.state_tracker.get_character(name)
                self.db.upsert_character(
                    name=name,
                    profile=sup,
                    state=old_state,
                    chapter=chapter_num
                )

        # 检查是否有伏笔可以被回收（简单规则：如果伏笔描述中的关键词出现在本章内容中，提示用户）
        print("   🔍 检查伏笔回收...")
        active = self.db.get_active_promises()
        if active:
            for p in active:
                if p['description'] in content:
                    print(
                        f"      ⚠️ 检测到伏笔#{p['id']}可能在本文中被回收，请人工确认后调用 resolve_promise({p['id']}, {chapter_num})")
        else:
            print("      当前无活跃伏笔。")

        # 注意：我们需要在 ContextAssembler 中关闭数据库连接，但这里不关闭，因为可能还需使用。
        # 可以在外部统一关闭，或者每个方法调用后关闭。为安全起见，我们不在此关闭。

        print(f"✅ 第 {chapter_num} 章定稿完成，记忆已更新（新旧系统同步）。")