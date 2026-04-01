"""
Navigator（导航官）实现

Skill 00 · 智能体导航官

职责：
- 意图识别（7 种意图类型）
- 置信度评估（三级处理）
- 路由推荐
- 生成交接包

基于 ai-skill-system skill-00-navigator 规范实现
"""

from typing import Tuple, List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import re

from qcm_tools.handoff import HandoffPackage, SkillID, HandoffType
from qcm_tools.handoff.models import create_handoff_d


class IntentType(Enum):
    """意图类型"""
    USE_EXISTING_SKILL = "use_existing_skill"    # 使用现有技能
    FIND_OPEN_SOURCE = "find_open_source"        # 寻找开源方案
    BUILD_CUSTOM = "build_custom"                # 构建自定义方案
    OPTIMIZE_PROMPT = "optimize_prompt"          # 优化提示词
    DEPLOY_PROJECT = "deploy_project"            # 部署项目
    TEST_VALIDATE = "test_validate"              # 测试验收
    UNCLEAR = "unclear"                          # 不明确


class ConfidenceLevel(Enum):
    """置信度级别"""
    HIGH = "high"        # ≥80% 直接路由
    MEDIUM = "medium"    # 60-79% 先确认
    LOW = "low"          # <60% 追问


@dataclass
class IntentAnalysis:
    """意图分析结果"""
    intent_type: IntentType
    confidence: float
    recommended_skill: str
    routing_reason: str
    alternative_skills: List[str] = field(default_factory=list)
    clarification_questions: List[str] = field(default_factory=list)
    project_summary: str = ""
    core_requirements: List[str] = field(default_factory=list)


class Navigator:
    """
    Skill 00 · 智能体导航官
    
    基于 ai-skill-system skill-00-navigator 规范实现
    
    职责：
    - 意图识别（7 种意图类型）
    - 置信度评估（三级处理）
    - 路由推荐
    - 生成交接包
    
    置信度处理规则：
    - ≥80%: 直接路由，输出交接包
    - 60-79%: 先确认「我理解你的需求是X，对吗？」
    - <60%: 追问（最多 3 次），第 3 次后强制路由到 skill-02
    
    Example:
        >>> from qcm_tools.skills import Navigator
        >>> 
        >>> # 方式1：本地关键词匹配
        >>> navigator = Navigator()
        >>> handoff = navigator.generate_handoff("开发一个情感分析系统")
        >>> print(handoff.to_skill)
        skill-03
        >>> 
        >>> # 方式2：AI 增强模式
        >>> from openai import OpenAI
        >>> navigator = Navigator(ai_client=OpenAI())
        >>> handoff = navigator.generate_handoff("帮我找一个开源的 NLP 库")
    """
    
    # 意图关键词映射
    INTENT_KEYWORDS = {
        IntentType.FIND_OPEN_SOURCE: [
            '开源', '库', '框架', '选型', '找', '寻找', '推荐',
            'open source', 'library', 'framework', 'find', 'search'
        ],
        IntentType.OPTIMIZE_PROMPT: [
            '提示词', 'prompt', '优化', '改进', '提示', '指令',
            'optimize', 'improve', 'enhance'
        ],
        IntentType.TEST_VALIDATE: [
            '验收', '测试', '检查', '质量', '验证',
            'validate', 'test', 'verify', 'check', 'qa'
        ],
        IntentType.DEPLOY_PROJECT: [
            '规划', '步骤', '操作手册', '部署', '实施', '执行',
            'plan', 'deploy', 'implement', 'execute', 'manual'
        ],
        IntentType.BUILD_CUSTOM: [
            '开发', '构建', '创建', '实现', '制作', '搭建',
            'build', 'create', 'develop', 'implement', 'make'
        ],
        IntentType.USE_EXISTING_SKILL: [
            '使用', '已有', '现有', '调用',
            'use', 'existing', 'available'
        ],
    }
    
    # Skill 能力映射
    SKILL_CAPABILITIES = {
        'skill-01': '提示词优化',
        'skill-02': '工程化打包',
        'skill-03': '开源技术选型',
        'skill-04': '执行规划',
        'skill-05': '测试验收',
    }
    
    # 意图到 Skill 的路由映射
    INTENT_TO_SKILL = {
        IntentType.FIND_OPEN_SOURCE: 'skill-03',
        IntentType.OPTIMIZE_PROMPT: 'skill-01',
        IntentType.TEST_VALIDATE: 'skill-05',
        IntentType.DEPLOY_PROJECT: 'skill-04',
        IntentType.BUILD_CUSTOM: 'skill-02',
        IntentType.USE_EXISTING_SKILL: 'skill-02',  # 需要进一步分析
        IntentType.UNCLEAR: 'skill-02',  # 默认路由
    }
    
    # 技术栈关键词
    TECH_KEYWORDS = [
        'python', 'javascript', 'java', 'go', 'rust',
        'api', 'web', 'database', 'ml', 'ai', 'nlp',
        'fastapi', 'django', 'flask', 'react', 'vue'
    ]
    
    def __init__(self, ai_client=None):
        """
        初始化导航官
        
        Args:
            ai_client: 可选的 AI 客户端（OpenAI/Claude 等）
                      若为 None，使用本地关键词匹配
        """
        self.ai_client = ai_client
        self._clarification_count = 0
    
    def analyze_intent(self, user_input: str) -> IntentAnalysis:
        """
        分析用户意图
        
        Args:
            user_input: 用户输入
            
        Returns:
            意图分析结果
            
        Example:
            >>> navigator = Navigator()
            >>> analysis = navigator.analyze_intent("开发一个情感分析系统")
            >>> print(analysis.intent_type)
            IntentType.BUILD_CUSTOM
        """
        if self.ai_client:
            return self._analyze_with_ai(user_input)
        else:
            return self._analyze_with_keywords(user_input)
    
    def generate_handoff(
        self,
        user_input: str,
        project_name: str = None
    ) -> HandoffPackage:
        """
        生成路由交接包
        
        完整流程：
        1. 分析意图
        2. 根据置信度处理
        3. 生成交接包
        
        Args:
            user_input: 用户输入
            project_name: 项目名称（可选）
            
        Returns:
            路由交接包（HP-D）
            
        Example:
            >>> navigator = Navigator()
            >>> handoff = navigator.generate_handoff("开发一个API系统")
            >>> print(handoff.to_skill)
            skill-02
        """
        # 分析意图
        analysis = self.analyze_intent(user_input)
        
        # 提取项目信息
        project_summary = self._extract_project_summary(user_input)
        core_requirements = self._extract_requirements(user_input)
        tech_stack = self._extract_tech_stack(user_input)
        
        # 生成交接包
        handoff = create_handoff_d(
            intent_type=analysis.intent_type.value,
            confidence_score=analysis.confidence,
            recommended_skill=analysis.recommended_skill,
            project_summary=project_summary,
            routing_reason=analysis.routing_reason
        )
        
        # 扩展 payload
        handoff.payload.update({
            'alternative_skills': analysis.alternative_skills,
            'core_requirements': core_requirements,
            'tech_stack_preference': tech_stack,
            'project_name': project_name or self._extract_project_name(user_input)
        })
        
        # 根据置信度添加额外信息
        if analysis.confidence < 0.6:
            handoff.payload['clarification_questions'] = analysis.clarification_questions
            handoff.downstream_notes = {
                'to_skill': analysis.recommended_skill,
                'cautions': ['置信度较低，建议先澄清需求'],
                'required_verification': ['确认用户意图是否准确']
            }
        
        return handoff
    
    def get_routing_suggestion(self, user_input: str) -> str:
        """
        获取路由建议（简化版）
        
        Args:
            user_input: 用户输入
            
        Returns:
            路由建议描述
            
        Example:
            >>> navigator = Navigator()
            >>> print(navigator.get_routing_suggestion("找个开源库"))
            建议路由到 Skill 03（开源侦察官）进行技术选型
        """
        analysis = self.analyze_intent(user_input)
        
        skill_name = self.SKILL_CAPABILITIES.get(
            analysis.recommended_skill, 
            '未知'
        )
        
        return (
            f"建议路由到 {analysis.recommended_skill}（{skill_name}）\n"
            f"原因：{analysis.routing_reason}\n"
            f"置信度：{analysis.confidence:.0%}"
        )
    
    # ===== 内部方法 =====
    
    def _analyze_with_keywords(self, user_input: str) -> IntentAnalysis:
        """基于关键词的本地意图分析"""
        user_input_lower = user_input.lower()
        
        # 统计各意图的匹配分数
        scores = {}
        matched_keywords = {}
        
        for intent_type, keywords in self.INTENT_KEYWORDS.items():
            score = 0
            matched = []
            for keyword in keywords:
                if keyword.lower() in user_input_lower:
                    score += 1
                    matched.append(keyword)
            
            scores[intent_type] = score
            matched_keywords[intent_type] = matched
        
        # 找到最高分的意图
        max_score = max(scores.values())
        
        if max_score == 0:
            # 没有匹配到任何关键词
            return IntentAnalysis(
                intent_type=IntentType.UNCLEAR,
                confidence=0.3,
                recommended_skill='skill-02',
                routing_reason="需求描述模糊，建议从工程化开始梳理",
                clarification_questions=self._generate_clarification_questions(user_input)
            )
        
        # 获取最佳匹配的意图
        best_intent = max(scores, key=scores.get)
        
        # 计算置信度
        confidence = min(0.95, 0.6 + max_score * 0.1)
        
        # 获取推荐的 Skill
        recommended_skill = self.INTENT_TO_SKILL[best_intent]
        
        # 生成路由原因
        routing_reason = self._generate_routing_reason(best_intent, matched_keywords[best_intent])
        
        # 生成备选 Skill
        alternative_skills = self._get_alternative_skills(scores, best_intent)
        
        return IntentAnalysis(
            intent_type=best_intent,
            confidence=confidence,
            recommended_skill=recommended_skill,
            routing_reason=routing_reason,
            alternative_skills=alternative_skills,
            project_summary=user_input[:100]
        )
    
    def _analyze_with_ai(self, user_input: str) -> IntentAnalysis:
        """使用 AI 进行意图分析"""
        # 构建 prompt
        prompt = f"""分析以下用户需求，识别意图并推荐路由。

用户需求：
{user_input}

请以 JSON 格式返回分析结果：
{{
    "intent_type": "find_open_source|optimize_prompt|test_validate|deploy_project|build_custom|use_existing_skill|unclear",
    "confidence": 0.0-1.0,
    "recommended_skill": "skill-01|skill-02|skill-03|skill-04|skill-05",
    "routing_reason": "路由原因说明",
    "project_summary": "项目摘要"
}}"""
        
        try:
            # 调用 AI
            response = self.ai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            # 解析响应
            import json
            result = json.loads(response.choices[0].message.content)
            
            return IntentAnalysis(
                intent_type=IntentType(result['intent_type']),
                confidence=result['confidence'],
                recommended_skill=result['recommended_skill'],
                routing_reason=result['routing_reason'],
                project_summary=result.get('project_summary', '')
            )
        except Exception as e:
            # AI 调用失败，降级到关键词匹配
            return self._analyze_with_keywords(user_input)
    
    def _generate_routing_reason(
        self,
        intent_type: IntentType,
        matched_keywords: List[str]
    ) -> str:
        """生成路由原因"""
        reasons = {
            IntentType.FIND_OPEN_SOURCE: f"检测到技术选型需求（关键词：{', '.join(matched_keywords[:3])}），建议使用开源侦察官进行评估",
            IntentType.OPTIMIZE_PROMPT: f"检测到提示词优化需求（关键词：{', '.join(matched_keywords[:3])}），建议使用超级提示词工程师",
            IntentType.TEST_VALIDATE: f"检测到验收测试需求（关键词：{', '.join(matched_keywords[:3])}），建议使用测试验收工程师",
            IntentType.DEPLOY_PROJECT: f"检测到执行规划需求（关键词：{', '.join(matched_keywords[:3])}），建议使用执行规划官",
            IntentType.BUILD_CUSTOM: f"检测到项目开发需求（关键词：{', '.join(matched_keywords[:3])}），建议使用 SOP 工程师进行工程化",
            IntentType.USE_EXISTING_SKILL: "检测到使用现有技能需求，建议评估后选择合适技能",
            IntentType.UNCLEAR: "需求描述不够明确，建议从工程化开始梳理",
        }
        
        return reasons.get(intent_type, "建议进行需求澄清")
    
    def _get_alternative_skills(
        self,
        scores: Dict[IntentType, int],
        best_intent: IntentType
    ) -> List[str]:
        """获取备选 Skill"""
        alternatives = []
        
        # 找到第二、第三高分的意图
        sorted_intents = sorted(
            scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        for intent_type, score in sorted_intents[1:3]:
            if score > 0:
                skill = self.INTENT_TO_SKILL[intent_type]
                if skill not in alternatives:
                    alternatives.append(skill)
        
        return alternatives[:2]  # 最多 2 个备选
    
    def _generate_clarification_questions(self, user_input: str) -> List[str]:
        """生成澄清问题"""
        questions = []
        
        if len(user_input) < 20:
            questions.append("能否详细描述一下您的具体需求？")
        
        if not any(kw in user_input.lower() for kw in self.TECH_KEYWORDS):
            questions.append("您希望使用什么技术栈？")
        
        if '做' in user_input or '弄' in user_input:
            questions.append("您是想开发新项目还是优化现有项目？")
        
        if not questions:
            questions.append("请说明您的项目目标和预期成果？")
        
        return questions[:3]  # 最多 3 个问题
    
    def _extract_project_summary(self, user_input: str) -> str:
        """提取项目摘要"""
        # 简单实现：取前 100 个字符
        if len(user_input) <= 100:
            return user_input
        
        # 尝试按句子分割
        sentences = re.split(r'[。！？.!?]', user_input)
        if sentences and len(sentences[0]) <= 100:
            return sentences[0]
        
        return user_input[:100] + "..."
    
    def _extract_requirements(self, user_input: str) -> List[str]:
        """提取核心需求"""
        requirements = []
        
        # 按标点符号分割
        parts = re.split(r'[，,、；;和与及]', user_input)
        
        for part in parts:
            part = part.strip()
            if len(part) >= 3 and len(part) <= 50:
                requirements.append(part)
        
        return requirements[:5]  # 最多 5 个需求
    
    def _extract_tech_stack(self, user_input: str) -> List[str]:
        """提取技术栈偏好"""
        user_input_lower = user_input.lower()
        tech_stack = []
        
        for tech in self.TECH_KEYWORDS:
            if tech in user_input_lower:
                tech_stack.append(tech)
        
        return tech_stack
    
    def _extract_project_name(self, user_input: str) -> str:
        """提取项目名称"""
        # 尝试匹配"开发XXX"或"创建XXX"模式
        match = re.search(r'(?:开发|创建|构建|实现)(.+?)(?:系统|平台|应用|工具|$)', user_input)
        if match:
            name = match.group(1).strip()
            if len(name) <= 20:
                return name
        
        # 取前 20 个字符作为名称
        return user_input[:20] if len(user_input) <= 20 else user_input[:20] + "..."


__all__ = ['Navigator', 'IntentType', 'ConfidenceLevel', 'IntentAnalysis']
