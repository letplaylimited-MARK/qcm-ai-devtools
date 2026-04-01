"""
QCM-AI-DevTools 异常处理体系

提供清晰的错误信息和恢复建议
"""

from typing import Optional, Dict, Any, List, Callable


class QCMBasicError(Exception):
    """
    QCM 工具基础异常类

    所有 QCM 工具异常的基类，提供统一的错误处理接口

    Attributes:
        message: 错误信息
        error_code: 错误代码
        recovery_hint: 恢复建议
        context: 额外的上下文信息
    """

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        recovery_hint: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "QCM_ERROR"
        self.recovery_hint = recovery_hint
        self.context = context or {}

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'error_type': self.__class__.__name__,
            'error_code': self.error_code,
            'message': self.message,
            'recovery_hint': self.recovery_hint,
            'context': self.context
        }

    def __str__(self) -> str:
        parts = [f"[{self.error_code}] {self.message}"]
        if self.recovery_hint:
            parts.append(f"  💡 建议: {self.recovery_hint}")
        if self.context:
            parts.append(f"  📋 上下文: {self.context}")
        return "\n".join(parts)


# ============================================================
# 配置相关异常
# ============================================================

class ConfigError(QCMBasicError):
    """配置相关错误的基类"""
    pass


class ConfigGenerationError(ConfigError):
    """配置生成失败"""

    def __init__(
        self,
        message: str,
        description: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="CONFIG_GEN_001",
            recovery_hint="检查项目描述是否清晰，确保包含关键信息（如项目类型、规模等）",
            context={**context, 'description': description} if context else {'description': description}
        )


class ConfigValidationError(ConfigError):
    """配置验证失败"""

    def __init__(
        self,
        message: str,
        validation_errors: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="CONFIG_VAL_001",
            recovery_hint="根据验证错误列表修正配置",
            context={**context, 'validation_errors': validation_errors} if context else {'validation_errors': validation_errors}
        )


class ConfigLoadError(ConfigError):
    """配置加载失败"""

    def __init__(
        self,
        message: str,
        file_path: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="CONFIG_LOAD_001",
            recovery_hint="确保配置文件存在且格式正确（YAML/JSON）",
            context={**context, 'file_path': file_path} if context else {'file_path': file_path}
        )


# ============================================================
# 模板相关异常
# ============================================================

class TemplateError(QCMBasicError):
    """模板相关错误的基类"""
    pass


class TemplateGenerationError(TemplateError):
    """模板生成失败"""

    def __init__(
        self,
        message: str,
        project_type: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="TEMPLATE_GEN_001",
            recovery_hint="检查项目类型是否支持，查看可用项目类型列表",
            context={**context, 'project_type': project_type} if context else {'project_type': project_type}
        )


class TemplateNotFoundError(TemplateError):
    """模板未找到"""

    def __init__(
        self,
        template_name: str,
        available_templates: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=f"模板 '{template_name}' 不存在",
            error_code="TEMPLATE_NF_001",
            recovery_hint=f"使用可用模板之一: {', '.join(available_templates or [])}",
            context={**context, 'template_name': template_name, 'available_templates': available_templates} if context else {'template_name': template_name, 'available_templates': available_templates}
        )


class TemplateRenderError(TemplateError):
    """模板渲染失败"""

    def __init__(
        self,
        message: str,
        template_name: Optional[str] = None,
        missing_vars: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="TEMPLATE_RENDER_001",
            recovery_hint=f"确保提供所有必需变量: {', '.join(missing_vars or [])}",
            context={**context, 'template_name': template_name, 'missing_vars': missing_vars} if context else {'template_name': template_name, 'missing_vars': missing_vars}
        )


# ============================================================
# 质量评估相关异常
# ============================================================

class QualityError(QCMBasicError):
    """质量评估相关错误的基类"""
    pass


class QualityAssessmentError(QualityError):
    """质量评估失败"""

    def __init__(
        self,
        message: str,
        project_path: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="QUALITY_ASSESS_001",
            recovery_hint="确保项目路径存在且包含必需文件",
            context={**context, 'project_path': project_path} if context else {'project_path': project_path}
        )


class QualityThresholdNotMetError(QualityError):
    """质量阈值未达标"""

    def __init__(
        self,
        current_score: float,
        threshold: float,
        failed_checks: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=f"质量评分 {current_score:.1f} 低于阈值 {threshold:.1f}",
            error_code="QUALITY_THRESH_001",
            recovery_hint="修复失败的质量检查项",
            context={
                **context,
                'current_score': current_score,
                'threshold': threshold,
                'failed_checks': failed_checks
            } if context else {
                'current_score': current_score,
                'threshold': threshold,
                'failed_checks': failed_checks
            }
        )


# ============================================================
# 置信度相关异常
# ============================================================

class ConfidenceError(QCMBasicError):
    """置信度相关错误的基类"""
    pass


class ConfidenceAnnotationError(ConfidenceError):
    """置信度标注失败"""

    def __init__(
        self,
        message: str,
        content: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="CONF_ANNOT_001",
            recovery_hint="检查内容格式是否正确",
            context={**context, 'content_preview': content[:100] if content else None} if context else {'content_preview': content[:100] if content else None}
        )


class LowConfidenceError(ConfidenceError):
    """低置信度警告"""

    def __init__(
        self,
        confidence_score: float,
        threshold: float = 0.7,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=f"置信度 {confidence_score:.2f} 低于阈值 {threshold:.2f}",
            error_code="CONF_LOW_001",
            recovery_hint="建议人工审核或提供更多上下文信息",
            context={**context, 'confidence_score': confidence_score, 'threshold': threshold} if context else {'confidence_score': confidence_score, 'threshold': threshold}
        )


# ============================================================
# 工作流相关异常
# ============================================================

class WorkflowError(QCMBasicError):
    """工作流相关错误的基类"""
    pass


class WorkflowExecutionError(WorkflowError):
    """工作流执行失败"""

    def __init__(
        self,
        message: str,
        step: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="WORKFLOW_EXEC_001",
            recovery_hint="检查工作流步骤配置和依赖项",
            context={**context, 'failed_step': step} if context else {'failed_step': step}
        )


class WorkflowInterruptedError(WorkflowError):
    """工作流中断"""

    def __init__(
        self,
        message: str,
        completed_steps: Optional[List[str]] = None,
        pending_steps: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="WORKFLOW_INT_001",
            recovery_hint="使用 resume 参数继续工作流",
            context={
                **context,
                'completed_steps': completed_steps,
                'pending_steps': pending_steps
            } if context else {
                'completed_steps': completed_steps,
                'pending_steps': pending_steps
            }
        )


# ============================================================
# 交接包相关异常
# ============================================================

class HandoffError(QCMBasicError):
    """交接包相关错误的基类"""
    pass


class HandoffValidationError(HandoffError):
    """交接包验证失败"""

    def __init__(
        self,
        message: str,
        handoff_id: Optional[str] = None,
        validation_errors: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="HANDOFF_VAL_001",
            recovery_hint="检查交接包格式是否符合 schema v1.1",
            context={
                **context,
                'handoff_id': handoff_id,
                'validation_errors': validation_errors
            } if context else {
                'handoff_id': handoff_id,
                'validation_errors': validation_errors
            }
        )


class HandoffChainBrokenError(HandoffError):
    """交接包链路中断"""

    def __init__(
        self,
        message: str,
        missing_skill: Optional[str] = None,
        expected_sequence: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="HANDOFF_CHAIN_001",
            recovery_hint="确保按正确的 skill 顺序生成交接包",
            context={
                **context,
                'missing_skill': missing_skill,
                'expected_sequence': expected_sequence
            } if context else {
                'missing_skill': missing_skill,
                'expected_sequence': expected_sequence
            }
        )


# ============================================================
# Navigator 相关异常
# ============================================================

class NavigatorError(QCMBasicError):
    """Navigator 相关错误的基类"""
    pass


class IntentRecognitionError(NavigatorError):
    """意图识别失败"""

    def __init__(
        self,
        message: str,
        user_input: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="NAV_INTENT_001",
            recovery_hint="提供更清晰的描述或使用显式命令",
            context={**context, 'user_input': user_input} if context else {'user_input': user_input}
        )


class LowConfidenceRoutingError(NavigatorError):
    """低置信度路由失败"""

    def __init__(
        self,
        confidence: float,
        threshold: float = 0.5,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=f"意图识别置信度 {confidence:.2f} 过低，无法确定路由",
            error_code="NAV_ROUTE_001",
            recovery_hint="尝试使用更明确的描述或直接调用具体命令",
            context={**context, 'confidence': confidence, 'threshold': threshold} if context else {'confidence': confidence, 'threshold': threshold}
        )


# ============================================================
# 文件系统相关异常
# ============================================================

class FileSystemError(QCMBasicError):
    """文件系统相关错误的基类"""
    pass


class FileWriteError(FileSystemError):
    """文件写入失败"""

    def __init__(
        self,
        message: str,
        file_path: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="FILE_WRITE_001",
            recovery_hint="检查文件路径权限和磁盘空间",
            context={**context, 'file_path': file_path} if context else {'file_path': file_path}
        )


class DirectoryCreationError(FileSystemError):
    """目录创建失败"""

    def __init__(
        self,
        message: str,
        dir_path: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="DIR_CREATE_001",
            recovery_hint="检查父目录权限和路径有效性",
            context={**context, 'dir_path': dir_path} if context else {'dir_path': dir_path}
        )


# ============================================================
# 依赖相关异常
# ============================================================

class DependencyError(QCMBasicError):
    """依赖相关错误的基类"""
    pass


class MissingDependencyError(DependencyError):
    """缺少依赖"""

    def __init__(
        self,
        message: str,
        package_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="DEP_MISS_001",
            recovery_hint=f"安装缺失的依赖: pip install {package_name}" if package_name else "安装缺失的依赖",
            context={**context, 'package_name': package_name} if context else {'package_name': package_name}
        )


class VersionConflictError(DependencyError):
    """版本冲突"""

    def __init__(
        self,
        message: str,
        package_name: Optional[str] = None,
        required_version: Optional[str] = None,
        installed_version: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="DEP_VER_001",
            recovery_hint=f"升级/降级 {package_name} 到版本 {required_version}" if package_name else "解决版本冲突",
            context={
                **context,
                'package_name': package_name,
                'required_version': required_version,
                'installed_version': installed_version
            } if context else {
                'package_name': package_name,
                'required_version': required_version,
                'installed_version': installed_version
            }
        )


# ============================================================
# 便捷函数
# ============================================================

def raise_if_none(obj: Any, message: str, exception_class: type = QCMBasicError) -> Any:
    """
    如果对象为 None，抛出异常

    Args:
        obj: 要检查的对象
        message: 错误信息
        exception_class: 异常类

    Returns:
        原对象（如果不为 None）

    Raises:
        exception_class: 如果 obj 为 None
    """
    if obj is None:
        raise exception_class(message)
    return obj


def wrap_exception(
    func: Callable,
    exception_class: type,
    message: str,
    **context
) -> Any:
    """
    包装函数调用，捕获异常并转换为 QCM 异常

    Args:
        func: 要调用的函数
        exception_class: 目标异常类
        message: 错误信息
        **context: 额外的上下文信息

    Returns:
        函数调用的结果

    Raises:
        exception_class: 如果原函数抛出异常
    """
    try:
        return func()
    except Exception as e:
        raise exception_class(
            message=f"{message}: {str(e)}",
            context={**context, 'original_error': str(e)}
        ) from e
