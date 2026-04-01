#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QCM-AI-DevTools 终极演示

展示完整的工作流编排能力
"""

import sys
sys.path.insert(0, '/workspace/qcm-ai-devtools')

from qcm_tools import (
    DevToolsWorkflow,
    quick_create_project,
    ProjectType
)

def demo_workflow():
    """工作流演示"""
    print("=" * 70)
    print("QCM-AI-DevTools 工作流编排器演示")
    print("=" * 70)
    print()
    
    workflow = DevToolsWorkflow()
    
    # 演示1: 快速启动
    print("【演示1】快速启动模式")
    print("-" * 70)
    
    result = workflow.quick_start("production", "快速API项目")
    
    print(f"✅ 项目创建成功")
    print(f"   路径: {result['project_path']}")
    print(f"   质量得分: {result['quality_score']:.1f}/100")
    print(f"   质量等级: {result['quality_level']}")
    print()
    
    # 演示2: 从描述创建完整项目
    print("【演示2】完整工作流")
    print("-" * 70)
    
    result2 = workflow.create_project_from_description(
        description="开发一个机器学习模型训练平台,使用FastAPI和PostgreSQL",
        output_path="/tmp/workflow_demo"
    )
    
    print(f"状态: {result2['status']}")
    if result2.get('config'):
        print(f"项目: {result2['config'].name}")
        print(f"类型: {result2['config'].project_type.value}")
    if result2.get('quality_report'):
        print(f"质量得分: {result2['quality_report'].overall_score:.1f}/100")
    print()
    
    # 演示3: AI辅助开发循环
    print("【演示3】AI辅助开发循环")
    print("-" * 70)
    
    def mock_ai_generator(prompt):
        """模拟AI代码生成"""
        return f"# AI生成的代码\nprint('Hello from AI!')"
    
    result3 = workflow.ai_assisted_development_cycle(
        requirement="开发简单的REST API",
        ai_code_generator=mock_ai_generator,
        output_path="/tmp/ai_project",
        max_iterations=2
    )
    
    print(f"最终状态: {result3['status']}")
    print(f"迭代次数: {len(result3['iterations'])}")
    print(f"最终得分: {result3['final_quality_score']:.1f}/100")
    print()
    
    # 演示4: 批量创建
    print("【演示4】批量项目创建")
    print("-" * 70)
    
    requirements = [
        "开发用户认证API",
        "开发数据分析工具",
        "开发机器学习模型"
    ]
    
    results = workflow.batch_create_projects(
        requirements,
        "/tmp/batch_projects"
    )
    
    print(f"成功创建 {len(results)} 个项目:")
    for i, r in enumerate(results, 1):
        if r.get('config'):
            score = r['quality_report'].overall_score if r.get('quality_report') else 0
            print(f"  {i}. {r['config'].name[:30]}... (得分: {score:.1f})")
    print()
    
    # 演示5: 便捷函数
    print("【演示5】便捷函数")
    print("-" * 70)
    
    result5 = quick_create_project(
        "开发一个简单的Web服务",
        "/tmp/quick_project"
    )
    
    print(f"✅ 一行代码创建项目成功")
    print(f"   路径: {result5['project_path']}")
    print(f"   得分: {result5['quality_report'].overall_score:.1f}/100")
    print()
    
    # 总结
    print("【总结】")
    print("-" * 70)
    print("✅ 工作流编排器功能验证完成")
    print()
    print("核心功能:")
    print("  • 快速启动模式")
    print("  • 完整工作流(配置→项目→评估→标注)")
    print("  • AI辅助开发循环")
    print("  • 批量项目创建")
    print("  • 内容分析和标注")
    print("  • 便捷函数(一行代码创建项目)")
    print()
    print("=" * 70)


if __name__ == "__main__":
    demo_workflow()
