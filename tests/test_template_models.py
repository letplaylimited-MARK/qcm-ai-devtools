"""模板模型测试"""

import pytest
from qcm_tools.template.models import DirectoryTemplate, ProjectTemplate


class TestDirectoryTemplate:
    """目录模板测试"""
    
    def test_create_directory_template(self):
        """测试创建目录模板"""
        template = DirectoryTemplate(
            path="src",
            description="源代码目录",
            files=["main.py"]
        )
        
        assert template.path == "src"
        assert template.description == "源代码目录"
        assert len(template.files) == 1


class TestProjectTemplate:
    """项目模板测试"""
    
    def test_create_project_template(self):
        """测试创建项目模板"""
        template = ProjectTemplate(
            name="生产系统模板",
            project_type="生产系统",
            scale="中型",
            description="生产系统中型项目模板"
        )
        
        assert template.name == "生产系统模板"
        assert template.project_type == "生产系统"
    
    def test_template_to_dict(self):
        """测试模板转字典"""
        template = ProjectTemplate(
            name="测试模板",
            project_type="生产系统",
            scale="中型",
            description="测试模板"
        )
        
        template_dict = template.to_dict()
        
        assert template_dict['name'] == "测试模板"
        assert template_dict['project_type'] == "生产系统"
