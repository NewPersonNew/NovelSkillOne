# -*- coding: utf-8 -*-
__author__ = "gezhaoqiang"
__date__ = "2026/8/27"

# core/outline_generator.py
import os
import json
import re
import yaml
from typing import Dict, Any, List
from infrastructure.llm_client import LLMClient
from infrastructure.file_manager import FileManager
from core.setting_builder import SettingBuilder


class OutlineGenerator:
    def __init__(self):
        self.llm = LLMClient()
        self.file_manager = FileManager()
        self.setting_builder = SettingBuilder()
        self.prompt_config = self._load_prompt()

    def _load_prompt(self) -> Dict[str, str]:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        prompt_path = os.path.join(base_dir, "config", "prompts", "outline_generator.yaml")
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _clean_json_response(self, raw_text: str) -> str:
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', raw_text, re.DOTALL)
        if json_match:
            return json_match.group(1).strip()
        brace_match = re.search(r'(\{.*\})', raw_text, re.DOTALL)
        if brace_match:
            return brace_match.group(1).strip()
        return raw_text.strip()

    def _calculate_chapter_count(self, total_words: int, words_per_chapter: int = 3000) -> int:
        count = max(5, total_words // words_per_chapter)
        return min(count, 150)

    def _generate_volume_outline(self, volume_info: Dict, total_chapters_in_volume: int,
                                   previous_bridge: str = "") -> Dict:
        """为单卷生成章节大纲"""
        user_prompt = self.prompt_config['volume_outline_template'].format(
            volume_number=volume_info['volume_number'],
            volume_title=volume_info.get('title', '未命名卷'),
            volume_summary=volume_info.get('summary', ''),
            key_events="、".join(volume_info.get('key_events', [])),
            world_change=volume_info.get('world_change', '无变化'),
            bridge_from_previous=previous_bridge if previous_bridge else "（第一卷，无前情）",
            bridge_to_next=volume_info.get('bridge_to_next', ''),
            chapter_count=total_chapters_in_volume
        )
        system_prompt = self.prompt_config['system_prompt']
        raw_response = self.llm.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.8
        )
        cleaned = self._clean_json_response(raw_response)
        return json.loads(cleaned)

    def generate_outline(self, project_name: str) -> Dict[str, Any]:
        print(f"📋 正在为项目 '{project_name}' 生成章节大纲...")
        setting_data = self.setting_builder.load_existing_setting(project_name)
        if not setting_data:
            raise FileNotFoundError(f"项目 '{project_name}' 的 settings.json 未找到。")

        total_words = setting_data.get('word_count', 100000)
        volumes = setting_data.get('volumes', [])
        all_chapters = []
        volume_meta = []

        # 如果设定中包含分卷，按卷生成大纲
        if volumes and len(volumes) > 1:
            print(f"  检测到 {len(volumes)} 卷，逐卷生成大纲...")
            # 根据总字数估算总章节数
            total_chapters = self._calculate_chapter_count(total_words)
            # 按字数比例分配各卷章节数（可用平均分配，或根据卷的剧情权重调整）
            chapters_per_volume = max(3, total_chapters // len(volumes))
            # 剩余章节分配给最后一卷
            remaining = total_chapters - chapters_per_volume * (len(volumes) - 1)
            if remaining < 3:
                remaining = 3

            prev_bridge = ""
            chapter_start = 1
            for idx, vol in enumerate(volumes):
                vol_number = vol.get('volume_number', idx+1)
                if idx == len(volumes) - 1:
                    count = remaining
                else:
                    count = chapters_per_volume

                print(f"     生成第 {vol_number} 卷 ({count} 章)...")
                try:
                    volume_outline = self._generate_volume_outline(
                        volume_info=vol,
                        total_chapters_in_volume=count,
                        previous_bridge=prev_bridge
                    )
                    # 获取本卷章节列表，并添加卷号信息
                    vol_chapters = volume_outline.get('chapters', [])
                    for ch in vol_chapters:
                        ch['volume'] = vol_number
                        ch['volume_title'] = vol.get('title', '')
                        # 全局章节号从1开始连续
                        ch['chapter_number'] = chapter_start
                        chapter_start += 1
                    all_chapters.extend(vol_chapters)
                    # 记录卷元信息（起止章节）
                    volume_meta.append({
                        'volume_number': vol_number,
                        'title': vol.get('title', ''),
                        'summary': vol.get('summary', ''),
                        'chapter_start': vol_chapters[0]['chapter_number'] if vol_chapters else 1,
                        'chapter_end': vol_chapters[-1]['chapter_number'] if vol_chapters else 1,
                        'key_events': vol.get('key_events', []),
                        'world_change': vol.get('world_change', ''),
                        'bridge_to_next': vol.get('bridge_to_next', '')
                    })
                    # 更新上一卷的衔接（用于下一卷）
                    prev_bridge = vol.get('bridge_to_next', '')
                except Exception as e:
                    print(f"      ⚠️ 第 {vol_number} 卷生成失败: {e}")
                    continue

            outline_data = {
                'chapters': all_chapters,
                'volumes': volume_meta,
                'total_chapters': len(all_chapters)
            }

        else:
            # 兼容旧模式：无分卷设定时一次性生成全本大纲
            print("  未检测到分卷规划，使用全本大纲生成模式...")
            outline_data = self._generate_legacy_outline(setting_data, total_words)

        # 保存大纲
        self.file_manager.save_json(project_name, "outline.json", outline_data)
        print(f"💾 大纲已保存至 data/{project_name}/outline.json")
        return outline_data

    def _generate_legacy_outline(self, setting_data: Dict, total_words: int) -> Dict:
        """原有的一次性生成全本大纲逻辑（保留兼容）"""
        chapter_count = self._calculate_chapter_count(total_words)
        setting_json_str = json.dumps(setting_data, ensure_ascii=False, indent=2)
        user_prompt = self.prompt_config['user_prompt_template'].format(
            setting_json=setting_json_str,
            chapter_count=chapter_count
        )
        system_prompt = self.prompt_config['system_prompt']
        raw_response = self.llm.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.8
        )
        cleaned = self._clean_json_response(raw_response)
        data = json.loads(cleaned)
        # 为章节添加卷号（默认卷号为1）
        for ch in data.get('chapters', []):
            ch['volume'] = 1
            ch['volume_title'] = ''
        data['volumes'] = [{
            'volume_number': 1,
            'title': '全书',
            'chapter_start': 1,
            'chapter_end': len(data.get('chapters', []))
        }]
        return data

    def load_existing_outline(self, project_name: str) -> Dict[str, Any]:
        return self.file_manager.load_json(project_name, "outline.json")