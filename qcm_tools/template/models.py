"""模板生成器数据模型"""

from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class DirectoryTemplate:
    """目录模板"""
    path: str
    description: str
    files: List[str] = field(default_factory=list)
    subdirs: List['DirectoryTemplate'] = field(default_factory=list)

@dataclass
class ProjectTemplate:
    """项目模板"""
    name: str
    project_type: str
    scale: str
    description: str
    structure: DirectoryTemplate = None
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'project_type': self.project_type,
            'scale': self.scale,
            'description': self.description
        }

__all__ = ['DirectoryTemplate', 'ProjectTemplate']
