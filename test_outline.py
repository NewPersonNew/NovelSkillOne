# -*- coding: utf-8 -*-
__author__ = "gezhaoqiang"
__date__ = "2026/8/27"

# test_outline.py
from core.outline_generator import OutlineGenerator

if __name__ == "__main__":
    generator = OutlineGenerator()

    # 使用你刚刚生成设定的项目名称
    project_name = "我的第一本小说"

    try:
        outline = generator.generate_outline(project_name)

        print("\n" + "=" * 50)
        print("📚 生成的大纲预览（前 5 章）：")
        print("=" * 50)
        for chapter in outline.get('chapters', [])[:5]:
            print(f"第 {chapter['chapter_number']} 章：{chapter['title']}")
            print(f"   -> {chapter['summary']}")
            print("-" * 40)

        print(f"\n🎉 目录生成器测试完成！共生成 {len(outline.get('chapters', []))} 章。")
        print("💡 提示：你可以打开 data/我的第一本小说/outline.json 手动调整章节内容。")

    except FileNotFoundError as e:
        print(f"❌ 错误：{e}")
        print("请先运行 test_setting.py 生成设定。")
