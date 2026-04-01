"""
交接包模块测试

测试 HandoffPackage 和 HandoffManager 的核心功能
"""

import pytest
from qcm_tools.handoff import (
    HandoffPackage,
    HandoffType,
    SkillID,
    HandoffManager
)
from qcm_tools.handoff.models import (
    create_handoff_d,
    create_handoff_b,
    create_handoff_c,
    create_handoff_f
)


class TestHandoffPackage:
    """测试 HandoffPackage 数据类"""
    
    def test_create_basic_handoff(self):
        """测试创建基本交接包"""
        handoff = HandoffPackage(
            from_skill="skill-00",
            to_skill="skill-03",
            payload={'test': 'data'}
        )
        
        assert handoff.from_skill == "skill-00"
        assert handoff.to_skill == "skill-03"
        assert handoff.payload == {'test': 'data'}
        assert handoff.schema_version == "1.1"
    
    def test_create_with_enum(self):
        """测试使用枚举创建交接包"""
        handoff = HandoffPackage(
            from_skill=SkillID.SKILL_00,
            to_skill=SkillID.SKILL_03,
            payload={}
        )
        
        assert handoff.from_skill == "skill-00"
        assert handoff.to_skill == "skill-03"
    
    def test_to_dict(self):
        """测试转换为字典"""
        handoff = HandoffPackage(
            from_skill="skill-00",
            to_skill="skill-03",
            payload={'key': 'value'},
            user_action="测试操作"
        )
        
        data = handoff.to_dict()
        
        assert 'handoff' in data
        assert data['handoff']['from_skill'] == "skill-00"
        assert data['handoff']['to_skill'] == "skill-03"
        assert data['handoff']['payload'] == {'key': 'value'}
    
    def test_to_yaml(self):
        """测试导出为 YAML"""
        handoff = HandoffPackage(
            from_skill="skill-00",
            to_skill="skill-03",
            payload={'intent_type': 'find_open_source'}
        )
        
        yaml_str = handoff.to_yaml()
        
        assert 'handoff:' in yaml_str
        assert 'from_skill: skill-00' in yaml_str
        assert 'to_skill: skill-03' in yaml_str
    
    def test_from_yaml(self):
        """测试从 YAML 导入"""
        yaml_str = """
handoff:
  schema_version: '1.1'
  from_skill: skill-00
  to_skill: skill-03
  payload:
    intent_type: find_open_source
    confidence_score: 0.85
  user_action: 测试操作
  created_at: '2025-03-31'
"""
        handoff = HandoffPackage.from_yaml(yaml_str)
        
        assert handoff.from_skill == "skill-00"
        assert handoff.to_skill == "skill-03"
        assert handoff.payload['intent_type'] == "find_open_source"
        assert handoff.payload['confidence_score'] == 0.85
    
    def test_to_json(self):
        """测试导出为 JSON"""
        handoff = HandoffPackage(
            from_skill="skill-00",
            to_skill="skill-03",
            payload={'test': 'data'}
        )
        
        json_str = handoff.to_json()
        
        assert '"from_skill": "skill-00"' in json_str
        assert '"to_skill": "skill-03"' in json_str
    
    def test_from_json(self):
        """测试从 JSON 导入"""
        json_str = '''
{
  "handoff": {
    "schema_version": "1.1",
    "from_skill": "skill-00",
    "to_skill": "skill-03",
    "payload": {"test": "data"}
  }
}
'''
        handoff = HandoffPackage.from_json(json_str)
        
        assert handoff.from_skill == "skill-00"
        assert handoff.to_skill == "skill-03"
    
    def test_validate_success(self):
        """测试验证成功"""
        handoff = HandoffPackage(
            from_skill="skill-00",
            to_skill="skill-03",
            payload={'test': 'data'}
        )
        
        issues = handoff.validate()
        
        assert len(issues) == 0
        assert handoff.is_valid()
    
    def test_validate_missing_fields(self):
        """测试验证缺少必填字段"""
        handoff = HandoffPackage()
        
        issues = handoff.validate()
        
        assert len(issues) > 0
        assert "from_skill 不能为空" in issues
        assert "to_skill 不能为空" in issues
    
    def test_validate_same_skill(self):
        """测试验证相同 Skill"""
        handoff = HandoffPackage(
            from_skill="skill-00",
            to_skill="skill-00",
            payload={'test': 'data'}
        )
        
        issues = handoff.validate()
        
        assert "from_skill 和 to_skill 不能相同" in issues
    
    def test_roundtrip_yaml(self):
        """测试 YAML 往返转换"""
        original = HandoffPackage(
            from_skill="skill-00",
            to_skill="skill-03",
            payload={'intent_type': 'find_open_source'},
            handoff_type=HandoffType.HP_D.value
        )
        
        yaml_str = original.to_yaml()
        restored = HandoffPackage.from_yaml(yaml_str)
        
        assert restored.from_skill == original.from_skill
        assert restored.to_skill == original.to_skill
        assert restored.payload == original.payload
        assert restored.handoff_type == original.handoff_type
    
    def test_with_self_review(self):
        """测试带自我审查的交接包"""
        handoff = HandoffPackage(
            from_skill="skill-00",
            to_skill="skill-03",
            payload={'test': 'data'},
            self_review={
                'assumptions': ['假设1', '假设2'],
                'potential_failures': ['可能失败'],
                'predicted_deduction_by_s05': "预计扣分 5 分"
            }
        )
        
        assert handoff.self_review is not None
        assert len(handoff.self_review['assumptions']) == 2
    
    def test_with_downstream_notes(self):
        """测试带下游注意事项的交接包"""
        handoff = HandoffPackage(
            from_skill="skill-00",
            to_skill="skill-03",
            payload={'test': 'data'},
            downstream_notes={
                'to_skill': 'skill-03',
                'cautions': ['注意1', '注意2'],
                'required_verification': ['需验证项']
            }
        )
        
        assert handoff.downstream_notes is not None
        assert len(handoff.downstream_notes['cautions']) == 2
    
    def test_get_summary(self):
        """测试获取摘要"""
        handoff = HandoffPackage(
            from_skill="skill-00",
            to_skill="skill-03",
            payload={'test': 'data'},
            handoff_type=HandoffType.HP_D.value
        )
        
        summary = handoff.get_summary()
        
        assert "skill-00" in summary
        assert "skill-03" in summary
        assert "HP-D" in summary


class TestFactoryFunctions:
    """测试工厂函数"""
    
    def test_create_handoff_d(self):
        """测试创建路由推荐包"""
        handoff = create_handoff_d(
            intent_type="find_open_source",
            confidence_score=0.85,
            recommended_skill="skill-03",
            project_summary="开发情感分析系统"
        )
        
        assert handoff.handoff_type == "HP-D"
        assert handoff.from_skill == "skill-00"
        assert handoff.to_skill == "skill-03"
        assert handoff.payload['intent_type'] == "find_open_source"
    
    def test_create_handoff_b(self):
        """测试创建技术选型包"""
        handoff = create_handoff_b(
            evaluation_matrix={'score': 85},
            selected_solution="方案A",
            gap_list=["缺口1"],
            config_suggestions={'tech': 'Python'}
        )
        
        assert handoff.handoff_type == "HP-B"
        assert handoff.from_skill == "skill-03"
        assert handoff.to_skill == "skill-02"
    
    def test_create_handoff_c(self):
        """测试创建工程包交付"""
        handoff = create_handoff_c(
            package_metadata={'name': 'test-project'},
            test_targets=[{'id': 'TC-001'}],
            defect_history={'p0': 0, 'p1': 2},
            known_limitations=["限制1"]
        )
        
        assert handoff.handoff_type == "HP-C"
        assert handoff.from_skill == "skill-02"
        assert handoff.to_skill == "skill-05"
    
    def test_create_handoff_f(self):
        """测试创建验收报告包"""
        handoff = create_handoff_f(
            verdict="CONDITIONAL_PASS",
            overall_score=85.7,
            test_results={'passed': 46, 'failed': 2},
            risk_assessment={'level': 'medium'},
            upstream_feedback={'suggestions': []}
        )
        
        assert handoff.handoff_type == "HP-F"
        assert handoff.from_skill == "skill-05"
        assert handoff.to_skill == "release"


class TestHandoffManager:
    """测试交接包管理器"""
    
    @pytest.fixture
    def manager(self):
        """创建管理器实例"""
        return HandoffManager()
    
    def test_save_and_load(self, manager):
        """测试保存和加载"""
        handoff = HandoffPackage(
            from_skill="skill-00",
            to_skill="skill-03",
            payload={'test': 'data'}
        )
        
        manager.save(handoff)
        loaded = manager.load("skill-00")
        
        assert loaded is not None
        assert loaded.from_skill == "skill-00"
        assert loaded.to_skill == "skill-03"
    
    def test_load_nonexistent(self, manager):
        """测试加载不存在的交接包"""
        loaded = manager.load("skill-99")
        assert loaded is None
    
    def test_get_chain(self, manager):
        """测试获取链路"""
        handoff1 = HandoffPackage(
            from_skill="skill-00",
            to_skill="skill-03",
            payload={'step': 1}
        )
        handoff2 = HandoffPackage(
            from_skill="skill-03",
            to_skill="skill-02",
            payload={'step': 2}
        )
        
        manager.save(handoff1)
        manager.save(handoff2)
        
        chain = manager.get_chain()
        
        assert len(chain) == 2
        assert chain[0].from_skill == "skill-00"
        assert chain[1].from_skill == "skill-03"
    
    def test_get_chain_summary(self, manager):
        """测试获取链路摘要"""
        handoff = HandoffPackage(
            from_skill="skill-00",
            to_skill="skill-03",
            payload={'test': 'data'}
        )
        
        manager.save(handoff)
        summary = manager.get_chain_summary()
        
        assert "skill-00" in summary
        assert "skill-03" in summary
    
    def test_validate_chain_success(self, manager):
        """测试验证链路成功"""
        handoff1 = HandoffPackage(
            from_skill="skill-00",
            to_skill="skill-03",
            payload={'step': 1}
        )
        handoff2 = HandoffPackage(
            from_skill="skill-03",
            to_skill="skill-02",
            payload={'step': 2}
        )
        
        manager.save(handoff1)
        manager.save(handoff2)
        
        issues = manager.validate_chain()
        
        assert len(issues) == 0
    
    def test_validate_chain_broken(self, manager):
        """测试验证链路断裂"""
        handoff1 = HandoffPackage(
            from_skill="skill-00",
            to_skill="skill-03",
            payload={'step': 1}
        )
        handoff2 = HandoffPackage(
            from_skill="skill-02",  # 应该是 skill-03
            to_skill="skill-05",
            payload={'step': 2}
        )
        
        manager.save(handoff1)
        manager.save(handoff2)
        
        issues = manager.validate_chain()
        
        assert len(issues) > 0
        assert issues[0]['type'] == 'chain_break'
    
    def test_clear_session(self, manager):
        """测试清空会话"""
        handoff = HandoffPackage(
            from_skill="skill-00",
            to_skill="skill-03",
            payload={'test': 'data'}
        )
        
        manager.save(handoff)
        manager.clear()
        
        chain = manager.get_chain()
        assert len(chain) == 0
    
    def test_multiple_sessions(self, manager):
        """测试多会话"""
        handoff1 = HandoffPackage(
            from_skill="skill-00",
            to_skill="skill-03",
            payload={'session': 1}
        )
        handoff2 = HandoffPackage(
            from_skill="skill-00",
            to_skill="skill-02",
            payload={'session': 2}
        )
        
        manager.save(handoff1, session_id="session1")
        manager.save(handoff2, session_id="session2")
        
        chain1 = manager.get_chain("session1")
        chain2 = manager.get_chain("session2")
        
        assert len(chain1) == 1
        assert len(chain2) == 1
        assert chain1[0].to_skill == "skill-03"
        assert chain2[0].to_skill == "skill-02"
    
    def test_export_import_yaml(self, manager):
        """测试导出导入 YAML"""
        handoff = HandoffPackage(
            from_skill="skill-00",
            to_skill="skill-03",
            payload={'test': 'data'}
        )
        
        manager.save(handoff)
        exported = manager.export_session(format="yaml")
        
        # 清空后重新导入
        manager.clear()
        manager.import_session(exported, format="yaml")
        
        chain = manager.get_chain()
        assert len(chain) == 1
    
    def test_save_invalid_handoff(self, manager):
        """测试保存无效交接包"""
        handoff = HandoffPackage()  # 缺少必填字段
        
        with pytest.raises(ValueError):
            manager.save(handoff)


class TestEnums:
    """测试枚举类型"""
    
    def test_skill_id_values(self):
        """测试 SkillID 枚举值"""
        assert SkillID.SKILL_00.value == "skill-00"
        assert SkillID.SKILL_05.value == "skill-05"
        assert SkillID.USER.value == "user"
        assert SkillID.RELEASE.value == "release"
    
    def test_handoff_type_values(self):
        """测试 HandoffType 枚举值"""
        assert HandoffType.HP_A.value == "HP-A"
        assert HandoffType.HP_D.value == "HP-D"
        assert HandoffType.HP_F.value == "HP-F"
