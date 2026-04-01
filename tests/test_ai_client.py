"""
测试 AI Client 抽象层

验证 AI 客户端的基础功能
"""

import pytest
from qcm_tools.ai import (
    AIClient,
    AIClientFactory,
    Message,
    ChatResponse,
    EmbeddingResponse,
    MockAIClient,
)
from qcm_tools.ai.client import MessageRole


class TestMessage:
    """测试消息类"""

    def test_create_message(self):
        """测试创建消息"""
        msg = Message(
            role=MessageRole.USER,
            content="Hello"
        )

        assert msg.role == MessageRole.USER
        assert msg.content == "Hello"
        assert msg.name is None

    def test_message_to_dict(self):
        """测试消息转字典"""
        msg = Message(
            role=MessageRole.USER,
            content="Hello",
            name="test_user"
        )

        result = msg.to_dict()

        assert result['role'] == 'user'
        assert result['content'] == 'Hello'
        assert result['name'] == 'test_user'

    def test_system_message(self):
        """测试系统消息"""
        msg = Message.system("You are a helpful assistant")

        assert msg.role == MessageRole.SYSTEM
        assert msg.content == "You are a helpful assistant"

    def test_user_message(self):
        """测试用户消息"""
        msg = Message.user("Hello")

        assert msg.role == MessageRole.USER
        assert msg.content == "Hello"

    def test_assistant_message(self):
        """测试助手消息"""
        msg = Message.assistant("Hi there")

        assert msg.role == MessageRole.ASSISTANT
        assert msg.content == "Hi there"


class TestChatResponse:
    """测试对话响应"""

    def test_create_chat_response(self):
        """测试创建对话响应"""
        response = ChatResponse(
            content="Hello",
            model="gpt-4",
            usage={'prompt_tokens': 10, 'completion_tokens': 5}
        )

        assert response.content == "Hello"
        assert response.model == "gpt-4"
        assert response.usage['prompt_tokens'] == 10


class TestEmbeddingResponse:
    """测试嵌入响应"""

    def test_create_embedding_response(self):
        """测试创建嵌入响应"""
        response = EmbeddingResponse(
            embedding=[0.1, 0.2, 0.3],
            model="text-embedding-ada-002"
        )

        assert len(response.embedding) == 3
        assert response.model == "text-embedding-ada-002"


class TestAIClientFactory:
    """测试客户端工厂"""

    def test_create_mock_client(self):
        """测试创建 Mock 客户端"""
        client = AIClientFactory.create(provider="mock")

        assert isinstance(client, MockAIClient)

    def test_create_mock_client_from_config(self):
        """测试从配置创建 Mock 客户端"""
        config = {
            'provider': 'mock',
            'model': 'test-model'
        }

        client = AIClientFactory.from_config(config)

        assert isinstance(client, MockAIClient)

    def test_unsupported_provider(self):
        """测试不支持的提供商"""
        with pytest.raises(ValueError) as exc_info:
            AIClientFactory.create(provider="unknown")

        assert "Unsupported AI provider" in str(exc_info.value)

    def test_anthropic_not_implemented(self):
        """测试 Anthropic 未实现"""
        with pytest.raises(ValueError) as exc_info:
            AIClientFactory.create(provider="anthropic")

        assert "not implemented" in str(exc_info.value)


class TestMockAIClient:
    """测试 Mock 客户端"""

    @pytest.mark.asyncio
    async def test_chat(self):
        """测试对话"""
        client = MockAIClient()

        response = await client.chat([
            Message.user("Hello")
        ])

        assert isinstance(response, ChatResponse)
        assert "Mock response" in response.content
        assert response.model == "mock-model"

    @pytest.mark.asyncio
    async def test_embed(self):
        """测试嵌入"""
        client = MockAIClient()

        response = await client.embed("Hello world")

        assert isinstance(response, EmbeddingResponse)
        assert len(response.embedding) == 16  # 32/2
        assert response.model == "mock-embedding"

    @pytest.mark.asyncio
    async def test_analyze_code(self):
        """测试代码分析"""
        client = MockAIClient()

        code = "def hello():\n    print('Hello')\n"
        response = await client.analyze_code(code)

        assert response.code == code
        assert response.score > 0
        assert 'lines' in response.metadata

    @pytest.mark.asyncio
    async def test_analyze_code_with_print(self):
        """测试包含 print 的代码分析"""
        client = MockAIClient()

        code = "print('Hello')"
        response = await client.analyze_code(code)

        assert "日志系统" in " ".join(response.suggestions)

    @pytest.mark.asyncio
    async def test_call_count(self):
        """测试调用计数"""
        client = MockAIClient()

        await client.chat([Message.user("test1")])
        await client.chat([Message.user("test2")])

        assert client.call_count == 2

    def test_reset(self):
        """测试重置"""
        client = MockAIClient()
        client.call_count = 5

        client.reset()

        assert client.call_count == 0


class TestAIClientIntegration:
    """测试客户端集成"""

    @pytest.mark.asyncio
    async def test_generate_config_from_description(self):
        """测试从描述生成配置"""
        client = MockAIClient()

        config = await client.generate_config_from_description(
            "开发一个 FastAPI 项目"
        )

        assert 'description' in config
        assert 'ai_suggestion' in config

    @pytest.mark.asyncio
    async def test_review_code(self):
        """测试代码审查"""
        client = MockAIClient()

        analysis = await client.review_code(
            "def test(): pass",
            focus_areas=["security"]
        )

        assert analysis.score > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
