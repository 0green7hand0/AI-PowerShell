<!-- 文档类型: 用户指南 | 最后更新: 2025-01-17 | 维护者: 项目团队 -->

# AI PowerShell 智能助手 - 用户指南

---
📍 [首页](../README.md) > [文档中心](README.md) > 用户指南

## 📋 目录

- [简介](#简介)
- [快速开始](#快速开始)
- [UI 系统](#ui-系统)
- [进度管理](#进度管理)
- [启动体验](#启动体验)
- [安全机制](#安全机制)
- [常见任务](#常见任务)
- [最佳实践](#最佳实践)
- [故障排除](#故障排除)

---

## 简介

AI PowerShell 智能助手是一个现代化的命令行工具，提供智能化的 PowerShell 脚本生成和执行能力。本指南将帮助您快速上手并充分利用系统的各项功能。

### 主要特性

- **智能 UI 系统**: 美观的彩色输出、图标支持、主题系统
- **进度管理**: 实时进度指示、多任务并发显示
- **启动优化**: 首次运行向导、系统检查、快速启动
- **安全保障**: 脚本安全检查、危险命令检测、路径验证
- **模板系统**: 丰富的脚本模板库、自定义模板支持

---

## 快速开始

### 安装和初始化

```bash
# 克隆项目
git clone https://github.com/0green7hand0/AI-PowerShell.git
cd AI-PowerShell

# 安装依赖
pip install -r requirements.txt

# 首次运行
python run.py
```

### 基本使用

```python
from src.ui import UIManager
from src.ui.models import UIConfig

# 创建 UI 管理器
config = UIConfig(
    enable_colors=True,
    enable_icons=True,
    theme="default"
)
ui = UIManager(config)

# 显示消息
ui.print_success("操作成功！")
ui.print_error("发生错误")
ui.print_warning("警告信息")
ui.print_info("提示信息")
```

### 交互模式

```bash
# 启动交互模式
python run.py

# 输入自然语言命令
> 列出所有正在运行的进程
> 创建一个备份脚本
> 检查网络连接状态
```

---

## UI 系统

### 彩色输出

UI 系统提供丰富的彩色输出功能，使用颜色区分不同类型的信息：

```python
# 成功消息（绿色）
ui.print_success("操作成功完成")

# 错误消息（红色）
ui.print_error("操作失败")

# 警告消息（黄色）
ui.print_warning("请注意此操作")

# 信息消息（蓝色）
ui.print_info("这是一条提示信息")
```

### 图标支持

支持三种图标风格：

- **Emoji**: ✅ ❌ ⚠️ ℹ️
- **ASCII**: [OK] [X] [!] [i]
- **Unicode**: ✓ ✗ ⚠ ℹ

```python
# 配置图标风格
config = UIConfig(
    enable_icons=True,
    icon_style="emoji"  # 或 "ascii", "unicode", "none"
)
ui = UIManager(config)
```

### 主题系统

内置四种颜色主题：

1. **default**: 默认主题，适合大多数终端
2. **dark**: 深色主题，适合深色背景
3. **light**: 浅色主题，适合浅色背景
4. **minimal**: 极简主题，仅使用白色

```python
# 切换主题
config = UIConfig(theme="dark")
ui = UIManager(config)
```

### 表格显示

创建美观的表格来展示数据：

```python
# 创建表格
table = ui.create_table(title="模板列表", show_header=True)
table.add_column("名称", style="cyan")
table.add_column("描述", style="white")
table.add_column("状态", justify="center")

# 添加数据
table.add_row("backup_script", "系统备份脚本", "✓")
table.add_row("network_test", "网络诊断工具", "✓")

# 显示表格
ui.print_table(table)
```

### 面板组件

使用面板突出显示重要信息：

```python
# 创建面板
panel = ui.create_panel(
    "这是重要信息\n请仔细阅读",
    title="提示",
    border_style="info"
)
ui.print_panel(panel)
```

### 列表和字典显示

```python
# 显示列表
items = ["项目1", "项目2", "项目3"]
ui.print_list(items, title="任务列表", numbered=True)

# 显示字典
data = {
    "名称": "AI PowerShell",
    "版本": "1.0.0",
    "状态": "运行中"
}
ui.print_dict(data, title="系统信息")
```

### UI 配置

UI 系统的配置文件位于 `config/ui.yaml`：

```yaml
ui:
  # 颜色设置
  colors:
    enabled: true           # 是否启用彩色输出
    theme: "default"        # 主题名称
  
  # 图标设置
  icons:
    enabled: true           # 是否显示图标
    style: "emoji"          # 图标风格
  
  # 进度指示器设置
  progress:
    enabled: true           # 是否显示进度指示
    animations: true        # 是否启用动画效果
  
  # 交互式输入设置
  input:
    auto_complete: true     # 是否启用自动补全
    history_enabled: true   # 是否启用历史记录
    history_size: 1000      # 历史记录最大条数
    history_file: ".ai_powershell_history"  # 历史记录文件
  
  # 显示设置
  display:
    max_width: 120          # 最大显示宽度
    page_size: 20           # 分页大小
    auto_pager: true        # 自动分页
    show_lines: false       # 表格是否显示行线
    box_style: "rounded"    # 边框样式
```

### 主题自定义

#### 主题基础

主题定义了 CLI 界面中各种元素的颜色和样式，包括成功/错误/警告/信息消息的颜色、主要和次要文本的颜色、高亮和弱化文本的样式等。

#### 主题结构

每个主题必须定义以下元素：

```yaml
themes:
  my_theme:
    success: "颜色定义"      # 成功消息
    error: "颜色定义"        # 错误消息
    warning: "颜色定义"      # 警告消息
    info: "颜色定义"         # 信息消息
    primary: "颜色定义"      # 主要文本
    secondary: "颜色定义"    # 次要文本
    muted: "颜色定义"        # 弱化文本
    highlight: "颜色定义"    # 高亮文本
```

#### 颜色语法

支持以下颜色语法：

- **基本颜色**: `red`, `green`, `blue`, `yellow`, `cyan`, `magenta`, `white`, `black`
- **亮色**: `bright_red`, `bright_green`, 等
- **样式**: `bold`, `dim`, `italic`, `underline`
- **背景色**: `on red`, `on blue`, 等
- **组合**: `bold red on white`, `dim cyan`, 等

#### 主题示例

##### 示例 1：Solarized Dark 风格

```yaml
themes:
  solarized_dark:
    success: "bold green"
    error: "bold red"
    warning: "bold yellow"
    info: "bold blue"
    primary: "bold cyan"
    secondary: "magenta"
    muted: "dim bright_black"
    highlight: "bold bright_cyan on black"
```

##### 示例 2：Nord 风格

```yaml
themes:
  nord:
    success: "bold bright_green"
    error: "bold bright_red"
    warning: "bold bright_yellow"
    info: "bold bright_blue"
    primary: "bold bright_cyan"
    secondary: "bold bright_magenta"
    muted: "dim white"
    highlight: "bold white on bright_blue"
```

#### 使用自定义主题

##### 方式 1：配置文件

在 `config/ui.yaml` 中设置：

```yaml
ui:
  colors:
    theme: "my_custom_theme"  # 使用自定义主题名称
```

##### 方式 2：命令行参数

```bash
python src/main.py --theme my_custom_theme
```

##### 方式 3：编程方式

```python
from src.ui import UIManager, UIConfigLoader

# 加载配置
config = UIConfigLoader.load_config()
ui = UIManager(config)

# 切换主题
ui.theme_manager.switch_theme("my_custom_theme")
```

### 图标配置

#### 图标风格

系统支持四种图标风格：

##### 1. Emoji（表情符号）

使用 Unicode Emoji，视觉效果最佳：

```yaml
ui:
  icons:
    style: "emoji"
```

显示效果：
- 成功: ✅
- 错误: ❌
- 警告: ⚠️
- 信息: ℹ️
- 进行中: 🔄

##### 2. ASCII（ASCII 字符）

使用纯 ASCII 字符，兼容性最好：

```yaml
ui:
  icons:
    style: "ascii"
```

显示效果：
- 成功: [OK]
- 错误: [X]
- 警告: [!]
- 信息: [i]
- 进行中: [~]

##### 3. Unicode（Unicode 符号）

使用 Unicode 符号，平衡美观和兼容性：

```yaml
ui:
  icons:
    style: "unicode"
```

显示效果：
- 成功: ✓
- 错误: ✗
- 警告: ⚠
- 信息: ⓘ
- 进行中: ⟳

### 进度指示器配置

```yaml
ui:
  progress:
    enabled: true           # 是否显示进度指示
    animations: true        # 是否启用动画效果
```

系统会根据任务类型自动选择合适的进度指示器：
- **Spinner**: 用于不确定时长的任务
- **Progress Bar**: 用于可以跟踪进度的任务
- **Status**: 用于简单的状态显示

### 交互式输入配置

#### 自动补全

```yaml
ui:
  input:
    auto_complete: true  # 启用命令自动补全
```

启用后，输入命令时按 `Tab` 键可以自动补全。

#### 命令历史

```yaml
ui:
  input:
    history_enabled: true              # 启用历史记录
    history_size: 1000                 # 最多保存 1000 条
    history_file: ".ai_powershell_history"  # 历史文件名
```

启用后，可以使用上下箭头键浏览历史命令。

### 显示配置

#### 宽度和分页

```yaml
ui:
  display:
    max_width: 120       # 最大显示宽度（字符）
    page_size: 20        # 每页显示行数
    auto_pager: true     # 自动分页长列表
```

#### 表格样式

```yaml
ui:
  display:
    show_lines: false    # 是否显示表格行线
    box_style: "rounded" # 边框样式
```

支持的边框样式：
- `rounded`: 圆角边框（默认）
- `minimal`: 极简边框
- `simple`: 简单边框
- `double`: 双线边框
- `heavy`: 粗线边框

### 终端兼容性

#### 自动检测

系统会自动检测终端能力并调整配置：
- 不支持颜色的终端：自动禁用颜色
- 不支持 Unicode 的终端：自动切换到 ASCII 图标
- 窄终端：自动调整显示宽度

#### 手动配置

如果自动检测不准确，可以手动配置：

```yaml
ui:
  colors:
    enabled: false       # 强制禁用颜色
  icons:
    style: "ascii"       # 强制使用 ASCII 图标
```

### 配置示例

#### 示例 1：极简配置

适合不支持高级功能的终端：

```yaml
ui:
  colors:
    enabled: false
    theme: "minimal"
  icons:
    enabled: false
  progress:
    enabled: false
    animations: false
  input:
    auto_complete: false
    history_enabled: true
  display:
    max_width: 80
    show_lines: false
    box_style: "simple"
```

#### 示例 2：完整功能配置

适合现代终端：

```yaml
ui:
  colors:
    enabled: true
    theme: "dark"
  icons:
    enabled: true
    style: "emoji"
  progress:
    enabled: true
    animations: true
  input:
    auto_complete: true
    history_enabled: true
    history_size: 2000
  display:
    max_width: 140
    page_size: 30
    auto_pager: true
    show_lines: true
    box_style: "rounded"
```

### 编程方式配置

```python
from src.ui import UIManager, UIConfigLoader
from src.ui.models import UIConfig

# 方式 1：从文件加载
config = UIConfigLoader.load_config("config/ui.yaml")
ui = UIManager(config)

# 方式 2：手动创建配置
config = UIConfig(
    enable_colors=True,
    enable_icons=True,
    theme="dark",
    icon_style="emoji",
    max_width=120
)
ui = UIManager(config)

# 方式 3：运行时修改
ui.theme_manager.switch_theme("light")
ui.config.icon_style = "unicode"
```

### 主题设计指南

#### 1. 保持一致性

确保主题在不同元素间保持视觉一致性：

```yaml
themes:
  consistent_theme:
    # 使用相同的颜色系列
    success: "bold green"
    info: "bold blue"
    warning: "bold yellow"
    error: "bold red"
    
    # 主要和次要文本使用相关颜色
    primary: "bold cyan"
    secondary: "cyan"
    
    # 弱化文本使用暗淡样式
    muted: "dim white"
    
    # 高亮使用对比色
    highlight: "bold bright_cyan"
```

#### 2. 考虑可读性

选择在目标终端背景上清晰可读的颜色：

**深色背景终端**:
```yaml
themes:
  dark_readable:
    success: "bold bright_green"    # 使用亮色
    error: "bold bright_red"
    primary: "bold bright_cyan"
    muted: "dim bright_white"       # 暗淡但仍可读
```

**浅色背景终端**:
```yaml
themes:
  light_readable:
    success: "bold green"           # 使用标准色
    error: "bold red"
    primary: "bold blue"
    muted: "dim black"              # 深色弱化文本
```

#### 3. 测试对比度

确保文本和背景有足够对比度：

```yaml
# 好的对比度
highlight: "bold white on blue"

# 差的对比度（避免）
highlight: "yellow on white"
```

### 高级技巧

#### 动态主题切换

根据时间或环境自动切换主题：

```python
from datetime import datetime
from src.ui import UIManager, UIConfigLoader

config = UIConfigLoader.load_config()
ui = UIManager(config)

# 根据时间选择主题
hour = datetime.now().hour
if 6 <= hour < 18:
    ui.theme_manager.switch_theme("light")
else:
    ui.theme_manager.switch_theme("dark")
```

#### 主题继承

基于现有主题创建变体：

```yaml
themes:
  # 基础主题
  base:
    success: "bold green"
    error: "bold red"
    warning: "bold yellow"
    info: "bold blue"
    primary: "bold cyan"
    secondary: "bold magenta"
    muted: "dim white"
    highlight: "bold bright_cyan"
  
  # 变体：只修改部分颜色
  base_variant:
    success: "bold bright_green"    # 修改
    error: "bold bright_red"        # 修改
    warning: "bold yellow"          # 保持
    info: "bold blue"               # 保持
    primary: "bold cyan"            # 保持
    secondary: "bold magenta"       # 保持
    muted: "dim white"              # 保持
    highlight: "bold bright_cyan"   # 保持
```

---

## 进度管理

### 进度条

用于显示可量化进度的操作：

```python
from src.ui import UIManager

ui = UIManager()
pm = ui.progress_manager

# 启动进度条
pm.start_progress("task1", "处理文件中...", total=100)

# 更新进度
for i in range(100):
    # 执行任务
    pm.update_progress("task1", advance=1)

# 完成进度
pm.finish_progress("task1", success=True)
```

### Spinner 加载动画

用于不确定时长的操作：

```python
# 启动 spinner
pm.start_spinner("loading", "正在加载数据...")

# 执行操作
# ...

# 完成
pm.finish_progress("loading", success=True)
```

### 上下文管理器

推荐使用上下文管理器自动管理进度：

```python
# 自动管理进度的开始和结束
with pm.progress_context("backup", "备份数据...", total=100) as progress:
    for i in range(100):
        # 执行任务
        progress.update_progress("backup", advance=1)
# 退出上下文时自动完成进度
```

### 更新进度

```python
# 使用绝对值更新
pm.update_progress("task1", completed=50)

# 使用相对值更新
pm.update_progress("task1", advance=10)

# 更新描述
pm.update_progress("task1", description="新的描述")

# 组合更新
pm.update_progress(
    "task1",
    completed=75,
    description="即将完成..."
)
```

### 多任务管理

同时显示多个进度任务：

```python
# 启动多个任务
pm.start_progress("download", "下载文件...", total=100)
pm.start_progress("extract", "解压文件...", total=50)
pm.start_spinner("verify", "验证数据...")

# 更新各个任务
pm.update_progress("download", advance=10)
pm.update_progress("extract", advance=5)

# 完成任务
pm.finish_progress("download")
pm.finish_progress("extract")
pm.finish_progress("verify")
```

### 查询任务状态

```python
# 获取任务状态
task = pm.get_task_status("task1")
if task:
    print(f"进度: {task.percentage}%")
    print(f"完成: {task.completed}/{task.total}")

# 检查是否有活动任务
if pm.has_active_tasks():
    print("有任务正在进行")
```

### 与其他模块集成

#### 与 AI 引擎集成

```python
from src.ai_engine import AIEngine

ai_engine = AIEngine()
pm = ui.progress_manager

# 启动进度
pm.start_progress("ai_translate", "AI 翻译中...", total=4)

# 定义进度回调
def progress_callback(step, total, description):
    pm.update_progress("ai_translate", completed=step, description=description)

# 执行翻译
suggestion = ai_engine.translate_natural_language(
    "列出所有文件",
    Context(),
    progress_callback=progress_callback
)

pm.finish_progress("ai_translate", success=True)
```

---

## 启动体验

### 首次运行向导

首次运行时，系统会自动启动欢迎向导：

1. **显示欢迎信息**: 展示欢迎横幅和程序介绍
2. **运行系统检查**: 执行完整的环境检查
3. **显示检查结果**: 以表格形式展示所有检查项
4. **自动修复问题**: 询问是否修复可修复的问题
5. **标记已初始化**: 创建标记文件，避免重复运行

### 系统检查项

启动向导会检查以下项目：

- ✓ Python 版本检查
- ✓ PowerShell 可用性检查
- ✓ 配置文件完整性检查
- ✓ 日志目录检查
- ✓ 模板目录检查
- ✓ 存储目录检查
- ✓ 依赖包检查

### 检查状态说明

- **PASSED** (✓): 检查通过
- **WARNING** (⚠): 有警告但不影响运行
- **FAILED** (✗): 检查失败，可能影响功能
- **SKIPPED** (-): 跳过检查

### 自动修复功能

支持自动修复的问题：
- 创建缺失的配置目录
- 创建缺失的日志目录
- 创建缺失的模板目录
- 创建缺失的存储目录

不支持自动修复的问题：
- Python 版本过低（需要升级 Python）
- PowerShell 未安装（需要安装 PowerShell）
- 依赖包缺失（需要运行 `pip install -r requirements.txt`）

### 常规启动流程

非首次运行时的启动流程：

1. **快速系统检查**: 仅检查关键项
2. **显示启动横幅**: 展示程序标题和版本
3. **显示功能概览**: 列出主要功能
4. **显示快速提示**: 提供使用建议
5. **显示就绪状态**: 显示启动耗时和就绪消息

### 使用启动向导

```python
from src.ui import StartupWizard, UIManager

ui_manager = UIManager()
wizard = StartupWizard(ui_manager)

# 检查是否首次运行
if wizard.is_first_run():
    wizard.run_welcome_wizard()

# 快速系统检查
success, checks = wizard.quick_system_check()
```

### 使用启动体验

```python
from src.ui import StartupExperience

startup = StartupExperience()

# 运行完整启动序列
startup.run_startup_sequence()

# 显示会话摘要（退出时）
stats = {
    'commands_executed': 10,
    'successful_commands': 8,
    'failed_commands': 2,
    'session_duration': 120.5,
}
startup.display_session_summary(stats)
```

---

## 安全机制

### 安全检查概述

系统内置全面的安全检查机制，用于检测 PowerShell 脚本中的危险操作：

- 危险命令检测
- 网络访问检测
- 路径遍历攻击检测
- 敏感路径访问检测

### 安全级别

#### Critical（严重 - 阻止执行）

- 递归强制删除: `Remove-Item -Recurse -Force`
- 磁盘操作: `Format-Volume`, `Clear-Disk`
- 系统关机: `Stop-Computer`, `Restart-Computer`
- 分区操作: `Remove-Partition`, `Set-Partition`

#### High（高危 - 阻止执行）

- 强制删除: `Remove-Item -Force`
- 系统目录访问: `C:\Windows`, `C:\Program Files`
- 代码执行: `Invoke-Expression`, `iex`
- 远程命令: `Invoke-Command`
- 服务管理: `New-Service`, `Set-Service`
- 不受限执行策略: `Set-ExecutionPolicy Unrestricted`

#### Medium（中危 - 仅警告）

- 一般删除: `Remove-Item`
- 回收站: `Clear-RecycleBin -Force`
- 网络适配器: `Disable-NetAdapter`
- 防火墙: `Set-NetFirewallProfile`

### 网络访问检测

#### High Severity（高危）

- Web 请求: `Invoke-WebRequest`, `Invoke-RestMethod`
- 文件传输: `Start-BitsTransfer`
- 邮件: `Send-MailMessage`

#### Medium Severity（中危）

- 网络测试: `Test-Connection`, `Test-NetConnection`
- DNS: `Resolve-DnsName`

### 路径安全

#### 检测的危险模式

- 路径遍历: `../`, `..\`, URL 编码变体
- 敏感路径:
  - `C:\Windows\System32`
  - `C:\Program Files`
  - 注册表: `HKLM:`, `HKCU:`

#### 安全路径

- 用户目录: `C:\Users\Documents`
- 项目目录: `D:\Projects`
- 相对路径: `.\output`

### 使用安全检查

```python
from src.template_engine.security_checker import SecurityChecker

# 创建安全检查器
checker = SecurityChecker()

# 检查脚本
script = """
param([string]$Path)
Remove-Item $Path -Recurse -Force
"""

result = checker.check_template(script)

if not result.is_safe:
    print("发现安全问题:")
    for issue in result.issues:
        print(f"  [{issue.severity}] {issue.message}")
        print(f"    第 {issue.line_number} 行: {issue.code_snippet}")
```

### 与模板验证器集成

```python
from src.template_engine.template_validator import TemplateValidator

# 安全检查默认启用
validator = TemplateValidator(enable_security_checks=True)

# 验证模板（包含安全检查）
result = validator.validate_template(template)

if not result.is_valid:
    for error in result.errors:
        print(f"错误: {error}")
```

### 安全最佳实践

#### 对于模板创建者

1. **避免危险操作**: 使用安全替代方案
   - ❌ `Remove-Item -Recurse -Force`
   - ✅ `Remove-Item -Confirm`

2. **验证用户输入**: 始终验证路径和参数
   ```powershell
   if (Test-Path $UserPath) {
       # 安全操作
   }
   ```

3. **使用相对路径**: 避免绝对系统路径
   - ❌ `C:\Windows\System32\file.txt`
   - ✅ `.\output\file.txt`

4. **限制网络访问**: 仅在必要时使用
   - 记录为什么需要网络访问
   - 使用 HTTPS 确保安全

#### 对于开发者

1. **始终启用安全检查**（生产环境）
2. **优雅处理安全错误**
3. **提供清晰的错误消息**
4. **记录安全问题**用于审计

---

## 常见任务

### 任务 1: 创建和使用模板

```python
from src.template_engine import TemplateEngine

# 创建模板引擎
template_engine = TemplateEngine(config={})

# 处理请求
script = template_engine.process_request("创建备份脚本")

# 执行脚本
from src.execution import CommandExecutor
executor = CommandExecutor()
result = executor.execute(script)
```

### 任务 2: 显示进度的长时间操作

```python
ui = UIManager()
pm = ui.progress_manager

with pm.progress_context("long_task", "处理中...", total=100) as progress:
    for i in range(100):
        # 执行任务
        time.sleep(0.1)
        progress.update_progress("long_task", advance=1)
```

### 任务 3: 自定义 UI 主题

```python
# 创建自定义主题
from src.ui.theme_manager import ThemeManager

theme_manager = ThemeManager()
theme_manager.add_custom_theme("my_theme", {
    "success": "bright_green",
    "error": "bright_red",
    "warning": "bright_yellow",
    "info": "bright_blue"
})

# 使用自定义主题
config = UIConfig(theme="my_theme")
ui = UIManager(config)
```

### 任务 4: 批量处理文件

```python
import os

ui = UIManager()
pm = ui.progress_manager

files = os.listdir("./data")
total = len(files)

with pm.progress_context("process_files", f"处理 {total} 个文件", total=total) as progress:
    for i, file in enumerate(files):
        # 处理文件
        process_file(file)
        progress.update_progress("process_files", completed=i+1, 
                                description=f"已处理 {i+1}/{total} 个文件")
```

### 任务 5: 运行系统检查

```python
from src.ui import StartupWizard, UIManager

ui_manager = UIManager()
wizard = StartupWizard(ui_manager)

# 运行完整系统检查
success, checks = wizard.run_system_check()

# 显示结果
for check in checks:
    print(f"{check.name}: {check.status}")
```

---

## 最佳实践

### UI 系统

1. **一致性**: 在整个应用中使用一致的消息类型和样式
2. **可读性**: 使用适当的颜色和图标提高可读性
3. **可配置性**: 允许用户自定义 UI 设置
4. **降级支持**: 在不支持颜色的终端上提供降级方案

### 进度管理

1. **使用上下文管理器**: 自动管理进度的生命周期
2. **选择合适的进度类型**:
   - Spinner: 不确定时长的操作
   - 进度条: 可量化进度的操作
3. **提供有意义的描述**: 让用户了解当前操作
4. **及时清理任务**: 确保调用 `finish_progress`
5. **避免过度更新**: 批量更新而非每次都更新

### 安全机制

1. **始终启用安全检查**: 在生产环境中
2. **验证用户输入**: 检查所有外部输入
3. **使用安全路径**: 避免系统目录和绝对路径
4. **限制网络访问**: 仅在必要时使用
5. **记录安全事件**: 用于审计和分析

---

## 故障排除

### UI 系统问题

#### 颜色不显示

**可能原因**:
- 终端不支持 ANSI 颜色
- 配置中禁用了颜色

**解决方案**:
1. 检查 `config/ui.yaml` 中 `colors.enabled` 是否为 `true`
2. 在 Windows 上，确保使用 Windows 10+ 或安装 colorama
3. 尝试不同的主题

#### 图标显示异常

**可能原因**:
- 终端字体不支持 Unicode/Emoji

**解决方案**:
1. 切换到 ASCII 图标风格: `icon_style: "ascii"`
2. 或禁用图标: `enable_icons: false`
3. 更换支持 Unicode 的终端字体

### 进度管理问题

#### 进度不显示

**可能原因**:
- 配置中禁用了进度功能

**解决方案**:
```python
config = UIConfig(enable_progress=True)  # 确保为 True
ui = UIManager(config)
```

#### 进度卡住不动

**可能原因**:
- 忘记调用 `finish_progress`

**解决方案**:
```python
# 使用上下文管理器自动完成
with pm.progress_context("task1", "处理中", total=100) as progress:
    # ...
```

#### 多个进度条重叠

**可能原因**:
- task_id 重复

**解决方案**:
```python
pm.start_progress("task1", "任务1", total=100)  # ✓
pm.start_progress("task2", "任务2", total=50)   # ✓
# 避免重复的 task_id
```

### 启动体验问题

#### 首次运行向导重复出现

**可能原因**:
- `.ai_powershell_initialized` 文件被删除

**解决方案**:
- 确保该文件存在于项目根目录
- 如果不想再次运行向导，不要删除该文件

#### 系统检查失败

**解决方案**:
1. 查看具体的失败项
2. 根据提示修复问题
3. 使用自动修复功能（如果可用）
4. 手动创建缺失的目录或安装依赖

### 安全机制问题

#### 误报（False Positives）

**解决方案**:
1. 检查命令是否在注释中（应该被跳过）
2. 验证命令模式
3. 考虑操作是否真的安全

#### 漏报（False Negatives）

**解决方案**:
1. 检查 `DANGEROUS_COMMANDS` 中的命令模式
2. 如果缺失，添加该模式
3. 提交 bug 报告

---

## 相关文档

- [模板系统指南](template-guide.md) - 详细的模板使用和创建指南
- [开发者指南](developer-guide.md) - 开发和扩展系统功能
- [系统架构](architecture.md) - 了解系统内部结构
- [API 参考](api-reference.md) - 完整的 API 文档
- [故障排除指南](troubleshooting.md) - 更多问题解决方案

## 下一步

- 📖 阅读 [模板系统指南](template-guide.md) 学习如何创建自定义模板
- 🔧 查看 [配置参考](config-reference.md) 了解所有配置选项
- 💻 参考 [开发者指南](developer-guide.md) 参与项目开发
- 🐛 遇到问题？查看 [故障排除指南](troubleshooting.md)

---

**需要帮助?** 查看 [故障排除指南](troubleshooting.md) 或 [提交 Issue](https://github.com/0green7hand0/AI-PowerShell/issues)
