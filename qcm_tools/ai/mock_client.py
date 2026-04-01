"""
Mock AI Client

用于测试的模拟 AI 客户端
"""

from typing import List, Optional, Dict, Any
from qcm_tools.ai.client import (
    AIClient,
    Message,
    ChatResponse,
    EmbeddingResponse,
    CodeAnalysis,
)


class MockAIClient(AIClient):
    """
    Mock AI 客户端

    用于测试和开发，不需要真实 API 调用

    Example:
        >>> client = MockAIClient()
        >>> response = await client.chat([
        ...     Message.user("Hello")
        ... ])
        >>> print(response.content)
        # Mock response: Hello
    """

    def __init__(self, **kwargs):
        """初始化 Mock 客户端"""
        self.call_count = 0
        self.last_messages = None
        self.options = kwargs

    async def chat(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ChatResponse:
        """
        模拟对话补全

        返回基于输入的简单响应
        """
        self.call_count += 1
        self.last_messages = messages

        # 生成简单的 mock 响应
        last_message = messages[-1] if messages else None
        content = f"Mock response to: {last_message.content if last_message else 'empty'}"

        return ChatResponse(
            content=content,
            model="mock-model",
            usage={
                'prompt_tokens': 10,
                'completion_tokens': 20,
                'total_tokens': 30
            },
            finish_reason="stop",
            metadata={'mock': True}
        )

    async def embed(
        self,
        text: str,
        **kwargs
    ) -> EmbeddingResponse:
        """
        模拟文本嵌入

        返回固定维度的随机嵌入
        """
        self.call_count += 1

        # 生成简单的 mock 嵌入
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        embedding = [float(int(hash_obj.hexdigest()[i:i+2], 16)) / 255.0 for i in range(0, 32, 2)]

        return EmbeddingResponse(
            embedding=embedding,
            model="mock-embedding",
            usage={
                'prompt_tokens': len(text.split()),
                'total_tokens': len(text.split())
            }
        )

    async def analyze_code(
        self,
        code: str,
        **kwargs
    ) -> CodeAnalysis:
        """
        模拟代码分析

        返回基于代码长度的简单分析
        """
        self.call_count += 1

        # 简单的 mock 分析
        lines = code.strip().split('\n')
        score = min(100, len(lines) * 5)

        issues = []
        suggestions = []

        if 'TODO' in code:
            issues.append("包含 TODO 注释")
        if 'print(' in code:
            suggestions.append("考虑使用日志系统代替 print")
        if len(lines) > 50:
            issues.append("代码较长，考虑拆分函数")

        return CodeAnalysis(
            code=code,
            score=score,
            issues=issues,
            suggestions=suggestions,
            metadata={
                'lines': len(lines),
                'chars': len(code),
                'mock': True
            }
        )

    def reset(self):
        """重置状态"""
        self.call_count = 0
        self.last_messages = None
