# -*- coding: utf-8 -*-
__author__ = "gezhaoqiang"
__date__ = "2026/8/28"

# app/pages/editor.py
import customtkinter as ctk
import json
from app.pages.base_page import BasePage
from app.styles import FONT_TITLE, FONT_HEADING, FONT_BODY, FONT_SMALL
from infrastructure.file_manager import FileManager
from core.chapter_generator import ChapterGenerator
from orchestration.context_assembler import ContextAssembler


class EditorPage(BasePage):
    def __init__(self, master, app, **kwargs):
        self.fm = FileManager()
        self.chapter_gen = None  # 延迟初始化，因为需要项目名
        self.context_assembler = None
        self.current_chapter_num = 1
        self.outline = {}
        super().__init__(master, app, **kwargs)

    def _create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)   # 标题
        self.grid_rowconfigure(1, weight=1)   # 主内容

        # 标题
        ctk.CTkLabel(
            self,
            text="✍️ 沉浸式编辑器",
            font=FONT_TITLE,
            text_color="#4fc3f7"
        ).grid(row=0, column=0, pady=(20, 10))

        # 主框架
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=0)   # 控制栏
        main_frame.grid_rowconfigure(1, weight=0)   # 章节选择+按钮
        main_frame.grid_rowconfigure(2, weight=1)   # 编辑区+侧栏

        # ---- 控制栏（项目名 + 状态） ----
        control_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        control_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        control_frame.grid_columnconfigure(0, weight=0)
        control_frame.grid_columnconfigure(1, weight=1)

        self.project_label = ctk.CTkLabel(
            control_frame,
            text="项目: 未选择",
            font=FONT_BODY,
            text_color="#888"
        )
        self.project_label.grid(row=0, column=0, padx=5, sticky="w")

        self.status_label = ctk.CTkLabel(
            control_frame,
            text="就绪",
            font=FONT_BODY,
            text_color="#888"
        )
        self.status_label.grid(row=0, column=1, padx=5, sticky="e")

        # ---- 章节选择与操作按钮 ----
        action_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        action_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        action_frame.grid_columnconfigure(0, weight=0)
        action_frame.grid_columnconfigure(1, weight=0)
        action_frame.grid_columnconfigure(2, weight=0)
        action_frame.grid_columnconfigure(3, weight=0)
        action_frame.grid_columnconfigure(4, weight=1)

        self.chapter_var = ctk.StringVar(value="1")
        self.chapter_dropdown = ctk.CTkOptionMenu(
            action_frame,
            variable=self.chapter_var,
            values=["1"],  # 初始占位
            font=FONT_BODY,
            width=80,
            height=32
        )
        self.chapter_dropdown.grid(row=0, column=0, padx=5)

        self.load_btn = ctk.CTkButton(
            action_frame,
            text="📖 加载",
            command=self._load_chapter,
            font=FONT_BODY,
            height=32,
            width=70
        )
        self.load_btn.grid(row=0, column=1, padx=5)

        self.generate_btn = ctk.CTkButton(
            action_frame,
            text="🚀 生成",
            command=self._generate_chapter,
            font=FONT_BODY,
            height=32,
            width=70,
            fg_color="#2a6bb0",
            hover_color="#1f538d"
        )
        self.generate_btn.grid(row=0, column=2, padx=5)

        self.finalize_btn = ctk.CTkButton(
            action_frame,
            text="🔒 定稿",
            command=self._finalize_chapter,
            font=FONT_BODY,
            height=32,
            width=70,
            fg_color="#28a745",
            hover_color="#218838"
        )
        self.finalize_btn.grid(row=0, column=3, padx=5)

        # 用户指导输入框
        self.guidance_entry = ctk.CTkEntry(
            action_frame,
            placeholder_text="用户指导（可选）",
            font=FONT_BODY,
            height=32
        )
        self.guidance_entry.grid(row=0, column=4, padx=5, sticky="ew")

        # ---- 主编辑区：左侧编辑器 + 右侧上下文面板 ----
        edit_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        edit_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 0))
        edit_frame.grid_columnconfigure(0, weight=3)
        edit_frame.grid_columnconfigure(1, weight=1)
        edit_frame.grid_rowconfigure(0, weight=1)

        # 左侧：内容编辑器
        self.content_editor = ctk.CTkTextbox(
            edit_frame,
            font=("Microsoft YaHei", 13),
            wrap="word",
            undo=True
        )
        self.content_editor.grid(row=0, column=0, padx=(0, 5), sticky="nsew")
        self.content_editor.insert("0.0", "请选择章节并点击「加载」或「生成」。")

        # 右侧：上下文面板
        context_frame = ctk.CTkFrame(edit_frame, fg_color="#1e1e3a", corner_radius=8)
        context_frame.grid(row=0, column=1, padx=(5, 0), sticky="nsew")
        context_frame.grid_columnconfigure(0, weight=1)
        context_frame.grid_rowconfigure(0, weight=0)
        context_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            context_frame,
            text="🧠 写前上下文",
            font=FONT_HEADING,
            text_color="#4fc3f7"
        ).grid(row=0, column=0, pady=(8, 5))

        self.context_display = ctk.CTkTextbox(
            context_frame,
            font=FONT_SMALL,
            wrap="word",
            state="disabled"
        )
        self.context_display.grid(row=1, column=0, padx=8, pady=(0, 8), sticky="nsew")
        self.context_display.insert("0.0", "点击「加载」或「生成」后，这里会显示当前章节的上下文信息。")

    def on_show(self):
        """页面激活时刷新项目信息和章节列表"""
        project = self.app.app_state.get_current_project()
        if not project:
            self.project_label.configure(text="项目: 未选择")
            self._set_status("请先选择项目", "#ff6b6b")
            self.content_editor.configure(state="normal")
            self.content_editor.delete("0.0", "end")
            self.content_editor.insert("0.0", "请先在侧边栏选择一个项目。")
            self.content_editor.configure(state="disabled")
            self.chapter_dropdown.configure(values=[])
            return

        self.project_label.configure(text=f"项目: {project}")
        # 初始化生成器和组装器
        self.chapter_gen = ChapterGenerator(project)
        self.context_assembler = ContextAssembler(project)

        # 加载大纲，更新章节下拉
        self.outline = self.fm.load_json(project, "outline.json")
        if self.outline and self.outline.get('chapters'):
            chapters = self.outline['chapters']
            choices = [str(i+1) for i in range(len(chapters))]
            self.chapter_dropdown.configure(values=choices)
            if choices:
                self.chapter_var.set(choices[0])
                self.current_chapter_num = 1
            self._set_status(f"已加载 {len(chapters)} 章", "#69db7c")
        else:
            self.chapter_dropdown.configure(values=[])
            self._set_status("未找到大纲，请先生成大纲。", "#ffc107")
            self.content_editor.configure(state="normal")
            self.content_editor.delete("0.0", "end")
            self.content_editor.insert("0.0", "未找到大纲文件，请前往「大纲设计」页面生成。")
            self.content_editor.configure(state="disabled")

        # 自动加载当前选中的第一章（如果有）
        if self.chapter_dropdown.cget('values'):
            self._load_chapter()

    def _set_status(self, msg, color="#888"):
        self.status_label.configure(text=msg, text_color=color)

    def _get_current_chapter_num(self):
        try:
            return int(self.chapter_var.get())
        except:
            return 1

    def _load_chapter(self):
        """加载当前选中章节的内容和上下文"""
        project = self.app.app_state.get_current_project()
        if not project:
            self._set_status("请先选择项目", "#ff6b6b")
            return

        ch_num = self._get_current_chapter_num()
        self.current_chapter_num = ch_num

        # 1. 加载正文
        content = self.fm.load_text(project, f"chapters/chapter_{ch_num}.txt")
        self.content_editor.configure(state="normal")
        self.content_editor.delete("0.0", "end")
        if content:
            self.content_editor.insert("0.0", content)
            self._set_status(f"✅ 已加载第 {ch_num} 章 (共 {len(content)} 字符)", "#69db7c")
        else:
            self.content_editor.insert("0.0", f"第 {ch_num} 章尚未生成，点击「生成」创建草稿。")
            self._set_status(f"第 {ch_num} 章无内容", "#ffc107")
        self.content_editor.configure(state="normal")  # 可编辑

        # 2. 加载上下文
        if self.context_assembler:
            try:
                context = self.context_assembler.assemble(ch_num)
                # 格式化上下文
                lines = []
                lines.append("【角色状态】")
                for name, info in context.get('characters', {}).items():
                    state = info.get('current_state', {})
                    lines.append(f"- {name}: {state.get('status', '正常')}")
                lines.append("\n【活跃伏笔】")
                for p in context.get('active_promises', []):
                    lines.append(f"- {p['description']}")
                lines.append("\n【近期事实】")
                for f in context.get('recent_facts', [])[-5:]:
                    lines.append(f"- {f['entity']} → {f['attribute']} = {f['value']}")
                context_text = "\n".join(lines) if lines else "无上下文信息"
                self.context_display.configure(state="normal")
                self.context_display.delete("0.0", "end")
                self.context_display.insert("0.0", context_text)
                self.context_display.configure(state="disabled")
            except Exception as e:
                self.context_display.configure(state="normal")
                self.context_display.delete("0.0", "end")
                self.context_display.insert("0.0", f"加载上下文失败: {str(e)}")
                self.context_display.configure(state="disabled")
        else:
            self.context_display.configure(state="normal")
            self.context_display.delete("0.0", "end")
            self.context_display.insert("0.0", "上下文组装器未初始化")
            self.context_display.configure(state="disabled")

    def _generate_chapter(self):
        """生成当前章节"""
        project = self.app.app_state.get_current_project()
        if not project:
            self._set_status("请先选择项目", "#ff6b6b")
            return

        ch_num = self._get_current_chapter_num()
        guidance = self.guidance_entry.get().strip()

        # 检查是否有大纲
        if not self.outline or not self.outline.get('chapters'):
            self._set_status("❌ 大纲不存在，请先生成大纲。", "#ff6b6b")
            return

        if ch_num > len(self.outline['chapters']):
            self._set_status(f"❌ 章节号超出范围 (共 {len(self.outline['chapters'])} 章)", "#ff6b6b")
            return

        try:
            self._set_status("⏳ 生成中，请稍候...", "#ffc107")
            self.generate_btn.configure(state="disabled", text="⏳ 生成中...")
            self.update_idletasks()

            # 调用 ChapterGenerator
            result = self.chapter_gen.generate_chapter(ch_num, guidance)
            content = result['content']

            # 更新编辑器
            self.content_editor.configure(state="normal")
            self.content_editor.delete("0.0", "end")
            self.content_editor.insert("0.0", content)
            self.content_editor.configure(state="normal")
            self._set_status(f"✅ 第 {ch_num} 章生成完成！字数: {len(content)}", "#69db7c")

            # 刷新上下文（可能已变化）
            self._load_context_only()

        except Exception as e:
            self._set_status(f"❌ 生成失败: {str(e)}", "#ff6b6b")
        finally:
            self.generate_btn.configure(state="normal", text="🚀 生成")

    def _finalize_chapter(self):
        """定稿当前章节"""
        project = self.app.app_state.get_current_project()
        if not project:
            self._set_status("请先选择项目", "#ff6b6b")
            return

        ch_num = self._get_current_chapter_num()
        content = self.content_editor.get("0.0", "end").strip()
        if not content:
            self._set_status("❌ 内容为空，无法定稿", "#ff6b6b")
            return

        try:
            self._set_status("⏳ 定稿中...", "#ffc107")
            self.finalize_btn.configure(state="disabled", text="⏳ 定稿中...")
            self.update_idletasks()

            self.chapter_gen.finalize_chapter(ch_num, content)
            self._set_status(f"✅ 第 {ch_num} 章定稿成功！记忆已更新。", "#69db7c")

            # 刷新上下文
            self._load_context_only()

        except Exception as e:
            self._set_status(f"❌ 定稿失败: {str(e)}", "#ff6b6b")
        finally:
            self.finalize_btn.configure(state="normal", text="🔒 定稿")

    def _load_context_only(self):
        """仅刷新上下文面板（不重新加载正文）"""
        if not self.context_assembler:
            return
        ch_num = self.current_chapter_num
        try:
            context = self.context_assembler.assemble(ch_num)
            lines = []
            lines.append("【角色状态】")
            for name, info in context.get('characters', {}).items():
                state = info.get('current_state', {})
                lines.append(f"- {name}: {state.get('status', '正常')}")
            lines.append("\n【活跃伏笔】")
            for p in context.get('active_promises', []):
                lines.append(f"- {p['description']}")
            lines.append("\n【近期事实】")
            for f in context.get('recent_facts', [])[-5:]:
                lines.append(f"- {f['entity']} → {f['attribute']} = {f['value']}")
            context_text = "\n".join(lines) if lines else "无上下文信息"
            self.context_display.configure(state="normal")
            self.context_display.delete("0.0", "end")
            self.context_display.insert("0.0", context_text)
            self.context_display.configure(state="disabled")
        except Exception as e:
            pass