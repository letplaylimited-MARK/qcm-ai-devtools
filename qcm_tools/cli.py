"""
QCM-AI-DevTools CLI 工具

提供命令行界面，支持：
- 项目创建
- 质量评估
- 意图识别
- 工作流编排
- 交接包管理
"""

try:
    import typer
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.syntax import Syntax
    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    print("警告: 请安装 typer 和 rich 以使用 CLI")
    print("pip install typer rich")

import os
from typing import Optional, List
from pathlib import Path

# 主应用
app = typer.Typer(
    name="qcm",
    help="QCM-AI-DevTools - AI 驱动的开发工具平台",
    add_completion=False
)

# 子应用
handoff_app = typer.Typer(help="交接包管理")
app.add_typer(handoff_app, name="handoff")

if HAS_RICH:
    console = Console()


def get_workflow():
    """获取工作流实例"""
    from qcm_tools import DevToolsWorkflow
    return DevToolsWorkflow()


def get_navigator():
    """获取导航器实例"""
    from qcm_tools.skills import Navigator
    return Navigator()


@app.command()
def create(
    description: str = typer.Argument(..., help="项目描述"),
    output: str = typer.Option("./project", "--output", "-o", help="输出路径"),
    no_assess: bool = typer.Option(False, "--no-assess", help="跳过质量评估")
):
    """
    创建新项目
    
    示例:
        qcm create "开发一个API系统"
        qcm create "开发情感分析API" -o ./my-project
    """
    if not HAS_RICH:
        print(f"创建项目: {description}")
        workflow = get_workflow()
        result = workflow.create_project_from_description(
            description, 
            output,
            auto_assess=not no_assess
        )
        print(f"项目已创建: {result.get('project_path')}")
        return
    
    console.print(Panel(f"[bold blue]创建项目[/bold blue]", expand=False))
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("分析需求...", total=None)
        
        workflow = get_workflow()
        
        progress.update(task, description="生成配置...")
        result = workflow.create_project_from_description(
            description,
            output,
            auto_assess=not no_assess
        )
    
    if result['status'] == 'completed':
        console.print("\n[bold green]✓ 项目创建成功！[/bold green]")
        
        # 显示配置信息
        if result.get('config'):
            config = result['config']
            console.print(f"\n[bold]项目信息:[/bold]")
            console.print(f"  名称: {config.name}")
            console.print(f"  类型: {config.project_type.value}")
            console.print(f"  规模: {config.scale.value}")
            if config.tech_stack:
                console.print(f"  技术栈: {', '.join(config.tech_stack)}")
        
        # 显示路径
        if result.get('project_path'):
            console.print(f"\n[bold]项目路径:[/bold] {result['project_path']}")
        
        # 显示质量评估
        if result.get('quality_report'):
            report = result['quality_report']
            console.print(f"\n[bold]质量评估:[/bold]")
            
            table = Table(show_header=True, header_style="bold")
            table.add_column("指标")
            table.add_column("得分")
            table.add_column("状态")
            
            for name, indicator in report.indicator_results.items():
                status = "✓" if indicator.passed else "✗"
                status_style = "green" if indicator.passed else "red"
                table.add_row(
                    name,
                    f"{indicator.score:.1f}",
                    f"[{status_style}]{status}[/{status_style}]"
                )
            
            console.print(table)
            console.print(f"\n[bold]总体得分:[/bold] {report.overall_score:.1f}/100")
            console.print(f"[bold]质量等级:[/bold] {report.overall_level.value}")
    else:
        console.print(f"\n[bold red]✗ 项目创建失败[/bold red]")
        if result.get('errors'):
            for error in result['errors']:
                console.print(f"  错误: {error}")


@app.command()
def assess(
    path: str = typer.Argument(..., help="项目路径"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="显示详细信息")
):
    """
    评估项目质量
    
    示例:
        qcm assess ./my-project
        qcm assess ./my-project -v
    """
    if not HAS_RICH:
        print(f"评估项目: {path}")
        from qcm_tools import QualityAssessor
        assessor = QualityAssessor()
        report = assessor.assess(path)
        print(f"总体得分: {report.overall_score:.1f}/100")
        return
    
    console.print(Panel(f"[bold blue]质量评估[/bold blue]", expand=False))
    
    from qcm_tools import QualityAssessor
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("评估中...", total=None)
        
        assessor = QualityAssessor()
        report = assessor.assess(path)
    
    console.print(f"\n[bold]项目:[/bold] {path}")
    
    # 评估结果表格
    table = Table(show_header=True, header_style="bold")
    table.add_column("指标", style="cyan")
    table.add_column("得分", justify="right")
    table.add_column("等级", justify="center")
    table.add_column("状态", justify="center")
    
    for name, indicator in report.indicator_results.items():
        status = "✓" if indicator.passed else "✗"
        status_style = "green" if indicator.passed else "red"
        
        table.add_row(
            name,
            f"{indicator.score:.1f}",
            indicator.level.value,
            f"[{status_style}]{status}[/{status_style}]"
        )
    
    console.print(table)
    
    # 总体结果
    overall_style = "green" if report.overall_score >= 80 else "yellow" if report.overall_score >= 60 else "red"
    console.print(f"\n[bold]总体得分:[/bold] [{overall_style}]{report.overall_score:.1f}/100[/{overall_style}]")
    console.print(f"[bold]质量等级:[/bold] {report.overall_level.value}")
    
    # 建议
    if report.recommendations and verbose:
        console.print(f"\n[bold]改进建议:[/bold]")
        for i, rec in enumerate(report.recommendations, 1):
            console.print(f"  {i}. {rec}")


@app.command()
def navigate(
    query: str = typer.Argument(..., help="自然语言查询"),
    json_output: bool = typer.Option(False, "--json", help="JSON 格式输出")
):
    """
    意图识别和路由推荐
    
    示例:
        qcm navigate "开发一个API系统"
        qcm navigate "找个开源的NLP库"
    """
    navigator = get_navigator()
    
    if not HAS_RICH:
        analysis = navigator.analyze_intent(query)
        print(f"意图类型: {analysis.intent_type.value}")
        print(f"置信度: {analysis.confidence:.0%}")
        print(f"推荐路由: {analysis.recommended_skill}")
        return
    
    console.print(Panel(f"[bold blue]意图识别[/bold blue]", expand=False))
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("分析中...", total=None)
        handoff = navigator.generate_handoff(query)
    
    if json_output:
        import json
        console.print_json(json.dumps(handoff.payload, indent=2, ensure_ascii=False))
        return
    
    # 显示结果
    console.print(f"\n[bold]意图类型:[/bold] {handoff.payload['intent_type']}")
    console.print(f"[bold]置信度:[/bold] {handoff.payload['confidence_score']:.0%}")
    console.print(f"[bold]推荐路由:[/bold] {handoff.to_skill}")
    console.print(f"[bold]路由原因:[/bold] {handoff.payload.get('routing_reason', 'N/A')}")
    
    # 显示项目摘要
    if handoff.payload.get('project_summary'):
        console.print(f"\n[bold]项目摘要:[/bold]")
        console.print(f"  {handoff.payload['project_summary']}")
    
    # 显示技术栈
    if handoff.payload.get('tech_stack_preference'):
        console.print(f"\n[bold]技术栈:[/bold] {', '.join(handoff.payload['tech_stack_preference'])}")
    
    # 显示澄清问题（如果有）
    if handoff.payload.get('clarification_questions'):
        console.print(f"\n[bold yellow]需要澄清:[/bold yellow]")
        for i, q in enumerate(handoff.payload['clarification_questions'], 1):
            console.print(f"  {i}. {q}")


@app.command()
def workflow(
    requirement: str = typer.Argument(..., help="需求描述"),
    output: str = typer.Option("./project", "--output", "-o", help="输出路径"),
    validate: bool = typer.Option(True, "--validate/--no-validate", help="是否验证")
):
    """
    执行完整工作流
    
    示例:
        qcm workflow "开发一个API系统"
        qcm workflow "开发情感分析API" -o ./my-project
    """
    if not HAS_RICH:
        print(f"执行工作流: {requirement}")
        wf = get_workflow()
        result = wf.start_from_natural_language(requirement, output)
        print(f"状态: {result['status']}")
        return
    
    console.print(Panel(f"[bold blue]完整工作流[/bold blue]", expand=False))
    
    wf = get_workflow()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("导航分析...", total=None)
        
        result = wf.start_from_natural_language(
            requirement,
            output,
            auto_execute=True
        )
    
    if result['status'] == 'completed':
        console.print("\n[bold green]✓ 工作流完成！[/bold green]")
        
        # 导航分析
        if result.get('navigator_analysis'):
            nav = result['navigator_analysis']
            console.print(f"\n[bold]导航分析:[/bold]")
            console.print(f"  意图: {nav['intent_type']}")
            console.print(f"  置信度: {nav['confidence']:.0%}")
            console.print(f"  路由: {nav['recommended_skill']}")
        
        # 执行结果
        if result.get('execution_result'):
            exec_result = result['execution_result']
            if exec_result.get('quality_report'):
                report = exec_result['quality_report']
                console.print(f"\n[bold]质量评估:[/bold]")
                console.print(f"  得分: {report.overall_score:.1f}/100")
                console.print(f"  等级: {report.overall_level.value}")
    else:
        console.print(f"\n[bold red]✗ 工作流失败[/bold red]")
        if result.get('error'):
            console.print(f"  错误: {result['error']}")


# ===== 交接包管理命令 =====

@handoff_app.command("list")
def handoff_list():
    """列出所有交接包"""
    if not HAS_RICH:
        print("交接包链路:")
        print("  无交接包记录")
        return
    
    console.print(Panel(f"[bold blue]交接包链路[/bold blue]", expand=False))
    
    from qcm_tools.handoff import HandoffManager
    manager = HandoffManager()
    
    chain = manager.get_chain()
    
    if not chain:
        console.print("\n[yellow]无交接包记录[/yellow]")
        return
    
    table = Table(show_header=True, header_style="bold")
    table.add_column("#", justify="right")
    table.add_column("从")
    table.add_column("到")
    table.add_column("类型")
    table.add_column("创建时间")
    
    for i, handoff in enumerate(chain, 1):
        table.add_row(
            str(i),
            handoff.from_skill,
            handoff.to_skill,
            handoff.handoff_type or "N/A",
            handoff.created_at
        )
    
    console.print(table)


@handoff_app.command("export")
def handoff_export(
    format: str = typer.Option("yaml", "--format", "-f", help="输出格式 (yaml/json)"),
    output_file: Optional[str] = typer.Option(None, "--output", "-o", help="输出文件")
):
    """导出交接包链路"""
    from qcm_tools.handoff import HandoffManager
    
    manager = HandoffManager()
    
    if format not in ["yaml", "json"]:
        if HAS_RICH:
            console.print("[red]错误: 格式必须是 yaml 或 json[/red]")
        else:
            print("错误: 格式必须是 yaml 或 json")
        raise typer.Exit(1)
    
    exported = manager.export_session(format=format)
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(exported)
        if HAS_RICH:
            console.print(f"[green]已导出到: {output_file}[/green]")
        else:
            print(f"已导出到: {output_file}")
    else:
        print(exported)


@handoff_app.command("clear")
def handoff_clear():
    """清空交接包链路"""
    from qcm_tools.handoff import HandoffManager
    
    manager = HandoffManager()
    manager.clear()
    
    if HAS_RICH:
        console.print("[green]交接包链路已清空[/green]")
    else:
        print("交接包链路已清空")


# ===== 其他命令 =====

@app.command()
def version():
    """显示版本信息"""
    from qcm_tools import __version__
    
    if HAS_RICH:
        console.print(Panel(
            f"[bold]QCM-AI-DevTools[/bold]\n"
            f"版本: {__version__}\n"
            f"定位: AI 驱动的开发工具平台\n"
            f"目标: 团队协作 + ai-skill-system 对接",
            title="关于",
            expand=False
        ))
    else:
        print(f"QCM-AI-DevTools v{__version__}")


@app.command()
def info():
    """显示项目信息"""
    if not HAS_RICH:
        print("QCM-AI-DevTools - AI 驱动的开发工具平台")
        print("目标用户: 团队")
        print("核心价值: 与 ai-skill-system 无缝对接")
        return
    
    console.print(Panel(
        "[bold]QCM-AI-DevTools[/bold]\n\n"
        "[bold]目标用户:[/bold] 团队\n"
        "[bold]核心价值:[/bold] 与 ai-skill-system 无缝对接\n"
        "[bold]使用模式:[/bold]\n"
        "  • 独立使用: 团队开发工具集\n"
        "  • 对接使用: ai-skill-system 代码化引擎\n\n"
        "[bold]核心工具:[/bold]\n"
        "  • ConfigGenerator: 智能配置生成\n"
        "  • TemplateGenerator: 项目模板创建\n"
        "  • QualityAssessor: 质量评估\n"
        "  • ConfidenceAnnotator: 置信度标注\n"
        "  • Navigator: 意图识别\n"
        "  • HandoffManager: 交接包管理",
        title="项目信息",
        expand=False
    ))


if __name__ == "__main__":
    app()
