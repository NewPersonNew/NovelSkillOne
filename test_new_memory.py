# -*- coding: utf-8 -*-
__author__ = "gezhaoqiang"
__date__ = "2026/8/28"

# test_new_memory.py
from core.chapter_generator import ChapterGenerator
from memory.db_manager import DatabaseManager
from orchestration.context_assembler import ContextAssembler

project = "我的第一本小说"

# 测试数据库
db = DatabaseManager(project)
db.insert_fact("林渊", "境界", "炼气期三层", 1)
db.insert_fact("林渊", "所在地", "星际废墟", 1)
print("插入事实:", db.get_facts("林渊"))

db.upsert_promise("林渊誓要查明青铜古棺的秘密", 1, 20)
print("活跃承诺:", db.get_active_promises())

# 测试上下文组装
assembler = ContextAssembler(project)
ctx = assembler.assemble(2)
print("上下文组装结果:", ctx)

# 测试章节生成（使用新上下文）
generator = ChapterGenerator(project)
result = generator.generate_chapter(2)  # 注意：这会使用新记忆系统
print("生成的第二章预览:", result['content'][:300])

# 定稿并更新记忆
generator.finalize_chapter(2, result['content'])
print("定稿完成，查看数据库事实:")
print(db.get_facts(chapter=2))