# -*- coding: utf-8 -*-
__author__ = "gezhaoqiang"
__date__ = "2026/8/27"

# memory/state_tracker.py
import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from infrastructure.file_manager import FileManager


class StateTracker:
    """
    管理小说的动态状态：角色发展、剧情节点、伏笔池。
    所有数据以 JSON 形式持久化存储。
    """

    def __init__(self, project_name: str):
        self.project_name = project_name
        self.file_manager = FileManager()

        # 定义三个核心文件的路径（相对于 data/project_name/）
        self.character_state_file = "character_state.json"
        self.plot_checkpoints_file = "plot_checkpoints.json"
        self.foreshadowing_file = "foreshadowing_pool.json"

        # 初始化或加载现有数据
        self.character_state = self._load_or_create(self.character_state_file, {})
        self.plot_checkpoints = self._load_or_create(self.plot_checkpoints_file, [])
        self.foreshadowing_pool = self._load_or_create(self.foreshadowing_file, [])

    def _load_or_create(self, filename: str, default: Any) -> Any:
        """加载 JSON，如果不存在则返回默认值并立即保存"""
        data = self.file_manager.load_json(self.project_name, filename)
        if not data:
            self.file_manager.save_json(self.project_name, filename, default)
            return default
        return data

    def _save_all(self):
        """原子化保存所有状态（确保一致性）"""
        self.file_manager.save_json(self.project_name, self.character_state_file, self.character_state)
        self.file_manager.save_json(self.project_name, self.plot_checkpoints_file, self.plot_checkpoints)
        self.file_manager.save_json(self.project_name, self.foreshadowing_file, self.foreshadowing_pool)

    # ==================== 角色状态管理 ====================
    def update_character(self, name: str, updates: Dict[str, Any]):
        """更新或创建角色的状态（如：等级、位置、HP、人际关系）"""
        if name not in self.character_state:
            self.character_state[name] = {"first_appearance": datetime.now().isoformat()}
        self.character_state[name].update(updates)
        self._save_all()

    def get_character(self, name: str) -> Dict[str, Any]:
        """获取单个角色的最新状态"""
        return self.character_state.get(name, {})

    def get_all_characters_summary(self) -> str:
        """生成供 LLM 提示词使用的角色状态摘要"""
        if not self.character_state:
            return "暂无角色状态。"
        lines = ["当前角色状态列表："]
        for name, state in self.character_state.items():
            # 过滤掉内部字段，只展示关键描述
            desc = state.get("description") or state.get("status") or state.get("level") or ""
            lines.append(f"- {name}: {desc}")
        return "\n".join(lines)

    # ==================== 剧情节点管理 ====================
    def add_plot_point(self, chapter_num: int, event_summary: str, is_major: bool = False):
        """记录一个已发生的剧情事件"""
        point = {
            "chapter": chapter_num,
            "timestamp": datetime.now().isoformat(),
            "summary": event_summary,
            "is_major": is_major
        }
        self.plot_checkpoints.append(point)
        self._save_all()

    def get_recent_plot_points(self, limit: int = 10) -> List[str]:
        """获取最近 N 个剧情节点（用于提示词）"""
        recent = self.plot_checkpoints[-limit:] if len(self.plot_checkpoints) > limit else self.plot_checkpoints
        return [f"第{p['chapter']}章: {p['summary']}" for p in recent]

    # ==================== 伏笔管理（核心特性） ====================
    def add_foreshadowing(self, description: str, expected_chapter: int = None):
        """埋下一个伏笔"""
        item = {
            "id": len(self.foreshadowing_pool) + 1,
            "description": description,
            "planted_chapter": len(self.plot_checkpoints) + 1,  # 粗略估计
            "expected_chapter": expected_chapter,
            "resolved": False,
            "resolved_chapter": None
        }
        self.foreshadowing_pool.append(item)
        self._save_all()
        return item["id"]

    def resolve_foreshadowing(self, foreshadowing_id: int, chapter_num: int):
        """回收一个伏笔（当它在某章被揭示时调用）"""
        for item in self.foreshadowing_pool:
            if item["id"] == foreshadowing_id and not item["resolved"]:
                item["resolved"] = True
                item["resolved_chapter"] = chapter_num
                self._save_all()
                return True
        return False

    def get_pending_foreshadowing(self) -> List[str]:
        """获取所有未回收的伏笔（提醒 AI 在后续章节回收）"""
        pending = [item for item in self.foreshadowing_pool if not item["resolved"]]
        return [f"[伏笔#{item['id']}] {item['description']}" for item in pending]

    # ==================== 一键生成上下文摘要（供章节生成器使用） ====================
    def get_context_for_chapter(self, chapter_num: int) -> str:
        """
        组装当前章节生成所需的全部上下文文本。
        这个字符串将被直接插入到章节生成的 Prompt 中。
        """
        parts = []
        parts.append("【当前角色状态】")
        parts.append(self.get_all_characters_summary())

        parts.append("\n【近期剧情回顾】")
        recent_plots = self.get_recent_plot_points(limit=5)
        if recent_plots:
            parts.extend(recent_plots)
        else:
            parts.append("（故事刚开始，暂无前情）")

        parts.append("\n【待回收伏笔】")
        pending = self.get_pending_foreshadowing()
        if pending:
            parts.extend(pending)
        else:
            parts.append("（暂无待回收伏笔）")

        return "\n".join(parts)