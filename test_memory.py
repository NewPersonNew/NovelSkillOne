# -*- coding: utf-8 -*-
__author__ = "gezhaoqiang"
__date__ = "2026/8/27"

# test_memory.py
from memory.state_tracker import StateTracker
from memory.vector_retriever import VectorRetriever

if __name__ == "__main__":
    project = "我的第一本小说"

    print("=" * 50)
    print("🧠 测试状态追踪器 (StateTracker)")
    print("=" * 50)

    tracker = StateTracker(project)

    # 1. 模拟更新角色状态
    tracker.update_character("林渊", {
        "description": "炼气期三层，混沌灵根持有者，性格冷静隐忍",
        "status": "正在逃亡中",
        "level": "炼气期三层",
        "location": "星际废墟外围"
    })
    tracker.update_character("神秘仙尊", {
        "description": "寄居在林渊识海中的残魂，自称上古仙帝",
        "status": "沉睡中，偶尔苏醒",
    })

    # 2. 模拟记录剧情节点
    tracker.add_plot_point(1, "林渊在废墟发现青铜古棺，激活传承试炼", is_major=True)
    tracker.add_plot_point(2, "林渊成功觉醒混沌灵根，但被战友视为威胁", is_major=True)

    # 3. 模拟埋设伏笔
    tracker.add_foreshadowing("青铜古棺底部的第三道符文似乎与林渊的身世有关", expected_chapter=15)
    tracker.add_foreshadowing("神秘仙尊曾在万年前被一位‘故人’背叛", expected_chapter=25)

    # 4. 打印上下文摘要（这就是未来给 AI 的提示词素材）
    print("\n📋 生成第 3 章的上下文摘要：")
    print(tracker.get_context_for_chapter(3))

    print("\n" + "=" * 50)
    print("🔍 测试向量检索器 (VectorRetriever)")
    print("=" * 50)

    retriever = VectorRetriever(project)

    # 5. 模拟存入第1章和第2章的摘要
    retriever.add_chapter_summary(
        chapter_num=1,
        summary="林渊在废弃空间站执行侦察任务时，意外发现一具悬浮的青铜古棺，触发了上古仙道传承的试炼。",
        key_events="发现青铜古棺，仙尊残魂苏醒，试炼开始"
    )
    retriever.add_chapter_summary(
        chapter_num=2,
        summary="林渊通过试炼并觉醒混沌灵根，但体质异变引起战友恐慌和敌视，被迫逃离基地。",
        key_events="灵根觉醒，与战友决裂，仙尊告知混沌灵根的秘密"
    )

    # 6. 模拟写第3章时，检索相关历史
    print("\n📖 为第3章（主题：逃亡中的奇遇）检索相关历史：")
    context = retriever.get_retrieved_context_prompt(
        query="林渊在逃亡途中遇到新的未知势力或遗迹",
        top_k=2
    )
    print(context)

    print("\n✅ 记忆层测试完成！所有状态已持久化到 data/ 目录中。")
