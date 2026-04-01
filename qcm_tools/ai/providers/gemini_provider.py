"""
Google Gemini 提供者实现
"""

from typing import List, Optional
import logging

from qcm_tools.ai.providers.base import (
    AIProvider,
    AIProviderType,
    AIProviderConfig,
    AIMessage,
    AIResponse,
    AIUsage,
)
from qcm_tools.ai.providers.factory import register_provider

logger = logging.getLogger(__name__)


@register_provider(AIProviderType.GEMINI)
class GeminiProvider(AIProvider):
    """
    Google Gemini 提供者
    
    支持 Gemini Pro 等模型
    
    Example:
        >>> config = AIProviderConfig(
        ...     provider_type=AIProviderType.GEMINI,
        ...     api_key="xxx",
        ...     model="gemini-pro"
        ... )
        >>> provider = GeminiProvider(config)
    """
    
    AVAILABLE_MODELS = [
        "gemini-pro",
        "gemini-pro-vision",
        "gemini-1.5-pro",
        "gemini-1.5-flash",
    ]
    
    def __init__(self, config: AIProviderConfig):
        super().__init__(config)
        self._client = None
    
    def _get_client(self):
        """获取 Gemini 客户端"""
        if self._client is None:
            try:
                import google.generativeai as genai
                
                genai.configure(api_key=self.config.api_key)
                self._client = genai
            except ImportError:
                raise ImportError(
                    "请安装 google-generativeai 库: pip install google-generativeai"
                )
        return self._client
    
    def chat(
        self,
        messages: List[AIMessage],
        model: Optional[str] = None,
        **kwargs
    ) -> AIResponse:
        """同步对话"""
        genai = self._get_client()
        
        model_name = model or self.config.model or "gemini-pro"
        model_instance = genai.GenerativeModel(model_name)
        
        # 转换消息格式
        history = []
        for msg in messages:
            if msg.role == "system":
                continue  # Gemini 不支持 system role
            role = "user" if msg.role == "user" else "model"
            history.append({"role": role, "parts": [msg.content]})
        
        # 启动聊天
        chat = model_instance.start_chat(history=history[:-1] if len(history) > 1 else [])
        
        # 发送最后一条用户消息
        if history:
            response = chat.send_message(history[-1]["parts"][0])
        else:
            response = model_instance.generate_content("")
        
        # 估算 token
        usage = AIUsage(
            prompt_tokens=self.count_tokens(str(history)),
            completion_tokens=self.count_tokens(response.text),
            total_tokens=self.count_tokens(str(history)) + self.count_tokens(response.text),
        )
        
        return AIResponse(
            content=response.text,
            model=model_name,
            provider=AIProviderType.GEMINI,
            usage=usage,
            finish_reason="stop",
        )
    
    async def achat(
        self,
        messages: List[AIMessage],
        model: Optional[str] = None,
        **kwargs
    ) -> AIResponse:
        """异步对话"""
        # Gemini 的异步支持需要额外配置
        # 这里使用同步方法作为后备
        return self.chat(messages, model, **kwargs)
    
    def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        return self.AVAILABLE_MODELS.copy()
    
    def validate_config(self) -> bool:
        """验证配置"""
        return bool(self.config.api_key)


__all__ = ['GeminiProvider']
