#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QCM工具系统基础使用示例

演示如何使用QCM工具系统创建项目配置、质量报告和置信度标注
"""

from qcm_tools import ProjectType, ProjectScale, Role, ConfidenceLevel, InfoType, QualityLevel
from qcm_tools.config.models import ProjectConfig, QualityStandard
from qcm_tools.quality.models import QualityReport, IndicatorResult
from qcm_tools.confidence.models import ConfidenceAnnotation


def example_project_config():
    """示例: 创建项目配置"""
    print("=== 项目配置示例 ===\n")
    
    # 创建质量标准
    quality = QualityStandard(
        functionality="所有功能正常",
        code_quality="测试覆盖≥85%",
        documentation="完整API文档+部署文档",
        security="无安全漏洞"
    )
    
    # 创建项目配置
    config = ProjectConfig(
        name="用户管理API",
        description="RESTful API服务",
        project_type=ProjectType.PRODUCTION,
        scale=ProjectScale.MEDIUM,
        tech_stack=["Python", "FastAPI", "PostgreSQL"],
        roles=[Role.ARCHITECT, Role.ENGINEER, Role.QA],
        quality_standards=quality
    )
    
    # 导出为YAML
    print("项目配置(YAML格式):")
    print(config.to_yaml())
    print()


def example_quality_report():
    """示例: 创建质量报告"""
    print("=== 质量报告示例 ===\n")
    
    # 创建质量报告
    report = QualityReport(
        project_name="用户管理API",
        project_type="生产系统"
    )
    
    # 添加指标结果
    report.indicator_results['代码质量'] = IndicatorResult(
        indicator_name="代码质量",
        score=85.0,
        level=QualityLevel.GOOD,
        passed=True,
        details=["测试覆盖率: 85%", "代码复杂度: 8.5"],
        recommendations=["建议提高测试覆盖率至90%"]
    )
    
    report.indicator_results['文档完整性'] = IndicatorResult(
        indicator_name="文档完整性",
        score=90.0,
        level=QualityLevel.EXCELLENT,
        passed=True,
        details=["✅ README.md", "✅ API文档", "✅ 部署文档"]
    )
    
    # 计算总体得分
    report.calculate_overall_score()
    
    # 生成Markdown报告
    print(report.to_markdown())
    print()


def example_confidence_annotation():
    """示例: 置信度标注"""
    print("=== 置信度标注示例 ===\n")
    
    # 创建标注
    annotation = ConfidenceAnnotation(
        info_type=InfoType.CONCLUSION,
        confidence=ConfidenceLevel.HIGH,
        source="Python官方文档 https://docs.python.org/3/",
        suggestion="可直接使用",
        content="Python的list.sort()方法使用Timsort算法"
    )
    
    # 生成Markdown格式
    print(annotation.to_markdown())
    print()
    
    # 验证标注
    issues = annotation.validate()
    if issues:
        print(f"验证问题: {issues}")
    else:
        print("✅ 标注验证通过")
    print()


if __name__ == "__main__":
    print("QCM工具系统基础使用示例\n")
    print("=" * 60)
    print()
    
    example_project_config()
    example_quality_report()
    example_confidence_annotation()
    
    print("=" * 60)
    print("示例运行完成!")
