# -*- coding: utf-8 -*-
__author__ = "gezhaoqiang"
__date__ = "2026/8/27"

# memory/vector_retriever.py
import os
import uuid
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from infrastructure.llm_client import LLMClient


class VectorRetriever:
    """
    基于 ChromaDB 的本地向量检索器。
    负责存储和检索小说章节的语义信息。
    """

    def __init__(self, project_name: str):
        self.project_name = project_name
        self.llm = LLMClient()

        # 定义向量库存储路径：data/project_name/chroma_db/
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.persist_path = os.path.join(base_dir, "data", project_name, "chroma_db")
        os.makedirs(self.persist_path, exist_ok=True)

        # 初始化 ChromaDB 客户端（持久化模式）
        self.client = chromadb.PersistentClient(
            path=self.persist_path,
            settings=Settings(anonymized_telemetry=False)  # 关闭匿名遥测
        )

        # 获取或创建 Collection（相当于一张表）
        self.collection = self.client.get_or_create_collection(
            name="novel_chapters",
            metadata={"description": f"向量存储 for {project_name}"}
        )

    def _get_embedding(self, text: str) -> List[float]:
        """调用 Ollama 的 embedding 接口"""
        return self.llm.embed(text)

    def add_chapter_summary(self, chapter_num: int, summary: str, key_events: str = ""):
        """
        将本章的摘要和关键事件向量化入库。
        :param summary: 本章的核心剧情摘要（50-100字）
        :param key_events: 本章发生的具体事件（如：林渊突破筑基期、获得神秘铜棺）
        """
        # 合并文本以增强检索语义
        combined_text = f"第{chapter_num}章摘要：{summary}。关键事件：{key_events}"

        # 生成向量
        embedding = self._get_embedding(combined_text)

        # 生成唯一 ID（基于项目名和章节号）
        doc_id = f"{self.project_name}_ch{chapter_num}"

        # 存储元数据（方便后续过滤）
        metadata = {
            "chapter": chapter_num,
            "summary": summary,
            "key_events": key_events
        }

        # 插入或更新（ChromaDB 的 upsert）
        self.collection.upsert(
            ids=[doc_id],
            embeddings=[embedding],
            metadatas=[metadata],
            documents=[combined_text]  # 存储原文，方便展示
        )
        print(f"   📌 已向量化第 {chapter_num} 章并存入记忆库。")

    def retrieve_similar_chapters(
            self,
            query: str,
            top_k: int = 5,
            exclude_chapter: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        根据查询文本，检索语义最相似的 Top-K 个历史章节片段。
        :param query: 当前章节的剧情描述或目标
        :param top_k: 返回数量
        :param exclude_chapter: 排除某一章（防止检索到当前正在写的草稿）
        """
        if self.collection.count() == 0:
            return []  # 还没有存储任何章节

        # 生成查询向量
        query_embedding = self._get_embedding(query)

        # 执行检索
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )

        # 格式化返回结果
        retrieved = []
        if results and results['ids'] and len(results['ids'][0]) > 0:
            for i, doc_id in enumerate(results['ids'][0]):
                # 如果指定了排除章节，且元数据中的章节号匹配，则跳过
                meta = results['metadatas'][0][i]
                if exclude_chapter and meta.get('chapter') == exclude_chapter:
                    continue
                retrieved.append({
                    "chapter": meta.get('chapter'),
                    "summary": meta.get('summary'),
                    "key_events": meta.get('key_events'),
                    "content": results['documents'][0][i],
                    "similarity": 1 - results['distances'][0][i]  # distance越小越相似
                })

        return retrieved

    def get_retrieved_context_prompt(self, query: str, top_k: int = 3) -> str:
        """
        将检索到的历史片段格式化为 LLM 可读的 Prompt 字符串。
        这是给章节生成器用的核心接口。
        """
        results = self.retrieve_similar_chapters(query, top_k=top_k)
        if not results:
            return "（暂无相关历史章节可参考）"

        lines = ["【相关历史章节回顾（基于向量检索）】"]
        for item in results:
            lines.append(f"- 第{item['chapter']}章：{item['summary']}")
            if item.get('key_events'):
                lines.append(f"  关键事件：{item['key_events']}")
        return "\n".join(lines)