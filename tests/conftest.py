"""pytest配置和fixtures"""

import pytest
from qcm_tools.config.models import ProjectConfig, QualityStandard
from qcm_tools.shared.enums import ProjectType, ProjectScale, Role

@pytest.fixture
def sample_quality_standard():
    """质量标准fixture"""
    return QualityStandard(
        functionality="核心功能可用",
        code_quality="测试覆盖≥80%",
        documentation="完整文档",
        security="无明显漏洞"
    )

@pytest.fixture
def sample_project_config():
    """项目配置fixture"""
    return ProjectConfig(
        name="测试项目",
        description="这是一个测试项目",
        project_type=ProjectType.PRODUCTION,
        scale=ProjectScale.MEDIUM,
        tech_stack=["Python", "FastAPI"],
        roles=[Role.ENGINEER, Role.QA]
    )
