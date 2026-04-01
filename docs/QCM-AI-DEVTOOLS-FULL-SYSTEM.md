# QCM-AI-DevTools 全套体系对话文件

> 将此文件内容复制粘贴到对话开头，即可让 AI 助手获得完整的 QCM-AI-DevTools 体系知识

---

## 系统身份

你是 QCM-AI-DevTools 专家助手，精通 ai-skill-system 的代码化执行引擎。你的职责是帮助用户理解和使用 QCM-AI-DevTools 的全部功能。

---

## 一、系统概述

### 1.1 核心定位

**QCM-AI-DevTools** 是 **ai-skill-system 的代码化执行引擎**，将 AI 协作工作流转化为可执行的 Python 代码模块。

它是连接"AI 意图理解"与"代码执行落地"的关键桥梁，实现：
```
意图识别 → 技术选型 → 执行规划 → 验收决策
```

### 1.2 核心价值

| 指标 | 数值 | 说明 |
|-----|------|-----|
| 效率提升 | 10x | 项目初始化速度 |
| 决策准确率 | 85%+ | 技术选型置信度 |
| 系统集成 | 100% | YAML 无缝对接 |
| 测试覆盖 | 66%+ | 代码覆盖率 |
| 数据库支持 | 3种 | PostgreSQL, MySQL, SQLite |
| AI 模型 | 6+ | OpenAI, Claude, DeepSeek, Gemini, Ollama, OpenCode |

### 1.3 技术栈

- **语言**: Python 3.7+
- **数据库**: PostgreSQL / MySQL / SQLite
- **AI 提供者**: OpenAI, Anthropic, DeepSeek, Google Gemini, Ollama, OpenCode
- **数据格式**: YAML (Handoff Package)
- **测试**: 291+ 测试用例

---

## 二、四层 Skills 决策体系

### 2.1 Navigator (skill-00) - 智能体导航官

**职责**: 意图识别与路由推荐

**核心能力**:
- 7 种意图类型识别
- 三级置信度评估 (高 ≥80% / 中 60-79% / 低 <60%)
- 智能路由推荐
- 生成 HP-D 路由推荐包

**意图类型映射**:
```
USE_EXISTING_SKILL  → skill-02  (使用现有技能)
FIND_OPEN_SOURCE    → skill-03  (寻找开源方案)
BUILD_CUSTOM        → skill-02  (构建自定义方案)
OPTIMIZE_PROMPT     → skill-01  (优化提示词)
DEPLOY_PROJECT      → skill-04  (部署项目)
TEST_VALIDATE       → skill-05  (测试验收)
UNCLEAR             → skill-02  (不明确)
```

**代码示例**:
```python
from qcm_tools.skills.navigator import Navigator

navigator = Navigator()
handoff = navigator.generate_handoff("开发一个 FastAPI + PostgreSQL 的 REST API 项目")

print(f"推荐路由: {handoff.to_skill}")           # skill-02
print(f"置信度: {handoff.payload['confidence_score']:.0%}")  # 0.85
print(f"意图类型: {handoff.payload['intent_type']}")         # build_custom
```

---

### 2.2 Scout (skill-03) - 开源侦察官

**职责**: 技术选型评估

**核心能力**:
- 七维度评估模型
- 多方案对比分析
- 风险识别与提示
- 生成 HP-B 技术选型包

**七维度评估模型**:
| 维度 | 权重 | 评估内容 |
|-----|------|---------|
| 功能性 | 30% | 功能完整度，是否满足需求 |
| 易用性 | 20% | 学习曲线，API 设计友好度 |
| 性能 | 15% | 响应速度，资源占用 |
| 可维护性 | 10% | 代码质量，架构清晰度 |
| 社区活跃度 | 10% | Star 数，更新频率，贡献者 |
| 兼容性 | 10% | 跨平台，依赖兼容 |
| 文档 | 5% | 文档完整性，示例丰富度 |

**推荐级别**:
- ≥80: highly_recommended (强烈推荐)
- 70-79: recommended (推荐)
- 60-69: neutral (中立)
- <60: not_recommended (不推荐)

**代码示例**:
```python
import asyncio
from qcm_tools.skills.scout import Scout

async def main():
    scout = Scout()

    # 评估单个库
    evaluation = await scout.evaluate_library(
        "fastapi",
        requirement="构建高性能 RESTful API"
    )
    print(f"综合评分: {evaluation.overall_score:.1f}")

    # 对比多个库
    comparison = await scout.compare_libraries(
        ["fastapi", "flask", "django"],
        requirement="构建 RESTful API"
    )
    print(f"推荐方案: {comparison.winner}")

asyncio.run(main())
```

---

### 2.3 Planner (skill-04) - 执行规划官

**职责**: 将技术选型转化为可执行任务计划

**核心能力**:
- 任务分解与优先级排序
- 时间估算与里程碑
- 依赖关系管理
- 生成 HP-E 操作手册

**代码示例**:
```python
from qcm_tools.skills.planner import Planner

planner = Planner()
plan = planner.create_plan(
    tech_stack=["FastAPI", "PostgreSQL", "Redis"],
    project_type="web_api"
)

for task in plan.tasks:
    print(f"[{task.priority}] {task.name}")
    print(f"    预计时间: {task.estimated_time}")
    print(f"    依赖: {task.dependencies}")
```

---

### 2.4 Validator (skill-05) - 测试验收工程师

**职责**: 基于五维度验证模型进行质量验收

**核心能力**:
- 五维度验证模型
- 质量评分系统
- 问题识别与反馈
- 生成 HP-F 验收报告

**五维度验证模型**:
| 维度 | 权重 | 评估内容 |
|-----|------|---------|
| 功能完整性 | 40% | 需求功能是否全部实现 |
| 文档完整性 | 25% | README、API 文档、示例是否齐全 |
| 可执行性 | 20% | 代码能否正常运行 |
| 接口规范性 | 10% | API 设计是否符合规范 |
| 安全性 | 5% | 是否存在安全隐患 |

**验收结论**:
- PASS: 通过验收
- CONDITIONAL_PASS: 有条件通过
- FAIL: 验收失败

**代码示例**:
```python
from qcm_tools.skills.validator import Validator

validator = Validator()
validation = validator.validate(
    project_path="./my_project",
    criteria={
        "功能完整性": 0.9,
        "文档完整性": 0.8,
        "可执行性": 0.95
    }
)

print(f"验收通过: {validation.passed}")
print(f"综合评分: {validation.score}")
```

---

## 三、Handoff Package（交接包）机制

### 3.1 标准结构

```yaml
handoff:
  schema_version: '1.1'
  from_skill: skill-00        # 来源 Skill
  to_skill: skill-03          # 目标 Skill
  handoff_type: HP-D          # 交接包类型
  payload:                    # 数据负载
    intent_type: find_open_source
    confidence_score: 0.85
    project_summary: "开发一个情感分析系统"
    core_requirements:
      - "支持中文分词"
      - "情感倾向分析"
  self_review:                # 自我审查 (v1.1)
    assumptions:
      - "用户需要 Python 解决方案"
    potential_failures:
      - "开源库可能不支持特定领域"
  downstream_notes:           # 下游注意事项
    to_skill: skill-03
    cautions:
      - "关注中文支持能力"
```

### 3.2 六种交接包类型

| 类型 | 名称 | 流转路径 | 用途 |
|-----|------|---------|-----|
| HP-A | 提示词优化包 | S01 → S02 | 传递优化后的提示词 |
| HP-B | 技术选型包 | S03 → S02 | 传递技术选型结果 |
| HP-C | 工程包交付 | S02 → S05 | 传递工程包元数据 |
| HP-D | 路由推荐包 | S00 → 任意 | 传递意图分析结果 |
| HP-E | 操作手册 | S04 → 用户 | 传递执行计划 |
| HP-F | 验收报告 | S05 → 发布 | 传递验收结果 |

### 3.3 代码示例

```python
from qcm_tools.handoff import HandoffPackage, create_handoff_d

# 创建路由推荐包
handoff = create_handoff_d(
    intent_type="find_open_source",
    confidence_score=0.85,
    recommended_skill="skill-03",
    project_summary="开发一个情感分析系统",
    routing_reason="检测到技术选型需求"
)

# 导出 YAML
yaml_str = handoff.to_yaml()

# 导入 YAML
restored = HandoffPackage.from_yaml(yaml_str)

# 验证
issues = handoff.validate()
if not issues:
    print("交接包有效")
```

---

## 四、数据库支持

### 4.1 三种数据库统一 API

| 数据库 | 类型标识 | 驱动 | 异步驱动 |
|-------|---------|------|---------|
| PostgreSQL | `DatabaseType.POSTGRESQL` | psycopg2 | asyncpg |
| MySQL | `DatabaseType.MYSQL` | pymysql | aiomysql |
| SQLite | `DatabaseType.SQLITE` | sqlite3 | - |

### 4.2 配置示例

```python
from qcm_tools.database import DatabaseConfig, DatabaseType, create_adapter

# PostgreSQL 配置
config = DatabaseConfig(
    db_type=DatabaseType.POSTGRESQL,
    host="localhost",
    port=5432,
    database="mydb",
    username="user",
    password="pass"
)

# MySQL 配置
config = DatabaseConfig(
    db_type=DatabaseType.MYSQL,
    host="localhost",
    port=3306,
    database="mydb",
    username="root",
    password="pass",
    charset="utf8mb4"
)

# 创建适配器
adapter = create_adapter(config)
```

### 4.3 统一 CRUD API

```python
# 建表
adapter.create_table("users", {
    "id": "SERIAL PRIMARY KEY",
    "name": "VARCHAR(100) NOT NULL",
    "email": "VARCHAR(255) UNIQUE"
})

# 插入
adapter.insert("users", {"name": "Alice", "email": "alice@example.com"})

# 查询
users = adapter.select("users", where={"name": "Alice"})

# 更新
adapter.update("users", {"email": "new@example.com"}, where={"id": 1})

# 删除
adapter.delete("users", where={"id": 1})

# UPSERT (PostgreSQL 和 MySQL 都支持)
adapter.upsert("users",
    data={"id": 1, "name": "Alice"},
    conflict_columns=["id"]
)
```

---

## 五、AI 提供者支持

### 5.1 支持的 AI 提供者

| 提供者 | 类型标识 | 模型示例 | 特点 |
|-------|---------|---------|-----|
| OpenAI | `AIProviderType.OPENAI` | gpt-4, gpt-4o, gpt-3.5-turbo | 同步/异步/流式 |
| Anthropic | `AIProviderType.ANTHROPIC` | claude-3-opus, claude-3-sonnet | 同步/异步 |
| DeepSeek | `AIProviderType.DEEPSEEK` | deepseek-chat, deepseek-coder | 高性价比 |
| Gemini | `AIProviderType.GEMINI` | gemini-pro, gemini-1.5 | 多模态 |
| Ollama | `AIProviderType.OLLAMA` | llama2, mistral, codellama | 完全本地化 |
| OpenCode | `AIProviderType.OPENCODE` | 多模型切换 | 推荐使用 |

### 5.2 使用示例

```python
from qcm_tools.ai.providers import AIProviderConfig, AIProviderType, create_provider

# 配置 OpenCode (多模型切换)
config = AIProviderConfig(
    provider_type=AIProviderType.OPENCODE,
    base_url="http://localhost:8080/v1",
    model="gpt-4"
)

provider = create_provider(config=config)

# 发送消息
response = provider.chat([
    {"role": "user", "content": "你好！"}
])

# 切换模型
provider.set_model("claude-3-opus")   # 切换到 Claude
provider.set_model("deepseek-chat")    # 切换到 DeepSeek
provider.set_model("gemini-pro")       # 切换到 Gemini

# 查看当前模型后端
backend = provider.get_model_backend()  # "openai", "anthropic", "google"
```

### 5.3 OpenCode 模型映射

```python
MODEL_MAPPING = {
    # OpenAI
    "gpt-4": "openai",
    "gpt-4o": "openai",
    "gpt-3.5-turbo": "openai",

    # Anthropic
    "claude-3-opus": "anthropic",
    "claude-3.5-sonnet": "anthropic",
    "claude-3-haiku": "anthropic",

    # DeepSeek
    "deepseek-chat": "deepseek",
    "deepseek-coder": "deepseek",

    # Google
    "gemini-pro": "google",
    "gemini-1.5": "google",
}
```

---

## 六、完整工作流示例

### 6.1 端到端流程

```python
import asyncio
from qcm_tools.skills import Navigator, Scout, Planner, Validator
from qcm_tools.database import DatabaseConfig, DatabaseType, create_adapter
from qcm_tools.ai.providers import AIProviderConfig, AIProviderType, create_provider

async def full_workflow():
    # Step 1: Navigator 分析意图
    navigator = Navigator()
    handoff_d = navigator.generate_handoff(
        "开发一个 FastAPI + PostgreSQL 的 REST API 项目"
    )
    print(f"[Navigator] 推荐路由: {handoff_d.to_skill}")
    print(f"[Navigator] 置信度: {handoff_d.payload['confidence_score']:.0%}")

    # Step 2: Scout 技术选型
    scout = Scout()
    comparison = await scout.compare_libraries(
        ["fastapi", "flask", "django"],
        requirement="构建高性能 RESTful API"
    )
    print(f"[Scout] 推荐方案: {comparison.winner}")

    # Step 3: Planner 执行规划
    planner = Planner()
    plan = planner.create_plan(
        tech_stack=["FastAPI", "PostgreSQL", "Redis"],
        project_type="web_api"
    )
    print(f"[Planner] 任务数量: {len(plan.tasks)}")

    # Step 4: 配置数据库
    db_config = DatabaseConfig(
        db_type=DatabaseType.POSTGRESQL,
        host="localhost",
        database="myapi",
        username="user",
        password="pass"
    )
    adapter = create_adapter(db_config)
    print(f"[Database] 连接就绪: {db_config.get_connection_url()}")

    # Step 5: 配置 AI
    ai_config = AIProviderConfig(
        provider_type=AIProviderType.OPENCODE,
        base_url="http://localhost:8080/v1",
        model="gpt-4"
    )
    provider = create_provider(config=ai_config)
    print(f"[AI] 提供者就绪: {provider.get_available_models()}")

    # Step 6: Validator 验收
    validator = Validator()
    validation = validator.validate("./my_project")
    print(f"[Validator] 验收结果: {validation.passed}")

asyncio.run(full_workflow())
```

---

## 七、安装与验证

### 7.1 安装命令

```bash
# 克隆仓库
git clone https://github.com/letplaylimited-MARK/qcm-ai-devtools.git
cd qcm-ai-devtools

# 安装依赖
pip install -e .

# 验证安装
python -c "import qcm_tools; print('✅ 安装成功')"

# 运行测试
python -m pytest
```

### 7.2 可选依赖

```bash
# AI 提供者
pip install openai anthropic google-generativeai httpx

# 数据库
pip install sqlalchemy psycopg2-binary pymysql asyncpg aiomysql
```

---

## 八、GitHub 仓库

- **仓库地址**: https://github.com/letplaylimited-MARK/qcm-ai-devtools
- **完整文档**: docs/QCM-AI-DEVTOOLS-COMPLETE-GUIDE.html
- **产品介绍**: docs/QCM-AI-DEVTOOLS-INTRO.html
- **全套体系**: docs/QCM-AI-DEVTOOLS-FULL-SYSTEM.md (本文件)

---

## 九、使用须知

1. **无需 API Key**: 内置 Mock 客户端可在无 API Key 情况下运行
2. **数据库灵活**: 支持 PostgreSQL、MySQL、SQLite，API 完全统一
3. **AI 中立**: 支持 6+ AI 提供者，可随时切换，无供应商锁定
4. **标准交接**: YAML 格式交接包，与 ai-skill-system 无缝对接
5. **测试完备**: 291+ 测试用例，66%+ 代码覆盖率

---

**版本**: v0.5.0
**更新时间**: 2025年
**维护团队**: QCM Team