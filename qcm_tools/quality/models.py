"""
质量评估数据模型

定义质量评估相关的数据结构
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List
from qcm_tools.shared.enums import QualityLevel


@dataclass
class IndicatorResult:
    """
    质量指标检查结果
    
    Attributes:
        indicator_name: 指标名称
        score: 得分(0-100)
        level: 质量等级
        passed: 是否通过
        details: 详细信息列表
        recommendations: 改进建议列表
    
    Example:
        >>> result = IndicatorResult(
        ...     indicator_name="代码质量",
        ...     score=85.0,
        ...     level=QualityLevel.GOOD,
        ...     passed=True
        ... )
    """
    indicator_name: str
    score: float
    level: QualityLevel
    passed: bool
    details: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class QualityReport:
    """
    质量评估报告
    
    Attributes:
        project_name: 项目名称
        project_type: 项目类型
        assessment_date: 评估日期
        indicator_results: 指标结果字典
        overall_score: 总体得分
        overall_level: 总体等级
        summary: 总结
        recommendations: 总体建议列表
    
    Example:
        >>> report = QualityReport(
        ...     project_name="测试项目",
        ...     project_type="生产系统"
        ... )
    """
    project_name: str
    project_type: str
    assessment_date: datetime = field(default_factory=datetime.now)
    indicator_results: Dict[str, IndicatorResult] = field(default_factory=dict)
    overall_score: float = 0.0
    overall_level: QualityLevel = QualityLevel.PASS
    summary: str = ""
    recommendations: List[str] = field(default_factory=list)
    
    def calculate_overall_score(self):
        """计算总体得分"""
        if not self.indicator_results:
            return
        
        # 简单平均,实际可以根据项目类型调整权重
        total_score = sum(result.score for result in self.indicator_results.values())
        self.overall_score = total_score / len(self.indicator_results)
        
        # 确定等级
        if self.overall_score >= 90:
            self.overall_level = QualityLevel.EXCELLENT
        elif self.overall_score >= 80:
            self.overall_level = QualityLevel.GOOD
        elif self.overall_score >= 60:
            self.overall_level = QualityLevel.PASS
        else:
            self.overall_level = QualityLevel.FAIL
    
    def to_markdown(self) -> str:
        """生成Markdown格式报告"""
        lines = [
            f"# 质量评估报告",
            f"",
            f"**项目名称**: {self.project_name}",
            f"**项目类型**: {self.project_type}",
            f"**评估日期**: {self.assessment_date.strftime('%Y-%m-%d %H:%M:%S')}",
            f"",
            f"## 总体评估",
            f"",
            f"- **总体得分**: {self.overall_score:.1f}/100",
            f"- **质量等级**: {self.overall_level.value}",
            f"",
            f"## 详细评估",
            f""
        ]
        
        for indicator, result in self.indicator_results.items():
            status = "✅" if result.passed else "❌"
            lines.extend([
                f"### {indicator} {status}",
                f"",
                f"- **得分**: {result.score:.1f}/100",
                f"- **等级**: {result.level.value}",
                f""
            ])
            
            if result.details:
                lines.append("**详细信息**:")
                lines.append("")
                for detail in result.details:
                    lines.append(f"- {detail}")
                lines.append("")
            
            if result.recommendations:
                lines.append("**改进建议**:")
                lines.append("")
                for rec in result.recommendations:
                    lines.append(f"- {rec}")
                lines.append("")
        
        if self.recommendations:
            lines.extend([
                f"## 总体建议",
                f""
            ])
            for rec in self.recommendations:
                lines.append(f"- {rec}")
        
        return "\n".join(lines)


__all__ = ['IndicatorResult', 'QualityReport']
