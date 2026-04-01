"""
Ollama 提供者实现（本地模型）
"""

from typing import List, Optional
import logging
import json

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


@register_provider(AIProviderType.OLLAMA)
class OllamaProvider(AIProvider):
    """
    Ollama 本地模型提供者
    
    支持本地运行的模型如 Llama, Mistral 等
    
    Example:
        >>> config = AIProviderConfig(
        ...     provider_type=AIProviderType.OLLAMA,
        ...     base_url="http://localhost:11434",
        ...     model="llama2"
        ... )
        >>> provider = OllamaProvider(config)
    """
    
    DEFAULT_BASE_URL = "http://localhost:11434"
    
    def __init__(self, config: AIProviderConfig):
        if not config.base_url:
            config.base_url = self.DEFAULT_BASE_URL
        super().__init__(config)
    
    def chat(
        self,
        messages: List[AIMessage],
        model: Optional[str] = None,
        **kwargs
    ) -> AIResponse:
        """同步对话"""
        import requests
        
        model = model or self.config.model or "llama2"
        messages_dict = [m.to_dict() for m in messages]
        
        url = f"{self.config.base_url}/api/chat"
        
        payload = {
            "model": model,
            "messages": messages_dict,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", self.config.temperature),
                "num_predict": kwargs.get("max_tokens", self.config.max_tokens),
            }
        }
        
        response = requests.post(url, json=payload, timeout=self.config.timeout)
        response.raise_for_status()
        
        data = response.json()
        
        # 构建响应
        content = data.get("message", {}).get("content", "")
        
        usage = AIUsage(
            prompt_tokens=data.get("prompt_eval_count", 0),
            completion_tokens=data.get("eval_count", 0),
            total_tokens=data.get("prompt_eval_count", 0) + data.get("eval_count", 0),
        )
        
        return AIResponse(
            content=content,
            model=model,
            provider=AIProviderType.OLLAMA,
            usage=usage,
            finish_reason="stop",
            extra=data,
        )
    
    async def achat(
        self,
        messages: List[AIMessage],
        model: Optional[str] = None,
        **kwargs
    ) -> AIResponse:
        """异步对话"""
        try:
            import httpx
            
            model = model or self.config.model or "llama2"
            messages_dict = [m.to_dict() for m in messages]
            
            url = f"{self.config.base_url}/api/chat"
            
            payload = {
                "model": model,
                "messages": messages_dict,
                "stream": False,
                "options": {
                    "temperature": kwargs.get("temperature", self.config.temperature),
                    "num_predict": kwargs.get("max_tokens", self.config.max_tokens),
                }
            }
            
            async with httpx.AsyncClient(timeout=self.config.timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                
                data = response.json()
                
                content = data.get("message", {}).get("content", "")
                
                usage = AIUsage(
                    prompt_tokens=data.get("prompt_eval_count", 0),
                    completion_tokens=data.get("eval_count", 0),
                    total_tokens=data.get("prompt_eval_count", 0) + data.get("eval_count", 0),
                )
                
                return AIResponse(
                    content=content,
                    model=model,
                    provider=AIProviderType.OLLAMA,
                    usage=usage,
                    finish_reason="stop",
                )
        except ImportError:
            raise ImportError("请安装 httpx 库: pip install httpx")
    
    def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        import requests
        
        try:
            url = f"{self.config.base_url}/api/tags"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return [model["name"] for model in data.get("models", [])]
        except Exception as e:
            logger.warning(f"获取 Ollama 模型列表失败: {e}")
            return ["llama2", "mistral", "codellama", "phi"]
    
    def validate_config(self) -> bool:
        """验证配置"""
        # Ollama 不需要 API Key
        return True


__all__ = ['OllamaProvider']
