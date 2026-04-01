"""
Skill 04 · Planner（执行规划官）

职责: 将 SOP 工程包转化为人可执行的分阶段操作手册
能力边界: 不写代码，不做技术决策，只负责执行规划
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
import yaml
from datetime import datetime

from qcm_tools.handoff.models import HandoffPackage
from qcm_tools.config.models import ProjectConfig


class PhaseStatus(Enum):
    """阶段状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskPriority(Enum):
    """任务优先级"""
    P0 = "P0"  # 关键路径
    P1 = "P1"  # 重要任务
    P2 = "P2"  # 一般任务
    P3 = "P3"  # 可选任务


@dataclass
class Step:
    """
    步骤（Step）- 最小执行单元
    
    编号规则: P{阶段号}-T{任务号}-S{步骤号}
    例如: P1-T2-S3 = 第1阶段 / 第2任务 / 第3步骤
    """
    id: str  # P1-T2-S3 格式
    description: str  # 步骤描述（动词开头）
    tool: str  # 工具：终端/编辑器/浏览器等
    operation: str  # 具体操作命令或步骤
    expected_result: str  # 预期结果
    verification: str  # 验证方式
    estimated_time: int  # 预估时间（分钟）
    dependencies: List[str] = field(default_factory=list)  # 前置步骤ID
    
    # PERT 三点估算
    optimistic_time: Optional[int] = None  # 乐观时间
    normal_time: Optional[int] = None  # 正常时间
    pessimistic_time: Optional[int] = None  # 悲观时间
    
    # 幻觉防护
    needs_user_verification: bool = False  # 是否需要用户核实
    verification_note: str = ""  # 核实说明
    
    # 错误处理
    error_handling: str = ""  # 错误处理方案
    rollback: str = ""  # 回滚步骤


@dataclass
class Task:
    """
    任务（Task）- 由多个步骤组成
    
    编号规则: P{阶段号}-T{任务号}
    例如: P1-T2 = 第1阶段 / 第2任务
    """
    id: str  # P1-T2 格式
    name: str  # 任务名称
    description: str  # 任务描述
    steps: List[Step] = field(default_factory=list)
    priority: TaskPriority = TaskPriority.P1
    estimated_time: int = 0  # 总时间（分钟）
    
    def calculate_total_time(self):
        """计算任务总时间"""
        self.estimated_time = sum(step.estimated_time for step in self.steps)
        return self.estimated_time


@dataclass
class Phase:
    """
    阶段（Phase）- 由多个任务组成
    
    编号规则: P{阶段号}
    例如: P1 = 第1阶段
    """
    id: str  # P1 格式
    name: str  # 阶段名称
    description: str  # 阶段描述
    tasks: List[Task] = field(default_factory=list)
    checkpoint: str = ""  # 检查点描述
    estimated_time: int = 0  # 总时间（分钟）
    status: PhaseStatus = PhaseStatus.PENDING
    
    def calculate_total_time(self):
        """计算阶段总时间"""
        for task in self.tasks:
            task.calculate_total_time()
        self.estimated_time = sum(task.estimated_time for task in self.tasks)
        return self.estimated_time


@dataclass
class Risk:
    """风险项"""
    id: str
    description: str  # 风险描述
    severity: str  # 严重程度: high/medium/low
    mitigation: str  # 缓解措施
    phase: str  # 涉及阶段


@dataclass
class Checkpoint:
    """检查点"""
    id: str
    phase_id: str
    description: str  # 检查点描述
    verification_command: str  # 验证命令
    expected_output: str  # 预期输出


@dataclass
class ExecutionPlan:
    """
    执行计划 - 完整的操作手册
    
    包含:
    - Phase/Task/Step 三层结构
    - 总时间估算
    - 风险识别
    - 检查点
    """
    project_name: str
    description: str
    phases: List[Phase] = field(default_factory=list)
    total_time: int = 0  # 总时间（分钟）
    risks: List[Risk] = field(default_factory=list)
    checkpoints: List[Checkpoint] = field(default_factory=list)
    
    # 环境信息
    target_environment: str = ""
    prerequisites: List[str] = field(default_factory=list)
    
    # 假设与限制
    assumptions: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)
    
    # 断点恢复
    recovery_points: Dict[str, str] = field(default_factory=dict)
    
    def calculate_total_time(self):
        """计算总时间"""
        for phase in self.phases:
            phase.calculate_total_time()
        self.total_time = sum(phase.estimated_time for phase in self.phases)
        return self.total_time
    
    def to_markdown(self) -> str:
        """
        生成 Markdown 格式的操作手册
        
        输出格式:
        1. 项目概览
        2. 环境配置
        3. 各阶段手册
        4. FAQ
        5. 断点恢复指南
        """
        md = f"""# {self.project_name} · 执行操作手册

## 一、项目概览

**项目描述**: {self.description}

**总估时**: {self.total_time} 分钟 (约 {self.total_time / 60:.1f} 小时) [估算，请根据实际调整]

**阶段数量**: {len(self.phases)}

**前置条件**:
"""
        for prereq in self.prerequisites:
            md += f"- {prereq}\n"
        
        md += "\n**环境要求**:\n"
        md += f"- 目标环境: {self.target_environment}\n"
        
        md += "\n**假设条件**:\n"
        for assumption in self.assumptions:
            md += f"- {assumption}\n"
        
        # 各阶段手册
        md += "\n## 二、执行手册\n\n"
        
        for phase in self.phases:
            md += f"### {phase.id}: {phase.name}\n\n"
            md += f"**描述**: {phase.description}\n\n"
            md += f"**估时**: {phase.estimated_time} 分钟\n\n"
            
            if phase.checkpoint:
                md += f"**检查点**: {phase.checkpoint}\n\n"
            
            for task in phase.tasks:
                md += f"#### {task.id}: {task.name}\n\n"
                md += f"**描述**: {task.description}\n\n"
                md += f"**估时**: {task.estimated_time} 分钟\n\n"
                
                for step in task.steps:
                    md += f"##### {step.id}: {step.description}\n\n"
                    md += f"- **工具**: {step.tool}\n"
                    md += f"- **操作**: {step.operation}\n"
                    md += f"- **预期结果**: {step.expected_result}\n"
                    md += f"- **验证**: {step.verification}\n"
                    md += f"- **估时**: {step.estimated_time} 分钟"
                    
                    if step.needs_user_verification:
                        md += f" [需用户核实: {step.verification_note}]"
                    
                    md += "\n"
                    
                    if step.error_handling:
                        md += f"- **错误处理**: {step.error_handling}\n"
                    
                    if step.rollback:
                        md += f"- **回滚**: {step.rollback}\n"
                    
                    if step.dependencies:
                        md += f"- **依赖**: {', '.join(step.dependencies)}\n"
                    
                    md += "\n"
        
        # FAQ
        md += "\n## 三、常见问题 (FAQ)\n\n"
        md += "### Q1: 如何查看当前进度？\n"
        md += "查看项目目录下的 `.progress` 文件，记录了当前执行到的步骤。\n\n"
        
        md += "### Q2: 执行中断后如何恢复？\n"
        md += "参考「断点恢复指南」章节，从最后一个完成的检查点继续。\n\n"
        
        md += "### Q3: 遇到错误怎么办？\n"
        md += "1. 查看步骤的「错误处理」说明\n"
        md += "2. 执行「回滚」步骤恢复到上一个稳定状态\n"
        md += "3. 重新执行当前步骤\n\n"
        
        # 断点恢复指南
        md += "\n## 四、断点恢复指南\n\n"
        md += "| 检查点ID | 阶段 | 恢复入口 |\n"
        md += "|---------|------|----------|\n"
        for checkpoint in self.checkpoints:
            md += f"| {checkpoint.id} | {checkpoint.phase_id} | {checkpoint.description} |\n"
        
        # 风险提示
        if self.risks:
            md += "\n## 五、风险提示\n\n"
            for risk in self.risks:
                md += f"### {risk.id}: {risk.description}\n\n"
                md += f"- **严重程度**: {risk.severity}\n"
                md += f"- **缓解措施**: {risk.mitigation}\n"
                md += f"- **涉及阶段**: {risk.phase}\n\n"
        
        # 限制说明
        if self.limitations:
            md += "\n## 六、限制说明\n\n"
            for limitation in self.limitations:
                md += f"- {limitation}\n"
        
        return md


class Planner:
    """
    Skill 04 · Planner（执行规划官）
    
    职责:
    - 将 SOP 工程包转化为人可执行的分阶段操作手册
    - Phase/Task/Step 三层拆解
    - PERT 三点估算
    - 进度跟踪
    - 计划调整
    
    能力边界:
    ✅ 能做: 将已有方案变成清晰可执行的行动计划
    ❌ 不做: 写代码、做技术决策
    """
    
    def __init__(self):
        self.plan: Optional[ExecutionPlan] = None
    
    async def create_execution_plan(
        self,
        handoff: HandoffPackage,
        config: Optional[ProjectConfig] = None
    ) -> ExecutionPlan:
        """
        从交接包创建执行计划
        
        Args:
            handoff: 来自 Skill 02 或 Skill 03 的交接包
            config: 项目配置（可选）
        
        Returns:
            ExecutionPlan: 完整的执行计划
        """
        # 解析交接包
        payload = handoff.payload
        
        # 创建执行计划
        plan = ExecutionPlan(
            project_name=payload.get('project_name', '未命名项目'),
            description=payload.get('description', ''),
            target_environment=payload.get('target_environment', 'Universal'),
        )
        
        # 从 payload 提取 SOP 信息并拆解任务
        # 这里需要根据实际的 SOP 结构进行拆解
        # 暂时创建示例阶段
        await self._decompose_from_sop(plan, payload)
        
        # 计算总时间
        plan.calculate_total_time()
        
        # 识别风险
        await self._identify_risks(plan)
        
        # 创建检查点
        self._create_checkpoints(plan)
        
        # 创建断点恢复映射
        self._create_recovery_points(plan)
        
        self.plan = plan
        return plan
    
    async def _decompose_from_sop(self, plan: ExecutionPlan, payload: Dict[str, Any]):
        """
        从 SOP 拆解任务
        
        Args:
            plan: 执行计划
            payload: 交接包载荷
        """
        # 这里需要根据实际的 SOP 结构进行拆解
        # 示例：创建标准的项目开发阶段
        
        # Phase 1: 项目初始化
        phase1 = Phase(
            id="P1",
            name="项目初始化",
            description="创建项目结构，配置开发环境"
        )
        
        task1 = Task(
            id="P1-T1",
            name="创建项目结构",
            description="初始化项目目录和基础文件"
        )
        
        task1.steps = [
            Step(
                id="P1-T1-S1",
                description="创建项目根目录",
                tool="终端",
                operation=f"mkdir {plan.project_name} && cd {plan.project_name}",
                expected_result=f"项目目录 {plan.project_name} 创建成功",
                verification=f"ls -la | grep {plan.project_name}",
                estimated_time=5,
                needs_user_verification=True,
                verification_note="请确认目录路径正确"
            ),
            Step(
                id="P1-T1-S2",
                description="初始化 Git 仓库",
                tool="终端",
                operation="git init",
                expected_result="Git 仓库初始化成功",
                verification="ls -la | grep .git",
                estimated_time=2,
                dependencies=["P1-T1-S1"]
            ),
            Step(
                id="P1-T1-S3",
                description="创建基础文件",
                tool="编辑器",
                operation="创建 README.md, .gitignore, requirements.txt",
                expected_result="基础文件创建完成",
                verification="ls -la | grep README.md",
                estimated_time=10,
                dependencies=["P1-T1-S1"]
            ),
        ]
        
        task1.calculate_total_time()
        phase1.tasks.append(task1)
        phase1.checkpoint = "项目结构创建完成，Git 仓库已初始化"
        phase1.calculate_total_time()
        plan.phases.append(phase1)
        
        # Phase 2: 核心开发
        phase2 = Phase(
            id="P2",
            name="核心开发",
            description="实现核心功能"
        )
        
        task2 = Task(
            id="P2-T1",
            name="实现核心模块",
            description="编写核心业务逻辑"
        )
        
        task2.steps = [
            Step(
                id="P2-T1-S1",
                description="创建核心模块文件",
                tool="编辑器",
                operation="创建 core/ 目录和相关文件",
                expected_result="核心模块文件创建完成",
                verification="ls -la core/",
                estimated_time=15,
                dependencies=["P1-T1-S3"]
            ),
            Step(
                id="P2-T1-S2",
                description="编写核心逻辑",
                tool="编辑器",
                operation="实现核心业务逻辑代码",
                expected_result="核心逻辑代码编写完成",
                verification="代码静态检查通过",
                estimated_time=60,
                optimistic_time=40,
                normal_time=60,
                pessimistic_time=90,
                dependencies=["P2-T1-S1"],
                error_handling="遇到编译错误，检查语法和导入",
                rollback="删除已创建的文件，重新开始"
            ),
        ]
        
        task2.calculate_total_time()
        phase2.tasks.append(task2)
        phase2.checkpoint = "核心功能实现完成，通过基础测试"
        phase2.calculate_total_time()
        plan.phases.append(phase2)
        
        # Phase 3: 测试验证
        phase3 = Phase(
            id="P3",
            name="测试验证",
            description="编写测试用例，验证功能正确性"
        )
        
        task3 = Task(
            id="P3-T1",
            name="编写测试用例",
            description="为核心模块编写测试"
        )
        
        task3.steps = [
            Step(
                id="P3-T1-S1",
                description="创建测试目录",
                tool="终端",
                operation="mkdir tests",
                expected_result="测试目录创建成功",
                verification="ls -la | grep tests",
                estimated_time=2,
                dependencies=["P2-T1-S2"]
            ),
            Step(
                id="P3-T1-S2",
                description="编写测试用例",
                tool="编辑器",
                operation="编写单元测试和集成测试",
                expected_result="测试用例编写完成",
                verification="测试文件存在",
                estimated_time=30,
                dependencies=["P3-T1-S1"]
            ),
            Step(
                id="P3-T1-S3",
                description="运行测试",
                tool="终端",
                operation="pytest tests/",
                expected_result="所有测试通过",
                verification="测试输出显示 passed",
                estimated_time=10,
                dependencies=["P3-T1-S2"]
            ),
        ]
        
        task3.calculate_total_time()
        phase3.tasks.append(task3)
        phase3.checkpoint = "所有测试通过，功能验证完成"
        phase3.calculate_total_time()
        plan.phases.append(phase3)
        
        # 设置前置条件和假设
        plan.prerequisites = [
            "Python 3.7+ 已安装",
            "Git 已安装",
            "文本编辑器或 IDE 已安装"
        ]
        
        plan.assumptions = [
            "用户具有基本的命令行操作能力",
            "项目不需要特殊的系统依赖",
            "开发环境为 macOS/Linux（Windows 用户需调整路径）"
        ]
        
        plan.limitations = [
            "本手册的命令针对 macOS/Linux，Windows 用户需将路径中的 / 替换为 \\",
            "时间估算基于标准开发速度，实际情况可能有所不同"
        ]
    
    async def _identify_risks(self, plan: ExecutionPlan):
        """
        识别风险
        
        Args:
            plan: 执行计划
        """
        # 添加常见风险
        plan.risks = [
            Risk(
                id="R1",
                description="环境配置差异导致命令执行失败",
                severity="medium",
                mitigation="在执行前验证环境信息，必要时调整命令",
                phase="P1"
            ),
            Risk(
                id="R2",
                description="依赖版本冲突",
                severity="medium",
                mitigation="使用虚拟环境隔离依赖",
                phase="P1"
            ),
            Risk(
                id="R3",
                description="核心逻辑实现时间超出预期",
                severity="high",
                mitigation="采用迭代式开发，先实现最小可用版本",
                phase="P2"
            ),
        ]
    
    def _create_checkpoints(self, plan: ExecutionPlan):
        """
        创建检查点
        
        Args:
            plan: 执行计划
        """
        for i, phase in enumerate(plan.phases, 1):
            checkpoint = Checkpoint(
                id=f"CP{i}",
                phase_id=phase.id,
                description=phase.checkpoint,
                verification_command=f"echo 'Checkpoint {i} reached'",
                expected_output="Checkpoint reached"
            )
            plan.checkpoints.append(checkpoint)
    
    def _create_recovery_points(self, plan: ExecutionPlan):
        """
        创建断点恢复映射
        
        Args:
            plan: 执行计划
        """
        for checkpoint in plan.checkpoints:
            plan.recovery_points[checkpoint.id] = f"从 {checkpoint.phase_id} 阶段开始"
    
    async def track_progress(
        self,
        plan: ExecutionPlan,
        completed_steps: List[str]
    ) -> Dict[str, Any]:
        """
        跟踪执行进度
        
        Args:
            plan: 执行计划
            completed_steps: 已完成的步骤ID列表
        
        Returns:
            进度报告
        """
        total_steps = 0
        completed_count = 0
        
        for phase in plan.phases:
            for task in phase.tasks:
                for step in task.steps:
                    total_steps += 1
                    if step.id in completed_steps:
                        completed_count += 1
        
        progress_percentage = (completed_count / total_steps * 100) if total_steps > 0 else 0
        
        # 找到当前阶段
        current_phase = None
        current_task = None
        
        for phase in plan.phases:
            phase_completed = True
            for task in phase.tasks:
                task_completed = True
                for step in task.steps:
                    if step.id not in completed_steps:
                        task_completed = False
                        phase_completed = False
                        if current_task is None:
                            current_task = task
                            current_phase = phase
                        break
                if not task_completed:
                    break
            if not phase_completed:
                break
        
        return {
            "total_steps": total_steps,
            "completed_steps": completed_count,
            "progress_percentage": progress_percentage,
            "current_phase": current_phase.id if current_phase else "N/A",
            "current_task": current_task.id if current_task else "N/A",
            "status": "completed" if progress_percentage == 100 else "in_progress"
        }
    
    async def adjust_plan(
        self,
        plan: ExecutionPlan,
        feedback: Dict[str, Any]
    ) -> ExecutionPlan:
        """
        根据反馈调整计划
        
        Args:
            plan: 执行计划
            feedback: 反馈信息
                - failed_step_id: 失败的步骤ID
                - reason: 失败原因
                - suggested_fix: 建议的修复方案
        
        Returns:
            调整后的执行计划
        """
        failed_step_id = feedback.get('failed_step_id')
        reason = feedback.get('reason', '')
        suggested_fix = feedback.get('suggested_fix', '')
        
        # 找到失败的步骤
        for phase in plan.phases:
            for task in phase.tasks:
                for step in task.steps:
                    if step.id == failed_step_id:
                        # 添加错误处理信息
                        if not step.error_handling:
                            step.error_handling = f"错误: {reason}\n建议: {suggested_fix}"
                        
                        # 如果有建议的修复方案，创建新的修复步骤
                        if suggested_fix:
                            new_step = Step(
                                id=f"{step.id}-FIX",
                                description=f"修复 {step.id} 的问题",
                                tool=step.tool,
                                operation=suggested_fix,
                                expected_result="问题已修复",
                                verification="重新执行原步骤验证",
                                estimated_time=10,
                                dependencies=[step.id]
                            )
                            task.steps.append(new_step)
                        
                        break
        
        # 重新计算时间
        plan.calculate_total_time()
        
        return plan
    
    def create_handoff(
        self,
        plan: ExecutionPlan,
        to_skill: str = "skill-05-validator"
    ) -> HandoffPackage:
        """
        创建交接包
        
        Args:
            plan: 执行计划
            to_skill: 目标 Skill (skill-05-validator 或 user)
        
        Returns:
            HandoffPackage: 标准交接包
        """
        payload = {
            "project_name": plan.project_name,
            "manual_version": "v1.0",
            "based_on_sop": "自动生成",
            "target_environment": plan.target_environment,
            "executor_level": "中级",
            "operation_manual": {
                "total_phases": len(plan.phases),
                "total_tasks": sum(len(phase.tasks) for phase in plan.phases),
                "total_steps": sum(
                    len(step)
                    for phase in plan.phases
                    for task in phase.tasks
                    for step in [task.steps]
                ),
                "estimated_total_time": f"{plan.total_time} 分钟",
                "phases": [
                    {
                        "phase_id": phase.id,
                        "name": phase.name,
                        "task_count": len(phase.tasks),
                        "checkpoint_defined": bool(phase.checkpoint)
                    }
                    for phase in plan.phases
                ],
                "critical_path": [
                    step.id
                    for phase in plan.phases
                    for task in phase.tasks
                    for step in task.steps
                    if step.priority == TaskPriority.P0
                ]
            },
            "test_targets": [
                {
                    "id": "TT-01",
                    "description": "所有 Phase 检查点可执行",
                    "pass_criteria": "全部检查点有验证命令"
                },
                {
                    "id": "TT-02",
                    "description": "所有步骤有验证方式",
                    "pass_criteria": "100% 步骤含 verify 字段"
                },
                {
                    "id": "TT-03",
                    "description": "幻觉防护标注完整",
                    "pass_criteria": "版本号/API限制全部标注[需用户核实]"
                }
            ],
            "quality_requirements": {
                "completeness": 0.95,
                "safety": 1.00
            },
            "known_risks": [
                {
                    "risk": risk.description,
                    "mitigation": risk.mitigation,
                    "phase": risk.phase
                }
                for risk in plan.risks
            ],
            "execution_assumptions": plan.assumptions,
        }
        
        handoff = HandoffPackage(
            schema_version="1.1",
            from_skill="skill-04-planner",
            to_skill=to_skill,
            handoff_type="HP-E",
            payload=payload
        )
        
        return handoff
    
    def generate_manual(self, plan: ExecutionPlan) -> str:
        """
        生成 Markdown 格式的操作手册
        
        Args:
            plan: 执行计划
        
        Returns:
            str: Markdown 格式的操作手册
        """
        return plan.to_markdown()
