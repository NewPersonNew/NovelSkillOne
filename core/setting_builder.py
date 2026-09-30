# -*- coding: utf-8 -*-
__author__ = "gezhaoqiang"
__date__ = "2026/8/27"

import os
import json
import re
import yaml
from typing import Dict, Any, Optional
from infrastructure.llm_client import LLMClient
from infrastructure.file_manager import FileManager


class SettingBuilder:
    def __init__(self):
        self.llm = LLMClient()
        self.file_manager = FileManager()
        self.prompt_config = self._load_prompt()

    def _load_prompt(self) -> Dict[str, str]:
        """加载设定生成的提示词模板"""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        prompt_path = os.path.join(base_dir, "config", "prompts", "setting_builder.yaml")
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _clean_json_response(self, raw_text: str) -> str:
        """清洗 LLM 返回的文本，提取纯 JSON"""
        # 提取 ```json ... ``` 代码块
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', raw_text, re.DOTALL)
        if json_match:
            return json_match.group(1).strip()
        # 尝试提取第一个 { 到最后一个 }
        brace_match = re.search(r'(\{.*\})', raw_text, re.DOTALL)
        if brace_match:
            return brace_match.group(1).strip()
        return raw_text.strip()

    def generate_setting(
        self,
        project_name: str,
        novel_title: Optional[str] = None,
        theme: str = "",
        style: str = "",
        protagonist: str = "",
        word_count: int = 100000,
        tone: str = "正剧",
        extra_info: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        生成小说设定并保存到 data/{project_name}/settings.json
        :param project_name: 项目名称（也是存储目录名）
        :param novel_title: 小说标题（若未提供则使用 project_name）
        :param theme: 题材
        :param style: 文风
        :param protagonist: 主角姓名
        :param word_count: 目标总字数
        :param tone: 故事基调
        :param extra_info: 可选额外信息（主角背景、女主、反派等）
        """
        if novel_title is None:
            novel_title = project_name

        # 计算卷数：每卷约30万字，最少3卷
        words_per_volume = 300000
        volume_count = max(3, word_count // words_per_volume)
        if word_count % words_per_volume > 0:
            volume_count += 1

        print(f"📖 目标字数 {word_count} 字，将规划 {volume_count} 卷。")

        # 构建额外信息文本
        extra_text = ""
        if extra_info:
            parts = []
            if extra_info.get('protagonist_bg'):
                parts.append(f"主角背景：{extra_info['protagonist_bg']}")
            if extra_info.get('heroine'):
                parts.append(f"女主角/重要女性：{extra_info['heroine']}")
            if extra_info.get('villain'):
                parts.append(f"反派Boss：{extra_info['villain']}")
            if extra_info.get('family'):
                parts.append(f"父母/家人：{extra_info['family']}")
            if extra_info.get('world_special'):
                parts.append(f"世界观特点：{extra_info['world_special']}")
            if parts:
                extra_text = "\n".join(parts)

        # 格式化用户提示
        user_prompt = self.prompt_config['user_prompt_template'].format(
            novel_title=novel_title,
            theme=theme,
            style=style,
            tone=tone,
            protagonist=protagonist,
            word_count=word_count,
            volume_count=volume_count,
            words_per_volume=word_count // volume_count,
            extra_info=extra_text
        )
        system_prompt = self.prompt_config['system_prompt']

        # 调用 LLM
        try:
            raw_response = self.llm.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.9
            )
            print("✅ LLM 设定生成完成，正在解析 JSON...")
        except Exception as e:
            print(f"❌ LLM 调用失败: {e}")
            raise

        # 清洗并解析 JSON
        cleaned_json = self._clean_json_response(raw_response)
        try:
            setting_data = json.loads(cleaned_json)
        except json.JSONDecodeError as e:
            print("❌ JSON 解析失败，原始返回内容如下：")
            print(raw_response[:500] + "...")
            raise ValueError(f"LLM 返回了无效的 JSON 格式: {e}")

        # 确保小说标题与用户输入一致
        if setting_data.get('novel_title') != novel_title:
            print(f"⚠️ 警告：LLM 将小说标题修改为 {setting_data['novel_title']}，已强制修正为 {novel_title}")
            setting_data['novel_title'] = novel_title

        # 确保主角姓名一致
        if setting_data.get('protagonist', {}).get('name') != protagonist:
            print(f"⚠️ 警告：LLM 将主角名修改为 {setting_data['protagonist']['name']}，已强制修正为 {protagonist}")
            setting_data['protagonist']['name'] = protagonist

        # 保存到文件
        self.file_manager.save_json(project_name, "settings.json", setting_data)
        print(f"💾 设定已保存至 data/{project_name}/settings.json")
        return setting_data

    def load_existing_setting(self, project_name: str) -> Dict[str, Any]:
        """加载已存在的设定"""
        return self.file_manager.load_json(project_name, "settings.json")