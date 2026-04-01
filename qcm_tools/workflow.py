"""
DevToolsWorkflow 工作流编排器实现

整合所有工具,提供完整的端到端工作流
"""

import os
from typing import Dict, List, Optional, Callable
from pathlib import Path
from qcm_tools.config import ConfigGenerator, ProjectConfig
from qcm_tools.template import TemplateGenerator
from qcm_tools.quality import QualityAssessor, QualityReport
from qcm_tools.confidence import ConfidenceAnnotator, ConfidenceAnnotation
from qcm_tools.shared.enums import ProjectType
from qcm_tools.handoff import HandoffManager, HandoffPackage
from qcm_tools.skills.navigator import Navigator


class DevToolsWorkflow:
    """
    开发工具工作流编排器
    
    整合ConfigGenerator、TemplateGenerator、QualityAssessor、ConfidenceAnnotator,
    提供完整的端到端工作流。
    
    Example:
        >>> from qcm_tools import DevToolsWorkflow
        >>> 
        >>> workflow = DevToolsWorkflow()
        >>> 
        >>> # 从描述创建完整项目
        >>> result = workflow.create_project_from_description(
        ...     "开发一个用户管理API系统",
        ...     output_path="./my_project"
        ... )
        >>> 
        >>> # AI辅助开发循环
        >>> result = workflow.ai_assisted_development(
        ...     requirement="开发微服务API",
        ...     ai_code_generator=my_ai_function
        ... )
    """
    
    def __init__(self, use_handoff: bool = True):
        """
        初始化工作流编排器
        
        Args:
            use_handoff: 是否启用交接包机制（默认启用）
        """
        self.config_generator = ConfigGenerator()
        self.template_generator = TemplateGenerator()
        self.quality_assessor = QualityAssessor()
        self.confidence_annotator = ConfidenceAnnotator()
        self.navigator = Navigator()
        self.handoff_manager = HandoffManager() if use_handoff else None
    
    def create_project_from_description(
        self,
        description: str,
        output_path: str,
        auto_assess: bool = True
    ) -> Dict:
        """
        从描述创建完整项目
        
        完整流程:
        1. 从描述生成配置
        2. 创建项目结构
        3. 质量评估
        4. 生成置信度标注
        
        Args:
            description: 项目描述
            output_path: 输出路径
            auto_assess: 是否自动质量评估
            
        Returns:
            包含所有结果的字典
            
        Example:
            >>> workflow = DevToolsWorkflow()
            >>> result = workflow.create_project_from_description(
            ...     "开发一个API系统,使用FastAPI",
            ...     "./my_project"
            ... )
            >>> print(result['project_path'])
            >>> print(result['quality_report'].overall_score)
        """
        result = {
            'config': None,
            'project_path': None,
            'quality_report': None,
            'confidence_annotation': None,
            'status': 'initialized',
            'errors': []
        }
        
        try:
            # 步骤1: 生成配置
            result['status'] = 'generating_config'
            config = self.config_generator.generate_from_description(description)
            
            # 验证配置
            issues = self.config_generator.validate_config(config)
            if issues:
                result['warnings'] = issues
            
            result['config'] = config
            
            # 步骤2: 创建项目
            result['status'] = 'creating_project'
            project_path = self.template_generator.create_project(
                config, 
                output_path
            )
            result['project_path'] = project_path
            
            # 步骤3: 质量评估
            if auto_assess:
                result['status'] = 'assessing_quality'
                quality_report = self.quality_assessor.assess(project_path, config)
                result['quality_report'] = quality_report
            
            # 步骤4: 标注配置置信度
            result['status'] = 'annotating'
            annotation = self.confidence_annotator.annotate(
                content=config.to_yaml(),
                info_type='结论',
                source='AI生成配置'
            )
            result['confidence_annotation'] = annotation
            
            result['status'] = 'completed'
            
        except Exception as e:
            result['status'] = 'failed'
            result['errors'].append(str(e))
        
        return result
    
    def ai_assisted_development_cycle(
        self,
        requirement: str,
        ai_code_generator: Callable[[str], str],
        output_path: str = "./ai_project",
        max_iterations: int = 3,
        quality_threshold: float = 80.0
    ) -> Dict:
        """
        AI辅助开发循环
        
        完整流程:
        1. 生成项目配置
        2. AI生成代码
        3. 质量评估
        4. 如果质量不达标,迭代改进
        
        Args:
            requirement: 需求描述
            ai_code_generator: AI代码生成函数
            output_path: 输出路径
            max_iterations: 最大迭代次数
            quality_threshold: 质量阈值
            
        Returns:
            开发循环结果
            
        Example:
            >>> def my_ai(prompt):
            ...     # 调用AI生成代码
            ...     return "generated code"
            >>> 
            >>> result = workflow.ai_assisted_development_cycle(
            ...     requirement="开发用户API",
            ...     ai_code_generator=my_ai
            ... )
        """
        result = {
            'iterations': [],
            'final_config': None,
            'final_project_path': None,
            'final_code': None,
            'final_quality_score': 0.0,
            'status': 'initialized'
        }
        
        try:
            # 步骤1: 生成配置
            result['status'] = 'generating_config'
            config = self.config_generator.generate_from_description(requirement)
            result['final_config'] = config
            
            # 步骤2: 创建项目结构
            result['status'] = 'creating_project'
            project_path = self.template_generator.create_project(
                config, 
                output_path
            )
            result['final_project_path'] = project_path
            
            # 步骤3: AI生成代码
            result['status'] = 'generating_code'
            code = ai_code_generator(requirement)
            result['final_code'] = code
            
            # 步骤4: 质量评估和迭代改进
            iteration = 0
            while iteration < max_iterations:
                iteration += 1
                result['status'] = f'iteration_{iteration}'
                
                # 评估质量
                quality_report = self.quality_assessor.assess(project_path, config)
                score = quality_report.overall_score
                
                iteration_result = {
                    'iteration': iteration,
                    'score': score,
                    'recommendations': quality_report.recommendations
                }
                result['iterations'].append(iteration_result)
                
                # 如果质量达标,退出循环
                if score >= quality_threshold:
                    result['final_quality_score'] = score
                    break
                
                # 如果质量不达标,让AI改进
                if iteration < max_iterations:
                    improvement_prompt = f"""
                    代码质量评分: {score}/100
                    问题: {', '.join(quality_report.recommendations)}
                    请改进代码以达到{quality_threshold}分。
                    """
                    code = ai_code_generator(improvement_prompt)
                    result['final_code'] = code
            
            result['final_quality_score'] = score if 'score' in locals() else 0.0
            result['status'] = 'completed'
            
        except Exception as e:
            result['status'] = 'failed'
            result['errors'] = [str(e)]
        
        return result
    
    def batch_create_projects(
        self,
        requirements: List[str],
        output_base_path: str = "./projects"
    ) -> List[Dict]:
        """
        批量创建项目
        
        Args:
            requirements: 需求描述列表
            output_base_path: 输出基础路径
            
        Returns:
            项目结果列表
            
        Example:
            >>> requirements = [
            ...     "开发用户API系统",
            ...     "开发数据分析工具",
            ...     "开发机器学习模型"
            ... ]
            >>> results = workflow.batch_create_projects(requirements)
        """
        results = []
        
        for i, requirement in enumerate(requirements, 1):
            print(f"处理项目 {i}/{len(requirements)}: {requirement[:50]}...")
            
            output_path = os.path.join(output_base_path, f"project_{i}")
            
            result = self.create_project_from_description(
                description=requirement,
                output_path=output_path,
                auto_assess=True
            )
            
            results.append(result)
        
        return results
    
    def analyze_and_annotate_content(
        self,
        content: str,
        context: Optional[str] = None
    ) -> Dict:
        """
        分析和标注内容
        
        完整流程:
        1. 置信度标注
        2. 验证标注
        3. 生成建议
        
        Args:
            content: 待分析内容
            context: 上下文信息
            
        Returns:
            分析结果
            
        Example:
            >>> result = workflow.analyze_and_annotate_content(
            ...     "根据官方文档,这个方案可行"
            ... )
        """
        result = {
            'annotation': None,
            'validation': None,
            'suggestions': []
        }
        
        # 自动标注
        annotation = self.confidence_annotator.auto_annotate(content)
        result['annotation'] = annotation
        
        # 验证标注
        validation = self.confidence_annotator.validate_annotation(annotation)
        result['validation'] = validation
        
        # 生成建议
        if validation.get('warnings'):
            result['suggestions'].extend(validation['warnings'])
        if validation.get('suggestions'):
            result['suggestions'].extend(validation['suggestions'])
        
        return result
    
    def quick_start(
        self,
        project_type: str = "production",
        name: str = "quick_project",
        output_path: str = "./quick_project"
    ) -> Dict:
        """
        快速启动 - 简化的工作流
        
        Args:
            project_type: 项目类型(production/research/teaching/personal)
            name: 项目名称
            output_path: 输出路径
            
        Returns:
            快速启动结果
            
        Example:
            >>> result = workflow.quick_start("production", "my_api")
        """
        # 映射项目类型
        type_map = {
            'production': ProjectType.PRODUCTION,
            'research': ProjectType.RESEARCH,
            'teaching': ProjectType.TEACHING,
            'personal': ProjectType.PERSONAL
        }
        
        ptype = type_map.get(project_type.lower(), ProjectType.PERSONAL)
        
        # 生成配置
        config = self.config_generator.generate_from_type(
            project_type=ptype,
            name=name,
            description=f"快速启动的{ptype.value}项目"
        )
        
        # 创建项目
        project_path = self.template_generator.create_project(config, output_path)
        
        # 快速评估
        report = self.quality_assessor.assess(project_path, config)
        
        return {
            'config': config,
            'project_path': project_path,
            'quality_score': report.overall_score,
            'quality_level': report.overall_level.value
        }
    
    def get_workflow_status(self, result: Dict) -> str:
        """
        获取工作流状态描述
        
        Args:
            result: 工作流结果
            
        Returns:
            状态描述字符串
        """
        status = result.get('status', 'unknown')
        
        status_descriptions = {
            'initialized': '工作流已初始化',
            'generating_config': '正在生成配置',
            'creating_project': '正在创建项目',
            'assessing_quality': '正在评估质量',
            'annotating': '正在生成标注',
            'completed': '工作流完成',
            'failed': '工作流失败'
        }
        
        desc = status_descriptions.get(status, f'未知状态: {status}')
        
        if result.get('errors'):
            desc += f"\n错误: {', '.join(result['errors'])}"
        
        return desc
    
    def generate_summary_report(self, result: Dict) -> str:
        """
        生成总结报告
        
        Args:
            result: 工作流结果
            
        Returns:
            Markdown格式的总结报告
        """
        lines = [
            "# QCM-AI-DevTools 工作流总结报告",
            "",
            f"**状态**: {result.get('status', 'unknown')}",
            ""
        ]
        
        # 配置信息
        if result.get('config'):
            config = result['config']
            lines.extend([
                "## 项目配置",
                "",
                f"- **项目名称**: {config.name}",
                f"- **项目类型**: {config.project_type.value}",
                f"- **项目规模**: {config.scale.value}",
                f"- **技术栈**: {', '.join(config.tech_stack) if config.tech_stack else '未指定'}",
                ""
            ])
        
        # 项目路径
        if result.get('project_path'):
            lines.extend([
                "## 项目路径",
                "",
                f"`{result['project_path']}`",
                ""
            ])
        
        # 质量评估
        if result.get('quality_report'):
            report = result['quality_report']
            lines.extend([
                "## 质量评估",
                "",
                f"- **总体得分**: {report.overall_score:.1f}/100",
                f"- **质量等级**: {report.overall_level.value}",
                ""
            ])
            
            if report.indicator_results:
                lines.append("### 详细指标")
                lines.append("")
                for name, r in report.indicator_results.items():
                    status = "✅" if r.passed else "❌"
                    lines.append(f"- {status} {name}: {r.score:.1f}分")
                lines.append("")
        
        # 错误信息
        if result.get('errors'):
            lines.extend([
                "## 错误信息",
                ""
            ])
            for error in result['errors']:
                lines.append(f"- ❌ {error}")
            lines.append("")
        
        # 建议
        if result.get('warnings'):
            lines.extend([
                "## 建议",
                ""
            ])
            for warning in result['warnings']:
                lines.append(f"- 💡 {warning}")
            lines.append("")
        
        return "\n".join(lines)
    
    # ===== 新增：Navigator 集成方法 =====
    
    def start_from_natural_language(
        self,
        user_input: str,
        output_path: str = "./project",
        auto_execute: bool = True
    ) -> Dict:
        """
        从自然语言开始工作流
        
        完整流程：
        1. Navigator 分析意图
        2. 根据意图路由到相应工具
        3. 执行工作流
        4. 生成交接包
        
        Args:
            user_input: 自然语言输入
            output_path: 输出路径
            auto_execute: 是否自动执行
            
        Returns:
            工作流结果
            
        Example:
            >>> workflow = DevToolsWorkflow()
            >>> result = workflow.start_from_natural_language(
            ...     "开发一个情感分析API系统"
            ... )
        """
        result = {
            'navigator_analysis': None,
            'handoff': None,
            'execution_result': None,
            'status': 'initialized'
        }
        
        try:
            # Step 1: Navigator 分析意图
            result['status'] = 'analyzing_intent'
            handoff = self.navigator.generate_handoff(user_input)
            result['handoff'] = handoff
            result['navigator_analysis'] = {
                'intent_type': handoff.payload.get('intent_type'),
                'confidence': handoff.payload.get('confidence_score'),
                'recommended_skill': handoff.to_skill
            }
            
            # 存储交接包
            if self.handoff_manager:
                self.handoff_manager.save(handoff)
            
            # Step 2: 自动执行
            if auto_execute:
                result['status'] = 'executing'
                execution_result = self._execute_from_handoff(handoff, output_path)
                result['execution_result'] = execution_result
            
            result['status'] = 'completed'
            
        except Exception as e:
            result['status'] = 'failed'
            result['error'] = str(e)
        
        return result
    
    def _execute_from_handoff(
        self,
        handoff: HandoffPackage,
        output_path: str
    ) -> Dict:
        """根据交接包执行相应工作流"""
        intent_type = handoff.payload.get('intent_type')
        
        if intent_type in ['build_custom', 'use_existing_skill']:
            # 项目开发工作流
            return self.create_project_from_description(
                description=handoff.payload.get('project_summary', ''),
                output_path=output_path
            )
        elif intent_type == 'test_validate':
            # 质量验收工作流
            return self.validate_project(output_path)
        elif intent_type == 'find_open_source':
            # 技术选型工作流
            return {
                'type': 'tech_selection',
                'project_summary': handoff.payload.get('project_summary'),
                'tech_stack': handoff.payload.get('tech_stack_preference', [])
            }
        else:
            return {'type': 'unknown', 'intent': intent_type}
    
    def validate_project(
        self,
        project_path: str,
        config: ProjectConfig = None
    ) -> Dict:
        """
        验证项目质量
        
        完整流程：
        1. 质量评估
        2. 生成验收报告
        3. 创建验收交接包
        
        Args:
            project_path: 项目路径
            config: 项目配置（可选）
            
        Returns:
            验收结果
        """
        result = {
            'quality_report': None,
            'verdict': None,
            'handoff': None,
            'status': 'initialized'
        }
        
        try:
            # 质量评估
            result['status'] = 'assessing'
            quality_report = self.quality_assessor.assess(project_path, config)
            result['quality_report'] = quality_report
            
            # 发布决策
            result['status'] = 'deciding'
            verdict = self._make_release_decision(quality_report)
            result['verdict'] = verdict
            
            # 创建验收交接包
            if self.handoff_manager:
                from qcm_tools.handoff.models import create_handoff_f
                handoff = create_handoff_f(
                    verdict=verdict,
                    overall_score=quality_report.overall_score,
                    test_results={'indicators': len(quality_report.indicator_results)},
                    risk_assessment={'recommendations': quality_report.recommendations[:3]},
                    upstream_feedback={'improvements': quality_report.recommendations}
                )
                self.handoff_manager.save(handoff)
                result['handoff'] = handoff
            
            result['status'] = 'completed'
            
        except Exception as e:
            result['status'] = 'failed'
            result['error'] = str(e)
        
        return result
    
    def _make_release_decision(self, report: QualityReport) -> str:
        """根据质量报告做出发布决策"""
        score = report.overall_score
        
        # 统计失败的指标
        failed_count = sum(
            1 for r in report.indicator_results.values() 
            if not r.passed
        )
        
        if score >= 80 and failed_count == 0:
            return 'PASS'
        elif score >= 70 and failed_count <= 2:
            return 'CONDITIONAL_PASS'
        else:
            return 'FAIL'
    
    def get_handoff_chain(self) -> List[HandoffPackage]:
        """获取完整的交接包链路"""
        if self.handoff_manager:
            return self.handoff_manager.get_chain()
        return []
    
    def export_handoff_chain(self, format: str = "yaml") -> str:
        """导出交接包链路"""
        if self.handoff_manager:
            return self.handoff_manager.export_session(format=format)
        return ""
    
    # ===== 新增：AI 辅助开发增强方法 =====
    
    def ai_development_with_navigation(
        self,
        requirement: str,
        ai_client = None,
        output_path: str = "./ai_project"
    ) -> Dict:
        """
        AI 辅助开发（带导航）
        
        完整流程：
        1. Navigator 分析需求
        2. 生成项目配置
        3. 创建项目结构
        4. （可选）AI 生成代码
        5. 质量验收
        6. 生成交接包
        
        Args:
            requirement: 需求描述
            ai_client: AI 客户端（可选）
            output_path: 输出路径
            
        Returns:
            开发结果
        """
        result = {
            'navigation': None,
            'config': None,
            'project_path': None,
            'quality_report': None,
            'verdict': None,
            'handoffs': [],
            'status': 'initialized'
        }
        
        try:
            # Step 1: Navigator 分析
            result['status'] = 'navigating'
            nav_handoff = self.navigator.generate_handoff(requirement)
            result['navigation'] = nav_handoff
            result['handoffs'].append(('navigator', nav_handoff))
            
            if self.handoff_manager:
                self.handoff_manager.save(nav_handoff)
            
            # Step 2: 生成配置
            result['status'] = 'configuring'
            config = self.config_generator.generate_from_description(requirement)
            result['config'] = config
            
            # Step 3: 创建项目
            result['status'] = 'creating'
            project_path = self.template_generator.create_project(config, output_path)
            result['project_path'] = project_path
            
            # Step 4: 质量验收
            result['status'] = 'validating'
            validation_result = self.validate_project(project_path, config)
            result['quality_report'] = validation_result.get('quality_report')
            result['verdict'] = validation_result.get('verdict')
            
            if validation_result.get('handoff'):
                result['handoffs'].append(('validator', validation_result['handoff']))
            
            result['status'] = 'completed'
            
        except Exception as e:
            result['status'] = 'failed'
            result['error'] = str(e)
        
        return result


# 便捷函数
def quick_create_project(description: str, output_path: str = "./project") -> Dict:
    """
    快速创建项目(便捷函数)
    
    Args:
        description: 项目描述
        output_path: 输出路径
        
    Returns:
        项目结果
        
    Example:
        >>> from qcm_tools import quick_create_project
        >>> result = quick_create_project("开发一个API系统")
    """
    workflow = DevToolsWorkflow()
    return workflow.create_project_from_description(description, output_path)


__all__ = ['DevToolsWorkflow', 'quick_create_project']
