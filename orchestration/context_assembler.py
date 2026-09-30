# -*- coding: utf-8 -*-
__author__ = "gezhaoqiang"
__date__ = "2026/8/28"

# orchestration/context_assembler.py
import json
from memory.db_manager import DatabaseManager
from infrastructure.file_manager import FileManager

class ContextAssembler:
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.db = DatabaseManager(project_name)
        self.file_manager = FileManager()
        self.setting = self.file_manager.load_json(project_name, "settings.json") or {}
        self.outline = self.file_manager.load_json(project_name, "outline.json") or {}

    def assemble(self, chapter_num: int, target_entities: list = None, recent_chapters: int = 3) -> dict:
        """组装写前上下文"""
        context = {}

        # 1. 世界观设定（几乎不变）
        context['world_rules'] = self.setting.get('world_setting', '')

        # 2. 角色档案（只加载目标实体，如果未指定则从大纲中推断）
        if not target_entities:
            # 从本章大纲中提取出现的角色（简化处理：从章节摘要中猜测）
            chapter_meta = self.outline.get('chapters', [])[chapter_num-1] if chapter_num <= len(self.outline.get('chapters', [])) else {}
            target_entities = self._extract_entities(chapter_meta.get('summary', ''))
        character_profiles = {}
        for entity in target_entities:
            char = self.db.get_character(entity)
            if char:
                character_profiles[entity] = {
                    'profile': char['profile'],
                    'current_state': char['current_state']
                }
        context['characters'] = character_profiles

        # 3. 活跃的承诺（伏笔）
        context['active_promises'] = self.db.get_active_promises()

        # 4. 最近N章的事实摘要（从facts中提取）
        recent_facts = self.db.get_facts(chapter=chapter_num, limit=recent_chapters*5)  # 限制条目
        context['recent_facts'] = recent_facts

        # 5. 获取之前章节的摘要（从存储中读取）
        summaries = []
        for i in range(max(1, chapter_num-recent_chapters), chapter_num):
            summary = self.file_manager.load_text(self.project_name, f"chapters/chapter_{i}.txt")[:200] if self.file_manager.load_text(self.project_name, f"chapters/chapter_{i}.txt") else ''
            if summary:
                summaries.append(f"第{i}章片段: {summary}")
        context['previous_summaries'] = summaries

        return context

    def _extract_entities(self, text: str) -> list:
        """简易实体提取（可以后续改进为NLP）"""
        # 假设每章大纲中角色名以“【】”或“，角色名”形式出现，简单用字符串匹配
        # 为了演示，我们只返回设定中的主角名和已知配角名
        known = []
        protagonist = self.setting.get('protagonist', {}).get('name', '')
        if protagonist:
            known.append(protagonist)
        for char in self.setting.get('supporting_characters', []):
            if 'name' in char:
                known.append(char['name'])
        # 实际可以结合正则提取，这里简化
        return known

    def close(self):
        self.db.close()