"""
Navigator（导航官）使用示例

演示如何使用 Navigator 进行意图识别和路由推荐
"""

from qcm_tools.skills import Navigator
from qcm_tools.handoff import HandoffManager


def example_1_basic_intent_analysis():
    """示例1：基本意图分析"""
    print("=" * 60)
    print("示例1：基本意图分析")
    print("=" * 60)
    
    navigator = Navigator()
    
    # 不同类型的用户输入
    test_cases = [
        "帮我找一个开源的情感分析库",
        "优化这个提示词",
        "验收这个项目的质量",
        "生成部署操作手册",
        "开发一个用户管理系统",
    ]
    
    for user_input in test_cases:
        analysis = navigator.analyze_intent(user_input)
        print(f"\n输入: {user_input}")
        print(f"  意图类型: {analysis.intent_type.value}")
        print(f"  置信度: {analysis.confidence:.0%}")
        print(f"  推荐路由: {analysis.recommended_skill}")
        print(f"  路由原因: {analysis.routing_reason[:50]}...")


def example_2_generate_handoff():
    """示例2：生成交接包"""
    print("\n" + "=" * 60)
    print("示例2：生成交接包")
    print("=" * 60)
    
    navigator = Navigator()
    
    # 生成交接包
    handoff = navigator.generate_handoff(
        "用 Python 和 FastAPI 开发一个情感分析 API 系统"
    )
    
    print(f"\n交接包类型: {handoff.handoff_type}")
    print(f"从: {handoff.from_skill}")
    print(f"到: {handoff.to_skill}")
    print(f"\nPayload:")
    for key, value in handoff.payload.items():
        if isinstance(value, list):
            print(f"  {key}: {value}")
        else:
            print(f"  {key}: {value}")
    
    print(f"\nYAML 格式:")
    print(handoff.to_yaml())


def example_3_unclear_intent():
    """示例3：不明确意图处理"""
    print("\n" + "=" * 60)
    print("示例3：不明确意图处理")
    print("=" * 60)
    
    navigator = Navigator()
    
    # 模糊的输入
    handoff = navigator.generate_handoff("帮忙看看")
    
    print(f"\n用户输入: '帮忙看看'")
    print(f"置信度: {handoff.payload['confidence_score']:.0%}")
    print(f"推荐路由: {handoff.to_skill}")
    
    if 'clarification_questions' in handoff.payload:
        print(f"\n澄清问题:")
        for i, q in enumerate(handoff.payload['clarification_questions'], 1):
            print(f"  {i}. {q}")
    
    if handoff.downstream_notes:
        print(f"\n下游注意事项:")
        for caution in handoff.downstream_notes.get('cautions', []):
            print(f"  ⚠️ {caution}")


def example_4_routing_suggestion():
    """示例4：获取路由建议"""
    print("\n" + "=" * 60)
    print("示例4：获取路由建议")
    print("=" * 60)
    
    navigator = Navigator()
    
    suggestions = [
        "找一个机器学习框架",
        "开发一个数据分析平台",
        "验收项目质量",
    ]
    
    for user_input in suggestions:
        suggestion = navigator.get_routing_suggestion(user_input)
        print(f"\n输入: {user_input}")
        print(suggestion)


def example_5_with_handoff_manager():
    """示例5：与 HandoffManager 集成"""
    print("\n" + "=" * 60)
    print("示例5：与 HandoffManager 集成")
    print("=" * 60)
    
    navigator = Navigator()
    manager = HandoffManager()
    
    # 模拟工作流
    print("\n模拟工作流:")
    
    # 1. 用户需求进入 Navigator
    print("\n1. 用户需求进入 Navigator")
    handoff_00 = navigator.generate_handoff("开发一个情感分析系统")
    print(f"   Navigator 分析: {handoff_00.payload['intent_type']}")
    print(f"   推荐路由: {handoff_00.to_skill}")
    manager.save(handoff_00)
    
    # 2. 查看交接包链路
    print("\n2. 交接包链路:")
    print(manager.get_chain_summary())


def example_6_tech_stack_extraction():
    """示例6：技术栈提取"""
    print("\n" + "=" * 60)
    print("示例6：技术栈提取")
    print("=" * 60)
    
    navigator = Navigator()
    
    handoff = navigator.generate_handoff(
        "用 Python FastAPI PostgreSQL Redis 开发一个高并发 API 系统"
    )
    
    print(f"\n用户输入:")
    print("用 Python FastAPI PostgreSQL Redis 开发一个高并发 API 系统")
    
    print(f"\n提取的技术栈:")
    for tech in handoff.payload.get('tech_stack_preference', []):
        print(f"  - {tech}")
    
    print(f"\n项目名称: {handoff.payload.get('project_name', 'N/A')}")
    print(f"项目摘要: {handoff.payload.get('project_summary', 'N/A')}")


def example_7_different_intents():
    """示例7：不同意图类型的处理"""
    print("\n" + "=" * 60)
    print("示例7：不同意图类型的处理")
    print("=" * 60)
    
    navigator = Navigator()
    
    scenarios = {
        "技术选型": "帮我找一个开源的自然语言处理库",
        "提示词优化": "优化这个系统提示词，让它更准确",
        "质量验收": "帮我验收这个项目，检查代码质量",
        "执行规划": "生成这个项目的部署步骤和操作手册",
        "项目开发": "开发一个用户认证系统",
    }
    
    for scenario, user_input in scenarios.items():
        analysis = navigator.analyze_intent(user_input)
        print(f"\n场景: {scenario}")
        print(f"  输入: {user_input}")
        print(f"  意图: {analysis.intent_type.value}")
        print(f"  路由: {analysis.recommended_skill}")
        print(f"  置信度: {analysis.confidence:.0%}")


def example_8_full_workflow():
    """示例8：完整工作流"""
    print("\n" + "=" * 60)
    print("示例8：完整工作流")
    print("=" * 60)
    
    navigator = Navigator()
    manager = HandoffManager()
    
    # 完整的 AI 辅助开发流程
    print("\n完整流程演示:")
    
    # Step 1: Navigator 分析需求
    print("\nStep 1: Navigator 分析需求")
    user_requirement = "开发一个情感分析 API，使用 Python 和 FastAPI"
    handoff = navigator.generate_handoff(user_requirement)
    print(f"  需求: {user_requirement}")
    print(f"  意图: {handoff.payload['intent_type']}")
    print(f"  推荐: {handoff.to_skill}")
    
    # Step 2: 存储交接包
    print("\nStep 2: 存储交接包")
    manager.save(handoff)
    print("  ✅ 交接包已保存")
    
    # Step 3: 导出交接包给下一个 Skill
    print("\nStep 3: 导出交接包")
    yaml_output = handoff.to_yaml()
    print("  ✅ 已导出 YAML 格式交接包")
    print(f"\n{yaml_output}")


if __name__ == "__main__":
    """运行所有示例"""
    example_1_basic_intent_analysis()
    example_2_generate_handoff()
    example_3_unclear_intent()
    example_4_routing_suggestion()
    example_5_with_handoff_manager()
    example_6_tech_stack_extraction()
    example_7_different_intents()
    example_8_full_workflow()
    
    print("\n" + "=" * 60)
    print("✅ 所有示例运行完成")
    print("=" * 60)
