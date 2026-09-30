# -*- coding: utf-8 -*-
__author__ = "gezhaoqiang"
__date__ = "2026/8/28"

# app.py
import gradio as gr
import json
import sqlite3
from core.chapter_generator import ChapterGenerator
from memory.db_manager import DatabaseManager
from orchestration.context_assembler import ContextAssembler
from infrastructure.file_manager import FileManager

# ---------- 全局状态 ----------
PROJECT_NAME = "我的第一本小说"
generator = ChapterGenerator(PROJECT_NAME)
file_manager = FileManager()
assembler = ContextAssembler(PROJECT_NAME)  # 注意：assembler 内部也有数据库连接，但我们尽量少用，主要用独立连接


# ---------- 辅助函数 ----------
def get_chapter_list():
    """获取所有章节列表"""
    chapters = generator.outline.get('chapters', [])
    finalized = []
    for i, ch in enumerate(chapters, 1):
        content = file_manager.load_text(PROJECT_NAME, f"chapters/chapter_{i}.txt")
        status = "✅ 已定稿" if content else "⏳ 待生成"
        finalized.append(f"第{i}章：{ch['title']} ({status})")
    return finalized


def get_project_status():
    """生成项目状态摘要（使用独立数据库连接）"""
    temp_db = None
    try:
        temp_db = DatabaseManager(PROJECT_NAME)
        facts = temp_db.get_facts(limit=100)
        promises = temp_db.get_active_promises()

        characters = []
        cursor = temp_db.conn.cursor()
        cursor.execute("SELECT name, last_updated_chapter FROM characters")
        for row in cursor.fetchall():
            characters.append(f"{row[0]} (更新于第{row[1]}章)")

        total_chapters = len(generator.outline.get('chapters', []))
        finalized_chapters = len(file_manager.list_chapters(PROJECT_NAME))

        return f"""
📊 项目：{PROJECT_NAME}
📖 总章节：{total_chapters}
✅ 已定稿：{finalized_chapters}
📝 事实总数：{len(facts)}
🎯 活跃伏笔：{len(promises)}
👥 角色数：{len(characters)}

【角色列表】
{chr(10).join(characters)}

【待回收伏笔】
{chr(10).join([p['description'] for p in promises]) if promises else '（无）'}
"""
    except Exception as e:
        import traceback
        return f"❌ 错误：{str(e)}\n\n堆栈：\n{traceback.format_exc()}"
    finally:
        if temp_db:
            temp_db.close()


def generate_chapter_ui(chapter_num, user_guidance):
    """生成章节（使用现有generator）"""
    if not chapter_num:
        return "请选择章节号", "", ""
    try:
        result = generator.generate_chapter(int(chapter_num), user_guidance)
        preview = result['content'][:500] + "..."
        return f"✅ 第{chapter_num}章生成完成！\n文件：{result['file_path']}", preview, result['content']
    except Exception as e:
        import traceback
        return f"❌ 生成失败：{str(e)}\n{traceback.format_exc()}", "", ""


def finalize_chapter_ui(chapter_num, content):
    """定稿章节"""
    if not chapter_num or not content:
        return "❌ 请先生成章节内容"
    try:
        generator.finalize_chapter(int(chapter_num), content)
        return f"✅ 第{chapter_num}章定稿完成，记忆已更新！"
    except Exception as e:
        import traceback
        return f"❌ 定稿失败：{str(e)}\n{traceback.format_exc()}"


def load_chapter_ui(chapter_num):
    """加载已生成内容"""
    if not chapter_num:
        return "", ""
    content = file_manager.load_text(PROJECT_NAME, f"chapters/chapter_{chapter_num}.txt")
    if content:
        return content, f"✅ 已加载第{chapter_num}章（{len(content)}字符）"
    return "", f"⚠️ 第{chapter_num}章尚未生成"


def show_context_ui(chapter_num):
    """显示上下文（使用独立assembler，内部可能也会用数据库，但assembler已经封装了）"""
    if not chapter_num:
        return "请选择章节号"
    try:
        # 由于 assembler 内部使用 db，也可能有线程问题，这里我们也用独立的 ContextAssembler 实例
        temp_assembler = ContextAssembler(PROJECT_NAME)
        context = temp_assembler.assemble(int(chapter_num))
        # 组装文本
        formatted = []
        formatted.append("【世界观设定】")
        formatted.append(context.get('world_rules', '')[:200] + "...")
        formatted.append("\n【角色状态】")
        for name, info in context.get('characters', {}).items():
            state = info.get('current_state', {})
            formatted.append(f"- {name}: {state.get('status', '正常')}")
        formatted.append("\n【活跃伏笔】")
        for p in context.get('active_promises', []):
            formatted.append(f"- {p['description']}")
        formatted.append("\n【近期事实】")
        for f in context.get('recent_facts', [])[-5:]:
            formatted.append(f"- {f['entity']} → {f['attribute']} = {f['value']}")
        return "\n".join(formatted)
    except Exception as e:
        import traceback
        return f"❌ 加载上下文失败：{str(e)}\n{traceback.format_exc()}"


def show_facts():
    """显示事实（独立连接）"""
    temp_db = None
    try:
        temp_db = DatabaseManager(PROJECT_NAME)
        facts = temp_db.get_facts(limit=50)
        if not facts:
            return "（暂无事实）"
        lines = []
        for f in facts:
            lines.append(f"第{f['chapter']}章 | {f['entity']} | {f['attribute']} = {f['value']}")
        return "\n".join(lines)
    except Exception as e:
        import traceback
        return f"❌ 错误：{str(e)}\n{traceback.format_exc()}"
    finally:
        if temp_db:
            temp_db.close()


def show_promises():
    """显示承诺（独立连接）"""
    temp_db = None
    try:
        temp_db = DatabaseManager(PROJECT_NAME)
        cursor = temp_db.conn.cursor()
        cursor.execute("SELECT * FROM promises ORDER BY id DESC")
        rows = cursor.fetchall()
        if not rows:
            return "（暂无承诺）"
        lines = []
        for r in rows:
            status = "✅ 已回收" if r['status'] == 'resolved' else "⏳ 活跃"
            lines.append(f"#{r['id']} | {r['description']} | 埋于第{r['planted_chapter']}章 | {status}")
        return "\n".join(lines)
    except Exception as e:
        import traceback
        return f"❌ 错误：{str(e)}\n{traceback.format_exc()}"
    finally:
        if temp_db:
            temp_db.close()


def get_chapter_options():
    chapters = generator.outline.get('chapters', [])
    return [str(i + 1) for i in range(len(chapters))]


# ---------- 构建UI ----------
with gr.Blocks(title="NovelSkillOne - AI小说创作系统", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 📚 NovelSkillOne - AI驱动的长篇小说创作系统")
    gr.Markdown(f"**当前项目：{PROJECT_NAME}**")

    with gr.Tabs():
        # 标签页1：项目看板
        with gr.TabItem("📊 项目看板"):
            with gr.Row():
                status_btn = gr.Button("🔄 刷新状态")
                status_output = gr.Textbox(label="项目状态", lines=20, interactive=False)
            status_btn.click(fn=get_project_status, outputs=status_output)
            demo.load(fn=get_project_status, outputs=status_output)
            with gr.Row():
                gr.Markdown("### 📋 章节列表")
                chapter_list = gr.Textbox(label="", lines=15, interactive=False)
                refresh_btn = gr.Button("刷新章节列表")
                refresh_btn.click(fn=lambda: "\n".join(get_chapter_list()), outputs=chapter_list)
            demo.load(fn=lambda: "\n".join(get_chapter_list()), outputs=chapter_list)

        # 标签页2：创作工作台
        with gr.TabItem("✍️ 创作工作台"):
            with gr.Row():
                with gr.Column(scale=1):
                    chapter_selector = gr.Dropdown(
                        choices=get_chapter_options(),
                        label="选择章节号",
                        value="1"
                    )
                    user_guidance = gr.Textbox(
                        label="用户指导（可选）",
                        placeholder="例如：本章重点描写林渊和神秘仙尊的第一次对话",
                        lines=3
                    )
                    load_btn = gr.Button("📖 加载已有内容")
                    generate_btn = gr.Button("🚀 生成本章", variant="primary")
                    context_btn = gr.Button("🔍 查看上下文")

                with gr.Column(scale=2):
                    status_box = gr.Textbox(label="操作状态", lines=3, interactive=False)
                    preview_box = gr.Textbox(label="内容预览", lines=5, interactive=False)

            with gr.Row():
                with gr.Column(scale=3):
                    content_editor = gr.Textbox(
                        label="📝 章节内容（可编辑）",
                        lines=25,
                        interactive=True,
                        placeholder="章节内容将在此显示..."
                    )
                with gr.Column(scale=1):
                    context_display = gr.Textbox(
                        label="🧠 写前上下文",
                        lines=25,
                        interactive=False,
                        placeholder="点击'查看上下文'按钮..."
                    )

            with gr.Row():
                finalize_btn = gr.Button("🔒 定稿本章", variant="stop")

            generate_btn.click(
                fn=generate_chapter_ui,
                inputs=[chapter_selector, user_guidance],
                outputs=[status_box, preview_box, content_editor]
            )
            load_btn.click(
                fn=load_chapter_ui,
                inputs=[chapter_selector],
                outputs=[content_editor, status_box]
            )
            context_btn.click(
                fn=show_context_ui,
                inputs=[chapter_selector],
                outputs=[context_display]
            )
            finalize_btn.click(
                fn=finalize_chapter_ui,
                inputs=[chapter_selector, content_editor],
                outputs=[status_box]
            )

        # 标签页3：记忆浏览器
        with gr.TabItem("🔍 记忆浏览器"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### 📋 事实列表")
                    facts_btn = gr.Button("刷新事实")
                    facts_output = gr.Textbox(label="事实", lines=15, interactive=False)
                with gr.Column():
                    gr.Markdown("### 🎯 承诺/伏笔列表")
                    promises_btn = gr.Button("刷新承诺")
                    promises_output = gr.Textbox(label="承诺", lines=15, interactive=False)

            facts_btn.click(fn=show_facts, outputs=facts_output)
            promises_btn.click(fn=show_promises, outputs=promises_output)
            demo.load(fn=show_facts, outputs=facts_output)
            demo.load(fn=show_promises, outputs=promises_output)

        # ===== 标签页4：智能Agent =====
        with gr.TabItem("🧠 智能Agent"):
            gr.Markdown("### 🔍 一致性检查")
            check_btn = gr.Button("检查最新章节")
            check_output = gr.Textbox(label="检查结果", lines=10, interactive=False)

            gr.Markdown("### 🎯 伏笔分析")
            scan_btn = gr.Button("扫描伏笔状态")
            scan_output = gr.Textbox(label="分析结果", lines=10, interactive=False)


            # 定义回调函数
            def run_consistency_check():
                from agents.consistency_agent import ConsistencyAgent
                from infrastructure.file_manager import FileManager
                fm = FileManager()
                chapters = fm.list_chapters(PROJECT_NAME)
                if not chapters:
                    return "⚠️ 没有已生成的章节可检查"
                # 检查最新一章
                latest = sorted(chapters)[-1]
                ch_num = int(latest.split('_')[1].split('.')[0])
                content = fm.load_text(PROJECT_NAME, f"chapters/{latest}")
                agent = ConsistencyAgent(PROJECT_NAME)
                try:
                    warnings = agent.check_chapter(ch_num, content)
                    if warnings:
                        return "⚠️ 发现问题：\n" + "\n".join(warnings)
                    return f"✅ 第{ch_num}章一致性检查通过！"
                finally:
                    agent.close()


            def run_foreshadowing_scan():
                from agents.foreshadowing_agent import ForeshadowingAgent
                agent = ForeshadowingAgent(PROJECT_NAME)
                try:
                    result = agent.scan_promises()
                    if "info" in result:
                        return result["info"]
                    return "📊 伏笔分析结果：\n" + result.get("raw_response", "无分析结果")
                finally:
                    agent.close()


            check_btn.click(fn=run_consistency_check, outputs=check_output)
            scan_btn.click(fn=run_foreshadowing_scan, outputs=scan_output)

# 在 app.py 中添加新标签页


# ---------- 启动 ----------
if __name__ == "__main__":
    demo.launch(share=False, server_name="127.0.0.1", server_port=7860)