"""
OpenCode 提供者实现

支持 OpenCode 多模型切换功能
"""

from typing import List, Optional, Dict, Any
import logging
import os

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


@register_provider(AIProviderType.OPENCODE)
class OpenCodeProvider(AIProvider):
    """
    OpenCode 提供者
    
    支持通过 OpenCode 接入和切换不同的 AI 大模型。
    OpenCode 提供统一的 API 接口，可以无缝切换不同的模型。
    
    Example:
        >>> config = AIProviderConfig(
        ...     provider_type=AIProviderType.OPENCODE,
        ...     api_key="your-opencode-key",
        ...     model="gpt-4",  # 可以切换为其他模型
        ...     base_url="http://localhost:8080/v1"  # OpenCode 服务地址
        ... )
        >>> provider = OpenCodeProvider(config)
        
        >>> # 切换模型
        >>> provider.set_model("claude-3-opus")
        >>> response = provider.chat([AIMessage(role="user", content="Hello")])
    """
    
    # OpenCode 支持的模型映射
    MODEL_MAPPING = {
        # OpenAI 系列
        "gpt-4": "openai:gpt-4",
        "gpt-4-turbo": "openai:gpt-4-turbo",
        "gpt-4o": "openai:gpt-4o",
        "gpt-3.5-turbo": "openai:gpt-3.5-turbo",
        
        # Anthropic 系列
        "claude-3-opus": "anthropic:claude-3-opus",
        "claude-3-sonnet": "anthropic:claude-3-sonnet",
        "claude-3-haiku": "anthropic:claude-3-haiku",
        "claude-3.5-sonnet": "anthropic:claude-3.5-sonnet",
        
        # DeepSeek 系列
        "deepseek-chat": "deepseek:deepseek-chat",
        "deepseek-coder": "deepseek:deepseek-coder",
        
        # 通义千问
        "qwen-turbo": "qwen:qwen-turbo",
        "qwen-plus": "qwen:qwen-plus",
        "qwen-max": "qwen:qwen-max",
        
        # 智谱
        "glm-4": "zhipu:glm-4",
        "glm-3-turbo": "zhipu:glm-3-turbo",
        
        # 本地模型
        "llama2": "ollama:llama2",
        "mistral": "ollama:mistral",
        "codellama": "ollama:codellama",
    }
    
    AVAILABLE_MODELS = list(MODEL_MAPPING.keys())
    
    def __init__(self, config: AIProviderConfig):
        # 默认 OpenCode 服务地址
        if not config.base_url:
            config.base_url = os.getenv(
                "OPENCODE_BASE_URL",
                "http://localhost:8080/v1"
            )
        if not config.api_key:
            config.api_key = os.getenv("OPENCODE_API_KEY", "opencode")
        
        super().__init__(config)
        self._current_model = config.model
        self._client = None
    
    def _get_client(self):
        """获取 OpenCode 客户端"""
        if self._client is None:
            try:
                from openai import OpenAI
                
                self._client = OpenAI(
                    base_url=self.config.base_url,
                    api_key=self.config.api_key,
                )
            except ImportError:
                raise ImportError(
                    "请安装 openai 库: pip install openai"
                )
        return self._client
    
    def set_model(self, model: str) -> None:
        """
        切换模型
        
        Args:
            model: 模型名称（如 "gpt-4", "claude-3-opus"）
        """
        if model not in self.MODEL_MAPPING:
            logger.warning(f"未知模型: {model}，将尝试直接使用")
        self._current_model = model
        logger.info(f"OpenCode 切换模型: {model}")
    
    def get_model_backend(self, model: str = None) -> str:
        """
        获取模型后端标识
        
        Args:
            model: 模型名称
            
        Returns:
            后端标识（如 "openai", "anthropic"）
        """
        model = model or self._current_model
        mapped = self.MODEL_MAPPING.get(model, model)
        if ":" in mapped:
            return mapped.split(":")[0]
        return "unknown"
    
    def chat(
        self,
        messages: List[AIMessage],
        model: Optional[str] = None,
        **kwargs
    ) -> AIResponse:
        """同步对话"""
        client = self._get_client()
        
        model = model or self._current_model or "gpt-4"
        messages_dict = [m.to_dict() for m in messages]
        
        # 获取映射后的模型名称
        mapped_model = self.MODEL_MAPPING.get(model, model)
        
        params = {
            "model": mapped_model,
            "messages": messages_dict,
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
        }
        
        # 添加额外参数
        for key in ["top_p", "presence_penalty", "frequency_penalty", "stop"]:
            if key in kwargs:
                params[key] = kwargs[key]
        
        try:
            response = client.chat.completions.create(**params)
            
            choice = response.choices[0]
            usage = AIUsage(
                prompt_tokens=response.usage.prompt_tokens if response.usage else 0,
                completion_tokens=response.usage.completion_tokens if response.usage else 0,
                total_tokens=response.usage.total_tokens if response.usage else 0,
            )
            
            return AIResponse(
                content=choice.message.content,
                model=model,
                provider=AIProviderType.OPENCODE,
                usage=usage,
                finish_reason=choice.finish_reason,
                extra={
                    "backend": self.get_model_backend(model),
                    "mapped_model": mapped_model,
                }
            )
        except Exception as e:
            logger.error(f"OpenCode 请求失败: {e}")
            raise
    
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
            
            model = model or self._current_model or "gpt-4"
            messages_dict = [m.to_dict() for m in messages]
            mapped_model = self.MODEL_MAPPING.get(model, model)
            
            params = {
                "model": mapped_model,
                "messages": messages_dict,
                "temperature": kwargs.get("temperature", self.config.temperature),
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            }
            
            response = await client.chat.completions.create(**params)
            
            choice = response.choices[0]
            usage = AIUsage(
                prompt_tokens=response.usage.prompt_tokens if response.usage else 0,
                completion_tokens=response.usage.completion_tokens if response.usage else 0,
                total_tokens=response.usage.total_tokens if response.usage else 0,
            )
            
            return AIResponse(
                content=choice.message.content,
                model=model,
                provider=AIProviderType.OPENCODE,
                usage=usage,
                finish_reason=choice.finish_reason,
            )
        except ImportError:
            raise ImportError("请安装 openai 库: pip install openai")
    
    def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        return self.AVAILABLE_MODELS.copy()
    
    def get_models_by_provider(self) -> Dict[str, List[str]]:
        """
        按提供者分组获取模型列表
        
        Returns:
            按提供者分组的模型字典
        """
        result = {}
        for model, mapped in self.MODEL_MAPPING.items():
            provider = mapped.split(":")[0] if ":" in mapped else "other"
            if provider not in result:
                result[provider] = []
            result[provider].append(model)
        return result
    
    def validate_config(self) -> bool:
        """验证配置"""
        # OpenCode 默认可用
        return True
    
    def __repr__(self) -> str:
        return f"OpenCodeProvider(base_url={self.config.base_url}, model={self._current_model})"


__all__ = ['OpenCodeProvider']
