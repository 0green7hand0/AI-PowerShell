# AI PowerShell 智能助手用户手册

**版本**: 1.0  
**更新日期**: 2025年11月  
**适用系统**: Windows / Linux / macOS

---

## 目录

1. [快速入门](#1-快速入门)
   - 1.1 [系统简介](#11-系统简介)
   - 1.2 [安装指南](#12-安装指南)
   - 1.3 [第一个示例](#13-第一个示例)
   - 1.4 [常用命令](#14-常用命令)

2. [功能详解](#2-功能详解)
   - 2.1 [基本功能](#21-基本功能)
   - 2.2 [高级功能](#22-高级功能)
   - 2.3 [配置选项](#23-配置选项)
   - 2.4 [使用技巧](#24-使用技巧)

3. [使用场景](#3-使用场景)
   - 3.1 [系统管理](#31-系统管理)
   - 3.2 [文件操作](#32-文件操作)
   - 3.3 [网络诊断](#33-网络诊断)
   - 3.4 [开发辅助](#34-开发辅助)

4. [配置指南](#4-配置指南)
   - 4.1 [配置文件结构](#41-配置文件结构)
   - 4.2 [配置参数详解](#42-配置参数详解)
   - 4.3 [自定义规则](#43-自定义规则)
   - 4.4 [性能调优](#44-性能调优)

5. [故障排除](#5-故障排除)
   - 5.1 [常见问题](#51-常见问题)
   - 5.2 [错误代码](#52-错误代码)
   - 5.3 [调试技巧](#53-调试技巧)
   - 5.4 [获取帮助](#54-获取帮助)

6. [附录](#6-附录)
   - 6.1 [命令参考表](#61-命令参考表)
   - 6.2 [配置示例](#62-配置示例)
   - 6.3 [术语表](#63-术语表)
   - 6.4 [更新日志](#64-更新日志)

---


## 1. 快速入门

### 1.1 系统简介

AI PowerShell 智能助手是一款基于本地AI模型的智能命令行工具，它能够将您的中文自然语言描述转换为PowerShell命令并安全执行。

**核心特性**：
- 🌏 **完整中文支持**：支持中文输入和输出，无需学习复杂的PowerShell语法
- 🤖 **智能翻译**：结合规则匹配和AI模型，快速准确地生成命令
- 🛡️ **三层安全保护**：命令白名单、权限检查、沙箱执行，确保系统安全
- 🔄 **跨平台支持**：支持Windows、Linux和macOS操作系统
- 📝 **历史管理**：自动记录命令历史，方便查询和重用
- ⚙️ **灵活配置**：支持自定义规则和安全策略

**适用人群**：
- 系统管理员：简化日常运维工作
- 开发人员：提高开发效率
- PowerShell初学者：降低学习门槛
- 普通用户：轻松完成系统操作

---

### 1.2 安装指南

#### 1.2.1 系统要求

**最低配置**：
- 操作系统：Windows 10/11、Linux (Ubuntu 20.04+)、macOS 11+
- Python：3.8 或更高版本
- PowerShell：5.1 或 PowerShell Core 7.0+
- 内存：4GB RAM
- 磁盘空间：2GB 可用空间

**推荐配置**：
- 内存：8GB RAM 或更高
- CPU：4核心或更高
- 磁盘空间：5GB 可用空间（用于AI模型）

#### 1.2.2 Windows 安装步骤

**步骤1：安装Python**
```powershell
# 从 python.org 下载并安装 Python 3.8+
# 或使用 winget 安装
winget install Python.Python.3.11
```

**步骤2：安装PowerShell Core（可选但推荐）**
```powershell
# 使用 winget 安装
winget install Microsoft.PowerShell
```

**步骤3：克隆项目**
```powershell
git clone https://github.com/yourusername/AI-PowerShell.git
cd AI-PowerShell
```

**步骤4：安装依赖**
```powershell
# 创建虚拟环境（推荐）
python -m venv venv
.\venv\Scripts\activate

# 安装依赖包
pip install -r requirements.txt
```

**步骤5：配置系统**
```powershell
# 复制配置文件模板
copy config\default.yaml config\user.yaml

# 编辑配置文件（可选）
notepad config\user.yaml
```

**步骤6：验证安装**
```powershell
# 运行测试命令
python run.py --version
```

![Windows安装完成截图](../07-项目资料/screenshots/windows-install.png)

#### 1.2.3 Linux 安装步骤

**步骤1：安装依赖**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv git

# 安装 PowerShell Core
wget https://packages.microsoft.com/config/ubuntu/20.04/packages-microsoft-prod.deb
sudo dpkg -i packages-microsoft-prod.deb
sudo apt update
sudo apt install powershell
```

**步骤2：克隆项目**
```bash
git clone https://github.com/yourusername/AI-PowerShell.git
cd AI-PowerShell
```

**步骤3：安装依赖**
```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖包
pip install -r requirements.txt
```

**步骤4：配置系统**
```bash
# 复制配置文件
cp config/default.yaml config/user.yaml

# 编辑配置文件
nano config/user.yaml
```

**步骤5：验证安装**
```bash
python run.py --version
```

#### 1.2.4 macOS 安装步骤

**步骤1：安装Homebrew（如未安装）**
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**步骤2：安装依赖**
```bash
# 安装 Python
brew install python@3.11

# 安装 PowerShell Core
brew install --cask powershell

# 安装 Git
brew install git
```

**步骤3：克隆项目**
```bash
git clone https://github.com/yourusername/AI-PowerShell.git
cd AI-PowerShell
```

**步骤4：安装依赖**
```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖包
pip install -r requirements.txt
```

**步骤5：配置系统**
```bash
# 复制配置文件
cp config/default.yaml config/user.yaml

# 编辑配置文件
nano config/user.yaml
```

**步骤6：验证安装**
```bash
python run.py --version
```

---

### 1.3 第一个示例

安装完成后，让我们通过一个简单的例子来体验AI PowerShell智能助手的强大功能。

#### 示例1：查看当前时间

**启动交互模式**：
```bash
python run.py
```

**输入中文描述**：
```
> 显示当前时间
```

**系统响应**：
```
[AI翻译] Get-Date

[安全检查] ✓ 安全命令
[置信度] 95%

是否执行此命令？(y/n): y

[执行结果]
2025年11月11日 星期二 14:30:25
```

![第一个示例截图](../07-项目资料/screenshots/first-example.png)

#### 示例2：查看系统信息

**输入**：
```
> 显示系统信息
```

**系统响应**：
```
[AI翻译] Get-ComputerInfo | Select-Object CsName, OsName, OsVersion, CsProcessors

[安全检查] ✓ 安全命令
[置信度] 92%

是否执行此命令？(y/n): y

[执行结果]
CsName      : DESKTOP-ABC123
OsName      : Microsoft Windows 11 Pro
OsVersion   : 10.0.22621
CsProcessors: {Intel(R) Core(TM) i7-10700K CPU @ 3.80GHz}
```

#### 示例3：列出文件

**输入**：
```
> 列出当前目录的所有文件
```

**系统响应**：
```
[AI翻译] Get-ChildItem

[安全检查] ✓ 安全命令
[置信度] 98%

是否执行此命令？(y/n): y

[执行结果]
    目录: C:\Users\YourName\AI-PowerShell

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d-----        2025/11/10     10:30                config
d-----        2025/11/10     10:30                src
d-----        2025/11/10     10:30                tests
-a----        2025/11/10     10:30           1234 README.md
-a----        2025/11/10     10:30            567 requirements.txt
```

---

### 1.4 常用命令

#### 1.4.1 命令行模式

除了交互模式，您还可以使用命令行模式直接执行单个命令：

```bash
# 基本用法
python run.py "显示当前时间"

# 查看帮助
python run.py --help

# 查看版本
python run.py --version

# 查看历史记录
python run.py --history

# 清除历史记录
python run.py --clear-history

# 使用指定配置文件
python run.py --config custom.yaml "显示系统信息"

# 启用调试模式
python run.py --debug "列出进程"

# 导出历史记录
python run.py --export-history history.json
```

#### 1.4.2 交互模式命令

在交互模式下，除了输入自然语言描述外，还支持以下特殊命令：

| 命令 | 说明 | 示例 |
|------|------|------|
| `help` | 显示帮助信息 | `help` |
| `history` | 查看命令历史 | `history` |
| `history N` | 查看最近N条历史 | `history 10` |
| `clear` | 清屏 | `clear` |
| `config` | 查看当前配置 | `config` |
| `reload` | 重新加载配置 | `reload` |
| `exit` / `quit` | 退出程序 | `exit` |
| `!N` | 重新执行第N条历史命令 | `!5` |
| `!!` | 重新执行上一条命令 | `!!` |

#### 1.4.3 快速参考

**系统管理**：
```
显示当前时间
查看系统信息
显示CPU使用率最高的5个进程
查看磁盘使用情况
显示网络连接状态
```

**文件操作**：
```
列出当前目录的所有文件
查找名称包含"test"的文件
显示文件的详细信息
创建一个名为"backup"的文件夹
复制文件到指定目录
```

**进程管理**：
```
显示所有正在运行的进程
查找名为"chrome"的进程
停止指定进程
显示进程的详细信息
```

**网络诊断**：
```
测试与百度的连接
显示本机IP地址
查看网络适配器信息
显示路由表
测试DNS解析
```

![常用命令示例](../07-项目资料/screenshots/common-commands.png)

---


## 2. 功能详解

### 2.1 基本功能

#### 2.1.1 自然语言翻译

AI PowerShell智能助手的核心功能是将中文自然语言描述转换为PowerShell命令。

**工作原理**：
1. **规则匹配**：首先尝试使用预定义规则进行快速匹配
2. **AI生成**：如果规则匹配失败，使用本地AI模型生成命令
3. **错误检测**：验证生成的命令语法和可行性
4. **缓存优化**：缓存常用翻译结果，提高响应速度

**支持的描述方式**：
- 直接描述：`显示当前时间`
- 带参数描述：`显示CPU使用率最高的5个进程`
- 条件描述：`查找大于100MB的文件`
- 组合操作：`列出所有txt文件并按大小排序`

**示例**：
```
输入：显示内存使用情况
输出：Get-Process | Sort-Object WorkingSet -Descending | Select-Object -First 10 Name, @{Name="Memory(MB)";Expression={[math]::Round($_.WorkingSet/1MB,2)}}

输入：查找包含"error"的日志文件
输出：Get-ChildItem -Recurse -Filter "*.log" | Select-String -Pattern "error"

输入：显示最近修改的5个文件
输出：Get-ChildItem | Sort-Object LastWriteTime -Descending | Select-Object -First 5
```

![翻译功能示例](../07-项目资料/screenshots/translation-feature.png)

#### 2.1.2 命令执行

系统支持跨平台的PowerShell命令执行，自动处理平台差异。

**执行特性**：
- **实时输出**：命令执行过程中实时显示输出
- **超时控制**：可配置命令执行超时时间（默认30秒）
- **错误处理**：捕获并友好显示错误信息
- **返回码处理**：根据命令返回码判断执行状态
- **编码处理**：自动处理中文编码问题

**执行模式**：
- **直接执行**：安全命令直接执行
- **确认执行**：中等风险命令需要用户确认
- **拒绝执行**：高危命令被拒绝执行
- **沙箱执行**：可选的Docker容器隔离执行

**示例**：
```
> 显示当前进程数量
[AI翻译] (Get-Process).Count
[安全检查] ✓ 安全命令
[执行结果] 156

> 重启计算机
[AI翻译] Restart-Computer
[安全检查] ⚠ 高风险命令
[风险等级] HIGH
[需要权限] 管理员
此命令将重启计算机，是否继续？(y/n): n
[已取消] 命令未执行
```

#### 2.1.3 安全验证

系统采用三层安全机制，确保命令执行的安全性。

**第一层：命令白名单验证**
- 识别30+种危险命令模式
- 评估命令风险等级（SAFE、LOW、MEDIUM、HIGH、CRITICAL）
- 自动拦截高危命令

**危险命令示例**：
```
❌ Remove-Item -Recurse C:\          # 递归删除
❌ Format-Volume                     # 格式化磁盘
❌ Stop-Computer -Force              # 强制关机
❌ Set-ItemProperty HKLM:\           # 修改注册表
❌ Invoke-Expression (iwr url)       # 远程下载执行
```

**第二层：权限检查**
- 检测命令是否需要管理员权限
- 验证当前用户权限级别
- 提示权限不足或请求提升

**第三层：沙箱执行（可选）**
- 在Docker容器中隔离执行
- 限制资源使用（CPU、内存、网络）
- 防止对主机系统的影响

![安全验证流程](../07-项目资料/screenshots/security-validation.png)

#### 2.1.4 历史管理

系统自动记录所有命令历史，方便查询和重用。

**历史记录内容**：
- 用户输入的自然语言描述
- 翻译后的PowerShell命令
- 执行状态（成功/失败）
- 命令输出和错误信息
- 执行时间和时间戳
- 置信度评分

**查看历史**：
```bash
# 查看所有历史
python run.py --history

# 查看最近10条
python run.py --history --limit 10

# 搜索历史
python run.py --history --search "进程"

# 导出历史
python run.py --export-history history.json
```

**交互模式历史命令**：
```
> history              # 查看所有历史
> history 10           # 查看最近10条
> !5                   # 重新执行第5条命令
> !!                   # 重新执行上一条命令
```

**历史记录格式**：
```
[1] 2025-11-11 14:30:25
    输入: 显示当前时间
    命令: Get-Date
    状态: ✓ 成功
    置信度: 95%

[2] 2025-11-11 14:31:10
    输入: 显示CPU最高的进程
    命令: Get-Process | Sort-Object CPU -Descending | Select-Object -First 5
    状态: ✓ 成功
    置信度: 92%
```

---

### 2.2 高级功能

#### 2.2.1 上下文理解

系统能够理解会话上下文，支持连续对话和引用。

**上下文类型**：
- **工作目录上下文**：记住当前工作目录
- **变量上下文**：记住之前定义的变量
- **命令上下文**：理解"再次执行"、"上一个结果"等引用

**示例**：
```
> 进入Documents文件夹
[执行] Set-Location Documents

> 列出这里的文件
[理解上下文] 当前在Documents目录
[执行] Get-ChildItem

> 显示第一个文件的内容
[理解上下文] 引用上一个命令的结果
[执行] Get-Content (Get-ChildItem | Select-Object -First 1).Name
```

#### 2.2.2 批量操作

支持批量执行多个命令或处理多个对象。

**批量命令执行**：
```bash
# 使用脚本文件
python run.py --script commands.txt

# 管道输入
echo "显示时间\n显示系统信息" | python run.py --batch
```

**批量对象处理**：
```
> 停止所有名称包含"test"的进程
[AI翻译] Get-Process | Where-Object {$_.Name -like "*test*"} | Stop-Process
[安全检查] ⚠ 需要确认
[影响对象] 3个进程
是否继续？(y/n):
```

#### 2.2.3 模板和别名

支持自定义命令模板和别名，提高效率。

**定义模板**：
```yaml
# config/templates.yaml
templates:
  - name: "top_cpu"
    description: "显示CPU使用率最高的进程"
    command: "Get-Process | Sort-Object CPU -Descending | Select-Object -First {count}"
    parameters:
      - name: "count"
        type: "int"
        default: 5
```

**使用模板**：
```
> 使用模板 top_cpu count=10
[执行] Get-Process | Sort-Object CPU -Descending | Select-Object -First 10
```

**定义别名**：
```yaml
# config/user.yaml
aliases:
  时间: "Get-Date"
  进程: "Get-Process"
  文件: "Get-ChildItem"
```

#### 2.2.4 输出格式化

支持多种输出格式，满足不同需求。

**支持的格式**：
- **表格格式**（默认）：适合查看结构化数据
- **列表格式**：适合查看详细信息
- **JSON格式**：适合程序处理
- **CSV格式**：适合导出到Excel
- **自定义格式**：使用格式化字符串

**示例**：
```bash
# 表格格式
python run.py "显示进程" --format table

# JSON格式
python run.py "显示进程" --format json

# CSV格式
python run.py "显示进程" --format csv --output processes.csv

# 自定义格式
python run.py "显示进程" --format custom --template "{Name}: {CPU}%"
```

![输出格式示例](../07-项目资料/screenshots/output-formats.png)

#### 2.2.5 远程执行

支持在远程计算机上执行命令（需要配置PowerShell远程管理）。

**配置远程连接**：
```yaml
# config/user.yaml
remote:
  enabled: true
  hosts:
    - name: "server1"
      hostname: "192.168.1.100"
      username: "admin"
      auth_method: "password"  # 或 "key"
```

**远程执行**：
```bash
# 在指定主机执行
python run.py --remote server1 "显示系统信息"

# 在多个主机执行
python run.py --remote server1,server2,server3 "显示磁盘使用情况"
```

#### 2.2.6 定时任务

支持创建定时执行的任务。

**创建定时任务**：
```bash
# 每天早上8点执行
python run.py --schedule "0 8 * * *" "备份重要文件" --save-task backup_daily

# 每小时执行
python run.py --schedule "0 * * * *" "检查系统状态" --save-task health_check

# 查看定时任务
python run.py --list-tasks

# 删除定时任务
python run.py --delete-task backup_daily
```

---

### 2.3 配置选项

#### 2.3.1 AI引擎配置

```yaml
ai:
  # AI提供商：local, ollama, openai
  provider: "local"
  
  # 模型配置
  model:
    name: "llama2"
    temperature: 0.7      # 生成随机性 (0.0-2.0)
    max_tokens: 256       # 最大生成长度
    top_p: 0.9           # 核采样参数
  
  # 翻译策略
  translation:
    use_rules_first: true      # 优先使用规则匹配
    enable_cache: true         # 启用缓存
    cache_ttl: 3600           # 缓存过期时间（秒）
    max_cache_size: 1000      # 最大缓存条目
  
  # 错误检测
  error_detection:
    enabled: true
    check_syntax: true
    check_command_exists: true
```

#### 2.3.2 安全引擎配置

```yaml
security:
  # 安全级别：strict, normal, permissive
  level: "normal"
  
  # 命令白名单
  whitelist:
    enabled: true
    dangerous_patterns_file: "config/dangerous_patterns.yaml"
    custom_patterns: []
  
  # 权限检查
  permission_check:
    enabled: true
    require_confirmation_for_admin: true
    require_confirmation_for_high_risk: true
  
  # 沙箱执行
  sandbox:
    enabled: false           # 默认关闭，性能开销较大
    provider: "docker"
    image: "powershell:latest"
    memory_limit: "512m"
    cpu_quota: 50000
    network_disabled: true
    timeout: 30
```

#### 2.3.3 执行引擎配置

```yaml
execution:
  # 默认超时时间（秒）
  default_timeout: 30
  
  # 最大超时时间（秒）
  max_timeout: 300
  
  # 输出编码
  output_encoding: "utf-8"
  
  # 平台特定配置
  platform:
    windows:
      shell: "pwsh"          # 或 "powershell"
      encoding: "utf-8"
    linux:
      shell: "pwsh"
      encoding: "utf-8"
    macos:
      shell: "pwsh"
      encoding: "utf-8"
```

#### 2.3.4 日志配置

```yaml
logging:
  # 日志级别：DEBUG, INFO, WARNING, ERROR, CRITICAL
  level: "INFO"
  
  # 日志格式
  format: "json"             # 或 "text"
  
  # 日志输出
  handlers:
    - type: "file"
      filename: "logs/app.log"
      max_bytes: 10485760    # 10MB
      backup_count: 5
    - type: "console"
      level: "INFO"
  
  # 敏感信息过滤
  filter_sensitive: true
  sensitive_patterns:
    - "password"
    - "token"
    - "secret"
```

#### 2.3.5 存储配置

```yaml
storage:
  # 存储后端：file, sqlite, redis
  backend: "file"
  
  # 文件存储配置
  file:
    base_path: "data"
    history_file: "history.json"
    cache_file: "cache.json"
  
  # 历史记录配置
  history:
    enabled: true
    max_entries: 1000
    retention_days: 30
```

---

### 2.4 使用技巧

#### 2.4.1 提高翻译准确性

**技巧1：使用明确的描述**
```
❌ 不好：显示东西
✓ 好：显示当前目录的所有文件

❌ 不好：查看信息
✓ 好：查看系统内存使用情况
```

**技巧2：包含具体参数**
```
❌ 不好：显示进程
✓ 好：显示CPU使用率最高的5个进程

❌ 不好：查找文件
✓ 好：查找当前目录下所有大于100MB的文件
```

**技巧3：使用标准术语**
```
✓ 进程、服务、文件、目录
✓ CPU、内存、磁盘、网络
✓ 启动、停止、重启、删除
```

#### 2.4.2 提高执行效率

**技巧1：使用缓存**
- 常用命令会被自动缓存
- 相同的输入直接返回缓存结果
- 缓存命中率可达60%以上

**技巧2：使用规则匹配**
- 简单命令优先使用规则匹配
- 规则匹配速度比AI生成快100倍
- 可自定义规则扩展

**技巧3：批量操作**
```bash
# 一次执行多个命令
python run.py --script commands.txt

# 使用管道
cat commands.txt | python run.py --batch
```

#### 2.4.3 安全使用建议

**建议1：启用安全检查**
```yaml
security:
  level: "normal"          # 推荐使用normal级别
  whitelist:
    enabled: true          # 始终启用白名单
```

**建议2：谨慎确认高危命令**
- 仔细阅读命令内容
- 理解命令的影响范围
- 不确定时选择拒绝

**建议3：使用沙箱测试**
```yaml
security:
  sandbox:
    enabled: true          # 测试未知命令时启用
```

**建议4：定期检查历史**
```bash
# 查看历史记录
python run.py --history

# 导出历史用于审计
python run.py --export-history audit.json
```

#### 2.4.4 性能优化技巧

**技巧1：调整缓存大小**
```yaml
ai:
  translation:
    max_cache_size: 2000   # 增加缓存大小
    cache_ttl: 7200        # 延长缓存时间
```

**技巧2：使用规则优先**
```yaml
ai:
  translation:
    use_rules_first: true  # 优先使用规则匹配
```

**技巧3：限制输出大小**
```bash
# 限制输出行数
python run.py "显示进程" --limit 10

# 只显示关键字段
python run.py "显示进程" --select "Name,CPU,Memory"
```

**技巧4：异步执行长时间命令**
```bash
# 后台执行
python run.py "备份大文件" --async

# 查看后台任务
python run.py --list-jobs

# 获取任务结果
python run.py --get-job-result <job_id>
```

![使用技巧示例](../07-项目资料/screenshots/usage-tips.png)

---


## 3. 使用场景

### 3.1 系统管理

#### 3.1.1 进程管理

**场景1：查看系统进程**
```
> 显示所有正在运行的进程
[命令] Get-Process

> 显示CPU使用率最高的10个进程
[命令] Get-Process | Sort-Object CPU -Descending | Select-Object -First 10 Name, CPU, WorkingSet

> 显示内存占用最多的进程
[命令] Get-Process | Sort-Object WorkingSet -Descending | Select-Object -First 1
```

**场景2：进程监控**
```
> 查找名为chrome的进程
[命令] Get-Process -Name chrome

> 显示chrome进程的详细信息
[命令] Get-Process -Name chrome | Format-List *

> 统计chrome进程的数量
[命令] (Get-Process -Name chrome).Count
```

**场景3：进程控制**
```
> 停止名为notepad的进程
[命令] Stop-Process -Name notepad
[安全检查] ⚠ 需要确认
是否继续？(y/n): y

> 强制停止无响应的进程
[命令] Stop-Process -Id 1234 -Force
[安全检查] ⚠ 高风险操作
```

#### 3.1.2 服务管理

**场景1：查看服务状态**
```
> 显示所有Windows服务
[命令] Get-Service

> 显示正在运行的服务
[命令] Get-Service | Where-Object {$_.Status -eq 'Running'}

> 查找名称包含"Windows Update"的服务
[命令] Get-Service | Where-Object {$_.DisplayName -like "*Windows Update*"}
```

**场景2：服务控制**
```
> 启动Windows Update服务
[命令] Start-Service -Name wuauserv
[安全检查] ⚠ 需要管理员权限

> 停止Print Spooler服务
[命令] Stop-Service -Name Spooler
[安全检查] ⚠ 需要管理员权限

> 重启某个服务
[命令] Restart-Service -Name ServiceName
```

#### 3.1.3 系统信息查询

**场景1：硬件信息**
```
> 显示计算机名称
[命令] $env:COMPUTERNAME

> 显示CPU信息
[命令] Get-WmiObject Win32_Processor | Select-Object Name, NumberOfCores, MaxClockSpeed

> 显示内存信息
[命令] Get-WmiObject Win32_PhysicalMemory | Measure-Object Capacity -Sum | Select-Object @{Name="TotalMemory(GB)";Expression={$_.Sum/1GB}}

> 显示磁盘信息
[命令] Get-WmiObject Win32_LogicalDisk | Select-Object DeviceID, @{Name="Size(GB)";Expression={[math]::Round($_.Size/1GB,2)}}, @{Name="FreeSpace(GB)";Expression={[math]::Round($_.FreeSpace/1GB,2)}}
```

**场景2：系统状态**
```
> 显示系统运行时间
[命令] (Get-Date) - (Get-CimInstance Win32_OperatingSystem).LastBootUpTime

> 显示当前登录用户
[命令] $env:USERNAME

> 显示系统版本
[命令] Get-ComputerInfo | Select-Object OsName, OsVersion, OsBuildNumber

> 显示环境变量
[命令] Get-ChildItem Env:
```

#### 3.1.4 性能监控

**场景1：实时监控**
```
> 显示CPU使用率
[命令] Get-Counter '\Processor(_Total)\% Processor Time'

> 显示内存使用率
[命令] Get-Counter '\Memory\% Committed Bytes In Use'

> 显示磁盘活动
[命令] Get-Counter '\PhysicalDisk(_Total)\Disk Reads/sec', '\PhysicalDisk(_Total)\Disk Writes/sec'
```

**场景2：性能分析**
```
> 显示最近1小时的CPU使用情况
[命令] Get-Counter '\Processor(_Total)\% Processor Time' -SampleInterval 60 -MaxSamples 60

> 导出性能数据到CSV
[命令] Get-Counter '\Processor(_Total)\% Processor Time' -MaxSamples 100 | Export-Counter -Path cpu_usage.csv
```

![系统管理场景](../07-项目资料/screenshots/system-management.png)

---

### 3.2 文件操作

#### 3.2.1 文件浏览

**场景1：列出文件**
```
> 列出当前目录的所有文件
[命令] Get-ChildItem

> 列出所有txt文件
[命令] Get-ChildItem -Filter "*.txt"

> 递归列出所有文件
[命令] Get-ChildItem -Recurse

> 只显示文件夹
[命令] Get-ChildItem -Directory

> 只显示文件
[命令] Get-ChildItem -File
```

**场景2：文件搜索**
```
> 查找名称包含"report"的文件
[命令] Get-ChildItem -Recurse -Filter "*report*"

> 查找大于100MB的文件
[命令] Get-ChildItem -Recurse | Where-Object {$_.Length -gt 100MB}

> 查找最近7天修改的文件
[命令] Get-ChildItem -Recurse | Where-Object {$_.LastWriteTime -gt (Get-Date).AddDays(-7)}

> 查找空文件
[命令] Get-ChildItem -Recurse -File | Where-Object {$_.Length -eq 0}
```

#### 3.2.2 文件操作

**场景1：创建和删除**
```
> 创建一个新文件
[命令] New-Item -Path "test.txt" -ItemType File

> 创建一个新文件夹
[命令] New-Item -Path "backup" -ItemType Directory

> 删除一个文件
[命令] Remove-Item "test.txt"
[安全检查] ⚠ 需要确认

> 删除一个空文件夹
[命令] Remove-Item "backup"
```

**场景2：复制和移动**
```
> 复制文件到另一个位置
[命令] Copy-Item "source.txt" -Destination "D:\backup\source.txt"

> 复制整个文件夹
[命令] Copy-Item "C:\data" -Destination "D:\backup\data" -Recurse

> 移动文件
[命令] Move-Item "old_location.txt" -Destination "new_location.txt"

> 重命名文件
[命令] Rename-Item "old_name.txt" -NewName "new_name.txt"
```

**场景3：文件内容操作**
```
> 显示文件内容
[命令] Get-Content "file.txt"

> 显示文件的前10行
[命令] Get-Content "file.txt" -TotalCount 10

> 显示文件的最后10行
[命令] Get-Content "file.txt" -Tail 10

> 在文件中搜索文本
[命令] Select-String -Path "file.txt" -Pattern "error"

> 统计文件行数
[命令] (Get-Content "file.txt").Count
```

#### 3.2.3 批量文件处理

**场景1：批量重命名**
```
> 将所有txt文件改为大写扩展名
[命令] Get-ChildItem -Filter "*.txt" | Rename-Item -NewName {$_.Name.Replace('.txt','.TXT')}

> 给所有文件添加前缀
[命令] Get-ChildItem | Rename-Item -NewName {"backup_" + $_.Name}

> 批量修改文件扩展名
[命令] Get-ChildItem -Filter "*.log" | Rename-Item -NewName {$_.Name -replace '.log','.txt'}
```

**场景2：批量处理**
```
> 压缩所有日志文件
[命令] Get-ChildItem -Filter "*.log" | Compress-Archive -DestinationPath "logs_backup.zip"

> 删除所有临时文件
[命令] Get-ChildItem -Filter "*.tmp" -Recurse | Remove-Item
[安全检查] ⚠ 批量删除操作

> 统计各类型文件的数量
[命令] Get-ChildItem -Recurse | Group-Object Extension | Select-Object Name, Count
```

#### 3.2.4 文件权限管理

**场景1：查看权限**
```
> 显示文件的访问控制列表
[命令] Get-Acl "file.txt" | Format-List

> 显示文件所有者
[命令] (Get-Acl "file.txt").Owner
```

**场景2：修改权限**
```
> 修改文件所有者
[命令] $acl = Get-Acl "file.txt"; $acl.SetOwner([System.Security.Principal.NTAccount]"Username"); Set-Acl "file.txt" $acl
[安全检查] ⚠ 需要管理员权限
```

![文件操作场景](../07-项目资料/screenshots/file-operations.png)

---

### 3.3 网络诊断

#### 3.3.1 网络连接测试

**场景1：连通性测试**
```
> 测试与百度的连接
[命令] Test-Connection baidu.com -Count 4

> 测试与多个主机的连接
[命令] Test-Connection baidu.com, google.com, github.com

> 快速测试连接（只发送1个包）
[命令] Test-Connection baidu.com -Count 1 -Quiet

> 测试指定端口是否开放
[命令] Test-NetConnection baidu.com -Port 80
```

**场景2：网络延迟测试**
```
> 测试网络延迟
[命令] Test-Connection baidu.com -Count 10 | Measure-Object ResponseTime -Average

> 持续监控网络延迟
[命令] while($true) { Test-Connection baidu.com -Count 1; Start-Sleep 1 }
```

#### 3.3.2 网络配置查询

**场景1：IP地址信息**
```
> 显示本机IP地址
[命令] Get-NetIPAddress | Where-Object {$_.AddressFamily -eq 'IPv4' -and $_.IPAddress -ne '127.0.0.1'}

> 显示所有网络适配器
[命令] Get-NetAdapter

> 显示网络适配器详细信息
[命令] Get-NetAdapter | Format-List *

> 显示DNS服务器配置
[命令] Get-DnsClientServerAddress
```

**场景2：路由信息**
```
> 显示路由表
[命令] Get-NetRoute

> 显示默认网关
[命令] Get-NetRoute -DestinationPrefix "0.0.0.0/0"

> 追踪到目标主机的路由
[命令] Test-NetConnection baidu.com -TraceRoute
```

#### 3.3.3 网络连接状态

**场景1：活动连接**
```
> 显示所有网络连接
[命令] Get-NetTCPConnection

> 显示正在监听的端口
[命令] Get-NetTCPConnection -State Listen

> 显示已建立的连接
[命令] Get-NetTCPConnection -State Established

> 查找占用特定端口的进程
[命令] Get-NetTCPConnection -LocalPort 80 | Select-Object OwningProcess
```

**场景2：网络统计**
```
> 显示网络统计信息
[命令] Get-NetAdapterStatistics

> 显示网络接口流量
[命令] Get-NetAdapterStatistics | Select-Object Name, ReceivedBytes, SentBytes

> 监控网络流量
[命令] Get-Counter '\Network Interface(*)\Bytes Total/sec'
```

#### 3.3.4 DNS诊断

**场景1：DNS查询**
```
> 查询域名的IP地址
[命令] Resolve-DnsName baidu.com

> 查询域名的所有记录
[命令] Resolve-DnsName baidu.com -Type ALL

> 查询MX记录
[命令] Resolve-DnsName gmail.com -Type MX

> 使用指定DNS服务器查询
[命令] Resolve-DnsName baidu.com -Server 8.8.8.8
```

**场景2：DNS缓存管理**
```
> 显示DNS缓存
[命令] Get-DnsClientCache

> 清除DNS缓存
[命令] Clear-DnsClientCache
[安全检查] ⚠ 需要管理员权限

> 查看特定域名的缓存
[命令] Get-DnsClientCache -Name "baidu.com"
```

#### 3.3.5 防火墙管理

**场景1：防火墙规则查询**
```
> 显示所有防火墙规则
[命令] Get-NetFirewallRule

> 显示启用的防火墙规则
[命令] Get-NetFirewallRule -Enabled True

> 查找特定端口的防火墙规则
[命令] Get-NetFirewallPortFilter | Where-Object {$_.LocalPort -eq 80}
```

**场景2：防火墙状态**
```
> 显示防火墙配置文件状态
[命令] Get-NetFirewallProfile

> 显示防火墙是否启用
[命令] Get-NetFirewallProfile | Select-Object Name, Enabled
```

![网络诊断场景](../07-项目资料/screenshots/network-diagnostics.png)

---

### 3.4 开发辅助

#### 3.4.1 环境管理

**场景1：环境变量**
```
> 显示所有环境变量
[命令] Get-ChildItem Env:

> 显示PATH环境变量
[命令] $env:PATH

> 显示特定环境变量
[命令] $env:JAVA_HOME

> 临时设置环境变量
[命令] $env:MY_VAR = "value"
```

**场景2：开发工具检查**
```
> 检查Python是否安装
[命令] python --version

> 检查Node.js版本
[命令] node --version

> 检查Git版本
[命令] git --version

> 查找可执行文件位置
[命令] Get-Command python | Select-Object Source
```

#### 3.4.2 代码管理

**场景1：Git操作**
```
> 显示Git状态
[命令] git status

> 显示Git日志
[命令] git log --oneline -10

> 显示当前分支
[命令] git branch --show-current

> 统计代码行数
[命令] git ls-files | Where-Object {$_ -match '\.(py|js|java)$'} | ForEach-Object {(Get-Content $_).Count} | Measure-Object -Sum
```

**场景2：项目分析**
```
> 统计各类型文件数量
[命令] Get-ChildItem -Recurse -File | Group-Object Extension | Sort-Object Count -Descending

> 查找最大的文件
[命令] Get-ChildItem -Recurse -File | Sort-Object Length -Descending | Select-Object -First 10 Name, @{Name="Size(MB)";Expression={[math]::Round($_.Length/1MB,2)}}

> 统计代码总行数
[命令] Get-ChildItem -Recurse -Include *.py,*.js,*.java | ForEach-Object {(Get-Content $_).Count} | Measure-Object -Sum
```

#### 3.4.3 日志分析

**场景1：日志查询**
```
> 查找包含"error"的日志
[命令] Select-String -Path "app.log" -Pattern "error" -CaseSensitive

> 统计错误数量
[命令] (Select-String -Path "app.log" -Pattern "error").Count

> 显示最近的错误日志
[命令] Select-String -Path "app.log" -Pattern "error" | Select-Object -Last 10

> 查找多个日志文件中的错误
[命令] Get-ChildItem -Filter "*.log" | Select-String -Pattern "error"
```

**场景2：日志统计**
```
> 统计各级别日志数量
[命令] Get-Content "app.log" | Group-Object {$_ -replace '.*\[(.*?)\].*','$1'} | Select-Object Name, Count

> 按时间段统计日志
[命令] Get-Content "app.log" | Where-Object {$_ -match '2025-11-11'} | Measure-Object -Line

> 提取特定时间段的日志
[命令] Get-Content "app.log" | Where-Object {$_ -match '2025-11-11 14:'} | Out-File "filtered.log"
```

#### 3.4.4 性能测试

**场景1：执行时间测量**
```
> 测量命令执行时间
[命令] Measure-Command {Get-Process}

> 比较不同方法的性能
[命令] Measure-Command {Get-ChildItem} ; Measure-Command {dir}

> 测试脚本性能
[命令] Measure-Command {& "script.ps1"}
```

**场景2：资源监控**
```
> 监控进程资源使用
[命令] Get-Process -Name python | Select-Object CPU, WorkingSet, Threads

> 持续监控资源使用
[命令] while($true) { Get-Process -Name python | Select-Object CPU, @{Name="Memory(MB)";Expression={$_.WorkingSet/1MB}}; Start-Sleep 1 }
```

#### 3.4.5 自动化任务

**场景1：批量处理**
```
> 批量转换文件编码
[命令] Get-ChildItem -Filter "*.txt" | ForEach-Object {$content = Get-Content $_ -Encoding UTF8; Set-Content $_ -Value $content -Encoding ASCII}

> 批量重命名文件
[命令] Get-ChildItem | ForEach-Object {Rename-Item $_ -NewName ($_.Name -replace 'old','new')}

> 批量压缩文件
[命令] Get-ChildItem -Directory | ForEach-Object {Compress-Archive -Path $_.FullName -DestinationPath "$($_.Name).zip"}
```

**场景2：定时任务**
```
> 创建定时任务
[命令] $action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-File backup.ps1"; $trigger = New-ScheduledTaskTrigger -Daily -At 2am; Register-ScheduledTask -TaskName "DailyBackup" -Action $action -Trigger $trigger
[安全检查] ⚠ 需要管理员权限

> 查看定时任务
[命令] Get-ScheduledTask | Where-Object {$_.State -eq 'Ready'}

> 运行定时任务
[命令] Start-ScheduledTask -TaskName "DailyBackup"
```

![开发辅助场景](../07-项目资料/screenshots/development-assistance.png)

---


## 4. 配置指南

### 4.1 配置文件结构

AI PowerShell智能助手使用YAML格式的配置文件，支持多层级配置和灵活的自定义选项。

#### 4.1.1 配置文件位置

```
config/
├── default.yaml          # 默认配置（不要修改）
├── templates.yaml        # 命令模板配置
├── ui.yaml              # UI配置
└── user.yaml            # 用户自定义配置（优先级最高）
```

**配置加载顺序**：
1. 加载 `default.yaml` 作为基础配置
2. 加载 `user.yaml` 覆盖默认配置
3. 命令行参数覆盖文件配置

#### 4.1.2 配置文件结构

```yaml
# config/user.yaml

# AI引擎配置
ai:
  provider: "local"
  model:
    name: "llama2"
    temperature: 0.7
  translation:
    use_rules_first: true
    enable_cache: true

# 安全引擎配置
security:
  level: "normal"
  whitelist:
    enabled: true
  sandbox:
    enabled: false

# 执行引擎配置
execution:
  default_timeout: 30
  output_encoding: "utf-8"

# 日志配置
logging:
  level: "INFO"
  format: "json"

# 存储配置
storage:
  backend: "file"
  history:
    max_entries: 1000

# UI配置
ui:
  theme: "default"
  show_confidence: true
  confirm_high_risk: true
```

---

### 4.2 配置参数详解

#### 4.2.1 AI引擎配置

**provider** - AI提供商
```yaml
ai:
  provider: "local"  # 可选值: local, ollama, openai
```
- `local`: 使用本地加载的AI模型（需要足够内存）
- `ollama`: 使用Ollama服务（推荐，性能更好）
- `openai`: 使用OpenAI API（需要API密钥）

**model** - 模型配置
```yaml
ai:
  model:
    name: "llama2"           # 模型名称
    temperature: 0.7         # 生成随机性 (0.0-2.0)
    max_tokens: 256          # 最大生成长度
    top_p: 0.9              # 核采样参数
    frequency_penalty: 0.0   # 频率惩罚
    presence_penalty: 0.0    # 存在惩罚
```

**参数说明**：
- `temperature`: 控制生成的随机性
  - 0.0: 确定性输出，总是选择最可能的词
  - 1.0: 平衡的随机性（推荐）
  - 2.0: 高度随机，可能产生不可预测的结果
- `max_tokens`: 限制生成的最大长度，避免过长输出
- `top_p`: 核采样，只考虑累积概率达到p的词

**translation** - 翻译策略配置
```yaml
ai:
  translation:
    use_rules_first: true        # 优先使用规则匹配
    enable_cache: true           # 启用缓存
    cache_ttl: 3600             # 缓存过期时间（秒）
    max_cache_size: 1000        # 最大缓存条目
    min_confidence: 0.7         # 最小置信度阈值
    retry_on_low_confidence: true  # 低置信度时重试
    max_retries: 2              # 最大重试次数
```

**error_detection** - 错误检测配置
```yaml
ai:
  error_detection:
    enabled: true                    # 启用错误检测
    check_syntax: true               # 检查语法
    check_command_exists: true       # 检查命令是否存在
    check_parameters: true           # 检查参数有效性
    suggest_corrections: true        # 建议修正
```

#### 4.2.2 安全引擎配置

**level** - 安全级别
```yaml
security:
  level: "normal"  # 可选值: strict, normal, permissive
```
- `strict`: 严格模式，拦截所有可能有风险的命令
- `normal`: 正常模式，平衡安全性和易用性（推荐）
- `permissive`: 宽松模式，只拦截明确的危险命令

**whitelist** - 命令白名单配置
```yaml
security:
  whitelist:
    enabled: true
    dangerous_patterns_file: "config/dangerous_patterns.yaml"
    custom_patterns:
      - pattern: "Remove-Item.*-Recurse.*C:\\\\"
        risk_level: "CRITICAL"
        description: "递归删除系统盘根目录"
      - pattern: "Format-Volume"
        risk_level: "CRITICAL"
        description: "格式化磁盘"
    safe_commands:
      - "Get-Date"
      - "Get-Process"
      - "Get-ChildItem"
```

**permission_check** - 权限检查配置
```yaml
security:
  permission_check:
    enabled: true
    require_confirmation_for_admin: true      # 管理员命令需要确认
    require_confirmation_for_high_risk: true  # 高风险命令需要确认
    admin_commands:
      - "Stop-Service"
      - "Start-Service"
      - "Restart-Computer"
      - "Stop-Computer"
```

**sandbox** - 沙箱配置
```yaml
security:
  sandbox:
    enabled: false                    # 默认关闭
    provider: "docker"                # 沙箱提供商
    image: "powershell:latest"        # Docker镜像
    memory_limit: "512m"              # 内存限制
    cpu_quota: 50000                  # CPU配额（50%）
    network_disabled: true            # 禁用网络
    timeout: 30                       # 超时时间（秒）
    auto_cleanup: true                # 自动清理容器
    volume_mounts: []                 # 挂载卷
```

#### 4.2.3 执行引擎配置

**timeout** - 超时配置
```yaml
execution:
  default_timeout: 30      # 默认超时（秒）
  max_timeout: 300         # 最大超时（秒）
  timeout_action: "kill"   # 超时动作: kill, interrupt
```

**encoding** - 编码配置
```yaml
execution:
  output_encoding: "utf-8"     # 输出编码
  input_encoding: "utf-8"      # 输入编码
  error_encoding: "utf-8"      # 错误编码
```

**platform** - 平台特定配置
```yaml
execution:
  platform:
    windows:
      shell: "pwsh"              # PowerShell可执行文件
      encoding: "utf-8"          # 编码
      use_chcp: true             # 使用chcp设置代码页
    linux:
      shell: "pwsh"
      encoding: "utf-8"
    macos:
      shell: "pwsh"
      encoding: "utf-8"
```

**output** - 输出配置
```yaml
execution:
  output:
    format: "table"              # 默认格式: table, list, json, csv
    max_lines: 1000              # 最大输出行数
    truncate_long_lines: true    # 截断长行
    max_line_length: 200         # 最大行长度
    colorize: true               # 彩色输出
```

#### 4.2.4 日志配置

**level** - 日志级别
```yaml
logging:
  level: "INFO"  # 可选值: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

**format** - 日志格式
```yaml
logging:
  format: "json"  # 可选值: json, text
  
  # JSON格式示例
  json_format:
    timestamp: true
    level: true
    message: true
    correlation_id: true
    extra_fields: true
  
  # 文本格式示例
  text_format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

**handlers** - 日志处理器
```yaml
logging:
  handlers:
    - type: "file"
      filename: "logs/app.log"
      max_bytes: 10485760        # 10MB
      backup_count: 5            # 保留5个备份
      level: "INFO"
    
    - type: "console"
      level: "INFO"
      colorize: true
    
    - type: "rotating"
      filename: "logs/app.log"
      when: "midnight"           # 每天午夜轮转
      interval: 1
      backup_count: 30
```

**filter** - 日志过滤
```yaml
logging:
  filter_sensitive: true
  sensitive_patterns:
    - "password"
    - "token"
    - "secret"
    - "api_key"
    - "access_key"
  replacement: "[REDACTED]"
```

#### 4.2.5 存储配置

**backend** - 存储后端
```yaml
storage:
  backend: "file"  # 可选值: file, sqlite, redis
```

**file** - 文件存储配置
```yaml
storage:
  file:
    base_path: "data"
    history_file: "history.json"
    cache_file: "cache.json"
    session_file: "sessions.json"
    create_backup: true
    backup_interval: 86400      # 24小时
```

**history** - 历史记录配置
```yaml
storage:
  history:
    enabled: true
    max_entries: 1000           # 最大条目数
    retention_days: 30          # 保留天数
    auto_cleanup: true          # 自动清理
    export_format: "json"       # 导出格式
```

**cache** - 缓存配置
```yaml
storage:
  cache:
    enabled: true
    max_size: 1000              # 最大缓存条目
    ttl: 3600                   # 默认TTL（秒）
    eviction_policy: "lru"      # 淘汰策略: lru, lfu, fifo
```

#### 4.2.6 UI配置

**theme** - 主题配置
```yaml
ui:
  theme: "default"              # 主题名称
  colors:
    success: "green"
    warning: "yellow"
    error: "red"
    info: "blue"
    prompt: "cyan"
```

**display** - 显示配置
```yaml
ui:
  display:
    show_confidence: true       # 显示置信度
    show_execution_time: true   # 显示执行时间
    show_command: true          # 显示生成的命令
    confirm_high_risk: true     # 高风险命令需要确认
    confirm_admin: true         # 管理员命令需要确认
    max_output_lines: 100       # 最大输出行数
```

**prompt** - 提示符配置
```yaml
ui:
  prompt:
    format: "> "
    show_session_id: false
    show_timestamp: false
    multiline: false
```

---

### 4.3 自定义规则

#### 4.3.1 添加翻译规则

创建或编辑 `config/custom_rules.yaml`：

```yaml
# 自定义翻译规则
translation_rules:
  # 规则1：简单替换
  - pattern: "^显示时间$"
    command: "Get-Date"
    confidence: 1.0
    description: "显示当前时间"
  
  # 规则2：带参数的规则
  - pattern: "^显示最近(\\d+)个进程$"
    command: "Get-Process | Select-Object -First {1}"
    confidence: 0.95
    description: "显示最近N个进程"
    parameters:
      - name: "count"
        type: "int"
        position: 1
  
  # 规则3：复杂规则
  - pattern: "^查找(.*?)文件$"
    command: "Get-ChildItem -Recurse -Filter '*{1}*'"
    confidence: 0.9
    description: "递归查找文件"
    parameters:
      - name: "filename"
        type: "string"
        position: 1
  
  # 规则4：条件规则
  - pattern: "^显示大于(\\d+)MB的文件$"
    command: "Get-ChildItem -Recurse | Where-Object {{$_.Length -gt {1}MB}}"
    confidence: 0.9
    description: "查找大文件"
    parameters:
      - name: "size"
        type: "int"
        position: 1
```

**规则优先级**：
1. 自定义规则优先级最高
2. 内置规则次之
3. AI生成优先级最低

#### 4.3.2 添加安全规则

创建或编辑 `config/custom_security.yaml`：

```yaml
# 自定义安全规则
security_rules:
  # 危险命令模式
  dangerous_patterns:
    - pattern: "Remove-Item.*-Recurse.*C:\\\\"
      risk_level: "CRITICAL"
      description: "递归删除系统盘"
      action: "block"
    
    - pattern: "Format-Volume.*-FileSystem"
      risk_level: "CRITICAL"
      description: "格式化磁盘"
      action: "block"
    
    - pattern: "Stop-Computer.*-Force"
      risk_level: "HIGH"
      description: "强制关机"
      action: "confirm"
    
    - pattern: "Restart-Computer"
      risk_level: "MEDIUM"
      description: "重启计算机"
      action: "confirm"
  
  # 安全命令白名单
  safe_commands:
    - "Get-Date"
    - "Get-Process"
    - "Get-ChildItem"
    - "Get-Content"
    - "Get-Service"
    - "Get-NetAdapter"
  
  # 需要管理员权限的命令
  admin_commands:
    - "Stop-Service"
    - "Start-Service"
    - "Restart-Service"
    - "Set-Service"
    - "New-Service"
    - "Remove-Service"
```

**风险等级说明**：
- `CRITICAL`: 极度危险，直接拒绝执行
- `HIGH`: 高度危险，需要特殊确认
- `MEDIUM`: 中等风险，需要用户确认
- `LOW`: 低风险，显示警告
- `SAFE`: 安全命令，直接执行

#### 4.3.3 添加命令模板

编辑 `config/templates.yaml`：

```yaml
# 命令模板
templates:
  # 模板1：进程监控
  - name: "monitor_process"
    description: "监控指定进程的资源使用"
    command: |
      while($true) {
        Get-Process -Name {process_name} | 
        Select-Object CPU, @{{Name="Memory(MB)";Expression={{$_.WorkingSet/1MB}}}}
        Start-Sleep {interval}
      }
    parameters:
      - name: "process_name"
        type: "string"
        required: true
        description: "进程名称"
      - name: "interval"
        type: "int"
        default: 1
        description: "监控间隔（秒）"
    category: "monitoring"
  
  # 模板2：文件备份
  - name: "backup_files"
    description: "备份指定目录的文件"
    command: |
      $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
      $backupPath = "{backup_dir}\backup_$timestamp"
      Copy-Item -Path "{source_dir}" -Destination $backupPath -Recurse
      Compress-Archive -Path $backupPath -DestinationPath "$backupPath.zip"
      Remove-Item -Path $backupPath -Recurse
    parameters:
      - name: "source_dir"
        type: "string"
        required: true
        description: "源目录"
      - name: "backup_dir"
        type: "string"
        required: true
        description: "备份目录"
    category: "backup"
  
  # 模板3：日志分析
  - name: "analyze_logs"
    description: "分析日志文件中的错误"
    command: |
      $errors = Select-String -Path "{log_file}" -Pattern "{pattern}"
      $errors | Group-Object Line | 
      Sort-Object Count -Descending | 
      Select-Object -First {top_n} Count, Name
    parameters:
      - name: "log_file"
        type: "string"
        required: true
        description: "日志文件路径"
      - name: "pattern"
        type: "string"
        default: "error"
        description: "搜索模式"
      - name: "top_n"
        type: "int"
        default: 10
        description: "显示前N个结果"
    category: "analysis"
```

**使用模板**：
```bash
# 使用模板
python run.py --template monitor_process process_name=chrome interval=2

# 列出所有模板
python run.py --list-templates

# 查看模板详情
python run.py --show-template monitor_process
```

---

### 4.4 性能调优

#### 4.4.1 翻译性能优化

**优化1：启用缓存**
```yaml
ai:
  translation:
    enable_cache: true
    cache_ttl: 7200              # 增加缓存时间
    max_cache_size: 2000         # 增加缓存大小
```

**优化2：优先使用规则**
```yaml
ai:
  translation:
    use_rules_first: true        # 优先规则匹配
    rule_timeout: 100            # 规则匹配超时（毫秒）
```

**优化3：调整AI参数**
```yaml
ai:
  model:
    temperature: 0.5             # 降低随机性，提高一致性
    max_tokens: 128              # 减少生成长度
```

**预期效果**：
- 缓存命中时响应时间 < 1ms
- 规则匹配响应时间 < 10ms
- AI生成响应时间 < 2s

#### 4.4.2 执行性能优化

**优化1：调整超时**
```yaml
execution:
  default_timeout: 15            # 减少默认超时
  max_timeout: 60                # 限制最大超时
```

**优化2：限制输出**
```yaml
execution:
  output:
    max_lines: 500               # 限制输出行数
    truncate_long_lines: true    # 截断长行
    max_line_length: 150         # 限制行长度
```

**优化3：禁用不必要的功能**
```yaml
execution:
  output:
    colorize: false              # 禁用彩色输出
logging:
  level: "WARNING"               # 减少日志输出
```

#### 4.4.3 内存优化

**优化1：限制历史记录**
```yaml
storage:
  history:
    max_entries: 500             # 减少历史条目
    auto_cleanup: true           # 启用自动清理
```

**优化2：限制缓存**
```yaml
storage:
  cache:
    max_size: 500                # 减少缓存大小
    eviction_policy: "lru"       # 使用LRU淘汰
```

**优化3：使用轻量级日志**
```yaml
logging:
  format: "text"                 # 使用文本格式
  handlers:
    - type: "console"            # 只输出到控制台
      level: "WARNING"
```

#### 4.4.4 网络优化

**优化1：使用本地AI**
```yaml
ai:
  provider: "local"              # 使用本地模型
  # 或使用本地Ollama服务
  provider: "ollama"
  ollama:
    base_url: "http://localhost:11434"
```

**优化2：禁用远程功能**
```yaml
remote:
  enabled: false                 # 禁用远程执行
```

#### 4.4.5 性能监控

**启用性能监控**：
```yaml
monitoring:
  enabled: true
  metrics:
    - "translation_time"
    - "execution_time"
    - "cache_hit_rate"
    - "memory_usage"
  export:
    enabled: true
    format: "json"
    file: "logs/metrics.json"
    interval: 60                 # 每60秒导出一次
```

**查看性能指标**：
```bash
# 查看实时性能
python run.py --show-metrics

# 导出性能报告
python run.py --export-metrics report.json
```

**性能基准**：
| 指标 | 目标值 | 优化后 |
|------|--------|--------|
| 缓存命中响应时间 | < 1ms | 0.5ms |
| 规则匹配响应时间 | < 10ms | 5ms |
| AI生成响应时间 | < 2s | 1.5s |
| 缓存命中率 | > 60% | 65% |
| 内存占用 | < 512MB | 380MB |

![性能调优效果](../07-项目资料/screenshots/performance-tuning.png)

---


## 5. 故障排除

### 5.1 常见问题

#### 5.1.1 安装问题

**问题1：Python版本不兼容**
```
错误信息: SyntaxError: invalid syntax
```
**原因**: Python版本低于3.8  
**解决方案**:
```bash
# 检查Python版本
python --version

# 升级Python到3.8或更高版本
# Windows: 从python.org下载安装
# Linux: sudo apt install python3.11
# macOS: brew install python@3.11
```

**问题2：依赖安装失败**
```
错误信息: ERROR: Could not find a version that satisfies the requirement
```
**原因**: pip版本过旧或网络问题  
**解决方案**:
```bash
# 升级pip
python -m pip install --upgrade pip

# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或使用阿里云镜像
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

**问题3：PowerShell未安装**
```
错误信息: 'pwsh' is not recognized as an internal or external command
```
**原因**: PowerShell Core未安装  
**解决方案**:
```bash
# Windows
winget install Microsoft.PowerShell

# Linux
wget https://packages.microsoft.com/config/ubuntu/20.04/packages-microsoft-prod.deb
sudo dpkg -i packages-microsoft-prod.deb
sudo apt update
sudo apt install powershell

# macOS
brew install --cask powershell
```

#### 5.1.2 运行问题

**问题1：中文乱码**
```
错误现象: 输出显示为乱码或问号
```
**原因**: 编码设置不正确  
**解决方案**:
```yaml
# 修改 config/user.yaml
execution:
  output_encoding: "utf-8"
  platform:
    windows:
      use_chcp: true    # 启用代码页设置
```

或在PowerShell中手动设置：
```powershell
chcp 65001
```

**问题2：命令执行超时**
```
错误信息: Command execution timeout after 30 seconds
```
**原因**: 命令执行时间过长  
**解决方案**:
```yaml
# 增加超时时间
execution:
  default_timeout: 60
  max_timeout: 300
```

或使用命令行参数：
```bash
python run.py "长时间命令" --timeout 120
```

**问题3：AI模型加载失败**
```
错误信息: Failed to load AI model
```
**原因**: 内存不足或模型文件损坏  
**解决方案**:
1. 检查可用内存（至少需要4GB）
2. 重新下载模型文件
3. 使用较小的模型
```yaml
ai:
  model:
    name: "llama2-7b"    # 使用较小的模型
```

**问题4：权限不足**
```
错误信息: Access denied / Permission denied
```
**原因**: 当前用户权限不足  
**解决方案**:
```bash
# Windows: 以管理员身份运行
# 右键点击 PowerShell -> 以管理员身份运行

# Linux/macOS: 使用sudo
sudo python run.py "需要管理员权限的命令"
```

#### 5.1.3 翻译问题

**问题1：翻译不准确**
```
输入: 显示进程
输出: Get-Service  # 错误，应该是 Get-Process
```
**原因**: AI模型理解错误或规则匹配失败  
**解决方案**:
1. 使用更明确的描述
```
改进: 显示所有正在运行的进程
```

2. 添加自定义规则
```yaml
# config/custom_rules.yaml
translation_rules:
  - pattern: "^显示进程$"
    command: "Get-Process"
    confidence: 1.0
```

3. 提高置信度阈值
```yaml
ai:
  translation:
    min_confidence: 0.8    # 提高到0.8
```

**问题2：翻译速度慢**
```
现象: 每次翻译需要3-5秒
```
**原因**: AI模型推理慢或缓存未启用  
**解决方案**:
1. 启用缓存
```yaml
ai:
  translation:
    enable_cache: true
    cache_ttl: 7200
```

2. 优先使用规则匹配
```yaml
ai:
  translation:
    use_rules_first: true
```

3. 使用Ollama服务
```yaml
ai:
  provider: "ollama"
  ollama:
    base_url: "http://localhost:11434"
```

**问题3：缓存失效**
```
现象: 相同输入每次都重新翻译
```
**原因**: 缓存配置错误或已过期  
**解决方案**:
```yaml
storage:
  cache:
    enabled: true
    max_size: 1000
    ttl: 3600
```

清除并重建缓存：
```bash
python run.py --clear-cache
```

#### 5.1.4 安全问题

**问题1：安全命令被拦截**
```
错误信息: Command blocked by security check
```
**原因**: 安全级别设置过严格  
**解决方案**:
1. 调整安全级别
```yaml
security:
  level: "normal"    # 从strict改为normal
```

2. 添加到安全白名单
```yaml
security:
  whitelist:
    safe_commands:
      - "Your-Command"
```

**问题2：危险命令未被拦截**
```
现象: 危险命令可以直接执行
```
**原因**: 安全检查被禁用或规则不完整  
**解决方案**:
1. 启用安全检查
```yaml
security:
  whitelist:
    enabled: true
  permission_check:
    enabled: true
```

2. 更新危险命令模式
```yaml
security:
  whitelist:
    custom_patterns:
      - pattern: "Your-Dangerous-Pattern"
        risk_level: "HIGH"
```

**问题3：沙箱执行失败**
```
错误信息: Docker container failed to start
```
**原因**: Docker未安装或未启动  
**解决方案**:
1. 安装Docker
```bash
# Windows/macOS: 下载Docker Desktop
# Linux: sudo apt install docker.io
```

2. 启动Docker服务
```bash
# Linux
sudo systemctl start docker

# Windows/macOS: 启动Docker Desktop
```

3. 或禁用沙箱
```yaml
security:
  sandbox:
    enabled: false
```

#### 5.1.5 历史记录问题

**问题1：历史记录丢失**
```
现象: 之前的命令历史不见了
```
**原因**: 历史文件被删除或损坏  
**解决方案**:
1. 检查历史文件
```bash
# 查看历史文件位置
cat config/user.yaml | grep history_file

# 检查文件是否存在
ls -la data/history.json
```

2. 从备份恢复
```bash
cp data/.backups/history_backup.json data/history.json
```

**问题2：历史记录过多**
```
现象: 系统变慢，历史文件很大
```
**原因**: 历史记录未清理  
**解决方案**:
1. 清理旧记录
```bash
python run.py --clear-history --before "2025-10-01"
```

2. 限制历史条目
```yaml
storage:
  history:
    max_entries: 500
    retention_days: 30
    auto_cleanup: true
```

---

### 5.2 错误代码

#### 5.2.1 系统错误代码

| 错误代码 | 说明 | 解决方案 |
|---------|------|----------|
| E001 | 配置文件加载失败 | 检查配置文件语法，确保YAML格式正确 |
| E002 | AI模型加载失败 | 检查模型文件是否存在，内存是否充足 |
| E003 | 存储引擎初始化失败 | 检查数据目录权限，确保可写 |
| E004 | 日志引擎初始化失败 | 检查日志目录权限 |
| E005 | 安全引擎初始化失败 | 检查安全配置文件 |

#### 5.2.2 翻译错误代码

| 错误代码 | 说明 | 解决方案 |
|---------|------|----------|
| T001 | 翻译超时 | 增加超时时间或使用更快的AI服务 |
| T002 | 置信度过低 | 使用更明确的描述或添加自定义规则 |
| T003 | AI服务不可用 | 检查AI服务状态，确保网络连接 |
| T004 | 规则匹配失败 | 添加自定义规则或使用AI翻译 |
| T005 | 缓存读取失败 | 清除缓存并重试 |

#### 5.2.3 执行错误代码

| 错误代码 | 说明 | 解决方案 |
|---------|------|----------|
| X001 | 命令执行超时 | 增加超时时间或优化命令 |
| X002 | 命令语法错误 | 检查生成的命令语法 |
| X003 | 权限不足 | 使用管理员权限运行 |
| X004 | 命令不存在 | 检查PowerShell版本和模块 |
| X005 | 输出编码错误 | 调整编码设置 |

#### 5.2.4 安全错误代码

| 错误代码 | 说明 | 解决方案 |
|---------|------|----------|
| S001 | 危险命令被拦截 | 确认命令安全性后调整安全级别 |
| S002 | 权限检查失败 | 使用管理员权限或调整权限配置 |
| S003 | 沙箱执行失败 | 检查Docker状态或禁用沙箱 |
| S004 | 安全规则加载失败 | 检查安全规则文件语法 |
| S005 | 风险评估失败 | 检查安全引擎配置 |

---

### 5.3 调试技巧

#### 5.3.1 启用调试模式

**方法1：命令行参数**
```bash
python run.py --debug "显示进程"
```

**方法2：配置文件**
```yaml
logging:
  level: "DEBUG"
```

**调试输出示例**：
```
[DEBUG] Loading configuration from config/user.yaml
[DEBUG] Initializing AI engine with provider: local
[DEBUG] Loading AI model: llama2
[DEBUG] AI model loaded successfully
[DEBUG] User input: 显示进程
[DEBUG] Checking cache for input hash: abc123...
[DEBUG] Cache miss, proceeding with translation
[DEBUG] Trying rule matching...
[DEBUG] Rule matched: pattern="^显示进程$"
[DEBUG] Generated command: Get-Process
[DEBUG] Confidence score: 0.95
[DEBUG] Running security check...
[DEBUG] Security check passed: SAFE
[DEBUG] Executing command: Get-Process
[DEBUG] Command completed in 0.5s
```

#### 5.3.2 查看详细日志

**查看实时日志**：
```bash
# Linux/macOS
tail -f logs/app.log

# Windows
Get-Content logs/app.log -Wait -Tail 50
```

**搜索特定错误**：
```bash
# 查找错误日志
grep "ERROR" logs/app.log

# 查找特定时间段的日志
grep "2025-11-11 14:" logs/app.log

# 统计错误数量
grep -c "ERROR" logs/app.log
```

**分析JSON日志**：
```bash
# 使用jq解析JSON日志
cat logs/app.log | jq 'select(.level=="ERROR")'

# 统计各级别日志数量
cat logs/app.log | jq -r '.level' | sort | uniq -c
```

#### 5.3.3 性能分析

**启用性能分析**：
```bash
python run.py --profile "显示进程"
```

**输出示例**：
```
Performance Profile:
  Total time: 1.523s
  - Configuration loading: 0.023s
  - AI model initialization: 0.500s
  - Translation: 0.850s
    - Cache lookup: 0.001s
    - Rule matching: 0.005s
    - AI generation: 0.844s
  - Security check: 0.050s
  - Command execution: 0.100s
```

**查看性能指标**：
```bash
python run.py --show-metrics
```

**导出性能报告**：
```bash
python run.py --export-metrics performance_report.json
```

#### 5.3.4 测试特定功能

**测试翻译功能**：
```bash
# 只翻译不执行
python run.py --translate-only "显示进程"

# 测试多个输入
python run.py --test-translation test_cases.txt
```

**测试安全检查**：
```bash
# 测试安全规则
python run.py --test-security "Remove-Item -Recurse C:\\"

# 显示风险评估详情
python run.py --security-details "Stop-Computer"
```

**测试缓存**：
```bash
# 清除缓存
python run.py --clear-cache

# 查看缓存统计
python run.py --cache-stats

# 预热缓存
python run.py --warm-cache common_commands.txt
```

#### 5.3.5 问题诊断工具

**系统诊断**：
```bash
# 运行完整诊断
python run.py --diagnose

# 输出示例
System Diagnostics:
✓ Python version: 3.11.0
✓ PowerShell version: 7.3.0
✓ Configuration: Valid
✓ AI model: Loaded
✓ Storage: Accessible
✓ Logging: Configured
⚠ Docker: Not running (sandbox disabled)
```

**连接测试**：
```bash
# 测试AI服务连接
python run.py --test-ai-connection

# 测试远程主机连接
python run.py --test-remote-connection server1
```

**配置验证**：
```bash
# 验证配置文件
python run.py --validate-config

# 显示当前配置
python run.py --show-config

# 比较配置差异
python run.py --diff-config default.yaml user.yaml
```

---

### 5.4 获取帮助

#### 5.4.1 内置帮助

**查看帮助信息**：
```bash
# 显示主帮助
python run.py --help

# 显示特定命令帮助
python run.py translate --help

# 显示配置帮助
python run.py config --help
```

**交互模式帮助**：
```
> help
Available commands:
  help              - Show this help message
  history           - View command history
  clear             - Clear screen
  config            - Show current configuration
  reload            - Reload configuration
  exit/quit         - Exit the program

Special commands:
  !N                - Re-execute command N from history
  !!                - Re-execute last command
```

#### 5.4.2 文档资源

**在线文档**：
- 用户手册: `docs/user-guide.md`
- API参考: `docs/api-reference.md`
- 开发指南: `docs/developer-guide.md`
- 配置参考: `docs/config-reference.md`

**示例代码**：
```bash
# 查看示例
ls examples/

# 运行示例
python examples/basic_usage.py
python examples/advanced_features.py
```

#### 5.4.3 社区支持

**GitHub Issues**：
- 报告Bug: https://github.com/yourusername/AI-PowerShell/issues/new?template=bug_report.md
- 功能请求: https://github.com/yourusername/AI-PowerShell/issues/new?template=feature_request.md
- 讨论: https://github.com/yourusername/AI-PowerShell/discussions

**提交Bug报告时请包含**：
1. 系统信息（操作系统、Python版本、PowerShell版本）
2. 错误信息和日志
3. 重现步骤
4. 配置文件（删除敏感信息）

**Bug报告模板**：
```markdown
## 环境信息
- OS: Windows 11
- Python: 3.11.0
- PowerShell: 7.3.0
- AI PowerShell版本: 1.0.0

## 问题描述
简要描述问题...

## 重现步骤
1. 运行命令 `python run.py "显示进程"`
2. 观察到错误...

## 预期行为
应该显示进程列表

## 实际行为
显示错误信息: ...

## 错误日志
```
[粘贴相关日志]
```

## 配置文件
```yaml
[粘贴相关配置]
```
```

#### 5.4.4 联系方式

**技术支持**：
- Email: support@example.com
- 微信群: [扫描二维码加入]
- QQ群: 123456789

**贡献代码**：
- Fork项目: https://github.com/yourusername/AI-PowerShell
- 提交PR: https://github.com/yourusername/AI-PowerShell/pulls
- 贡献指南: `CONTRIBUTING.md`

![获取帮助](../07-项目资料/screenshots/getting-help.png)

---


## 6. 附录

### 6.1 命令参考表

#### 6.1.1 命令行参数

| 参数 | 简写 | 说明 | 示例 |
|------|------|------|------|
| `--help` | `-h` | 显示帮助信息 | `python run.py --help` |
| `--version` | `-v` | 显示版本信息 | `python run.py --version` |
| `--config` | `-c` | 指定配置文件 | `python run.py -c custom.yaml` |
| `--debug` | `-d` | 启用调试模式 | `python run.py --debug` |
| `--history` | | 查看命令历史 | `python run.py --history` |
| `--clear-history` | | 清除历史记录 | `python run.py --clear-history` |
| `--export-history` | | 导出历史记录 | `python run.py --export-history out.json` |
| `--translate-only` | `-t` | 只翻译不执行 | `python run.py -t "显示进程"` |
| `--timeout` | | 设置超时时间 | `python run.py --timeout 60 "命令"` |
| `--format` | `-f` | 指定输出格式 | `python run.py -f json "命令"` |
| `--output` | `-o` | 输出到文件 | `python run.py -o result.txt "命令"` |
| `--remote` | `-r` | 远程执行 | `python run.py -r server1 "命令"` |
| `--sandbox` | | 在沙箱中执行 | `python run.py --sandbox "命令"` |
| `--template` | | 使用模板 | `python run.py --template name` |
| `--list-templates` | | 列出所有模板 | `python run.py --list-templates` |
| `--show-metrics` | | 显示性能指标 | `python run.py --show-metrics` |
| `--diagnose` | | 运行系统诊断 | `python run.py --diagnose` |
| `--validate-config` | | 验证配置文件 | `python run.py --validate-config` |

#### 6.1.2 交互模式命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `help` | 显示帮助信息 | `help` |
| `history` | 查看命令历史 | `history` |
| `history N` | 查看最近N条历史 | `history 10` |
| `!N` | 重新执行第N条命令 | `!5` |
| `!!` | 重新执行上一条命令 | `!!` |
| `clear` | 清屏 | `clear` |
| `config` | 查看当前配置 | `config` |
| `reload` | 重新加载配置 | `reload` |
| `exit` / `quit` | 退出程序 | `exit` |
| `metrics` | 显示性能指标 | `metrics` |
| `cache` | 查看缓存统计 | `cache` |

#### 6.1.3 常用PowerShell命令映射

| 中文描述 | PowerShell命令 | 说明 |
|---------|---------------|------|
| 显示当前时间 | `Get-Date` | 获取当前日期和时间 |
| 显示进程 | `Get-Process` | 列出所有进程 |
| 显示服务 | `Get-Service` | 列出所有服务 |
| 列出文件 | `Get-ChildItem` | 列出目录内容 |
| 显示文件内容 | `Get-Content` | 读取文件内容 |
| 查找文件 | `Get-ChildItem -Recurse -Filter` | 递归搜索文件 |
| 复制文件 | `Copy-Item` | 复制文件或目录 |
| 移动文件 | `Move-Item` | 移动文件或目录 |
| 删除文件 | `Remove-Item` | 删除文件或目录 |
| 创建文件夹 | `New-Item -ItemType Directory` | 创建新目录 |
| 显示IP地址 | `Get-NetIPAddress` | 获取网络配置 |
| 测试连接 | `Test-Connection` | Ping测试 |
| 显示路由表 | `Get-NetRoute` | 查看路由信息 |
| 显示系统信息 | `Get-ComputerInfo` | 获取计算机信息 |
| 显示环境变量 | `Get-ChildItem Env:` | 列出环境变量 |

---

### 6.2 配置示例

#### 6.2.1 基础配置示例

**最小配置**（适合快速开始）：
```yaml
# config/minimal.yaml
ai:
  provider: "local"
  model:
    name: "llama2"

security:
  level: "normal"

execution:
  default_timeout: 30

logging:
  level: "INFO"
```

**推荐配置**（平衡性能和功能）：
```yaml
# config/recommended.yaml
ai:
  provider: "ollama"
  model:
    name: "llama2"
    temperature: 0.7
    max_tokens: 256
  translation:
    use_rules_first: true
    enable_cache: true
    cache_ttl: 3600
    max_cache_size: 1000

security:
  level: "normal"
  whitelist:
    enabled: true
  permission_check:
    enabled: true
    require_confirmation_for_admin: true
  sandbox:
    enabled: false

execution:
  default_timeout: 30
  output_encoding: "utf-8"

logging:
  level: "INFO"
  format: "json"
  handlers:
    - type: "file"
      filename: "logs/app.log"
      max_bytes: 10485760
      backup_count: 5

storage:
  backend: "file"
  history:
    enabled: true
    max_entries: 1000
    retention_days: 30
```

**高性能配置**（优化速度）：
```yaml
# config/performance.yaml
ai:
  provider: "ollama"
  model:
    name: "llama2-7b"
    temperature: 0.5
    max_tokens: 128
  translation:
    use_rules_first: true
    enable_cache: true
    cache_ttl: 7200
    max_cache_size: 2000

security:
  level: "normal"
  whitelist:
    enabled: true
  sandbox:
    enabled: false

execution:
  default_timeout: 15
  output:
    max_lines: 500
    truncate_long_lines: true

logging:
  level: "WARNING"
  format: "text"

storage:
  cache:
    max_size: 2000
    eviction_policy: "lru"
```

**高安全配置**（严格安全）：
```yaml
# config/secure.yaml
ai:
  provider: "local"
  model:
    name: "llama2"

security:
  level: "strict"
  whitelist:
    enabled: true
    custom_patterns:
      - pattern: ".*Remove-Item.*"
        risk_level: "HIGH"
      - pattern: ".*Stop-.*"
        risk_level: "MEDIUM"
  permission_check:
    enabled: true
    require_confirmation_for_admin: true
    require_confirmation_for_high_risk: true
  sandbox:
    enabled: true
    provider: "docker"
    memory_limit: "512m"
    network_disabled: true

execution:
  default_timeout: 30

logging:
  level: "INFO"
  format: "json"
  filter_sensitive: true

storage:
  history:
    enabled: true
    max_entries: 10000
```

#### 6.2.2 场景配置示例

**开发环境配置**：
```yaml
# config/development.yaml
ai:
  provider: "ollama"
  translation:
    use_rules_first: true
    enable_cache: false  # 禁用缓存便于测试

security:
  level: "permissive"
  sandbox:
    enabled: false

logging:
  level: "DEBUG"
  handlers:
    - type: "console"
      level: "DEBUG"

storage:
  history:
    max_entries: 100
```

**生产环境配置**：
```yaml
# config/production.yaml
ai:
  provider: "ollama"
  translation:
    use_rules_first: true
    enable_cache: true
    cache_ttl: 7200

security:
  level: "normal"
  whitelist:
    enabled: true
  permission_check:
    enabled: true

logging:
  level: "INFO"
  format: "json"
  handlers:
    - type: "rotating"
      filename: "logs/app.log"
      when: "midnight"
      backup_count: 30

storage:
  history:
    enabled: true
    max_entries: 10000
    auto_cleanup: true

monitoring:
  enabled: true
  export:
    enabled: true
    interval: 300
```

---

### 6.3 术语表

| 术语 | 英文 | 说明 |
|------|------|------|
| AI引擎 | AI Engine | 负责自然语言到PowerShell命令转换的模块 |
| 安全引擎 | Security Engine | 负责命令安全验证的模块 |
| 执行引擎 | Execution Engine | 负责命令执行的模块 |
| 规则匹配 | Rule Matching | 使用预定义规则进行快速翻译 |
| 置信度 | Confidence Score | AI翻译结果的可信程度（0.0-1.0） |
| 风险等级 | Risk Level | 命令的危险程度（SAFE/LOW/MEDIUM/HIGH/CRITICAL） |
| 沙箱 | Sandbox | 隔离的执行环境，用于安全地运行命令 |
| 缓存 | Cache | 存储翻译结果以提高性能 |
| TTL | Time To Live | 缓存条目的生存时间 |
| LRU | Least Recently Used | 最近最少使用的缓存淘汰策略 |
| 命令白名单 | Command Whitelist | 允许或禁止的命令列表 |
| 权限检查 | Permission Check | 验证用户是否有执行命令的权限 |
| 历史记录 | Command History | 已执行命令的记录 |
| 会话 | Session | 一次交互式使用的上下文 |
| 模板 | Template | 预定义的命令模板 |
| 提示词 | Prompt | 发送给AI模型的输入文本 |
| 温度 | Temperature | 控制AI生成随机性的参数 |
| 令牌 | Token | AI模型处理的基本单位 |
| 编码 | Encoding | 字符编码方式（如UTF-8） |
| 超时 | Timeout | 命令执行的最大等待时间 |
| 日志 | Log | 系统运行的记录信息 |
| 配置 | Configuration | 系统的设置参数 |
| 诊断 | Diagnostics | 系统健康检查 |
| 性能指标 | Metrics | 系统性能的度量数据 |

---

### 6.4 更新日志

#### 版本 1.0.0 (2025-11-11)

**新功能**：
- ✨ 完整的中文自然语言支持
- ✨ 基于本地AI模型的智能翻译
- ✨ 三层安全保护机制
- ✨ 跨平台支持（Windows/Linux/macOS）
- ✨ 命令历史管理
- ✨ 灵活的配置系统
- ✨ 交互式和命令行两种模式
- ✨ 规则匹配快速路径
- ✨ LRU缓存优化
- ✨ Docker沙箱隔离执行

**核心模块**：
- AI引擎：支持规则匹配和AI生成
- 安全引擎：命令白名单、权限检查、沙箱执行
- 执行引擎：跨平台命令执行
- 配置管理：YAML配置文件支持
- 日志引擎：结构化日志和敏感信息过滤
- 存储引擎：文件存储和缓存
- 上下文管理：会话和历史管理

**性能指标**：
- 翻译准确率：92%
- 缓存命中响应时间：< 1ms
- 规则匹配响应时间：< 10ms
- AI生成响应时间：< 2s
- 缓存命中率：65%
- 内存占用：380MB（不含AI模型）

**已知问题**：
- AI模型推理速度在低配置机器上较慢
- Docker沙箱有一定性能开销
- 复杂命令的翻译准确率有待提高

---

#### 版本 0.9.0 (2025-10-15) - Beta

**新功能**：
- 基础的自然语言翻译功能
- 简单的安全检查
- 命令历史记录
- 基本配置支持

**改进**：
- 优化翻译速度
- 改进错误处理
- 完善文档

**修复**：
- 修复中文编码问题
- 修复配置加载错误
- 修复历史记录丢失问题

---

#### 版本 0.5.0 (2025-09-01) - Alpha

**新功能**：
- 初始版本发布
- 基本的命令翻译功能
- 简单的命令执行

**已知限制**：
- 仅支持Windows平台
- 翻译准确率较低
- 缺少安全机制

---

### 6.5 快速参考卡片

#### 常用命令速查

**系统信息**：
```
显示当前时间          -> Get-Date
显示系统信息          -> Get-ComputerInfo
显示CPU使用率         -> Get-Counter '\Processor(_Total)\% Processor Time'
显示内存使用情况      -> Get-Process | Sort WorkingSet -Desc | Select -First 10
```

**进程管理**：
```
显示所有进程          -> Get-Process
显示CPU最高的进程     -> Get-Process | Sort CPU -Desc | Select -First 5
查找特定进程          -> Get-Process -Name chrome
停止进程              -> Stop-Process -Name notepad
```

**文件操作**：
```
列出文件              -> Get-ChildItem
查找文件              -> Get-ChildItem -Recurse -Filter "*.txt"
显示文件内容          -> Get-Content file.txt
复制文件              -> Copy-Item source.txt dest.txt
删除文件              -> Remove-Item file.txt
```

**网络诊断**：
```
测试连接              -> Test-Connection baidu.com
显示IP地址            -> Get-NetIPAddress
显示网络连接          -> Get-NetTCPConnection
查询DNS               -> Resolve-DnsName baidu.com
```

#### 配置速查

**AI配置**：
```yaml
ai:
  provider: "ollama"           # local/ollama/openai
  model:
    temperature: 0.7           # 0.0-2.0
  translation:
    use_rules_first: true      # 优先规则匹配
    enable_cache: true         # 启用缓存
```

**安全配置**：
```yaml
security:
  level: "normal"              # strict/normal/permissive
  whitelist:
    enabled: true              # 启用白名单
  sandbox:
    enabled: false             # 启用沙箱
```

**性能优化**：
```yaml
ai:
  translation:
    cache_ttl: 7200            # 增加缓存时间
    max_cache_size: 2000       # 增加缓存大小
execution:
  output:
    max_lines: 500             # 限制输出行数
logging:
  level: "WARNING"             # 减少日志输出
```

---

## 结语

感谢您使用AI PowerShell智能助手！

本用户手册涵盖了系统的主要功能和使用方法。如果您在使用过程中遇到任何问题，请参考故障排除章节或联系技术支持。

我们持续改进系统功能和文档质量，欢迎您提供反馈和建议。

**祝您使用愉快！**

---

**文档版本**: 1.0  
**最后更新**: 2025年11月11日  
**维护者**: AI PowerShell开发团队  
**许可证**: MIT License

