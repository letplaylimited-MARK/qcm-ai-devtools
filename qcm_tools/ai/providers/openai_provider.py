"""
OpenAI 提供者实现
"""

from typing import List, Optional, AsyncIterator
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


@register_provider(AIProviderType.OPENAI)
class OpenAIProvider(AIProvider):
    """
    OpenAI 提供者
    
    支持 GPT-4, GPT-3.5-turbo 等模型
    
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
    """
    
    # OpenAI 支持的模型列表
    AVAILABLE_MODELS = [
        "gpt-4",
        "gpt-4-turbo",
        "gpt-4-turbo-preview",
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-3.5-turbo",
        "gpt-3.5-turbo-16k",
    ]
    
    def __init__(self, config: AIProviderConfig):
        super().__init__(config)
        self._client = None
    
    def _get_client(self):
        """获取 OpenAI 客户端"""
        if self._client is None:
            try:
                from openai import OpenAI
                
                client_kwargs = {}
                if self.config.api_key:
                    client_kwargs["api_key"] = self.config.api_key
                if self.config.base_url:
                    client_kwargs["base_url"] = self.config.base_url
                
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
        
        model = model or self.config.model or "gpt-4"
        messages_dict = [m.to_dict() for m in messages]
        
        # 合并参数
        params = {
            "model": model,
            "messages": messages_dict,
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
        }
        
        # 添加额外参数
        for key in ["top_p", "presence_penalty", "frequency_penalty", "stop"]:
            if key in kwargs:
                params[key] = kwargs[key]
        
        response = client.chat.completions.create(**params)
        
        # 构建响应
        choice = response.choices[0]
        usage = AIUsage(
            prompt_tokens=response.usage.prompt_tokens,
            completion_tokens=response.usage.completion_tokens,
            total_tokens=response.usage.total_tokens,
        )
        
        return AIResponse(
            content=choice.message.content,
            model=response.model,
            provider=AIProviderType.OPENAI,
            usage=usage,
            finish_reason=choice.finish_reason,
            extra={
                "id": response.id,
                "created": response.created,
            }
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
            
            client_kwargs = {}
            if self.config.api_key:
                client_kwargs["api_key"] = self.config.api_key
            if self.config.base_url:
                client_kwargs["base_url"] = self.config.base_url
            
            client = AsyncOpenAI(**client_kwargs)
            
            model = model or self.config.model or "gpt-4"
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
                provider=AIProviderType.OPENAI,
                usage=usage,
                finish_reason=choice.finish_reason,
            )
        except ImportError:
            raise ImportError("请安装 openai 库: pip install openai")
    
    def stream(
        self,
        messages: List[AIMessage],
        model: Optional[str] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """流式对话"""
        client = self._get_client()
        
        model = model or self.config.model or "gpt-4"
        messages_dict = [m.to_dict() for m in messages]
        
        params = {
            "model": model,
            "messages": messages_dict,
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "stream": True,
        }
        
        stream = client.chat.completions.create(**params)
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        return self.AVAILABLE_MODELS.copy()
    
    def validate_config(self) -> bool:
        """验证配置"""
        return bool(self.config.api_key)


__all__ = ['OpenAIProvider']
