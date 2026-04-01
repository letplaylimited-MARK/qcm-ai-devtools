"""
AI Client 抽象层

定义统一的 AI 服务调用接口，支持多种 AI 提供商
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class MessageRole(Enum):
    """消息角色"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class Message:
    """
    对话消息

    Example:
        >>> msg = Message(
        ...     role=MessageRole.USER,
        ...     content="帮我创建一个 FastAPI 项目"
        ... )
    """
    role: MessageRole
    content: str
    name: Optional[str] = None

    def to_dict(self) -> Dict[str, str]:
        """转换为字典格式"""
        result = {
            'role': self.role.value,
            'content': self.content
        }
        if self.name:
            result['name'] = self.name
        return result

    @classmethod
    def system(cls, content: str) -> 'Message':
        """创建系统消息"""
        return cls(role=MessageRole.SYSTEM, content=content)

    @classmethod
    def user(cls, content: str) -> 'Message':
        """创建用户消息"""
        return cls(role=MessageRole.USER, content=content)

    @classmethod
    def assistant(cls, content: str) -> 'Message':
        """创建助手消息"""
        return cls(role=MessageRole.ASSISTANT, content=content)


@dataclass
class ChatResponse:
    """
    对话响应

    Example:
        >>> response = ChatResponse(
        ...     content="这是一个 FastAPI 项目模板...",
        ...     model="gpt-4",
        ...     usage={'prompt_tokens': 50, 'completion_tokens': 200}
        ... )
    """
    content: str
    model: str
    usage: Dict[str, int] = field(default_factory=dict)
    finish_reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EmbeddingResponse:
    """
    文本嵌入响应

    Example:
        >>> response = EmbeddingResponse(
        ...     embedding=[0.1, 0.2, 0.3, ...],
        ...     model="text-embedding-ada-002"
        ... )
    """
    embedding: List[float]
    model: str
    usage: Dict[str, int] = field(default_factory=dict)


@dataclass
class CodeAnalysis:
    """
    代码分析结果

    Example:
        >>> analysis = CodeAnalysis(
        ...     code="def hello(): pass",
        ...     score=85,
        ...     issues=["缺少文档字符串"],
        ...     suggestions=["添加类型注解"]
        ... )
    """
    code: str
    score: float
    issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class AIClient(ABC):
    """
    AI 客户端抽象基类

    定义统一的 AI 服务调用接口，支持多种 AI 提供商

    Example:
        >>> # 使用工厂创建客户端
        >>> client = AIClientFactory.create(
        ...     provider="openai",
        ...     model="gpt-4",
        ...     api_key="sk-xxx"
        ... )
        >>>
        >>> # 对话补全
        >>> response = await client.chat([
        ...     Message.system("你是一个代码助手"),
        ...     Message.user("创建一个 FastAPI 项目")
        ... ])
        >>>
        >>> # 文本嵌入
        >>> embedding = await client.embed("Hello world")
    """

    @abstractmethod
    async def chat(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ChatResponse:
        """
        对话补全

        Args:
            messages: 消息列表
            temperature: 温度参数 (0-2)
            max_tokens: 最大 token 数
            **kwargs: 其他参数

        Returns:
            ChatResponse 对象

        Example:
            >>> response = await client.chat([
            ...     Message.user("Hello")
            ... ])
        """
        pass

    @abstractmethod
    async def embed(
        self,
        text: str,
        **kwargs
    ) -> EmbeddingResponse:
        """
        文本嵌入

        Args:
            text: 输入文本
            **kwargs: 其他参数

        Returns:
            EmbeddingResponse 对象

        Example:
            >>> embedding = await client.embed("Hello world")
        """
        pass

    @abstractmethod
    async def analyze_code(
        self,
        code: str,
        **kwargs
    ) -> CodeAnalysis:
        """
        代码分析

        Args:
            code: 源代码
            **kwargs: 其他参数

        Returns:
            CodeAnalysis 对象

        Example:
            >>> analysis = await client.analyze_code(
            ...     "def hello(): pass"
            ... )
        """
        pass

    # ============================================================
    # 便捷方法
    # ============================================================

    async def generate_config_from_description(
        self,
        description: str,
        prompt_template: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        从描述生成配置

        Args:
            description: 项目描述
            prompt_template: Prompt 模板（可选）

        Returns:
            配置字典

        Example:
            >>> config = await client.generate_config_from_description(
            ...     "开发一个 FastAPI 用户管理 API"
            ... )
        """
        # 使用桥接层加载 ai-skill-system 的 Prompt
        from qcm_tools.bridge import AISkillSystemBridge

        bridge = AISkillSystemBridge()

        if prompt_template is None:
            prompt_template = bridge.load_prompt_from_skill_system("skill-01")

        messages = [
            Message.system(prompt_template),
            Message.user(f"请根据以下描述生成项目配置:\n\n{description}")
        ]

        response = await self.chat(messages)
        # 这里可以解析响应为配置字典
        return {'description': description, 'ai_suggestion': response.content}

    async def review_code(
        self,
        code: str,
        focus_areas: Optional[List[str]] = None
    ) -> CodeAnalysis:
        """
        代码审查

        Args:
            code: 源代码
            focus_areas: 关注点列表

        Returns:
            CodeAnalysis 对象

        Example:
            >>> analysis = await client.review_code(
            ...     code,
            ...     focus_areas=["security", "performance"]
            ... )
        """
        return await self.analyze_code(code, focus_areas=focus_areas)


class AIClientFactory:
    """
    AI 客户端工厂

    用于创建不同 AI 提供商的客户端

    Example:
        >>> # 创建 OpenAI 客户端
        >>> client = AIClientFactory.create(
        ...     provider="openai",
        ...     model="gpt-4",
        ...     api_key="sk-xxx"
        ... )
        >>>
        >>> # 创建 Mock 客户端（用于测试）
        >>> client = AIClientFactory.create(
        ...     provider="mock"
        ... )
    """

    @staticmethod
    def create(
        provider: str,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        **kwargs
    ) -> AIClient:
        """
        创建 AI 客户端

        Args:
            provider: 提供商名称 ('openai', 'mock', 'anthropic')
            model: 模型名称
            api_key: API 密钥
            **kwargs: 其他参数

        Returns:
            AIClient 实例

        Raises:
            ValueError: 不支持的提供商
        """
        provider = provider.lower()

        if provider == "openai":
            from qcm_tools.ai.openai_client import OpenAIClient
            return OpenAIClient(
                model=model or "gpt-4",
                api_key=api_key,
                **kwargs
            )
        elif provider == "mock":
            from qcm_tools.ai.mock_client import MockAIClient
            return MockAIClient(**kwargs)
        elif provider == "anthropic":
            # 未来实现
            raise ValueError("Anthropic client not implemented yet")
        else:
            raise ValueError(f"Unsupported AI provider: {provider}")

    @staticmethod
    def from_config(config: Dict[str, Any]) -> AIClient:
        """
        从配置创建客户端

        Args:
            config: 配置字典

        Returns:
            AIClient 实例

        Example:
            >>> client = AIClientFactory.from_config({
            ...     'provider': 'openai',
            ...     'model': 'gpt-4',
            ...     'api_key': 'sk-xxx'
            ... })
        """
        return AIClientFactory.create(
            provider=config.get('provider', 'mock'),
            model=config.get('model'),
            api_key=config.get('api_key'),
            **config.get('options', {})
        )
