"""置信度标注模型测试"""

import pytest
from qcm_tools.confidence.models import ConfidenceAnnotation
from qcm_tools.shared.enums import InfoType, ConfidenceLevel


class TestConfidenceAnnotation:
    """置信度标注测试"""
    
    def test_create_annotation(self):
        """测试创建标注"""
        annotation = ConfidenceAnnotation(
            info_type=InfoType.CONCLUSION,
            confidence=ConfidenceLevel.HIGH,
            source="Python官方文档",
            suggestion="可直接使用",
            content="Python使用Timsort算法"
        )
        
        assert annotation.info_type == InfoType.CONCLUSION
        assert annotation.confidence == ConfidenceLevel.HIGH
        assert annotation.source == "Python官方文档"
    
    def test_to_markdown(self):
        """测试生成Markdown格式"""
        annotation = ConfidenceAnnotation(
            info_type=InfoType.CONCLUSION,
            confidence=ConfidenceLevel.HIGH,
            source="Python官方文档",
            suggestion="可直接使用",
            content="Python使用Timsort算法"
        )
        
        markdown = annotation.to_markdown()
        
        assert "[结论]" in markdown
        assert "[置信度] 高(基于文献)" in markdown
        assert "Python官方文档" in markdown
    
    def test_validate(self):
        """测试验证标注"""
        annotation = ConfidenceAnnotation(
            info_type=InfoType.CONCLUSION,
            confidence=ConfidenceLevel.HIGH,
            source="",
            suggestion="建议"
        )
        
        issues = annotation.validate()
        
        assert len(issues) > 0
        assert "来源不能为空" in issues
