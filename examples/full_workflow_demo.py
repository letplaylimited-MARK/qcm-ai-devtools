#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QCM-AI-DevTools 完整工作流演示

演示完整的工具链使用流程:
1. 从描述生成配置
2. 创建项目结构
3. 质量评估
4. 置信度标注
"""

import sys
import os
sys.path.insert(0, '/workspace/qcm-ai-devtools')

from qcm_tools.config import ConfigGenerator
from qcm_tools.template import TemplateGenerator
from qcm_tools.quality import QualityAssessor
from qcm_tools.shared.enums import ProjectType


def main():
    """完整工作流演示"""
    print("=" * 70)
    print("QCM-AI-DevTools 完整工作流演示")
    print("=" * 70)
    print()
    
    # 步骤1: 从描述生成配置
    print("【步骤1】生成项目配置")
    print("-" * 70)
    
    config_gen = ConfigGenerator()
    description = "开发一个用户管理API系统,使用FastAPI和PostgreSQL,中型生产项目"
    
    print(f"需求描述: {description}")
    config = config_gen.generate_from_description(description)
    
    print(f"✅ 配置生成成功")
    print(f"   项目名称: {config.name}")
    print(f"   项目类型: {config.project_type.value}")
    print(f"   技术栈: {', '.join(config.tech_stack)}")
    print()
    
    # 步骤2: 创建项目结构
    print("【步骤2】创建项目结构")
    print("-" * 70)
    
    template_gen = TemplateGenerator()
    output_path = "/tmp/qcm_full_demo"
    
    project_path = template_gen.create_project(config, output_path, overwrite=True)
    
    print(f"✅ 项目创建成功: {project_path}")
    
    # 显示项目结构(只显示前3层)
    print("\n项目结构预览:")
    for i, (root, dirs, files) in enumerate(os.walk(project_path)):
        if i >= 10:  # 只显示前10个目录
            break
        level = root.replace(project_path, '').count(os.sep)
        indent = '  ' * level
        print(f"{indent}{os.path.basename(root)}/")
        if level < 2:  # 只显示文件到第2层
            subindent = '  ' * (level + 1)
            for file in files[:3]:
                print(f"{subindent}{file}")
            if len(files) > 3:
                print(f"{subindent}... ({len(files) - 3} more files)")
    print()
    
    # 步骤3: 质量评估
    print("【步骤3】质量评估")
    print("-" * 70)
    
    assessor = QualityAssessor()
    report = assessor.assess(project_path, config)
    
    print(f"✅ 评估完成")
    print(f"   总体得分: {report.overall_score:.1f}/100")
    print(f"   质量等级: {report.overall_level.value}")
    print()
    
    print("各指标评估结果:")
    for name, result in report.indicator_results.items():
        status = "✅" if result.passed else "❌"
        print(f"  {status} {name}: {result.score:.1f}分 ({result.level.value})")
    print()
    
    if report.recommendations:
        print("改进建议:")
        for i, rec in enumerate(report.recommendations[:3], 1):
            print(f"  {i}. {rec}")
    print()
    
    # 步骤4: 总结
    print("【总结】")
    print("-" * 70)
    print("✅ ConfigGenerator: 配置自动生成")
    print("✅ TemplateGenerator: 项目结构创建")
    print("✅ QualityAssessor: 质量评估")
    print()
    
    print("工作流完成!")
    print(f"项目路径: {project_path}")
    print(f"配置文件: {os.path.join(project_path, 'qcm_project.yaml')}")
    print()
    
    # 显示配置文件内容
    config_file = os.path.join(project_path, 'qcm_project.yaml')
    if os.path.exists(config_file):
        print("配置文件预览:")
        with open(config_file, 'r') as f:
            lines = f.readlines()[:10]
            for line in lines:
                print(f"  {line.rstrip()}")
        print("  ...")
    
    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
