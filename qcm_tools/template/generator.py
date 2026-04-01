"""
模板生成器实现

提供项目结构和文件模板生成功能
"""

import os
from typing import List, Dict, Optional
from pathlib import Path
from qcm_tools.template.models import DirectoryTemplate, ProjectTemplate
from qcm_tools.config.models import ProjectConfig
from qcm_tools.shared.enums import ProjectType, ProjectScale


class TemplateGenerator:
    """
    项目模板生成器
    
    根据项目配置生成项目目录结构和基础文件
    
    Example:
        >>> from qcm_tools.config import ConfigGenerator
        >>> from qcm_tools.template import TemplateGenerator
        >>> 
        >>> # 生成配置
        >>> config_gen = ConfigGenerator()
        >>> config = config_gen.generate_from_description("开发一个API系统")
        >>> 
        >>> # 生成项目
        >>> template_gen = TemplateGenerator()
        >>> template_gen.create_project(config, "./my_project")
    """
    
    # 预定义的项目模板
    TEMPLATES = {
        (ProjectType.PRODUCTION, ProjectScale.SMALL): DirectoryTemplate(
            path='',
            description='生产系统小型项目',
            files=['README.md', 'requirements.txt', '.gitignore', 'main.py'],
            subdirs=[
                DirectoryTemplate('src', '源代码', files=['__init__.py']),
                DirectoryTemplate('tests', '测试代码', files=['__init__.py', 'test_main.py']),
                DirectoryTemplate('docs', '文档')
            ]
        ),
        (ProjectType.PRODUCTION, ProjectScale.MEDIUM): DirectoryTemplate(
            path='',
            description='生产系统中型项目',
            files=['README.md', 'requirements.txt', '.gitignore', 'Dockerfile', 'docker-compose.yml'],
            subdirs=[
                DirectoryTemplate('src', '源代码', subdirs=[
                    DirectoryTemplate('core', '核心模块', files=['__init__.py']),
                    DirectoryTemplate('utils', '工具函数', files=['__init__.py']),
                    DirectoryTemplate('api', 'API接口', files=['__init__.py']),
                    DirectoryTemplate('models', '数据模型', files=['__init__.py'])
                ]),
                DirectoryTemplate('tests', '测试代码', subdirs=[
                    DirectoryTemplate('unit', '单元测试', files=['__init__.py']),
                    DirectoryTemplate('integration', '集成测试', files=['__init__.py'])
                ]),
                DirectoryTemplate('docs', '文档', files=['api.md', 'deployment.md']),
                DirectoryTemplate('scripts', '脚本文件'),
                DirectoryTemplate('config', '配置文件')
            ]
        ),
        (ProjectType.PRODUCTION, ProjectScale.LARGE): DirectoryTemplate(
            path='',
            description='生产系统大型项目',
            files=['README.md', 'requirements.txt', '.gitignore', 'Dockerfile', 'docker-compose.yml', 'pyproject.toml'],
            subdirs=[
                DirectoryTemplate('src', '源代码', subdirs=[
                    DirectoryTemplate('core', '核心模块', files=['__init__.py']),
                    DirectoryTemplate('utils', '工具函数', files=['__init__.py']),
                    DirectoryTemplate('api', 'API接口', files=['__init__.py']),
                    DirectoryTemplate('models', '数据模型', files=['__init__.py']),
                    DirectoryTemplate('services', '业务服务', files=['__init__.py']),
                    DirectoryTemplate('repositories', '数据访问', files=['__init__.py'])
                ]),
                DirectoryTemplate('tests', '测试代码', subdirs=[
                    DirectoryTemplate('unit', '单元测试', files=['__init__.py']),
                    DirectoryTemplate('integration', '集成测试', files=['__init__.py']),
                    DirectoryTemplate('e2e', '端到端测试', files=['__init__.py'])
                ]),
                DirectoryTemplate('docs', '文档', subdirs=[
                    DirectoryTemplate('api', 'API文档'),
                    DirectoryTemplate('architecture', '架构文档'),
                    DirectoryTemplate('deployment', '部署文档')
                ]),
                DirectoryTemplate('scripts', '脚本文件'),
                DirectoryTemplate('config', '配置文件', subdirs=[
                    DirectoryTemplate('dev', '开发环境'),
                    DirectoryTemplate('prod', '生产环境')
                ]),
                DirectoryTemplate('migrations', '数据库迁移')
            ]
        ),
        (ProjectType.RESEARCH, ProjectScale.SMALL): DirectoryTemplate(
            path='',
            description='研究原型小型项目',
            files=['README.md', 'requirements.txt', '.gitignore'],
            subdirs=[
                DirectoryTemplate('code', '实验代码', files=['main.py']),
                DirectoryTemplate('data', '数据文件', subdirs=[
                    DirectoryTemplate('raw', '原始数据'),
                    DirectoryTemplate('processed', '处理后数据'),
                    DirectoryTemplate('results', '实验结果')
                ]),
                DirectoryTemplate('notebooks', 'Jupyter笔记本'),
                DirectoryTemplate('paper', '论文文件', files=['main.tex', 'references.bib'])
            ]
        ),
        (ProjectType.RESEARCH, ProjectScale.MEDIUM): DirectoryTemplate(
            path='',
            description='研究原型中型项目',
            files=['README.md', 'requirements.txt', '.gitignore'],
            subdirs=[
                DirectoryTemplate('code', '实验代码', subdirs=[
                    DirectoryTemplate('experiments', '实验脚本', files=['__init__.py']),
                    DirectoryTemplate('models', '模型定义', files=['__init__.py']),
                    DirectoryTemplate('utils', '工具函数', files=['__init__.py'])
                ]),
                DirectoryTemplate('data', '数据文件', subdirs=[
                    DirectoryTemplate('raw', '原始数据'),
                    DirectoryTemplate('processed', '处理后数据'),
                    DirectoryTemplate('results', '实验结果')
                ]),
                DirectoryTemplate('notebooks', 'Jupyter笔记本'),
                DirectoryTemplate('paper', '论文文件', files=['main.tex', 'references.bib']),
                DirectoryTemplate('figures', '图表文件')
            ]
        ),
        (ProjectType.TEACHING, ProjectScale.SMALL): DirectoryTemplate(
            path='',
            description='教学项目小型',
            files=['README.md', 'requirements.txt', '.gitignore'],
            subdirs=[
                DirectoryTemplate('examples', '示例代码', files=['example1.py']),
                DirectoryTemplate('exercises', '练习题'),
                DirectoryTemplate('solutions', '参考答案')
            ]
        ),
        (ProjectType.TEACHING, ProjectScale.MEDIUM): DirectoryTemplate(
            path='',
            description='教学项目中型',
            files=['README.md', 'requirements.txt', '.gitignore', 'setup.py'],
            subdirs=[
                DirectoryTemplate('examples', '示例代码', subdirs=[
                    DirectoryTemplate('basic', '基础示例'),
                    DirectoryTemplate('advanced', '进阶示例')
                ]),
                DirectoryTemplate('exercises', '练习题'),
                DirectoryTemplate('solutions', '参考答案'),
                DirectoryTemplate('docs', '教学文档', files=['tutorial.md', 'api.md'])
            ]
        ),
        (ProjectType.PERSONAL, ProjectScale.SMALL): DirectoryTemplate(
            path='',
            description='个人工具小型',
            files=['README.md', 'requirements.txt', '.gitignore', 'main.py'],
            subdirs=[
                DirectoryTemplate('src', '源代码', files=['__init__.py'])
            ]
        )
    }
    
    # 文件模板内容
    FILE_TEMPLATES = {
        'README.md': """# {project_name}

{description}

## 安装

```bash
pip install -r requirements.txt
```

## 使用

```python
# 使用示例
```

## 开发

```bash
# 运行测试
python -m pytest tests/

# 代码检查
pylint src/
```

## 许可证

MIT License
""",
        'requirements.txt': """# Python依赖
# 核心依赖
{dependencies}
""",
        '.gitignore': """*.pyc
__pycache__/
.env
venv/
*.egg-info/
dist/
build/
.pytest_cache/
.coverage
htmlcov/
""",
        'main.py': """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
{project_name} - {description}
\"\"\"

def main():
    \"\"\"主函数\"\"\"
    print("Hello, {project_name}!")

if __name__ == "__main__":
    main()
""",
        '__init__.py': """\"\"\"模块初始化\"\"\"
""",
        'test_main.py': """\"\"\"测试主模块\"\"\"
import pytest

def test_placeholder():
    \"\"\"占位测试\"\"\"
    assert True
""",
        'Dockerfile': """FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
""",
        'docker-compose.yml': """version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENV=development
""",
        'main.tex': r"""\documentclass{article}
\title{{{{project_name}}}}
\author{{Author Name}}
\date{{\today}}

\begin{{document}}
\maketitle

\begin{{abstract}}
{description}
\end{{abstract}}

\section{{Introduction}}
% 在这里写介绍

\bibliographystyle{{plain}}
\bibliography{{references}}
\end{{document}}
""",
        'references.bib': """@article{example2023,
  title={Example Article},
  author={Author, Name},
  journal={Journal},
  year={2023}
}
"""
    }
    
    def __init__(self):
        """初始化模板生成器"""
        pass
    
    def generate_template(
        self,
        project_type: ProjectType,
        scale: ProjectScale
    ) -> ProjectTemplate:
        """
        生成项目模板
        
        Args:
            project_type: 项目类型
            scale: 项目规模
            
        Returns:
            项目模板对象
            
        Example:
            >>> generator = TemplateGenerator()
            >>> template = generator.generate_template(
            ...     ProjectType.PRODUCTION,
            ...     ProjectScale.MEDIUM
            ... )
        """
        key = (project_type, scale)
        
        # 如果没有精确匹配,尝试降级到小型项目
        if key not in self.TEMPLATES:
            # 对于研究项目,默认使用小型模板
            if project_type == ProjectType.RESEARCH:
                key = (ProjectType.RESEARCH, ProjectScale.SMALL)
            # 对于教学项目,默认使用小型模板
            elif project_type == ProjectType.TEACHING:
                key = (ProjectType.TEACHING, ProjectScale.SMALL)
            # 对于个人工具,默认使用小型模板
            elif project_type == ProjectType.PERSONAL:
                key = (ProjectType.PERSONAL, ProjectScale.SMALL)
            # 对于生产系统,默认使用中型模板
            else:
                key = (ProjectType.PRODUCTION, ProjectScale.MEDIUM)
        
        structure = self.TEMPLATES[key]
        
        return ProjectTemplate(
            name=f"{project_type.value}-{scale.value}",
            project_type=project_type.value,
            scale=scale.value,
            description=f"{project_type.value}项目模板({scale.value})",
            structure=structure
        )
    
    def create_project(
        self,
        config: ProjectConfig,
        output_path: str,
        overwrite: bool = False
    ) -> str:
        """
        创建项目目录结构
        
        Args:
            config: 项目配置
            output_path: 输出路径
            overwrite: 是否覆盖已存在的文件
            
        Returns:
            项目路径
            
        Example:
            >>> from qcm_tools.config import ConfigGenerator
            >>> config_gen = ConfigGenerator()
            >>> config = config_gen.generate_from_description("开发一个API系统")
            >>> 
            >>> template_gen = TemplateGenerator()
            >>> project_path = template_gen.create_project(config, "./my_project")
        """
        # 生成模板
        template = self.generate_template(config.project_type, config.scale)
        
        # 创建项目目录
        project_path = Path(output_path) / self._sanitize_name(config.name)
        
        if project_path.exists() and not overwrite:
            raise FileExistsError(f"项目目录已存在: {project_path}")
        
        project_path.mkdir(parents=True, exist_ok=True)
        
        # 创建目录结构
        if template.structure:
            self._create_structure(template.structure, project_path, config)
        
        # 保存项目配置文件
        config_file = project_path / 'qcm_project.yaml'
        config.to_yaml_file(str(config_file))
        
        return str(project_path)
    
    def _create_structure(
        self,
        structure: DirectoryTemplate,
        base_path: Path,
        config: ProjectConfig
    ):
        """创建目录结构"""
        current_path = base_path / structure.path if structure.path else base_path
        
        # 创建当前目录
        current_path.mkdir(parents=True, exist_ok=True)
        
        # 创建文件
        for file_name in structure.files:
            file_path = current_path / file_name
            
            # 只在文件不存在时创建,避免覆盖
            if not file_path.exists():
                content = self._get_file_content(file_name, config)
                file_path.write_text(content, encoding='utf-8')
        
        # 递归创建子目录
        for subdir in structure.subdirs:
            self._create_structure(subdir, current_path, config)
    
    def _get_file_content(self, file_name: str, config: ProjectConfig) -> str:
        """获取文件内容"""
        if file_name in self.FILE_TEMPLATES:
            template = self.FILE_TEMPLATES[file_name]
            
            # 替换模板变量
            content = template.format(
                project_name=config.name,
                description=config.description,
                dependencies=self._generate_dependencies(config.tech_stack)
            )
            
            return content
        
        # 默认空文件
        return ""
    
    def _generate_dependencies(self, tech_stack: List[str]) -> str:
        """生成依赖列表"""
        # 根据技术栈生成推荐依赖
        deps = ["# 核心依赖"]
        
        if "Python" in tech_stack or "API" in tech_stack or "Backend" in tech_stack:
            deps.extend([
                "# fastapi>=0.100.0",
                "# uvicorn>=0.23.0",
                "# pydantic>=2.0"
            ])
        
        if "Database" in tech_stack:
            deps.extend([
                "# sqlalchemy>=2.0",
                "# psycopg2-binary>=2.9"
            ])
        
        if "Frontend" in tech_stack or "JavaScript" in tech_stack:
            deps.append("# 前端相关依赖...")
        
        return "\n".join(deps) if len(deps) > 1 else "# 添加项目依赖"
    
    def _sanitize_name(self, name: str) -> str:
        """清理项目名称"""
        # 移除特殊字符,转小写,空格转下划线
        import re
        sanitized = re.sub(r'[^\w\s-]', '', name)
        sanitized = re.sub(r'[-\s]+', '_', sanitized)
        return sanitized.lower().strip('_')
    
    def list_available_templates(self) -> List[Dict]:
        """列出所有可用模板"""
        templates = []
        for (project_type, scale), structure in self.TEMPLATES.items():
            templates.append({
                'project_type': project_type.value,
                'scale': scale.value,
                'name': f"{project_type.value}-{scale.value}",
                'description': structure.description
            })
        return templates


__all__ = ['TemplateGenerator']
