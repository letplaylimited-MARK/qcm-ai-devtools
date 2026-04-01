"""置信度标注数据模型"""

from dataclasses import dataclass
from typing import Optional, List
from qcm_tools.shared.enums import InfoType, ConfidenceLevel

@dataclass
class ConfidenceAnnotation:
    """
    置信度标注
    
    Attributes:
        info_type: 信息类型
        confidence: 置信度级别
        source: 信息来源
        suggestion: 使用建议
        content: 标注内容(可选)
    
    Example:
        >>> annotation = ConfidenceAnnotation(
        ...     info_type=InfoType.CONCLUSION,
        ...     confidence=ConfidenceLevel.HIGH,
        ...     source="Python官方文档",
        ...     suggestion="可直接使用"
        ... )
    """
    info_type: InfoType
    confidence: ConfidenceLevel
    source: str
    suggestion: str
    content: Optional[str] = None
    
    def to_markdown(self) -> str:
        """生成Markdown格式"""
        lines = [
            f"[{self.info_type.value}] {self.content if self.content else ''}",
            f"[置信度] {self.confidence.value}({self._get_confidence_reason()})",
            f"[来源] {self.source}",
            f"[建议] {self.suggestion}"
        ]
        return "\n".join(lines)
    
    def _get_confidence_reason(self) -> str:
        """获取置信度原因"""
        reasons = {
            ConfidenceLevel.HIGH: "基于文献",
            ConfidenceLevel.MEDIUM: "基于推理",
            ConfidenceLevel.LOW: "可能不准确"
        }
        return reasons[self.confidence]
    
    def validate(self) -> List[str]:
        """验证标注"""
        issues = []
        
        if not self.source:
            issues.append("来源不能为空")
        
        if not self.suggestion:
            issues.append("建议不能为空")
        
        return issues

__all__ = ['ConfidenceAnnotation']
