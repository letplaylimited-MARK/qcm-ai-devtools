"""
OpenAI Client Enhanced

增强版 OpenAI 客户端，支持：
- 流式响应
- 错误重试
- 成本追踪
- 响应缓存
"""

from typing import List, Optional, Dict, Any, AsyncIterator
import asyncio
import time
from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import json

from qcm_tools.ai.client import (
    AIClient,
    Message,
    ChatResponse,
    EmbeddingResponse,
    CodeAnalysis,
)
from qcm_tools.exceptions import MissingDependencyError


@dataclass
class UsageStats:
    """使用统计"""
    total_requests: int = 0
    total_tokens: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_cost: float = 0.0
    requests_by_model: Dict[str, int] = field(default_factory=dict)

    def add_usage(self, model: str, prompt_tokens: int, completion_tokens: int, cost: float):
        """添加使用记录"""
        self.total_requests += 1
        self.total_tokens += prompt_tokens + completion_tokens
        self.prompt_tokens += prompt_tokens
        self.completion_tokens += completion_tokens
        self.total_cost += cost
        self.requests_by_model[model] = self.requests_by_model.get(model, 0) + 1


@dataclass
class CostCalculator:
    """成本计算器"""

    # OpenAI 定价（美元 / 1K tokens）
    PRICING = {
        'gpt-4': {'prompt': 0.03, 'completion': 0.06},
        'gpt-4-turbo': {'prompt': 0.01, 'completion': 0.03},
        'gpt-3.5-turbo': {'prompt': 0.0005, 'completion': 0.0015},
        'text-embedding-ada-002': {'prompt': 0.0001, 'completion': 0.0},
    }

    @staticmethod
    def calculate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """计算成本"""
        # 标准化模型名称
        model_key = model.lower()
        if 'gpt-4-turbo' in model_key or 'gpt-4-1106' in model_key:
            pricing = CostCalculator.PRICING['gpt-4-turbo']
        elif 'gpt-4' in model_key:
            pricing = CostCalculator.PRICING['gpt-4']
        elif 'gpt-3.5' in model_key:
            pricing = CostCalculator.PRICING['gpt-3.5-turbo']
        elif 'embedding' in model_key:
            pricing = CostCalculator.PRICING['text-embedding-ada-002']
        else:
            # 默认使用 GPT-3.5 价格
            pricing = CostCalculator.PRICING['gpt-3.5-turbo']

        prompt_cost = (prompt_tokens / 1000) * pricing['prompt']
        completion_cost = (completion_tokens / 1000) * pricing['completion']

        return prompt_cost + completion_cost


class OpenAIClientEnhanced(AIClient):
    """
    增强版 OpenAI 客户端

    支持：
    - 流式响应
    - 错误重试
    - 成本追踪
    - 响应缓存

    Example:
        >>> client = OpenAIClientEnhanced(
        ...     model="gpt-4",
        ...     api_key="sk-xxx",
        ...     enable_cache=True,
        ...     max_retries=3
        ... )
        >>>
        >>> # 普通对话
        >>> response = await client.chat([Message.user("Hello")])
        >>>
        >>> # 流式对话
        >>> async for chunk in client.chat_stream([Message.user("Hello")]):
        ...     print(chunk, end='', flush=True)
        >>>
        >>> # 查看使用统计
        >>> print(client.usage_stats)
    """

    def __init__(
        self,
        model: str = "gpt-4",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        enable_cache: bool = False,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        timeout: float = 30.0,
        **kwargs
    ):
        """
        初始化增强版 OpenAI 客户端

        Args:
            model: 模型名称
            api_key: API 密钥
            base_url: API 基础 URL
            enable_cache: 是否启用缓存
            max_retries: 最大重试次数
            retry_delay: 重试延迟（秒）
            timeout: 请求超时（秒）
            **kwargs: 其他参数
        """
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
        self.enable_cache = enable_cache
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.timeout = timeout
        self.options = kwargs

        # 使用统计
        self.usage_stats = UsageStats()
        self.cost_calculator = CostCalculator()

        # 缓存
        self._cache: Dict[str, ChatResponse] = {} if enable_cache else None

        # 延迟导入
        self._client = None

    def _get_client(self):
        """获取 OpenAI 客户端"""
        if self._client is None:
            try:
                import openai
                self._client = openai.AsyncOpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url,
                    timeout=self.timeout
                )
            except ImportError:
                raise MissingDependencyError(
                    message="OpenAI 库未安装",
                    package_name="openai"
                )
        return self._client

    def _get_cache_key(self, messages: List[Message], **kwargs) -> str:
        """生成缓存键"""
        content = json.dumps([msg.to_dict() for msg in messages] + [kwargs], sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()

    async def chat(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ChatResponse:
        """
        对话补全（带重试和缓存）

        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大 token 数
            **kwargs: 其他参数

        Returns:
            ChatResponse 对象
        """
        # 检查缓存
        if self.enable_cache and self._cache is not None:
            cache_key = self._get_cache_key(messages, temperature=temperature, max_tokens=max_tokens, **kwargs)
            if cache_key in self._cache:
                return self._cache[cache_key]

        # 带重试的调用
        last_error = None
        for attempt in range(self.max_retries):
            try:
                response = await self._chat_impl(messages, temperature, max_tokens, **kwargs)

                # 缓存结果
                if self.enable_cache and self._cache is not None:
                    self._cache[cache_key] = response

                return response

            except Exception as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))

        # 所有重试失败
        raise last_error

    async def _chat_impl(
        self,
        messages: List[Message],
        temperature: float,
        max_tokens: Optional[int],
        **kwargs
    ) -> ChatResponse:
        """实际调用 OpenAI API"""
        client = self._get_client()

        message_dicts = [msg.to_dict() for msg in messages]

        response = await client.chat.completions.create(
            model=self.model,
            messages=message_dicts,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )

        choice = response.choices[0]

        # 计算成本
        cost = self.cost_calculator.calculate_cost(
            model=response.model,
            prompt_tokens=response.usage.prompt_tokens,
            completion_tokens=response.usage.completion_tokens
        )

        # 更新统计
        self.usage_stats.add_usage(
            model=response.model,
            prompt_tokens=response.usage.prompt_tokens,
            completion_tokens=response.usage.completion_tokens,
            cost=cost
        )

        return ChatResponse(
            content=choice.message.content,
            model=response.model,
            usage={
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens
            },
            finish_reason=choice.finish_reason,
            metadata={
                'id': response.id,
                'cost': cost
            }
        )

    async def chat_stream(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        流式对话补全

        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大 token 数
            **kwargs: 其他参数

        Yields:
            str: 文本块

        Example:
            >>> async for chunk in client.chat_stream([Message.user("Hello")]):
            ...     print(chunk, end='', flush=True)
        """
        client = self._get_client()

        message_dicts = [msg.to_dict() for msg in messages]

        stream = await client.chat.completions.create(
            model=self.model,
            messages=message_dicts,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs
        )

        async for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

    async def embed(
        self,
        text: str,
        model: str = "text-embedding-ada-002",
        **kwargs
    ) -> EmbeddingResponse:
        """文本嵌入（带重试）"""
        last_error = None

        for attempt in range(self.max_retries):
            try:
                return await self._embed_impl(text, model, **kwargs)
            except Exception as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))

        raise last_error

    async def _embed_impl(
        self,
        text: str,
        model: str,
        **kwargs
    ) -> EmbeddingResponse:
        """实际调用 OpenAI Embedding API"""
        client = self._get_client()

        response = await client.embeddings.create(
            model=model,
            input=text,
            **kwargs
        )

        embedding = response.data[0].embedding

        # 计算成本
        cost = self.cost_calculator.calculate_cost(
            model=model,
            prompt_tokens=response.usage.prompt_tokens,
            completion_tokens=0
        )

        # 更新统计
        self.usage_stats.add_usage(
            model=model,
            prompt_tokens=response.usage.prompt_tokens,
            completion_tokens=0,
            cost=cost
        )

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
        """代码分析"""
        focus_str = ""
        if focus_areas:
            focus_str = f"\n\n特别关注以下方面：{', '.join(focus_areas)}"

        prompt = f"""请分析以下代码并提供评估:

```python
{code}
```
{focus_str}

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
            Message.system("你是一个专业的代码审查专家，擅长发现问题和提供改进建议。"),
            Message.user(prompt)
        ]

        response = await self.chat(messages, temperature=0.3, **kwargs)

        import json
        try:
            # 尝试提取 JSON
            content = response.content
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0]
            elif '```' in content:
                content = content.split('```')[1].split('```')[0]

            result = json.loads(content.strip())
            return CodeAnalysis(
                code=code,
                score=float(result.get('score', 75)),
                issues=result.get('issues', []),
                suggestions=result.get('suggestions', []),
                metadata={
                    'model': self.model,
                    'cost': response.metadata.get('cost', 0)
                }
            )
        except (json.JSONDecodeError, KeyError, ValueError):
            return CodeAnalysis(
                code=code,
                score=75.0,
                issues=["无法解析 AI 响应"],
                suggestions=["请手动审查代码"],
                metadata={
                    'raw_response': response.content,
                    'model': self.model
                }
            )

    def get_usage_stats(self) -> Dict[str, Any]:
        """获取使用统计"""
        return {
            'total_requests': self.usage_stats.total_requests,
            'total_tokens': self.usage_stats.total_tokens,
            'prompt_tokens': self.usage_stats.prompt_tokens,
            'completion_tokens': self.usage_stats.completion_tokens,
            'total_cost': self.usage_stats.total_cost,
            'requests_by_model': dict(self.usage_stats.requests_by_model)
        }

    def clear_cache(self):
        """清空缓存"""
        if self._cache is not None:
            self._cache.clear()
