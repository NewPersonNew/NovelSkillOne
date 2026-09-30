# -*- coding: utf-8 -*-
__author__ = "gezhaoqiang"
__date__ = "2026/8/27"

import os
import json
from typing import Any, Dict, List


class FileManager:
    def __init__(self, base_path: str = "./data"):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)

    def _get_project_path(self, project_name: str) -> str:
        proj_path = os.path.join(self.base_path, project_name)
        os.makedirs(proj_path, exist_ok=True)
        return proj_path

    def save_json(self, project_name: str, filename: str, data: Dict[str, Any]):
        path = os.path.join(self._get_project_path(project_name), filename)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_json(self, project_name: str, filename: str) -> Dict[str, Any]:
        path = os.path.join(self._get_project_path(project_name), filename)
        if not os.path.exists(path):
            return {}
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_text(self, project_name: str, filename: str, content: str):
        path = os.path.join(self._get_project_path(project_name), filename)
        # 如果文件名包含文件夹，自动创建父目录
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

    def load_text(self, project_name: str, filename: str) -> str:
        path = os.path.join(self._get_project_path(project_name), filename)
        if not os.path.exists(path):
            return ""
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    def list_chapters(self, project_name: str) -> List[str]:
        proj_path = self._get_project_path(project_name)
        chapters_dir = os.path.join(proj_path, "chapters")
        if not os.path.exists(chapters_dir):
            return []
        return [f for f in os.listdir(chapters_dir) if f.startswith("chapter_") and f.endswith(".txt")]