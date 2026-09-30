# -*- coding: utf-8 -*-
__author__ = "gezhaoqiang"
__date__ = "2026/8/27"

# test_setting.py
from core.setting_builder import SettingBuilder

if __name__ == "__main__":
    builder = SettingBuilder()

    # 模拟用户输入：一本“科幻修仙”题材的小说
    setting = builder.generate_setting(
        project_name="我的第一本小说",
        theme="科幻修仙，未来人类在星际废墟中发现了上古修仙传承",
        style="硬核科幻与古典仙侠的结合，冷峻理性的文风",
        protagonist="林渊",
        word_count=150000
    )

    print("\n" + "=" * 50)
    print("📚 生成的小说设定预览：")
    print("=" * 50)
    print(f"标题：{setting.get('novel_title')}")
    print(f"世界观：{setting.get('world_setting')[:100]}...")
    print(f"主角：{setting.get('protagonist').get('name')} - {setting.get('protagonist').get('personality')}")
    print(f"核心冲突：{setting.get('core_conflict')}")
    print("=" * 50)
    print("\n🎉 设定构建器测试完成！")
