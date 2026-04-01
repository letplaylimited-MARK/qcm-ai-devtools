"""ConfigGenerator测试"""

import pytest
from qcm_tools.config import ConfigGenerator
from qcm_tools.shared.enums import ProjectType, ProjectScale, Role


class TestConfigGenerator:
    """配置生成器测试"""
    
    @pytest.fixture
    def generator(self):
        """创建生成器实例"""
        return ConfigGenerator()
    
    def test_generate_from_type_production(self, generator):
        """测试生成生产系统配置"""
        config = generator.generate_from_type(
            ProjectType.PRODUCTION,
            name="用户管理API",
            description="RESTful API服务",
            tech_stack=["Python", "FastAPI"]
        )
        
        assert config.name == "用户管理API"
        assert config.project_type == ProjectType.PRODUCTION
        assert Role.ARCHITECT in config.roles
        assert Role.SECURITY_EXPERT in config.roles
        assert "Python" in config.tech_stack
    
    def test_generate_from_type_research(self, generator):
        """测试生成研究原型配置"""
        config = generator.generate_from_type(
            ProjectType.RESEARCH,
            name="算法实验"
        )
        
        assert config.project_type == ProjectType.RESEARCH
        assert Role.RESEARCHER in config.roles
        assert config.quality_standards.reproducibility == "实验可重复"
    
    def test_generate_from_description_api(self, generator):
        """测试从描述生成配置 - API项目"""
        config = generator.generate_from_description(
            "开发一个用户管理API系统,使用FastAPI和PostgreSQL"
        )
        
        assert config.project_type == ProjectType.PRODUCTION
        assert "API" in config.tech_stack or "Backend" in config.tech_stack
    
    def test_generate_from_description_research(self, generator):
        """测试从描述生成配置 - 研究项目"""
        config = generator.generate_from_description(
            "这是一个机器学习算法研究项目"
        )
        
        assert config.project_type == ProjectType.RESEARCH
        assert Role.RESEARCHER in config.roles
    
    def test_generate_from_description_teaching(self, generator):
        """测试从描述生成配置 - 教学项目"""
        config = generator.generate_from_description(
            "创建一个Python教学示例项目"
        )
        
        assert config.project_type == ProjectType.TEACHING
    
    def test_generate_custom(self, generator):
        """测试生成自定义配置"""
        config = generator.generate_custom(
            base_type=ProjectType.PRODUCTION,
            name="微服务API",
            description="微服务架构",
            customizations={
                'roles': [Role.ENGINEER, Role.QA],
                'quality_standards': {
                    'code_quality': '测试覆盖≥90%'
                }
            }
        )
        
        assert len(config.roles) == 2
        assert config.quality_standards.code_quality == "测试覆盖≥90%"
    
    def test_validate_config_success(self, generator):
        """测试验证正确的配置"""
        config = generator.generate_from_type(
            ProjectType.PRODUCTION,
            name="测试项目",
            description="这是一个测试项目"
        )
        
        issues = generator.validate_config(config)
        assert len(issues) == 0
    
    def test_validate_config_missing_fields(self, generator):
        """测试验证缺少必填字段的配置"""
        from qcm_tools.config.models import ProjectConfig
        
        config = ProjectConfig(
            name="",
            description="",
            project_type=ProjectType.PRODUCTION
        )
        
        issues = generator.validate_config(config)
        assert len(issues) > 0
        assert "项目名称不能为空" in issues
        assert "项目描述不能为空" in issues
    
    def test_infer_project_type(self, generator):
        """测试推断项目类型"""
        assert generator._infer_project_type("开发一个API系统") == ProjectType.PRODUCTION
        assert generator._infer_project_type("这是一个研究项目") == ProjectType.RESEARCH
        assert generator._infer_project_type("创建教学示例") == ProjectType.TEACHING
    
    def test_extract_tech_stack(self, generator):
        """测试提取技术栈"""
        tech = generator._extract_tech_stack("使用Python和FastAPI开发")
        assert "Python" in tech or "API" in tech
        
        tech = generator._extract_tech_stack("使用React和Node.js开发前端")
        assert "JavaScript" in tech or "Frontend" in tech
    
    def test_infer_scale(self, generator):
        """测试推断项目规模"""
        assert generator._infer_scale("这是一个大型企业级系统") == ProjectScale.LARGE
        assert generator._infer_scale("这是一个简单的演示demo") == ProjectScale.SMALL
        assert generator._infer_scale("这是一个普通项目") == ProjectScale.MEDIUM
