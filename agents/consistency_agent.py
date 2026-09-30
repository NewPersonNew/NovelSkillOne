# -*- coding: utf-8 -*-
__author__ = "gezhaoqiang"
__date__ = "2026/8/28"

# agents/consistency_agent.py
import json
from typing import List, Dict, Any
from infrastructure.llm_client import LLMClient
from memory.db_manager import DatabaseManager


class ConsistencyAgent:
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.llm = LLMClient()
        self.db = DatabaseManager(project_name)

    def check_chapter(self, chapter_num: int, content: str) -> List[str]:
        """
        检查单章是否存在逻辑矛盾。
        返回警告列表，空列表表示无问题。
        """
        # 获取该角色已有的所有事实（作为背景知识）
        protagonist = self._get_protagonist()
        existing_facts = self.db.get_facts(entity=protagonist, limit=50)
        all_facts = self.db.get_facts(limit=100)

        # 构建事实摘要
        fact_summary = []
        for f in all_facts:
            fact_summary.append(f"{f['entity']}的{f['attribute']}是{f['value']}（第{f['chapter']}章确认）")
        fact_context = "\n".join(fact_summary[-20:])  # 只取最近20条避免上下文过长

        prompt = f"""
        请审核以下小说章节是否存在与已确认事实的矛盾。

        【已确认事实（只读参考）】
        {fact_context}

        【待审核章节内容（片段）】
        {content[:2000]}

        【审核任务】
        1. 检查角色实力/等级是否出现不合理倒退或跳跃。
        2. 检查角色所在地点是否突然跳跃（如无合理解释）。
        3. 检查是否提及已死亡/已离开的角色且无合理解释。
        4. 检查时间线是否清晰，是否存在逻辑倒置。

        【输出格式】
        如果无问题，输出 "PASS"。
        如果有问题，列出每条问题，用 "WARNING: ..." 开头，每行一条。
        """

        response = self.llm.generate(prompt, system_prompt="你是一位严谨的小说逻辑校对专家。", temperature=0.1)
        warnings = [line.strip() for line in response.split('\n') if line.strip().startswith('WARNING:')]
        return warnings if warnings else []

    def _get_protagonist(self) -> str:
        """从设定中获取主角名"""
        import json
        from infrastructure.file_manager import FileManager
        fm = FileManager()
        setting = fm.load_json(self.project_name, "settings.json")
        return setting.get('protagonist', {}).get('name', '主角')

    def close(self):
        self.db.close()