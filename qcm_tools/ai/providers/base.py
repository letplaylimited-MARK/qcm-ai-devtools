"""
AI 提供者基类

定义所有 AI 大模型提供者的统一接口
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any, List, Optional, AsyncIterator
from dataclasses import dataclass, field
from datetime import datetime


class AIProviderType(Enum):
    """
    支持的 AI 提供者类型
    
    Attributes:
        OPENAI: OpenAI (GPT-4, GPT-3.5, etc.)
        ANTHROPIC: Anthropic (Claude)
        DEEPSEEK: DeepSeek
        GEMINI: Google Gemini
        OLLAMA: Ollama (本地模型)
        OPENCODE: OpenCode (多模型切换)
        ZHIPU: 智谱 AI (GLM)
        QWEN: 通义千问 (Qwen)
        CUSTOM: 自定义提供者
    """
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    DEEPSEEK = "deepseek"
    GEMINI = "gemini"
    OLLAMA = "ollama"
    OPENCODE = "opencode"
    ZHIPU = "zhipu"
    QWEN = "qwen"
    CUSTOM = "custom"


@dataclass
class AIMessage:
    """
    AI 消息结构
    
    Attributes:
        role: 角色 (system, user, assistant)
        content: 消息内容
        name: 可选的名称
    """
    role: str
    content: str
    name: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = {"role": self.role, "content": self.content}
        if self.name:
            result["name"] = self.name
        return result


@dataclass
class AIUsage:
    """
    AI 使用统计
    
    Attributes:
        prompt_tokens: 提示词 token 数
        completion_tokens: 完成 token 数
        total_tokens: 总 token 数
    """
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


@dataclass
class AIResponse:
    """
    AI 响应结构
    
    Attributes:
        content: 响应内容
        model: 使用的模型
        provider: 提供者类型
        usage: 使用统计
        finish_reason: 完成原因
        created: 创建时间
        extra: 额外信息
    """
    content: str
    model: str
    provider: AIProviderType
    usage: AIUsage = field(default_factory=AIUsage)
    finish_reason: str = "stop"
    created: datetime = field(default_factory=datetime.now)
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AIProviderConfig:
    """
    AI 提供者配置
    
    Attributes:
        provider_type: 提供者类型
        api_key: API 密钥
        base_url: API 基础 URL
        model: 默认模型
        temperature: 温度参数
        max_tokens: 最大 token 数
        timeout: 超时时间
        extra: 额外配置
    """
    provider_type: AIProviderType
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: str = ""
    temperature: float = 0.7
    max_tokens: int = 4096
    timeout: int = 60
    extra: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_env(cls, provider_type: AIProviderType = None) -> "AIProviderConfig":
        """
        从环境变量创建配置
        
        支持的环境变量:
            - AI_PROVIDER: 提供者类型
            - AI_API_KEY: API 密钥
            - AI_BASE_URL: 基础 URL
            - AI_MODEL: 默认模型
            - AI_TEMPERATURE: 温度
            - AI_MAX_TOKENS: 最大 token
        """
        import os
        
        provider_str = os.getenv("AI_PROVIDER", "opencode").lower()
        provider_type = provider_type or AIProviderType(provider_str)
        
        return cls(
            provider_type=provider_type,
            api_key=os.getenv("AI_API_KEY") or os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("AI_BASE_URL"),
            model=os.getenv("AI_MODEL", ""),
            temperature=float(os.getenv("AI_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("AI_MAX_TOKENS", "4096")),
        )


class AIProvider(ABC):
    """
    AI 提供者抽象基类
    
    所有 AI 大模型提供者都需要实现此接口，
    以确保统一的调用方式。
    
    Example:
        >>> config = AIProviderConfig(
        ...     provider_type=AIProviderType.OPENAI,
        ...     api_key="sk-xxx",
        ...     model="gpt-4"
        ... )
        >>> provider = OpenAIProvider(config)
        >>> response = provider.chat([
        ...     AIMessage(role="user", content="Hello!")
        ... ])
        >>> print(response.content)
    """
    
    def __init__(self, config: AIProviderConfig):
        """
        初始化 AI 提供者
        
        Args:
            config: 提供者配置
        """
        self.config = config
        self._client = None
    
    @abstractmethod
    def chat(
        self,
        messages: List[AIMessage],
        model: Optional[str] = None,
        **kwargs
    ) -> AIResponse:
        """
        同步对话
        
        Args:
            messages: 消息列表
            model: 模型名称（可选，使用配置中的默认模型）
            **kwargs: 额外参数
            
        Returns:
            AI 响应
        """
        pass
    
    @abstractmethod
    async def achat(
        self,
        messages: List[AIMessage],
        model: Optional[str] = None,
        **kwargs
    ) -> AIResponse:
        """
        异步对话
        
        Args:
            messages: 消息列表
            model: 模型名称
            **kwargs: 额外参数
            
        Returns:
            AI 响应
        """
        pass
    
    def stream(
        self,
        messages: List[AIMessage],
        model: Optional[str] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        流式对话
        
        Args:
            messages: 消息列表
            model: 模型名称
            **kwargs: 额外参数
            
        Yields:
            响应文本片段
        """
        # 默认实现：调用同步方法后分割返回
        response = self.chat(messages, model, **kwargs)
        yield response.content
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """
        获取可用模型列表
        
        Returns:
            模型名称列表
        """
        pass
    
    def validate_config(self) -> bool:
        """
        验证配置是否有效
        
        Returns:
            配置是否有效
        """
        return True
    
    def count_tokens(self, text: str) -> int:
        """
        计算 token 数量
        
        Args:
            text: 文本内容
            
        Returns:
            token 数量
        """
        # 简单估算：平均每 4 个字符约 1 个 token
        return len(text) // 4
    
    @property
    def provider_name(self) -> str:
        """获取提供者名称"""
        return self.config.provider_type.value
    
    @property
    def default_model(self) -> str:
        """获取默认模型"""
        return self.config.model
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(provider={self.provider_name}, model={self.default_model})"


__all__ = [
    'AIProviderType',
    'AIMessage',
    'AIUsage',
    'AIResponse',
    'AIProviderConfig',
    'AIProvider',
]
