# -*- coding: utf-8 -*-
__author__ = "gezhaoqiang"
__date__ = "2026/8/28"

# agents/foreshadowing_agent.py
from typing import List, Dict
from infrastructure.llm_client import LLMClient
from memory.db_manager import DatabaseManager


class ForeshadowingAgent:
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.llm = LLMClient()
        self.db = DatabaseManager(project_name)

    def scan_promises(self, start_chapter: int = 1, end_chapter: int = None) -> Dict:
        """
        扫描指定范围章节，识别：
        1. 哪些承诺已自然被回收（但数据库未标记）
        2. 哪些章节埋下了新承诺但未记录
        3. 哪些承诺长期未回收（警告）
        """
        active = self.db.get_active_promises()
        if not active:
            return {"info": "当前无活跃伏笔需要追踪"}

        # 构建承诺摘要
        promise_summary = [f"[{i}] {p['description']}（埋于第{p['planted_chapter']}章）" for i, p in enumerate(active)]
        prompt = f"""
        请分析以下活跃伏笔/承诺的回收情况。

        【活跃伏笔列表】
        {chr(10).join(promise_summary)}

        【分析任务】
        1. 哪些承诺在当前已生成的章节中可能已经被回收（但未标记）？
        2. 哪些承诺已经超过建议回收章节仍未回收？
        3. 如果某个承诺的描述与某章内容高度相关，给出建议。

        【输出格式】
        用简洁的列表输出建议，每条以 "建议:" 开头。
        """
        response = self.llm.generate(prompt, system_prompt="你是专业的小说伏笔管理专家。", temperature=0.3)
        return {
            "raw_response": response,
            "suggestions": [line.strip() for line in response.split('\n') if line.strip().startswith('建议:')]
        }

    def analyze_chapter_promises(self, chapter_num: int, content: str) -> List[str]:
        """
        分析本章埋下了哪些新承诺，返回描述列表。
        这是对 _extract_promises_from_chapter 的增强版本。
        """
        prompt = f"""
        请从以下章节中识别所有新出现的承诺、伏笔或暗示。

        章节内容（片段）：
        {content[:2000]}

        输出 JSON 数组，每个元素包含 description（承诺描述）和 expected_chapter（如果提到了预计回收章节）。
        如果没有新承诺，输出空数组 []。
        只输出 JSON：
        """
        try:
            response = self.llm.generate(prompt, system_prompt="你是情节分析师。", temperature=0.1)
            import re, json
            match = re.search(r'\[.*\]', response, re.DOTALL)
            if match:
                data = json.loads(match.group())
                return [d['description'] for d in data if 'description' in d]
            return []
        except:
            return []

    def close(self):
        self.db.close()