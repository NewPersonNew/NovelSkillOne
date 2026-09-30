# -*- coding: utf-8 -*-
__author__ = "gezhaoqiang"
__date__ = "2026/8/28"

# app/main.py
import sys
import ctypes
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

import customtkinter as ctk
from app.state import AppState
from app.components.sidebar import Sidebar
from app.pages.dashboard import DashboardPage
from app.pages.project_init import ProjectInitPage
from app.pages.setting_workshop import SettingWorkshopPage
from app.pages.outline_designer import OutlineDesignerPage
from app.pages.editor import EditorPage
from app.pages.agents import AgentsPage
from app.styles import configure_theme

configure_theme()

class NovelApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("NovelSkillOne - AI小说创作系统")
        self.geometry("1280x800")
        self.minsize(1100, 700)

        self.app_state = AppState()
        self.pages = {}

        # 侧边栏（左侧）
        self.sidebar = Sidebar(self, app=self)
        self.sidebar.pack(side="left", fill="y")

        # 主内容区域（右侧）
        self.main_frame = ctk.CTkFrame(self, corner_radius=0)
        self.main_frame.pack(side="right", fill="both", expand=True)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        self._init_pages()
        self.switch_page("dashboard")  # 默认显示看板

    def _init_pages(self):
        """创建所有页面实例并缓存"""
        self.pages = {
            "dashboard": DashboardPage(self.main_frame, app=self),
            "init": ProjectInitPage(self.main_frame, app=self),
            "settings": SettingWorkshopPage(self.main_frame, app=self),
            "outline": OutlineDesignerPage(self.main_frame, app=self),
            "editor": EditorPage(self.main_frame, app=self),
            "agents": AgentsPage(self.main_frame, app=self),
        }
        for page in self.pages.values():
            page.grid(row=0, column=0, sticky="nsew")
            page.grid_remove()

    def switch_page(self, page_id):
        """切换到指定页面"""
        if page_id not in self.pages:
            return
        # 隐藏所有页面
        for page in self.pages.values():
            page.grid_remove()
        # 显示目标页面
        page = self.pages[page_id]
        page.grid()
        page.on_show()

    def refresh_current_page(self):
        """刷新当前可见页面（用于项目切换后更新数据）"""
        for page in self.pages.values():
            if page.winfo_ismapped():
                page.on_show()
                break

if __name__ == "__main__":
    app = NovelApp()
    app.mainloop()