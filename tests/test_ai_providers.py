"""
AI 提供者测试

测试多 AI 大模型兼容支持
"""

import pytest
from qcm_tools.ai.providers.base import (
    AIProviderType,
    AIProviderConfig,
    AIMessage,
    AIResponse,
    AIUsage,
)
from qcm_tools.ai.providers.factory import create_provider, get_available_providers


class TestAIProviderConfig:
    """测试 AI 提供者配置"""
    
    def test_provider_type_values(self):
        """测试提供者类型枚举值"""
        assert AIProviderType.OPENAI.value == "openai"
        assert AIProviderType.ANTHROPIC.value == "anthropic"
        assert AIProviderType.DEEPSEEK.value == "deepseek"
        assert AIProviderType.GEMINI.value == "gemini"
        assert AIProviderType.OLLAMA.value == "ollama"
        assert AIProviderType.OPENCODE.value == "opencode"
    
    def test_config_creation(self):
        """测试配置创建"""
        config = AIProviderConfig(
            provider_type=AIProviderType.OPENAI,
            api_key="test-key",
            model="gpt-4",
            temperature=0.5
        )
        assert config.provider_type == AIProviderType.OPENAI
        assert config.api_key == "test-key"
        assert config.model == "gpt-4"
        assert config.temperature == 0.5
    
    def test_message_to_dict(self):
        """测试消息转换"""
        msg = AIMessage(role="user", content="Hello")
        d = msg.to_dict()
        assert d["role"] == "user"
        assert d["content"] == "Hello"
    
    def test_usage_creation(self):
        """测试使用统计"""
        usage = AIUsage(
            prompt_tokens=10,
            completion_tokens=20,
            total_tokens=30
        )
        assert usage.prompt_tokens == 10
        assert usage.completion_tokens == 20
        assert usage.total_tokens == 30


class TestAIProviderFactory:
    """测试 AI 提供者工厂"""
    
    def test_get_available_providers(self):
        """测试获取可用提供者"""
        providers = get_available_providers()
        assert isinstance(providers, list)
        assert len(providers) > 0
        
        # 检查 OpenCode 是否可用
        opencode = next(
            (p for p in providers if p["type"] == "opencode"),
            None
        )
        assert opencode is not None
    
    def test_create_opencode_provider(self):
        """测试创建 OpenCode 提供者"""
        config = AIProviderConfig(
            provider_type=AIProviderType.OPENCODE,
            base_url="http://localhost:8080/v1",
            model="gpt-4"
        )
        provider = create_provider(config=config)
        assert provider.provider_name == "opencode"
        assert provider.default_model == "gpt-4"
    
    def test_create_provider_with_kwargs(self):
        """测试使用关键字参数创建提供者"""
        provider = create_provider(
            provider_type=AIProviderType.OLLAMA,
            base_url="http://localhost:11434",
            model="llama2"
        )
        assert provider.provider_name == "ollama"


class TestOpenCodeProvider:
    """测试 OpenCode 提供者"""
    
    def test_provider_initialization(self):
        """测试提供者初始化"""
        from qcm_tools.ai.providers.opencode_provider import OpenCodeProvider
        
        config = AIProviderConfig(
            provider_type=AIProviderType.OPENCODE,
            model="gpt-4"
        )
        provider = OpenCodeProvider(config)
        
        assert provider.default_model == "gpt-4"
        assert len(provider.get_available_models()) > 0
    
    def test_model_mapping(self):
        """测试模型映射"""
        from qcm_tools.ai.providers.opencode_provider import OpenCodeProvider
        
        config = AIProviderConfig(
            provider_type=AIProviderType.OPENCODE,
            model="gpt-4"
        )
        provider = OpenCodeProvider(config)
        
        # 测试模型后端识别
        assert provider.get_model_backend("gpt-4") == "openai"
        assert provider.get_model_backend("claude-3-opus") == "anthropic"
        assert provider.get_model_backend("deepseek-chat") == "deepseek"
    
    def test_set_model(self):
        """测试切换模型"""
        from qcm_tools.ai.providers.opencode_provider import OpenCodeProvider
        
        config = AIProviderConfig(
            provider_type=AIProviderType.OPENCODE,
            model="gpt-4"
        )
        provider = OpenCodeProvider(config)
        
        provider.set_model("claude-3-opus")
        assert provider._current_model == "claude-3-opus"
    
    def test_get_models_by_provider(self):
        """测试按提供者分组获取模型"""
        from qcm_tools.ai.providers.opencode_provider import OpenCodeProvider
        
        config = AIProviderConfig(
            provider_type=AIProviderType.OPENCODE
        )
        provider = OpenCodeProvider(config)
        
        grouped = provider.get_models_by_provider()
        
        assert "openai" in grouped
        assert "anthropic" in grouped
        assert "deepseek" in grouped


class TestOllamaProvider:
    """测试 Ollama 提供者"""
    
    def test_provider_initialization(self):
        """测试提供者初始化"""
        from qcm_tools.ai.providers.ollama_provider import OllamaProvider
        
        config = AIProviderConfig(
            provider_type=AIProviderType.OLLAMA,
            base_url="http://localhost:11434",
            model="llama2"
        )
        provider = OllamaProvider(config)
        
        assert provider.default_model == "llama2"
        assert provider.config.base_url == "http://localhost:11434"
    
    def test_default_base_url(self):
        """测试默认 URL"""
        from qcm_tools.ai.providers.ollama_provider import OllamaProvider
        
        config = AIProviderConfig(
            provider_type=AIProviderType.OLLAMA
        )
        provider = OllamaProvider(config)
        
        assert provider.config.base_url == "http://localhost:11434"


class TestDeepSeekProvider:
    """测试 DeepSeek 提供者"""
    
    def test_provider_initialization(self):
        """测试提供者初始化"""
        from qcm_tools.ai.providers.deepseek_provider import DeepSeekProvider
        
        config = AIProviderConfig(
            provider_type=AIProviderType.DEEPSEEK,
            api_key="test-key",
            model="deepseek-chat"
        )
        provider = DeepSeekProvider(config)
        
        assert provider.default_model == "deepseek-chat"
        assert len(provider.get_available_models()) > 0


class TestAnthropicProvider:
    """测试 Anthropic 提供者"""
    
    def test_provider_initialization(self):
        """测试提供者初始化"""
        from qcm_tools.ai.providers.anthropic_provider import AnthropicProvider
        
        config = AIProviderConfig(
            provider_type=AIProviderType.ANTHROPIC,
            api_key="test-key",
            model="claude-3-opus-20240229"
        )
        provider = AnthropicProvider(config)
        
        assert provider.default_model == "claude-3-opus-20240229"
        assert len(provider.get_available_models()) > 0


class TestGeminiProvider:
    """测试 Gemini 提供者"""
    
    def test_provider_initialization(self):
        """测试提供者初始化"""
        from qcm_tools.ai.providers.gemini_provider import GeminiProvider
        
        config = AIProviderConfig(
            provider_type=AIProviderType.GEMINI,
            api_key="test-key",
            model="gemini-pro"
        )
        provider = GeminiProvider(config)
        
        assert provider.default_model == "gemini-pro"
        assert "gemini-pro" in provider.get_available_models()


# 集成测试（需要实际 API）
@pytest.mark.integration
class TestAIProviderIntegration:
    """集成测试"""
    
    @pytest.mark.skip(reason="需要 OpenCode 服务运行")
    def test_opencode_chat(self):
        """测试 OpenCode 对话"""
        config = AIProviderConfig(
            provider_type=AIProviderType.OPENCODE,
            base_url="http://localhost:8080/v1"
        )
        provider = create_provider(config)
        
        response = provider.chat([
            AIMessage(role="user", content="Hello!")
        ])
        
        assert isinstance(response, AIResponse)
        assert response.content
    
    @pytest.mark.skip(reason="需要 Ollama 服务运行")
    def test_ollama_chat(self):
        """测试 Ollama 对话"""
        config = AIProviderConfig(
            provider_type=AIProviderType.OLLAMA,
            model="llama2"
        )
        provider = create_provider(config)
        
        response = provider.chat([
            AIMessage(role="user", content="Hello!")
        ])
        
        assert isinstance(response, AIResponse)
