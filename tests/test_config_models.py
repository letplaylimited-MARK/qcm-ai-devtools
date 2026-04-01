"""配置模型测试"""

import pytest
from qcm_tools.config.models import ProjectConfig, QualityStandard
from qcm_tools.shared.enums import ProjectType, ProjectScale, Role


class TestQualityStandard:
    """质量标准测试"""
    
    def test_create_quality_standard(self):
        """测试创建质量标准"""
        qs = QualityStandard(
            functionality="核心功能可用",
            code_quality="测试覆盖≥80%"
        )
        
        assert qs.functionality == "核心功能可用"
        assert qs.code_quality == "测试覆盖≥80%"
        assert qs.security == "无明显安全漏洞"  # 默认值
    
    def test_quality_standard_to_dict(self):
        """测试质量标准转字典"""
        qs = QualityStandard(
            functionality="核心功能可用",
            code_quality="测试覆盖≥80%"
        )
        
        qs_dict = qs.to_dict()
        
        assert qs_dict['functionality'] == "核心功能可用"
        assert qs_dict['code_quality'] == "测试覆盖≥80%"
        assert 'security' in qs_dict


class TestProjectConfig:
    """项目配置测试"""
    
    def test_create_project_config(self):
        """测试创建项目配置"""
        config = ProjectConfig(
            name="测试项目",
            description="这是一个测试项目",
            project_type=ProjectType.PRODUCTION,
            scale=ProjectScale.MEDIUM
        )
        
        assert config.name == "测试项目"
        assert config.project_type == ProjectType.PRODUCTION
        assert config.scale == ProjectScale.MEDIUM
    
    def test_config_to_dict(self):
        """测试配置转字典"""
        config = ProjectConfig(
            name="测试项目",
            description="测试描述",
            project_type=ProjectType.PRODUCTION
        )
        
        config_dict = config.to_dict()
        
        assert config_dict['name'] == "测试项目"
        assert config_dict['project_type'] == "生产系统"
        assert config_dict['scale'] == "中型"
    
    def test_config_to_yaml(self):
        """测试配置转YAML"""
        config = ProjectConfig(
            name="测试项目",
            description="测试描述",
            project_type=ProjectType.PRODUCTION
        )
        
        yaml_str = config.to_yaml()
        
        assert 'name: 测试项目' in yaml_str
        assert 'project_type: 生产系统' in yaml_str
    
    def test_config_from_yaml(self):
        """测试从YAML加载配置"""
        yaml_str = """
name: 测试项目
description: 测试描述
project_type: 生产系统
scale: 中型
tech_stack:
  - Python
  - FastAPI
"""
        config = ProjectConfig.from_yaml(yaml_str)
        
        assert config.name == "测试项目"
        assert config.project_type == ProjectType.PRODUCTION
        assert config.scale == ProjectScale.MEDIUM
        assert len(config.tech_stack) == 2
    
    def test_config_with_roles(self, sample_project_config):
        """测试带角色的配置"""
        assert len(sample_project_config.roles) == 2
        assert Role.ENGINEER in sample_project_config.roles
        assert Role.QA in sample_project_config.roles
