"""
交接包模块使用示例

演示如何使用 HandoffPackage 和 HandoffManager
"""

from qcm_tools.handoff import (
    HandoffPackage,
    HandoffType,
    SkillID,
    HandoffManager
)
from qcm_tools.handoff.models import (
    create_handoff_d,
    create_handoff_b,
    create_handoff_f
)


def example_1_basic_handoff():
    """示例1：创建基本交接包"""
    print("=" * 60)
    print("示例1：创建基本交接包")
    print("=" * 60)
    
    # 创建交接包
    handoff = HandoffPackage(
        from_skill="skill-00",
        to_skill="skill-03",
        payload={
            'intent_type': 'find_open_source',
            'confidence_score': 0.85,
            'project_summary': '开发一个情感分析系统'
        }
    )
    
    # 导出为 YAML
    yaml_str = handoff.to_yaml()
    print("\n导出为 YAML:")
    print(yaml_str)
    
    # 验证交接包
    issues = handoff.validate()
    print(f"\n验证结果: {'通过' if not issues else issues}")
    
    # 获取摘要
    print("\n交接包摘要:")
    print(handoff.get_summary())


def example_2_using_enums():
    """示例2：使用枚举类型"""
    print("\n" + "=" * 60)
    print("示例2：使用枚举类型")
    print("=" * 60)
    
    # 使用枚举创建交接包
    handoff = HandoffPackage(
        from_skill=SkillID.SKILL_00,
        to_skill=SkillID.SKILL_03,
        handoff_type=HandoffType.HP_D,
        payload={'test': 'data'}
    )
    
    print(f"\nfrom_skill: {handoff.from_skill}")
    print(f"to_skill: {handoff.to_skill}")
    print(f"handoff_type: {handoff.handoff_type}")


def example_3_factory_functions():
    """示例3：使用工厂函数创建标准交接包"""
    print("\n" + "=" * 60)
    print("示例3：使用工厂函数")
    print("=" * 60)
    
    # 创建路由推荐包 (HP-D)
    handoff_d = create_handoff_d(
        intent_type="find_open_source",
        confidence_score=0.85,
        recommended_skill="skill-03",
        project_summary="开发情感分析系统",
        routing_reason="项目需要技术选型"
    )
    
    print("\n路由推荐包 (HP-D):")
    print(handoff_d.to_yaml())
    
    # 创建技术选型包 (HP-B)
    handoff_b = create_handoff_b(
        evaluation_matrix={
            '方案A': {'score': 85, 'rank': 1},
            '方案B': {'score': 78, 'rank': 2}
        },
        selected_solution="方案A",
        gap_list=["缺少中文模型"],
        config_suggestions={'model': 'bert-base-chinese'}
    )
    
    print("\n技术选型包 (HP-B):")
    print(handoff_b.get_summary())
    
    # 创建验收报告包 (HP-F)
    handoff_f = create_handoff_f(
        verdict="CONDITIONAL_PASS",
        overall_score=85.7,
        test_results={'passed': 46, 'failed': 2},
        risk_assessment={'level': 'medium'},
        upstream_feedback={'suggestions': ['修复BUG-001', '修复BUG-002']}
    )
    
    print("\n验收报告包 (HP-F):")
    print(f"结论: {handoff_f.payload['verdict']}")
    print(f"得分: {handoff_f.payload['overall_score']}")


def example_4_handoff_manager():
    """示例4：使用交接包管理器"""
    print("\n" + "=" * 60)
    print("示例4：使用交接包管理器")
    print("=" * 60)
    
    # 创建管理器
    manager = HandoffManager()
    
    # 模拟完整工作流
    # Step 1: Navigator 分析意图
    handoff_00 = HandoffPackage(
        from_skill=SkillID.SKILL_00,
        to_skill=SkillID.SKILL_03,
        handoff_type=HandoffType.HP_D,
        payload={
            'intent_type': 'find_open_source',
            'confidence_score': 0.85,
            'project_summary': '开发情感分析系统'
        }
    )
    manager.save(handoff_00)
    print("\n✅ Skill 00 → Skill 03 交接包已保存")
    
    # Step 2: Scout 技术选型
    handoff_03 = HandoffPackage(
        from_skill=SkillID.SKILL_03,
        to_skill=SkillID.SKILL_02,
        handoff_type=HandoffType.HP_B,
        payload={
            'selected_solution': 'Hugging Face Transformers',
            'evaluation_score': 92
        }
    )
    manager.save(handoff_03)
    print("✅ Skill 03 → Skill 02 交接包已保存")
    
    # Step 3: SOP 工程化
    handoff_02 = HandoffPackage(
        from_skill=SkillID.SKILL_02,
        to_skill=SkillID.SKILL_05,
        handoff_type=HandoffType.HP_C,
        payload={
            'package_name': 'sentiment-analyzer',
            'version': '1.0.0'
        }
    )
    manager.save(handoff_02)
    print("✅ Skill 02 → Skill 05 交接包已保存")
    
    # 获取完整链路
    print("\n" + manager.get_chain_summary())
    
    # 验证链路完整性
    issues = manager.validate_chain()
    print(f"\n链路验证: {'✅ 通过' if not issues else issues}")


def example_5_yaml_roundtrip():
    """示例5：YAML 往返转换"""
    print("\n" + "=" * 60)
    print("示例5：YAML 往返转换")
    print("=" * 60)
    
    # 创建交接包
    original = HandoffPackage(
        from_skill="skill-00",
        to_skill="skill-03",
        handoff_type="HP-D",
        payload={
            'intent_type': 'find_open_source',
            'confidence_score': 0.85,
            'project_summary': '开发情感分析系统'
        },
        self_review={
            'assumptions': ['用户有Python基础'],
            'potential_failures': ['需求可能不明确'],
            'predicted_deduction_by_s05': "预计无扣分"
        }
    )
    
    # 导出为 YAML
    yaml_str = original.to_yaml()
    print("\n导出为 YAML:")
    print(yaml_str)
    
    # 从 YAML 导入
    restored = HandoffPackage.from_yaml(yaml_str)
    print("\n从 YAML 恢复:")
    print(f"  from_skill: {restored.from_skill}")
    print(f"  to_skill: {restored.to_skill}")
    print(f"  handoff_type: {restored.handoff_type}")
    print(f"  payload: {restored.payload}")
    print(f"  self_review: {restored.self_review}")
    
    # 验证数据一致性
    assert restored.from_skill == original.from_skill
    assert restored.to_skill == original.to_skill
    assert restored.payload == original.payload
    print("\n✅ 往返转换验证通过")


def example_6_session_management():
    """示例6：多会话管理"""
    print("\n" + "=" * 60)
    print("示例6：多会话管理")
    print("=" * 60)
    
    manager = HandoffManager()
    
    # 会话1：项目A
    handoff_a = HandoffPackage(
        from_skill="skill-00",
        to_skill="skill-03",
        payload={'project': 'A'}
    )
    manager.save(handoff_a, session_id="project-a")
    
    # 会话2：项目B
    handoff_b = HandoffPackage(
        from_skill="skill-00",
        to_skill="skill-02",
        payload={'project': 'B'}
    )
    manager.save(handoff_b, session_id="project-b")
    
    # 查看各会话
    print(f"\n会话 project-a: {len(manager.get_chain('project-a'))} 个交接包")
    print(f"会话 project-b: {len(manager.get_chain('project-b'))} 个交接包")
    
    # 导出会话
    exported = manager.export_session("project-a", format="yaml")
    print("\n导出会话 project-a:")
    print(exported[:200] + "...")


def example_7_compatibility_with_ai_skill_system():
    """示例7：与 ai-skill-system 兼容性"""
    print("\n" + "=" * 60)
    print("示例7：与 ai-skill-system 兼容性")
    print("=" * 60)
    
    # 模拟从 ai-skill-system 接收的交接包
    ai_skill_system_yaml = """
handoff:
  schema_version: '1.1'
  from_skill: skill-00
  to_skill: skill-03
  payload:
    intent_type: find_open_source
    confidence_score: 0.85
    recommended_skill: skill-03
    routing_reason: 项目需要技术选型
    project_summary: 开发情感分析系统
  user_action: 将此交接包复制，粘贴到 skill-03 的对话开头
  created_at: '2025-03-31'
  self_review:
    assumptions:
    - 用户有明确的技术需求
    potential_failures: []
    predicted_deduction_by_s05: ''
"""
    
    # 导入交接包
    handoff = HandoffPackage.from_yaml(ai_skill_system_yaml)
    
    print("\n✅ 成功导入 ai-skill-system 交接包")
    print(f"  schema_version: {handoff.schema_version}")
    print(f"  from_skill: {handoff.from_skill}")
    print(f"  to_skill: {handoff.to_skill}")
    print(f"  intent_type: {handoff.payload['intent_type']}")
    
    # 处理后生成交给下一个 Skill 的交接包
    response_handoff = HandoffPackage(
        schema_version="1.1",
        from_skill="skill-03",
        to_skill="skill-02",
        handoff_type="HP-B",
        payload={
            'evaluation_matrix': {'score': 92},
            'selected_solution': 'Transformers',
            'gap_list': [],
            'config_suggestions': {'model': 'bert-base'}
        },
        self_review={
            'assumptions': ['用户接受开源方案'],
            'potential_failures': [],
            'predicted_deduction_by_s05': ''
        }
    )
    
    print("\n✅ 生成交往 skill-02 的交接包:")
    print(response_handoff.to_yaml())


if __name__ == "__main__":
    """运行所有示例"""
    example_1_basic_handoff()
    example_2_using_enums()
    example_3_factory_functions()
    example_4_handoff_manager()
    example_5_yaml_roundtrip()
    example_6_session_management()
    example_7_compatibility_with_ai_skill_system()
    
    print("\n" + "=" * 60)
    print("✅ 所有示例运行完成")
    print("=" * 60)
