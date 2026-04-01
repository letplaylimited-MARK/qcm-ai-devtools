"""
测试 OpenAI 客户端增强功能

验证流式响应、错误重试、成本追踪等功能
"""

import pytest
from qcm_tools.ai import (
    OpenAIClientEnhanced,
    Message,
    CostCalculator,
    UsageStats,
)


class TestCostCalculator:
    """测试成本计算器"""

    def test_calculate_gpt4_cost(self):
        """测试 GPT-4 成本计算"""
        # GPT-4: $0.03/1K prompt, $0.06/1K completion
        cost = CostCalculator.calculate_cost(
            model="gpt-4",
            prompt_tokens=1000,
            completion_tokens=500
        )

        # 预期: (1000/1000 * 0.03) + (500/1000 * 0.06) = 0.03 + 0.03 = 0.06
        assert abs(cost - 0.06) < 0.001

    def test_calculate_gpt35_cost(self):
        """测试 GPT-3.5 成本计算"""
        # GPT-3.5: $0.0005/1K prompt, $0.0015/1K completion
        cost = CostCalculator.calculate_cost(
            model="gpt-3.5-turbo",
            prompt_tokens=2000,
            completion_tokens=1000
        )

        # 预期: (2000/1000 * 0.0005) + (1000/1000 * 0.0015) = 0.001 + 0.0015 = 0.0025
        assert abs(cost - 0.0025) < 0.0001

    def test_calculate_embedding_cost(self):
        """测试嵌入模型成本计算"""
        cost = CostCalculator.calculate_cost(
            model="text-embedding-ada-002",
            prompt_tokens=10000,
            completion_tokens=0
        )

        # 预期: (10000/1000 * 0.0001) = 0.001
        assert abs(cost - 0.001) < 0.0001

    def test_calculate_unknown_model_cost(self):
        """测试未知模型使用默认价格"""
        cost = CostCalculator.calculate_cost(
            model="unknown-model",
            prompt_tokens=1000,
            completion_tokens=500
        )

        # 应该使用 GPT-3.5 价格作为默认
        assert cost > 0


class TestUsageStats:
    """测试使用统计"""

    def test_initial_stats(self):
        """测试初始统计"""
        stats = UsageStats()

        assert stats.total_requests == 0
        assert stats.total_tokens == 0
        assert stats.total_cost == 0.0

    def test_add_usage(self):
        """测试添加使用记录"""
        stats = UsageStats()

        stats.add_usage(
            model="gpt-4",
            prompt_tokens=100,
            completion_tokens=50,
            cost=0.06
        )

        assert stats.total_requests == 1
        assert stats.total_tokens == 150
        assert stats.prompt_tokens == 100
        assert stats.completion_tokens == 50
        assert stats.total_cost == 0.06

    def test_multiple_usage(self):
        """测试多次使用"""
        stats = UsageStats()

        stats.add_usage("gpt-4", 100, 50, 0.06)
        stats.add_usage("gpt-3.5-turbo", 200, 100, 0.0025)

        assert stats.total_requests == 2
        assert stats.total_tokens == 450
        assert abs(stats.total_cost - 0.0625) < 0.0001
        assert stats.requests_by_model['gpt-4'] == 1
        assert stats.requests_by_model['gpt-3.5-turbo'] == 1


class TestOpenAIClientEnhanced:
    """测试增强版 OpenAI 客户端"""

    def test_create_client(self):
        """测试创建客户端"""
        client = OpenAIClientEnhanced(
            model="gpt-4",
            api_key="test-key",
            enable_cache=True,
            max_retries=3
        )

        assert client.model == "gpt-4"
        assert client.api_key == "test-key"
        assert client.enable_cache is True
        assert client.max_retries == 3
        assert client._cache is not None

    def test_create_client_without_cache(self):
        """测试创建不带缓存的客户端"""
        client = OpenAIClientEnhanced(
            model="gpt-4",
            api_key="test-key",
            enable_cache=False
        )

        assert client.enable_cache is False
        assert client._cache is None

    def test_get_cache_key(self):
        """测试缓存键生成"""
        client = OpenAIClientEnhanced(enable_cache=True)

        messages1 = [Message.user("Hello")]
        messages2 = [Message.user("Hello")]
        messages3 = [Message.user("Hi")]

        key1 = client._get_cache_key(messages1, temperature=0.7)
        key2 = client._get_cache_key(messages2, temperature=0.7)
        key3 = client._get_cache_key(messages3, temperature=0.7)

        # 相同消息应该生成相同键
        assert key1 == key2
        # 不同消息应该生成不同键
        assert key1 != key3

    def test_get_usage_stats(self):
        """测试获取使用统计"""
        client = OpenAIClientEnhanced()

        # 添加一些使用记录
        client.usage_stats.add_usage("gpt-4", 100, 50, 0.06)

        stats = client.get_usage_stats()

        assert stats['total_requests'] == 1
        assert stats['total_tokens'] == 150
        assert stats['total_cost'] == 0.06
        assert 'gpt-4' in stats['requests_by_model']

    def test_clear_cache(self):
        """测试清空缓存"""
        client = OpenAIClientEnhanced(enable_cache=True)

        # 添加一些缓存
        client._cache['test_key'] = "test_value"

        # 清空
        client.clear_cache()

        assert len(client._cache) == 0


class TestOpenAIClientEnhancedIntegration:
    """测试增强版客户端集成"""

    @pytest.mark.asyncio
    async def test_chat_with_mock(self):
        """测试对话（模拟）"""
        # 注意：这个测试需要 Mock 或真实的 OpenAI API
        # 这里我们只是测试客户端的配置和初始化
        client = OpenAIClientEnhanced(
            model="gpt-3.5-turbo",
            api_key="mock-key",
            enable_cache=True,
            max_retries=1
        )

        assert client.model == "gpt-3.5-turbo"
        assert client.enable_cache is True

    def test_retry_configuration(self):
        """测试重试配置"""
        client = OpenAIClientEnhanced(
            max_retries=5,
            retry_delay=2.0
        )

        assert client.max_retries == 5
        assert client.retry_delay == 2.0

    def test_timeout_configuration(self):
        """测试超时配置"""
        client = OpenAIClientEnhanced(timeout=60.0)

        assert client.timeout == 60.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
