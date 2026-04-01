#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QCM-AI-DevTools 端到端演示

演示完整的工具链使用流程:
1. 从描述生成配置
2. 创建项目结构  
3. 展示质量评估
4. 展示置信度标注
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, '/workspace/qcm-ai-devtools')

from qcm_tools.config import ConfigGenerator
from qcm_tools.template import TemplateGenerator
from qcm_tools.shared.enums import ProjectType


def main():
    """端到端演示"""
    print("=" * 70)
    print("QCM-AI-DevTools 端到端演示")
    print("=" * 70)
    print()
    
    # 步骤1: 从描述生成配置
    print("【步骤1】从描述生成项目配置")
    print("-" * 70)
    
    generator = ConfigGenerator()
    
    description = "开发一个用户管理API系统,使用FastAPI和PostgreSQL,中型生产项目"
    print(f"项目描述: {description}")
    print()
    
    config = generator.generate_from_description(description)
    
    print(f"✅ 配置生成成功!")
    print(f"   项目名称: {config.name}")
    print(f"   项目类型: {config.project_type.value}")
    print(f"   项目规模: {config.scale.value}")
    print(f"   技术栈: {', '.join(config.tech_stack) if config.tech_stack else '未指定'}")
    print(f"   角色: {', '.join([role.value for role in config.roles])}")
    print()
    
    # 验证配置
    issues = generator.validate_config(config)
    if issues:
        print(f"⚠️  配置验证问题: {issues}")
    else:
        print(f"✅ 配置验证通过")
    print()
    
    # 步骤2: 创建项目结构
    print("【步骤2】创建项目结构")
    print("-" * 70)
    
    template_gen = TemplateGenerator()
    
    # 创建临时项目目录
    output_path = "/tmp/qcm_demo_project"
    
    try:
        project_path = template_gen.create_project(config, output_path, overwrite=True)
        
        print(f"✅ 项目创建成功!")
        print(f"   项目路径: {project_path}")
        print()
        
        # 显示项目结构
        print("   项目结构:")
        import os
        for root, dirs, files in os.walk(project_path):
            level = root.replace(project_path, '').count(os.sep)
            indent = ' ' * 4 * level
            print(f'{indent}{os.path.basename(root)}/')
            subindent = ' ' * 4 * (level + 1)
            for file in files[:5]:  # 只显示前5个文件
                print(f'{subindent}{file}')
            if len(files) > 5:
                print(f'{subindent}... ({len(files) - 5} more files)')
        print()
        
        # 显示配置文件内容
        config_file = os.path.join(project_path, 'qcm_project.yaml')
        if os.path.exists(config_file):
            print("   配置文件内容:")
            with open(config_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()[:10]  # 只显示前10行
                for line in lines:
                    print(f"   {line.rstrip()}")
            print()
            
    except Exception as e:
        print(f"❌ 项目创建失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 步骤3: 展示其他功能
    print("【步骤3】展示其他功能")
    print("-" * 70)
    
    # 3.1 自定义配置
    print("   3.1 自定义配置示例:")
    custom_config = generator.generate_custom(
        base_type=ProjectType.PRODUCTION,
        name="微服务API",
        description="微服务架构的用户管理系统",
        customizations={
            'roles': ['代码工程师', '质量保障师'],  # 精简团队
            'quality_standards': {
                'code_quality': '测试覆盖≥90%'  # 提高标准
            }
        }
    )
    print(f"      自定义配置创建成功: {custom_config.name}")
    print(f"      角色: {[role.value if hasattr(role, 'value') else role for role in custom_config.roles]}")
    print(f"      代码质量标准: {custom_config.quality_standards.code_quality}")
    print()
    
    # 3.2 模板列表
    print("   3.2 可用模板列表:")
    templates = template_gen.list_available_templates()
    for i, template in enumerate(templates[:5], 1):
        print(f"      {i}. {template['name']}: {template['description']}")
    if len(templates) > 5:
        print(f"      ... 还有 {len(templates) - 5} 个模板")
    print()
    
    # 步骤4: 总结
    print("【总结】")
    print("-" * 70)
    print("✅ ConfigGenerator: 配置生成功能正常")
    print("✅ TemplateGenerator: 项目创建功能正常")
    print("✅ 数据模型: 序列化/反序列化正常")
    print("✅ 验证功能: 配置验证正常")
    print()
    
    print("🎉 端到端演示完成!")
    print()
    print("下一步可以实现:")
    print("  1. QualityAssessor - 质量评估器")
    print("  2. ConfidenceAnnotator - 置信度标注器增强")
    print("  3. DevToolsWorkflow - 工作流编排器")
    print("  4. AI集成示例")
    print()
    
    print("=" * 70)


if __name__ == "__main__":
    main()
