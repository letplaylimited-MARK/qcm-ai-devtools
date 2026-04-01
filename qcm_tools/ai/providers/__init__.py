"""
AI 提供者模块

支持多种 AI 大模型的统一接口，兼容 OpenCode 等工具
"""

from qcm_tools.ai.providers.base import (
    AIProvider,
    AIProviderType,
    AIProviderConfig,
    AIMessage,
    AIResponse,
    AIUsage,
)
from qcm_tools.ai.providers.openai_provider import OpenAIProvider
from qcm_tools.ai.providers.anthropic_provider import AnthropicProvider
from qcm_tools.ai.providers.deepseek_provider import DeepSeekProvider
from qcm_tools.ai.providers.gemini_provider import GeminiProvider
from qcm_tools.ai.providers.ollama_provider import OllamaProvider
from qcm_tools.ai.providers.opencode_provider import OpenCodeProvider
from qcm_tools.ai.providers.factory import create_provider, get_available_providers

__all__ = [
    'AIProvider',
    'AIProviderType',
    'AIProviderConfig',
    'AIMessage',
    'AIResponse',
    'AIUsage',
    'OpenAIProvider',
    'AnthropicProvider',
    'DeepSeekProvider',
    'GeminiProvider',
    'OllamaProvider',
    'OpenCodeProvider',
    'create_provider',
    'get_available_providers',
]
