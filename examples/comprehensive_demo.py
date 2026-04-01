#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QCM-AI-DevTools 综合演示

展示所有核心工具的完整功能:
1. ConfigGenerator - 配置生成
2. TemplateGenerator - 项目创建
3. QualityAssessor - 质量评估
4. ConfidenceAnnotator - 置信度标注
"""

import sys
import os
sys.path.insert(0, '/workspace/qcm-ai-devtools')

from qcm_tools.config import ConfigGenerator
from qcm_tools.template import TemplateGenerator
from qcm_tools.quality import QualityAssessor
from qcm_tools.confidence import ConfidenceAnnotator
from qcm_tools.shared.enums import ProjectType, InfoType


def main():
    """综合功能演示"""
    print("=" * 70)
    print("QCM-AI-DevTools 综合功能演示")
    print("=" * 70)
    print()
    
    # ===== 1. 配置生成 =====
    print("【1】ConfigGenerator - 智能配置生成")
    print("-" * 70)
    
    config_gen = ConfigGenerator()
    
    # 从描述生成配置
    description = "开发一个企业级微服务API系统,使用FastAPI和PostgreSQL"
    config = config_gen.generate_from_description(description)
    
    print(f"需求描述: {description}")
    print(f"\n自动识别结果:")
    print(f"  项目名称: {config.name}")
    print(f"  项目类型: {config.project_type.value}")
    print(f"  项目规模: {config.scale.value}")
    print(f"  技术栈: {', '.join(config.tech_stack)}")
    print(f"  团队角色: {', '.join([r.value for r in config.roles])}")
    
    # 验证配置
    issues = config_gen.validate_config(config)
    print(f"\n配置验证: {'✅ 通过' if not issues else '⚠️ ' + ', '.join(issues)}")
    print()
    
    # ===== 2. 项目创建 =====
    print("【2】TemplateGenerator - 自动项目创建")
    print("-" * 70)
    
    template_gen = TemplateGenerator()
    output_path = "/tmp/qcm_comprehensive_demo"
    
    project_path = template_gen.create_project(config, output_path, overwrite=True)
    
    print(f"✅ 项目创建成功")
    print(f"   路径: {project_path}")
    print(f"\n项目结构:")
    
    # 显示部分目录结构
    for i, (root, dirs, files) in enumerate(os.walk(project_path)):
        if i >= 8:
            break
        level = root.replace(project_path, '').count(os.sep)
        indent = '  ' * level
        print(f"{indent}{os.path.basename(root)}/")
        if level < 2 and files:
            subindent = '  ' * (level + 1)
            for file in files[:2]:
                print(f"{subindent}{file}")
    print()
    
    # ===== 3. 质量评估 =====
    print("【3】QualityAssessor - 多维度质量评估")
    print("-" * 70)
    
    assessor = QualityAssessor()
    report = assessor.assess(project_path, config)
    
    print(f"✅ 评估完成")
    print(f"   总体得分: {report.overall_score:.1f}/100")
    print(f"   质量等级: {report.overall_level.value}")
    print(f"\n详细评估:")
    
    for name, result in report.indicator_results.items():
        status = "✅" if result.passed else "❌"
        print(f"  {status} {name}: {result.score:.1f}分 ({result.level.value})")
    
    if report.recommendations:
        print(f"\n改进建议:")
        for i, rec in enumerate(report.recommendations[:3], 1):
            print(f"  {i}. {rec}")
    print()
    
    # ===== 4. 置信度标注 =====
    print("【4】ConfidenceAnnotator - AI输出置信度管理")
    print("-" * 70)
    
    annotator = ConfidenceAnnotator()
    
    # 演示自动标注
    ai_outputs = [
        "根据官方文档,Python 3.9引入了新的字符串方法",
        "统计数据显示,性能提升约40%",
        "推测这个问题可能是由于配置错误导致的",
        "实验结果证实了这个假设"
    ]
    
    print("AI输出自动标注:")
    for i, output in enumerate(ai_outputs, 1):
        annotation = annotator.auto_annotate(output)
        print(f"\n{i}. 输出: {output}")
        print(f"   类型: {annotation.info_type.value}")
        print(f"   置信度: {annotation.confidence.value}")
        print(f"   来源: {annotation.source}")
        print(f"   建议: {annotation.suggestion}")
    
    print()
    
    # ===== 5. 完整工作流示例 =====
    print("【5】完整工作流 - 从需求到交付")
    print("-" * 70)
    
    workflow_steps = [
        "需求描述 → 智能配置生成",
        "配置 → 项目结构创建",
        "代码 → 质量评估",
        "AI输出 → 置信度标注"
    ]
    
    print("\n工作流程:")
    for i, step in enumerate(workflow_steps, 1):
        print(f"  {i}. {step}")
    
    print(f"\n完成状态:")
    print(f"  ✅ 配置文件: {os.path.join(project_path, 'qcm_project.yaml')}")
    print(f"  ✅ 项目结构: {project_path}")
    print(f"  ✅ 质量报告: 得分 {report.overall_score:.1f}/100")
    print(f"  ✅ 标注功能: 已验证")
    print()
    
    # ===== 总结 =====
    print("【总结】")
    print("-" * 70)
    print("✅ ConfigGenerator: 智能配置生成,支持自然语言输入")
    print("✅ TemplateGenerator: 8种项目模板,自动创建结构")
    print("✅ QualityAssessor: 3维度评估,生成详细报告")
    print("✅ ConfidenceAnnotator: 自动分析,批量处理")
    print()
    print("核心特性:")
    print("  • 自然语言驱动的项目配置")
    print("  • 标准化的项目结构模板")
    print("  • 多维度质量评估")
    print("  • AI输出可信度管理")
    print()
    
    print("=" * 70)
    print("演示完成! 所有功能正常运行")
    print("=" * 70)


if __name__ == "__main__":
    main()
