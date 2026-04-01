"""
交接包数据模型

实现与 ai-skill-system 接口契约兼容的交接包结构
schema v1.1 规范

支持 Pydantic v2 进行数据验证
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import date
from enum import Enum
import yaml
import json

# Pydantic 支持
try:
    from pydantic import BaseModel, Field, field_validator
    from pydantic import ConfigDict
    HAS_PYDANTIC = True
except ImportError:
    HAS_PYDANTIC = False
    BaseModel = object  # 占位符


class SkillID(Enum):
    """Skill 标识符"""
    SKILL_00 = "skill-00"  # Navigator
    SKILL_01 = "skill-01"  # 超级提示词工程师
    SKILL_02 = "skill-02"  # SOP 工程师
    SKILL_03 = "skill-03"  # Scout 开源侦察官
    SKILL_04 = "skill-04"  # Planner 执行规划官
    SKILL_05 = "skill-05"  # Validator 测试验收工程师
    USER = "user"          # 用户
    RELEASE = "release"    # 发布决策


class HandoffType(Enum):
    """交接包类型（基于 ai-skill-system 接口契约）"""
    HP_A = "HP-A"  # 提示词优化包 (S01 → S02)
    HP_B = "HP-B"  # 技术选型包 (S03 → S02)
    HP_C = "HP-C"  # 工程包交付 (S02 → S05)
    HP_D = "HP-D"  # 路由推荐包 (S00 → 任意)
    HP_E = "HP-E"  # 操作手册 (S04 → 用户)
    HP_F = "HP-F"  # 验收报告 (S05 → 发布)


@dataclass
class SelfReview:
    """
    自我审查（v1.1 新增）
    
    执行前假设、潜在失败点和 S05 预扣分预测
    """
    assumptions: List[str] = field(default_factory=list)
    potential_failures: List[str] = field(default_factory=list)
    predicted_deduction_by_s05: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'assumptions': self.assumptions,
            'potential_failures': self.potential_failures,
            'predicted_deduction_by_s05': self.predicted_deduction_by_s05
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SelfReview':
        return cls(
            assumptions=data.get('assumptions', []),
            potential_failures=data.get('potential_failures', []),
            predicted_deduction_by_s05=data.get('predicted_deduction_by_s05', "")
        )


@dataclass
class DownstreamNotes:
    """
    下游注意事项（v1.1 新增）
    
    对下游 Skill 的注意事项和必须验证项
    """
    to_skill: str = ""
    cautions: List[str] = field(default_factory=list)
    required_verification: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'to_skill': self.to_skill,
            'cautions': self.cautions,
            'required_verification': self.required_verification
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DownstreamNotes':
        return cls(
            to_skill=data.get('to_skill', ""),
            cautions=data.get('cautions', []),
            required_verification=data.get('required_verification', [])
        )


@dataclass
class HandoffPackage:
    """
    标准化交接包
    
    兼容 ai-skill-system schema v1.1
    
    基于 YAML 格式，用于 Skill 之间的上下文传递。
    每个交接包包含完整的上下文信息，确保信息无损传递。
    
    Example:
        >>> # 创建路由推荐包
        >>> handoff = HandoffPackage(
        ...     from_skill=SkillID.SKILL_00,
        ...     to_skill=SkillID.SKILL_03,
        ...     payload={
        ...         'intent_type': 'find_open_source',
        ...         'confidence_score': 0.85,
        ...         'project_summary': '开发一个情感分析系统'
        ...     }
        ... )
        >>> 
        >>> # 导出为 YAML
        >>> yaml_str = handoff.to_yaml()
        >>> 
        >>> # 从 YAML 导入
        >>> restored = HandoffPackage.from_yaml(yaml_str)
    """
    
    # 必填字段
    schema_version: str = "1.1"
    from_skill: str = ""  # 使用字符串以支持枚举和原始字符串
    to_skill: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    user_action: str = ""
    created_at: str = field(default_factory=lambda: date.today().isoformat())
    
    # 可选字段（v1.1 新增）
    handoff_type: str = ""  # HP-A, HP-B, HP-C, HP-D, HP-E, HP-F
    self_review: Optional[Dict[str, Any]] = None
    downstream_notes: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """初始化后处理"""
        # 如果传入的是枚举，转换为字符串
        if isinstance(self.from_skill, SkillID):
            self.from_skill = self.from_skill.value
        if isinstance(self.to_skill, SkillID):
            self.to_skill = self.to_skill.value
        if isinstance(self.handoff_type, HandoffType):
            self.handoff_type = self.handoff_type.value
        
        # 处理日期
        if isinstance(self.created_at, date):
            self.created_at = self.created_at.isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        
        Returns:
            字典格式的交接包数据
        """
        result = {
            'handoff': {
                'schema_version': self.schema_version,
                'from_skill': self.from_skill,
                'to_skill': self.to_skill,
                'payload': self.payload,
                'user_action': self.user_action,
                'created_at': self.created_at
            }
        }
        
        # 添加可选字段
        if self.handoff_type:
            result['handoff']['handoff_type'] = self.handoff_type
        
        if self.self_review:
            result['handoff']['self_review'] = self.self_review
        
        if self.downstream_notes:
            result['handoff']['downstream_notes'] = self.downstream_notes
        
        return result
    
    def to_yaml(self) -> str:
        """
        导出为 YAML 格式
        
        Returns:
            YAML 格式的交接包字符串
            
        Example:
            >>> handoff = HandoffPackage(
            ...     from_skill="skill-00",
            ...     to_skill="skill-03"
            ... )
            >>> print(handoff.to_yaml())
            handoff:
              schema_version: '1.1'
              from_skill: skill-00
              ...
        """
        return yaml.dump(
            self.to_dict(),
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False
        )
    
    def to_json(self) -> str:
        """
        导出为 JSON 格式
        
        Returns:
            JSON 格式的交接包字符串
        """
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HandoffPackage':
        """
        从字典创建交接包
        
        Args:
            data: 字典数据（支持嵌套 handoff 键或平铺格式）
            
        Returns:
            HandoffPackage 实例
        """
        # 支持两种格式：嵌套 {'handoff': {...}} 或平铺 {...}
        if 'handoff' in data:
            data = data['handoff']
        
        return cls(
            schema_version=data.get('schema_version', '1.1'),
            from_skill=data.get('from_skill', ''),
            to_skill=data.get('to_skill', ''),
            payload=data.get('payload', {}),
            user_action=data.get('user_action', ''),
            created_at=data.get('created_at', date.today().isoformat()),
            handoff_type=data.get('handoff_type', ''),
            self_review=data.get('self_review'),
            downstream_notes=data.get('downstream_notes')
        )
    
    @classmethod
    def from_yaml(cls, yaml_str: str) -> 'HandoffPackage':
        """
        从 YAML 导入
        
        Args:
            yaml_str: YAML 格式的字符串
            
        Returns:
            HandoffPackage 实例
            
        Example:
            >>> yaml_str = '''
            ... handoff:
            ...   schema_version: '1.1'
            ...   from_skill: skill-00
            ...   to_skill: skill-03
            ...   payload:
            ...     intent_type: find_open_source
            ... '''
            >>> handoff = HandoffPackage.from_yaml(yaml_str)
        """
        data = yaml.safe_load(yaml_str)
        return cls.from_dict(data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'HandoffPackage':
        """
        从 JSON 导入
        
        Args:
            json_str: JSON 格式的字符串
            
        Returns:
            HandoffPackage 实例
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def validate(self) -> List[str]:
        """
        验证交接包的完整性和一致性
        
        Returns:
            问题列表，空列表表示验证通过
        """
        issues = []
        
        # 必填字段检查
        if not self.from_skill:
            issues.append("from_skill 不能为空")
        
        if not self.to_skill:
            issues.append("to_skill 不能为空")
        
        if not self.payload:
            issues.append("payload 不能为空")
        
        # 一致性检查
        if self.from_skill == self.to_skill:
            issues.append("from_skill 和 to_skill 不能相同")
        
        # schema 版本检查
        if self.schema_version not in ['1.0', '1.1']:
            issues.append(f"不支持的 schema_version: {self.schema_version}")
        
        return issues
    
    def is_valid(self) -> bool:
        """
        检查交接包是否有效
        
        Returns:
            True 表示有效
        """
        return len(self.validate()) == 0
    
    def get_summary(self) -> str:
        """
        获取交接包摘要
        
        Returns:
            人类可读的摘要字符串
        """
        lines = [
            f"📦 交接包 ({self.handoff_type or '未知类型'})",
            f"  从: {self.from_skill}",
            f"  到: {self.to_skill}",
            f"  创建时间: {self.created_at}",
            f"  Schema: v{self.schema_version}",
        ]
        
        if self.payload:
            lines.append(f"  Payload: {len(self.payload)} 个字段")
        
        if self.self_review:
            lines.append(f"  自我审查: ✅")
        
        if self.downstream_notes:
            lines.append(f"  下游注意事项: ✅")
        
        return "\n".join(lines)


# ===== 便捷工厂方法 =====

def create_handoff_d(
    intent_type: str,
    confidence_score: float,
    recommended_skill: str,
    project_summary: str,
    routing_reason: str = ""
) -> HandoffPackage:
    """
    创建路由推荐包 (HP-D: S00 → 任意)
    
    Args:
        intent_type: 意图类型
        confidence_score: 置信度分数 (0.0-1.0)
        recommended_skill: 推荐的 Skill
        project_summary: 项目摘要
        routing_reason: 路由原因
        
    Returns:
        路由推荐交接包
    """
    return HandoffPackage(
        handoff_type=HandoffType.HP_D.value,
        from_skill=SkillID.SKILL_00.value,
        to_skill=recommended_skill,
        payload={
            'intent_type': intent_type,
            'confidence_score': confidence_score,
            'recommended_skill': recommended_skill,
            'routing_reason': routing_reason,
            'project_summary': project_summary
        },
        user_action=f"将此交接包复制，粘贴到 {recommended_skill} 的对话开头"
    )


def create_handoff_b(
    evaluation_matrix: Dict[str, Any],
    selected_solution: str,
    gap_list: List[str],
    config_suggestions: Dict[str, str]
) -> HandoffPackage:
    """
    创建技术选型包 (HP-B: S03 → S02)
    
    Args:
        evaluation_matrix: 七维度评估矩阵
        selected_solution: 选定方案
        gap_list: 缺口列表
        config_suggestions: 配置建议
        
    Returns:
        技术选型交接包
    """
    return HandoffPackage(
        handoff_type=HandoffType.HP_B.value,
        from_skill=SkillID.SKILL_03.value,
        to_skill=SkillID.SKILL_02.value,
        payload={
            'evaluation_matrix': evaluation_matrix,
            'selected_solution': selected_solution,
            'gap_list': gap_list,
            'config_suggestions': config_suggestions
        },
        user_action="将此交接包复制，粘贴到 Skill 02（SOP 工程师）的对话开头"
    )


def create_handoff_c(
    package_metadata: Dict[str, Any],
    test_targets: List[Dict[str, Any]],
    defect_history: Dict[str, int],
    known_limitations: List[str]
) -> HandoffPackage:
    """
    创建工程包交付 (HP-C: S02 → S05)
    
    Args:
        package_metadata: 工程包元数据
        test_targets: 测试目标列表
        defect_history: 缺陷历史
        known_limitations: 已知限制
        
    Returns:
        工程包交接包
    """
    return HandoffPackage(
        handoff_type=HandoffType.HP_C.value,
        from_skill=SkillID.SKILL_02.value,
        to_skill=SkillID.SKILL_05.value,
        payload={
            'package_metadata': package_metadata,
            'test_targets': test_targets,
            'defect_history': defect_history,
            'known_limitations': known_limitations
        },
        user_action="将此交接包复制，粘贴到 Skill 05（测试验收工程师）的对话开头"
    )


def create_handoff_f(
    verdict: str,
    overall_score: float,
    test_results: Dict[str, Any],
    risk_assessment: Dict[str, Any],
    upstream_feedback: Dict[str, Any]
) -> HandoffPackage:
    """
    创建验收报告包 (HP-F: S05 → 发布)
    
    Args:
        verdict: 验收结论 (PASS/CONDITIONAL_PASS/FAIL)
        overall_score: 总体得分
        test_results: 测试结果
        risk_assessment: 风险评估
        upstream_feedback: 上游反馈包
        
    Returns:
        验收报告交接包
    """
    return HandoffPackage(
        handoff_type=HandoffType.HP_F.value,
        from_skill=SkillID.SKILL_05.value,
        to_skill=SkillID.RELEASE.value,
        payload={
            'verdict': verdict,
            'overall_score': overall_score,
            'test_results': test_results,
            'risk_assessment': risk_assessment,
            'upstream_feedback': upstream_feedback
        },
        user_action="验收完成，根据结论决定是否发布"
    )


def create_handoff(
    schema_version: str = "1.1",
    session_id: str = "",
    from_skill: str = "",
    to_skill: str = "",
    handoff_type: str = "HP-A",
    confidence_score: Optional[float] = None,
    payload: Optional[Dict[str, Any]] = None
) -> HandoffPackage:
    """
    创建通用交接包

    Args:
        schema_version: Schema 版本
        session_id: 会话 ID
        from_skill: 来源 Skill
        to_skill: 目标 Skill
        handoff_type: 交接包类型
        confidence_score: 置信度分数
        payload: 数据负载

    Returns:
        HandoffPackage 对象

    Example:
        >>> handoff = create_handoff(
        ...     from_skill="skill-00",
        ...     to_skill="skill-04",
        ...     handoff_type="HP-A",
        ...     payload={'intent_type': 'build_custom'}
        ... )
    """
    return HandoffPackage(
        schema_version=schema_version,
        session_id=session_id,
        from_skill=from_skill,
        to_skill=to_skill,
        handoff_type=handoff_type,
        confidence_score=confidence_score,
        payload=payload or {}
    )


__all__ = [
    'SkillID',
    'HandoffType',
    'SelfReview',
    'DownstreamNotes',
    'HandoffPackage',
    'create_handoff',
    'create_handoff_d',
    'create_handoff_b',
    'create_handoff_c',
    'create_handoff_f',
]
