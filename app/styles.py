# -*- coding: utf-8 -*-
__author__ = "gezhaoqiang"
__date__ = "2026/8/28"

# app/styles.py
import customtkinter as ctk

# 字体常量（供各组件使用，但组件若不指定则会使用全局默认）
FONT_FAMILY = "Microsoft YaHei"
FONT_TITLE = (FONT_FAMILY, 18, "bold")
FONT_HEADING = (FONT_FAMILY, 15, "bold")
FONT_BODY = (FONT_FAMILY, 13)
FONT_SMALL = (FONT_FAMILY, 11)
FONT_EDITOR = (FONT_FAMILY, 14)

def configure_theme():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")