"""
共享枚举类型定义

定义QCM工具系统中使用的所有枚举类型
"""

from enum import Enum


class ProjectType(Enum):
    """
    项目类型枚举
    
    定义四种项目类型,每种类型有不同的质量标准和工作流程
    
    Attributes:
        RESEARCH: 研究原型 - 学术研究、算法实验、概念验证
        PRODUCTION: 生产系统 - 商业应用、企业系统、长期维护项目
        TEACHING: 教学项目 - 教程示例、课程作业、学习项目
        PERSONAL: 个人工具 - 个人使用的小工具、快速验证想法
    """
    RESEARCH = "研究原型"
    PRODUCTION = "生产系统"
    TEACHING = "教学项目"
    PERSONAL = "个人工具"


class ProjectScale(Enum):
    """
    项目规模枚举
    
    根据代码量级定义项目规模
    
    Attributes:
        SMALL: 小型项目 - <1000行代码
        MEDIUM: 中型项目 - 1000-10000行代码
        LARGE: 大型项目 - >10000行代码
    """
    SMALL = "小型"
    MEDIUM = "中型"
    LARGE = "大型"


class Role(Enum):
    """
    角色类型枚举
    
    定义项目中可能涉及的角色,包括核心角色和扩展角色
    
    核心角色:
        ARCHITECT: 项目架构师 - 负责技术方案设计
        ENGINEER: 代码工程师 - 负责编码实现
        RESEARCHER: 研究设计师 - 负责科研设计
        QA: 质量保障师 - 负责质量验证
        DOC_WRITER: 文档工程师 - 负责文档输出
    
    扩展角色:
        SECURITY_EXPERT: 安全专家 - 负责安全相关
        PERFORMANCE_EXPERT: 性能优化师 - 负责性能优化
        DATA_ANALYST: 数据分析师 - 负责数据分析
    """
    # 核心角色
    ARCHITECT = "项目架构师"
    ENGINEER = "代码工程师"
    RESEARCHER = "研究设计师"
    QA = "质量保障师"
    DOC_WRITER = "文档工程师"
    # 扩展角色
    SECURITY_EXPERT = "安全专家"
    PERFORMANCE_EXPERT = "性能优化师"
    DATA_ANALYST = "数据分析师"


class ConfidenceLevel(Enum):
    """
    置信度级别枚举
    
    用于标注信息的可信程度
    
    Attributes:
        HIGH: 高置信度 - 基于文献、官方文档等可靠来源
        MEDIUM: 中置信度 - 基于推理、经验判断
        LOW: 低置信度 - 可能不准确,需要验证
    """
    HIGH = "高"
    MEDIUM = "中"
    LOW = "低"


class InfoType(Enum):
    """
    信息类型枚举
    
    定义置信度标注的信息类型
    
    Attributes:
        CONCLUSION: 结论 - 研究或分析得出的结论
        DATA: 数据 - 具体的数据或统计信息
        CITATION: 引用 - 引用文献或资料
        INFERENCE: 推断 - 基于推理得出的结论
    """
    CONCLUSION = "结论"
    DATA = "数据"
    CITATION = "引用"
    INFERENCE = "推断"


class QualityLevel(Enum):
    """
    质量等级枚举
    
    用于评估质量得分对应的等级
    
    Attributes:
        EXCELLENT: 优秀 - ≥90分
        GOOD: 良好 - ≥80分
        PASS: 合格 - ≥60分
        FAIL: 不合格 - <60分
    """
    EXCELLENT = "优秀"
    GOOD = "良好"
    PASS = "合格"
    FAIL = "不合格"


# 导出所有枚举类型
__all__ = [
    'ProjectType',
    'ProjectScale',
    'Role',
    'ConfidenceLevel',
    'InfoType',
    'QualityLevel',
]
