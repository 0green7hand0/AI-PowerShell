# 主题自定义指南

## 概述

本指南介绍如何为 AI PowerShell 智能助手创建和自定义 UI 主题。

## 主题基础

### 什么是主题？

主题定义了 CLI 界面中各种元素的颜色和样式，包括：
- 成功/错误/警告/信息消息的颜色
- 主要和次要文本的颜色
- 高亮和弱化文本的样式
- 表格、面板等组件的边框颜色

### 主题文件位置

主题配置在 `config/ui.yaml` 文件的 `themes` 部分。

## 创建自定义主题

### 基本步骤

1. 打开 `config/ui.yaml`
2. 在 `themes` 部分添加新主题
3. 定义所需的颜色元素
4. 在 `ui.colors.theme` 中引用新主题

### 主题结构

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

## 颜色语法

### 基本颜色

支持以下基本颜色名称：

- `black` - 黑色
- `red` - 红色
- `green` - 绿色
- `yellow` - 黄色
- `blue` - 蓝色
- `magenta` - 品红色
- `cyan` - 青色
- `white` - 白色

### 亮色变体

每种颜色都有亮色版本：

- `bright_black` - 亮黑色（灰色）
- `bright_red` - 亮红色
- `bright_green` - 亮绿色
- `bright_yellow` - 亮黄色
- `bright_blue` - 亮蓝色
- `bright_magenta` - 亮品红色
- `bright_cyan` - 亮青色
- `bright_white` - 亮白色

### 文本样式

可以添加以下样式修饰符：

- `bold` - 粗体
- `dim` - 暗淡
- `italic` - 斜体
- `underline` - 下划线
- `blink` - 闪烁（不推荐）
- `reverse` - 反转前景和背景色
- `strike` - 删除线

### 背景色

使用 `on` 关键字设置背景色：

```yaml
# 白色文本，蓝色背景
highlight: "white on blue"

# 粗体黄色文本，红色背景
warning: "bold yellow on red"
```

### 组合样式

可以组合多个样式：

```yaml
# 粗体、斜体、红色文本
error: "bold italic red"

# 粗体、下划线、青色文本，黑色背景
highlight: "bold underline cyan on black"

# 暗淡的绿色文本
muted: "dim green"
```

## 主题示例

### 示例 1：Solarized Dark 风格

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

### 示例 2：Nord 风格

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

### 示例 3：Dracula 风格

```yaml
themes:
  dracula:
    success: "bold bright_green"
    error: "bold bright_red"
    warning: "bold bright_yellow"
    info: "bold bright_cyan"
    primary: "bold bright_magenta"
    secondary: "bold magenta"
    muted: "dim bright_black"
    highlight: "bold bright_cyan on black"
```

### 示例 4：Monokai 风格

```yaml
themes:
  monokai:
    success: "bold bright_green"
    error: "bold bright_red"
    warning: "bold bright_yellow"
    info: "bold bright_blue"
    primary: "bold bright_cyan"
    secondary: "bold bright_magenta"
    muted: "dim white"
    highlight: "bold black on bright_yellow"
```

### 示例 5：高对比度主题

```yaml
themes:
  high_contrast:
    success: "bold bright_green on black"
    error: "bold bright_red on black"
    warning: "bold bright_yellow on black"
    info: "bold bright_cyan on black"
    primary: "bold bright_white on black"
    secondary: "bold bright_blue on black"
    muted: "bright_black on black"
    highlight: "bold black on bright_white"
```

### 示例 6：柔和主题

```yaml
themes:
  soft:
    success: "green"
    error: "red"
    warning: "yellow"
    info: "blue"
    primary: "cyan"
    secondary: "magenta"
    muted: "dim white"
    highlight: "bold cyan"
```

## 使用自定义主题

### 方式 1：配置文件

在 `config/ui.yaml` 中设置：

```yaml
ui:
  colors:
    enabled: true
    theme: "my_custom_theme"  # 使用自定义主题名称
```

### 方式 2：命令行参数

```bash
python src/main.py --theme my_custom_theme
```

### 方式 3：编程方式

```python
from src.ui import UIManager, UIConfigLoader

# 加载配置
config = UIConfigLoader.load_config()
ui = UIManager(config)

# 切换主题
ui.theme_manager.switch_theme("my_custom_theme")
```

## 主题设计指南

### 1. 保持一致性

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

### 2. 考虑可读性

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

### 3. 测试对比度

确保文本和背景有足够对比度：

```yaml
# 好的对比度
highlight: "bold white on blue"

# 差的对比度（避免）
highlight: "yellow on white"
```

### 4. 限制颜色数量

不要使用太多不同的颜色，保持简洁：

```yaml
# 推荐：使用有限的颜色调色板
themes:
  simple:
    success: "bold green"
    error: "bold red"
    warning: "bold yellow"
    info: "bold blue"
    primary: "bold white"
    secondary: "white"
    muted: "dim white"
    highlight: "bold cyan"
```

### 5. 考虑色盲用户

不要仅依赖颜色区分信息，结合图标和文本：

```yaml
# 使用不同的样式，不仅是颜色
themes:
  accessible:
    success: "bold green"           # 粗体 + 绿色
    error: "bold underline red"     # 粗体 + 下划线 + 红色
    warning: "bold italic yellow"   # 粗体 + 斜体 + 黄色
    info: "bold blue"               # 粗体 + 蓝色
```

## 主题测试

### 使用演示脚本

运行 UI 演示查看主题效果：

```bash
python examples/ui_demo.py
```

### 测试所有消息类型

确保测试所有消息类型：

```python
from src.ui import UIManager, UIConfigLoader

config = UIConfigLoader.load_config()
ui = UIManager(config)

# 测试所有消息类型
ui.print_success("成功消息测试")
ui.print_error("错误消息测试")
ui.print_warning("警告消息测试")
ui.print_info("信息消息测试")

# 测试表格
table = ui.create_table(title="测试表格")
table.add_column("列1", style="primary")
table.add_column("列2", style="secondary")
table.add_row("数据1", "数据2")
ui.print_table(table)

# 测试面板
panel = ui.create_panel("测试面板内容", title="测试", border_style="info")
ui.print_panel(panel)
```

### 在不同终端测试

在多个终端环境中测试主题：

- Windows Terminal
- PowerShell
- CMD
- Git Bash
- WSL
- macOS Terminal
- iTerm2
- Linux 终端

## 分享主题

### 导出主题

创建独立的主题文件：

```yaml
# my_theme.yaml
name: "My Custom Theme"
author: "Your Name"
description: "A beautiful custom theme"
version: "1.0.0"

colors:
  success: "bold green"
  error: "bold red"
  warning: "bold yellow"
  info: "bold blue"
  primary: "bold cyan"
  secondary: "bold magenta"
  muted: "dim white"
  highlight: "bold bright_cyan"
```

### 导入主题

将主题添加到 `config/ui.yaml`：

```yaml
themes:
  # 从文件导入的主题
  my_custom_theme:
    success: "bold green"
    error: "bold red"
    warning: "bold yellow"
    info: "bold blue"
    primary: "bold cyan"
    secondary: "bold magenta"
    muted: "dim white"
    highlight: "bold bright_cyan"
```

## 故障排除

### 颜色不显示

**问题**: 自定义颜色不生效

**解决方案**:
1. 检查颜色名称拼写是否正确
2. 确认终端支持指定的颜色
3. 验证 YAML 语法是否正确
4. 检查是否启用了颜色：`colors.enabled: true`

### 主题切换无效

**问题**: 切换主题后没有变化

**解决方案**:
1. 确认主题名称正确
2. 重启应用程序
3. 清除缓存：删除 `.ai_powershell_cache`
4. 检查配置文件是否正确保存

### 样式冲突

**问题**: 某些样式组合不工作

**解决方案**:
1. 简化样式组合
2. 测试单个样式是否工作
3. 查看终端文档了解支持的样式
4. 尝试不同的样式组合

## 高级技巧

### 动态主题切换

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

### 主题继承

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

### 条件主题

根据条件使用不同主题：

```python
import os
from src.ui import UIManager, UIConfigLoader

config = UIConfigLoader.load_config()
ui = UIManager(config)

# 根据环境变量选择主题
theme = os.getenv("AI_POWERSHELL_THEME", "default")
ui.theme_manager.switch_theme(theme)
```

## 相关资源

- [UI 配置指南](ui-configuration-guide.md) - 完整 UI 配置说明
- [CLI UI 系统指南](ui-system-guide.md) - UI 系统使用说明
- [Rich 文档](https://rich.readthedocs.io/) - Rich 库官方文档

## 贡献主题

如果您创建了优秀的主题，欢迎贡献：

1. Fork 项目仓库
2. 添加主题到 `config/ui.yaml`
3. 添加主题截图到 `docs/themes/`
4. 更新本文档添加主题示例
5. 提交 Pull Request

## 反馈

如有问题或建议：
- 提交 [Issue](https://github.com/0green7hand0/AI-PowerShell/issues)
- 参与 [讨论](https://github.com/0green7hand0/AI-PowerShell/discussions)
