# -*- coding: utf-8 -*-
__author__ = "gezhaoqiang"
__date__ = "2026/8/28"

# consistency_checker.py
import re
import json
from typing import List, Dict, Any
from infrastructure.llm_client import LLMClient
from infrastructure.file_manager import FileManager


class ConsistencyChecker:
    """
    小说一致性审查器
    检查：角色名混淆、战力/等级冲突、已死角色复活、时间线错乱
    """

    def __init__(self, project_name: str):
        self.project_name = project_name
        self.llm = LLMClient()
        self.file_manager = FileManager()
        self.setting = self.file_manager.load_json(project_name, "settings.json")
        self.outline = self.file_manager.load_json(project_name, "outline.json")

    def check_chapter(self, chapter_num: int) -> List[str]:
        """
        检查指定章节是否存在内部逻辑矛盾。
        返回警告列表。
        """
        content = self.file_manager.load_text(
            self.project_name,
            f"chapters/chapter_{chapter_num}.txt"
        )
        if not content:
            return [f"第 {chapter_num} 章不存在，请先生成。"]

        # 获取前几章的摘要（用于上下文比较）
        previous_summaries = []
        for i in range(max(1, chapter_num - 3), chapter_num):
            summary_file = f"scene_outline_{i}.json"  # 我们保存了每章的大纲
            summary = self.file_manager.load_json(self.project_name, summary_file)
            if summary:
                previous_summaries.append(f"第{i}章大纲：{json.dumps(summary, ensure_ascii=False)[:300]}")

        prev_context = "\n".join(previous_summaries) if previous_summaries else "（无前情提要）"

        prompt = f"""
        请审查以下小说章节是否存在逻辑矛盾或设定冲突。

        【项目设定】
        {json.dumps(self.setting, ensure_ascii=False, indent=2)[:1000]}

        【前情提要（近3章大纲）】
        {prev_context}

        【待审查章节正文】
        {content[:3000]}

        【审查任务】
        检查以下方面：
        1. 角色名字是否与设定一致？有没有出现名字写错/张冠李戴？
        2. 角色实力/等级是否出现不合理跳跃？（如：上一章炼气期，这一章突然金丹）
        3. 是否提到某个已死/已离开的角色突然出现且无合理解释？
        4. 时间线是否清晰？是否存在倒置？

        【输出格式】
        如果没有问题，输出 "无异常"。
        如果有问题，用列表格式输出每一条问题，每条一行。
        """

        try:
            response = self.llm.generate(prompt, system_prompt="你是一位严谨的小说校对编辑。", temperature=0.3)
            issues = [line.strip() for line in response.split('\n') if line.strip() and '无异常' not in line]
            return issues if issues else ["✅ 本章一致性检查通过！"]
        except Exception as e:
            return [f"⚠️ 检查失败: {e}"]

    def check_all(self) -> Dict[int, List[str]]:
        """检查所有已生成的章节"""
        results = {}
        chapters = self.file_manager.list_chapters(self.project_name)
        for ch_file in chapters:
            ch_num = int(re.search(r'chapter_(\d+)\.txt', ch_file).group(1))
            results[ch_num] = self.check_chapter(ch_num)
        return results

    def report_summary(self) -> str:
        """生成一份简要的一致性报告"""
        results = self.check_all()
        total_issues = sum(len(issues) for issues in results.values() if issues)
        lines = [
            f"📊 一致性检查报告 - 项目: {self.project_name}",
            f"   已检查章节数: {len(results)}",
            f"   发现潜在问题: {total_issues} 处"
        ]
        for ch_num, issues in results.items():
            if issues and issues != ["✅ 本章一致性检查通过！"]:
                lines.append(f"   - 第 {ch_num} 章:")
                for issue in issues:
                    lines.append(f"       • {issue}")
        return "\n".join(lines)