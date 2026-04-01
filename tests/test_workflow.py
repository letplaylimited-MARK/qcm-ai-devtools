"""
DevToolsWorkflow 增强功能测试

测试新增的 Navigator 和 HandoffManager 集成方法
"""

import pytest
import os
import tempfile
import shutil
from qcm_tools import DevToolsWorkflow, quick_create_project
from qcm_tools.handoff import HandoffPackage


class TestDevToolsWorkflowBasic:
    """测试基本工作流功能"""
    
    @pytest.fixture
    def workflow(self):
        return DevToolsWorkflow()
    
    @pytest.fixture
    def temp_dir(self):
        dir_path = tempfile.mkdtemp()
        yield dir_path
        shutil.rmtree(dir_path, ignore_errors=True)
    
    def test_create_workflow(self):
        """测试创建工作流"""
        workflow = DevToolsWorkflow()
        assert workflow is not None
        assert workflow.config_generator is not None
        assert workflow.navigator is not None
        assert workflow.handoff_manager is not None
    
    def test_create_workflow_without_handoff(self):
        """测试不启用交接包的工作流"""
        workflow = DevToolsWorkflow(use_handoff=False)
        assert workflow.handoff_manager is None
    
    def test_quick_create_project(self, temp_dir):
        """测试快速创建项目"""
        result = quick_create_project(
            "开发一个API系统",
            output_path=os.path.join(temp_dir, "test_project")
        )
        
        assert result['status'] == 'completed'
        assert result['config'] is not None


class TestDevToolsWorkflowNavigator:
    """测试 Navigator 集成"""
    
    @pytest.fixture
    def workflow(self):
        return DevToolsWorkflow()
    
    @pytest.fixture
    def temp_dir(self):
        dir_path = tempfile.mkdtemp()
        yield dir_path
        shutil.rmtree(dir_path, ignore_errors=True)
    
    def test_start_from_natural_language(self, workflow, temp_dir):
        """测试从自然语言开始工作流"""
        result = workflow.start_from_natural_language(
            "开发一个API系统",
            output_path=os.path.join(temp_dir, "test_project")
        )
        
        assert result['status'] == 'completed'
        assert result['navigator_analysis'] is not None
        assert result['handoff'] is not None
    
    def test_navigator_analysis_result(self, workflow):
        """测试 Navigator 分析结果"""
        result = workflow.start_from_natural_language(
            "找一个开源的NLP库",
            auto_execute=False
        )
        
        assert result['navigator_analysis']['intent_type'] == 'find_open_source'
        assert result['navigator_analysis']['confidence'] >= 0.6
    
    def test_handoff_stored(self, workflow):
        """测试交接包存储"""
        result = workflow.start_from_natural_language(
            "开发一个用户管理系统",
            auto_execute=False
        )
        
        # 交接包应该在结果中
        assert result['handoff'] is not None
        assert result['handoff'].from_skill == "skill-00"


class TestDevToolsWorkflowValidation:
    """测试项目验证"""
    
    @pytest.fixture
    def workflow(self):
        return DevToolsWorkflow()
    
    @pytest.fixture
    def temp_dir(self):
        dir_path = tempfile.mkdtemp()
        yield dir_path
        shutil.rmtree(dir_path, ignore_errors=True)
    
    def test_validate_project(self, workflow, temp_dir):
        """测试项目验证"""
        # 先创建项目
        create_result = workflow.create_project_from_description(
            "开发一个API系统",
            output_path=os.path.join(temp_dir, "test_project")
        )
        
        # 验证项目
        validate_result = workflow.validate_project(create_result['project_path'])
        
        assert validate_result['status'] == 'completed'
        assert validate_result['quality_report'] is not None
        assert validate_result['verdict'] in ['PASS', 'CONDITIONAL_PASS', 'FAIL']
    
    def test_release_decision(self, workflow):
        """测试发布决策"""
        from qcm_tools.quality import QualityReport
        from qcm_tools.quality.models import IndicatorResult
        from qcm_tools.shared.enums import QualityLevel
        
        # 高质量项目
        report_high = QualityReport(project_name="test", project_type="production")
        report_high.overall_score = 85.0
        report_high.indicator_results = {
            'code': IndicatorResult(indicator_name='code', score=85, level=QualityLevel.GOOD, passed=True, details=[], recommendations=[])
        }
        verdict = workflow._make_release_decision(report_high)
        assert verdict == 'PASS'
        
        # 中等质量项目
        report_medium = QualityReport(project_name="test", project_type="production")
        report_medium.overall_score = 75.0
        report_medium.indicator_results = {
            'code': IndicatorResult(indicator_name='code', score=75, level=QualityLevel.PASS, passed=True, details=[], recommendations=[])
        }
        verdict = workflow._make_release_decision(report_medium)
        assert verdict == 'CONDITIONAL_PASS'
        
        # 低质量项目
        report_low = QualityReport(project_name="test", project_type="production")
        report_low.overall_score = 50.0
        report_low.indicator_results = {
            'code': IndicatorResult(indicator_name='code', score=50, level=QualityLevel.FAIL, passed=False, details=[], recommendations=[])
        }
        verdict = workflow._make_release_decision(report_low)
        assert verdict == 'FAIL'


class TestDevToolsWorkflowHandoff:
    """测试交接包管理"""
    
    @pytest.fixture
    def workflow(self):
        return DevToolsWorkflow()
    
    @pytest.fixture
    def temp_dir(self):
        dir_path = tempfile.mkdtemp()
        yield dir_path
        shutil.rmtree(dir_path, ignore_errors=True)
    
    def test_get_handoff_chain(self, workflow):
        """测试获取交接包链路"""
        # 执行工作流
        result = workflow.start_from_natural_language(
            "开发一个系统",
            auto_execute=False
        )
        
        # 检查交接包在结果中
        assert result['handoff'] is not None
        
        # 如果有 handoff_manager，检查链路
        if workflow.handoff_manager:
            chain = workflow.get_handoff_chain()
            assert len(chain) > 0
    
    def test_export_handoff_chain(self, workflow):
        """测试导出交接包链路"""
        result = workflow.start_from_natural_language(
            "开发一个系统",
            auto_execute=False
        )
        
        # 检查交接包
        assert result['handoff'] is not None
        
        # 导出交接包
        yaml_str = result['handoff'].to_yaml()
        assert "skill-00" in yaml_str
    
    def test_multiple_handoffs_in_chain(self, workflow, temp_dir):
        """测试链路中有多个交接包"""
        result = workflow.ai_development_with_navigation(
            "开发一个API系统",
            output_path=os.path.join(temp_dir, "test_project")
        )
        
        # 检查至少有一个交接包
        assert len(result['handoffs']) >= 1


class TestDevToolsWorkflowAI:
    """测试 AI 辅助开发"""
    
    @pytest.fixture
    def workflow(self):
        return DevToolsWorkflow()
    
    @pytest.fixture
    def temp_dir(self):
        dir_path = tempfile.mkdtemp()
        yield dir_path
        shutil.rmtree(dir_path, ignore_errors=True)
    
    def test_ai_development_with_navigation(self, workflow, temp_dir):
        """测试 AI 辅助开发（带导航）"""
        result = workflow.ai_development_with_navigation(
            "开发一个用户管理API",
            output_path=os.path.join(temp_dir, "ai_project")
        )
        
        assert result['status'] == 'completed'
        assert result['navigation'] is not None
        assert result['config'] is not None
        assert result['quality_report'] is not None
    
    def test_ai_development_generates_handoffs(self, workflow, temp_dir):
        """测试 AI 开发生成交接包"""
        result = workflow.ai_development_with_navigation(
            "开发一个系统",
            output_path=os.path.join(temp_dir, "ai_project")
        )
        
        assert len(result['handoffs']) >= 1


class TestDevToolsWorkflowIntegration:
    """测试完整集成工作流"""
    
    @pytest.fixture
    def workflow(self):
        return DevToolsWorkflow()
    
    @pytest.fixture
    def temp_dir(self):
        dir_path = tempfile.mkdtemp()
        yield dir_path
        shutil.rmtree(dir_path, ignore_errors=True)
    
    def test_full_workflow_end_to_end(self, workflow, temp_dir):
        """测试端到端完整工作流"""
        # Step 1: 用户输入
        user_input = "开发一个情感分析API系统"
        
        # Step 2: Navigator 分析
        result = workflow.start_from_natural_language(
            user_input,
            output_path=os.path.join(temp_dir, "full_project")
        )
        
        # Step 3: 验证
        assert result['status'] == 'completed'
        assert result['handoff'] is not None
        
        # Step 4: 检查交接包
        handoff = result['handoff']
        assert handoff.from_skill == "skill-00"
        
        # Step 5: 导出交接包
        yaml_str = handoff.to_yaml()
        assert 'skill-00' in yaml_str
    
    def test_workflow_status_report(self, workflow, temp_dir):
        """测试工作流状态报告"""
        result = workflow.create_project_from_description(
            "开发一个API系统",
            output_path=os.path.join(temp_dir, "report_project")
        )
        
        status = workflow.get_workflow_status(result)
        assert "完成" in status or "completed" in status.lower()
    
    def test_workflow_summary_report(self, workflow, temp_dir):
        """测试工作流总结报告"""
        result = workflow.create_project_from_description(
            "开发一个API系统",
            output_path=os.path.join(temp_dir, "summary_project")
        )
        
        report = workflow.generate_summary_report(result)
        assert "QCM-AI-DevTools" in report
        assert "项目配置" in report
