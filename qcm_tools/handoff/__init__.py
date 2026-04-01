"""
交接包管理模块

提供与 ai-skill-system 兼容的标准化交接包机制
"""

from qcm_tools.handoff.models import (
    HandoffPackage,
    HandoffType,
    SkillID,
    create_handoff,
    create_handoff_d,
    create_handoff_b,
    create_handoff_c,
    create_handoff_f,
)
from qcm_tools.handoff.manager import HandoffManager

__all__ = [
    'HandoffPackage',
    'HandoffType',
    'SkillID',
    'HandoffManager',
    'create_handoff',
    'create_handoff_d',
    'create_handoff_b',
    'create_handoff_c',
    'create_handoff_f',
]
