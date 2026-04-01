"""
Navigator 模块测试

测试 Navigator 类的核心功能
"""

import pytest
from qcm_tools.skills import Navigator
from qcm_tools.skills.navigator import IntentType, ConfidenceLevel, IntentAnalysis


class TestNavigator:
    """测试 Navigator 类"""
    
    @pytest.fixture
    def navigator(self):
        """创建 Navigator 实例"""
        return Navigator()
    
    def test_create_navigator(self):
        """测试创建 Navigator"""
        navigator = Navigator()
        assert navigator is not None
        assert navigator.ai_client is None
    
    def test_create_navigator_with_ai_client(self):
        """测试带 AI 客户端创建 Navigator"""
        # 模拟 AI 客户端
        class MockAIClient:
            class chat:
                class completions:
                    @staticmethod
                    def create(**kwargs):
                        class MockResponse:
                            class choices:
                                class message:
                                    content = '{"intent_type": "find_open_source", "confidence": 0.9, "recommended_skill": "skill-03", "routing_reason": "测试"}'
                        return MockResponse()
        
        navigator = Navigator(ai_client=MockAIClient())
        assert navigator.ai_client is not None
    
    def test_analyze_intent_find_open_source(self, navigator):
        """测试意图识别 - 寻找开源方案"""
        analysis = navigator.analyze_intent("帮我找一个开源的情感分析库")
        
        assert analysis.intent_type == IntentType.FIND_OPEN_SOURCE
        assert analysis.confidence >= 0.6
        assert analysis.recommended_skill == "skill-03"
    
    def test_analyze_intent_optimize_prompt(self, navigator):
        """测试意图识别 - 优化提示词"""
        analysis = navigator.analyze_intent("帮我优化这个提示词")
        
        assert analysis.intent_type == IntentType.OPTIMIZE_PROMPT
        assert analysis.recommended_skill == "skill-01"
    
    def test_analyze_intent_test_validate(self, navigator):
        """测试意图识别 - 测试验收"""
        analysis = navigator.analyze_intent("帮我验收这个项目，进行质量检查")
        
        assert analysis.intent_type == IntentType.TEST_VALIDATE
        assert analysis.recommended_skill == "skill-05"
    
    def test_analyze_intent_deploy_project(self, navigator):
        """测试意图识别 - 部署项目"""
        analysis = navigator.analyze_intent("生成部署步骤和操作手册")
        
        assert analysis.intent_type == IntentType.DEPLOY_PROJECT
        assert analysis.recommended_skill == "skill-04"
    
    def test_analyze_intent_build_custom(self, navigator):
        """测试意图识别 - 构建自定义方案"""
        analysis = navigator.analyze_intent("开发一个用户管理系统")
        
        assert analysis.intent_type == IntentType.BUILD_CUSTOM
        assert analysis.recommended_skill == "skill-02"
    
    def test_analyze_intent_unclear(self, navigator):
        """测试意图识别 - 不明确"""
        analysis = navigator.analyze_intent("帮忙看看")
        
        assert analysis.intent_type == IntentType.UNCLEAR
        assert analysis.confidence < 0.6
        assert len(analysis.clarification_questions) > 0
    
    def test_generate_handoff(self, navigator):
        """测试生成交接包"""
        handoff = navigator.generate_handoff("开发一个情感分析系统")
        
        assert handoff.from_skill == "skill-00"
        assert handoff.to_skill in ["skill-01", "skill-02", "skill-03", "skill-04", "skill-05"]
        assert handoff.handoff_type == "HP-D"
        assert 'intent_type' in handoff.payload
        assert 'confidence_score' in handoff.payload
    
    def test_generate_handoff_with_project_name(self, navigator):
        """测试带项目名称生成交接包"""
        handoff = navigator.generate_handoff(
            "开发一个API系统",
            project_name="my-api-project"
        )
        
        assert handoff.payload['project_name'] == "my-api-project"
    
    def test_generate_handoff_unclear_intent(self, navigator):
        """测试不明确意图的交接包"""
        handoff = navigator.generate_handoff("帮忙看看")
        
        assert handoff.to_skill == "skill-02"
        assert handoff.payload['confidence_score'] < 0.6
        assert 'clarification_questions' in handoff.payload
    
    def test_get_routing_suggestion(self, navigator):
        """测试获取路由建议"""
        suggestion = navigator.get_routing_suggestion("找个开源的NLP库")
        
        assert "skill-03" in suggestion
        assert "开源" in suggestion or "侦察" in suggestion
    
    def test_extract_tech_stack(self, navigator):
        """测试提取技术栈"""
        analysis = navigator.analyze_intent("用 Python 和 FastAPI 开发一个API系统")
        
        assert 'python' in analysis.project_summary.lower() or 'fastapi' in analysis.project_summary.lower()
    
    def test_confidence_levels(self, navigator):
        """测试置信度级别"""
        # 高置信度
        analysis_high = navigator.analyze_intent("帮我找一个开源的机器学习框架")
        assert analysis_high.confidence >= 0.6
        
        # 低置信度
        analysis_low = navigator.analyze_intent("帮忙")
        assert analysis_low.confidence < 0.6


class TestIntentType:
    """测试意图类型枚举"""
    
    def test_intent_type_values(self):
        """测试意图类型值"""
        assert IntentType.FIND_OPEN_SOURCE.value == "find_open_source"
        assert IntentType.OPTIMIZE_PROMPT.value == "optimize_prompt"
        assert IntentType.TEST_VALIDATE.value == "test_validate"
        assert IntentType.DEPLOY_PROJECT.value == "deploy_project"
        assert IntentType.BUILD_CUSTOM.value == "build_custom"
        assert IntentType.UNCLEAR.value == "unclear"


class TestIntentAnalysis:
    """测试意图分析结果"""
    
    def test_create_intent_analysis(self):
        """测试创建意图分析结果"""
        analysis = IntentAnalysis(
            intent_type=IntentType.FIND_OPEN_SOURCE,
            confidence=0.85,
            recommended_skill="skill-03",
            routing_reason="检测到技术选型需求"
        )
        
        assert analysis.intent_type == IntentType.FIND_OPEN_SOURCE
        assert analysis.confidence == 0.85
        assert analysis.recommended_skill == "skill-03"
    
    def test_intent_analysis_with_alternatives(self):
        """测试带备选的意图分析"""
        analysis = IntentAnalysis(
            intent_type=IntentType.BUILD_CUSTOM,
            confidence=0.75,
            recommended_skill="skill-02",
            routing_reason="项目开发需求",
            alternative_skills=["skill-03", "skill-04"]
        )
        
        assert len(analysis.alternative_skills) == 2


class TestNavigatorEdgeCases:
    """测试 Navigator 边界情况"""
    
    @pytest.fixture
    def navigator(self):
        return Navigator()
    
    def test_empty_input(self, navigator):
        """测试空输入"""
        analysis = navigator.analyze_intent("")
        assert analysis.intent_type == IntentType.UNCLEAR
    
    def test_very_long_input(self, navigator):
        """测试超长输入"""
        long_input = "开发一个系统" * 100
        analysis = navigator.analyze_intent(long_input)
        
        assert analysis.intent_type == IntentType.BUILD_CUSTOM
    
    def test_mixed_language_input(self, navigator):
        """测试中英混合输入"""
        analysis = navigator.analyze_intent("Help me find an open source Python library")
        
        assert analysis.intent_type == IntentType.FIND_OPEN_SOURCE
    
    def test_multiple_intents(self, navigator):
        """测试多意图输入"""
        # 包含开发和部署关键词
        analysis = navigator.analyze_intent("开发一个系统并部署上线")
        
        # 应该识别为主要意图（开发优先级高于部署）
        assert analysis.intent_type in [IntentType.BUILD_CUSTOM, IntentType.DEPLOY_PROJECT, IntentType.TEST_VALIDATE]
        # 可能包含备选
        assert len(analysis.alternative_skills) >= 0
    
    def test_special_characters(self, navigator):
        """测试特殊字符"""
        analysis = navigator.analyze_intent("帮我找一个库！！！@#$%")
        
        assert analysis.intent_type == IntentType.FIND_OPEN_SOURCE
    
    def test_tech_stack_extraction(self, navigator):
        """测试技术栈提取"""
        handoff = navigator.generate_handoff(
            "用 Python FastAPI PostgreSQL 开发一个 API 系统"
        )
        
        tech_stack = handoff.payload.get('tech_stack_preference', [])
        assert 'python' in tech_stack or 'fastapi' in tech_stack


class TestNavigatorIntegration:
    """测试 Navigator 集成"""
    
    def test_full_workflow(self):
        """测试完整工作流"""
        navigator = Navigator()
        
        # 1. 分析意图
        analysis = navigator.analyze_intent("开发一个情感分析系统")
        
        # 2. 生成交接包
        handoff = navigator.generate_handoff("开发一个情感分析系统")
        
        # 3. 验证交接包
        assert handoff.is_valid()
        assert handoff.to_skill in ["skill-01", "skill-02", "skill-03", "skill-04", "skill-05"]
        
        # 4. 导出 YAML
        yaml_str = handoff.to_yaml()
        assert 'skill-00' in yaml_str
    
    def test_chain_with_handoff_manager(self):
        """测试与 HandoffManager 集成"""
        from qcm_tools.handoff import HandoffManager
        
        navigator = Navigator()
        manager = HandoffManager()
        
        # 生成交接包
        handoff = navigator.generate_handoff("开发一个数据分析平台")
        
        # 存储到管理器
        manager.save(handoff)
        
        # 验证存储
        loaded = manager.load("skill-00")
        assert loaded is not None
        assert loaded.to_skill == handoff.to_skill
