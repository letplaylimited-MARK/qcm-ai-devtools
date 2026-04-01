"""
Anthropic (Claude) 提供者实现
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


@register_provider(AIProviderType.ANTHROPIC)
class AnthropicProvider(AIProvider):
    """
    Anthropic Claude 提供者
    
    支持 Claude-3 系列模型
    
    Example:
        >>> config = AIProviderConfig(
        ...     provider_type=AIProviderType.ANTHROPIC,
        ...     api_key="sk-ant-xxx",
        ...     model="claude-3-opus-20240229"
        ... )
        >>> provider = AnthropicProvider(config)
    """
    
    AVAILABLE_MODELS = [
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
        "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-20241022",
    ]
    
    def __init__(self, config: AIProviderConfig):
        super().__init__(config)
        self._client = None
    
    def _get_client(self):
        """获取 Anthropic 客户端"""
        if self._client is None:
            try:
                import anthropic
                
                client_kwargs = {}
                if self.config.api_key:
                    client_kwargs["api_key"] = self.config.api_key
                
                self._client = anthropic.Anthropic(**client_kwargs)
            except ImportError:
                raise ImportError(
                    "请安装 anthropic 库: pip install anthropic"
                )
        return self._client
    
    def _convert_messages(self, messages: List[AIMessage]) -> tuple:
        """
        转换消息格式
        
        Anthropic 需要分离 system 消息
        
        Returns:
            (system_prompt, messages_list)
        """
        system_prompt = ""
        converted_messages = []
        
        for msg in messages:
            if msg.role == "system":
                system_prompt = msg.content
            else:
                converted_messages.append(msg.to_dict())
        
        return system_prompt, converted_messages
    
    def chat(
        self,
        messages: List[AIMessage],
        model: Optional[str] = None,
        **kwargs
    ) -> AIResponse:
        """同步对话"""
        client = self._get_client()
        
        model = model or self.config.model or "claude-3-sonnet-20240229"
        system_prompt, converted_messages = self._convert_messages(messages)
        
        params = {
            "model": model,
            "messages": converted_messages,
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
        }
        
        if system_prompt:
            params["system"] = system_prompt
        
        response = client.messages.create(**params)
        
        # 构建响应
        usage = AIUsage(
            prompt_tokens=response.usage.input_tokens,
            completion_tokens=response.usage.output_tokens,
            total_tokens=response.usage.input_tokens + response.usage.output_tokens,
        )
        
        content = response.content[0].text if response.content else ""
        
        return AIResponse(
            content=content,
            model=response.model,
            provider=AIProviderType.ANTHROPIC,
            usage=usage,
            finish_reason=response.stop_reason,
            extra={
                "id": response.id,
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
            import anthropic
            
            client_kwargs = {}
            if self.config.api_key:
                client_kwargs["api_key"] = self.config.api_key
            
            client = anthropic.AsyncAnthropic(**client_kwargs)
            
            model = model or self.config.model or "claude-3-sonnet-20240229"
            system_prompt, converted_messages = self._convert_messages(messages)
            
            params = {
                "model": model,
                "messages": converted_messages,
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            }
            
            if system_prompt:
                params["system"] = system_prompt
            
            response = await client.messages.create(**params)
            
            usage = AIUsage(
                prompt_tokens=response.usage.input_tokens,
                completion_tokens=response.usage.output_tokens,
                total_tokens=response.usage.input_tokens + response.usage.output_tokens,
            )
            
            content = response.content[0].text if response.content else ""
            
            return AIResponse(
                content=content,
                model=response.model,
                provider=AIProviderType.ANTHROPIC,
                usage=usage,
                finish_reason=response.stop_reason,
            )
        except ImportError:
            raise ImportError("请安装 anthropic 库: pip install anthropic")
    
    def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        return self.AVAILABLE_MODELS.copy()
    
    def validate_config(self) -> bool:
        """验证配置"""
        return bool(self.config.api_key)


__all__ = ['AnthropicProvider']
