# -*- coding: utf-8 -*-
__author__ = "gezhaoqiang"
__date__ = "2026/8/28"

# app/pages/project_init.py
import customtkinter as ctk
from app.pages.base_page import BasePage
from core.setting_builder import SettingBuilder
from app.styles import FONT_TITLE, FONT_HEADING, FONT_BODY, FONT_SMALL


class ProjectInitPage(BasePage):
    def _create_widgets(self):
        self.builder = SettingBuilder()
        self.scrollable_frame = ctk.CTkScrollableFrame(self)
        self.scrollable_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            self.scrollable_frame,
            text="🆕 新建小说项目",
            font=FONT_TITLE
        ).pack(pady=10)

        # ---- 基础信息 ----
        ctk.CTkLabel(
            self.scrollable_frame,
            text="📌 基础信息",
            font=FONT_HEADING
        ).pack(anchor="w", pady=(10, 5))

        frame1 = ctk.CTkFrame(self.scrollable_frame)
        frame1.pack(fill="x", pady=5)

        ctk.CTkLabel(frame1, text="项目名称 / 小说标题", font=FONT_BODY).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.project_name = ctk.CTkEntry(frame1, width=300, font=FONT_BODY)
        self.project_name.grid(row=0, column=1, padx=5, pady=5)
        ctk.CTkLabel(
            frame1,
            text="（将作为小说标题）",
            font=FONT_SMALL,
            text_color="#888"
        ).grid(row=0, column=2, padx=5, pady=5, sticky="w")

        ctk.CTkLabel(frame1, text="目标总字数", font=FONT_BODY).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.word_count = ctk.CTkEntry(frame1, width=200, font=FONT_BODY, placeholder_text="100000")
        self.word_count.grid(row=1, column=1, padx=5, pady=5)

        # ---- 故事核心 ----
        ctk.CTkLabel(
            self.scrollable_frame,
            text="📖 故事核心",
            font=FONT_HEADING
        ).pack(anchor="w", pady=(10, 5))

        frame2 = ctk.CTkFrame(self.scrollable_frame)
        frame2.pack(fill="x", pady=5)

        # 题材
        ctk.CTkLabel(frame2, text="题材", font=FONT_BODY).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.theme_var = ctk.StringVar(value="科幻")
        theme_options = ["科幻", "修仙", "都市", "历史", "奇幻", "悬疑", "言情", "其他"]
        self.theme_dropdown = ctk.CTkOptionMenu(
            frame2,
            variable=self.theme_var,
            values=theme_options,
            font=FONT_BODY,
            dropdown_font=FONT_BODY,
            width=150
        )
        self.theme_dropdown.grid(row=0, column=1, padx=5, pady=5)
        self.theme_custom = ctk.CTkEntry(frame2, width=150, font=FONT_BODY, placeholder_text="自定义")
        self.theme_custom.grid(row=0, column=2, padx=5, pady=5)

        # 文风（更丰富的选项+说明）
        ctk.CTkLabel(frame2, text="文风", font=FONT_BODY).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.style_var = ctk.StringVar(value="冷静理性")
        style_options = [
            "热血激昂",
            "冷静理性",
            "细腻婉约",
            "幽默风趣",
            "暗黑哥特",
            "诗意唯美",
            "简洁白描",
            "华丽繁复",
            "其他"
        ]
        self.style_dropdown = ctk.CTkOptionMenu(
            frame2,
            variable=self.style_var,
            values=style_options,
            font=FONT_BODY,
            dropdown_font=FONT_BODY,
            width=180
        )
        self.style_dropdown.grid(row=1, column=1, padx=5, pady=5)
        self.style_custom = ctk.CTkEntry(frame2, width=150, font=FONT_BODY, placeholder_text="自定义")
        self.style_custom.grid(row=1, column=2, padx=5, pady=5)
        ctk.CTkLabel(
            frame2,
            text="（语言风格，可自定义）",
            font=FONT_SMALL,
            text_color="#888"
        ).grid(row=2, column=1, columnspan=2, padx=5, pady=0, sticky="w")

        # 故事基调（更丰富的选项+说明）
        ctk.CTkLabel(frame2, text="故事基调", font=FONT_BODY).grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.tone_var = ctk.StringVar(value="正剧")
        tone_options = [
            "正剧（严肃写实）",
            "喜剧（幽默轻松）",
            "悲剧（沉重悲伤）",
            "燃向（热血励志）",
            "治愈（温暖抚慰）",
            "悬疑（紧张神秘）",
            "史诗（宏大壮阔）",
            "日常（平淡温馨）",
            "其他"
        ]
        self.tone_dropdown = ctk.CTkOptionMenu(
            frame2,
            variable=self.tone_var,
            values=tone_options,
            font=FONT_BODY,
            dropdown_font=FONT_BODY,
            width=180
        )
        self.tone_dropdown.grid(row=3, column=1, padx=5, pady=5)
        self.tone_custom = ctk.CTkEntry(frame2, width=150, font=FONT_BODY, placeholder_text="自定义")
        self.tone_custom.grid(row=3, column=2, padx=5, pady=5)
        ctk.CTkLabel(
            frame2,
            text="（情感底色和叙事态度，可自定义）",
            font=FONT_SMALL,
            text_color="#888"
        ).grid(row=4, column=1, columnspan=2, padx=5, pady=0, sticky="w")

        # ---- 角色信息 ----
        ctk.CTkLabel(
            self.scrollable_frame,
            text="👥 角色信息",
            font=FONT_HEADING
        ).pack(anchor="w", pady=(10, 5))

        frame3 = ctk.CTkFrame(self.scrollable_frame)
        frame3.pack(fill="x", pady=5)

        ctk.CTkLabel(frame3, text="主角姓名*", font=FONT_BODY).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.protagonist = ctk.CTkEntry(frame3, width=200, font=FONT_BODY)
        self.protagonist.grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(frame3, text="主角背景", font=FONT_BODY).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.protagonist_bg = ctk.CTkTextbox(frame3, height=60, width=400, font=FONT_BODY)
        self.protagonist_bg.grid(row=1, column=1, columnspan=2, padx=5, pady=5)

        ctk.CTkLabel(frame3, text="女主/重要女性", font=FONT_BODY).grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.heroine = ctk.CTkEntry(frame3, width=300, font=FONT_BODY, placeholder_text="姓名或设定")
        self.heroine.grid(row=2, column=1, columnspan=2, padx=5, pady=5)

        ctk.CTkLabel(frame3, text="反派Boss", font=FONT_BODY).grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.villain = ctk.CTkEntry(frame3, width=300, font=FONT_BODY, placeholder_text="姓名或设定")
        self.villain.grid(row=3, column=1, columnspan=2, padx=5, pady=5)

        ctk.CTkLabel(frame3, text="父母/家人", font=FONT_BODY).grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.family = ctk.CTkEntry(frame3, width=300, font=FONT_BODY, placeholder_text="姓名或设定")
        self.family.grid(row=4, column=1, columnspan=2, padx=5, pady=5)

        # ---- 世界观补充 ----
        ctk.CTkLabel(
            self.scrollable_frame,
            text="🌍 世界观补充（可选）",
            font=FONT_HEADING
        ).pack(anchor="w", pady=(10, 5))

        frame4 = ctk.CTkFrame(self.scrollable_frame)
        frame4.pack(fill="x", pady=5)

        ctk.CTkLabel(frame4, text="世界观特点", font=FONT_BODY).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.world_special = ctk.CTkEntry(frame4, width=400, font=FONT_BODY, placeholder_text="如：灵气复苏、星际殖民等")
        self.world_special.grid(row=0, column=1, padx=5, pady=5)

        # 创建按钮
        self.create_btn = ctk.CTkButton(
            self.scrollable_frame,
            text="🚀 创建项目",
            command=self._create_project,
            font=FONT_BODY,
            height=40
        )
        self.create_btn.pack(pady=20)

        self.status_label = ctk.CTkLabel(self.scrollable_frame, text="", font=FONT_BODY)
        self.status_label.pack(pady=5)

        self.preview_text = ctk.CTkTextbox(
            self.scrollable_frame,
            height=200,
            font=("Consolas", 12)
        )
        self.preview_text.pack(fill="x", pady=10)
        self.preview_text.pack_forget()

    def _create_project(self):
        name = self.project_name.get().strip()
        wc_text = self.word_count.get().strip()
        wc = int(wc_text) if wc_text.isdigit() else 100000

        theme = self.theme_var.get()
        custom_theme = self.theme_custom.get().strip()
        if custom_theme:
            theme = custom_theme

        style = self.style_var.get()
        custom_style = self.style_custom.get().strip()
        if custom_style:
            style = custom_style

        tone = self.tone_var.get()
        custom_tone = self.tone_custom.get().strip()
        if custom_tone:
            tone = custom_tone

        protagonist = self.protagonist.get().strip()
        if not name or not protagonist:
            self.status_label.configure(text="❌ 请至少填写项目名称和主角姓名", text_color="red")
            return

        extra = {
            'protagonist_bg': self.protagonist_bg.get("0.0", "end").strip(),
            'heroine': self.heroine.get().strip(),
            'villain': self.villain.get().strip(),
            'family': self.family.get().strip(),
            'world_special': self.world_special.get().strip(),
        }
        extra = {k: v for k, v in extra.items() if v}

        try:
            # 将项目名称作为小说标题传入
            setting = self.builder.generate_setting(
                project_name=name,
                novel_title=name,
                theme=theme,
                style=style,
                protagonist=protagonist,
                word_count=wc,
                tone=tone,
                extra_info=extra
            )
            self.app.app_state.add_project(name)
            self.app.app_state.set_current_project(name)
            self.app.sidebar.refresh_projects()

            import json
            self.preview_text.pack(fill="x", pady=10)
            self.preview_text.delete("0.0", "end")
            self.preview_text.insert("0.0", json.dumps(setting, ensure_ascii=False, indent=2))
            self.status_label.configure(text=f"✅ 项目 '{name}' 创建成功！", text_color="green")

            self.app.switch_page("settings")
        except Exception as e:
            self.status_label.configure(text=f"❌ 创建失败: {str(e)}", text_color="red")