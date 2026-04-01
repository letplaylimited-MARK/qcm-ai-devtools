"""
AI-Skill-System 桥接层

实现 ai-skill-system 与 QCM-AI-DevTools 的完美互操作
"""

import yaml
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime

from qcm_tools.handoff import HandoffPackage, HandoffType, SkillID
from qcm_tools.quality import QualityReport
from qcm_tools.config import ProjectConfig
from qcm_tools.confidence import ConfidenceAnnotation


class AISkillSystemBridge:
    """
    ai-skill-system 与 QCM-AI-DevTools 的桥接层

    职责：
    1. YAML ↔ Python 对象转换
    2. 数据格式验证
    3. 版本兼容性处理
    4. Prompt 策略加载

    Example:
        >>> from qcm_tools.bridge import AISkillSystemBridge
        >>> bridge = AISkillSystemBridge()
        >>>
        >>> # 从 ai-skill-system 导入
        >>> handoff = bridge.import_from_skill_system("handoff.yaml")
        >>>
        >>> # 导出到 ai-skill-system
        >>> yaml_str = bridge.export_to_skill_system(quality_report)
    """

    SUPPORTED_SCHEMA_VERSIONS = ["1.0", "1.1"]

    def __init__(self, strict_mode: bool = True):
        """
        初始化桥接层

        Args:
            strict_mode: 是否严格验证格式（默认 True）
        """
        self.strict_mode = strict_mode

    # ============================================================
    # 导入方法（ai-skill-system → QCM-AI-DevTools）
    # ============================================================

    def import_from_skill_system(
        self,
        source: str,
        format: str = "yaml"
    ) -> HandoffPackage:
        """
        从 ai-skill-system 导入交接包

        Args:
            source: YAML/JSON 字符串或文件路径
            format: 格式类型 ('yaml' 或 'json')

        Returns:
            HandoffPackage 对象

        Example:
            >>> handoff = bridge.import_from_skill_system('''
            ... schema_version: "1.1"
            ... from_skill: "skill-00"
            ... to_skill: "skill-04"
            ... payload:
            ...   intent_type: "build_custom"
            ... ''')
        """
        # 判断是文件路径还是内容
        if self._is_file_path(source):
            data = self._load_from_file(source, format)
        else:
            data = self._parse_content(source, format)

        # 验证 schema 版本
        self._validate_schema_version(data)

        # 转换为 HandoffPackage
        return self._convert_to_handoff(data)

    def import_intent_from_yaml(self, yaml_str: str) -> Dict[str, Any]:
        """
        从 YAML 导入意图分析结果

        Args:
            yaml_str: YAML 格式的意图分析

        Returns:
            意图字典

        Example:
            >>> intent = bridge.import_intent_from_yaml('''
            ... intent_type: "build_custom"
            ... confidence: 0.95
            ... recommended_skill: "skill-04"
            ... ''')
        """
        data = yaml.safe_load(yaml_str)
        return {
            'intent_type': data.get('intent_type'),
            'confidence': data.get('confidence'),
            'recommended_skill': data.get('recommended_skill'),
            'keywords': data.get('keywords', []),
            'project_summary': data.get('project_summary', {})
        }

    def import_tech_stack_from_yaml(self, yaml_str: str) -> List[str]:
        """
        从 YAML 导入技术栈信息

        Args:
            yaml_str: YAML 格式的技术栈

        Returns:
            技术栈列表

        Example:
            >>> stack = bridge.import_tech_stack_from_yaml('''
            ... tech_stack:
            ...   - FastAPI
            ...   - SQLAlchemy
            ...   - PostgreSQL
            ... ''')
        """
        data = yaml.safe_load(yaml_str)
        return data.get('tech_stack', [])

    # ============================================================
    # 导出方法（QCM-AI-DevTools → ai-skill-system）
    # ============================================================

    def export_to_skill_system(
        self,
        obj: Any,
        format: str = "yaml"
    ) -> str:
        """
        导出到 ai-skill-system

        Args:
            obj: Python 对象（HandoffPackage, QualityReport, etc.）
            format: 格式类型 ('yaml' 或 'json')

        Returns:
            YAML/JSON 字符串

        Example:
            >>> yaml_str = bridge.export_to_skill_system(quality_report)
            >>> print(yaml_str)
        """
        if isinstance(obj, HandoffPackage):
            return self._export_handoff(obj, format)
        elif isinstance(obj, QualityReport):
            return self._export_quality_report(obj, format)
        elif isinstance(obj, ProjectConfig):
            return self._export_project_config(obj, format)
        elif isinstance(obj, ConfidenceAnnotation):
            return self._export_confidence_annotation(obj, format)
        else:
            raise ValueError(f"不支持的对象类型: {type(obj)}")

    def export_quality_report_to_yaml(
        self,
        report: QualityReport,
        include_details: bool = True
    ) -> str:
        """
        将质量报告导出为 ai-skill-system 可读的 YAML

        Args:
            report: QualityReport 对象
            include_details: 是否包含详细检查项

        Returns:
            YAML 字符串

        Example:
            >>> yaml_str = bridge.export_quality_report_to_yaml(report)
            >>> # 发送给 ai-skill-system 的 Skill-05 Validator
        """
        data = {
            'schema_version': '1.1',
            'exported_at': datetime.now().isoformat(),
            'source': 'qcm-ai-devtools',
            'quality_report': {
                'overall_score': report.overall_score,
                'quality_level': report.quality_level.value if hasattr(report, 'quality_level') else 'unknown',
                'total_checks': len(report.indicators),
                'passed_checks': sum(1 for i in report.indicators if i.passed),
                'failed_checks': sum(1 for i in report.indicators if not i.passed),
            }
        }

        if include_details:
            data['quality_report']['indicators'] = [
                {
                    'name': ind.name,
                    'passed': ind.passed,
                    'score': ind.score,
                    'message': ind.message,
                    'details': ind.details
                }
                for ind in report.indicators
            ]

            if hasattr(report, 'recommendations'):
                data['quality_report']['recommendations'] = report.recommendations

        return yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False)

    def export_project_config_to_yaml(self, config: ProjectConfig) -> str:
        """
        将项目配置导出为 ai-skill-system 可读的 YAML

        Args:
            config: ProjectConfig 对象

        Returns:
            YAML 字符串
        """
        data = {
            'schema_version': '1.1',
            'exported_at': datetime.now().isoformat(),
            'source': 'qcm-ai-devtools',
            'project_config': {
                'project_name': config.project_name,
                'project_type': config.project_type.value if hasattr(config.project_type, 'value') else str(config.project_type),
                'description': config.description,
                'tech_stack': [t.value if hasattr(t, 'value') else str(t) for t in config.tech_stack],
                'scale': config.scale.value if hasattr(config.scale, 'value') else str(config.scale),
                'roles': [r.value if hasattr(r, 'value') else str(r) for r in config.roles],
            }
        }

        if hasattr(config, 'features'):
            data['project_config']['features'] = config.features

        if hasattr(config, 'quality_standards'):
            data['project_config']['quality_standards'] = {
                k: v for k, v in config.quality_standards.items()
            }

        return yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False)

    # ============================================================
    # 双向转换核心方法
    # ============================================================

    def _convert_to_handoff(self, data: Dict[str, Any]) -> HandoffPackage:
        """将字典转换为 HandoffPackage 对象"""
        from qcm_tools.handoff.models import HandoffPackage

        # 提取 confidence_score 和 session_id 并放入 payload
        payload = data.get('payload', {})
        
        # 将额外的字段放入 payload
        if 'confidence_score' in data and 'confidence_score' not in payload:
            payload['confidence_score'] = data['confidence_score']
        if 'session_id' in data and 'session_id' not in payload:
            payload['session_id'] = data['session_id']

        return HandoffPackage(
            schema_version=data.get('schema_version', '1.1'),
            from_skill=data.get('from_skill', ''),
            to_skill=data.get('to_skill', ''),
            handoff_type=data.get('handoff_type', 'HP-A'),
            payload=payload
        )

    def _export_handoff(self, handoff: HandoffPackage, format: str) -> str:
        """导出 HandoffPackage"""
        if format == 'yaml':
            return handoff.to_yaml()
        else:
            return json.dumps(handoff.to_dict(), ensure_ascii=False, indent=2)

    def _export_quality_report(self, report: QualityReport, format: str) -> str:
        """导出 QualityReport"""
        return self.export_quality_report_to_yaml(report)

    def _export_project_config(self, config: ProjectConfig, format: str) -> str:
        """导出 ProjectConfig"""
        return self.export_project_config_to_yaml(config)

    def _export_confidence_annotation(
        self,
        annotation: ConfidenceAnnotation,
        format: str
    ) -> str:
        """导出 ConfidenceAnnotation"""
        data = {
            'schema_version': '1.1',
            'exported_at': datetime.now().isoformat(),
            'source': 'qcm-ai-devtools',
            'confidence_annotation': {
                'overall_confidence': annotation.overall_confidence.value if hasattr(annotation.overall_confidence, 'value') else str(annotation.overall_confidence),
                'annotations': [
                    {
                        'text': ann.text,
                        'confidence': ann.confidence.value if hasattr(ann.confidence, 'value') else str(ann.confidence),
                        'type': ann.type.value if hasattr(ann.type, 'value') else str(ann.type),
                        'reason': ann.reason
                    }
                    for ann in annotation.annotations
                ]
            }
        }

        if format == 'yaml':
            return yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False)
        else:
            return json.dumps(data, ensure_ascii=False, indent=2)

    # ============================================================
    # 辅助方法
    # ============================================================

    def _is_file_path(self, source: str) -> bool:
        """判断是否为文件路径"""
        return Path(source).exists()

    def _load_from_file(self, file_path: str, format: str) -> Dict[str, Any]:
        """从文件加载数据"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return self._parse_content(content, format)

    def _parse_content(self, content: str, format: str) -> Dict[str, Any]:
        """解析内容"""
        if format == 'yaml':
            return yaml.safe_load(content)
        elif format == 'json':
            return json.loads(content)
        else:
            raise ValueError(f"不支持的格式: {format}")

    def _validate_schema_version(self, data: Dict[str, Any]) -> None:
        """验证 schema 版本"""
        version = data.get('schema_version', '1.0')

        if version not in self.SUPPORTED_SCHEMA_VERSIONS:
            if self.strict_mode:
                raise ValueError(
                    f"不支持的 schema 版本: {version}. "
                    f"支持的版本: {self.SUPPORTED_SCHEMA_VERSIONS}"
                )
            else:
                # 非严格模式下，使用最新版本
                pass

    # ============================================================
    # Prompt 策略加载
    # ============================================================

    def load_prompt_from_skill_system(
        self,
        skill_id: str,
        prompt_dir: Optional[str] = None
    ) -> str:
        """
        从 ai-skill-system 加载 Prompt 策略

        Args:
            skill_id: Skill ID (e.g., "skill-01", "skill-03")
            prompt_dir: Prompt 文件目录（可选）

        Returns:
            Prompt 字符串

        Example:
            >>> prompt = bridge.load_prompt_from_skill_system("skill-01")
            >>> # 使用该 Prompt 调用 OpenAI
        """
        if prompt_dir is None:
            # 默认从 ai-skill-system 项目加载
            prompt_dir = "/workspace/ai-skill-system/prompts"

        prompt_file = Path(prompt_dir) / f"{skill_id}.md"

        if prompt_file.exists():
            return prompt_file.read_text(encoding='utf-8')
        else:
            # 返回默认 Prompt
            return self._get_default_prompt(skill_id)

    def _get_default_prompt(self, skill_id: str) -> str:
        """获取默认 Prompt"""
        default_prompts = {
            'skill-00': """你是 Navigator（导航官），负责识别用户意图并路由到合适的 Skill。
请分析用户需求，确定：
1. intent_type: 意图类型
2. confidence: 置信度（0-1）
3. recommended_skill: 推荐的 Skill
""",
            'skill-01': """你是超级提示词工程师，负责优化用户的提示词。
请优化用户的需求描述，使其更加清晰、具体、可执行。
""",
            'skill-03': """你是 Scout（开源侦察官），负责技术选型评估。
请基于七维度评估框架分析开源方案：
1. 功能性 (30%)
2. 易用性 (20%)
3. 性能 (15%)
4. 可维护性 (10%)
5. 社区活跃度 (10%)
6. 兼容性 (10%)
7. 文档 (5%)
""",
            'skill-04': """你是 Planner（执行规划官），负责任务分解和规划。
请将任务分解为可执行的步骤：
1. Phase 阶段
2. Task 任务
3. Step 步骤
""",
            'skill-05': """你是 Validator（测试验收工程师），负责质量验收。
请基于五维度验证框架评估：
1. 功能性 (40%)
2. 文档完整性 (25%)
3. 可执行性 (20%)
4. 接口规范 (10%)
5. 安全性 (5%)
"""
        }
        return default_prompts.get(skill_id, "你是 AI 助手，请帮助用户完成任务。")


class ExecutionFeedback:
    """
    执行结果反馈

    将代码执行结果反馈给 ai-skill-system
    形成闭环：AI 决策 → 代码执行 → 结果反馈 → AI 优化
    """

    def __init__(self, bridge: AISkillSystemBridge):
        self.bridge = bridge

    def create_feedback_handoff(
        self,
        execution_result: Dict[str, Any],
        from_skill: str = "qcm-tools",
        to_skill: str = "skill-05"
    ) -> HandoffPackage:
        """
        创建反馈交接包

        Args:
            execution_result: 执行结果
            from_skill: 来源
            to_skill: 目标 Skill

        Returns:
            HandoffPackage 对象

        Example:
            >>> feedback = ExecutionFeedback(bridge)
            >>> handoff = feedback.create_feedback_handoff({
            ...     'status': 'success',
            ...     'output_path': './my-project',
            ...     'quality_score': 85
            ... })
        """
        from qcm_tools.handoff.models import create_handoff

        return create_handoff(
            schema_version="1.1",
            from_skill=from_skill,
            to_skill=to_skill,
            handoff_type="HP-F",  # Feedback
            payload={
                'execution_status': execution_result.get('status'),
                'output': execution_result.get('output_path'),
                'quality_score': execution_result.get('quality_score'),
                'errors': execution_result.get('errors', []),
                'warnings': execution_result.get('warnings', []),
                'suggestions': execution_result.get('suggestions', []),
                'timestamp': datetime.now().isoformat()
            }
        )

    def create_error_handoff(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None
    ) -> HandoffPackage:
        """
        创建错误交接包

        Args:
            error: 异常对象
            context: 上下文信息

        Returns:
            HandoffPackage 对象
        """
        from qcm_tools.handoff.models import create_handoff

        return create_handoff(
            schema_version="1.1",
            from_skill="qcm-tools",
            to_skill="skill-00",  # 返回给 Navigator 重新路由
            handoff_type="HP-F",
            payload={
                'execution_status': 'failed',
                'error_type': type(error).__name__,
                'error_message': str(error),
                'context': context or {},
                'timestamp': datetime.now().isoformat()
            }
        )


# 便捷函数
def create_bridge(strict_mode: bool = True) -> AISkillSystemBridge:
    """创建桥接器"""
    return AISkillSystemBridge(strict_mode=strict_mode)


def import_handoff(source: str, format: str = "yaml") -> HandoffPackage:
    """导入交接包（便捷函数）"""
    bridge = AISkillSystemBridge()
    return bridge.import_from_skill_system(source, format)


def export_to_yaml(obj: Any) -> str:
    """导出为 YAML（便捷函数）"""
    bridge = AISkillSystemBridge()
    return bridge.export_to_skill_system(obj, format="yaml")
