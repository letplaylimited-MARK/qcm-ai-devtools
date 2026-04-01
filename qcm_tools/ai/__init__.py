"""
QCM-AI-DevTools AI 模块

提供 AI 客户端抽象层和实现
"""

from qcm_tools.ai.client import (
    AIClient,
    AIClientFactory,
    Message,
    ChatResponse,
    EmbeddingResponse,
)
from qcm_tools.ai.openai_client import OpenAIClient
from qcm_tools.ai.openai_client_enhanced import (
    OpenAIClientEnhanced,
    UsageStats,
    CostCalculator,
)
from qcm_tools.ai.mock_client import MockAIClient

__all__ = [
    'AIClient',
    'AIClientFactory',
    'Message',
    'ChatResponse',
    'EmbeddingResponse',
    'OpenAIClient',
    'OpenAIClientEnhanced',
    'UsageStats',
    'CostCalculator',
    'MockAIClient',
]
