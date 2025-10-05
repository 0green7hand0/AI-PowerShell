# AI PowerShell 智能助手

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![PowerShell](https://img.shields.io/badge/powershell-core%207.0+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-windows%20%7C%20linux%20%7C%20macos-lightgrey.svg)
![AI Model](https://img.shields.io/badge/ai-local%20processing-orange.svg)
![Language](https://img.shields.io/badge/language-中文%20%7C%20english-red.svg)
![Version](https://img.shields.io/badge/version-v1.1.0-brightgreen.svg)

一个智能的命令行交互系统，在自然语言和 PowerShell 命令之间架起桥梁。该系统利用本地 AI 模型提供直观的命令生成，通过三层保护系统实施全面的安全措施，并确保无缝的跨平台兼容性。

## 📚 快速导航

- [🚀 快速开始](#快速开始)
- [📖 中文文档](中文项目说明.md)
- [📋 快速开始指南](快速开始.md)
- [📁 项目结构](#项目结构)
- [🔧 安装说明](#安装)
- [📚 文档](#文档)

## 核心特性

- **自然语言处理**: 使用本地 AI 模型将中文/英文转换为 PowerShell 命令
- **安全验证**: 三层安全保护，包括命令白名单、权限检查和沙箱执行
- **跨平台支持**: 在 Windows、Linux 和 macOS 上与 PowerShell Core 协同工作
- **本地 AI 处理**: 注重隐私的本地模型执行 - 不向外部服务发送数据
- **全面日志记录**: 完整的审计跟踪和性能监控，支持关联追踪
- **MCP 协议**: 基于模型上下文协议构建，实现无缝集成

## 项目结构

```
AI-PowerShell/
├── 实用版本.py              # 核心：简化版本，适合个人用户
├── 最终修复版本.py          # 核心：企业版本，功能完整
├── README.md               # 项目主文档
├── 中文项目说明.md         # 中文详细说明
├── 快速开始.md             # 快速上手指南
├── requirements.txt        # Python 依赖
├── CHANGELOG.md           # 更新日志
├── LICENSE                # 许可证
├── docs/                  # 文档目录
│   ├── 安装指南.md
│   ├── 使用示例.md
│   └── 常见问题.md
└── scripts/              # 安装脚本目录
    ├── install.ps1       # Windows 安装脚本
    └── install.sh        # Linux/macOS 安装脚本
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

**简化版本（推荐新用户）**
```bash
python 实用版本.py
```

**企业版本（完整功能）**
```bash
python 最终修复版本.py
```

详细使用说明请参考 [快速开始指南](快速开始.md)

## 文档

- **[快速开始指南](快速开始.md)** - 快速上手使用
- **[中文项目说明](中文项目说明.md)** - 详细的中文文档
- **[安装指南](docs/安装指南.md)** - 详细安装说明
- **[使用示例](docs/使用示例.md)** - 实际使用案例
- **[常见问题](docs/常见问题.md)** - 常见问题解答

## 版本说明

### 实用版本.py
- **适用对象**: 个人用户、快速体验
- **特点**: 单文件运行，简单易用
- **功能**: 基础 AI PowerShell 交互功能

### 最终修复版本.py  
- **适用对象**: 企业用户、高级用户
- **特点**: 完整架构，功能全面
- **功能**: 包含所有高级特性和安全机制

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
```

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

- **文档**: [docs/](docs/)
- **问题反馈**: [GitHub Issues](https://github.com/0green7hand0/AI-PowerShell/issues)
- **讨论**: [GitHub Discussions](https://github.com/0green7hand0/AI-PowerShell/discussions)

## 致谢

- 基于本地 AI 模型构建 (LLaMA, Ollama 等)
- 跨平台 PowerShell 支持
- 注重隐私和安全的设计理念

---

**Note**: This is an open-source project focused on privacy and security. All AI processing happens locally on your machine - no data is sent to external services.
