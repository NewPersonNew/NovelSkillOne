# -*- coding: utf-8 -*-
__author__ = "gezhaoqiang"
__date__ = "2026/8/28"

# main.py
import sys
import os
from orchestration.workflow import NovelWorkflow
from consistency_checker import ConsistencyChecker
from core.setting_builder import SettingBuilder
from core.outline_generator import OutlineGenerator


def print_banner():
    print("""
╔══════════════════════════════════════════════╗
║    📚  NovelSkillOne - AI 小说生成引擎     ║
║    基于 Qwen2.5 + 本地化记忆管理           ║
╚══════════════════════════════════════════════╝
    """)


def main():
    print_banner()

    if len(sys.argv) < 2:
        print("用法：")
        print("  python main.py init      - 初始化新项目（生成设定+大纲）")
        print("  python main.py generate  - 批量生成所有章节（自动定稿）")
        print("  python main.py status    - 查看当前进度")
        print("  python main.py check     - 运行一致性检查")
        print("  python main.py finalize <章节号> - 手动定稿指定章节")
        return

    command = sys.argv[1]
    project_name = "我的第一本小说"  # 后续可以改为动态输入

    try:
        if command == "init":
            print("📖 开始初始化新项目...")
            # 从命令行读取设定参数（或从配置文件）
            builder = SettingBuilder()
            setting = builder.generate_setting(
                project_name=project_name,
                theme=input("请输入题材（如：科幻修仙）: "),
                style=input("请输入文风（如：冷峻理性）: "),
                protagonist=input("请输入主角姓名: "),
                word_count=int(input("请输入目标总字数: "))
            )
            print(f"✅ 设定生成完成！")

            outline_gen = OutlineGenerator()
            outline = outline_gen.generate_outline(project_name)
            print(f"✅ 大纲生成完成！共 {len(outline.get('chapters', []))} 章。")

        elif command == "generate":
            workflow = NovelWorkflow(project_name)
            status = workflow.get_status()
            print(f"当前进度: {status['completion_rate']}")
            confirm = input(f"将从第 {status['finalized'] + 1} 章开始生成，是否继续？(y/n): ")
            if confirm.lower() == 'y':
                workflow.generate_all(start_from=status['finalized'] + 1, auto_finalize=True)

        elif command == "status":
            workflow = NovelWorkflow(project_name)
            status = workflow.get_status()
            print(f"\n📊 项目进度: {project_name}")
            print(f"   总章节: {status['total']}")
            print(f"   已定稿: {status['finalized']}")
            print(f"   未定稿草稿: {status['generated_but_unfinalized']}")
            print(f"   完成度: {status['completion_rate']}")

        elif command == "check":
            checker = ConsistencyChecker(project_name)
            print(checker.report_summary())

        elif command == "finalize":
            if len(sys.argv) < 3:
                print("请指定章节号，如: python main.py finalize 5")
                return
            chapter_num = int(sys.argv[2])
            workflow = NovelWorkflow(project_name)
            workflow.finalize_chapter(chapter_num)

        else:
            print(f"未知命令: {command}")

    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()