"""质量模型测试"""

import pytest
from qcm_tools.quality.models import IndicatorResult, QualityReport
from qcm_tools.shared.enums import QualityLevel


class TestIndicatorResult:
    """指标结果测试"""
    
    def test_create_indicator_result(self):
        """测试创建指标结果"""
        result = IndicatorResult(
            indicator_name="代码质量",
            score=85.0,
            level=QualityLevel.GOOD,
            passed=True
        )
        
        assert result.indicator_name == "代码质量"
        assert result.score == 85.0
        assert result.level == QualityLevel.GOOD
        assert result.passed is True


class TestQualityReport:
    """质量报告测试"""
    
    def test_create_quality_report(self):
        """测试创建质量报告"""
        report = QualityReport(
            project_name="测试项目",
            project_type="生产系统"
        )
        
        assert report.project_name == "测试项目"
        assert report.project_type == "生产系统"
        assert len(report.indicator_results) == 0
    
    def test_calculate_overall_score(self):
        """测试计算总体得分"""
        report = QualityReport(
            project_name="测试项目",
            project_type="生产系统"
        )
        
        report.indicator_results['代码质量'] = IndicatorResult(
            indicator_name="代码质量",
            score=80.0,
            level=QualityLevel.GOOD,
            passed=True
        )
        report.indicator_results['文档完整性'] = IndicatorResult(
            indicator_name="文档完整性",
            score=90.0,
            level=QualityLevel.EXCELLENT,
            passed=True
        )
        
        report.calculate_overall_score()
        
        assert report.overall_score == 85.0
        assert report.overall_level == QualityLevel.GOOD
    
    def test_to_markdown(self):
        """测试生成Markdown报告"""
        report = QualityReport(
            project_name="测试项目",
            project_type="生产系统"
        )
        
        report.indicator_results['代码质量'] = IndicatorResult(
            indicator_name="代码质量",
            score=85.0,
            level=QualityLevel.GOOD,
            passed=True,
            details=["测试覆盖率: 85%"]
        )
        
        markdown = report.to_markdown()
        
        assert "# 质量评估报告" in markdown
        assert "测试项目" in markdown
