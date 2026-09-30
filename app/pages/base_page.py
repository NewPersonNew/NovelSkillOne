# -*- coding: utf-8 -*-
__author__ = "gezhaoqiang"
__date__ = "2026/8/28"

# app/pages/base_page.py
import customtkinter as ctk

class BasePage(ctk.CTkFrame):
    def __init__(self, master, app, **kwargs):
        super().__init__(master, **kwargs)
        self.app = app  # 主应用引用，可访问状态、切换页面等
        self._create_widgets()

    def _create_widgets(self):
        """子类重写，创建界面组件"""
        raise NotImplementedError

    def on_show(self):
        """当页面被切换到前台时调用，可用于刷新数据"""
        pass