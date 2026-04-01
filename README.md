# QCM-AI-DevTools

> **AI 驱动的开发工具平台 - 与 ai-skill-system 无缝对接**

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## 🎯 项目定位

| 维度 | 说明 |
|---|---|
| **目标用户** | 团队 |
| **核心价值** | 与 ai-skill-system 无缝对接 |
| **使用模式** | 可独立使用，也可对接 ai-skill-system |

---

## ✨ 核心特性

### 两种使用模式

```
模式一：独立使用
├── 团队开发工具集
├── 快速项目创建
├── 自动质量评估
└── 工作流编排

模式二：对接使用
├── ai-skill-system 代码化引擎
├── Navigator 意图识别
├── 交接包机制
└── Skill 代码实现
```

---

## 🚀 快速开始

### 安装

```bash
# 基础安装
pip install qcm-ai-devtools

# 包含 CLI 工具
pip install qcm-ai-devtools[cli]

# 开发模式
git clone https://github.com/qcm-ai-devtools/qcm-ai-devtools.git
cd qcm-ai-devtools
pip install -e ".[cli,dev]"
```

### CLI 使用

```bash
# 创建项目
qcm create "开发一个API系统"

# 质量评估
qcm assess ./my-project

# 意图识别
qcm navigate "找个开源的NLP库"

# 完整工作流
qcm workflow "开发情感分析API"

# 交接包管理
qcm handoff list
qcm handoff export -f yaml

# 项目信息
qcm info
qcm version
```

### Python API

```python
from qcm_tools import DevToolsWorkflow, Navigator

# 方式1：完整工作流
workflow = DevToolsWorkflow()
result = workflow.start_from_natural_language(
    "开发一个情感分析API系统"
)

# 方式2：意图识别
navigator = Navigator()
handoff = navigator.generate_handoff("开发一个API系统")
print(f"推荐路由: {handoff.to_skill}")
```

---

## 📦 核心工具

### 1. ConfigGenerator - 智能配置生成

```python
from qcm_tools import ConfigGenerator

generator = ConfigGenerator()
config = generator.generate_from_description(
    "开发一个企业级微服务API系统,使用FastAPI"
)
```

**特性**：
- 自动识别项目类型（研究/生产/教学/个人）
- 自动提取技术栈
- 自动推断项目规模
- 配置合理性验证

### 2. TemplateGenerator - 项目模板创建

```python
from qcm_tools import TemplateGenerator

generator = TemplateGenerator()
project_path = generator.create_project(config, "./my-project")
```

**模板类型**：8 种预定义模板，覆盖不同类型和规模

### 3. QualityAssessor - 质量评估

```python
from qcm_tools import QualityAssessor

assessor = QualityAssessor()
report = assessor.assess("./my-project")
print(f"得分: {report.overall_score}/100")
```

**评估维度**：代码质量、文档完整性、安全性

### 4. Navigator - 意图识别

```python
from qcm_tools.skills import Navigator

navigator = Navigator()
handoff = navigator.generate_handoff("找个开源库")
# handoff.to_skill == "skill-03"
```

**支持意图**：7 种意图类型，自动路由推荐

### 5. HandoffManager - 交接包管理

```python
from qcm_tools.handoff import HandoffManager

manager = HandoffManager()
manager.save(handoff)
chain = manager.get_chain()
```

**兼容性**：完全兼容 ai-skill-system schema v1.1

---

## 🔗 与 ai-skill-system 集成

### 交接包互通

QCM-AI-DevTools 生成的交接包可直接传递给 ai-skill-system：

```python
# 在 QCM-AI-DevTools 中生成
navigator = Navigator()
handoff = navigator.generate_handoff("开发一个系统")

# 导出交接包
yaml_str = handoff.to_yaml()

# 传递给 ai-skill-system 的下一个 Skill
# （复制 yaml_str 到 ai-skill-system 对话）
```

### 完整工作流示例

```python
from qcm_tools import DevToolsWorkflow

workflow = DevToolsWorkflow()

# Step 1: Navigator 分析意图
result = workflow.start_from_natural_language(
    "开发一个情感分析API系统"
)

# Step 2: 自动生成交接包
handoff = result['handoff']

# Step 3: 导出给 ai-skill-system 使用
yaml_output = handoff.to_yaml()
```

---

## 📁 项目结构

```
qcm-ai-devtools/
├── qcm_tools/
│   ├── config/           # 配置生成器
│   ├── template/         # 模板生成器
│   ├── quality/          # 质量评估器
│   ├── confidence/       # 置信度标注器
│   ├── skills/           # Skill 实现
│   │   └── navigator.py  # Navigator 导航官
│   ├── handoff/          # 交接包管理
│   ├── workflow.py       # 工作流编排器
│   ├── cli.py            # CLI 工具
│   └── shared/           # 共享模块
├── tests/                # 测试（119个）
├── examples/             # 示例代码
└── docs/                 # 文档
```

---

## 📚 文档

| 文档 | 说明 |
|---|---|
| [使用手册](USER-GUIDE.md) | 详细使用指南 |
| [CLI 文档](docs/CLI.md) | CLI 命令参考 |
| [API 文档](docs/API.md) | Python API 参考 |
| [集成指南](docs/INTEGRATION.md) | 与 ai-skill-system 集成 |

---

## 🧪 测试

```bash
# 运行所有测试
pytest

# 运行测试（无覆盖率）
pytest -p no:cacheprovider -o "addopts="

# 运行特定测试
pytest tests/test_navigator.py -v
```

**测试状态**：✅ 119/119 通过

---

## 📝 版本历史

### v0.4.0 (2025-03-31)
- ✅ CLI 工具实现
- ✅ DevToolsWorkflow 增强
- ✅ Navigator + HandoffManager 集成

### v0.3.0 (2025-03-31)
- ✅ Navigator（导航官）实现
- ✅ 意图识别与路由推荐

### v0.2.0 (2025-03-31)
- ✅ HandoffPackage 交接包机制
- ✅ HandoffManager 管理器
- ✅ ai-skill-system 兼容

### v0.1.0 (2025-03-31)
- ✅ 4 个核心工具实现
- ✅ 工作流编排器
- ✅ 41+ 测试用例

---

## 🤝 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

## 🙏 致谢

- ai-skill-system 团队
- QCM 框架设计团队
- 所有贡献者

---

**Made with ❤️ by QCM Team**
