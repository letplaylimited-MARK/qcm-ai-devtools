"""
配置生成器实现

提供自动化的项目配置生成功能
"""

from typing import List, Dict, Optional
from qcm_tools.config.models import ProjectConfig, QualityStandard
from qcm_tools.shared.enums import ProjectType, ProjectScale, Role


class ConfigGenerator:
    """
    配置生成器
    
    根据项目类型或描述自动生成项目配置
    
    Example:
        >>> generator = ConfigGenerator()
        >>> config = generator.generate_from_type(ProjectType.PRODUCTION)
        >>> print(config.name)
        未命名项目
        
        >>> config = generator.generate_from_description("开发一个用户管理API")
        >>> print(config.project_type)
        ProjectType.PRODUCTION
    """
    
    # 预定义的项目类型配置模板
    TYPE_CONFIGS = {
        ProjectType.RESEARCH: {
            'roles': [Role.ARCHITECT, Role.ENGINEER, Role.RESEARCHER, Role.QA, Role.DOC_WRITER],
            'quality_standards': QualityStandard(
                functionality="核心功能可用",
                code_quality="基本规范",
                documentation="论文格式+实验说明",
                reproducibility="实验可重复",
                academic_norms="符合学术规范",
                security="无明显漏洞"
            ),
            'documentation_requirements': [
                "README.md",
                "实验说明文档",
                "论文全文",
                "实验数据"
            ],
            'keywords': ['研究', '实验', '算法', '论文', '科研', '学术']
        },
        ProjectType.PRODUCTION: {
            'roles': [Role.ARCHITECT, Role.ENGINEER, Role.QA, Role.DOC_WRITER, Role.SECURITY_EXPERT],
            'quality_standards': QualityStandard(
                functionality="所有功能正常",
                code_quality="测试覆盖≥80%",
                documentation="完整文档+部署指南",
                security="无安全漏洞"
            ),
            'documentation_requirements': [
                "README.md",
                "API文档",
                "部署文档",
                "用户手册",
                "测试报告"
            ],
            'keywords': ['API', '系统', '服务', '应用', '生产', '企业', '后端', '前端', 'Web']
        },
        ProjectType.TEACHING: {
            'roles': [Role.ENGINEER, Role.DOC_WRITER],
            'quality_standards': QualityStandard(
                functionality="示例功能正常",
                code_quality="代码清晰、注释完整",
                documentation="详细教程+示例代码"
            ),
            'documentation_requirements': [
                "README.md",
                "教程文档",
                "示例代码",
                "练习题"
            ],
            'keywords': ['教学', '教程', '课程', '学习', '示例', 'demo', 'example']
        },
        ProjectType.PERSONAL: {
            'roles': [Role.ENGINEER],
            'quality_standards': QualityStandard(
                functionality="功能正确",
                code_quality="基本规范",
                documentation="README"
            ),
            'documentation_requirements': [
                "README.md"
            ],
            'keywords': ['个人', '工具', '脚本', '小工具', 'personal', 'tool', 'script']
        }
    }
    
    # 技术栈关键词映射
    TECH_KEYWORDS = {
        'Python': ['python', 'django', 'flask', 'fastapi', 'pytorch', 'tensorflow'],
        'JavaScript': ['javascript', 'js', 'node', 'react', 'vue', 'angular'],
        'Java': ['java', 'spring', 'springboot'],
        'Go': ['go', 'golang'],
        'Database': ['database', 'mysql', 'postgresql', 'mongodb', 'redis'],
        'API': ['api', 'rest', 'restful', 'graphql'],
        'Frontend': ['frontend', 'web', 'html', 'css', 'react', 'vue'],
        'Backend': ['backend', 'server', 'service', 'microservice'],
    }
    
    def __init__(self):
        """初始化配置生成器"""
        pass
    
    def generate_from_type(
        self,
        project_type: ProjectType,
        name: str = "未命名项目",
        description: str = "",
        scale: ProjectScale = ProjectScale.MEDIUM,
        tech_stack: List[str] = None
    ) -> ProjectConfig:
        """
        根据项目类型生成配置
        
        Args:
            project_type: 项目类型枚举
            name: 项目名称
            description: 项目描述
            scale: 项目规模
            tech_stack: 技术栈列表
            
        Returns:
            项目配置对象
            
        Example:
            >>> generator = ConfigGenerator()
            >>> config = generator.generate_from_type(
            ...     ProjectType.PRODUCTION,
            ...     name="用户管理API",
            ...     tech_stack=["Python", "FastAPI"]
            ... )
        """
        template = self.TYPE_CONFIGS[project_type]
        
        return ProjectConfig(
            name=name,
            description=description,
            project_type=project_type,
            scale=scale,
            tech_stack=tech_stack or [],
            roles=template['roles'].copy(),
            quality_standards=template['quality_standards'],
            documentation_requirements=template['documentation_requirements'].copy()
        )
    
    def generate_from_description(
        self,
        description: str,
        name: str = None,
        scale: ProjectScale = None
    ) -> ProjectConfig:
        """
        根据描述生成配置(基于关键词匹配)
        
        Args:
            description: 项目描述(自然语言)
            name: 项目名称(可选,从描述中提取)
            scale: 项目规模(可选,从描述中推断)
            
        Returns:
            项目配置对象
            
        Example:
            >>> generator = ConfigGenerator()
            >>> config = generator.generate_from_description(
            ...     "开发一个用户管理API,使用FastAPI和PostgreSQL"
            ... )
        """
        # 分析描述,推断项目类型
        project_type = self._infer_project_type(description)
        
        # 提取技术栈
        tech_stack = self._extract_tech_stack(description)
        
        # 推断项目规模
        if scale is None:
            scale = self._infer_scale(description)
        
        # 提取项目名称
        if name is None:
            name = self._extract_project_name(description)
        
        # 生成配置
        return self.generate_from_type(
            project_type=project_type,
            name=name,
            description=description,
            scale=scale,
            tech_stack=tech_stack
        )
    
    def generate_custom(
        self,
        base_type: ProjectType,
        name: str,
        description: str,
        customizations: Dict
    ) -> ProjectConfig:
        """
        基于基础类型生成自定义配置
        
        Args:
            base_type: 基础项目类型
            name: 项目名称
            description: 项目描述
            customizations: 自定义配置项
            
        Returns:
            自定义配置对象
            
        Example:
            >>> config = generator.generate_custom(
            ...     ProjectType.PRODUCTION,
            ...     name="微服务API",
            ...     description="微服务架构",
            ...     customizations={
            ...         'roles': [Role.ENGINEER, Role.QA],
            ...         'quality_standards': {
            ...             'code_quality': '测试覆盖≥90%'
            ...         }
            ...     }
            ... )
        """
        # 生成基础配置
        base_config = self.generate_from_type(base_type, name, description)
        
        # 应用自定义设置
        if 'roles' in customizations:
            base_config.roles = customizations['roles']
        
        if 'quality_standards' in customizations:
            # 合并质量标准
            qs_dict = {
                'functionality': base_config.quality_standards.functionality,
                'code_quality': base_config.quality_standards.code_quality,
                'documentation': base_config.quality_standards.documentation,
                'security': base_config.quality_standards.security,
            }
            qs_dict.update(customizations['quality_standards'])
            base_config.quality_standards = QualityStandard(**qs_dict)
        
        if 'documentation_requirements' in customizations:
            base_config.documentation_requirements = customizations['documentation_requirements']
        
        if 'tech_stack' in customizations:
            base_config.tech_stack = customizations['tech_stack']
        
        if 'scale' in customizations:
            base_config.scale = customizations['scale']
        
        return base_config
    
    def validate_config(self, config: ProjectConfig) -> List[str]:
        """
        验证配置的合理性
        
        Args:
            config: 项目配置
            
        Returns:
            问题列表,空列表表示验证通过
            
        Example:
            >>> config = ProjectConfig(name="", description="", project_type=ProjectType.PRODUCTION)
            >>> issues = generator.validate_config(config)
            >>> print(issues)
            ['项目名称不能为空', '项目描述不能为空']
        """
        issues = []
        
        # 检查必填字段
        if not config.name or not config.name.strip():
            issues.append("项目名称不能为空")
        
        if not config.description or not config.description.strip():
            issues.append("项目描述不能为空")
        
        # 检查角色合理性
        if config.project_type == ProjectType.RESEARCH and Role.RESEARCHER not in config.roles:
            issues.append("研究原型项目建议包含研究设计师角色")
        
        if config.project_type == ProjectType.PRODUCTION and Role.QA not in config.roles:
            issues.append("生产系统项目建议包含质量保障师角色")
        
        if config.project_type == ProjectType.PRODUCTION and Role.SECURITY_EXPERT not in config.roles:
            issues.append("生产系统项目建议包含安全专家角色")
        
        # 检查质量标准合理性
        qs = config.quality_standards
        if config.project_type == ProjectType.PRODUCTION:
            if "测试覆盖" not in qs.code_quality and "测试" not in qs.code_quality:
                issues.append("生产系统项目建议明确测试覆盖率要求")
        
        if config.project_type == ProjectType.RESEARCH:
            if not qs.reproducibility or qs.reproducibility == "N/A":
                issues.append("研究原型项目建议明确实验可重复性要求")
        
        # 检查文档要求
        if not config.documentation_requirements:
            issues.append("建议明确文档要求")
        
        return issues
    
    def _infer_project_type(self, description: str) -> ProjectType:
        """从描述中推断项目类型"""
        description_lower = description.lower()
        
        # 统计各类型关键词出现次数
        scores = {}
        for ptype, config in self.TYPE_CONFIGS.items():
            score = sum(1 for keyword in config['keywords'] if keyword.lower() in description_lower)
            scores[ptype] = score
        
        # 选择得分最高的类型
        max_score = max(scores.values())
        if max_score == 0:
            # 如果没有匹配关键词,默认为个人工具
            return ProjectType.PERSONAL
        
        for ptype, score in scores.items():
            if score == max_score:
                return ptype
    
    def _extract_tech_stack(self, description: str) -> List[str]:
        """从描述中提取技术栈"""
        description_lower = description.lower()
        tech_stack = []
        
        for tech, keywords in self.TECH_KEYWORDS.items():
            if any(keyword in description_lower for keyword in keywords):
                tech_stack.append(tech)
        
        return tech_stack
    
    def _infer_scale(self, description: str) -> ProjectScale:
        """从描述中推断项目规模"""
        description_lower = description.lower()
        
        # 大型项目关键词
        large_keywords = ['大型', '企业级', '微服务', '分布式', '高并发', 'large', 'enterprise', 'microservice']
        if any(keyword in description_lower for keyword in large_keywords):
            return ProjectScale.LARGE
        
        # 小型项目关键词
        small_keywords = ['小型', '简单', '快速', '原型', '演示', 'small', 'simple', 'prototype', 'demo', 'poc']
        if any(keyword in description_lower for keyword in small_keywords):
            return ProjectScale.SMALL
        
        # 默认中型
        return ProjectScale.MEDIUM
    
    def _extract_project_name(self, description: str) -> str:
        """从描述中提取项目名称"""
        # 简单实现:取描述的前20个字符作为名称
        # 实际应用中可以使用NLP技术提取
        name = description.split('，')[0].split(',')[0].split('。')[0]
        if len(name) > 20:
            name = name[:20]
        return name or "未命名项目"


__all__ = ['ConfigGenerator']
