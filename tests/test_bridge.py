"""
测试 ai-skill-system 桥接层（简化版）

验证交接包的双向转换核心功能
"""

import pytest
import tempfile
import os
from pathlib import Path

from qcm_tools.bridge import (
    AISkillSystemBridge,
    ExecutionFeedback,
    create_bridge,
    import_handoff,
    export_to_yaml
)
from qcm_tools.handoff import create_handoff, HandoffPackage


class TestAISkillSystemBridge:
    """测试桥接层核心功能"""

    def test_create_bridge(self):
        """测试创建桥接器"""
        bridge = create_bridge()
        assert isinstance(bridge, AISkillSystemBridge)
        assert bridge.strict_mode is True

        bridge = create_bridge(strict_mode=False)
        assert bridge.strict_mode is False

    def test_import_from_yaml_string(self):
        """测试从 YAML 字符串导入"""
        bridge = AISkillSystemBridge()

        yaml_str = """
schema_version: "1.1"
from_skill: "skill-00"
to_skill: "skill-04"
handoff_type: "HP-A"
payload:
  intent_type: "build_custom"
  tech_stack:
    - FastAPI
    - SQLAlchemy
"""

        handoff = bridge.import_from_skill_system(yaml_str, format="yaml")

        assert handoff.schema_version == "1.1"
        assert handoff.from_skill == "skill-00"
        assert handoff.to_skill == "skill-04"
        assert handoff.payload['intent_type'] == "build_custom"
        assert "FastAPI" in handoff.payload['tech_stack']

    def test_import_from_json_string(self):
        """测试从 JSON 字符串导入"""
        bridge = AISkillSystemBridge()

        json_str = """
{
  "schema_version": "1.1",
  "from_skill": "skill-00",
  "to_skill": "skill-04",
  "handoff_type": "HP-A",
  "payload": {
    "intent_type": "build_custom"
  }
}
"""

        handoff = bridge.import_from_skill_system(json_str, format="json")

        assert handoff.schema_version == "1.1"
        assert handoff.from_skill == "skill-00"
        assert handoff.payload['intent_type'] == "build_custom"

    def test_import_from_file(self):
        """测试从文件导入"""
        bridge = AISkillSystemBridge()

        yaml_content = """
schema_version: "1.1"
from_skill: "skill-00"
to_skill: "skill-04"
handoff_type: "HP-A"
payload:
  intent_type: "find_open_source"
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            temp_file = f.name

        try:
            handoff = bridge.import_from_skill_system(temp_file, format="yaml")
            assert handoff.from_skill == "skill-00"
            assert handoff.payload['intent_type'] == "find_open_source"
        finally:
            os.unlink(temp_file)

    def test_import_intent_from_yaml(self):
        """测试导入意图分析"""
        bridge = AISkillSystemBridge()

        yaml_str = """
intent_type: "build_custom"
confidence: 0.95
recommended_skill: "skill-04"
keywords:
  - API
  - FastAPI
project_summary:
  description: "开发一个 API 系统"
"""

        intent = bridge.import_intent_from_yaml(yaml_str)

        assert intent['intent_type'] == "build_custom"
        assert intent['confidence'] == 0.95
        assert intent['recommended_skill'] == "skill-04"
        assert "API" in intent['keywords']

    def test_import_tech_stack_from_yaml(self):
        """测试导入技术栈"""
        bridge = AISkillSystemBridge()

        yaml_str = """
tech_stack:
  - FastAPI
  - SQLAlchemy
  - PostgreSQL
"""

        stack = bridge.import_tech_stack_from_yaml(yaml_str)

        assert len(stack) == 3
        assert "FastAPI" in stack
        assert "SQLAlchemy" in stack

    def test_export_handoff_to_yaml(self):
        """测试导出 HandoffPackage 为 YAML"""
        bridge = AISkillSystemBridge()

        handoff = HandoffPackage(
            schema_version="1.1",
            from_skill="qcm-tools",
            to_skill="skill-05",
            handoff_type="HP-F",
            payload={'status': 'success'}
        )

        yaml_str = bridge.export_to_skill_system(handoff, format="yaml")

        assert "schema_version" in yaml_str
        assert "qcm-tools" in yaml_str
        assert "skill-05" in yaml_str

    def test_export_handoff_to_json(self):
        """测试导出 HandoffPackage 为 JSON"""
        bridge = AISkillSystemBridge()

        handoff = HandoffPackage(
            from_skill="qcm-tools",
            to_skill="skill-05",
            handoff_type="HP-F"
        )

        json_str = bridge.export_to_skill_system(handoff, format="json")

        assert '"from_skill"' in json_str or 'from_skill' in json_str
        assert '"to_skill"' in json_str or 'to_skill' in json_str


class TestSchemaVersionValidation:
    """测试 Schema 版本验证"""

    def test_supported_version_1_0(self):
        """测试支持的版本 1.0"""
        bridge = AISkillSystemBridge(strict_mode=True)

        yaml_str = """
schema_version: "1.0"
from_skill: "skill-00"
to_skill: "skill-04"
handoff_type: "HP-A"
"""

        handoff = bridge.import_from_skill_system(yaml_str)
        assert handoff.schema_version == "1.0"

    def test_supported_version_1_1(self):
        """测试支持的版本 1.1"""
        bridge = AISkillSystemBridge(strict_mode=True)

        yaml_str = """
schema_version: "1.1"
from_skill: "skill-00"
to_skill: "skill-04"
handoff_type: "HP-A"
"""

        handoff = bridge.import_from_skill_system(yaml_str)
        assert handoff.schema_version == "1.1"

    def test_unsupported_version_strict_mode(self):
        """测试不支持的版本（严格模式）"""
        bridge = AISkillSystemBridge(strict_mode=True)

        yaml_str = """
schema_version: "2.0"
from_skill: "skill-00"
to_skill: "skill-04"
"""

        with pytest.raises(ValueError) as exc_info:
            bridge.import_from_skill_system(yaml_str)

        assert "不支持的 schema 版本" in str(exc_info.value)

    def test_unsupported_version_non_strict_mode(self):
        """测试不支持的版本（非严格模式）"""
        bridge = AISkillSystemBridge(strict_mode=False)

        yaml_str = """
schema_version: "2.0"
from_skill: "skill-00"
to_skill: "skill-04"
"""

        # 非严格模式应该不抛出异常
        handoff = bridge.import_from_skill_system(yaml_str)
        assert handoff is not None


class TestPromptLoading:
    """测试 Prompt 加载"""

    def test_get_default_prompt_skill_00(self):
        """测试获取 skill-00 默认 Prompt"""
        bridge = AISkillSystemBridge()

        prompt = bridge._get_default_prompt("skill-00")

        assert "Navigator" in prompt
        assert "意图" in prompt

    def test_get_default_prompt_skill_03(self):
        """测试获取 skill-03 默认 Prompt"""
        bridge = AISkillSystemBridge()

        prompt = bridge._get_default_prompt("skill-03")

        assert "Scout" in prompt
        assert "七维度" in prompt

    def test_get_default_prompt_unknown_skill(self):
        """测试获取未知 Skill 的默认 Prompt"""
        bridge = AISkillSystemBridge()

        prompt = bridge._get_default_prompt("skill-99")

        assert "AI 助手" in prompt


class TestConvenienceFunctions:
    """测试便捷函数"""

    def test_create_bridge_function(self):
        """测试创建桥接器函数"""
        bridge = create_bridge()
        assert isinstance(bridge, AISkillSystemBridge)

    def test_import_handoff_function(self):
        """测试导入交接包函数"""
        yaml_str = """
schema_version: "1.1"
from_skill: "skill-00"
to_skill: "skill-04"
handoff_type: "HP-A"
"""

        handoff = import_handoff(yaml_str)
        assert handoff.from_skill == "skill-00"

    def test_export_to_yaml_function(self):
        """测试导出为 YAML 函数"""
        handoff = HandoffPackage(
            from_skill="qcm-tools",
            to_skill="skill-05"
        )

        yaml_str = export_to_yaml(handoff)
        assert "qcm-tools" in yaml_str


class TestEdgeCases:
    """测试边缘情况"""

    def test_empty_payload(self):
        """测试空 payload"""
        bridge = AISkillSystemBridge()

        yaml_str = """
schema_version: "1.1"
from_skill: "skill-00"
to_skill: "skill-04"
"""

        handoff = bridge.import_from_skill_system(yaml_str)
        assert handoff.payload == {}

    def test_complex_payload(self):
        """测试复杂 payload"""
        bridge = AISkillSystemBridge()

        yaml_str = """
schema_version: "1.1"
from_skill: "skill-00"
to_skill: "skill-04"
payload:
  nested:
    level1:
      level2:
        - item1
        - item2
  numbers:
    - 1
    - 2
    - 3
"""

        handoff = bridge.import_from_skill_system(yaml_str)
        assert handoff.payload['nested']['level1']['level2'] == ['item1', 'item2']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
