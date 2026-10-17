"""
AI 客户端模块 - 调用大模型生成回复建议
使用 OpenAI 兼容协议，支持 OpenAI / DeepSeek / 月之暗面 / 通义千问 / 本地 Ollama 等。
"""

import json
from typing import List, Optional

import requests

from config import (
    AI_API_KEY,
    AI_BASE_URL,
    AI_MODEL,
    AI_SYSTEM_PROMPT,
    SUGGESTION_COUNT,
)


class AIClient:
    def __init__(self):
        self.api_key = AI_API_KEY
        self.base_url = AI_BASE_URL.rstrip("/")
        self.model = AI_MODEL

    def generate_suggestions(
        self,
        latest_message: str,
        context_messages: Optional[List] = None,
    ) -> List[str]:
        """
        根据对方最新消息和聊天上下文，生成回复建议列表。
        :param latest_message: 对方最新发来的消息文本
        :param context_messages: 历史消息列表（ChatMessage 对象）
        :return: 回复建议字符串列表
        """
        if not self.api_key or self.api_key.startswith("sk-your-"):
            print("[AI] 未配置有效的 API Key，使用本地兜底回复")
            return self._fallback_suggestions(latest_message)

        # 构建上下文
        context_text = ""
        if context_messages:
            lines = []
            for m in context_messages[-10:]:
                sender = "对方" if m.is_from_other else "我"
                lines.append(f"{sender}: {m.text}")
            context_text = "\n".join(lines)

        user_prompt = (
            f"聊天上下文：\n{context_text}\n\n"
            f"对方最新消息：{latest_message}\n\n"
            f"请生成 {SUGGESTION_COUNT} 条不同的中文回复建议，"
            f"每条单独一行，不要编号，不要多余解释。"
        )

        try:
            resp = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": AI_SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                    "temperature": 0.8,
                    "max_tokens": 500,
                },
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"].strip()
            # 按行拆分，过滤空行
            suggestions = [
                line.strip().lstrip("0123456789.、) ")
                for line in content.splitlines()
                if line.strip()
            ]
            # 去重并限制数量
            seen = set()
            unique = []
            for s in suggestions:
                if s and s not in seen:
                    seen.add(s)
                    unique.append(s)
            return unique[:SUGGESTION_COUNT] or self._fallback_suggestions(latest_message)
        except Exception as e:
            print(f"[AI] 调用失败: {e}")
            return self._fallback_suggestions(latest_message)

    @staticmethod
    def _fallback_suggestions(message: str) -> List[str]:
        """API 不可用时的本地兜底回复"""
        return [
            "好的，我知道啦~",
            "哈哈，你说得对",
            "那你现在在干嘛呢？",
        ]
