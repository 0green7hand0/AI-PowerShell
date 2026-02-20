# AI PowerShell 智能助手 - 开发文档

> **文档类型**: 开发文档 | **最后更新**: 2025-01-11 | **版本**: v2.0.0

## 文档概述

本开发文档面向后续维护者和二次开发人员，提供完整的开发环境搭建、代码结构说明、开发规范、扩展开发指南、调试技巧和部署运维方案。通过本文档，开发者可以快速理解项目架构，掌握开发流程，并进行功能扩展和系统维护。

## 目录

1. [环境搭建](#1-环境搭建)
2. [代码结构](#2-代码结构)
3. [开发指南](#3-开发指南)
4. [扩展开发](#4-扩展开发)
5. [调试技巧](#5-调试技巧)
6. [部署运维](#6-部署运维)

---

## 1. 环境搭建

### 1.1 系统要求

#### 最低要求

- **操作系统**: Windows 10+, Ubuntu 18.04+, macOS 10.15+
- **Python**: 3.8 或更高版本
- **PowerShell**: PowerShell Core 7.0+ 或 Windows PowerShell 5.1+
- **内存**: 4GB RAM
- **存储**: 2GB 可用空间（AI 模型需要额外 5GB）
- **Git**: 用于版本控制

#### 推荐配置

- **内存**: 8GB+ RAM（用于 AI 模型推理）
- **存储**: 10GB+ 可用空间
- **CPU**: 多核处理器（支持并发处理）
- **Docker**: 用于沙箱执行（强烈推荐）
- **GPU**: 可选，用于加速 AI 模型推理

### 1.2 依赖安装步骤

#### 步骤 1: 安装 Python

**Windows**:
```powershell
# 从官网下载安装包
# https://www.python.org/downloads/

# 或使用 Chocolatey
choco install python --version=3.11.0

# 验证安装
python --version
```

**Linux (Ubuntu/Debian)**:
```bash
# 更新包列表
sudo apt update

# 安装 Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip

# 验证安装
python3 --version
```

**macOS**:
```bash
# 使用 Homebrew
brew install python@3.11

# 验证安装
python3 --version
```

#### 步骤 2: 安装 PowerShell Core

**Windows**:
```powershell
# 使用 winget
winget install Microsoft.PowerShell

# 或使用 Chocolatey
choco install powershell-core

# 验证安装
pwsh --version
```

**Linux (Ubuntu/Debian)**:
```bash
# 下载安装包
wget https://github.com/PowerShell/PowerShell/releases/download/v7.4.0/powershell_7.4.0-1.deb_amd64.deb

# 安装
sudo dpkg -i powershell_7.4.0-1.deb_amd64.deb

# 安装依赖
sudo apt-get install -f

# 验证安装
pwsh --version
```

**macOS**:
```bash
# 使用 Homebrew
brew install --cask powershell

# 验证安装
pwsh --version
```

#### 步骤 3: 克隆项目

```bash
# 克隆仓库
git clone https://github.com/0green7hand0/AI-PowerShell.git

# 进入项目目录
cd AI-PowerShell
```

#### 步骤 4: 创建虚拟环境

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Windows CMD
venv\Scripts\activate.bat

# Linux/macOS
source venv/bin/activate
```

#### 步骤 5: 安装 Python 依赖

```bash
# 安装基础依赖
pip install -r requirements.txt

# 安装开发依赖
pip install -r requirements-dev.txt

# 或安装所有依赖
pip install -e ".[dev,ai,docker]"
```

#### 步骤 6: 安装 Docker（可选）

**Windows**:
```powershell
# 下载并安装 Docker Desktop
# https://www.docker.com/products/docker-desktop

# 验证安装
docker --version
```

**Linux (Ubuntu/Debian)**:
```bash
# 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 添加用户到 docker 组
sudo usermod -aG docker $USER

# 验证安装
docker --version
```

**macOS**:
```bash
# 使用 Homebrew
brew install --cask docker

# 验证安装
docker --version
```

### 1.3 推荐开发工具

#### 代码编辑器

**Visual Studio Code** (推荐)
```bash
# 安装 VS Code
# https://code.visualstudio.com/

# 推荐扩展
- Python (Microsoft)
- PowerShell (Microsoft)
- Pylance (Microsoft)
- Python Test Explorer
- GitLens
- Docker
- YAML
```

**PyCharm**
```bash
# 专业的 Python IDE
# https://www.jetbrains.com/pycharm/
```

#### 命令行工具

**Windows Terminal** (Windows)
```powershell
# 使用 winget 安装
winget install Microsoft.WindowsTerminal
```

**iTerm2** (macOS)
```bash
# 使用 Homebrew 安装
brew install --cask iterm2
```

#### 版本控制

**Git**
```bash
# 配置 Git
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# 配置默认编辑器
git config --global core.editor "code --wait"
```

#### 数据库工具（可选）

**DBeaver** - 通用数据库管理工具
```bash
# 下载安装
# https://dbeaver.io/
```

### 1.4 环境配置方法

#### 配置文件设置

```bash
# 复制默认配置
cp config/default.yaml config.yaml

# 编辑配置文件
# Windows
notepad config.yaml

# Linux/macOS
nano config.yaml
# 或
vim config.yaml
```

#### 基本配置示例

```yaml
# config.yaml

# AI 引擎配置
ai:
  provider: "ollama"  # local, ollama, openai, azure
  model_name: "llama2"
  temperature: 0.7
  max_tokens: 256
  timeout: 30

# 安全引擎配置
security:
  whitelist_mode: "strict"  # strict, moderate, permissive
  require_confirmation: true
  sandbox_enabled: false
  docker_image: "mcr.microsoft.com/powershell:latest"

# 执行引擎配置
execution:
  timeout: 30
  max_output_length: 10000
  encoding: "utf-8"

# 日志配置
logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
  format: "json"  # json, text
  output: "file"  # console, file, both
  file_path: "logs/app.log"
  max_file_size: 10485760  # 10MB
  backup_count: 5

# 存储配置
storage:
  type: "file"  # file, database
  base_path: "~/.ai-powershell"
  cache_ttl: 3600
  max_history: 1000

# 上下文配置
context:
  max_context_depth: 10
  session_timeout: 3600
  auto_save: true
```

#### 环境变量设置

**Windows PowerShell**:
```powershell
# 设置环境变量
$env:AI_POWERSHELL_CONFIG = "C:\path\to\config.yaml"
$env:AI_POWERSHELL_LOG_LEVEL = "DEBUG"

# 永久设置（需要管理员权限）
[System.Environment]::SetEnvironmentVariable("AI_POWERSHELL_CONFIG", "C:\path\to\config.yaml", "User")
```

**Linux/macOS**:
```bash
# 临时设置
export AI_POWERSHELL_CONFIG="/path/to/config.yaml"
export AI_POWERSHELL_LOG_LEVEL="DEBUG"

# 永久设置（添加到 ~/.bashrc 或 ~/.zshrc）
echo 'export AI_POWERSHELL_CONFIG="/path/to/config.yaml"' >> ~/.bashrc
echo 'export AI_POWERSHELL_LOG_LEVEL="DEBUG"' >> ~/.bashrc
source ~/.bashrc
```

#### AI 模型配置

**使用 Ollama（推荐）**:
```bash
# 安装 Ollama
# https://ollama.ai/

# 下载模型
ollama pull llama2

# 验证模型
ollama list

# 测试模型
ollama run llama2 "Hello, world!"
```

**使用本地模型**:
```yaml
# config.yaml
ai:
  provider: "local"
  model_path: "/path/to/model.gguf"
  n_ctx: 2048
  n_threads: 4
```

#### 验证环境

```bash
# 运行验证脚本
python scripts/verify_installation.py

# 运行测试
pytest tests/ -v

# 检查配置
python -c "from src.config import ConfigManager; print(ConfigManager().get_config())"
```

#### 常见环境问题

**问题 1: Python 版本不兼容**
```bash
# 检查 Python 版本
python --version

# 如果版本低于 3.8，需要升级
# Windows: 从官网下载新版本
# Linux: sudo apt install python3.11
# macOS: brew install python@3.11
```

**问题 2: 依赖安装失败**
```bash
# 升级 pip
python -m pip install --upgrade pip

# 清除缓存
pip cache purge

# 重新安装
pip install -r requirements.txt --no-cache-dir
```

**问题 3: PowerShell 未找到**
```bash
# 检查 PowerShell 是否在 PATH 中
# Windows
where pwsh

# Linux/macOS
which pwsh

# 如果未找到，需要添加到 PATH
```

**问题 4: Docker 权限问题（Linux）**
```bash
# 添加用户到 docker 组
sudo usermod -aG docker $USER

# 重新登录或运行
newgrp docker

# 验证
docker ps
```

### 1.5 开发环境快速启动

#### 使用安装脚本（推荐）

**Windows**:
```powershell
# 运行安装脚本
.\scripts\install.ps1

# 脚本会自动：
# 1. 检查 Python 和 PowerShell
# 2. 创建虚拟环境
# 3. 安装依赖
# 4. 配置环境
# 5. 运行验证测试
```

**Linux/macOS**:
```bash
# 运行安装脚本
bash scripts/install.sh

# 脚本会自动：
# 1. 检查 Python 和 PowerShell
# 2. 创建虚拟环境
# 3. 安装依赖
# 4. 配置环境
# 5. 运行验证测试
```

#### 手动快速启动

```bash
# 1. 克隆项目
git clone https://github.com/0green7hand0/AI-PowerShell.git
cd AI-PowerShell

# 2. 创建并激活虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 .\venv\Scripts\Activate.ps1  # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 运行测试
pytest tests/

# 5. 启动应用
python src/main.py --interactive
```

#### 开发环境检查清单

- [ ] Python 3.8+ 已安装
- [ ] PowerShell Core 7.0+ 已安装
- [ ] Git 已安装并配置
- [ ] 虚拟环境已创建并激活
- [ ] 所有依赖已安装
- [ ] 配置文件已创建
- [ ] Docker 已安装（可选）
- [ ] AI 模型已下载（可选）
- [ ] 测试全部通过
- [ ] 开发工具已安装

---

## 2. 代码结构

### 2.1 目录结构

```
AI-PowerShell/
├── src/                          # 源代码目录
│   ├── interfaces/               # 接口定义层
│   │   ├── __init__.py
│   │   └── base.py              # 基础接口和数据模型
│   │
│   ├── ai_engine/               # AI 引擎模块
│   │   ├── __init__.py
│   │   ├── engine.py            # AI 引擎主类
│   │   ├── providers.py         # AI 提供商实现
│   │   ├── translation.py       # 自然语言翻译器
│   │   ├── error_detection.py   # 错误检测器
│   │   └── cache.py             # 翻译缓存
│   │
│   ├── security/                # 安全引擎模块
│   │   ├── __init__.py
│   │   ├── engine.py            # 安全引擎主类
│   │   ├── whitelist.py         # 命令白名单验证
│   │   ├── permission.py        # 权限检查器
│   │   └── sandbox.py           # 沙箱执行器
│   │
│   ├── execution/               # 执行引擎模块
│   │   ├── __init__.py
│   │   ├── executor.py          # 命令执行器
│   │   ├── platform_adapter.py  # 平台适配器
│   │   └── output_formatter.py  # 输出格式化器
│   │
│   ├── config/                  # 配置管理模块
│   │   ├── __init__.py
│   │   ├── manager.py           # 配置管理器
│   │   ├── models.py            # 配置数据模型
│   │   └── validator.py         # 配置验证器
│   │
│   ├── log_engine/              # 日志引擎模块
│   │   ├── __init__.py
│   │   ├── engine.py            # 日志引擎主类
│   │   ├── formatters.py        # 日志格式化器
│   │   └── filters.py           # 敏感信息过滤器
│   │
│   ├── storage/                 # 存储引擎模块
│   │   ├── __init__.py
│   │   ├── interfaces.py        # 存储接口定义
│   │   ├── file_storage.py      # 文件存储实现
│   │   ├── factory.py           # 存储工厂
│   │   └── cache.py             # 缓存管理
│   │
│   ├── context/                 # 上下文管理模块
│   │   ├── __init__.py
│   │   ├── manager.py           # 上下文管理器
│   │   ├── history.py           # 历史记录管理
│   │   ├── session.py           # 会话管理
│   │   └── models.py            # 上下文数据模型
│   │
│   ├── ui/                      # UI 系统模块
│   │   ├── __init__.py
│   │   ├── cli.py               # 命令行界面
│   │   ├── progress.py          # 进度管理器
│   │   ├── interactive.py       # 交互式输入
│   │   └── themes.py            # 主题配置
│   │
│   ├── template_engine/         # 模板引擎模块
│   │   ├── __init__.py
│   │   ├── engine.py            # 模板引擎主类
│   │   ├── manager.py           # 模板管理器
│   │   └── validator.py         # 模板验证器
│   │
│   ├── cleanup/                 # 清理模块
│   │   ├── __init__.py
│   │   └── manager.py           # 清理管理器
│   │
│   ├── main.py                  # 主入口文件
│   └── __init__.py
│
├── tests/                       # 测试目录
│   ├── ai_engine/               # AI 引擎测试
│   ├── security/                # 安全引擎测试
│   ├── execution/               # 执行引擎测试
│   ├── config/                  # 配置管理测试
│   ├── log_engine/              # 日志引擎测试
│   ├── storage/                 # 存储引擎测试
│   ├── context/                 # 上下文管理测试
│   ├── ui/                      # UI 系统测试
│   ├── template_engine/         # 模板引擎测试
│   ├── integration/             # 集成测试
│   ├── e2e/                     # 端到端测试
│   └── usability/               # 可用性测试
│
├── config/                      # 配置文件目录
│   ├── default.yaml             # 默认配置
│   ├── templates.yaml           # 模板配置
│   ├── ui.yaml                  # UI 配置
│   └── .backups/                # 配置备份
│
├── templates/                   # 模板目录
│   ├── automation/              # 自动化模板
│   ├── file_management/         # 文件管理模板
│   ├── system_monitoring/       # 系统监控模板
│   ├── custom/                  # 自定义模板
│   └── .history/                # 模板历史
│
├── docs/                        # 文档目录
│   ├── README.md                # 文档中心
│   ├── user-guide.md            # 用户指南
│   ├── template-guide.md        # 模板指南
│   ├── architecture.md          # 架构文档
│   ├── developer-guide.md       # 开发者指南
│   ├── deployment-guide.md      # 部署指南
│   ├── api-reference.md         # API 参考
│   ├── cli-reference.md         # CLI 参考
│   ├── config-reference.md      # 配置参考
│   ├── troubleshooting.md       # 故障排除
│   └── archive/                 # 文档归档
│
├── scripts/                     # 脚本目录
│   ├── install.ps1              # Windows 安装脚本
│   ├── install.sh               # Linux/macOS 安装脚本
│   ├── release.ps1              # Windows 发布脚本
│   ├── release.sh               # Linux/macOS 发布脚本
│   ├── verify_installation.py   # 安装验证脚本
│   ├── verify_content_completeness.py  # 内容完整性验证
│   └── verify_links.py          # 链接验证脚本
│
├── examples/                    # 示例目录
│   ├── analyze_project.py       # 项目分析示例
│   ├── progress_demo.py         # 进度管理示例
│   ├── startup_demo.py          # 启动体验示例
│   └── ui_demo.py               # UI 系统示例
│
├── web-ui/                      # Web UI 目录（可选）
│   ├── backend/                 # 后端代码
│   ├── src/                     # 前端代码
│   ├── tests/                   # 测试代码
│   └── docs/                    # 文档
│
├── logs/                        # 日志目录
│   ├── app.log                  # 应用日志
│   ├── error.log                # 错误日志
│   └── audit.log                # 审计日志
│
├── .github/                     # GitHub 配置
│   └── workflows/               # CI/CD 工作流
│
├── .vscode/                     # VS Code 配置
│   ├── settings.json            # 编辑器设置
│   ├── launch.json              # 调试配置
│   └── extensions.json          # 推荐扩展
│
├── README.md                    # 项目主文档
├── 中文项目说明.md              # 中文详细说明
├── 快速开始.md                  # 快速上手指南
├── DOCUMENTATION.md             # 文档门户
├── CHANGELOG.md                 # 更新日志
├── RELEASE_NOTES.md             # 发布说明
├── LICENSE                      # MIT 许可证
├── .gitignore                   # Git 忽略文件
├── .dockerignore                # Docker 忽略文件
├── .flake8                      # Flake8 配置
├── .coveragerc                  # 覆盖率配置
├── .pre-commit-config.yaml      # Pre-commit 配置
├── pyproject.toml               # 项目配置
├── requirements.txt             # Python 依赖
├── requirements-dev.txt         # 开发依赖
├── Makefile                     # Make 命令
├── Dockerfile                   # Docker 镜像
├── docker-compose.yml           # Docker Compose 配置
└── run.py                       # 快速启动脚本
```

### 2.2 各模块职责

#### 2.2.1 接口定义层 (interfaces/)

**职责**: 定义所有模块间的接口和数据模型，确保模块间的松耦合。

**核心文件**:
- `base.py`: 定义基础接口和数据模型
  - `AIEngineInterface`: AI 引擎接口
  - `SecurityEngineInterface`: 安全引擎接口
  - `ExecutorInterface`: 执行器接口
  - `StorageInterface`: 存储接口
  - `Suggestion`: 命令建议数据模型
  - `ValidationResult`: 验证结果数据模型
  - `ExecutionResult`: 执行结果数据模型
  - `Context`: 上下文数据模型
  - `CommandEntry`: 命令历史条目数据模型

**设计原则**:
- 使用抽象基类 (ABC) 定义接口
- 使用 dataclass 定义数据模型
- 接口与实现分离
- 依赖倒置原则

#### 2.2.2 AI 引擎模块 (ai_engine/)

**职责**: 将自然语言转换为 PowerShell 命令，支持多种 AI 提供商。

**核心组件**:
- `engine.py`: AI 引擎主类，协调翻译流程
- `providers.py`: AI 提供商实现（Ollama, OpenAI, Azure, Local）
- `translation.py`: 自然语言翻译器，包含规则匹配
- `error_detection.py`: 命令错误检测和修正
- `cache.py`: 翻译结果缓存（LRU 算法）

**翻译策略**:
1. 检查缓存
2. 尝试规则匹配（快速路径）
3. 使用 AI 模型生成
4. 错误检测和修正
5. 缓存结果

**支持的 AI 提供商**:
- **Ollama**: 本地 AI 模型服务
- **OpenAI**: GPT-3.5/GPT-4
- **Azure OpenAI**: Azure 托管的 OpenAI 服务
- **Local**: 本地 LLaMA 模型

#### 2.2.3 安全引擎模块 (security/)

**职责**: 提供三层安全验证机制，确保命令执行的安全性。

**核心组件**:
- `engine.py`: 安全引擎主类，协调三层验证
- `whitelist.py`: 命令白名单验证器（30+ 危险模式）
- `permission.py`: 权限检查器（管理员权限检测）
- `sandbox.py`: 沙箱执行器（Docker 容器隔离）

**三层安全机制**:
1. **第一层**: 命令白名单验证
   - 危险命令模式匹配
   - 风险等级评估（SAFE, LOW, MEDIUM, HIGH, CRITICAL）
   
2. **第二层**: 权限检查
   - 管理员权限检测
   - 用户确认流程
   
3. **第三层**: 沙箱执行（可选）
   - Docker 容器隔离
   - 资源限制（CPU、内存、网络）

#### 2.2.4 执行引擎模块 (execution/)

**职责**: 跨平台 PowerShell 命令执行，处理平台差异。

**核心组件**:
- `executor.py`: 命令执行器主类
- `platform_adapter.py`: 平台适配器（Windows, Linux, macOS）
- `output_formatter.py`: 输出格式化器（文本、JSON、表格）

**平台支持**:
- **Windows**: PowerShell 5.1 / PowerShell Core 7.0+
- **Linux**: PowerShell Core 7.0+
- **macOS**: PowerShell Core 7.0+

**功能特性**:
- 进程管理和超时控制
- 实时输出捕获
- 编码问题处理（UTF-8）
- 返回码处理
- 错误信息格式化

#### 2.2.5 配置管理模块 (config/)

**职责**: 提供灵活的配置系统，支持多层级配置和验证。

**核心组件**:
- `manager.py`: 配置管理器，负责加载和保存配置
- `models.py`: 配置数据模型（使用 Pydantic）
- `validator.py`: 配置验证器

**配置层级**:
1. 默认配置 (`config/default.yaml`)
2. 项目配置 (`config.yaml`)
3. 用户配置 (`~/.ai-powershell/config.yaml`)
4. 环境变量

**配置模型**:
- `AppConfig`: 应用总配置
- `AIConfig`: AI 引擎配置
- `SecurityConfig`: 安全引擎配置
- `ExecutionConfig`: 执行引擎配置
- `LoggingConfig`: 日志配置
- `StorageConfig`: 存储配置
- `ContextConfig`: 上下文配置

#### 2.2.6 日志引擎模块 (log_engine/)

**职责**: 提供结构化日志记录、审计追踪和性能监控。

**核心组件**:
- `engine.py`: 日志引擎主类
- `formatters.py`: 日志格式化器（JSON, Text）
- `filters.py`: 敏感信息过滤器

**日志功能**:
- 结构化日志（JSON 格式）
- 关联 ID 追踪
- 敏感信息过滤（密码、密钥等）
- 日志轮转和归档
- 性能监控

**日志级别**:
- DEBUG: 详细的调试信息
- INFO: 一般信息
- WARNING: 警告信息
- ERROR: 错误信息
- CRITICAL: 严重错误

#### 2.2.7 存储引擎模块 (storage/)

**职责**: 提供数据持久化功能，支持多种存储后端。

**核心组件**:
- `interfaces.py`: 存储接口定义
- `file_storage.py`: 文件存储实现
- `factory.py`: 存储工厂
- `cache.py`: 缓存管理（TTL 支持）

**存储功能**:
- 命令历史记录
- 会话数据
- 上下文快照
- 用户偏好设置
- 翻译缓存

**存储结构**:
```
~/.ai-powershell/
├── history.json         # 命令历史
├── config.yaml          # 用户配置
├── sessions/            # 会话数据
├── snapshots/           # 上下文快照
├── preferences/         # 用户偏好
└── cache/              # 缓存目录
```

#### 2.2.8 上下文管理模块 (context/)

**职责**: 管理用户会话、命令历史和上下文信息。

**核心组件**:
- `manager.py`: 上下文管理器
- `history.py`: 历史记录管理器
- `session.py`: 会话管理器
- `models.py`: 上下文数据模型

**上下文功能**:
- 会话管理（创建、终止、恢复）
- 命令历史记录
- 上下文快照和恢复
- 用户偏好管理
- 历史搜索和过滤

**数据模型**:
- `Session`: 会话信息
- `CommandEntry`: 命令历史条目
- `ContextSnapshot`: 上下文快照
- `UserPreferences`: 用户偏好

#### 2.2.9 UI 系统模块 (ui/)

**职责**: 提供现代化的命令行界面和交互体验。

**核心组件**:
- `cli.py`: 命令行界面
- `progress.py`: 进度管理器
- `interactive.py`: 交互式输入
- `themes.py`: 主题配置

**UI 功能**:
- 彩色输出和语法高亮
- 进度条和加载动画
- 交互式输入和自动补全
- 表格和列表展示
- 错误提示和警告

#### 2.2.10 模板引擎模块 (template_engine/)

**职责**: 管理和执行 PowerShell 脚本模板。

**核心组件**:
- `engine.py`: 模板引擎主类
- `manager.py`: 模板管理器
- `validator.py`: 模板验证器

**模板功能**:
- 模板创建和编辑
- 模板执行和参数化
- 模板导入和导出
- 模板版本管理
- 模板分类和搜索

#### 2.2.11 主控制器 (main.py)

**职责**: 协调所有模块工作，提供统一的入口点。

**核心类**:
- `PowerShellAssistant`: 主控制器类

**请求处理流程**:
1. 生成关联 ID 并记录请求
2. 获取当前上下文
3. AI 翻译自然语言
4. 安全验证
5. 用户确认（如需要）
6. 执行命令
7. 保存历史记录
8. 更新上下文

**依赖注入**:
```python
self.ai_engine = AIEngine(config)
self.security_engine = SecurityEngine(config)
self.executor = CommandExecutor(config)
self.context_manager = ContextManager(storage=storage)
```

### 2.3 依赖关系图

```mermaid
graph TD
    A[main.py<br/>主控制器] --> B[ai_engine<br/>AI 引擎]
    A --> C[security<br/>安全引擎]
    A --> D[execution<br/>执行引擎]
    A --> E[context<br/>上下文管理]
    
    B --> F[interfaces<br/>接口定义]
    C --> F
    D --> F
    E --> F
    
    B --> G[config<br/>配置管理]
    C --> G
    D --> G
    E --> G
    
    A --> H[log_engine<br/>日志引擎]
    B --> H
    C --> H
    D --> H
    E --> H
    
    E --> I[storage<br/>存储引擎]
    
    A --> J[ui<br/>UI 系统]
    
    A --> K[template_engine<br/>模板引擎]
    
    style A fill:#f9f,stroke:#333,stroke-width:4px
    style F fill:#bbf,stroke:#333,stroke-width:2px
    style G fill:#bfb,stroke:#333,stroke-width:2px
    style H fill:#fbb,stroke:#333,stroke-width:2px
    style I fill:#ffb,stroke:#333,stroke-width:2px
```

**依赖层次**:
1. **接口层**: `interfaces/` - 最底层，被所有模块依赖
2. **基础设施层**: `config/`, `log_engine/`, `storage/` - 提供基础服务
3. **核心业务层**: `ai_engine/`, `security/`, `execution/`, `context/` - 实现核心功能
4. **应用层**: `main.py`, `ui/`, `template_engine/` - 协调和展示

### 2.4 命名规范

#### 2.4.1 文件和目录命名

- **模块目录**: 小写字母 + 下划线，如 `ai_engine/`, `log_engine/`
- **Python 文件**: 小写字母 + 下划线，如 `engine.py`, `file_storage.py`
- **配置文件**: 小写字母 + 连字符，如 `default.yaml`, `config-reference.md`
- **文档文件**: 小写字母 + 连字符，如 `user-guide.md`, `api-reference.md`

#### 2.4.2 Python 代码命名

**类名**: PascalCase（大驼峰）
```python
class PowerShellAssistant:
    pass

class AIEngine:
    pass

class CommandWhitelist:
    pass
```

**函数和方法名**: snake_case（小写 + 下划线）
```python
def process_request(user_input: str) -> Result:
    pass

def validate_command(command: str) -> ValidationResult:
    pass

def get_context(depth: int = 5) -> Context:
    pass
```

**常量**: UPPER_CASE（大写 + 下划线）
```python
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30
LOG_FORMAT = "json"
```

**私有方法**: 前缀下划线
```python
def _internal_method(self):
    pass

def _build_prompt(self, text: str) -> str:
    pass
```

**受保护方法**: 单下划线前缀
```python
def _protected_method(self):
    pass
```

**特殊方法**: 双下划线前后
```python
def __init__(self):
    pass

def __str__(self):
    pass
```

#### 2.4.3 变量命名

**局部变量**: snake_case
```python
user_input = "显示当前时间"
command_result = executor.execute(command)
confidence_score = 0.95
```

**实例变量**: snake_case
```python
self.ai_engine = AIEngine()
self.config = config
self.logger = logger
```

**类变量**: snake_case 或 UPPER_CASE（常量）
```python
class MyClass:
    default_timeout = 30  # 类变量
    MAX_RETRIES = 3       # 类常量
```

#### 2.4.4 模块和包命名

**包名**: 小写字母，简短，避免下划线
```python
import ai_engine
import security
import execution
```

**模块名**: 小写字母 + 下划线
```python
from ai_engine import engine
from security import whitelist
from storage import file_storage
```

#### 2.4.5 测试文件命名

**测试文件**: `test_` 前缀 + 被测试模块名
```python
test_engine.py          # 测试 engine.py
test_translation.py     # 测试 translation.py
test_whitelist.py       # 测试 whitelist.py
```

**测试类**: `Test` 前缀 + 被测试类名
```python
class TestAIEngine:
    pass

class TestCommandWhitelist:
    pass
```

**测试方法**: `test_` 前缀 + 测试场景
```python
def test_translate_simple_command():
    pass

def test_validate_dangerous_command():
    pass

def test_execute_with_timeout():
    pass
```

### 2.5 代码组织原则

#### 2.5.1 单一职责原则 (SRP)

每个类和函数应该只有一个职责：

```python
# ❌ 不好 - 职责过多
class DataProcessor:
    def load_and_process_and_save(self, file_path):
        data = self.load(file_path)
        result = self.process(data)
        self.save(result)

# ✅ 好 - 职责分离
class DataLoader:
    def load(self, file_path):
        pass

class DataProcessor:
    def process(self, data):
        pass

class DataSaver:
    def save(self, data):
        pass
```

#### 2.5.2 开闭原则 (OCP)

对扩展开放，对修改关闭：

```python
# ✅ 好 - 使用抽象基类
from abc import ABC, abstractmethod

class AIProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str:
        pass

class OllamaProvider(AIProvider):
    def generate(self, prompt: str) -> str:
        # Ollama 实现
        pass

class OpenAIProvider(AIProvider):
    def generate(self, prompt: str) -> str:
        # OpenAI 实现
        pass
```

#### 2.5.3 依赖倒置原则 (DIP)

依赖抽象而不是具体实现：

```python
# ❌ 不好 - 依赖具体实现
class MyClass:
    def __init__(self):
        self.storage = FileStorage()  # 硬编码

# ✅ 好 - 依赖抽象接口
class MyClass:
    def __init__(self, storage: StorageInterface):
        self.storage = storage  # 依赖注入
```

#### 2.5.4 接口隔离原则 (ISP)

客户端不应该依赖它不需要的接口：

```python
# ✅ 好 - 接口分离
class ReadableInterface(ABC):
    @abstractmethod
    def read(self) -> str:
        pass

class WritableInterface(ABC):
    @abstractmethod
    def write(self, data: str) -> bool:
        pass

class ReadOnlyStorage(ReadableInterface):
    def read(self) -> str:
        pass

class ReadWriteStorage(ReadableInterface, WritableInterface):
    def read(self) -> str:
        pass
    
    def write(self, data: str) -> bool:
        pass
```

---

## 3. 开发指南

### 3.1 编码规范

#### 3.1.1 Python 代码风格

项目遵循 **PEP 8** Python 代码风格指南。

**导入顺序**:
```python
# 1. 标准库导入
import os
import sys
from typing import Dict, List, Optional

# 2. 第三方库导入
import yaml
from pydantic import BaseModel

# 3. 项目内部导入
from src.interfaces.base import AIEngineInterface
from src.config import ConfigManager
```

**行长度**: 最大 127 字符（配置在 `pyproject.toml`）

**缩进**: 4 个空格

**引号**: 优先使用双引号 `"`

**类型提示**: 所有公共函数和方法都应该有类型提示

```python
from typing import Dict, List, Optional, Union

def process_data(
    data: List[str],
    config: Dict[str, any],
    timeout: Optional[int] = None
) -> Union[str, None]:
    """处理数据
    
    Args:
        data: 输入数据列表
        config: 配置字典
        timeout: 超时时间（秒），可选
        
    Returns:
        处理结果字符串，失败返回 None
    """
    pass
```

#### 3.1.2 文档字符串规范

使用 **Google 风格** 的文档字符串：

```python
def complex_function(param1: str, param2: int) -> Dict[str, any]:
    """执行复杂操作
    
    这是一个更详细的说明，解释函数的具体行为。
    可以包含多行描述。
    
    Args:
        param1: 第一个参数的说明
        param2: 第二个参数的说明
        
    Returns:
        包含结果的字典，格式为：
        {
            'status': 'success' 或 'error',
            'data': 处理后的数据,
            'message': 状态消息
        }
        
    Raises:
        ValueError: 当 param2 为负数时
        RuntimeError: 当处理失败时
        
    Example:
        >>> result = complex_function("test", 10)
        >>> print(result['status'])
        'success'
        
    Note:
        这个函数可能需要较长时间执行
    """
    pass
```

**类文档字符串**:
```python
class MyClass:
    """类的简短描述
    
    详细说明类的用途、功能和使用场景。
    
    Attributes:
        attr1: 属性1的说明
        attr2: 属性2的说明
        
    Example:
        >>> obj = MyClass(param="value")
        >>> result = obj.method()
    """
    
    def __init__(self, param: str):
        """初始化方法
        
        Args:
            param: 参数说明
        """
        self.attr1 = param
```

#### 3.1.3 错误处理规范

**使用具体的异常类型**:
```python
# ❌ 不好 - 捕获所有异常
try:
    result = process()
except:
    pass

# ✅ 好 - 捕获具体异常
try:
    result = process()
except ValueError as e:
    logger.error(f"Invalid value: {e}")
    raise
except FileNotFoundError as e:
    logger.error(f"File not found: {e}")
    return None
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    raise
```

**提供有用的错误信息**:
```python
# ❌ 不好 - 错误信息不明确
raise ValueError("Invalid input")

# ✅ 好 - 提供详细的错误信息
raise ValueError(
    f"Invalid temperature value: {temp}. "
    f"Must be between 0.0 and 2.0, got {temp}"
)
```

**错误恢复和重试**:
```python
def process_with_retry(data, max_retries=3):
    """带重试的处理函数
    
    Args:
        data: 要处理的数据
        max_retries: 最大重试次数
        
    Returns:
        处理结果
        
    Raises:
        RuntimeError: 重试次数用尽后仍然失败
    """
    for attempt in range(max_retries):
        try:
            return process(data)
        except TemporaryError as e:
            if attempt == max_retries - 1:
                raise RuntimeError(
                    f"Failed after {max_retries} attempts: {e}"
                )
            logger.warning(
                f"Attempt {attempt + 1} failed, retrying...",
                extra={'error': str(e)}
            )
            time.sleep(2 ** attempt)  # 指数退避
```

#### 3.1.4 日志记录规范

**使用适当的日志级别**:
```python
from src.log_engine.engine import LogEngine

logger = LogEngine.get_logger(__name__)

# DEBUG: 详细的调试信息
logger.debug(
    "Processing input",
    extra={'input': user_input, 'length': len(user_input)}
)

# INFO: 一般信息
logger.info(
    "Command executed successfully",
    extra={'command': command, 'duration': duration}
)

# WARNING: 警告信息
logger.warning(
    "High confidence score",
    extra={'score': score, 'threshold': threshold}
)

# ERROR: 错误信息
logger.error(
    "Failed to execute command",
    extra={'command': command, 'error': str(error)},
    exc_info=True
)

# CRITICAL: 严重错误
logger.critical(
    "System failure",
    extra={'error': str(error)},
    exc_info=True
)
```

**结构化日志**:
```python
# ✅ 好 - 使用结构化日志
logger.info(
    "User request processed",
    extra={
        'correlation_id': correlation_id,
        'user_input': user_input,
        'command': command,
        'duration_ms': duration * 1000,
        'success': True
    }
)

# ❌ 不好 - 字符串拼接
logger.info(f"User request {correlation_id} processed: {user_input} -> {command}")
```

#### 3.1.5 代码注释规范

**何时写注释**:
- 复杂的算法或逻辑
- 非显而易见的代码
- 临时解决方案或 TODO
- 重要的业务规则

**注释风格**:
```python
# 单行注释：解释为什么这样做，而不是做什么

# TODO: 需要优化性能
# FIXME: 这里有一个已知的 bug
# NOTE: 这是一个重要的注意事项
# HACK: 临时解决方案，需要重构

def complex_algorithm(data):
    """复杂算法实现"""
    
    # 第一步：数据预处理
    # 移除空值和重复项，确保数据质量
    cleaned_data = [x for x in data if x is not None]
    
    # 第二步：应用核心算法
    # 使用快速排序算法，时间复杂度 O(n log n)
    sorted_data = sorted(cleaned_data)
    
    # 第三步：后处理
    # 应用业务规则：只保留前 10 个结果
    return sorted_data[:10]
```

### 3.2 提交规范

#### 3.2.1 Git 提交信息格式

使用 **约定式提交** (Conventional Commits) 格式：

```
<type>(<scope>): <subject>

<body>

<footer>
```

**类型 (type)**:
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式（不影响代码运行）
- `refactor`: 重构（既不是新功能也不是 bug 修复）
- `perf`: 性能优化
- `test`: 添加或修改测试
- `chore`: 构建过程或辅助工具的变动
- `ci`: CI 配置文件和脚本的变动
- `build`: 影响构建系统或外部依赖的更改

**范围 (scope)**: 可选，指定影响的模块
- `ai_engine`
- `security`
- `execution`
- `config`
- `storage`
- `context`
- `ui`
- `docs`

**示例**:
```bash
# 新功能
git commit -m "feat(ai_engine): add support for GPT-4 model"

# Bug 修复
git commit -m "fix(security): fix command validation regex"

# 文档更新
git commit -m "docs: update installation guide"

# 重构
git commit -m "refactor(storage): simplify file storage implementation"

# 性能优化
git commit -m "perf(ai_engine): optimize translation cache"

# 测试
git commit -m "test(security): add tests for whitelist validation"
```

**详细提交信息**:
```bash
git commit -m "feat(ai_engine): add support for Azure OpenAI

- Add AzureOpenAIProvider class
- Update configuration model to support Azure endpoints
- Add tests for Azure provider
- Update documentation

Closes #123"
```

#### 3.2.2 分支命名规范

**分支类型**:
- `feature/` - 新功能开发
- `fix/` - Bug 修复
- `hotfix/` - 紧急修复
- `refactor/` - 代码重构
- `docs/` - 文档更新
- `test/` - 测试相关
- `chore/` - 杂项任务

**命名格式**: `<type>/<issue-number>-<short-description>`

**示例**:
```bash
# 新功能
git checkout -b feature/123-add-azure-support

# Bug 修复
git checkout -b fix/456-validation-error

# 文档更新
git checkout -b docs/update-api-reference

# 重构
git checkout -b refactor/simplify-storage
```

#### 3.2.3 Pull Request 规范

**PR 标题**: 使用与提交信息相同的格式

**PR 描述模板**:
```markdown
## 变更类型
- [ ] 新功能 (feat)
- [ ] Bug 修复 (fix)
- [ ] 文档更新 (docs)
- [ ] 代码重构 (refactor)
- [ ] 性能优化 (perf)
- [ ] 测试 (test)
- [ ] 其他 (chore)

## 变更说明
简要描述你的变更内容和原因。

## 测试
- [ ] 添加了单元测试
- [ ] 添加了集成测试
- [ ] 所有测试通过
- [ ] 代码覆盖率 ≥ 85%

## 检查清单
- [ ] 代码遵循项目编码规范
- [ ] 已添加必要的文档
- [ ] 已更新 CHANGELOG.md
- [ ] 通过了所有 CI 检查

## 相关 Issue
Closes #123
Relates to #456

## 截图（如适用）
[添加截图或 GIF]

## 其他说明
[其他需要说明的内容]
```

### 3.3 测试规范

#### 3.3.1 测试结构

**测试文件组织**:
```
tests/
├── ai_engine/
│   ├── test_engine.py
│   ├── test_translation.py
│   └── test_providers.py
├── security/
│   ├── test_engine.py
│   ├── test_whitelist.py
│   └── test_sandbox.py
├── integration/
│   ├── test_main_integration.py
│   └── test_end_to_end.py
└── conftest.py  # pytest 配置和 fixtures
```

**测试命名**:
```python
# 测试类：Test + 被测试类名
class TestAIEngine:
    pass

class TestCommandWhitelist:
    pass

# 测试方法：test_ + 测试场景
def test_translate_simple_command():
    pass

def test_validate_dangerous_command():
    pass

def test_execute_with_timeout():
    pass
```

#### 3.3.2 测试编写规范

**AAA 模式** (Arrange-Act-Assert):
```python
def test_translate_command():
    # Arrange - 准备测试数据和环境
    translator = NaturalLanguageTranslator()
    user_input = "显示当前时间"
    context = Context()
    
    # Act - 执行被测试的操作
    result = translator.translate(user_input, context)
    
    # Assert - 验证结果
    assert result.generated_command == "Get-Date"
    assert result.confidence_score > 0.9
    assert result.explanation is not None
```

**使用 fixtures**:
```python
# conftest.py
import pytest
from src.config import ConfigManager

@pytest.fixture
def config():
    """提供测试配置"""
    return ConfigManager().get_config()

@pytest.fixture
def mock_storage():
    """提供 mock 存储"""
    storage = Mock()
    storage.save_history.return_value = True
    storage.load_history.return_value = []
    return storage

# test_example.py
def test_with_fixtures(config, mock_storage):
    """使用 fixtures 的测试"""
    manager = ContextManager(storage=mock_storage)
    # 测试逻辑
```

**参数化测试**:
```python
import pytest

@pytest.mark.parametrize("user_input,expected_command", [
    ("显示当前时间", "Get-Date"),
    ("列出所有文件", "Get-ChildItem"),
    ("显示进程", "Get-Process"),
])
def test_translate_commands(user_input, expected_command):
    """参数化测试多个命令翻译"""
    translator = NaturalLanguageTranslator()
    result = translator.translate(user_input, Context())
    assert result.generated_command == expected_command
```

**测试异常**:
```python
def test_invalid_input_raises_error():
    """测试无效输入抛出异常"""
    translator = NaturalLanguageTranslator()
    
    with pytest.raises(ValueError) as exc_info:
        translator.translate("", Context())
    
    assert "empty input" in str(exc_info.value).lower()
```

#### 3.3.3 测试覆盖率目标

- **核心模块**: ≥ 90%
  - `ai_engine/`
  - `security/`
  - `execution/`
  
- **工具模块**: ≥ 80%
  - `config/`
  - `storage/`
  - `context/`
  
- **总体覆盖率**: ≥ 85%

**运行覆盖率测试**:
```bash
# 生成覆盖率报告
pytest --cov=src tests/

# 生成 HTML 报告
pytest --cov=src --cov-report=html tests/

# 查看未覆盖的行
pytest --cov=src --cov-report=term-missing tests/
```

#### 3.3.4 Mock 和 Stub

**使用 unittest.mock**:
```python
from unittest.mock import Mock, patch, MagicMock

def test_with_mock():
    """使用 mock 对象"""
    # 创建 mock 对象
    mock_ai_provider = Mock()
    mock_ai_provider.generate.return_value = "Get-Date"
    
    # 使用 mock
    engine = AIEngine(provider=mock_ai_provider)
    result = engine.translate("显示时间")
    
    # 验证调用
    mock_ai_provider.generate.assert_called_once()

def test_with_patch():
    """使用 patch 装饰器"""
    with patch('src.ai_engine.providers.OllamaProvider') as mock_provider:
        mock_provider.return_value.generate.return_value = "Get-Date"
        
        engine = AIEngine()
        result = engine.translate("显示时间")
        
        assert result == "Get-Date"
```

### 3.4 文档规范

#### 3.4.1 文档类型

1. **用户文档**: 面向最终用户
   - 快速开始指南
   - 用户手册
   - 常见问题

2. **开发者文档**: 面向开发者
   - 架构文档
   - 开发者指南
   - API 参考

3. **运维文档**: 面向运维人员
   - 部署指南
   - 配置参考
   - 故障排除

#### 3.4.2 文档结构

每个文档应包含：

```markdown
# 文档标题

> **文档类型**: [用户文档/开发者文档/运维文档] | **最后更新**: YYYY-MM-DD

简短的文档描述（1-2 句话）

## 目录（可选，长文档需要）

## 主要内容

### 二级标题

内容...

## 相关文档

- [文档1](link1.md) - 简短描述
- [文档2](link2.md) - 简短描述

## 获取帮助

- 问题反馈: [GitHub Issues](link)
- 讨论: [GitHub Discussions](link)
```

#### 3.4.3 代码示例规范

**使用语言标识**:
````markdown
```python
# Python 代码
from src.main import PowerShellAssistant
assistant = PowerShellAssistant()
```

```bash
# Bash 命令
python src/main.py --interactive
```

```yaml
# YAML 配置
ai:
  provider: ollama
  model_name: llama2
```

```powershell
# PowerShell 命令
Get-Process | Sort-Object CPU -Descending
```
````

**提供完整可运行的示例**:
```markdown
## 示例：处理用户请求

```python
from src.main import PowerShellAssistant

# 创建助手实例
assistant = PowerShellAssistant()

# 处理请求
result = assistant.process_request(
    user_input="显示CPU使用率最高的5个进程",
    auto_execute=True
)

# 检查结果
if result.success:
    print(f"命令: {result.command}")
    print(f"输出: {result.output}")
else:
    print(f"错误: {result.error}")
```

**输出**:
```
命令: Get-Process | Sort-Object CPU -Descending | Select-Object -First 5
输出:
Handles  NPM(K)    PM(K)      WS(K)     CPU(s)     Id  SI ProcessName
-------  ------    -----      -----     ------     --  -- -----------
   1234      56   123456     234567     123.45   1234   1 chrome
    567      23    45678      67890      45.67   5678   1 code
```
```

#### 3.4.4 文档维护

**文档更新检查清单**:
- [ ] 内容准确无误
- [ ] 代码示例可运行
- [ ] 链接正确有效
- [ ] 格式规范统一
- [ ] 拼写检查通过
- [ ] 相关文档已更新
- [ ] 添加到文档索引

**文档版本控制**:
- 在文档头部标注最后更新日期
- 重大变更记录在 CHANGELOG.md
- 使用 Git 跟踪文档变更

---

## 4. 扩展开发

### 4.1 如何添加 AI 提供商

#### 4.1.1 创建提供商类

创建新的 AI 提供商需要实现 `AIProvider` 抽象基类：

```python
# src/ai_engine/providers.py

from abc import ABC, abstractmethod
from typing import Optional
from src.interfaces.base import Suggestion, Context

class AIProvider(ABC):
    """AI 提供商抽象基类"""
    
    @abstractmethod
    def generate(self, text: str, context: Context) -> Suggestion:
        """生成命令建议
        
        Args:
            text: 用户输入的自然语言
            context: 上下文信息
            
        Returns:
            命令建议对象
        """
        pass

class CustomAIProvider(AIProvider):
    """自定义 AI 提供商实现"""
    
    def __init__(self, config: dict):
        """初始化提供商
        
        Args:
            config: 配置字典，包含：
                - api_key: API 密钥
                - endpoint: API 端点
                - model_name: 模型名称
                - temperature: 温度参数
                - max_tokens: 最大令牌数
        """
        self.config = config
        self.api_key = config.get('api_key')
        self.endpoint = config.get('endpoint')
        self.model_name = config.get('model_name', 'default-model')
        self.temperature = config.get('temperature', 0.7)
        self.max_tokens = config.get('max_tokens', 256)
        
        # 初始化客户端
        self.client = self._initialize_client()
    
    def _initialize_client(self):
        """初始化 API 客户端"""
        # 实现客户端初始化逻辑
        # 例如：return CustomAPIClient(api_key=self.api_key)
        pass
    
    def generate(self, text: str, context: Context) -> Suggestion:
        """生成命令建议
        
        Args:
            text: 用户输入的自然语言
            context: 上下文信息
            
        Returns:
            命令建议对象
        """
        # 1. 构建提示词
        prompt = self._build_prompt(text, context)
        
        # 2. 调用 API 生成
        response = self._call_api(prompt)
        
        # 3. 解析响应
        return self._parse_response(response, text)
    
    def _build_prompt(self, text: str, context: Context) -> str:
        """构建提示词
        
        Args:
            text: 用户输入
            context: 上下文信息
            
        Returns:
            完整的提示词
        """
        # 基础提示词
        system_prompt = (
            "你是一个 PowerShell 命令助手。"
            "将用户的中文描述转换为对应的 PowerShell 命令。"
            "只返回命令，不要包含解释。"
        )
        
        # 添加上下文
        context_info = ""
        if context.command_history:
            recent_commands = context.command_history[-3:]
            context_info = "最近的命令：\n" + "\n".join(
                f"- {cmd.translated_command}" 
                for cmd in recent_commands
            )
        
        # 组合提示词
        full_prompt = f"{system_prompt}\n\n{context_info}\n\n用户输入：{text}\n\nPowerShell 命令："
        return full_prompt
    
    def _call_api(self, prompt: str) -> dict:
        """调用 API
        
        Args:
            prompt: 提示词
            
        Returns:
            API 响应
        """
        # 实现 API 调用逻辑
        response = self.client.generate(
            prompt=prompt,
            model=self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        return response
    
    def _parse_response(self, response: dict, original_input: str) -> Suggestion:
        """解析 API 响应
        
        Args:
            response: API 响应
            original_input: 原始用户输入
            
        Returns:
            命令建议对象
        """
        # 提取生成的命令
        generated_command = response.get('text', '').strip()
        
        # 提取置信度（如果 API 提供）
        confidence = response.get('confidence', 0.8)
        
        # 创建建议对象
        return Suggestion(
            original_input=original_input,
            generated_command=generated_command,
            confidence_score=confidence,
            explanation=f"由 {self.model_name} 生成",
            alternatives=response.get('alternatives', []),
            metadata={
                'provider': 'custom',
                'model': self.model_name,
                'temperature': self.temperature
            }
        )
```


#### 4.1.2 注册提供商

在 `src/ai_engine/engine.py` 中注册新的提供商：

```python
# src/ai_engine/engine.py

from src.ai_engine.providers import (
    OllamaProvider,
    OpenAIProvider,
    AzureOpenAIProvider,
    CustomAIProvider  # 导入自定义提供商
)

class AIEngine:
    """AI 引擎主类"""
    
    def __init__(self, config: dict):
        """初始化 AI 引擎"""
        self.config = config
        self.provider = self._create_provider()
    
    def _create_provider(self) -> AIProvider:
        """创建 AI 提供商实例"""
        provider_type = self.config.get('provider', 'ollama')
        
        providers = {
            'ollama': OllamaProvider,
            'openai': OpenAIProvider,
            'azure': AzureOpenAIProvider,
            'custom': CustomAIProvider,  # 注册自定义提供商
        }
        
        provider_class = providers.get(provider_type)
        if not provider_class:
            raise ValueError(f"Unknown provider: {provider_type}")
        
        return provider_class(self.config)
```

#### 4.1.3 配置提供商

在配置文件中添加提供商配置：

```yaml
# config/default.yaml

ai:
  provider: "custom"  # 使用自定义提供商
  
  # 自定义提供商配置
  custom:
    api_key: "your-api-key"
    endpoint: "https://api.example.com/v1"
    model_name: "custom-model-v1"
    temperature: 0.7
    max_tokens: 256
    timeout: 30
```

#### 4.1.4 测试提供商

编写测试确保提供商正常工作：

```python
# tests/ai_engine/test_custom_provider.py

import pytest
from src.ai_engine.providers import CustomAIProvider
from src.interfaces.base import Context

class TestCustomAIProvider:
    """测试自定义 AI 提供商"""
    
    def setup_method(self):
        """测试前设置"""
        self.config = {
            'api_key': 'test-key',
            'endpoint': 'https://api.example.com/v1',
            'model_name': 'test-model',
            'temperature': 0.7,
            'max_tokens': 256
        }
        self.provider = CustomAIProvider(self.config)
    
    def test_generate_simple_command(self):
        """测试生成简单命令"""
        text = "显示当前时间"
        context = Context()
        
        result = self.provider.generate(text, context)
        
        assert result.generated_command is not None
        assert result.confidence_score > 0
        assert result.explanation is not None
    
    def test_generate_with_context(self):
        """测试带上下文的生成"""
        text = "显示详细信息"
        context = Context(
            command_history=[
                CommandEntry(translated_command="Get-Process")
            ]
        )
        
        result = self.provider.generate(text, context)
        
        assert result.generated_command is not None
```

### 4.2 如何添加安全规则

#### 4.2.1 添加危险命令模式

在 `src/security/whitelist.py` 中添加新的危险命令模式：

```python
# src/security/whitelist.py

from src.interfaces.base import RiskLevel

class CommandWhitelist:
    """命令白名单验证器"""
    
    def __init__(self, config: dict):
        """初始化白名单"""
        self.config = config
        self.dangerous_patterns = self._load_dangerous_patterns()
        self.custom_rules = self._load_custom_rules()
    
    def _load_dangerous_patterns(self) -> List[Dict]:
        """加载危险命令模式"""
        return [
            # 文件删除
            {
                'pattern': r'Remove-Item.*-Recurse.*-Force',
                'description': '递归强制删除',
                'risk_level': RiskLevel.CRITICAL
            },
            {
                'pattern': r'rm\s+-rf\s+/',
                'description': '递归删除根目录',
                'risk_level': RiskLevel.CRITICAL
            },
            
            # 磁盘操作
            {
                'pattern': r'Format-Volume',
                'description': '格式化磁盘',
                'risk_level': RiskLevel.CRITICAL
            },
            
            # 系统操作
            {
                'pattern': r'Stop-Computer.*-Force',
                'description': '强制关机',
                'risk_level': RiskLevel.HIGH
            },
            {
                'pattern': r'Restart-Computer.*-Force',
                'description': '强制重启',
                'risk_level': RiskLevel.HIGH
            },
            
            # 注册表操作
            {
                'pattern': r'Set-ItemProperty.*HKLM:',
                'description': '修改系统注册表',
                'risk_level': RiskLevel.HIGH
            },
            
            # 网络操作
            {
                'pattern': r'Invoke-WebRequest.*\|.*Invoke-Expression',
                'description': '下载并执行远程脚本',
                'risk_level': RiskLevel.CRITICAL
            },
            
            # 添加自定义危险模式
            {
                'pattern': r'Your-DangerousCommand',
                'description': '自定义危险命令',
                'risk_level': RiskLevel.HIGH
            },
        ]
    
    def _load_custom_rules(self) -> List[Dict]:
        """加载自定义规则"""
        return self.config.get('custom_rules', [])
    
    def add_custom_rule(
        self,
        pattern: str,
        description: str,
        risk_level: RiskLevel,
        action: str = 'block'
    ):
        """添加自定义规则
        
        Args:
            pattern: 正则表达式模式
            description: 规则描述
            risk_level: 风险等级
            action: 动作（block/warn/allow）
        """
        rule = {
            'pattern': pattern,
            'description': description,
            'risk_level': risk_level,
            'action': action
        }
        self.custom_rules.append(rule)
```


#### 4.2.2 配置自定义规则

在配置文件中添加自定义安全规则：

```yaml
# config/default.yaml

security:
  whitelist_mode: "strict"  # strict, moderate, permissive
  require_confirmation: true
  
  # 自定义安全规则
  custom_rules:
    # 允许公司批准的脚本
    - pattern: ".*\\\\company_scripts\\\\.*"
      action: "allow"
      risk_level: "low"
      description: "允许执行公司批准的脚本"
    
    # 阻止删除重要文件
    - pattern: "Remove-Item.*important_files"
      action: "block"
      risk_level: "critical"
      description: "阻止删除重要文件目录"
    
    # 警告但允许执行
    - pattern: "Stop-Service.*critical-service"
      action: "warn"
      risk_level: "high"
      description: "停止关键服务需要确认"
```

#### 4.2.3 实现自定义验证逻辑

```python
# src/security/custom_validator.py

from src.interfaces.base import ValidationResult, RiskLevel

class CustomValidator:
    """自定义验证器"""
    
    def __init__(self, config: dict):
        """初始化验证器"""
        self.config = config
        self.rules = self._load_rules()
    
    def validate(self, command: str, context: Context) -> ValidationResult:
        """验证命令
        
        Args:
            command: 要验证的命令
            context: 上下文信息
            
        Returns:
            验证结果
        """
        # 1. 检查命令长度
        if len(command) > 1000:
            return ValidationResult(
                is_valid=False,
                risk_level=RiskLevel.HIGH,
                blocked_reasons=["命令过长，可能存在安全风险"]
            )
        
        # 2. 检查是否包含敏感路径
        sensitive_paths = ['/etc', 'C:\\Windows\\System32']
        for path in sensitive_paths:
            if path in command:
                return ValidationResult(
                    is_valid=True,
                    risk_level=RiskLevel.HIGH,
                    requires_confirmation=True,
                    warnings=[f"命令涉及敏感路径: {path}"]
                )
        
        # 3. 检查是否在工作时间外执行
        if not self._is_working_hours():
            return ValidationResult(
                is_valid=True,
                risk_level=RiskLevel.MEDIUM,
                requires_confirmation=True,
                warnings=["当前不在工作时间，请确认是否执行"]
            )
        
        # 4. 检查用户权限
        if not self._check_user_permission(command, context):
            return ValidationResult(
                is_valid=False,
                risk_level=RiskLevel.HIGH,
                blocked_reasons=["用户无权限执行此命令"]
            )
        
        return ValidationResult(
            is_valid=True,
            risk_level=RiskLevel.LOW
        )
    
    def _is_working_hours(self) -> bool:
        """检查是否在工作时间"""
        from datetime import datetime
        now = datetime.now()
        return 9 <= now.hour < 18
    
    def _check_user_permission(self, command: str, context: Context) -> bool:
        """检查用户权限"""
        # 实现权限检查逻辑
        return True
```

### 4.3 如何添加存储后端

#### 4.3.1 实现存储接口

创建新的存储后端需要实现 `StorageInterface`：

```python
# src/storage/database_storage.py

from typing import List, Optional, Dict, Any
from src.storage.interfaces import StorageInterface
from src.interfaces.base import CommandEntry

class DatabaseStorage(StorageInterface):
    """数据库存储实现"""
    
    def __init__(self, connection_string: str):
        """初始化数据库连接
        
        Args:
            connection_string: 数据库连接字符串
                例如: "postgresql://user:pass@localhost/dbname"
        """
        self.connection_string = connection_string
        self.connection = self._connect()
        self._initialize_tables()
    
    def _connect(self):
        """建立数据库连接"""
        # 使用 SQLAlchemy 或其他 ORM
        from sqlalchemy import create_engine
        engine = create_engine(self.connection_string)
        return engine
    
    def _initialize_tables(self):
        """初始化数据库表"""
        # 创建必要的表结构
        with self.connection.begin() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS command_history (
                    id SERIAL PRIMARY KEY,
                    command_id VARCHAR(255) UNIQUE,
                    user_input TEXT,
                    translated_command TEXT,
                    status VARCHAR(50),
                    output TEXT,
                    error TEXT,
                    return_code INTEGER,
                    execution_time FLOAT,
                    confidence_score FLOAT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
    
    def save_history(self, entry: CommandEntry) -> bool:
        """保存命令历史
        
        Args:
            entry: 命令历史条目
            
        Returns:
            是否保存成功
        """
        try:
            with self.connection.begin() as conn:
                conn.execute("""
                    INSERT INTO command_history (
                        command_id, user_input, translated_command,
                        status, output, error, return_code,
                        execution_time, confidence_score, timestamp
                    ) VALUES (
                        :command_id, :user_input, :translated_command,
                        :status, :output, :error, :return_code,
                        :execution_time, :confidence_score, :timestamp
                    )
                """, {
                    'command_id': entry.command_id,
                    'user_input': entry.user_input,
                    'translated_command': entry.translated_command,
                    'status': entry.status.value,
                    'output': entry.output,
                    'error': entry.error,
                    'return_code': entry.return_code,
                    'execution_time': entry.execution_time,
                    'confidence_score': entry.confidence_score,
                    'timestamp': entry.timestamp
                })
            return True
        except Exception as e:
            logger.error(f"Failed to save history: {e}")
            return False
    
    def load_history(self, limit: int = 100) -> List[CommandEntry]:
        """加载命令历史
        
        Args:
            limit: 最大返回数量
            
        Returns:
            命令历史列表
        """
        try:
            with self.connection.begin() as conn:
                result = conn.execute("""
                    SELECT * FROM command_history
                    ORDER BY timestamp DESC
                    LIMIT :limit
                """, {'limit': limit})
                
                entries = []
                for row in result:
                    entry = CommandEntry(
                        command_id=row['command_id'],
                        user_input=row['user_input'],
                        translated_command=row['translated_command'],
                        status=CommandStatus(row['status']),
                        output=row['output'],
                        error=row['error'],
                        return_code=row['return_code'],
                        execution_time=row['execution_time'],
                        confidence_score=row['confidence_score'],
                        timestamp=row['timestamp']
                    )
                    entries.append(entry)
                
                return entries
        except Exception as e:
            logger.error(f"Failed to load history: {e}")
            return []
    
    def save_cache(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """保存缓存"""
        # 实现缓存保存逻辑
        pass
    
    def load_cache(self, key: str) -> Optional[Any]:
        """加载缓存"""
        # 实现缓存加载逻辑
        pass
    
    def delete_cache(self, key: str) -> bool:
        """删除缓存"""
        # 实现缓存删除逻辑
        pass
```


#### 4.3.2 注册存储后端

在存储工厂中注册新的存储后端：

```python
# src/storage/factory.py

from src.storage.interfaces import StorageInterface
from src.storage.file_storage import FileStorage
from src/storage.database_storage import DatabaseStorage

class StorageFactory:
    """存储工厂"""
    
    @staticmethod
    def create_storage(storage_type: str, config: dict) -> StorageInterface:
        """创建存储实例
        
        Args:
            storage_type: 存储类型（file, database）
            config: 存储配置
            
        Returns:
            存储实例
            
        Raises:
            ValueError: 不支持的存储类型
        """
        if storage_type == "file":
            base_path = config.get('base_path', '~/.ai-powershell')
            return FileStorage(base_path)
        
        elif storage_type == "database":
            connection_string = config.get('connection_string')
            if not connection_string:
                raise ValueError("Database connection string is required")
            return DatabaseStorage(connection_string)
        
        else:
            raise ValueError(f"Unsupported storage type: {storage_type}")
    
    @staticmethod
    def get_default_storage() -> StorageInterface:
        """获取默认存储实例"""
        from src.config import ConfigManager
        config = ConfigManager().get_config()
        return StorageFactory.create_storage(
            config.storage.type,
            config.storage.dict()
        )
```

#### 4.3.3 配置存储后端

```yaml
# config/default.yaml

storage:
  type: "database"  # file, database
  
  # 数据库存储配置
  database:
    connection_string: "postgresql://user:pass@localhost/ai_powershell"
    pool_size: 5
    max_overflow: 10
    pool_timeout: 30
  
  # 文件存储配置（备用）
  file:
    base_path: "~/.ai-powershell"
    cache_ttl: 3600
    max_history: 1000
```

### 4.4 如何开发插件

#### 4.4.1 插件系统架构

```python
# src/plugins/base.py

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class PluginInterface(ABC):
    """插件接口"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """插件名称"""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """插件版本"""
        pass
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """初始化插件
        
        Args:
            config: 插件配置
            
        Returns:
            是否初始化成功
        """
        pass
    
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行插件逻辑
        
        Args:
            context: 执行上下文
            
        Returns:
            执行结果
        """
        pass
    
    @abstractmethod
    def cleanup(self) -> bool:
        """清理插件资源
        
        Returns:
            是否清理成功
        """
        pass
```

#### 4.4.2 创建示例插件

```python
# plugins/notification_plugin.py

from src.plugins.base import PluginInterface
from typing import Dict, Any

class NotificationPlugin(PluginInterface):
    """通知插件 - 在命令执行后发送通知"""
    
    @property
    def name(self) -> str:
        return "notification"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        """初始化插件"""
        self.enabled = config.get('enabled', True)
        self.notification_type = config.get('type', 'desktop')
        self.webhook_url = config.get('webhook_url')
        
        if self.notification_type == 'webhook' and not self.webhook_url:
            logger.error("Webhook URL is required for webhook notifications")
            return False
        
        logger.info(f"Notification plugin initialized: {self.notification_type}")
        return True
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行通知逻辑"""
        if not self.enabled:
            return {'success': True, 'skipped': True}
        
        # 获取命令执行结果
        command = context.get('command')
        success = context.get('success')
        output = context.get('output')
        
        # 构建通知消息
        message = self._build_message(command, success, output)
        
        # 发送通知
        if self.notification_type == 'desktop':
            self._send_desktop_notification(message)
        elif self.notification_type == 'webhook':
            self._send_webhook_notification(message)
        
        return {'success': True, 'message': message}
    
    def cleanup(self) -> bool:
        """清理资源"""
        logger.info("Notification plugin cleaned up")
        return True
    
    def _build_message(self, command: str, success: bool, output: str) -> str:
        """构建通知消息"""
        status = "成功" if success else "失败"
        return f"命令执行{status}\n命令: {command}\n输出: {output[:100]}"
    
    def _send_desktop_notification(self, message: str):
        """发送桌面通知"""
        try:
            # Windows
            if sys.platform == 'win32':
                from win10toast import ToastNotifier
                toaster = ToastNotifier()
                toaster.show_toast("AI PowerShell", message, duration=5)
            
            # Linux
            elif sys.platform == 'linux':
                import subprocess
                subprocess.run(['notify-send', 'AI PowerShell', message])
            
            # macOS
            elif sys.platform == 'darwin':
                import subprocess
                subprocess.run([
                    'osascript', '-e',
                    f'display notification "{message}" with title "AI PowerShell"'
                ])
        except Exception as e:
            logger.error(f"Failed to send desktop notification: {e}")
    
    def _send_webhook_notification(self, message: str):
        """发送 Webhook 通知"""
        try:
            import requests
            response = requests.post(
                self.webhook_url,
                json={'text': message},
                timeout=5
            )
            response.raise_for_status()
        except Exception as e:
            logger.error(f"Failed to send webhook notification: {e}")
```

#### 4.4.3 插件管理器

```python
# src/plugins/manager.py

from typing import Dict, List, Optional
from src.plugins.base import PluginInterface

class PluginManager:
    """插件管理器"""
    
    def __init__(self, config: dict):
        """初始化插件管理器"""
        self.config = config
        self.plugins: Dict[str, PluginInterface] = {}
        self._load_plugins()
    
    def _load_plugins(self):
        """加载插件"""
        plugin_configs = self.config.get('plugins', {})
        
        for plugin_name, plugin_config in plugin_configs.items():
            if not plugin_config.get('enabled', False):
                continue
            
            try:
                plugin = self._create_plugin(plugin_name, plugin_config)
                if plugin and plugin.initialize(plugin_config):
                    self.plugins[plugin_name] = plugin
                    logger.info(f"Plugin loaded: {plugin_name}")
            except Exception as e:
                logger.error(f"Failed to load plugin {plugin_name}: {e}")
    
    def _create_plugin(self, name: str, config: dict) -> Optional[PluginInterface]:
        """创建插件实例"""
        # 动态导入插件
        try:
            module_path = config.get('module', f'plugins.{name}_plugin')
            class_name = config.get('class', f'{name.capitalize()}Plugin')
            
            module = __import__(module_path, fromlist=[class_name])
            plugin_class = getattr(module, class_name)
            
            return plugin_class()
        except Exception as e:
            logger.error(f"Failed to create plugin {name}: {e}")
            return None
    
    def execute_plugins(self, context: Dict[str, any]) -> List[Dict[str, any]]:
        """执行所有插件"""
        results = []
        for name, plugin in self.plugins.items():
            try:
                result = plugin.execute(context)
                results.append({
                    'plugin': name,
                    'result': result
                })
            except Exception as e:
                logger.error(f"Plugin {name} execution failed: {e}")
                results.append({
                    'plugin': name,
                    'error': str(e)
                })
        return results
    
    def cleanup(self):
        """清理所有插件"""
        for name, plugin in self.plugins.items():
            try:
                plugin.cleanup()
            except Exception as e:
                logger.error(f"Failed to cleanup plugin {name}: {e}")
```

#### 4.4.4 配置插件

```yaml
# config/default.yaml

plugins:
  # 通知插件
  notification:
    enabled: true
    module: "plugins.notification_plugin"
    class: "NotificationPlugin"
    type: "desktop"  # desktop, webhook
    webhook_url: "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
  
  # 日志插件
  logging:
    enabled: true
    module: "plugins.logging_plugin"
    class: "LoggingPlugin"
    log_level: "INFO"
    log_file: "logs/plugin.log"
  
  # 统计插件
  statistics:
    enabled: false
    module: "plugins.statistics_plugin"
    class: "StatisticsPlugin"
    report_interval: 3600
```

---

## 5. 调试技巧

### 5.1 日志使用方法

#### 5.1.1 基本日志记录

```python
from src.log_engine.engine import LogEngine

# 获取日志记录器
logger = LogEngine.get_logger(__name__)

# 不同级别的日志
logger.debug("详细的调试信息")
logger.info("一般信息")
logger.warning("警告信息")
logger.error("错误信息")
logger.critical("严重错误")
```

#### 5.1.2 结构化日志

```python
# 使用 extra 参数添加结构化数据
logger.info(
    "User request processed",
    extra={
        'correlation_id': correlation_id,
        'user_input': user_input,
        'command': command,
        'duration_ms': duration * 1000,
        'success': True
    }
)

# 日志输出（JSON 格式）
{
    "timestamp": "2025-01-11T10:30:45.123Z",
    "level": "INFO",
    "message": "User request processed",
    "correlation_id": "abc-123",
    "user_input": "显示当前时间",
    "command": "Get-Date",
    "duration_ms": 150.5,
    "success": true
}
```

#### 5.1.3 异常日志

```python
try:
    result = process_data(data)
except Exception as e:
    # 记录异常堆栈
    logger.error(
        "Failed to process data",
        extra={'data': data},
        exc_info=True  # 包含异常堆栈
    )
    raise
```

#### 5.1.4 性能日志

```python
import time

def log_performance(func):
    """性能日志装饰器"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            logger.info(
                f"{func.__name__} completed",
                extra={
                    'function': func.__name__,
                    'duration_ms': duration * 1000,
                    'success': True
                }
            )
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"{func.__name__} failed",
                extra={
                    'function': func.__name__,
                    'duration_ms': duration * 1000,
                    'error': str(e)
                },
                exc_info=True
            )
            raise
    return wrapper

@log_performance
def expensive_operation(data):
    """耗时操作"""
    # 处理逻辑
    pass
```

#### 5.1.5 调整日志级别

```python
# 在代码中动态调整
logger.setLevel(logging.DEBUG)

# 或在配置文件中设置
# config.yaml
logging:
  level: "DEBUG"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### 5.2 断点调试技巧

#### 5.2.1 使用 pdb 调试器

```python
import pdb

def my_function(param):
    # 设置断点
    pdb.set_trace()
    
    # 代码会在这里暂停
    result = process(param)
    return result

# 或使用 breakpoint() (Python 3.7+)
def my_function(param):
    breakpoint()  # 更简洁的方式
    result = process(param)
    return result
```

**pdb 常用命令**:
```
n (next)      - 执行下一行
s (step)      - 进入函数
c (continue)  - 继续执行
l (list)      - 显示当前代码
p var         - 打印变量值
pp var        - 美化打印变量
w (where)     - 显示调用栈
u (up)        - 上移一层调用栈
d (down)      - 下移一层调用栈
q (quit)      - 退出调试器
```

#### 5.2.2 使用 VS Code 调试

创建 `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Main",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/src/main.py",
            "console": "integratedTerminal",
            "args": ["--interactive"],
            "env": {
                "PYTHONPATH": "${workspaceFolder}"
            }
        },
        {
            "name": "Python: Current File",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal"
        },
        {
            "name": "Python: Pytest",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": [
                "${workspaceFolder}/tests",
                "-v",
                "-s"
            ],
            "console": "integratedTerminal"
        }
    ]
}
```

**使用步骤**:
1. 在代码行号左侧点击设置断点（红点）
2. 按 F5 或点击"运行和调试"
3. 使用调试工具栏控制执行流程

#### 5.2.3 条件断点

```python
# 在 VS Code 中右键断点 -> 编辑断点 -> 添加条件
# 例如：只在 user_input 包含 "delete" 时暂停
user_input == "delete" or "remove" in user_input

# 或在代码中使用条件
if some_condition:
    breakpoint()
```

#### 5.2.4 日志断点

```python
# 在 VS Code 中右键断点 -> 编辑断点 -> 日志消息
# 例如：User input: {user_input}, Command: {command}

# 不会暂停执行，只输出日志
```

### 5.3 性能分析方法

#### 5.3.1 使用 cProfile

```python
import cProfile
import pstats

# 方法 1：装饰器
def profile(func):
    """性能分析装饰器"""
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()
        result = func(*args, **kwargs)
        profiler.disable()
        
        stats = pstats.Stats(profiler)
        stats.sort_stats('cumulative')
        stats.print_stats(10)  # 显示前 10 个最耗时的函数
        
        return result
    return wrapper

@profile
def my_function():
    # 函数逻辑
    pass

# 方法 2：上下文管理器
with cProfile.Profile() as profiler:
    my_function()
    
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats()

# 方法 3：命令行
# python -m cProfile -o output.prof src/main.py
# python -m pstats output.prof
```

#### 5.3.2 使用 line_profiler

```bash
# 安装
pip install line_profiler

# 使用装饰器
@profile
def my_function():
    # 函数逻辑
    pass

# 运行
kernprof -l -v script.py
```

#### 5.3.3 使用 memory_profiler

```bash
# 安装
pip install memory_profiler

# 使用装饰器
from memory_profiler import profile

@profile
def my_function():
    # 函数逻辑
    pass

# 运行
python -m memory_profiler script.py
```

#### 5.3.4 使用 py-spy

```bash
# 安装
pip install py-spy

# 实时性能分析（不需要修改代码）
py-spy top --pid <process_id>

# 生成火焰图
py-spy record -o profile.svg --pid <process_id>

# 分析脚本
py-spy record -o profile.svg -- python src/main.py
```

### 5.4 问题排查流程

#### 5.4.1 系统性排查步骤

**步骤 1: 收集信息**
```python
# 记录关键信息
logger.info(
    "Issue occurred",
    extra={
        'python_version': sys.version,
        'platform': sys.platform,
        'config': config.dict(),
        'environment': dict(os.environ)
    }
)
```

**步骤 2: 重现问题**
```python
# 创建最小可重现示例
def minimal_reproduction():
    """最小可重现示例"""
    assistant = PowerShellAssistant()
    result = assistant.process_request("问题输入")
    return result
```

**步骤 3: 隔离问题**
```python
# 逐步注释代码，找出问题所在
def debug_step_by_step():
    # 步骤 1
    logger.debug("Step 1: Initialize")
    assistant = PowerShellAssistant()
    
    # 步骤 2
    logger.debug("Step 2: Translate")
    suggestion = assistant.ai_engine.translate(user_input)
    
    # 步骤 3
    logger.debug("Step 3: Validate")
    validation = assistant.security_engine.validate(suggestion.command)
    
    # 步骤 4
    logger.debug("Step 4: Execute")
    result = assistant.executor.execute(suggestion.command)
```

**步骤 4: 验证修复**
```python
# 编写测试验证修复
def test_fix():
    """验证修复的测试"""
    assistant = PowerShellAssistant()
    result = assistant.process_request("之前失败的输入")
    assert result.success
```

#### 5.4.2 常见问题排查

**问题 1: AI 翻译不准确**
```python
# 检查点 1: 查看提示词
logger.debug("Prompt", extra={'prompt': prompt})

# 检查点 2: 查看 AI 响应
logger.debug("AI Response", extra={'response': response})

# 检查点 3: 检查规则匹配
logger.debug("Rule Match", extra={'matched_rule': rule})

# 检查点 4: 查看缓存
logger.debug("Cache", extra={'cache_hit': cache_hit})
```

**问题 2: 命令执行失败**
```python
# 检查点 1: 验证命令语法
logger.debug("Command", extra={'command': command})

# 检查点 2: 检查平台兼容性
logger.debug("Platform", extra={'platform': sys.platform})

# 检查点 3: 查看执行输出
logger.debug("Execution", extra={
    'stdout': stdout,
    'stderr': stderr,
    'return_code': return_code
})

# 检查点 4: 检查编码问题
logger.debug("Encoding", extra={'encoding': encoding})
```

**问题 3: 性能问题**
```python
# 检查点 1: 测量各阶段耗时
import time

start = time.time()
# 操作 1
duration1 = time.time() - start
logger.debug("Operation 1", extra={'duration_ms': duration1 * 1000})

start = time.time()
# 操作 2
duration2 = time.time() - start
logger.debug("Operation 2", extra={'duration_ms': duration2 * 1000})

# 检查点 2: 检查缓存命中率
logger.debug("Cache Stats", extra={
    'hits': cache_hits,
    'misses': cache_misses,
    'hit_rate': cache_hits / (cache_hits + cache_misses)
})

# 检查点 3: 检查资源使用
import psutil
process = psutil.Process()
logger.debug("Resource Usage", extra={
    'memory_mb': process.memory_info().rss / 1024 / 1024,
    'cpu_percent': process.cpu_percent()
})
```

#### 5.4.3 使用调试工具

**pytest 调试选项**:
```bash
# 在失败时进入调试器
pytest --pdb tests/

# 在第一个失败时停止
pytest -x tests/

# 显示详细输出
pytest -vv tests/

# 显示打印输出
pytest -s tests/

# 只运行失败的测试
pytest --lf tests/

# 运行上次失败和新修改的测试
pytest --ff tests/

# 显示最慢的 10 个测试
pytest --durations=10 tests/
```

**使用 ipdb（增强的 pdb）**:
```bash
# 安装
pip install ipdb

# 使用
import ipdb
ipdb.set_trace()

# 或设置为默认调试器
export PYTHONBREAKPOINT=ipdb.set_trace
```

**使用 pudb（全屏调试器）**:
```bash
# 安装
pip install pudb

# 使用
import pudb
pudb.set_trace()

# 或从命令行运行
python -m pudb script.py
```

---

## 6. 部署运维

### 6.1 部署方式

#### 6.1.1 单机部署

**标准安装**:
```bash
# 1. 克隆项目
git clone https://github.com/0green7hand0/AI-PowerShell.git
cd AI-PowerShell

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 .\venv\Scripts\Activate.ps1  # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置系统
cp config/default.yaml config.yaml
# 编辑 config.yaml 根据需要修改配置

# 5. 验证安装
python scripts/verify_installation.py

# 6. 启动服务
python src/main.py --interactive
```

**使用安装脚本**:
```bash
# Windows
.\scripts\install.ps1

# Linux/macOS
bash scripts/install.sh
```

#### 6.1.2 Docker 部署

**创建 Dockerfile**:
```dockerfile
# Dockerfile
FROM python:3.11-slim

# 安装 PowerShell
RUN apt-get update && \
    apt-get install -y wget apt-transport-https software-properties-common && \
    wget -q https://packages.microsoft.com/config/debian/11/packages-microsoft-prod.deb && \
    dpkg -i packages-microsoft-prod.deb && \
    apt-get update && \
    apt-get install -y powershell && \
    rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 创建数据目录
RUN mkdir -p /data/logs /data/history /data/cache

# 设置环境变量
ENV PYTHONPATH=/app
ENV AI_POWERSHELL_DATA_DIR=/data

# 暴露端口（如果有 Web UI）
EXPOSE 8000

# 启动命令
CMD ["python", "src/main.py", "--interactive"]
```

**构建和运行**:
```bash
# 构建镜像
docker build -t ai-powershell:latest .

# 运行容器
docker run -it \
    --name ai-powershell \
    -v $(pwd)/config:/app/config \
    -v $(pwd)/data:/data \
    ai-powershell:latest

# 后台运行
docker run -d \
    --name ai-powershell \
    --restart unless-stopped \
    -v $(pwd)/config:/app/config \
    -v $(pwd)/data:/data \
    ai-powershell:latest
```

**使用 Docker Compose**:
```yaml
# docker-compose.yml
version: '3.8'

services:
  ai-powershell:
    build: .
    container_name: ai-powershell
    restart: unless-stopped
    volumes:
      - ./config:/app/config
      - ./data:/data
    environment:
      - AI_POWERSHELL_LOG_LEVEL=INFO
      - AI_POWERSHELL_CONFIG=/app/config/config.yaml
    ports:
      - "8000:8000"
    networks:
      - ai-powershell-network

  # 可选：数据库服务
  postgres:
    image: postgres:15
    container_name: ai-powershell-db
    restart: unless-stopped
    environment:
      - POSTGRES_DB=ai_powershell
      - POSTGRES_USER=ai_user
      - POSTGRES_PASSWORD=secure_password
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - ai-powershell-network

networks:
  ai-powershell-network:
    driver: bridge

volumes:
  postgres-data:
```

**启动服务**:
```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f ai-powershell

# 停止服务
docker-compose down

# 重启服务
docker-compose restart
```

#### 6.1.3 Kubernetes 部署

**创建 Deployment**:
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-powershell
  labels:
    app: ai-powershell
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ai-powershell
  template:
    metadata:
      labels:
        app: ai-powershell
    spec:
      containers:
      - name: ai-powershell
        image: ai-powershell:latest
        ports:
        - containerPort: 8000
        env:
        - name: AI_POWERSHELL_LOG_LEVEL
          value: "INFO"
        - name: AI_POWERSHELL_CONFIG
          value: "/app/config/config.yaml"
        volumeMounts:
        - name: config
          mountPath: /app/config
        - name: data
          mountPath: /data
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: config
        configMap:
          name: ai-powershell-config
      - name: data
        persistentVolumeClaim:
          claimName: ai-powershell-data
```

**创建 Service**:
```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: ai-powershell
spec:
  selector:
    app: ai-powershell
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

**创建 ConfigMap**:
```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: ai-powershell-config
data:
  config.yaml: |
    ai:
      provider: "ollama"
      model_name: "llama2"
    security:
      whitelist_mode: "strict"
    logging:
      level: "INFO"
```

**部署到 Kubernetes**:
```bash
# 应用配置
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# 查看状态
kubectl get pods
kubectl get services

# 查看日志
kubectl logs -f deployment/ai-powershell

# 扩容
kubectl scale deployment ai-powershell --replicas=5
```

### 6.2 配置管理方法

#### 6.2.1 配置文件管理

**配置层级**:
```
1. 默认配置: config/default.yaml
2. 项目配置: config.yaml
3. 用户配置: ~/.ai-powershell/config.yaml
4. 环境变量: AI_POWERSHELL_*
```

**配置合并策略**:
```python
# 配置优先级（从高到低）
# 1. 环境变量
# 2. 用户配置
# 3. 项目配置
# 4. 默认配置

from src.config import ConfigManager

manager = ConfigManager()
config = manager.get_config()  # 自动合并所有层级
```

**环境变量配置**:
```bash
# 设置环境变量
export AI_POWERSHELL_CONFIG="/path/to/config.yaml"
export AI_POWERSHELL_LOG_LEVEL="DEBUG"
export AI_POWERSHELL_AI_PROVIDER="ollama"
export AI_POWERSHELL_AI_MODEL="llama2"

# 在 Docker 中使用
docker run -e AI_POWERSHELL_LOG_LEVEL=DEBUG ai-powershell

# 在 Kubernetes 中使用
env:
- name: AI_POWERSHELL_LOG_LEVEL
  value: "DEBUG"
```

#### 6.2.2 配置验证

```python
# 验证配置
from src.config import ConfigManager

manager = ConfigManager()
try:
    config = manager.get_config()
    print("配置验证通过")
except Exception as e:
    print(f"配置验证失败: {e}")
```

#### 6.2.3 配置备份和恢复

```bash
# 备份配置
cp config.yaml config.yaml.backup.$(date +%Y%m%d)

# 恢复配置
cp config.yaml.backup.20250111 config.yaml

# 自动备份（在配置更新时）
# 配置文件会自动备份到 config/.backups/
```

### 6.3 监控告警方案

#### 6.3.1 日志监控

**日志收集**:
```yaml
# 使用 Filebeat 收集日志
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /app/logs/*.log
  json.keys_under_root: true
  json.add_error_key: true

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
  index: "ai-powershell-%{+yyyy.MM.dd}"
```

**日志分析**:
```python
# 使用 ELK Stack 分析日志
# Elasticsearch + Logstash + Kibana

# 创建 Kibana 仪表板
# - 请求量趋势
# - 错误率统计
# - 响应时间分布
# - 命令执行成功率
```

#### 6.3.2 性能监控

**使用 Prometheus**:
```python
# src/monitoring/metrics.py

from prometheus_client import Counter, Histogram, Gauge, start_http_server

# 定义指标
request_count = Counter(
    'ai_powershell_requests_total',
    'Total number of requests',
    ['status']
)

request_duration = Histogram(
    'ai_powershell_request_duration_seconds',
    'Request duration in seconds'
)

active_sessions = Gauge(
    'ai_powershell_active_sessions',
    'Number of active sessions'
)

# 记录指标
def process_request(user_input):
    with request_duration.time():
        try:
            result = assistant.process_request(user_input)
            request_count.labels(status='success').inc()
            return result
        except Exception as e:
            request_count.labels(status='error').inc()
            raise

# 启动 Prometheus 服务器
start_http_server(9090)
```

**Prometheus 配置**:
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'ai-powershell'
    static_configs:
      - targets: ['localhost:9090']
```

#### 6.3.3 告警配置

**Prometheus Alertmanager**:
```yaml
# alertmanager.yml
route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'team-notifications'

receivers:
- name: 'team-notifications'
  email_configs:
  - to: 'team@example.com'
  slack_configs:
  - api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
    channel: '#alerts'

# 告警规则
groups:
- name: ai-powershell
  rules:
  - alert: HighErrorRate
    expr: rate(ai_powershell_requests_total{status="error"}[5m]) > 0.1
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High error rate detected"
      description: "Error rate is {{ $value }} requests/second"
  
  - alert: SlowResponse
    expr: histogram_quantile(0.95, ai_powershell_request_duration_seconds) > 5
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "Slow response time"
      description: "95th percentile response time is {{ $value }} seconds"
```

### 6.4 备份恢复方法

#### 6.4.1 数据备份

**备份脚本**:
```bash
#!/bin/bash
# scripts/backup.sh

# 配置
BACKUP_DIR="/backup/ai-powershell"
DATA_DIR="$HOME/.ai-powershell"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$DATE.tar.gz"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据
tar -czf $BACKUP_FILE \
    $DATA_DIR/history.json \
    $DATA_DIR/config.yaml \
    $DATA_DIR/sessions/ \
    $DATA_DIR/cache/

# 保留最近 7 天的备份
find $BACKUP_DIR -name "backup_*.tar.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_FILE"
```

**自动备份（cron）**:
```bash
# 每天凌晨 2 点备份
0 2 * * * /path/to/scripts/backup.sh
```

#### 6.4.2 数据恢复

**恢复脚本**:
```bash
#!/bin/bash
# scripts/restore.sh

# 配置
BACKUP_FILE=$1
DATA_DIR="$HOME/.ai-powershell"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file>"
    exit 1
fi

# 备份当前数据
mv $DATA_DIR $DATA_DIR.old

# 恢复数据
tar -xzf $BACKUP_FILE -C /

echo "Restore completed from: $BACKUP_FILE"
echo "Old data backed up to: $DATA_DIR.old"
```

**使用方法**:
```bash
# 恢复数据
bash scripts/restore.sh /backup/ai-powershell/backup_20250111_020000.tar.gz
```

#### 6.4.3 数据库备份（如使用数据库）

**PostgreSQL 备份**:
```bash
#!/bin/bash
# scripts/backup_db.sh

# 配置
DB_NAME="ai_powershell"
DB_USER="ai_user"
BACKUP_DIR="/backup/database"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/db_backup_$DATE.sql"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据库
pg_dump -U $DB_USER -d $DB_NAME -F c -f $BACKUP_FILE

# 压缩备份
gzip $BACKUP_FILE

# 保留最近 30 天的备份
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +30 -delete

echo "Database backup completed: $BACKUP_FILE.gz"
```

**PostgreSQL 恢复**:
```bash
#!/bin/bash
# scripts/restore_db.sh

# 配置
BACKUP_FILE=$1
DB_NAME="ai_powershell"
DB_USER="ai_user"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file>"
    exit 1
fi

# 解压备份
gunzip -c $BACKUP_FILE > /tmp/restore.sql

# 恢复数据库
pg_restore -U $DB_USER -d $DB_NAME -c /tmp/restore.sql

# 清理临时文件
rm /tmp/restore.sql

echo "Database restore completed from: $BACKUP_FILE"
```

---

## 总结

本开发文档提供了 AI PowerShell 智能助手的完整开发指南，包括：

1. **环境搭建**: 详细的安装步骤和配置方法
2. **代码结构**: 清晰的目录组织和模块职责说明
3. **开发指南**: 编码规范、提交规范、测试规范和文档规范
4. **扩展开发**: 如何添加 AI 提供商、安全规则、存储后端和插件
5. **调试技巧**: 日志使用、断点调试、性能分析和问题排查
6. **部署运维**: 多种部署方式、配置管理、监控告警和备份恢复

通过本文档，开发者可以：
- 快速搭建开发环境
- 理解项目架构和代码组织
- 遵循统一的开发规范
- 扩展系统功能
- 高效调试和排查问题
- 部署和运维系统

## 相关文档

- [系统架构文档](../02-设计文档/design-doc.md) - 了解系统整体架构
- [用户手册](../03-用户手册/user-manual.md) - 用户使用指南
- [毕业论文](../01-论文/thesis.md) - 完整的毕业论文

## 获取帮助

如有问题，请通过以下方式联系：

- **GitHub Issues**: https://github.com/0green7hand0/AI-PowerShell/issues
- **GitHub Discussions**: https://github.com/0green7hand0/AI-PowerShell/discussions
- **项目文档**: https://github.com/0green7hand0/AI-PowerShell/tree/main/docs

---

**文档版本**: v2.0.0  
**最后更新**: 2025-01-11  
**维护者**: AI PowerShell 开发团队

