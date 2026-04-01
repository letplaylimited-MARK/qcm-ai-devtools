"""
AI 提供者工厂

创建和管理不同 AI 提供者的实例
"""

from typing import Dict, List, Optional, Type
import logging

from qcm_tools.ai.providers.base import (
    AIProvider,
    AIProviderType,
    AIProviderConfig,
)

logger = logging.getLogger(__name__)

# 提供者注册表
_PROVIDER_REGISTRY: Dict[AIProviderType, Type[AIProvider]] = {}


def register_provider(provider_type: AIProviderType):
    """
    注册 AI 提供者的装饰器
    
    Example:
        >>> @register_provider(AIProviderType.OPENAI)
        ... class OpenAIProvider(AIProvider):
        ...     pass
    """
    def decorator(cls: Type[AIProvider]) -> Type[AIProvider]:
        _PROVIDER_REGISTRY[provider_type] = cls
        logger.debug(f"注册 AI 提供者: {provider_type.value} -> {cls.__name__}")
        return cls
    return decorator


def create_provider(
    provider_type: Optional[AIProviderType] = None,
    config: Optional[AIProviderConfig] = None,
    **kwargs
) -> AIProvider:
    """
    创建 AI 提供者实例
    
    Args:
        provider_type: 提供者类型
        config: 提供者配置
        **kwargs: 配置参数（如果没有提供 config）
        
    Returns:
        AI 提供者实例
        
    Example:
        >>> # 使用配置对象
        >>> config = AIProviderConfig(
        ...     provider_type=AIProviderType.OPENAI,
        ...     api_key="sk-xxx"
        ... )
        >>> provider = create_provider(config=config)
        
        >>> # 使用关键字参数
        >>> provider = create_provider(
        ...     provider_type=AIProviderType.OPENAI,
        ...     api_key="sk-xxx"
        ... )
        
        >>> # 从环境变量
        >>> provider = create_provider()
    """
    # 如果没有提供配置，创建默认配置
    if config is None:
        if provider_type:
            config = AIProviderConfig(provider_type=provider_type, **kwargs)
        else:
            config = AIProviderConfig.from_env()
    elif isinstance(provider_type, AIProviderType) and config is not None:
        # 如果同时提供了 provider_type 和 config，使用 provider_type
        pass
    
    provider_type = config.provider_type
    
    # 懒加载提供者类
    _lazy_load_providers()
    
    if provider_type not in _PROVIDER_REGISTRY:
        raise ValueError(f"不支持的 AI 提供者类型: {provider_type.value}")
    
    provider_class = _PROVIDER_REGISTRY[provider_type]
    return provider_class(config)


def get_available_providers() -> List[Dict[str, str]]:
    """
    获取所有可用的 AI 提供者
    
    Returns:
        提供者信息列表
    """
    _lazy_load_providers()
    
    providers = []
    for provider_type in AIProviderType:
        if provider_type in _PROVIDER_REGISTRY:
            providers.append({
                "type": provider_type.value,
                "name": _get_provider_display_name(provider_type),
                "available": True,
            })
        else:
            providers.append({
                "type": provider_type.value,
                "name": _get_provider_display_name(provider_type),
                "available": False,
            })
    
    return providers


def _get_provider_display_name(provider_type: AIProviderType) -> str:
    """获取提供者显示名称"""
    names = {
        AIProviderType.OPENAI: "OpenAI (GPT-4, GPT-3.5)",
        AIProviderType.ANTHROPIC: "Anthropic (Claude)",
        AIProviderType.DEEPSEEK: "DeepSeek",
        AIProviderType.GEMINI: "Google Gemini",
        AIProviderType.OLLAMA: "Ollama (本地模型)",
        AIProviderType.OPENCODE: "OpenCode (多模型切换)",
        AIProviderType.ZHIPU: "智谱 AI (GLM)",
        AIProviderType.QWEN: "通义千问 (Qwen)",
        AIProviderType.CUSTOM: "自定义提供者",
    }
    return names.get(provider_type, provider_type.value)


def _lazy_load_providers():
    """懒加载所有提供者"""
    if _PROVIDER_REGISTRY:
        return
    
    try:
        from qcm_tools.ai.providers.openai_provider import OpenAIProvider
        _PROVIDER_REGISTRY[AIProviderType.OPENAI] = OpenAIProvider
    except ImportError:
        pass
    
    try:
        from qcm_tools.ai.providers.anthropic_provider import AnthropicProvider
        _PROVIDER_REGISTRY[AIProviderType.ANTHROPIC] = AnthropicProvider
    except ImportError:
        pass
    
    try:
        from qcm_tools.ai.providers.deepseek_provider import DeepSeekProvider
        _PROVIDER_REGISTRY[AIProviderType.DEEPSEEK] = DeepSeekProvider
    except ImportError:
        pass
    
    try:
        from qcm_tools.ai.providers.gemini_provider import GeminiProvider
        _PROVIDER_REGISTRY[AIProviderType.GEMINI] = GeminiProvider
    except ImportError:
        pass
    
    try:
        from qcm_tools.ai.providers.ollama_provider import OllamaProvider
        _PROVIDER_REGISTRY[AIProviderType.OLLAMA] = OllamaProvider
    except ImportError:
        pass
    
    try:
        from qcm_tools.ai.providers.opencode_provider import OpenCodeProvider
        _PROVIDER_REGISTRY[AIProviderType.OPENCODE] = OpenCodeProvider
    except ImportError:
        pass


__all__ = [
    'register_provider',
    'create_provider',
    'get_available_providers',
]
