# -*- coding: utf-8 -*-
__author__ = "gezhaoqiang"
__date__ = "2026/8/28"

# app/pages/outline_designer.py
import customtkinter as ctk
import json
from app.pages.base_page import BasePage
from app.styles import FONT_TITLE, FONT_HEADING, FONT_BODY, FONT_SMALL
from infrastructure.file_manager import FileManager
from core.outline_generator import OutlineGenerator


class OutlineDesignerPage(BasePage):
    def __init__(self, master, app, **kwargs):
        self.fm = FileManager()
        self.outline_gen = OutlineGenerator()
        self.outline_data = {}
        self.is_editable = False
        super().__init__(master, app, **kwargs)

    def _create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)   # 标题
        self.grid_rowconfigure(1, weight=0)   # 项目标签 + 卷信息
        self.grid_rowconfigure(2, weight=1)   # 编辑器
        self.grid_rowconfigure(3, weight=0)   # 按钮栏

        # 标题
        ctk.CTkLabel(
            self,
            text="📋 大纲设计",
            font=FONT_TITLE,
            text_color="#4fc3f7"
        ).grid(row=0, column=0, pady=(20, 10))

        # 信息栏（项目名 + 卷信息）
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.grid(row=1, column=0, sticky="ew", padx=30, pady=(0, 10))
        info_frame.grid_columnconfigure(0, weight=0)
        info_frame.grid_columnconfigure(1, weight=1)

        self.project_label = ctk.CTkLabel(
            info_frame,
            text="当前项目: 未选择",
            font=FONT_BODY,
            text_color="#888"
        )
        self.project_label.grid(row=0, column=0, padx=5, sticky="w")

        self.volume_info_label = ctk.CTkLabel(
            info_frame,
            text="",
            font=FONT_SMALL,
            text_color="#888"
        )
        self.volume_info_label.grid(row=0, column=1, padx=5, sticky="e")

        # 编辑器
        self.editor = ctk.CTkTextbox(
            self,
            font=("Microsoft YaHei", 14),
            wrap="none",
            undo=True
        )
        self.editor.grid(row=2, column=0, padx=30, pady=5, sticky="nsew")
        self.editor.insert("0.0", "尚未加载大纲，请先生成或加载已有大纲。")
        self.editor.configure(state="disabled")

        # 按钮栏
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=3, column=0, padx=30, pady=(5, 20), sticky="ew")
        btn_frame.grid_columnconfigure(0, weight=0)
        btn_frame.grid_columnconfigure(1, weight=1)
        btn_frame.grid_columnconfigure(2, weight=0)
        btn_frame.grid_columnconfigure(3, weight=0)
        btn_frame.grid_columnconfigure(4, weight=0)
        btn_frame.grid_columnconfigure(5, weight=0)

        self.status_label = ctk.CTkLabel(
            btn_frame,
            text="",
            font=FONT_BODY,
            text_color="#888"
        )
        self.status_label.grid(row=0, column=0, padx=5, sticky="w")

        # 重新加载按钮
        self.reload_btn = ctk.CTkButton(
            btn_frame,
            text="🔄 重新加载",
            command=self._load_outline,
            font=FONT_BODY,
            height=36,
            width=100,
            fg_color="#6c757d",
            hover_color="#5a6268"
        )
        self.reload_btn.grid(row=0, column=2, padx=5)

        # 编辑切换按钮
        self.edit_toggle_btn = ctk.CTkButton(
            btn_frame,
            text="✏️ 编辑",
            command=self._toggle_edit,
            font=FONT_BODY,
            height=36,
            width=80,
            fg_color="#6c757d",
            hover_color="#5a6268"
        )
        self.edit_toggle_btn.grid(row=0, column=3, padx=5)

        # 保存按钮
        self.save_btn = ctk.CTkButton(
            btn_frame,
            text="💾 保存大纲",
            command=self._save_outline,
            font=FONT_BODY,
            height=36,
            width=120,
            fg_color="#28a745",
            hover_color="#218838"
        )
        self.save_btn.grid(row=0, column=4, padx=5)

        # 生成大纲按钮
        self.generate_btn = ctk.CTkButton(
            btn_frame,
            text="🚀 生成大纲",
            command=self._generate_outline,
            font=FONT_BODY,
            height=36,
            width=120,
            fg_color="#2a6bb0",
            hover_color="#1f538d"
        )
        self.generate_btn.grid(row=0, column=5, padx=5)

    def on_show(self):
        project = self.app.app_state.get_current_project()
        if project:
            self.project_label.configure(text=f"当前项目: {project}")
            self._load_outline()
        else:
            self.project_label.configure(text="当前项目: 未选择")
            self.volume_info_label.configure(text="")
            self._set_status("请先选择项目", "#ff6b6b")
            self.editor.configure(state="normal")
            self.editor.delete("0.0", "end")
            self.editor.insert("0.0", "未选择项目，无法加载大纲。")
            self.editor.configure(state="disabled")

    def _load_outline(self):
        project = self.app.app_state.get_current_project()
        if not project:
            return

        try:
            data = self.fm.load_json(project, "outline.json")
            if not data or not data.get('chapters'):
                self._set_status("⚠️ 大纲不存在，请点击「生成大纲」", "#ffc107")
                self.volume_info_label.configure(text="")
                self.editor.configure(state="normal")
                self.editor.delete("0.0", "end")
                self.editor.insert("0.0", "大纲尚未生成。\n请确保已存在设定文件，然后点击「生成大纲」。")
                self.editor.configure(state="disabled")
                self.outline_data = {}
                return

            self.outline_data = data
            # 格式化显示
            formatted = json.dumps(data, ensure_ascii=False, indent=2)
            self.editor.configure(state="normal")
            self.editor.delete("0.0", "end")
            self.editor.insert("0.0", formatted)
            if not self.is_editable:
                self.editor.configure(state="disabled")

            # 更新卷信息
            volumes = data.get('volumes', [])
            if volumes:
                vol_lines = []
                for v in volumes:
                    vol_lines.append(f"第{v.get('volume_number', '?')}卷: {v.get('title', '未命名')} (第{v.get('chapter_start', '?')}-{v.get('chapter_end', '?')}章)")
                self.volume_info_label.configure(text="  ".join(vol_lines))
            else:
                self.volume_info_label.configure(text="")

            chapter_count = len(data.get('chapters', []))
            self._set_status(f"✅ 大纲加载成功 (共 {chapter_count} 章)", "#69db7c")
        except Exception as e:
            self._set_status(f"❌ 加载失败: {str(e)}", "#ff6b6b")
            self.editor.configure(state="normal")
            self.editor.delete("0.0", "end")
            self.editor.insert("0.0", f"加载出错: {str(e)}")
            self.editor.configure(state="disabled")

    def _generate_outline(self):
        project = self.app.app_state.get_current_project()
        if not project:
            self._set_status("请先选择项目", "#ff6b6b")
            return

        setting = self.fm.load_json(project, "settings.json")
        if not setting:
            self._set_status("❌ 设定文件不存在，请先生成设定。", "#ff6b6b")
            return

        try:
            self._set_status("⏳ 正在生成大纲，请稍候...", "#ffc107")
            self.generate_btn.configure(state="disabled", text="⏳ 生成中...")
            self.update_idletasks()

            result = self.outline_gen.generate_outline(project)
            self.outline_data = result

            # 更新卷信息
            volumes = result.get('volumes', [])
            if volumes:
                vol_lines = []
                for v in volumes:
                    vol_lines.append(f"第{v.get('volume_number', '?')}卷: {v.get('title', '未命名')} (第{v.get('chapter_start', '?')}-{v.get('chapter_end', '?')}章)")
                self.volume_info_label.configure(text="  ".join(vol_lines))
            else:
                self.volume_info_label.configure(text="")

            formatted = json.dumps(result, ensure_ascii=False, indent=2)
            self.editor.configure(state="normal")
            self.editor.delete("0.0", "end")
            self.editor.insert("0.0", formatted)
            if not self.is_editable:
                self.editor.configure(state="disabled")

            chapter_count = len(result.get('chapters', []))
            self._set_status(f"✅ 大纲生成成功！共 {chapter_count} 章。", "#69db7c")
        except Exception as e:
            self._set_status(f"❌ 生成失败: {str(e)}", "#ff6b6b")
        finally:
            self.generate_btn.configure(state="normal", text="🚀 生成大纲")

    def _save_outline(self):
        project = self.app.app_state.get_current_project()
        if not project:
            self._set_status("请先选择项目", "#ff6b6b")
            return

        try:
            content = self.editor.get("0.0", "end").strip()
            if not content:
                self._set_status("❌ 内容为空，无法保存", "#ff6b6b")
                return
            new_data = json.loads(content)
            if 'chapters' not in new_data:
                self._set_status("❌ 大纲格式错误：缺少 'chapters' 字段", "#ff6b6b")
                return
            self.fm.save_json(project, "outline.json", new_data)
            self.outline_data = new_data
            self._set_status("✅ 大纲已保存！", "#69db7c")
            # 重新格式化显示
            formatted = json.dumps(new_data, ensure_ascii=False, indent=2)
            self.editor.configure(state="normal")
            self.editor.delete("0.0", "end")
            self.editor.insert("0.0", formatted)
            if not self.is_editable:
                self.editor.configure(state="disabled")
            # 刷新卷信息
            volumes = new_data.get('volumes', [])
            if volumes:
                vol_lines = []
                for v in volumes:
                    vol_lines.append(f"第{v.get('volume_number', '?')}卷: {v.get('title', '未命名')} (第{v.get('chapter_start', '?')}-{v.get('chapter_end', '?')}章)")
                self.volume_info_label.configure(text="  ".join(vol_lines))
            else:
                self.volume_info_label.configure(text="")
        except json.JSONDecodeError as e:
            self._set_status(f"❌ JSON 格式错误: {str(e)}", "#ff6b6b")
        except Exception as e:
            self._set_status(f"❌ 保存失败: {str(e)}", "#ff6b6b")

    def _toggle_edit(self):
        self.is_editable = not self.is_editable
        if self.is_editable:
            self.editor.configure(state="normal")
            self.edit_toggle_btn.configure(text="🔒 锁定", fg_color="#dc3545", hover_color="#c82333")
            self._set_status("✏️ 编辑模式已开启，修改后请点击保存。", "#ffc107")
        else:
            self.editor.configure(state="disabled")
            self.edit_toggle_btn.configure(text="✏️ 编辑", fg_color="#6c757d", hover_color="#5a6268")
            self._set_status("🔒 已锁定，只读模式。", "#888")
            self._load_outline()  # 重新加载以丢弃未保存更改

    def _set_status(self, msg, color="#888"):
        self.status_label.configure(text=msg, text_color=color)