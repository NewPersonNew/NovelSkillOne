# -*- coding: utf-8 -*-
__author__ = "gezhaoqiang"
__date__ = "2026/8/28"

# app/state.py
import os
from infrastructure.file_manager import FileManager

class AppState:
    """全局状态管理，保存当前项目、项目列表等"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.fm = FileManager()
        self.current_project = None

    def list_projects(self):
        """扫描 data/ 目录返回所有项目名"""
        data_path = self.fm.base_path
        if not os.path.exists(data_path):
            return []
        projects = [d for d in os.listdir(data_path) if os.path.isdir(os.path.join(data_path, d))]
        return sorted(projects)

    def set_current_project(self, name):
        if name in self.list_projects():
            self.current_project = name
            return True
        return False

    def get_current_project(self):
        return self.current_project

    def add_project(self, name):
        # 项目文件夹由 FileManager 在保存设定时创建，此处仅刷新列表
        pass