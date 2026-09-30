# -*- coding: utf-8 -*-
__author__ = "gezhaoqiang"
__date__ = "2026/8/28"

import customtkinter as ctk
import json
from app.pages.base_page import BasePage
from app.styles import FONT_TITLE, FONT_HEADING, FONT_BODY, FONT_SMALL
from infrastructure.file_manager import FileManager


class SettingWorkshopPage(BasePage):
    def __init__(self, master, app, **kwargs):
        self.fm = FileManager()
        self.setting_data = {}
        self.is_editable = False
        super().__init__(master, app, **kwargs)

    def _create_widgets(self):
        # 主布局
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)   # 标题
        self.grid_rowconfigure(1, weight=0)   # 项目标签
        self.grid_rowconfigure(2, weight=1)   # 可滚动表单区域
        self.grid_rowconfigure(3, weight=0)   # 按钮栏

        # 标题
        ctk.CTkLabel(
            self,
            text="🛠️ 设定工坊",
            font=FONT_TITLE,
            text_color="#4fc3f7"
        ).grid(row=0, column=0, pady=(20, 10))

        # 项目标签
        self.project_label = ctk.CTkLabel(
            self,
            text="当前项目: 未选择",
            font=FONT_BODY,
            text_color="#888"
        )
        self.project_label.grid(row=1, column=0, sticky="w", padx=30, pady=(0, 10))

        # 可滚动表单容器
        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.grid(row=2, column=0, padx=30, pady=5, sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)

        # 存放所有输入控件的字典
        self.widgets = {}

        # 创建表单字段
        self._build_form()

        # 按钮栏
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=3, column=0, padx=30, pady=(5, 20), sticky="ew")
        btn_frame.grid_columnconfigure(0, weight=0)
        btn_frame.grid_columnconfigure(1, weight=1)
        btn_frame.grid_columnconfigure(2, weight=0)
        btn_frame.grid_columnconfigure(3, weight=0)
        btn_frame.grid_columnconfigure(4, weight=0)

        self.status_label = ctk.CTkLabel(
            btn_frame,
            text="",
            font=FONT_BODY,
            text_color="#888"
        )
        self.status_label.grid(row=0, column=0, padx=5, sticky="w")

        self.reload_btn = ctk.CTkButton(
            btn_frame,
            text="🔄 重新加载",
            command=self._load_setting,
            font=FONT_BODY,
            height=36,
            width=100,
            fg_color="#6c757d",
            hover_color="#5a6268"
        )
        self.reload_btn.grid(row=0, column=2, padx=5)

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

        self.save_btn = ctk.CTkButton(
            btn_frame,
            text="💾 保存设定",
            command=self._save_setting,
            font=FONT_BODY,
            height=36,
            width=120,
            fg_color="#28a745",
            hover_color="#218838"
        )
        self.save_btn.grid(row=0, column=4, padx=5)

    def _build_form(self):
        """构建表单控件（初始为空，由_load_setting填充）"""
        # 1. 小说标题
        self._add_label("小说标题")
        self.widgets['novel_title'] = ctk.CTkEntry(self.scroll_frame, font=FONT_BODY, width=400)
        self.widgets['novel_title'].pack(fill="x", pady=(0, 10))

        # 2. 世界观设定
        self._add_label("世界观设定")
        self.widgets['world_setting'] = ctk.CTkTextbox(self.scroll_frame, height=80, font=FONT_BODY)
        self.widgets['world_setting'].pack(fill="x", pady=(0, 10))

        # 3. 主角信息
        self._add_section_header("主角信息")
        # 姓名
        self._add_label("姓名")
        self.widgets['protagonist_name'] = ctk.CTkEntry(self.scroll_frame, font=FONT_BODY, width=200)
        self.widgets['protagonist_name'].pack(fill="x", pady=(0, 5))
        # 年龄
        self._add_label("年龄")
        self.widgets['protagonist_age'] = ctk.CTkEntry(self.scroll_frame, font=FONT_BODY, width=100)
        self.widgets['protagonist_age'].pack(fill="x", pady=(0, 5))
        # 性格
        self._add_label("性格")
        self.widgets['protagonist_personality'] = ctk.CTkTextbox(self.scroll_frame, height=50, font=FONT_BODY)
        self.widgets['protagonist_personality'].pack(fill="x", pady=(0, 5))
        # 背景
        self._add_label("背景")
        self.widgets['protagonist_background'] = ctk.CTkTextbox(self.scroll_frame, height=50, font=FONT_BODY)
        self.widgets['protagonist_background'].pack(fill="x", pady=(0, 5))
        # 初始目标
        self._add_label("初始目标")
        self.widgets['protagonist_goal'] = ctk.CTkEntry(self.scroll_frame, font=FONT_BODY, width=400)
        self.widgets['protagonist_goal'].pack(fill="x", pady=(0, 10))

        # 4. 配角列表
        self._add_section_header("配角列表（每行一个，格式：姓名|角色|性格|关系）")
        self.widgets['supporting_characters'] = ctk.CTkTextbox(self.scroll_frame, height=80, font=FONT_BODY)
        self.widgets['supporting_characters'].pack(fill="x", pady=(0, 10))

        # 5. 女主角
        self._add_label("女主角/重要女性")
        self.widgets['heroine'] = ctk.CTkEntry(self.scroll_frame, font=FONT_BODY, width=400)
        self.widgets['heroine'].pack(fill="x", pady=(0, 10))

        # 6. 反派Boss
        self._add_label("反派Boss")
        self.widgets['villain'] = ctk.CTkEntry(self.scroll_frame, font=FONT_BODY, width=400)
        self.widgets['villain'].pack(fill="x", pady=(0, 10))

        # 7. 父母/家人
        self._add_label("父母/家人")
        self.widgets['family'] = ctk.CTkEntry(self.scroll_frame, font=FONT_BODY, width=400)
        self.widgets['family'].pack(fill="x", pady=(0, 10))

        # 8. 核心冲突
        self._add_label("核心冲突")
        self.widgets['core_conflict'] = ctk.CTkTextbox(self.scroll_frame, height=60, font=FONT_BODY)
        self.widgets['core_conflict'].pack(fill="x", pady=(0, 10))

        # 9. 世界规则
        self._add_label("世界规则（等级体系、魔法体系等）")
        self.widgets['world_rules'] = ctk.CTkTextbox(self.scroll_frame, height=80, font=FONT_BODY)
        self.widgets['world_rules'].pack(fill="x", pady=(0, 10))

        # 10. 开局事件
        self._add_label("开局事件（前1-3章）")
        self.widgets['initial_plot'] = ctk.CTkTextbox(self.scroll_frame, height=80, font=FONT_BODY)
        self.widgets['initial_plot'].pack(fill="x", pady=(0, 10))

        # 11. 伏笔提示（JSON数组）
        self._add_label("伏笔提示（JSON数组，如 [\"伏笔1\", \"伏笔2\"] ）")
        self.widgets['foreshadowing_hints'] = ctk.CTkEntry(self.scroll_frame, font=FONT_BODY, width=400)
        self.widgets['foreshadowing_hints'].pack(fill="x", pady=(0, 10))

        # 12. 故事基调（额外字段）
        self._add_label("故事基调")
        self.widgets['story_tone'] = ctk.CTkEntry(self.scroll_frame, font=FONT_BODY, width=400)
        self.widgets['story_tone'].pack(fill="x", pady=(0, 10))

        # 所有控件默认禁用
        self._set_widgets_state("disabled")

    def _add_label(self, text):
        ctk.CTkLabel(self.scroll_frame, text=text, font=FONT_BODY, anchor="w").pack(fill="x", pady=(5, 0))

    def _add_section_header(self, text):
        ctk.CTkLabel(self.scroll_frame, text=text, font=FONT_HEADING, anchor="w").pack(fill="x", pady=(10, 5))

    def _set_widgets_state(self, state):
        for widget in self.widgets.values():
            if isinstance(widget, (ctk.CTkEntry, ctk.CTkTextbox)):
                try:
                    widget.configure(state=state)
                except:
                    pass

    def _populate_form(self, data):
        """从设定数据填充表单，临时启用控件"""
        # 临时启用所有控件
        self._set_widgets_state("normal")

        # 小说标题
        self.widgets['novel_title'].delete(0, "end")
        self.widgets['novel_title'].insert(0, data.get('novel_title', ''))

        # 世界观设定
        self._set_text(self.widgets['world_setting'], data.get('world_setting', ''))

        # 主角信息
        prot = data.get('protagonist', {})
        self.widgets['protagonist_name'].delete(0, "end")
        self.widgets['protagonist_name'].insert(0, prot.get('name', ''))
        self.widgets['protagonist_age'].delete(0, "end")
        self.widgets['protagonist_age'].insert(0, str(prot.get('age', '')))
        self._set_text(self.widgets['protagonist_personality'], prot.get('personality', ''))
        self._set_text(self.widgets['protagonist_background'], prot.get('background', ''))
        self.widgets['protagonist_goal'].delete(0, "end")
        self.widgets['protagonist_goal'].insert(0, prot.get('initial_goal', ''))

        # 配角列表
        supporting = data.get('supporting_characters', [])
        if supporting:
            lines = []
            for char in supporting:
                lines.append(f"{char.get('name','')}|{char.get('role','')}|{char.get('personality','')}|{char.get('relationship','')}")
            self._set_text(self.widgets['supporting_characters'], "\n".join(lines))
        else:
            self._set_text(self.widgets['supporting_characters'], '')

        # 其他字段
        self.widgets['heroine'].delete(0, "end")
        self.widgets['heroine'].insert(0, data.get('heroine', ''))
        self.widgets['villain'].delete(0, "end")
        self.widgets['villain'].insert(0, data.get('villain', ''))
        self.widgets['family'].delete(0, "end")
        self.widgets['family'].insert(0, data.get('family', ''))

        self._set_text(self.widgets['core_conflict'], data.get('core_conflict', ''))
        self._set_text(self.widgets['world_rules'], data.get('world_rules', ''))
        self._set_text(self.widgets['initial_plot'], data.get('initial_plot', ''))

        # 伏笔提示（JSON数组）
        foreshadowing = data.get('foreshadowing_hints', [])
        self.widgets['foreshadowing_hints'].delete(0, "end")
        self.widgets['foreshadowing_hints'].insert(0, json.dumps(foreshadowing, ensure_ascii=False))

        # 故事基调
        self.widgets['story_tone'].delete(0, "end")
        self.widgets['story_tone'].insert(0, data.get('story_tone', ''))

        # 恢复原始状态
        self._set_widgets_state("disabled" if not self.is_editable else "normal")

    def _set_text(self, textbox, text):
        textbox.delete("0.0", "end")
        textbox.insert("0.0", text)

    def _collect_form_data(self):
        """从表单收集数据，构造JSON"""
        data = {}
        # 简单字段
        data['novel_title'] = self.widgets['novel_title'].get().strip()
        data['world_setting'] = self.widgets['world_setting'].get("0.0", "end").strip()
        data['heroine'] = self.widgets['heroine'].get().strip()
        data['villain'] = self.widgets['villain'].get().strip()
        data['family'] = self.widgets['family'].get().strip()
        data['core_conflict'] = self.widgets['core_conflict'].get("0.0", "end").strip()
        data['world_rules'] = self.widgets['world_rules'].get("0.0", "end").strip()
        data['initial_plot'] = self.widgets['initial_plot'].get("0.0", "end").strip()
        data['story_tone'] = self.widgets['story_tone'].get().strip()

        # 主角
        prot = {
            'name': self.widgets['protagonist_name'].get().strip(),
            'age': self.widgets['protagonist_age'].get().strip(),
            'personality': self.widgets['protagonist_personality'].get("0.0", "end").strip(),
            'background': self.widgets['protagonist_background'].get("0.0", "end").strip(),
            'initial_goal': self.widgets['protagonist_goal'].get().strip(),
        }
        data['protagonist'] = {k: v for k, v in prot.items() if v}

        # 配角列表
        supporting_text = self.widgets['supporting_characters'].get("0.0", "end").strip()
        supporting = []
        if supporting_text:
            lines = supporting_text.split('\n')
            for line in lines:
                parts = line.split('|')
                if len(parts) >= 4:
                    supporting.append({
                        'name': parts[0].strip(),
                        'role': parts[1].strip(),
                        'personality': parts[2].strip(),
                        'relationship': parts[3].strip()
                    })
                else:
                    supporting.append({'name': line.strip()})
        data['supporting_characters'] = supporting

        # 伏笔提示（JSON数组）
        try:
            foreshadowing = json.loads(self.widgets['foreshadowing_hints'].get().strip() or '[]')
            if isinstance(foreshadowing, list):
                data['foreshadowing_hints'] = foreshadowing
            else:
                data['foreshadowing_hints'] = []
        except:
            data['foreshadowing_hints'] = []

        return data

    def _clear_form(self):
        """清空所有表单控件"""
        self._set_widgets_state("normal")
        for key, widget in self.widgets.items():
            if isinstance(widget, ctk.CTkEntry):
                widget.delete(0, "end")
            elif isinstance(widget, ctk.CTkTextbox):
                widget.delete("0.0", "end")
        self._set_widgets_state("disabled" if not self.is_editable else "normal")

    def on_show(self):
        """页面激活时刷新数据"""
        project = self.app.app_state.get_current_project()
        if project:
            self.project_label.configure(text=f"当前项目: {project}")
            self._load_setting()
        else:
            self.project_label.configure(text="当前项目: 未选择")
            self._set_status("请先选择项目", "#ff6b6b")
            self._clear_form()
            self._set_widgets_state("disabled")

    def _load_setting(self):
        """从文件加载设定并显示"""
        project = self.app.app_state.get_current_project()
        if not project:
            return

        try:
            data = self.fm.load_json(project, "settings.json")
            if not data:
                self._set_status("⚠️ 设定文件不存在，请先创建项目。", "#ffc107")
                self._clear_form()
                self._set_widgets_state("disabled")
                return

            self.setting_data = data
            self._populate_form(data)
            # 状态已在 _populate_form 中设置，但确保最终状态正确
            self._set_widgets_state("disabled" if not self.is_editable else "normal")
            self._set_status(f"✅ 设定加载成功", "#69db7c")
        except Exception as e:
            self._set_status(f"❌ 加载失败: {str(e)}", "#ff6b6b")
            self._clear_form()
            self._set_widgets_state("disabled")

    def _save_setting(self):
        """保存编辑器中的内容到文件"""
        project = self.app.app_state.get_current_project()
        if not project:
            self._set_status("请先选择项目", "#ff6b6b")
            return

        try:
            new_data = self._collect_form_data()
            # 合并原有的可能缺失的字段（如theme, style等），避免丢失
            if self.setting_data:
                for key in ['theme', 'style']:
                    if key in self.setting_data:
                        new_data[key] = self.setting_data[key]
            self.fm.save_json(project, "settings.json", new_data)
            self.setting_data = new_data
            self._set_status("✅ 设定已保存成功！", "#69db7c")
        except Exception as e:
            self._set_status(f"❌ 保存失败: {str(e)}", "#ff6b6b")

    def _toggle_edit(self):
        """切换编辑模式"""
        self.is_editable = not self.is_editable
        if self.is_editable:
            self._set_widgets_state("normal")
            self.edit_toggle_btn.configure(text="🔒 锁定", fg_color="#dc3545", hover_color="#c82333")
            self._set_status("✏️ 编辑模式已开启，修改后请点击保存。", "#ffc107")
        else:
            self._set_widgets_state("disabled")
            self.edit_toggle_btn.configure(text="✏️ 编辑", fg_color="#6c757d", hover_color="#5a6268")
            self._set_status("🔒 已锁定，只读模式。", "#888")
            # 重新加载以丢弃未保存的更改
            self._load_setting()

    def _set_status(self, msg, color="#888"):
        self.status_label.configure(text=msg, text_color=color)