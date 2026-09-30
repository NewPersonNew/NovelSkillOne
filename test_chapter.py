# -*- coding: utf-8 -*-
__author__ = "gezhaoqiang"
__date__ = "2026/8/28"

# test_chapter.py
from core.chapter_generator import ChapterGenerator

if __name__ == "__main__":
    project = "我的第一本小说"

    # 1. 初始化生成器
    generator = ChapterGenerator(project)

    # 2. 生成第一章
    result = generator.generate_chapter(chapter_num=1)

    # 3. 打印预览
    print("\n" + "=" * 60)
    print(f"📖 第 {result['chapter_num']} 章：{result['title']}")
    print("=" * 60)
    print(f"本章目标：{result['summary']}\n")
    print("【正文预览（前500字）】")
    print(result['content'][:500] + "...\n")
    print("=" * 60)

    # 4. 询问是否定稿
    confirm = input("\n🔍 请阅读以上草稿，是否定稿此章？(y/n): ")
    if confirm.lower() == 'y':
        generator.finalize_chapter(1, result['content'])
        print("🎉 第一章定稿完成！已写入长期记忆。")
    else:
        print("💡 你可以手动修改 data/我的第一本小说/chapters/chapter_1.txt 后，再调用 finalize_chapter。")
