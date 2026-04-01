"""
置信度标注器实现

提供AI输出置信度自动分析、标注和管理功能
"""

import re
from typing import List, Dict, Optional, Tuple
from qcm_tools.confidence.models import ConfidenceAnnotation
from qcm_tools.shared.enums import InfoType, ConfidenceLevel


class ConfidenceAnnotator:
    """
    置信度标注器
    
    自动分析内容并生成置信度标注,支持批量处理和标注提取
    
    Example:
        >>> from qcm_tools.confidence import ConfidenceAnnotator
        >>> 
        >>> annotator = ConfidenceAnnotator()
        >>> 
        >>> # 方式1: 手动标注
        >>> annotation = annotator.annotate(
        ...     content="Python的list.sort()使用Timsort算法",
        ...     info_type=InfoType.CONCLUSION,
        ...     source="Python官方文档"
        ... )
        >>> 
        >>> # 方式2: 自动分析
        >>> annotation = annotator.auto_annotate(
        ...     "根据官方文档,Python使用Timsort算法进行排序"
        ... )
        >>> 
        >>> # 方式3: 批量处理
        >>> contents = ["结论1", "结论2", "结论3"]
        >>> annotations = annotator.batch_annotate(contents)
    """
    
    # 信息类型关键词模式
    INFO_TYPE_PATTERNS = {
        InfoType.CONCLUSION: [
            r'(因此|所以|综上所述|总结|结论是|可以得出)',
            r'(证明了|表明了|显示了|证实了)',
            r'(研究结果|实验结果|分析结果)',
            r'(发现|得出|推断出)',
        ],
        InfoType.DATA: [
            r'(\d+\.?\d*%|\d+个|\d+次|\d+项)',
            r'(统计|数据|调查|研究显示)',
            r'(达到|超过|低于|平均)',
            r'(增长|下降|提升|减少)\s*\d+',
        ],
        InfoType.CITATION: [
            r'(根据|依据|按照|引用)',
            r'(文献|论文|研究|报告)',
            r'(\w+\s+et\s+al\.|等人的研究)',
            r'(官方文档|标准|规范)',
        ],
        InfoType.INFERENCE: [
            r'(推测|估计|可能|或许|也许)',
            r'(应该|可能是|大概是)',
            r'(预期|预测|推断)',
            r'(假设|如果|假如)',
        ]
    }
    
    # 置信度判断模式
    CONFIDENCE_PATTERNS = {
        ConfidenceLevel.HIGH: [
            r'(官方|权威|标准|规范|文献|论文)',
            r'(证实|证明|验证|实验结果|数据表明)',
            r'(确定的|明确的|毫无疑问)',
        ],
        ConfidenceLevel.LOW: [
            r'(可能|或许|也许|大概|猜测)',
            r'(不确定|推测|估计|预期)',
            r'(需要验证|待确认|可能有误)',
        ]
    }
    
    # 来源关键词映射
    SOURCE_KEYWORDS = {
        '官方文档': ['官方', '官方文档', 'documentation', 'official'],
        '学术论文': ['论文', '研究', 'paper', 'research', 'study'],
        '技术博客': ['博客', 'blog', '文章', 'article'],
        '个人经验': ['经验', '个人', '实践', '实践证明'],
        '推理结论': ['推测', '推断', '分析', '判断'],
    }
    
    # 标注模板
    ANNOTATION_TEMPLATES = {
        InfoType.CONCLUSION: {
            'high': {
                'suggestion': '可直接使用,来源可靠',
                'template': '[结论] {content}\n[置信度] 高(基于{source_type})\n[来源] {source}\n[建议] 可直接使用'
            },
            'medium': {
                'suggestion': '建议进一步验证',
                'template': '[结论] {content}\n[置信度] 中(基于推理)\n[来源] {source}\n[建议] 建议进一步验证'
            },
            'low': {
                'suggestion': '需要谨慎使用,务必验证',
                'template': '[结论] {content}\n[置信度] 低(可能不准确)\n[来源] {source}\n[建议] 需要谨慎使用,务必验证'
            }
        },
        InfoType.DATA: {
            'high': {
                'suggestion': '数据来源可靠,可直接引用',
                'template': '[数据] {content}\n[置信度] 高(基于可靠来源)\n[来源] {source}\n[建议] 数据来源可靠,可直接引用'
            },
            'medium': {
                'suggestion': '建议核实数据来源',
                'template': '[数据] {content}\n[置信度] 中(数据来源一般)\n[来源] {source}\n[建议] 建议核实数据来源'
            },
            'low': {
                'suggestion': '数据准确性存疑,务必验证',
                'template': '[数据] {content}\n[置信度] 低(数据可能不准确)\n[来源] {source}\n[建议] 数据准确性存疑,务必验证'
            }
        },
        InfoType.CITATION: {
            'high': {
                'suggestion': '引用来源权威,可信度高',
                'template': '[引用] {content}\n[置信度] 高(权威来源)\n[来源] {source}\n[建议] 引用来源权威,可信度高'
            },
            'medium': {
                'suggestion': '建议查阅原文确认',
                'template': '[引用] {content}\n[置信度] 中(一般来源)\n[来源] {source}\n[建议] 建议查阅原文确认'
            },
            'low': {
                'suggestion': '引用来源不明确,需要核实',
                'template': '[引用] {content}\n[置信度] 低(来源不明)\n[来源] {source}\n[建议] 引用来源不明确,需要核实'
            }
        },
        InfoType.INFERENCE: {
            'high': {
                'suggestion': '推理逻辑清晰,可信度较高',
                'template': '[推断] {content}\n[置信度] 高(基于合理推理)\n[来源] {source}\n[建议] 推理逻辑清晰,可信度较高'
            },
            'medium': {
                'suggestion': '建议通过实验或数据验证',
                'template': '[推断] {content}\n[置信度] 中(基于一般推理)\n[来源] {source}\n[建议] 建议通过实验或数据验证'
            },
            'low': {
                'suggestion': '推测性较强,需要大量验证',
                'template': '[推断] {content}\n[置信度] 低(推测性较强)\n[来源] {source}\n[建议] 推测性较强,需要大量验证'
            }
        }
    }
    
    def __init__(self):
        """初始化置信度标注器"""
        pass
    
    def annotate(
        self,
        content: str,
        info_type: InfoType,
        confidence: ConfidenceLevel = None,
        source: str = None,
        suggestion: str = None
    ) -> ConfidenceAnnotation:
        """
        创建置信度标注
        
        Args:
            content: 待标注内容
            info_type: 信息类型
            confidence: 置信度级别(可选,自动推断)
            source: 信息来源(可选,自动推断)
            suggestion: 使用建议(可选,自动生成)
            
        Returns:
            置信度标注对象
            
        Example:
            >>> annotator = ConfidenceAnnotator()
            >>> annotation = annotator.annotate(
            ...     content="Python使用Timsort算法",
            ...     info_type=InfoType.CONCLUSION,
            ...     source="Python官方文档"
            ... )
        """
        # 自动推断置信度
        if confidence is None:
            confidence = self._infer_confidence(content, source)
        
        # 自动推断来源
        if source is None:
            source = self._infer_source(content)
        
        # 自动生成建议
        if suggestion is None:
            suggestion = self._generate_suggestion(info_type, confidence, source)
        
        annotation = ConfidenceAnnotation(
            info_type=info_type,
            confidence=confidence,
            source=source,
            suggestion=suggestion,
            content=content
        )
        
        # 验证标注
        issues = annotation.validate()
        if issues:
            # 如果有验证问题,调整标注
            if "来源不能为空" in issues:
                annotation.source = "未知来源"
            if "建议不能为空" in issues:
                annotation.suggestion = "请核实信息"
        
        return annotation
    
    def auto_annotate(self, content: str) -> ConfidenceAnnotation:
        """
        自动分析内容并生成标注
        
        Args:
            content: 待分析内容
            
        Returns:
            自动生成的置信度标注
            
        Example:
            >>> annotator = ConfidenceAnnotator()
            >>> annotation = annotator.auto_annotate(
            ...     "根据官方文档,Python使用Timsort算法进行排序"
            ... )
        """
        # 推断信息类型
        info_type = self._infer_info_type(content)
        
        # 推断置信度
        confidence = self._infer_confidence(content)
        
        # 推断来源
        source = self._infer_source(content)
        
        # 生成建议
        suggestion = self._generate_suggestion(info_type, confidence, source)
        
        return self.annotate(
            content=content,
            info_type=info_type,
            confidence=confidence,
            source=source,
            suggestion=suggestion
        )
    
    def batch_annotate(
        self,
        contents: List[str],
        auto: bool = True
    ) -> List[ConfidenceAnnotation]:
        """
        批量标注处理
        
        Args:
            contents: 内容列表
            auto: 是否自动分析(默认True)
            
        Returns:
            标注列表
            
        Example:
            >>> annotator = ConfidenceAnnotator()
            >>> contents = [
            ...     "Python使用Timsort算法",
            ...     "可能有50%的性能提升",
            ...     "根据研究表明..."
            ... ]
            >>> annotations = annotator.batch_annotate(contents)
        """
        annotations = []
        
        for content in contents:
            if auto:
                annotation = self.auto_annotate(content)
            else:
                # 使用默认参数
                annotation = self.annotate(
                    content=content,
                    info_type=InfoType.CONCLUSION
                )
            annotations.append(annotation)
        
        return annotations
    
    def extract_annotations(self, text: str) -> List[ConfidenceAnnotation]:
        """
        从文本中提取现有标注
        
        Args:
            text: 包含标注的文本
            
        Returns:
            提取的标注列表
            
        Example:
            >>> text = '''
            ... [结论] Python使用Timsort算法
            ... [置信度] 高(基于文献)
            ... [来源] Python官方文档
            ... [建议] 可直接使用
            ... '''
            >>> annotations = annotator.extract_annotations(text)
        """
        annotations = []
        
        # 标注块模式
        pattern = r'\[(结论|数据|引用|推断)\]\s*(.+?)\n\[置信度\]\s*(.+?)\n\[来源\]\s*(.+?)\n\[建议\]\s*(.+?)(?=\n\[|\n\n|\Z)'
        
        matches = re.finditer(pattern, text, re.DOTALL)
        
        for match in matches:
            info_type_str = match.group(1)
            content = match.group(2).strip()
            confidence_str = match.group(3).strip()
            source = match.group(4).strip()
            suggestion = match.group(5).strip()
            
            # 解析信息类型
            info_type_map = {
                '结论': InfoType.CONCLUSION,
                '数据': InfoType.DATA,
                '引用': InfoType.CITATION,
                '推断': InfoType.INFERENCE
            }
            info_type = info_type_map.get(info_type_str)
            
            # 解析置信度
            confidence_map = {
                '高': ConfidenceLevel.HIGH,
                '中': ConfidenceLevel.MEDIUM,
                '低': ConfidenceLevel.LOW
            }
            confidence = None
            for key, value in confidence_map.items():
                if key in confidence_str:
                    confidence = value
                    break
            
            if info_type and confidence:
                annotation = ConfidenceAnnotation(
                    info_type=info_type,
                    confidence=confidence,
                    source=source,
                    suggestion=suggestion,
                    content=content
                )
                annotations.append(annotation)
        
        return annotations
    
    def generate_template(self, info_type: InfoType) -> str:
        """
        生成标注模板
        
        Args:
            info_type: 信息类型
            
        Returns:
            标注模板字符串
            
        Example:
            >>> template = annotator.generate_template(InfoType.CONCLUSION)
            >>> print(template)
            [结论] {内容}
            [置信度] {高/中/低}
            [来源] {来源信息}
            [建议] {使用建议}
        """
        templates = {
            InfoType.CONCLUSION: """[结论] {输入结论内容}
[置信度] 高(基于文献) / 中(基于推理) / 低(可能不准确)
[来源] {输入信息来源}
[建议] 可直接使用 / 建议验证 / 需要核实""",
            
            InfoType.DATA: """[数据] {输入数据内容}
[置信度] 高(基于可靠来源) / 中(数据来源一般) / 低(数据可能不准确)
[来源] {输入数据来源}
[建议] 可直接引用 / 建议核实 / 需要验证""",
            
            InfoType.CITATION: """[引用] {输入引用内容}
[置信度] 高(权威来源) / 中(一般来源) / 低(来源不明)
[来源] {输入引用来源}
[建议] 可信度高 / 建议查阅原文 / 需要核实""",
            
            InfoType.INFERENCE: """[推断] {输入推断内容}
[置信度] 高(基于合理推理) / 中(基于一般推理) / 低(推测性较强)
[来源] {输入推断依据}
[建议] 可信度较高 / 建议验证 / 需要大量验证"""
        }
        
        return templates.get(info_type, "未知信息类型")
    
    def suggest_confidence(self, content: str, source: str = None) -> Tuple[ConfidenceLevel, str]:
        """
        建议置信度级别
        
        Args:
            content: 内容
            source: 来源(可选)
            
        Returns:
            (置信度级别, 原因说明)
            
        Example:
            >>> confidence, reason = annotator.suggest_confidence(
            ...     "根据官方文档...",
            ...     "Python官方文档"
            ... )
            >>> print(confidence, reason)
            ConfidenceLevel.HIGH, "包含权威来源关键词"
        """
        # 优先检查低置信度模式（不确定性关键词）
        for pattern in self.CONFIDENCE_PATTERNS[ConfidenceLevel.LOW]:
            if re.search(pattern, content, re.IGNORECASE):
                return ConfidenceLevel.LOW, "包含不确定性关键词"
        
        # 再检查高置信度模式
        for pattern in self.CONFIDENCE_PATTERNS[ConfidenceLevel.HIGH]:
            if re.search(pattern, content, re.IGNORECASE):
                return ConfidenceLevel.HIGH, "包含权威来源关键词"
        
        # 如果有明确的来源
        if source:
            source_lower = source.lower()
            for source_type, keywords in self.SOURCE_KEYWORDS.items():
                if any(keyword in source_lower for keyword in keywords):
                    if source_type in ['官方文档', '学术论文']:
                        return ConfidenceLevel.HIGH, f"来源类型为{source_type}"
                    elif source_type == '个人经验':
                        return ConfidenceLevel.MEDIUM, f"来源类型为{source_type}"
        
        # 默认中置信度
        return ConfidenceLevel.MEDIUM, "基于一般推理"
    
    def validate_annotation(self, annotation: ConfidenceAnnotation) -> Dict:
        """
        验证标注的完整性和一致性
        
        Args:
            annotation: 待验证的标注
            
        Returns:
            验证结果字典
            
        Example:
            >>> result = annotator.validate_annotation(annotation)
            >>> print(result['valid'], result['issues'])
        """
        result = {
            'valid': True,
            'issues': [],
            'warnings': [],
            'suggestions': []
        }
        
        # 检查必填字段
        issues = annotation.validate()
        if issues:
            result['valid'] = False
            result['issues'].extend(issues)
        
        # 检查一致性
        if annotation.confidence == ConfidenceLevel.HIGH:
            if '文献' not in annotation.source and '官方' not in annotation.source:
                result['warnings'].append("高置信度建议基于文献或官方来源")
        
        if annotation.confidence == ConfidenceLevel.LOW:
            if '验证' not in annotation.suggestion and '核实' not in annotation.suggestion:
                result['suggestions'].append("低置信度建议包含验证提示")
        
        # 检查内容完整性
        if not annotation.content or len(annotation.content.strip()) < 5:
            result['warnings'].append("标注内容过短,建议补充详细信息")
        
        return result
    
    # ===== 内部方法 =====
    
    def _infer_info_type(self, content: str) -> InfoType:
        """推断信息类型"""
        scores = {}
        
        for info_type, patterns in self.INFO_TYPE_PATTERNS.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                score += len(matches)
            scores[info_type] = score
        
        # 选择得分最高的类型
        if all(score == 0 for score in scores.values()):
            return InfoType.CONCLUSION  # 默认
        
        return max(scores, key=scores.get)
    
    def _infer_confidence(self, content: str, source: str = None) -> ConfidenceLevel:
        """推断置信度"""
        confidence, _ = self.suggest_confidence(content, source)
        return confidence
    
    def _infer_source(self, content: str) -> str:
        """推断来源"""
        content_lower = content.lower()
        
        for source_type, keywords in self.SOURCE_KEYWORDS.items():
            if any(keyword in content_lower for keyword in keywords):
                return source_type
        
        return "未明确来源"
    
    def _generate_suggestion(
        self,
        info_type: InfoType,
        confidence: ConfidenceLevel,
        source: str
    ) -> str:
        """生成建议"""
        confidence_key = {
            ConfidenceLevel.HIGH: 'high',
            ConfidenceLevel.MEDIUM: 'medium',
            ConfidenceLevel.LOW: 'low'
        }
        
        templates = self.ANNOTATION_TEMPLATES.get(info_type, {})
        template = templates.get(confidence_key[confidence], {})
        
        return template.get('suggestion', '请根据实际情况判断')


__all__ = ['ConfidenceAnnotator']
