"""ConfidenceAnnotator测试"""

import pytest
from qcm_tools.confidence import ConfidenceAnnotator
from qcm_tools.shared.enums import InfoType, ConfidenceLevel


class TestConfidenceAnnotator:
    """置信度标注器测试"""
    
    @pytest.fixture
    def annotator(self):
        """创建标注器实例"""
        return ConfidenceAnnotator()
    
    def test_manual_annotate(self, annotator):
        """测试手动标注"""
        annotation = annotator.annotate(
            content="Python使用Timsort算法",
            info_type=InfoType.CONCLUSION,
            source="Python官方文档"
        )
        
        assert annotation.content == "Python使用Timsort算法"
        assert annotation.info_type == InfoType.CONCLUSION
        assert annotation.source == "Python官方文档"
    
    def test_auto_annotate_conclusion(self, annotator):
        """测试自动标注 - 结论类型"""
        annotation = annotator.auto_annotate(
            "因此,Python使用Timsort算法进行排序"
        )
        
        assert annotation.info_type == InfoType.CONCLUSION
        assert annotation.confidence is not None
    
    def test_auto_annotate_data(self, annotator):
        """测试自动标注 - 数据类型"""
        annotation = annotator.auto_annotate(
            "统计显示,性能提升了50%"
        )
        
        assert annotation.info_type == InfoType.DATA
    
    def test_auto_annotate_citation(self, annotator):
        """测试自动标注 - 引用类型"""
        annotation = annotator.auto_annotate(
            "根据官方文档,Python支持多种数据类型"
        )
        
        assert annotation.info_type == InfoType.CITATION
    
    def test_auto_annotate_inference(self, annotator):
        """测试自动标注 - 推断类型"""
        annotation = annotator.auto_annotate(
            "推测这可能是因为算法优化导致的"
        )
        
        assert annotation.info_type == InfoType.INFERENCE
    
    def test_batch_annotate(self, annotator):
        """测试批量标注"""
        contents = [
            "因此得出结论",
            "数据显示增长50%",
            "根据官方文档"
        ]
        
        annotations = annotator.batch_annotate(contents)
        
        assert len(annotations) == 3
        assert all(a.content is not None for a in annotations)
    
    def test_extract_annotations(self, annotator):
        """测试提取标注"""
        text = """
[结论] Python使用Timsort算法
[置信度] 高(基于文献)
[来源] Python官方文档
[建议] 可直接使用
"""
        annotations = annotator.extract_annotations(text)
        
        assert len(annotations) > 0
        assert annotations[0].info_type == InfoType.CONCLUSION
        assert annotations[0].confidence == ConfidenceLevel.HIGH
    
    def test_suggest_confidence_high(self, annotator):
        """测试置信度建议 - 高"""
        confidence, reason = annotator.suggest_confidence(
            "根据官方文档,这是确定的结论",
            "官方文档"
        )
        
        assert confidence == ConfidenceLevel.HIGH
        assert "权威" in reason or "官方" in reason
    
    def test_suggest_confidence_low(self, annotator):
        """测试置信度建议 - 低"""
        confidence, reason = annotator.suggest_confidence(
            "这可能是个问题,或许需要验证"
        )
        
        assert confidence == ConfidenceLevel.LOW
    
    def test_generate_template(self, annotator):
        """测试生成模板"""
        template = annotator.generate_template(InfoType.CONCLUSION)
        
        assert "[结论]" in template
        assert "[置信度]" in template
        assert "[来源]" in template
    
    def test_validate_annotation(self, annotator):
        """测试标注验证"""
        annotation = annotator.annotate(
            content="测试内容",
            info_type=InfoType.CONCLUSION,
            source="测试来源"
        )
        
        result = annotator.validate_annotation(annotation)
        
        assert result['valid'] is True
        assert len(result['issues']) == 0
    
    def test_to_markdown(self, annotator):
        """测试Markdown格式输出"""
        annotation = annotator.annotate(
            content="Python使用Timsort算法",
            info_type=InfoType.CONCLUSION,
            confidence=ConfidenceLevel.HIGH,
            source="Python官方文档",
            suggestion="可直接使用"
        )
        
        markdown = annotation.to_markdown()
        
        assert "[结论]" in markdown
        assert "Python使用Timsort算法" in markdown
        assert "高" in markdown
