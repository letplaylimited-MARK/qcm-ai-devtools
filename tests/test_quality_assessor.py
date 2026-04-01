"""QualityAssessor测试"""

import pytest
import os
import tempfile
from qcm_tools.quality import QualityAssessor
from qcm_tools.config import ConfigGenerator
from qcm_tools.shared.enums import ProjectType


class TestQualityAssessor:
    """质量评估器测试"""
    
    @pytest.fixture
    def assessor(self):
        """创建评估器实例"""
        return QualityAssessor()
    
    @pytest.fixture
    def sample_project(self):
        """创建示例项目"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建Python文件
            code = '''
"""示例模块"""

def hello(name: str) -> str:
    """问候函数"""
    return f"Hello, {name}!"

def add(a: int, b: int) -> int:
    """加法函数"""
    return a + b
'''
            with open(os.path.join(tmpdir, 'main.py'), 'w') as f:
                f.write(code)
            
            # 创建README
            readme = '''# 测试项目

## 安装

pip install -r requirements.txt

## 使用

python main.py
'''
            with open(os.path.join(tmpdir, 'README.md'), 'w') as f:
                f.write(readme)
            
            yield tmpdir
    
    def test_assess_project(self, assessor, sample_project):
        """测试评估项目"""
        report = assessor.assess(sample_project)
        
        assert report.project_name is not None
        assert len(report.indicator_results) > 0
        assert report.overall_score >= 0
    
    def test_assess_code(self, assessor):
        """测试评估代码"""
        code = '''
def hello():
    """问候函数"""
    print("Hello, World!")
'''
        report = assessor.assess_code(code)
        
        assert '代码质量' in report.indicator_results
        assert report.overall_score > 0
    
    def test_code_quality_checker(self, assessor, sample_project):
        """测试代码质量检查"""
        report = assessor.assess(sample_project)
        
        assert '代码质量' in report.indicator_results
        result = report.indicator_results['代码质量']
        
        assert result.score >= 0
        assert result.level is not None
    
    def test_documentation_checker(self, assessor, sample_project):
        """测试文档完整性检查"""
        report = assessor.assess(sample_project)
        
        assert '文档完整性' in report.indicator_results
        result = report.indicator_results['文档完整性']
        
        # 有README,应该有分数
        assert result.score > 0
    
    def test_security_checker(self, assessor, sample_project):
        """测试安全性检查"""
        report = assessor.assess(sample_project)
        
        assert '安全性' in report.indicator_results
        result = report.indicator_results['安全性']
        
        # 没有安全问题,应该得高分
        assert result.score >= 80
    
    def test_insecure_code(self, assessor):
        """测试不安全代码"""
        code = '''
password = "hardcoded_password123"
secret = "my_secret_key"
eval(user_input)
'''
        report = assessor.assess_code(code)
        
        # 应该检测到安全问题
        assert '安全性' in report.indicator_results
        security_result = report.indicator_results['安全性']
        assert security_result.score < 80
    
    def test_report_markdown(self, assessor, sample_project):
        """测试Markdown报告生成"""
        report = assessor.assess(sample_project)
        markdown = report.to_markdown()
        
        assert "# 质量评估报告" in markdown
        assert "总体得分" in markdown
        assert "代码质量" in markdown
    
    def test_with_config(self, assessor, sample_project):
        """测试带配置的评估"""
        config_gen = ConfigGenerator()
        config = config_gen.generate_from_type(
            ProjectType.PRODUCTION,
            name="测试项目",
            description="测试项目描述"
        )
        
        report = assessor.assess(sample_project, config)
        
        assert report.project_name == "测试项目"
        assert report.project_type == "生产系统"
