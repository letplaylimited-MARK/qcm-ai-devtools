# QCM-AI-DevTools 与 ai-skill-system 桥接指南

**版本**: v1.0
**更新日期**: 2026-04-01

---

## 一、桥接机制概述

QCM-AI-DevTools 作为 **ai-skill-system 的代码化执行引擎**，通过 `Bridge` 层实现与 ai-skill-system 的无缝对接。

```
┌─────────────────────────────────────────────────────────────┐
│                      ai-skill-system                        │
│                   (六层协作 AI 工作流系统)                    │
├─────────────────────────────────────────────────────────────┤
│   skill-00    skill-01    skill-02    skill-03    ...       │
│   Navigator   Prompt     SOP        Scout                   │
│     │           │          │          │                     │
│     └───────────┴──────────┴──────────┘                     │
│                     │                                       │
│              YAML Handoff Package                           │
│                     │                                       │
│                     ▼                                       │
├─────────────────────────────────────────────────────────────┤
│                  AISkillSystemBridge                        │
│              (双向数据转换 + 格式验证)                        │
├─────────────────────────────────────────────────────────────┤
│                     │                                       │
│                     ▼                                       │
├─────────────────────────────────────────────────────────────┤
│                   QCM-AI-DevTools                           │
│                  (代码化执行引擎)                             │
├─────────────────────────────────────────────────────────────┤
│   Skills     Tools      Workflow      Infrastructure        │
│   Navigator  Config     DevTools      Exceptions            │
│   Scout      Template   Workflow      Logging               │
│   Planner    Quality                                        │
│   Validator  Handoff                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 二、核心桥接功能

### 2.1 Bridge 模块位置

```python
from qcm_tools.bridge import (
    AISkillSystemBridge,  # 主桥接类
    ExecutionFeedback,    # 执行反馈辅助类
    create_bridge,        # 工厂函数
    import_handoff,       # 快捷导入函数
    export_to_yaml        # 快捷导出函数
)
```

### 2.2 支持的数据格式

| 格式 | 导入 | 导出 | 用途 |
|------|------|------|------|
| **YAML** | ✅ | ✅ | ai-skill-system 标准格式 |
| **JSON** | ✅ | ✅ | API 交互格式 |

### 2.3 支持的交接包类型

| 类型标识 | 名称 | 方向 | 说明 |
|---------|------|------|------|
| `HP-A` | 意图交接 | skill-00 → skill-03/04 | Navigator 传递意图分析结果 |
| `HP-B` | 技术选型交接 | skill-03 → skill-04 | Scout 传递技术栈决策 |
| `HP-C` | 执行计划交接 | skill-04 → 执行层 | Planner 传递执行计划 |
| `HP-D` | 执行状态交接 | 执行层 → skill-05 | 执行进度反馈 |
| `HP-E` | 验收结果交接 | skill-05 → skill-00 | Validator 传递验收结果 |

---

## 三、使用示例

### 3.1 创建桥接器

```python
from qcm_tools.bridge import create_bridge

# 创建严格模式桥接器（推荐）
bridge = create_bridge(strict_mode=True)

# 创建宽松模式桥接器（用于调试）
bridge = create_bridge(strict_mode=False)
```

### 3.2 从 ai-skill-system 导入交接包

```python
# 方式一：从 YAML 字符串导入
yaml_str = """
schema_version: "1.1"
from_skill: "skill-00"
to_skill: "skill-03"
handoff_type: "HP-A"
payload:
  intent_type: "build_custom"
  tech_stack:
    - FastAPI
    - PostgreSQL
  requirements:
    performance: high
"""
handoff = bridge.import_from_skill_system(yaml_str, format="yaml")

# 方式二：从文件导入
handoff = bridge.import_from_skill_system("/path/to/handoff.yaml")

# 方式三：使用快捷函数
from qcm_tools.bridge import import_handoff
handoff = import_handoff(yaml_str)
```

### 3.3 导出到 ai-skill-system 格式

```python
from qcm_tools.handoff import create_handoff

# 创建交接包
handoff = create_handoff(
    from_skill="skill-05",
    to_skill="skill-00",
    handoff_type="HP-E",
    payload={
        "validation_result": "passed",
        "score": 0.92,
        "issues": []
    }
)

# 导出为 YAML
yaml_output = bridge.export_to_skill_system(handoff, format="yaml")
print(yaml_output)
# 输出:
# handoff:
#   schema_version: '1.1'
#   from_skill: skill-05
#   to_skill: skill-00
#   ...

# 导出为 JSON
json_output = bridge.export_to_skill_system(handoff, format="json")
```

### 3.4 加载 Skill Prompt 策略

```python
# 加载 Navigator 的默认 Prompt
prompt = bridge.load_prompt_from_skill_system("skill-00")
print(prompt)
# 输出 Navigator 的角色定义和任务描述

# 加载 Scout 的 Prompt
prompt = bridge.load_prompt_from_skill_system("skill-03")
```

### 3.5 创建执行反馈

```python
from qcm_tools.bridge import AISkillSystemBridge, ExecutionFeedback

bridge = AISkillSystemBridge()
feedback = ExecutionFeedback(bridge)

# 创建成功反馈
success_handoff = feedback.create_feedback_handoff(
    skill_id="skill-04",
    success=True,
    message="项目生成成功",
    details={"files_created": 15, "duration": "45s"}
)

# 创建错误反馈
error_handoff = feedback.create_error_handoff(
    skill_id="skill-04",
    error_message="配置文件解析失败",
    error_details={"file": "config.yaml", "line": 23}
)
```

---

## 四、完整工作流示例

### 4.1 标准 Skill 协作流程

```python
from qcm_tools.bridge import create_bridge
from qcm_tools.skills import Navigator, Scout, Planner, Validator
from qcm_tools.handoff import create_handoff

# 初始化
bridge = create_bridge()
navigator = Navigator()
scout = Scout()
planner = Planner()
validator = Validator()

# Step 1: Navigator 接收用户输入，分析意图
intent_result = navigator.analyze("创建一个高性能的 REST API 项目")

# Step 2: 创建 HP-A 交接包，传递给 Scout
handoff_to_scout = create_handoff(
    from_skill="skill-00",
    to_skill="skill-03",
    handoff_type="HP-A",
    payload={
        "intent_type": intent_result.intent_type,
        "requirements": intent_result.requirements
    }
)

# Step 3: Scout 接收交接包，进行技术选型
tech_result = scout.select(intent_result.requirements)

# Step 4: 创建 HP-B 交接包，传递给 Planner
handoff_to_planner = create_handoff(
    from_skill="skill-03",
    to_skill="skill-04",
    handoff_type="HP-B",
    payload={
        "tech_stack": tech_result.recommendations,
        "rationale": tech_result.rationale
    }
)

# Step 5: Planner 创建执行计划
execution_plan = planner.create_plan(tech_result.recommendations)

# Step 6: 执行完成后，Validator 验收
validation_result = validator.validate(execution_plan)

# Step 7: 创建 HP-E 交接包，反馈给 Navigator
handoff_feedback = create_handoff(
    from_skill="skill-05",
    to_skill="skill-00",
    handoff_type="HP-E",
    payload={
        "passed": validation_result.passed,
        "score": validation_result.score,
        "issues": validation_result.issues
    }
)

# Step 8: 导出到 ai-skill-system 格式
yaml_output = bridge.export_to_skill_system(handoff_feedback, format="yaml")
```

### 4.2 使用 DevToolsWorkflow 自动化

```python
from qcm_tools.workflow import DevToolsWorkflow
from qcm_tools.bridge import create_bridge

# 初始化工作流
workflow = DevToolsWorkflow()
bridge = create_bridge()

# 执行完整工作流
result = workflow.execute_ai_development(
    user_input="创建一个 FastAPI + PostgreSQL 的微服务项目",
    output_dir="./output/project"
)

# 导出结果给 ai-skill-system
for handoff in result.handoffs:
    yaml_str = bridge.export_to_skill_system(handoff, format="yaml")
    # 发送给 ai-skill-system 的下一个 Skill...
```

---

## 五、数据格式规范

### 5.1 YAML 交接包格式

```yaml
# ai-skill-system 标准交接包格式
handoff:
  # Schema 版本（必需）
  schema_version: "1.1"
  
  # 来源 Skill（必需）
  from_skill: "skill-00"
  
  # 目标 Skill（必需）
  to_skill: "skill-03"
  
  # 交接包类型（必需）
  handoff_type: "HP-A"
  
  # 时间戳（自动生成）
  timestamp: "2026-04-01T12:00:00Z"
  
  # 唯一标识（自动生成）
  package_id: "pkg-abc123"
  
  # 负载数据（根据类型变化）
  payload:
    intent_type: "build_custom"
    tech_stack:
      - FastAPI
      - PostgreSQL
    requirements:
      performance: high
      scalability: medium
  
  # 置信度标注（可选）
  confidence:
    overall: 0.85
    factors:
      clarity: 0.9
      feasibility: 0.8
```

### 5.2 Skill ID 映射

| Skill ID | 名称 | 角色 |
|----------|------|------|
| `skill-00` | Navigator | 意图识别与路由 |
| `skill-01` | Prompt Engineer | Prompt 优化 |
| `skill-02` | SOP Engineer | 标准流程制定 |
| `skill-03` | Scout | 技术调研与选型 |
| `skill-04` | Planner | 执行规划 |
| `skill-05` | Validator | 验收决策 |

---

## 六、错误处理

### 6.1 常见错误

```python
from qcm_tools.bridge import AISkillSystemBridge
from qcm_tools.exceptions import BridgeError

bridge = AISkillSystemBridge(strict_mode=True)

try:
    # 尝试导入无效的 YAML
    handoff = bridge.import_from_skill_system("invalid: yaml: content")
except BridgeError as e:
    print(f"桥接错误: {e}")
    # 处理错误...
```

### 6.2 版本兼容性检查

```python
# Bridge 会自动检查 schema_version
# 支持 "1.0" 和 "1.1" 版本

yaml_v1_0 = """
schema_version: "1.0"
from_skill: "skill-00"
# ... v1.0 格式
"""

yaml_v1_1 = """
schema_version: "1.1"
from_skill: "skill-00"
# ... v1.1 格式（包含置信度标注）
"""

# 两个版本都能正确导入
handoff_v1_0 = bridge.import_from_skill_system(yaml_v1_0)
handoff_v1_1 = bridge.import_from_skill_system(yaml_v1_1)
```

---

## 七、测试验证

### 7.1 运行桥接测试

```bash
cd /workspace/qcm-ai-devtools
python -m pytest tests/test_bridge.py -v
```

### 7.2 测试覆盖范围

| 测试项 | 状态 |
|--------|------|
| YAML 导入 | ✅ 通过 |
| JSON 导入 | ✅ 通过 |
| 文件导入 | ✅ 通过 |
| YAML 导出 | ✅ 通过 |
| JSON 导出 | ✅ 通过 |
| Prompt 加载 | ✅ 通过 |
| 执行反馈创建 | ✅ 通过 |
| 错误处理 | ✅ 通过 |

---

## 八、最佳实践

### 8.1 推荐使用模式

1. **始终使用 `strict_mode=True`**（默认），确保数据格式正确
2. **使用工厂函数** `create_bridge()` 而非直接实例化
3. **导出时使用 YAML 格式**，与 ai-skill-system 保持一致
4. **保留所有交接包**，便于追溯和调试

### 8.2 与 ai-skill-system 集成检查清单

- [ ] 确认 schema_version 为 "1.1"
- [ ] 验证 from_skill 和 to_skill 的 Skill ID 正确
- [ ] 检查 handoff_type 与实际流程匹配
- [ ] 确保 payload 数据结构符合预期
- [ ] 添加置信度标注（可选但推荐）

---

## 九、参考资源

- **QCM-AI-DevTools 完整规格**: `/workspace/QCM-AI-DEVTOOLS-COMPLETE-SPEC.md`
- **ai-skill-system 文档**: `/workspace/ai-skill-system/README.md`
- **接口合约**: `/workspace/ai-skill-system/interface-contracts/README.md`
- **Bridge 源码**: `/workspace/qcm-ai-devtools/qcm_tools/bridge.py`

---

**文档版本**: v1.0
**最后更新**: 2026-04-01
**维护者**: QCM Team
