"""
DeepSeek 提供者实现
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


@register_provider(AIProviderType.DEEPSEEK)
class DeepSeekProvider(AIProvider):
    """
    DeepSeek 提供者
    
    支持 DeepSeek-V3, DeepSeek-Coder 等模型
    
    Example:
        >>> config = AIProviderConfig(
        ...     provider_type=AIProviderType.DEEPSEEK,
        ...     api_key="sk-xxx",
        ...     model="deepseek-chat"
        ... )
        >>> provider = DeepSeekProvider(config)
    """
    
    AVAILABLE_MODELS = [
        "deepseek-chat",
        "deepseek-coder",
        "deepseek-reasoner",
    ]
    
    DEFAULT_BASE_URL = "https://api.deepseek.com/v1"
    
    def __init__(self, config: AIProviderConfig):
        # 设置默认 base_url
        if not config.base_url:
            config.base_url = self.DEFAULT_BASE_URL
        super().__init__(config)
        self._client = None
    
    def _get_client(self):
        """获取 DeepSeek 客户端（兼容 OpenAI SDK）"""
        if self._client is None:
            try:
                from openai import OpenAI
                
                client_kwargs = {
                    "base_url": self.config.base_url,
                }
                if self.config.api_key:
                    client_kwargs["api_key"] = self.config.api_key
                
                self._client = OpenAI(**client_kwargs)
            except ImportError:
                raise ImportError(
                    "请安装 openai 库: pip install openai"
                )
        return self._client
    
    def chat(
        self,
        messages: List[AIMessage],
        model: Optional[str] = None,
        **kwargs
    ) -> AIResponse:
        """同步对话"""
        client = self._get_client()
        
        model = model or self.config.model or "deepseek-chat"
        messages_dict = [m.to_dict() for m in messages]
        
        params = {
            "model": model,
            "messages": messages_dict,
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
        }
        
        response = client.chat.completions.create(**params)
        
        choice = response.choices[0]
        usage = AIUsage(
            prompt_tokens=response.usage.prompt_tokens,
            completion_tokens=response.usage.completion_tokens,
            total_tokens=response.usage.total_tokens,
        )
        
        return AIResponse(
            content=choice.message.content,
            model=response.model,
            provider=AIProviderType.DEEPSEEK,
            usage=usage,
            finish_reason=choice.finish_reason,
        )
    
    async def achat(
        self,
        messages: List[AIMessage],
        model: Optional[str] = None,
        **kwargs
    ) -> AIResponse:
        """异步对话"""
        try:
            from openai import AsyncOpenAI
            
            client = AsyncOpenAI(
                base_url=self.config.base_url,
                api_key=self.config.api_key,
            )
            
            model = model or self.config.model or "deepseek-chat"
            messages_dict = [m.to_dict() for m in messages]
            
            params = {
                "model": model,
                "messages": messages_dict,
                "temperature": kwargs.get("temperature", self.config.temperature),
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            }
            
            response = await client.chat.completions.create(**params)
            
            choice = response.choices[0]
            usage = AIUsage(
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens,
            )
            
            return AIResponse(
                content=choice.message.content,
                model=response.model,
                provider=AIProviderType.DEEPSEEK,
                usage=usage,
                finish_reason=choice.finish_reason,
            )
        except ImportError:
            raise ImportError("请安装 openai 库: pip install openai")
    
    def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        return self.AVAILABLE_MODELS.copy()
    
    def validate_config(self) -> bool:
        """验证配置"""
        return bool(self.config.api_key)


__all__ = ['DeepSeekProvider']
