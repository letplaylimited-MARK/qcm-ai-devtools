# QCM-AI-DevTools
<div align="center">

**让开发团队用自然语言，1分钟生成生产就绪的项目**

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-241%20passed-brightgreen.svg)](tests/)

[快速开始](#-快速开始) • [功能特性](#-功能特性) • [使用指南](docs/USER-GUIDE.md) • [API 文档](docs/API-REFERENCE.md)

</div>

---

## 🎯 我们解决什么问题？

### 传统项目开发的痛点

| 痛点 | 传统方式 | QCM-AI-DevTools |
|------|---------|-----------------|
| **项目初始化** | 30分钟手动配置 | <1分钟自动生成 |
| **代码质量** | 人工审查耗时 | AI 自动检测问题 |
| **技术选型** | 信息分散难选 | AI 七维度评估 |
| **团队规范** | 每人一个风格 | 统一标准化模板 |

### 真实用户案例

> **李明 - 某互联网公司技术负责人**
>
> "以前每次启动新项目都要花半小时配置，现在用自然语言描述需求，1分钟就生成了符合团队规范的项目，效率提升 95%！"

---

## ✨ 核心功能

### ⚡ 极速启动项目

**用自然语言描述需求，1分钟生成完整项目**

```bash
# 输入自然语言
qcm create "开发一个用户管理 API，使用 FastAPI 和 PostgreSQL"

# 自动生成
✅ 项目结构标准化
✅ 配置文件完整
✅ 测试框架内置
✅ 文档自动生成
✅ Docker 支持
```

**生成内容**:
```
my-project/
├── main.py              # 应用入口
├── models/              # 数据模型
│   └── user.py
├── api/                 # API 路由
│   └── users.py
├── tests/               # 测试用例
│   └── test_users.py
├── requirements.txt     # 依赖管理
├── Dockerfile          # Docker 配置
└── README.md           # 项目文档
```

### 🎯 智能质量保障

**AI 自动审查代码，提前发现 90% 的问题**

```bash
# 质量评估
qcm assess ./my-project

# 五维度评估报告
✓ 代码质量: 85/100
✓ 文档完整性: 90/100
✓ 可执行性: 100/100
✓ 接口规范: 80/100
✓ 安全性: 75/100

# 发现问题
⚠️ 发现 3 个问题:
  1. [安全性] user.py:45 - 潜在 SQL 注入风险
  2. [代码质量] api/users.py:23 - 缺少类型注解
  3. [文档] README.md - 缺少安装说明

# 修复建议
💡 修复建议:
  1. 使用参数化查询替代字符串拼接
  2. 添加函数参数类型注解
  3. 补充安装步骤文档
```

### 🤖 AI 技术顾问

**不懂技术选型？AI 帮你七维度评估**

```bash
# 技术选型
qcm recommend "需要高性能的 Web 框架"

# 七维度评估对比
评估对比:
┌─────────────┬────────┬────────┬────────┐
│ 维度        │ FastAPI│ Flask  │ Django │
├─────────────┼────────┼────────┼────────┤
│ 功能性      │   90   │   75   │   95   │
│ 易用性      │   85   │   90   │   70   │
│ 性能        │   95   │   80   │   70   │
│ 可维护性    │   85   │   80   │   85   │
│ 社区活跃度  │   90   │   95   │   95   │
│ 兼容性      │   90   │   90   │   85   │
│ 文档        │   95   │   90   │   95   │
├─────────────┼────────┼────────┼────────┤
│ 综合评分    │   89.5 │   83.5 │   83.0 │
└─────────────┴────────┴────────┴────────┘

推荐: FastAPI（综合评分 89.5）

理由:
✅ 性能优异（异步支持）
✅ 类型安全（自动校验）
✅ 文档完善（自动生成 API 文档）
```

### 👥 团队标准化

**统一团队项目规范，告别每人一个风格**

```yaml
# team-standards.yaml
project_template: "standard-api"
code_style: "black"
test_framework: "pytest"
documentation: "google"

# 自动应用团队规范
qcm create "开发订单管理 API" --template team-standards
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

### 1分钟快速体验

```bash
# 1. 创建项目（30秒）
qcm create "开发一个博客 API" -o ./my-blog

# 2. 查看生成的项目
cd my-blog
ls -la

# 3. 质量评估（10秒）
qcm assess .

# 4. 运行项目
python main.py
```

### Python API 使用

```python
from qcm_tools import DevToolsWorkflow

# 创建工作流
workflow = DevToolsWorkflow()

# 从自然语言创建项目
result = workflow.create_project_from_description(
    "开发一个用户管理 API，包含注册、登录、权限管理"
)

# 查看结果
print(f"项目路径: {result['project_path']}")
print(f"质量评分: {result['quality_report'].overall_score}/100")

# 技术选型
from qcm_tools.skills import Scout

scout = Scout()
recommendation = await scout.recommend_best(
    requirement="高性能 Web 框架",
    language="python"
)

print(f"推荐: {recommendation.library.name}")
print(f"评分: {recommendation.overall_score}/100")
```

---

## 📖 使用场景

### 场景 1：新项目快速启动

**传统方式**: 30分钟手动配置
**QCM 方式**: 1分钟自动生成

```bash
# 输入需求
qcm create "电商平台 API，包含用户、商品、订单模块"

# 自动生成
✅ 完整项目结构
✅ 数据库模型
✅ API 路由
✅ 测试用例
✅ 文档
```

### 场景 2：代码质量保障

**传统方式**: 人工审查，耗时且易遗漏
**QCM 方式**: AI 自动检测 + 修复建议

```bash
# 自动审查
qcm assess ./my-project

# 发现问题 + 建议修复
⚠️ 发现 5 个问题
💡 提供修复建议
🔧 一键修复（开发中）
```

### 场景 3：技术方案选型

**传统方式**: 信息分散，难以对比
**QCM 方式**: AI 七维度评估 + 智能推荐

```bash
# 智能推荐
qcm recommend "实时数据处理框架"

# 多维度对比
FastAPI vs Flask vs Django
✅ 性能对比
✅ 易用性分析
✅ 社区活跃度
✅ 文档完整性
```

---

## 🛠️ CLI 命令参考

```bash
# 项目创建
qcm create <描述> [选项]
  --output, -o      输出路径
  --no-assess       跳过质量评估

# 质量评估
qcm assess <项目路径> [选项]
  --format          输出格式 (text/json/markdown)

# 意图识别
qcm navigate <需求描述>

# 技术选型
qcm recommend <需求描述> [选项]
  --language        编程语言
  --limit           候选数量

# 完整工作流
qcm workflow <需求描述> [选项]
  --with-validation 启用质量验证

# 交接包管理
qcm handoff list              # 列出交接包
qcm handoff export [选项]     # 导出交接包
  --format          格式 (yaml/json)

# 项目信息
qcm info          # 项目信息
qcm version       # 版本信息
```

---

## 📚 文档

- **[用户指南](docs/USER-GUIDE.md)** - 详细使用教程
- **[API 文档](docs/API-REFERENCE.md)** - 完整 API 参考
- **[用户画像](docs/USER-PERSONAS.md)** - 目标用户定义
- **[价值主张](docs/VALUE-PROPOSITION.md)** - 产品价值说明

---

## 🎓 学习资源

### 示例项目

```bash
# 查看示例
ls examples/
├── basic_usage.py          # 基础用法
├── advanced_workflow.py    # 高级工作流
├── ai_integration.py       # AI 集成
└── team_standards.py       # 团队标准
```

### 视频教程（计划中）

1. **快速上手** - 5分钟入门
2. **团队协作** - 标准化实践
3. **AI 增强** - 智能开发技巧

---

## 🤝 与 ai-skill-system 集成

QCM-AI-DevTools 可以与 [ai-skill-system](https://github.com/ai-skill-system) 无缝对接：

```python
from qcm_tools.bridge import AISkillSystemBridge
from qcm_tools.skills import Scout

# 从 ai-skill-system 导入交接包
bridge = AISkillSystemBridge()
handoff = bridge.import_from_skill_system("navigator_handoff.yaml")

# 使用 Scout 技术选型
scout = Scout()
evaluation = await scout.recommend_best(
    requirement=handoff.payload['requirement']
)

# 导出给 ai-skill-system
result_handoff = scout.create_handoff(evaluation)
yaml_str = bridge.export_to_skill_system(result_handoff)
```

---

## 🏢 企业版功能

需要企业级功能？我们提供：

- ✅ **私有部署** - 在自己的服务器上运行
- ✅ **权限管理** - 细粒度权限控制
- ✅ **审计日志** - 完整的操作记录
- ✅ **定制开发** - 根据需求定制功能
- ✅ **技术支持** - 专属技术支持团队

[联系我们](mailto:enterprise@qcm-ai-devtools.com) 了解更多

---

## 📊 性能指标

| 操作 | 耗时 | 说明 |
|------|------|------|
| 项目生成 | <1分钟 | 包含所有标准组件 |
| 质量评估 | <30秒 | 五维度完整评估 |
| 技术选型 | <1分钟 | AI 七维度评估 |
| 意图识别 | <5秒 | AI 智能识别 |

---

## 🤝 贡献

我们欢迎所有形式的贡献！

- 🐛 [报告 Bug](https://github.com/qcm-ai-devtools/qcm-ai-devtools/issues)
- 💡 [功能建议](https://github.com/qcm-ai-devtools/qcm-ai-devtools/issues)
- 📖 [改进文档](https://github.com/qcm-ai-devtools/qcm-ai-devtools/pulls)
- 🔧 [提交代码](https://github.com/qcm-ai-devtools/qcm-ai-devtools/pulls)

查看 [贡献指南](CONTRIBUTING.md) 了解详情

---

## 📄 License

MIT License - 详见 [LICENSE](LICENSE)

---

## 💬 社区

- **GitHub Discussions** - 讨论和问答
- **Discord** - 实时交流（计划中）
- **Twitter** - 最新动态 [@qcm_devtools](https://twitter.com/qcm_devtools)

---

<div align="center">

**让 AI 成为你的开发助手**

[开始使用](#-快速开始) | [查看文档](docs/USER-GUIDE.md) | [反馈问题](https://github.com/qcm-ai-devtools/qcm-ai-devtools/issues)

</div>
