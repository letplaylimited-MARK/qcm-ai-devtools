"""
OpenAI Client

OpenAI API 的具体实现
"""

from typing import List, Optional, Dict, Any
import asyncio

from qcm_tools.ai.client import (
    AIClient,
    Message,
    ChatResponse,
    EmbeddingResponse,
    CodeAnalysis,
)
from qcm_tools.exceptions import MissingDependencyError


class OpenAIClient(AIClient):
    """
    OpenAI 客户端

    实现 OpenAI API 的调用

    Example:
        >>> client = OpenAIClient(
        ...     model="gpt-4",
        ...     api_key="sk-xxx"
        ... )
        >>>
        >>> response = await client.chat([
        ...     Message.user("Hello")
        ... ])
    """

    def __init__(
        self,
        model: str = "gpt-4",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        **kwargs
    ):
        """
        初始化 OpenAI 客户端

        Args:
            model: 模型名称 (gpt-4, gpt-3.5-turbo, etc.)
            api_key: OpenAI API 密钥
            base_url: API 基础 URL（可选，用于代理）
            **kwargs: 其他参数
        """
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
        self.options = kwargs

        # 延迟导入 openai
        self._client = None

    def _get_client(self):
        """获取 OpenAI 客户端（延迟导入）"""
        if self._client is None:
            try:
                import openai
                self._client = openai.AsyncOpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url
                )
            except ImportError:
                raise MissingDependencyError(
                    message="OpenAI 库未安装",
                    package_name="openai"
                )
        return self._client

    async def chat(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ChatResponse:
        """
        OpenAI 对话补全

        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大 token 数
            **kwargs: 其他参数

        Returns:
            ChatResponse 对象
        """
        client = self._get_client()

        # 转换消息格式
        message_dicts = [msg.to_dict() for msg in messages]

        # 调用 OpenAI API
        response = await client.chat.completions.create(
            model=self.model,
            messages=message_dicts,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )

        # 转换响应
        choice = response.choices[0]
        return ChatResponse(
            content=choice.message.content,
            model=response.model,
            usage={
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens
            },
            finish_reason=choice.finish_reason,
            metadata={'id': response.id}
        )

    async def embed(
        self,
        text: str,
        model: str = "text-embedding-ada-002",
        **kwargs
    ) -> EmbeddingResponse:
        """
        OpenAI 文本嵌入

        Args:
            text: 输入文本
            model: 嵌入模型
            **kwargs: 其他参数

        Returns:
            EmbeddingResponse 对象
        """
        client = self._get_client()

        response = await client.embeddings.create(
            model=model,
            input=text,
            **kwargs
        )

        embedding = response.data[0].embedding
        return EmbeddingResponse(
            embedding=embedding,
            model=response.model,
            usage={
                'prompt_tokens': response.usage.prompt_tokens,
                'total_tokens': response.usage.total_tokens
            }
        )

    async def analyze_code(
        self,
        code: str,
        focus_areas: Optional[List[str]] = None,
        **kwargs
    ) -> CodeAnalysis:
        """
        使用 OpenAI 分析代码

        Args:
            code: 源代码
            focus_areas: 关注点列表
            **kwargs: 其他参数

        Returns:
            CodeAnalysis 对象
        """
        # 构造分析 Prompt
        prompt = f"""请分析以下代码并提供评估:

```python
{code}
```

请从以下维度评估（每项 0-100 分）：
1. 代码质量
2. 可读性
3. 性能
4. 安全性

请用 JSON 格式返回结果：
{{
    "score": 总体评分,
    "issues": ["问题列表"],
    "suggestions": ["改进建议"]
}}
"""

        messages = [
            Message.system("你是一个代码审查专家"),
            Message.user(prompt)
        ]

        response = await self.chat(messages, temperature=0.3, **kwargs)

        # 解析响应（简化处理）
        import json
        try:
            result = json.loads(response.content)
            return CodeAnalysis(
                code=code,
                score=result.get('score', 75),
                issues=result.get('issues', []),
                suggestions=result.get('suggestions', []),
                metadata={'model': self.model}
            )
        except json.JSONDecodeError:
            # 如果无法解析，返回默认值
            return CodeAnalysis(
                code=code,
                score=75,
                issues=["无法解析 AI 响应"],
                suggestions=[],
                metadata={'raw_response': response.content}
            )
