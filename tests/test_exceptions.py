"""
测试异常处理体系

验证所有自定义异常的功能
"""

import pytest
from qcm_tools.exceptions import (
    QCMBasicError,
    ConfigGenerationError,
    ConfigValidationError,
    ConfigLoadError,
    TemplateGenerationError,
    TemplateNotFoundError,
    TemplateRenderError,
    QualityAssessmentError,
    QualityThresholdNotMetError,
    ConfidenceAnnotationError,
    LowConfidenceError,
    WorkflowExecutionError,
    WorkflowInterruptedError,
    HandoffValidationError,
    HandoffChainBrokenError,
    IntentRecognitionError,
    LowConfidenceRoutingError,
    FileWriteError,
    DirectoryCreationError,
    MissingDependencyError,
    VersionConflictError,
    raise_if_none,
    wrap_exception,
)


class TestQCMBasicError:
    """测试基础异常类"""

    def test_basic_error_creation(self):
        """测试基础异常创建"""
        error = QCMBasicError(
            message="测试错误",
            error_code="TEST_001",
            recovery_hint="这是恢复建议",
            context={'key': 'value'}
        )

        assert error.message == "测试错误"
        assert error.error_code == "TEST_001"
        assert error.recovery_hint == "这是恢复建议"
        assert error.context == {'key': 'value'}

    def test_to_dict(self):
        """测试转换为字典"""
        error = QCMBasicError(
            message="测试错误",
            error_code="TEST_001",
            recovery_hint="恢复建议",
            context={'key': 'value'}
        )

        result = error.to_dict()

        assert result['error_type'] == 'QCMBasicError'
        assert result['error_code'] == 'TEST_001'
        assert result['message'] == '测试错误'
        assert result['recovery_hint'] == '恢复建议'
        assert result['context'] == {'key': 'value'}

    def test_str_representation(self):
        """测试字符串表示"""
        error = QCMBasicError(
            message="测试错误",
            error_code="TEST_001",
            recovery_hint="恢复建议"
        )

        error_str = str(error)

        assert "[TEST_001]" in error_str
        assert "测试错误" in error_str
        assert "💡 建议:" in error_str
        assert "恢复建议" in error_str

    def test_str_without_hint(self):
        """测试无恢复建议的字符串表示"""
        error = QCMBasicError(message="测试错误", error_code="TEST_001")

        error_str = str(error)

        assert "[TEST_001]" in error_str
        assert "测试错误" in error_str
        assert "💡" not in error_str


class TestConfigErrors:
    """测试配置相关异常"""

    def test_config_generation_error(self):
        """测试配置生成错误"""
        error = ConfigGenerationError(
            message="配置生成失败",
            description="这是一个测试描述"
        )

        assert error.error_code == "CONFIG_GEN_001"
        assert error.context['description'] == "这是一个测试描述"
        assert "检查项目描述" in error.recovery_hint

    def test_config_validation_error(self):
        """测试配置验证错误"""
        error = ConfigValidationError(
            message="配置验证失败",
            validation_errors=["字段缺失", "格式错误"]
        )

        assert error.error_code == "CONFIG_VAL_001"
        assert len(error.context['validation_errors']) == 2

    def test_config_load_error(self):
        """测试配置加载错误"""
        error = ConfigLoadError(
            message="配置加载失败",
            file_path="/path/to/config.yaml"
        )

        assert error.error_code == "CONFIG_LOAD_001"
        assert error.context['file_path'] == "/path/to/config.yaml"


class TestTemplateErrors:
    """测试模板相关异常"""

    def test_template_generation_error(self):
        """测试模板生成错误"""
        error = TemplateGenerationError(
            message="模板生成失败",
            project_type="api"
        )

        assert error.error_code == "TEMPLATE_GEN_001"
        assert error.context['project_type'] == "api"

    def test_template_not_found_error(self):
        """测试模板未找到错误"""
        error = TemplateNotFoundError(
            template_name="missing_template",
            available_templates=["api", "web", "cli"]
        )

        assert error.error_code == "TEMPLATE_NF_001"
        assert "missing_template" in error.message
        assert "api, web, cli" in error.recovery_hint

    def test_template_render_error(self):
        """测试模板渲染错误"""
        error = TemplateRenderError(
            message="模板渲染失败",
            template_name="api_template",
            missing_vars=["project_name", "version"]
        )

        assert error.error_code == "TEMPLATE_RENDER_001"
        assert len(error.context['missing_vars']) == 2


class TestQualityErrors:
    """测试质量评估相关异常"""

    def test_quality_assessment_error(self):
        """测试质量评估错误"""
        error = QualityAssessmentError(
            message="质量评估失败",
            project_path="./my_project"
        )

        assert error.error_code == "QUALITY_ASSESS_001"
        assert error.context['project_path'] == "./my_project"

    def test_quality_threshold_not_met_error(self):
        """测试质量阈值未达标错误"""
        error = QualityThresholdNotMetError(
            current_score=65.0,
            threshold=80.0,
            failed_checks=["文档缺失", "测试不足"]
        )

        assert error.error_code == "QUALITY_THRESH_001"
        assert "65.0" in error.message
        assert "80.0" in error.message
        assert error.context['current_score'] == 65.0
        assert len(error.context['failed_checks']) == 2


class TestConfidenceErrors:
    """测试置信度相关异常"""

    def test_confidence_annotation_error(self):
        """测试置信度标注错误"""
        error = ConfidenceAnnotationError(
            message="置信度标注失败",
            content="这是一个很长的内容..." * 10
        )

        assert error.error_code == "CONF_ANNOT_001"
        assert error.context['content_preview'] is not None
        assert len(error.context['content_preview']) == 100

    def test_low_confidence_error(self):
        """测试低置信度错误"""
        error = LowConfidenceError(
            confidence_score=0.5,
            threshold=0.7
        )

        assert error.error_code == "CONF_LOW_001"
        assert "0.50" in error.message
        assert "0.70" in error.message
        assert "人工审核" in error.recovery_hint


class TestWorkflowErrors:
    """测试工作流相关异常"""

    def test_workflow_execution_error(self):
        """测试工作流执行错误"""
        error = WorkflowExecutionError(
            message="工作流执行失败",
            step="generate_config"
        )

        assert error.error_code == "WORKFLOW_EXEC_001"
        assert error.context['failed_step'] == "generate_config"

    def test_workflow_interrupted_error(self):
        """测试工作流中断错误"""
        error = WorkflowInterruptedError(
            message="工作流中断",
            completed_steps=["step1", "step2"],
            pending_steps=["step3", "step4"]
        )

        assert error.error_code == "WORKFLOW_INT_001"
        assert "resume" in error.recovery_hint.lower()
        assert len(error.context['completed_steps']) == 2
        assert len(error.context['pending_steps']) == 2


class TestHandoffErrors:
    """测试交接包相关异常"""

    def test_handoff_validation_error(self):
        """测试交接包验证错误"""
        error = HandoffValidationError(
            message="交接包验证失败",
            handoff_id="handoff-123",
            validation_errors=["schema 不匹配", "缺少字段"]
        )

        assert error.error_code == "HANDOFF_VAL_001"
        assert error.context['handoff_id'] == "handoff-123"
        assert len(error.context['validation_errors']) == 2

    def test_handoff_chain_broken_error(self):
        """测试交接包链路中断错误"""
        error = HandoffChainBrokenError(
            message="交接包链路中断",
            missing_skill="skill-03",
            expected_sequence=["skill-00", "skill-03", "skill-04"]
        )

        assert error.error_code == "HANDOFF_CHAIN_001"
        assert error.context['missing_skill'] == "skill-03"
        assert len(error.context['expected_sequence']) == 3


class TestNavigatorErrors:
    """测试 Navigator 相关异常"""

    def test_intent_recognition_error(self):
        """测试意图识别错误"""
        error = IntentRecognitionError(
            message="意图识别失败",
            user_input="这是一个模糊的输入"
        )

        assert error.error_code == "NAV_INTENT_001"
        assert error.context['user_input'] == "这是一个模糊的输入"

    def test_low_confidence_routing_error(self):
        """测试低置信度路由错误"""
        error = LowConfidenceRoutingError(
            confidence=0.3,
            threshold=0.5
        )

        assert error.error_code == "NAV_ROUTE_001"
        assert "0.30" in error.message
        assert "命令" in error.recovery_hint


class TestFileSystemErrors:
    """测试文件系统相关异常"""

    def test_file_write_error(self):
        """测试文件写入错误"""
        error = FileWriteError(
            message="文件写入失败",
            file_path="/path/to/file.txt"
        )

        assert error.error_code == "FILE_WRITE_001"
        assert error.context['file_path'] == "/path/to/file.txt"

    def test_directory_creation_error(self):
        """测试目录创建错误"""
        error = DirectoryCreationError(
            message="目录创建失败",
            dir_path="/path/to/dir"
        )

        assert error.error_code == "DIR_CREATE_001"
        assert error.context['dir_path'] == "/path/to/dir"


class TestDependencyErrors:
    """测试依赖相关异常"""

    def test_missing_dependency_error(self):
        """测试缺少依赖错误"""
        error = MissingDependencyError(
            message="缺少依赖",
            package_name="pydantic"
        )

        assert error.error_code == "DEP_MISS_001"
        assert "pip install pydantic" in error.recovery_hint

    def test_version_conflict_error(self):
        """测试版本冲突错误"""
        error = VersionConflictError(
            message="版本冲突",
            package_name="pydantic",
            required_version="2.0",
            installed_version="1.0"
        )

        assert error.error_code == "DEP_VER_001"
        assert error.context['package_name'] == "pydantic"
        assert error.context['required_version'] == "2.0"
        assert error.context['installed_version'] == "1.0"


class TestUtilityFunctions:
    """测试便捷函数"""

    def test_raise_if_none_with_none(self):
        """测试 raise_if_none 在 None 时抛出异常"""
        with pytest.raises(QCMBasicError) as exc_info:
            raise_if_none(None, "对象不能为 None")

        assert "对象不能为 None" in str(exc_info.value)

    def test_raise_if_none_with_value(self):
        """测试 raise_if_none 在有值时不抛出异常"""
        result = raise_if_none("value", "对象不能为 None")
        assert result == "value"

    def test_wrap_exception_success(self):
        """测试 wrap_exception 成功情况"""
        def successful_func():
            return "success"

        result = wrap_exception(
            successful_func,
            ConfigGenerationError,
            "操作失败"
        )

        assert result == "success"

    def test_wrap_exception_failure(self):
        """测试 wrap_exception 失败情况"""
        def failing_func():
            raise ValueError("原始错误")

        with pytest.raises(ConfigGenerationError) as exc_info:
            wrap_exception(
                failing_func,
                ConfigGenerationError,
                "配置生成失败"
            )

        assert "配置生成失败" in str(exc_info.value)
        assert "原始错误" in str(exc_info.value)
        assert exc_info.value.context['original_error'] == "原始错误"


class TestExceptionChaining:
    """测试异常链"""

    def test_exception_chaining(self):
        """测试异常链是否正确保留"""
        try:
            try:
                raise ValueError("底层错误")
            except ValueError as e:
                raise ConfigGenerationError(
                    message="配置生成失败",
                    context={'original': 'error'}
                ) from e
        except ConfigGenerationError as e:
            assert e.__cause__ is not None
            assert isinstance(e.__cause__, ValueError)
            assert str(e.__cause__) == "底层错误"


class TestErrorCodes:
    """测试错误代码唯一性"""

    def test_all_error_codes_unique(self):
        """测试所有错误代码唯一"""
        exceptions = [
            ConfigGenerationError("test"),
            ConfigValidationError("test"),
            ConfigLoadError("test"),
            TemplateGenerationError("test"),
            TemplateNotFoundError("test"),
            TemplateRenderError("test"),
            QualityAssessmentError("test"),
            QualityThresholdNotMetError(50.0, 80.0),
            ConfidenceAnnotationError("test"),
            LowConfidenceError(0.5),
            WorkflowExecutionError("test"),
            WorkflowInterruptedError("test"),
            HandoffValidationError("test"),
            HandoffChainBrokenError("test"),
            IntentRecognitionError("test"),
            LowConfidenceRoutingError(0.3),
            FileWriteError("test"),
            DirectoryCreationError("test"),
            MissingDependencyError("test"),
            VersionConflictError("test"),
        ]

        error_codes = [e.error_code for e in exceptions]
        assert len(error_codes) == len(set(error_codes)), "错误代码有重复"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
