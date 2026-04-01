"""
配置工具数据模型

定义项目配置相关的数据结构
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
import yaml
import json

from qcm_tools.shared.enums import ProjectType, ProjectScale, Role


@dataclass
class QualityStandard:
    """
    质量标准数据类
    
    定义项目的质量标准要求
    
    Attributes:
        functionality: 功能正确性标准
        code_quality: 代码质量标准
        documentation: 文档完整性标准
        reproducibility: 实验可重复性标准(可选,科研项目使用)
        academic_norms: 学术规范标准(可选,科研项目使用)
        security: 安全性标准
    
    Example:
        >>> qs = QualityStandard(
        ...     functionality="所有功能正常",
        ...     code_quality="测试覆盖≥85%"
        ... )
        >>> print(qs.functionality)
        所有功能正常
    """
    functionality: str = "核心功能可用"
    code_quality: str = "通过静态检查"
    documentation: str = "README完整"
    reproducibility: Optional[str] = None
    academic_norms: Optional[str] = None
    security: str = "无明显安全漏洞"
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'functionality': self.functionality,
            'code_quality': self.code_quality,
            'documentation': self.documentation,
            'reproducibility': self.reproducibility,
            'academic_norms': self.academic_norms,
            'security': self.security,
        }


@dataclass
class ProjectConfig:
    """
    项目配置数据类
    
    定义完整的项目配置信息
    
    Attributes:
        name: 项目名称
        description: 项目描述
        project_type: 项目类型
        scale: 项目规模
        tech_stack: 技术栈列表
        roles: 角色列表
        quality_standards: 质量标准
        workflow_stages: 工作流阶段
        documentation_requirements: 文档要求列表
        custom_settings: 自定义设置
    
    Example:
        >>> from qcm_tools.shared.enums import ProjectType
        >>> config = ProjectConfig(
        ...     name="用户管理API",
        ...     description="RESTful API服务",
        ...     project_type=ProjectType.PRODUCTION
        ... )
        >>> print(config.name)
        用户管理API
    """
    name: str
    description: str
    project_type: ProjectType
    scale: ProjectScale = ProjectScale.MEDIUM
    tech_stack: List[str] = field(default_factory=list)
    roles: List[Role] = field(default_factory=list)
    quality_standards: QualityStandard = field(default_factory=QualityStandard)
    workflow_stages: List[str] = field(default_factory=lambda: [
        "需求确认与方案设计",
        "核心开发与实验",
        "完善与优化",
        "文档与论文撰写",
        "验收与交付"
    ])
    documentation_requirements: List[str] = field(default_factory=list)
    custom_settings: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """
        转换为字典
        
        Returns:
            包含所有配置信息的字典
            
        Example:
            >>> config = ProjectConfig(
            ...     name="测试项目",
            ...     description="测试描述",
            ...     project_type=ProjectType.PRODUCTION
            ... )
            >>> config_dict = config.to_dict()
            >>> print(config_dict['name'])
            测试项目
        """
        return {
            'name': self.name,
            'description': self.description,
            'project_type': self.project_type.value,
            'scale': self.scale.value,
            'tech_stack': self.tech_stack,
            'roles': [role.value for role in self.roles],
            'quality_standards': self.quality_standards.to_dict(),
            'workflow_stages': self.workflow_stages,
            'documentation_requirements': self.documentation_requirements,
            'custom_settings': self.custom_settings,
        }
    
    def to_yaml(self) -> str:
        """
        导出为YAML格式
        
        Returns:
            YAML格式的配置字符串
            
        Example:
            >>> config = ProjectConfig(
            ...     name="测试项目",
            ...     description="测试描述",
            ...     project_type=ProjectType.PRODUCTION
            ... )
            >>> yaml_str = config.to_yaml()
            >>> print('name: 测试项目' in yaml_str)
            True
        """
        return yaml.dump(self.to_dict(), allow_unicode=True, sort_keys=False, default_flow_style=False)
    
    def to_json(self) -> str:
        """
        导出为JSON格式
        
        Returns:
            JSON格式的配置字符串
        """
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ProjectConfig':
        """
        从字典加载配置
        
        Args:
            data: 包含配置信息的字典
            
        Returns:
            项目配置对象
            
        Example:
            >>> data = {
            ...     'name': '测试项目',
            ...     'description': '测试描述',
            ...     'project_type': '生产系统',
            ...     'scale': '中型'
            ... }
            >>> config = ProjectConfig.from_dict(data)
            >>> print(config.name)
            测试项目
        """
        # 处理枚举类型
        data['project_type'] = ProjectType(data['project_type'])
        data['scale'] = ProjectScale(data.get('scale', '中型'))
        
        # 处理角色列表
        if 'roles' in data and data['roles']:
            data['roles'] = [Role(role) for role in data['roles']]
        
        # 处理质量标准
        if 'quality_standards' in data and isinstance(data['quality_standards'], dict):
            data['quality_standards'] = QualityStandard(**data['quality_standards'])
        
        return cls(**data)
    
    @classmethod
    def from_yaml(cls, yaml_str: str) -> 'ProjectConfig':
        """
        从YAML加载配置
        
        Args:
            yaml_str: YAML格式的配置字符串
            
        Returns:
            项目配置对象
            
        Example:
            >>> yaml_str = '''
            ... name: 测试项目
            ... description: 测试描述
            ... project_type: 生产系统
            ... scale: 中型
            ... '''
            >>> config = ProjectConfig.from_yaml(yaml_str)
            >>> print(config.name)
            测试项目
        """
        data = yaml.safe_load(yaml_str)
        return cls.from_dict(data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'ProjectConfig':
        """
        从JSON加载配置
        
        Args:
            json_str: JSON格式的配置字符串
            
        Returns:
            项目配置对象
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def to_yaml_file(self, filepath: str):
        """
        导出为YAML文件
        
        Args:
            filepath: 目标文件路径
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.to_yaml())
    
    @classmethod
    def from_yaml_file(cls, filepath: str) -> 'ProjectConfig':
        """
        从YAML文件加载配置
        
        Args:
            filepath: YAML文件路径
            
        Returns:
            项目配置对象
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            return cls.from_yaml(f.read())


__all__ = ['QualityStandard', 'ProjectConfig']
