"""
QCM-AI-DevTools

AI Programming and Research Integrated Development Tools
"""

__version__ = '0.1.0'
__author__ = 'QCM Team'
__project__ = 'QCM-AI-DevTools'

from qcm_tools.shared.enums import (
    ProjectType,
    ProjectScale,
    Role,
    ConfidenceLevel,
    InfoType,
    QualityLevel
)

from qcm_tools.config import ConfigGenerator, ProjectConfig, QualityStandard
from qcm_tools.template import TemplateGenerator, ProjectTemplate
from qcm_tools.quality import QualityAssessor, QualityReport
from qcm_tools.confidence import ConfidenceAnnotator, ConfidenceAnnotation
from qcm_tools.workflow import DevToolsWorkflow, quick_create_project
from qcm_tools.handoff import (
    HandoffPackage,
    HandoffType,
    SkillID,
    HandoffManager
)
from qcm_tools.skills import Navigator
from qcm_tools.exceptions import (
    QCMBasicError,
    ConfigError,
    ConfigGenerationError,
    ConfigValidationError,
    ConfigLoadError,
    TemplateError,
    TemplateGenerationError,
    TemplateNotFoundError,
    TemplateRenderError,
    QualityError,
    QualityAssessmentError,
    QualityThresholdNotMetError,
    ConfidenceError,
    ConfidenceAnnotationError,
    LowConfidenceError,
    WorkflowError,
    WorkflowExecutionError,
    WorkflowInterruptedError,
    HandoffError,
    HandoffValidationError,
    HandoffChainBrokenError,
    NavigatorError,
    IntentRecognitionError,
    LowConfidenceRoutingError,
    FileSystemError,
    FileWriteError,
    DirectoryCreationError,
    DependencyError,
    MissingDependencyError,
    VersionConflictError,
)

__all__ = [
    # Enums
    'ProjectType',
    'ProjectScale', 
    'Role',
    'ConfidenceLevel',
    'InfoType',
    'QualityLevel',
    # Tools
    'ConfigGenerator',
    'ProjectConfig',
    'QualityStandard',
    'TemplateGenerator',
    'ProjectTemplate',
    'QualityAssessor',
    'QualityReport',
    'ConfidenceAnnotator',
    'ConfidenceAnnotation',
    'DevToolsWorkflow',
    # Handoff
    'HandoffPackage',
    'HandoffType',
    'SkillID',
    'HandoffManager',
    # Skills
    'Navigator',
    # Exceptions
    'QCMBasicError',
    'ConfigError',
    'ConfigGenerationError',
    'ConfigValidationError',
    'ConfigLoadError',
    'TemplateError',
    'TemplateGenerationError',
    'TemplateNotFoundError',
    'TemplateRenderError',
    'QualityError',
    'QualityAssessmentError',
    'QualityThresholdNotMetError',
    'ConfidenceError',
    'ConfidenceAnnotationError',
    'LowConfidenceError',
    'WorkflowError',
    'WorkflowExecutionError',
    'WorkflowInterruptedError',
    'HandoffError',
    'HandoffValidationError',
    'HandoffChainBrokenError',
    'NavigatorError',
    'IntentRecognitionError',
    'LowConfidenceRoutingError',
    'FileSystemError',
    'FileWriteError',
    'DirectoryCreationError',
    'DependencyError',
    'MissingDependencyError',
    'VersionConflictError',
    # Convenience functions
    'quick_create_project',
]
