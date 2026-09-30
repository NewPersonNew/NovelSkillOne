# -*- coding: utf-8 -*-
__author__ = "gezhaoqiang"
__date__ = "2026/8/27"

import requests
import yaml
import os


class LLMClient:
    def __init__(self, config_path: str = "config/settings.yaml"):
        # 获取项目根目录的绝对路径，防止 PyCharm 运行目录不对
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        full_config_path = os.path.join(base_dir, config_path)

        with open(full_config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        llm_cfg = config['llm']
        self.model = llm_cfg['model']
        self.base_url = llm_cfg['base_url']
        self.temperature = llm_cfg['temperature']
        self.max_tokens = llm_cfg['max_tokens']
        self.timeout = llm_cfg['timeout']

        self.generate_url = f"{self.base_url}/api/generate"
        self.embed_url = f"{self.base_url}/api/embeddings"
        self.embed_model = config['embedding']['model']  # 新增

    def generate(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        final_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

        payload = {
            "model": self.model,
            "prompt": final_prompt,
            "stream": False,
            "options": {
                "temperature": kwargs.get('temperature', self.temperature),
                "num_predict": kwargs.get('max_tokens', self.max_tokens),
            }
        }

        try:
            response = requests.post(self.generate_url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            result = response.json()
            return result.get('response', '').strip()
        except requests.exceptions.Timeout:
            raise TimeoutError(f"LLM 请求超时（{self.timeout}秒）")
        except Exception as e:
            raise RuntimeError(f"LLM 调用失败: {e}")

    def embed(self, text: str) -> list:
        payload = {
            "model": self.embed_model,  # 改为使用 embedding 专用模型
            "prompt": text
        }
        try:
            response = requests.post(self.embed_url, json=payload, timeout=60)
            response.raise_for_status()
            return response.json().get('embedding', [])
        except Exception as e:
            raise RuntimeError(f"Embedding 调用失败: {e}")