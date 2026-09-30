# -*- coding: utf-8 -*-
__author__ = "gezhaoqiang"
__date__ = "2026/8/28"

# orchestration/workflow.py
import os
import json
from typing import Dict, Any, List, Optional
from core.chapter_generator import ChapterGenerator
from core.setting_builder import SettingBuilder
from core.outline_generator import OutlineGenerator
from infrastructure.file_manager import FileManager


class NovelWorkflow:
    """
    小说生成工作流编排器
    负责批量生成、进度追踪、断点续传
    """

    def __init__(self, project_name: str):
        self.project_name = project_name
        self.file_manager = FileManager()
        self.setting_builder = SettingBuilder()
        self.outline_generator = OutlineGenerator()

        # 加载已存在的设定和大纲
        self.setting = self.setting_builder.load_existing_setting(project_name)
        self.outline = self.outline_generator.load_existing_outline(project_name)

        if not self.setting or not self.outline:
            raise FileNotFoundError(f"项目 '{project_name}' 的设定或大纲不完整。")

        self.total_chapters = len(self.outline.get('chapters', []))

        # 工作流进度文件
        self.progress_file = "workflow_progress.json"
        self.progress = self._load_progress()

        # 章节生成器（延迟初始化）
        self.generator = None

    def _load_progress(self) -> Dict[str, Any]:
        """加载工作流进度（用于断点续传）"""
        data = self.file_manager.load_json(self.project_name, self.progress_file)
        if not data:
            return {
                "last_completed_chapter": 0,  # 已完成定稿的最后一章
                "generated_but_unfinalized": [],  # 已生成草稿但未定稿的章节列表
                "finalized_chapters": []  # 已定稿章节列表
            }
        return data

    def _save_progress(self):
        """保存工作流进度"""
        self.file_manager.save_json(self.project_name, self.progress_file, self.progress)

    def _get_generator(self):
        """懒加载章节生成器（避免重复初始化）"""
        if self.generator is None:
            self.generator = ChapterGenerator(self.project_name)
        return self.generator

    def generate_all(self, start_from: int = 1, auto_finalize: bool = True, pause_after_each: bool = False):
        """
        批量生成从 start_from 到最后一章的所有章节。
        :param start_from: 从第几章开始（默认1）
        :param auto_finalize: 是否自动定稿（否则需要手动确认）
        :param pause_after_each: 每生成一章后暂停，等待用户输入继续（方便人工检查）
        """
        print(f"\n🚀 开始批量生成小说《{self.setting.get('novel_title', '未命名')}》")
        print(f"   总章节数: {self.total_chapters}")
        print(f"   起始章节: 第 {start_from} 章")
        print(f"   自动定稿: {'是' if auto_finalize else '否'}\n")

        # 检查是否有未定稿的章节（断点续传恢复）
        if self.progress['generated_but_unfinalized']:
            print(f"⚠️ 检测到未定稿章节: {self.progress['generated_but_unfinalized']}")
            if auto_finalize:
                print("   自动定稿模式已开启，将自动定稿这些章节...")
                for ch_num in self.progress['generated_but_unfinalized']:
                    self._finalize_existing_chapter(ch_num)
                self.progress['generated_but_unfinalized'] = []
                self._save_progress()
            else:
                print("   请运行 self.finalize_chapter(chapter_num) 手动定稿后再继续。")
                return

        # 开始生成循环
        for chapter_num in range(start_from, self.total_chapters + 1):
            # 检查是否已定稿（跳过已完成的）
            if chapter_num in self.progress['finalized_chapters']:
                print(f"   ⏭️ 第 {chapter_num} 章已定稿，跳过。")
                continue

            print(f"\n{'=' * 50}")
            print(f"📖 正在生成第 {chapter_num} / {self.total_chapters} 章")
            print(f"{'=' * 50}")

            try:
                # 生成草稿
                generator = self._get_generator()
                result = generator.generate_chapter(chapter_num)

                # 显示预览（前300字）
                preview = result['content'][:300].replace('\n', ' ')
                print(f"\n📝 预览: {preview}...\n")

                if auto_finalize:
                    # 自动定稿
                    generator.finalize_chapter(chapter_num, result['content'])
                    self.progress['finalized_chapters'].append(chapter_num)
                    print(f"   ✅ 第 {chapter_num} 章已自动定稿并存入记忆。")
                else:
                    # 标记为已生成但未定稿
                    if chapter_num not in self.progress['generated_but_unfinalized']:
                        self.progress['generated_but_unfinalized'].append(chapter_num)
                    print(f"   💾 第 {chapter_num} 章草稿已保存，等待定稿。")

                self._save_progress()

                if pause_after_each and chapter_num < self.total_chapters:
                    input("   ⏸️ 按 Enter 继续下一章...")

            except Exception as e:
                print(f"   ❌ 第 {chapter_num} 章生成失败: {e}")
                print("   进度已保存，修复后可以重新运行 workflow.generate_all() 继续。")
                break

    def _finalize_existing_chapter(self, chapter_num: int):
        """定稿一个已存在草稿的章节"""
        generator = self._get_generator()
        content = self.file_manager.load_text(
            self.project_name,
            f"chapters/chapter_{chapter_num}.txt"
        )
        if content:
            generator.finalize_chapter(chapter_num, content)
            self.progress['finalized_chapters'].append(chapter_num)
            if chapter_num in self.progress['generated_but_unfinalized']:
                self.progress['generated_but_unfinalized'].remove(chapter_num)
            self._save_progress()
            print(f"   ✅ 第 {chapter_num} 章已手动定稿。")

    def finalize_chapter(self, chapter_num: int):
        """外部调用的手动定稿接口"""
        if chapter_num in self.progress['finalized_chapters']:
            print(f"   ⚠️ 第 {chapter_num} 章已定稿。")
            return
        self._finalize_existing_chapter(chapter_num)

    def get_status(self) -> Dict[str, Any]:
        """获取当前工作流状态"""
        return {
            "total": self.total_chapters,
            "finalized": len(self.progress['finalized_chapters']),
            "generated_but_unfinalized": self.progress['generated_but_unfinalized'],
            "completion_rate": f"{len(self.progress['finalized_chapters'])}/{self.total_chapters} ({len(self.progress['finalized_chapters']) / self.total_chapters * 100:.1f}%)"
        }
