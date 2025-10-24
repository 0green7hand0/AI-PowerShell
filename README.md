# AI PowerShell 智能助手

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![PowerShell](https://img.shields.io/badge/powershell-core%207.0+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-windows%20%7C%20linux%20%7C%20macos-lightgrey.svg)
![AI Model](https://img.shields.io/badge/ai-local%20processing-orange.svg)
![Language](https://img.shields.io/badge/language-中文%20%7C%20english-red.svg)
![Version](https://img.shields.io/badge/version-v2.0.0-brightgreen.svg)

一个基于本地 AI 模型的智能 PowerShell 命令行助手，采用模块化架构设计，支持中文自然语言交互，提供三层安全保护机制。该系统通过高内聚低耦合的设计原则，确保代码的可维护性和可扩展性。

## 📚 快速导航

- [🚀 快速开始](#快速开始)
- [📖 完整文档索引](DOCUMENTATION.md) - 所有文档导航门户
- [📖 中文文档](中文项目说明.md)
- [📋 快速开始指南](快速开始.md)
- [📁 项目结构](#项目结构)
- [🔧 安装说明](#安装)
- [📚 文档中心](docs/README.md)

> **📢 文档重构说明**: 我们最近完成了文档体系的全面重构，将28个文档精简整合为15个核心文档，建立了清晰的三层架构（入门层、深入层、参考层）。所有文档内容已完整保留并优化组织。查看 [文档迁移映射表](docs/migration-map.md) 了解详情。

## 核心特性

- **模块化架构**: 采用高内聚低耦合的设计，6 个核心模块清晰分离
- **自然语言处理**: 使用本地 AI 模型将中文/英文转换为 PowerShell 命令
- **自定义模板系统**: 创建、管理和共享您自己的 PowerShell 脚本模板
- **三层安全保护**: 命令白名单、权限检查和沙箱执行的完整安全体系
- **跨平台支持**: 在 Windows、Linux 和 macOS 上与 PowerShell Core 协同工作
- **本地 AI 处理**: 注重隐私的本地模型执行 - 不向外部服务发送数据
- **完整日志系统**: 结构化日志记录、审计跟踪和性能监控
- **灵活配置管理**: 基于 YAML 的配置系统，支持多层级配置
- **现代化 CLI 界面**: 彩色输出、进度指示、交互式输入和智能提示
- **增强的用户体验**: 友好的错误提示、自动补全和命令历史记录

## 项目结构

```
AI-PowerShell/
├── src/                   # 源代码目录（模块化架构）
│   ├── interfaces/        # 接口定义层
│   ├── ai_engine/         # AI 引擎模块
│   ├── security/          # 安全引擎模块
│   ├── execution/         # 执行引擎模块
│   ├── config/            # 配置管理模块
│   ├── log_engine/        # 日志引擎模块
│   ├── storage/           # 存储引擎模块
│   ├── context/           # 上下文管理模块
│   ├── ui/                # UI 系统模块
│   └── main.py            # 主入口文件
├── tests/                 # 测试目录
│   ├── ai_engine/         # AI 引擎测试
│   ├── security/          # 安全引擎测试
│   ├── execution/         # 执行引擎测试
│   ├── config/            # 配置管理测试
│   ├── log_engine/        # 日志引擎测试
│   ├── storage/           # 存储引擎测试
│   ├── context/           # 上下文管理测试
│   └── integration/       # 集成测试
├── config/                # 配置文件目录
│   ├── default.yaml       # 默认配置文件
│   ├── templates.yaml     # 模板配置文件
│   └── ui.yaml            # UI 配置文件
├── docs/                  # 文档目录（三层架构）
│   ├── README.md          # 文档中心导航
│   ├── user-guide.md      # 综合用户指南
│   ├── template-guide.md  # 模板系统完整指南
│   ├── architecture.md    # 系统架构文档
│   ├── developer-guide.md # 开发者综合指南
│   ├── deployment-guide.md # 部署运维指南
│   ├── api-reference.md   # API 完整参考
│   ├── cli-reference.md   # CLI 命令参考
│   ├── config-reference.md # 配置参考
│   ├── troubleshooting.md # 故障排除指南
│   ├── CONTRIBUTING.md    # 文档贡献指南
│   └── archive/           # 历史文档归档
├── scripts/               # 脚本目录
│   ├── install.ps1        # Windows 安装脚本
│   └── install.sh         # Linux/macOS 安装脚本
├── logs/                  # 日志目录
├── README.md              # 项目主文档
├── 中文项目说明.md        # 中文详细说明
├── 快速开始.md            # 快速上手指南
├── requirements.txt       # Python 依赖
├── CHANGELOG.md           # 更新日志
└── LICENSE                # MIT 许可证
```

## 快速开始

### 安装

**方式一：使用安装脚本（推荐）**

```bash
# Windows PowerShell
.\scripts\install.ps1

# Linux/macOS
bash scripts/install.sh
```

**方式二：手动安装**

```bash
# 克隆项目
git clone https://github.com/0green7hand0/AI-PowerShell.git
cd AI-PowerShell

# 安装依赖
pip install -r requirements.txt
```

### 基本使用

**启动助手**
```bash
# 运行主程序
python src/main.py

# 或使用交互模式
python src/main.py --interactive
```

**使用示例**
```python
# 导入主控制器
from src.main import PowerShellAssistant

# 创建助手实例
assistant = PowerShellAssistant()

# 处理自然语言请求
result = assistant.process_request("显示CPU使用率最高的5个进程")

# 查看结果
print(result.output)
```

**自定义模板管理**
```bash
# 创建自定义模板
python src/main.py template create

# 列出所有模板
python src/main.py template list

# 编辑模板
python src/main.py template edit <template_id>

# 导出模板
python src/main.py template export <template_id> -o template.zip

# 导入模板
python src/main.py template import template.zip
```

详细使用说明请参考：
- [快速开始指南](快速开始.md) - 5分钟快速上手
- [用户指南](docs/user-guide.md) - 综合用户使用手册（UI系统、进度管理、安全机制）
- [模板系统指南](docs/template-guide.md) - 完整的模板系统使用指南（快速入门、深入指南、CLI参考）
- [故障排除指南](docs/troubleshooting.md) - 常见问题和解决方案

## 文档

我们的文档采用三层架构设计，帮助不同角色的用户快速找到所需信息：

### 📖 入门层 - 快速上手
- **[完整文档门户](DOCUMENTATION.md)** - 文档导航中心，按角色推荐阅读路径
- **[快速开始指南](快速开始.md)** - 5分钟快速上手
- **[中文项目说明](中文项目说明.md)** - 详细的中文项目介绍
- **[文档中心](docs/README.md)** - 所有文档的分类导航

### 📚 深入层 - 详细指南

#### 用户指南
- **[用户指南](docs/user-guide.md)** - 综合用户使用手册
  - UI系统使用、进度管理、启动体验、安全机制、常见任务
- **[模板系统指南](docs/template-guide.md)** - 完整的模板系统使用指南
  - 快速入门、深入指南、CLI参考、最佳实践、故障排除

#### 开发者文档
- **[系统架构](docs/architecture.md)** - 系统架构和设计原则
  - 整体架构、核心模块详解、数据流、设计模式、扩展点
- **[开发者指南](docs/developer-guide.md)** - 开发和扩展指南
  - 环境设置、项目结构、开发规范、模块开发、测试指南、贡献流程

#### 运维文档
- **[部署指南](docs/deployment-guide.md)** - 部署和运维完整指南
  - 安装部署、Docker部署、CI/CD配置、发布流程、AI模型配置

### 🔍 参考层 - 快速查找
- **[API参考](docs/api-reference.md)** - 完整的API文档（按模块组织）
- **[CLI命令参考](docs/cli-reference.md)** - 命令行工具完整参考（按字母顺序）
- **[配置参考](docs/config-reference.md)** - 配置文件详细说明
- **[故障排除指南](docs/troubleshooting.md)** - 常见问题和解决方案

### 📝 其他资源
- **[文档贡献指南](docs/CONTRIBUTING.md)** - 如何贡献和维护文档
- **[文档迁移映射表](docs/migration-map.md)** - 旧文档到新文档的映射关系

## 架构概览

### 模块化设计

项目采用高内聚低耦合的模块化架构，包含以下核心模块：

- **接口定义层** (`interfaces/`): 定义所有模块间的接口和数据模型
- **AI 引擎** (`ai_engine/`): 自然语言到 PowerShell 命令的转换
- **安全引擎** (`security/`): 三层安全验证和沙箱执行
- **执行引擎** (`execution/`): 跨平台 PowerShell 命令执行
- **配置管理** (`config/`): 灵活的配置系统和验证
- **日志引擎** (`log_engine/`): 结构化日志和审计跟踪
- **存储引擎** (`storage/`): 数据持久化和历史记录
- **上下文管理** (`context/`): 会话管理和上下文维护
- **UI 系统** (`ui/`): 现代化 CLI 界面、进度管理和交互式输入

详细架构说明请参考 [架构文档](docs/architecture.md)

## 系统要求

### 最低要求
- **操作系统**: Windows 10+, Ubuntu 18.04+, macOS 10.15+
- **Python**: 3.8 或更高版本
- **内存**: 4GB RAM（推荐 8GB）
- **存储**: 2GB 可用空间（AI 模型推荐 5GB）
- **PowerShell**: PowerShell Core 7.0+ 或 Windows PowerShell 5.1+

### 推荐配置
- **内存**: 8GB+ RAM 以获得最佳 AI 性能
- **存储**: 10GB+ 用于模型和日志
- **CPU**: 多核处理器以支持并发处理
- **Docker**: 用于沙箱执行（强烈推荐）

## 开发和贡献

### 开发环境设置

```bash
# 克隆仓库
git clone https://github.com/0green7hand0/AI-PowerShell.git
cd AI-PowerShell

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 运行测试
pytest tests/

# 代码格式化
black src/ tests/

# 类型检查
mypy src/
```

### 添加新功能

详细的开发指南请参考 [开发者指南](docs/developer-guide.md)，包括：

- 如何添加新的 AI 提供商
- 如何扩展安全规则
- 如何添加自定义命令模板
- 代码规范和最佳实践

## Security

### Three-Tier Security System

1. **Command Whitelist Validation**
   - Commands checked against configurable security rules
   - Pattern matching for dangerous operations
   - Risk assessment and categorization

2. **Dynamic Permission Checking**
   - Administrative command detection
   - User confirmation workflows
   - Permission escalation logging

3. **Sandbox Execution Environment**
   - Docker container isolation
   - Resource limits and network restrictions
   - Secure file system access

### 安全建议

- 首次使用前请仔细阅读生成的命令
- 对于系统级操作建议先在测试环境验证
- 定期更新项目以获得最新安全修复

## 贡献

欢迎贡献代码！请遵循以下流程：

1. Fork 本仓库
2. 创建功能分支: `git checkout -b feature/new-feature`
3. 提交更改并添加说明
4. 提交 Pull Request

### 代码规范

- 遵循 PEP 8 Python 代码规范
- 为函数添加类型提示
- 编写清晰的文档字符串

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 支持

- **文档门户**: [DOCUMENTATION.md](DOCUMENTATION.md) - 完整文档导航
- **文档中心**: [docs/README.md](docs/README.md) - 按类别浏览文档
- **故障排除**: [docs/troubleshooting.md](docs/troubleshooting.md) - 常见问题解决
- **问题反馈**: [GitHub Issues](https://github.com/0green7hand0/AI-PowerShell/issues)
- **讨论**: [GitHub Discussions](https://github.com/0green7hand0/AI-PowerShell/discussions)

## 致谢

- 基于本地 AI 模型构建 (LLaMA, Ollama 等)
- 跨平台 PowerShell 支持
- 注重隐私和安全的设计理念

---

**Note**: This is an open-source project focused on privacy and security. All AI processing happens locally on your machine - no data is sent to external services.
