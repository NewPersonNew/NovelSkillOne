# -*- coding: utf-8 -*-
__author__ = "gezhaoqiang"
__date__ = "2026/8/28"

# app/pages/agents.py
import customtkinter as ctk
from app.pages.base_page import BasePage

class AgentsPage(BasePage):
    def _create_widgets(self):
        ctk.CTkLabel(self, text="🛠️ 设定工坊", font=("Arial", 24, "bold")).pack(pady=20)
        ctk.CTkLabel(self, text="（待实现）", font=("Arial", 16)).pack(pady=10)