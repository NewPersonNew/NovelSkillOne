# -*- coding: utf-8 -*-
__author__ = "gezhaoqiang"
__date__ = "2026/8/27"

# test_setup.py
from infrastructure.llm_client import LLMClient
from infrastructure.file_manager import FileManager

if __name__ == "__main__":
    print("1. 测试 LLM 连接...")
    client = LLMClient()
    response = client.generate(
        prompt="写一句关于'秋夜'的唯美句子。",
        system_prompt="你是一位文笔细腻的散文家。"
    )
    print(f"LLM 回复: {response}")

    print("\n2. 测试文件管理器...")
    fm = FileManager()
    fm.save_text("test_project", "hello.txt", "测试内容")
    content = fm.load_text("test_project", "hello.txt")
    print(f"文件读写成功: {content}")

    print("\n✅ 环境验证通过！准备进入核心逻辑开发。")
