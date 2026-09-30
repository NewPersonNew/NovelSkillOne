# -*- coding: utf-8 -*-
__author__ = "gezhaoqiang"
__date__ = "2026/8/28"

# app/components/sidebar.py
import customtkinter as ctk
from customtkinter import CTkComboBox
import os
import shutil
from app.state import AppState
from app.styles import FONT_TITLE, FONT_BODY, FONT_SMALL

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, app, **kwargs):
        super().__init__(master, width=220, corner_radius=0, **kwargs)
        self.app = app
        self.pack(side="left", fill="y", padx=0, pady=0)
        self.grid_columnconfigure(0, weight=1)
        self._create_widgets()

    def _create_widgets(self):
        # 标题
        self.title_label = ctk.CTkLabel(
            self,
            text="📚 NovelSkillOne",
            font=FONT_TITLE,
            text_color="#4fc3f7"
        )
        self.title_label.grid(row=0, column=0, pady=(20, 15), padx=15, sticky="w")

        # 项目选择下拉（改用 CTkComboBox）
        self.project_var = ctk.StringVar(value="选择项目")
        self.project_dropdown = CTkComboBox(
            self,
            variable=self.project_var,
            values=self.app.app_state.list_projects(),
            command=self._on_project_change,
            font=FONT_BODY,
            width=200,
            height=35,
            state="readonly",
            dropdown_font=FONT_BODY
        )
        self.project_dropdown.grid(row=1, column=0, pady=5, padx=15, sticky="ew")

        # 新建项目按钮
        self.new_btn = ctk.CTkButton(
            self,
            text="➕ 新建项目",
            command=self._new_project,
            font=FONT_BODY,
            height=35,
            fg_color="#2a6bb0",
            hover_color="#1f538d"
        )
        self.new_btn.grid(row=2, column=0, pady=5, padx=15, sticky="ew")

        # 分隔线
        ctk.CTkFrame(self, height=2, fg_color="#2a2a4a").grid(row=3, column=0, pady=(15, 10), padx=15, sticky="ew")

        # 导航按钮
        nav_items = [
            ("📊 项目看板", "dashboard"),
            ("🛠️ 设定工坊", "settings"),
            ("📋 大纲设计", "outline"),
            ("✍️ 编辑器", "editor"),
            ("🧠 智能Agent", "agents")
        ]

        self.nav_buttons = {}
        for idx, (label, page_id) in enumerate(nav_items):
            btn = ctk.CTkButton(
                self,
                text=label,
                command=lambda pid=page_id: self.app.switch_page(pid),
                font=FONT_BODY,
                height=38,
                fg_color="transparent",
                hover_color="#2a2a4a",
                anchor="w"
            )
            btn.grid(row=4 + idx, column=0, pady=3, padx=15, sticky="ew")
            self.nav_buttons[page_id] = btn

        # 底部：当前项目状态 + 删除按钮
        self.project_label = ctk.CTkLabel(
            self,
            text="当前项目: 未选择",
            font=FONT_SMALL,
            text_color="#888"
        )
        self.project_label.grid(row=100, column=0, pady=(20, 5), padx=15, sticky="w")

        self.delete_btn = ctk.CTkButton(
            self,
            text="🗑️ 删除当前项目",
            command=self._delete_project,
            font=FONT_SMALL,
            fg_color="#dc3545",
            hover_color="#c82333",
            height=30
        )
        self.delete_btn.grid(row=101, column=0, pady=(0, 15), padx=15, sticky="ew")

    def _on_project_change(self, choice):
        if choice and choice != "选择项目":
            self.app.app_state.set_current_project(choice)
            self.project_label.configure(text=f"当前项目: {choice}")
            self.app.refresh_current_page()

    def _new_project(self):
        self.app.switch_page("init")

    def _delete_project(self):
        project = self.app.app_state.get_current_project()
        if not project:
            ctk.CTkMessagebox.show_error("错误", "请先选择一个项目。")
            return

        result = ctk.CTkMessagebox.show_question(
            "确认删除",
            f"确定要永久删除项目 '{project}' 吗？\n此操作不可恢复！",
            icon="warning",
            option_1="取消",
            option_2="确认删除"
        )
        if result != "确认删除":
            return

        project_path = os.path.join(self.app.app_state.fm.base_path, project)
        try:
            if os.path.exists(project_path):
                shutil.rmtree(project_path)
                self.app.app_state.current_project = None
                self.project_var.set("选择项目")
                self.project_label.configure(text="当前项目: 未选择")
                self.refresh_projects()
                self.app.switch_page("init")
                ctk.CTkMessagebox.show_info("成功", f"项目 '{project}' 已删除。")
            else:
                ctk.CTkMessagebox.show_error("错误", "项目路径不存在。")
        except Exception as e:
            ctk.CTkMessagebox.show_error("错误", f"删除失败: {str(e)}")

    def refresh_projects(self):
        projects = self.app.app_state.list_projects()
        self.project_dropdown.configure(values=projects)
        current = self.app.app_state.get_current_project()
        if current and current in projects:
            self.project_var.set(current)
        else:
            self.project_var.set("选择项目")