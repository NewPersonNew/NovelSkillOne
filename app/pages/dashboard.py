# -*- coding: utf-8 -*-
__author__ = "gezhaoqiang"
__date__ = "2026/8/28"

# app/pages/dashboard.py
import customtkinter as ctk
from app.pages.base_page import BasePage
from app.styles import FONT_TITLE, FONT_HEADING, FONT_BODY, FONT_SMALL
from infrastructure.file_manager import FileManager
import os
import json

class DashboardPage(BasePage):
    def __init__(self, master, app, **kwargs):
        self.fm = FileManager()
        super().__init__(master, app, **kwargs)

    def _create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            self,
            text="📊 项目看板",
            font=FONT_TITLE,
            text_color="#4fc3f7"
        ).grid(row=0, column=0, pady=(20, 10))

        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=1, column=0, padx=30, pady=10, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=0)
        self.content_frame.grid_rowconfigure(1, weight=1)

        self.project_label = ctk.CTkLabel(
            self.content_frame,
            text="当前项目: 未选择",
            font=FONT_HEADING,
            text_color="#888"
        )
        self.project_label.grid(row=0, column=0, sticky="w", pady=(0, 15))

        self.info_text = ctk.CTkTextbox(
            self.content_frame,
            font=FONT_BODY,
            wrap="word",
            height=300,
            state="disabled"
        )
        self.info_text.grid(row=1, column=0, sticky="nsew", pady=5)

    def on_show(self):
        self._refresh()

    def _refresh(self):
        project = self.app.app_state.get_current_project()
        if not project:
            self.project_label.configure(text="当前项目: 未选择")
            self._set_info("请选择一个项目或创建一个新项目。")
            return

        self.project_label.configure(text=f"当前项目: {project}")
        # 收集项目信息
        info_lines = [f"📁 项目名称: {project}"]
        info_lines.append("")

        # 读取设定
        settings = self.fm.load_json(project, "settings.json")
        if settings:
            title = settings.get('novel_title', '未命名')
            total_words = settings.get('word_count', 0)
            protagonist = settings.get('protagonist', {}).get('name', '未知')
            info_lines.append(f"📖 小说标题: {title}")
            info_lines.append(f"✏️ 主角: {protagonist}")
            info_lines.append(f"📏 目标字数: {total_words:,}")
        else:
            info_lines.append("⚠️ 设定文件未找到，请先创建设定。")

        # 大纲信息
        outline = self.fm.load_json(project, "outline.json")
        if outline and outline.get('chapters'):
            chapter_count = len(outline['chapters'])
            info_lines.append(f"📋 大纲章节数: {chapter_count}")
        else:
            info_lines.append("📋 大纲未生成或为空。")

        # 章节完成情况
        chapters_dir = os.path.join(self.fm.base_path, project, "chapters")
        if os.path.exists(chapters_dir):
            chapter_files = [f for f in os.listdir(chapters_dir) if f.startswith("chapter_") and f.endswith(".txt")]
            completed = len(chapter_files)
            info_lines.append(f"✍️ 已生成章节数: {completed}")
        else:
            info_lines.append("✍️ 尚未生成任何章节。")

        # 数据库统计（如果存在）
        db_path = os.path.join(self.fm.base_path, project, "canon.db")
        if os.path.exists(db_path):
            import sqlite3
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM facts")
                fact_count = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM promises WHERE status='active'")
                promise_count = cursor.fetchone()[0]
                conn.close()
                info_lines.append(f"🧠 事实库条目: {fact_count}")
                info_lines.append(f"🎯 活跃伏笔数: {promise_count}")
            except:
                pass

        info_lines.append("\n📂 数据存储位置:")
        info_lines.append(f"   {os.path.join(self.fm.base_path, project)}")

        self._set_info("\n".join(info_lines))

    def _set_info(self, text):
        self.info_text.configure(state="normal")
        self.info_text.delete("0.0", "end")
        self.info_text.insert("0.0", text)
        self.info_text.configure(state="disabled")