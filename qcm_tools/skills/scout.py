"""
Scout (Skill-03) - 开源侦察官

负责技术选型评估，提供七维度评估框架
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum
import json

from qcm_tools.ai import AIClient, Message, AIClientFactory
from qcm_tools.bridge import AISkillSystemBridge
from qcm_tools.handoff import HandoffPackage, create_handoff


class EvaluationDimension(Enum):
    """评估维度"""
    FUNCTIONALITY = "功能性"      # 30%
    USABILITY = "易用性"          # 20%
    PERFORMANCE = "性能"          # 15%
    MAINTAINABILITY = "可维护性"  # 10%
    COMMUNITY = "社区活跃度"      # 10%
    COMPATIBILITY = "兼容性"      # 10%
    DOCUMENTATION = "文档"        # 5%


@dataclass
class DimensionScore:
    """维度评分"""
    dimension: EvaluationDimension
    score: float  # 0-100
    weight: float
    notes: str = ""
    details: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'dimension': self.dimension.value,
            'score': self.score,
            'weight': self.weight,
            'notes': self.notes,
            'details': self.details
        }


@dataclass
class LibraryInfo:
    """库信息"""
    name: str
    version: Optional[str] = None
    description: str = ""
    stars: int = 0
    forks: int = 0
    last_update: Optional[str] = None
    license: str = ""
    url: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'stars': self.stars,
            'forks': self.forks,
            'last_update': self.last_update,
            'license': self.license,
            'url': self.url
        }


@dataclass
class LibraryEvaluation:
    """库评估结果"""
    library: LibraryInfo
    overall_score: float
    dimension_scores: List[DimensionScore]
    pros: List[str]
    cons: List[str]
    recommendation: str  # highly_recommended, recommended, neutral, not_recommended
    use_cases: List[str]
    risks: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'library': self.library.to_dict(),
            'overall_score': self.overall_score,
            'dimension_scores': [ds.to_dict() for ds in self.dimension_scores],
            'pros': self.pros,
            'cons': self.cons,
            'recommendation': self.recommendation,
            'use_cases': self.use_cases,
            'risks': self.risks,
            'metadata': self.metadata
        }


@dataclass
class ComparisonReport:
    """对比报告"""
    libraries: List[LibraryEvaluation]
    comparison_matrix: Dict[str, Dict[str, float]]
    winner: str
    summary: str
    recommendation: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            'libraries': [lib.to_dict() for lib in self.libraries],
            'comparison_matrix': self.comparison_matrix,
            'winner': self.winner,
            'summary': self.summary,
            'recommendation': self.recommendation
        }


class Scout:
    """
    Scout (Skill-03) - 开源侦察官

    负责技术选型评估，使用七维度评估框架

    Example:
        >>> from qcm_tools.skills import Scout
        >>> from qcm_tools.ai import AIClientFactory
        >>>
        >>> ai_client = AIClientFactory.create("openai", api_key="sk-xxx")
        >>> scout = Scout(ai_client=ai_client)
        >>>
        >>> # 评估单个库
        >>> evaluation = await scout.evaluate_library(
        ...     "fastapi",
        ...     requirement="构建高性能 API"
        ... )
        >>>
        >>> # 对比多个库
        >>> comparison = await scout.compare_libraries(
        ...     ["fastapi", "flask", "django"],
        ...     requirement="构建 RESTful API"
        ... )
    """

    # 七维度权重
    DIMENSION_WEIGHTS = {
        EvaluationDimension.FUNCTIONALITY: 0.30,
        EvaluationDimension.USABILITY: 0.20,
        EvaluationDimension.PERFORMANCE: 0.15,
        EvaluationDimension.MAINTAINABILITY: 0.10,
        EvaluationDimension.COMMUNITY: 0.10,
        EvaluationDimension.COMPATIBILITY: 0.10,
        EvaluationDimension.DOCUMENTATION: 0.05,
    }

    def __init__(
        self,
        ai_client: Optional[AIClient] = None,
        use_ai: bool = True
    ):
        """
        初始化 Scout

        Args:
            ai_client: AI 客户端（可选）
            use_ai: 是否使用 AI 增强
        """
        self.ai_client = ai_client or AIClientFactory.create("mock")
        self.use_ai = use_ai
        self.bridge = AISkillSystemBridge()

    async def search_libraries(
        self,
        requirement: str,
        language: str = "python",
        limit: int = 10
    ) -> List[LibraryInfo]:
        """
        搜索开源库

        Args:
            requirement: 需求描述
            language: 编程语言
            limit: 返回结果数量

        Returns:
            库信息列表

        Example:
            >>> libraries = await scout.search_libraries(
            ...     "FastAPI 权限管理",
            ...     language="python"
            ... )
        """
        if self.use_ai:
            return await self._search_with_ai(requirement, language, limit)
        else:
            return self._search_basic(requirement, language, limit)

    async def _search_with_ai(
        self,
        requirement: str,
        language: str,
        limit: int
    ) -> List[LibraryInfo]:
        """使用 AI 搜索"""
        prompt = f"""请推荐 {limit} 个适合以下需求的 {language} 开源库：

需求: {requirement}

请用 JSON 格式返回：
{{
    "libraries": [
        {{
            "name": "库名",
            "description": "简介",
            "stars": 星数（估算）,
            "url": "GitHub URL"
        }}
    ]
}}
"""

        response = await self.ai_client.chat([
            Message.system("你是一个开源库搜索专家"),
            Message.user(prompt)
        ])

        try:
            # 解析 AI 响应
            content = response.content
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0]

            result = json.loads(content.strip())

            return [
                LibraryInfo(
                    name=lib['name'],
                    description=lib.get('description', ''),
                    stars=lib.get('stars', 0),
                    url=lib.get('url', '')
                )
                for lib in result.get('libraries', [])
            ]
        except (json.JSONDecodeError, KeyError):
            # 解析失败，返回空列表
            return []

    def _search_basic(
        self,
        requirement: str,
        language: str,
        limit: int
    ) -> List[LibraryInfo]:
        """基础搜索（不使用 AI）"""
        # 这里可以实现基于关键词的搜索
        # 目前返回空列表作为占位
        return []

    async def evaluate_library(
        self,
        library_name: str,
        requirement: str,
        constraints: Optional[List[str]] = None
    ) -> LibraryEvaluation:
        """
        评估单个库

        Args:
            library_name: 库名
            requirement: 需求描述
            constraints: 约束条件

        Returns:
            LibraryEvaluation 对象

        Example:
            >>> evaluation = await scout.evaluate_library(
            ...     "fastapi",
            ...     requirement="构建高性能 API",
            ...     constraints=["Python 3.8+", "异步支持"]
            ... )
        """
        # 构造评估 Prompt
        constraints_str = ""
        if constraints:
            constraints_str = f"\n\n约束条件：{', '.join(constraints)}"

        prompt = f"""请评估 {library_name} 库是否适合以下需求：

需求: {requirement}
{constraints_str}

请使用七维度评估框架：
1. 功能性 (30%) - 是否满足需求功能
2. 易用性 (20%) - 学习曲线和开发体验
3. 性能 (15%) - 运行效率和资源占用
4. 可维护性 (10%) - 代码质量和架构
5. 社区活跃度 (10%) - Star 数、更新频率、贡献者
6. 兼容性 (10%) - 依赖、平台支持
7. 文档 (5%) - 文档完整性和质量

请用 JSON 格式返回：
{{
    "dimension_scores": [
        {{
            "dimension": "功能性",
            "score": 85,
            "notes": "评分理由",
            "details": ["详细点1", "详细点2"]
        }}
    ],
    "pros": ["优势列表"],
    "cons": ["劣势列表"],
    "use_cases": ["适用场景"],
    "risks": ["风险点"]
}}
"""

        response = await self.ai_client.chat([
            Message.system("你是一个技术选型评估专家，擅长客观评估开源库的优劣。"),
            Message.user(prompt)
        ])

        # 解析响应
        try:
            content = response.content
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0]

            result = json.loads(content.strip())

            # 构造维度评分
            dimension_scores = []
            for ds in result.get('dimension_scores', []):
                dimension_str = ds.get('dimension', '功能性')
                # 匹配枚举
                dimension = None
                for dim in EvaluationDimension:
                    if dim.value in dimension_str or dimension_str in dim.value:
                        dimension = dim
                        break
                if dimension is None:
                    dimension = EvaluationDimension.FUNCTIONALITY

                dimension_scores.append(DimensionScore(
                    dimension=dimension,
                    score=float(ds.get('score', 75)),
                    weight=self.DIMENSION_WEIGHTS[dimension],
                    notes=ds.get('notes', ''),
                    details=ds.get('details', [])
                ))

            # 计算总分
            overall_score = sum(
                ds.score * ds.weight for ds in dimension_scores
            )

            # 确定推荐级别
            if overall_score >= 80:
                recommendation = "highly_recommended"
            elif overall_score >= 70:
                recommendation = "recommended"
            elif overall_score >= 60:
                recommendation = "neutral"
            else:
                recommendation = "not_recommended"

            return LibraryEvaluation(
                library=LibraryInfo(name=library_name),
                overall_score=overall_score,
                dimension_scores=dimension_scores,
                pros=result.get('pros', []),
                cons=result.get('cons', []),
                recommendation=recommendation,
                use_cases=result.get('use_cases', []),
                risks=result.get('risks', []),
                metadata={'model': response.model}
            )

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # 解析失败，返回默认评估
            return LibraryEvaluation(
                library=LibraryInfo(name=library_name),
                overall_score=75.0,
                dimension_scores=[
                    DimensionScore(
                        dimension=dim,
                        score=75.0,
                        weight=weight
                    )
                    for dim, weight in self.DIMENSION_WEIGHTS.items()
                ],
                pros=["解析失败"],
                cons=["无法解析 AI 响应"],
                recommendation="neutral",
                use_cases=[],
                risks=[],
                metadata={'error': str(e)}
            )

    async def compare_libraries(
        self,
        library_names: List[str],
        requirement: str,
        constraints: Optional[List[str]] = None
    ) -> ComparisonReport:
        """
        对比多个库

        Args:
            library_names: 库名列表
            requirement: 需求描述
            constraints: 约束条件

        Returns:
            ComparisonReport 对象

        Example:
            >>> comparison = await scout.compare_libraries(
            ...     ["fastapi", "flask", "django"],
            ...     requirement="构建 RESTful API"
            ... )
        """
        # 评估每个库
        evaluations = []
        for lib_name in library_names:
            evaluation = await self.evaluate_library(
                lib_name,
                requirement,
                constraints
            )
            evaluations.append(evaluation)

        # 构造对比矩阵
        comparison_matrix = {}
        for evaluation in evaluations:
            comparison_matrix[evaluation.library.name] = {
                ds.dimension.value: ds.score
                for ds in evaluation.dimension_scores
            }
            comparison_matrix[evaluation.library.name]['overall'] = evaluation.overall_score

        # 确定获胜者
        winner = max(evaluations, key=lambda e: e.overall_score).library.name

        # 生成摘要
        summary = f"对比了 {len(library_names)} 个库：{', '.join(library_names)}。"
        summary += f"推荐使用 {winner}，综合评分 {comparison_matrix[winner]['overall']:.1f}。"

        return ComparisonReport(
            libraries=evaluations,
            comparison_matrix=comparison_matrix,
            winner=winner,
            summary=summary,
            recommendation=f"基于七维度评估，{winner} 最适合 '{requirement}' 需求。"
        )

    async def recommend_best(
        self,
        requirement: str,
        language: str = "python",
        constraints: Optional[List[str]] = None,
        limit: int = 3
    ) -> LibraryEvaluation:
        """
        智能推荐最佳选择

        Args:
            requirement: 需求描述
            language: 编程语言
            constraints: 约束条件
            limit: 候选数量

        Returns:
            最佳库的评估结果

        Example:
            >>> best = await scout.recommend_best(
            ...     "构建高性能 RESTful API",
            ...     language="python"
            ... )
        """
        # 1. 搜索候选库
        libraries = await self.search_libraries(
            requirement,
            language,
            limit=limit
        )

        if not libraries:
            # 如果搜索失败，返回默认推荐
            return LibraryEvaluation(
                library=LibraryInfo(name="未找到合适的库"),
                overall_score=0.0,
                dimension_scores=[],
                pros=[],
                cons=[],
                recommendation="not_recommended",
                use_cases=[],
                risks=["未找到合适的库"]
            )

        # 2. 对比候选库
        comparison = await self.compare_libraries(
            [lib.name for lib in libraries],
            requirement,
            constraints
        )

        # 3. 返回最佳选择
        return comparison.libraries[0]

    def create_handoff(
        self,
        evaluation: LibraryEvaluation,
        to_skill: str = "skill-04"
    ) -> HandoffPackage:
        """
        创建交接包

        Args:
            evaluation: 评估结果
            to_skill: 目标 Skill

        Returns:
            HandoffPackage 对象
        """
        return create_handoff(
            from_skill="skill-03",
            to_skill=to_skill,
            handoff_type="HP-B",  # 技术选型包
            payload={
                'selected_library': evaluation.library.name,
                'overall_score': evaluation.overall_score,
                'recommendation': evaluation.recommendation,
                'pros': evaluation.pros,
                'cons': evaluation.cons,
                'use_cases': evaluation.use_cases,
                'risks': evaluation.risks,
                'dimension_scores': [ds.to_dict() for ds in evaluation.dimension_scores]
            }
        )
