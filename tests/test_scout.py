"""
测试 Scout (skill-03)

验证技术选型评估功能
"""

import pytest
from qcm_tools.skills import (
    Scout,
    LibraryInfo,
    LibraryEvaluation,
    ComparisonReport,
    DimensionScore,
    EvaluationDimension,
)
from qcm_tools.ai import MockAIClient


class TestLibraryInfo:
    """测试库信息"""

    def test_create_library_info(self):
        """测试创建库信息"""
        lib = LibraryInfo(
            name="fastapi",
            version="0.104.0",
            description="现代高性能 Web 框架",
            stars=60000,
            forks=5000
        )

        assert lib.name == "fastapi"
        assert lib.version == "0.104.0"
        assert lib.stars == 60000

    def test_library_info_to_dict(self):
        """测试库信息转字典"""
        lib = LibraryInfo(
            name="fastapi",
            stars=60000
        )

        result = lib.to_dict()

        assert result['name'] == "fastapi"
        assert result['stars'] == 60000


class TestDimensionScore:
    """测试维度评分"""

    def test_create_dimension_score(self):
        """测试创建维度评分"""
        score = DimensionScore(
            dimension=EvaluationDimension.FUNCTIONALITY,
            score=85.0,
            weight=0.30,
            notes="功能完整",
            details=["支持异步", "类型提示"]
        )

        assert score.dimension == EvaluationDimension.FUNCTIONALITY
        assert score.score == 85.0
        assert score.weight == 0.30
        assert len(score.details) == 2

    def test_dimension_score_to_dict(self):
        """测试维度评分转字典"""
        score = DimensionScore(
            dimension=EvaluationDimension.PERFORMANCE,
            score=90.0,
            weight=0.15
        )

        result = score.to_dict()

        assert result['dimension'] == "性能"
        assert result['score'] == 90.0
        assert result['weight'] == 0.15


class TestScout:
    """测试 Scout"""

    def test_create_scout(self):
        """测试创建 Scout"""
        scout = Scout()

        assert scout.use_ai is True
        assert scout.ai_client is not None

    def test_create_scout_with_mock(self):
        """测试使用 Mock 客户端"""
        mock_client = MockAIClient()
        scout = Scout(ai_client=mock_client)

        assert scout.ai_client is mock_client

    def test_dimension_weights(self):
        """测试维度权重"""
        assert Scout.DIMENSION_WEIGHTS[EvaluationDimension.FUNCTIONALITY] == 0.30
        assert Scout.DIMENSION_WEIGHTS[EvaluationDimension.USABILITY] == 0.20
        assert Scout.DIMENSION_WEIGHTS[EvaluationDimension.PERFORMANCE] == 0.15

        # 权重总和应该为 1.0
        total = sum(Scout.DIMENSION_WEIGHTS.values())
        assert abs(total - 1.0) < 0.001


class TestScoutEvaluation:
    """测试 Scout 评估功能"""

    @pytest.mark.asyncio
    async def test_evaluate_library(self):
        """测试评估库"""
        scout = Scout(use_ai=True)

        evaluation = await scout.evaluate_library(
            "fastapi",
            requirement="构建高性能 API"
        )

        assert isinstance(evaluation, LibraryEvaluation)
        assert evaluation.library.name == "fastapi"
        assert 0 <= evaluation.overall_score <= 100
        assert len(evaluation.dimension_scores) > 0
        assert evaluation.recommendation in [
            "highly_recommended",
            "recommended",
            "neutral",
            "not_recommended"
        ]

    @pytest.mark.asyncio
    async def test_evaluate_library_with_constraints(self):
        """测试带约束的评估"""
        scout = Scout()

        evaluation = await scout.evaluate_library(
            "django",
            requirement="构建 Web 应用",
            constraints=["Python 3.8+", "支持异步"]
        )

        assert evaluation.library.name == "django"
        assert evaluation.overall_score > 0


class TestScoutComparison:
    """测试 Scout 对比功能"""

    @pytest.mark.asyncio
    async def test_compare_libraries(self):
        """测试对比库"""
        scout = Scout()

        comparison = await scout.compare_libraries(
            ["fastapi", "flask"],
            requirement="构建 RESTful API"
        )

        assert isinstance(comparison, ComparisonReport)
        assert len(comparison.libraries) == 2
        assert comparison.winner in ["fastapi", "flask"]
        assert len(comparison.comparison_matrix) == 2
        assert comparison.summary != ""
        assert comparison.recommendation != ""

    @pytest.mark.asyncio
    async def test_compare_three_libraries(self):
        """测试对比三个库"""
        scout = Scout()

        comparison = await scout.compare_libraries(
            ["fastapi", "flask", "django"],
            requirement="构建 API"
        )

        assert len(comparison.libraries) == 3


class TestScoutRecommendation:
    """测试 Scout 推荐功能"""

    @pytest.mark.asyncio
    async def test_recommend_best(self):
        """测试推荐最佳"""
        scout = Scout()

        best = await scout.recommend_best(
            requirement="构建高性能 API",
            language="python",
            limit=3
        )

        assert isinstance(best, LibraryEvaluation)
        assert best.library.name != ""

    @pytest.mark.asyncio
    async def test_recommend_best_with_constraints(self):
        """测试带约束的推荐"""
        scout = Scout()

        best = await scout.recommend_best(
            requirement="Web 框架",
            language="python",
            constraints=["异步支持", "高性能"],
            limit=2
        )

        assert best.overall_score >= 0


class TestScoutHandoff:
    """测试 Scout 交接包"""

    def test_create_handoff(self):
        """测试创建交接包"""
        scout = Scout()

        evaluation = LibraryEvaluation(
            library=LibraryInfo(name="fastapi"),
            overall_score=85.0,
            dimension_scores=[
                DimensionScore(
                    dimension=EvaluationDimension.FUNCTIONALITY,
                    score=90.0,
                    weight=0.30
                )
            ],
            pros=["高性能", "易用"],
            cons=["学习曲线"],
            recommendation="highly_recommended",
            use_cases=["API 开发"],
            risks=["较少"]
        )

        handoff = scout.create_handoff(evaluation)

        assert handoff.from_skill == "skill-03"
        assert handoff.to_skill == "skill-04"
        assert handoff.handoff_type == "HP-B"
        assert handoff.payload['selected_library'] == "fastapi"
        assert handoff.payload['overall_score'] == 85.0


class TestEvaluationDimensions:
    """测试评估维度"""

    def test_all_dimensions_defined(self):
        """测试所有维度已定义"""
        dimensions = [
            EvaluationDimension.FUNCTIONALITY,
            EvaluationDimension.USABILITY,
            EvaluationDimension.PERFORMANCE,
            EvaluationDimension.MAINTAINABILITY,
            EvaluationDimension.COMMUNITY,
            EvaluationDimension.COMPATIBILITY,
            EvaluationDimension.DOCUMENTATION,
        ]

        assert len(dimensions) == 7

    def test_dimension_values(self):
        """测试维度值"""
        assert EvaluationDimension.FUNCTIONALITY.value == "功能性"
        assert EvaluationDimension.USABILITY.value == "易用性"
        assert EvaluationDimension.PERFORMANCE.value == "性能"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
