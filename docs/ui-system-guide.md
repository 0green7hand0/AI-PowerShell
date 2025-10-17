# CLI UI 系统使用指南

## 概述

AI PowerShell 智能助手现在配备了现代化的 CLI 用户界面系统，提供美观的彩色输出、进度指示、交互式输入等功能。

## 功能特性

### ✨ 已实现的功能

- **彩色输出**: 使用颜色区分不同类型的信息（成功、错误、警告、信息）
- **图标支持**: 支持 Emoji、ASCII、Unicode 三种图标风格
- **主题系统**: 内置多种颜色主题（default、dark、light、minimal）
- **格式化表格**: 美观的表格显示，支持自定义样式
- **面板组件**: 用于显示重要信息的面板
- **列表和字典显示**: 格式化的数据展示

### 🚧 开发中的功能

- 进度指示器和加载动画
- 交互式输入和自动补全
- 增强的帮助系统
- 智能错误处理

## 快速开始

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

# 显示各种消息
ui.print_success("操作成功！")
ui.print_error("发生错误")
ui.print_warning("警告信息")
ui.print_info("提示信息")
```

### 创建表格

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

### 创建面板

```python
# 创建面板
panel = ui.create_panel(
    "这是重要信息\n请仔细阅读",
    title="提示",
    border_style="info"
)
ui.print_panel(panel)
```

## 配置

### UI 配置文件

UI 系统的配置文件位于 `config/ui.yaml`：

```yaml
ui:
  colors:
    enabled: true
    theme: "default"
  
  icons:
    enabled: true
    style: "emoji"  # emoji, ascii, unicode, none
  
  display:
    max_width: 120
    page_size: 20
```

### 主题配置

支持以下内置主题：

- **default**: 默认主题，适合大多数终端
- **dark**: 深色主题，适合深色背景终端
- **light**: 浅色主题，适合浅色背景终端
- **minimal**: 极简主题，仅使用白色

### 图标风格

支持三种图标风格：

- **emoji**: 使用 Emoji 图标（✅ ❌ ⚠️）
- **ascii**: 使用 ASCII 字符（[OK] [X] [!]）
- **unicode**: 使用 Unicode 符号（✓ ✗ ⚠）
- **none**: 不显示图标

## 示例

### 运行演示

```bash
python examples/ui_demo.py
```

这将展示所有可用的 UI 功能。

### 在项目中使用

```python
from src.ui import UIManager, UIConfigLoader

# 从配置文件加载
config = UIConfigLoader.load_config()
ui = UIManager(config)

# 显示欢迎信息
ui.print_header("AI PowerShell 智能助手", "欢迎使用")

# 显示操作结果
ui.print_success("初始化完成")
```

## API 参考

### UIManager

主要的 UI 管理类。

#### 方法

- `print_success(message, icon=True)`: 打印成功消息
- `print_error(message, icon=True)`: 打印错误消息
- `print_warning(message, icon=True)`: 打印警告消息
- `print_info(message, icon=True)`: 打印信息消息
- `print_header(title, subtitle=None)`: 打印标题头部
- `create_table(title, show_header, show_lines, box_style)`: 创建表格
- `create_panel(content, title, border_style)`: 创建面板
- `print_list(items, title, numbered)`: 打印列表
- `print_dict(data, title)`: 打印字典
- `clear_screen()`: 清空屏幕

### ThemeManager

主题管理类。

#### 方法

- `get_color(element)`: 获取元素颜色
- `get_style(element)`: 获取元素样式
- `list_available_themes()`: 列出可用主题
- `switch_theme(theme_name)`: 切换主题
- `add_custom_theme(name, colors)`: 添加自定义主题

## 最佳实践

1. **一致性**: 在整个应用中使用一致的消息类型和样式
2. **可读性**: 使用适当的颜色和图标提高可读性
3. **可配置性**: 允许用户自定义 UI 设置
4. **降级支持**: 在不支持颜色的终端上提供降级方案

## 故障排除

### 颜色不显示

如果颜色不显示，请检查：

1. 终端是否支持 ANSI 颜色
2. `config/ui.yaml` 中 `colors.enabled` 是否为 `true`
3. 在 Windows 上，确保使用 Windows 10+ 或安装了 colorama

### 图标显示异常

如果图标显示为方块或问号：

1. 确保终端字体支持 Unicode/Emoji
2. 尝试切换到 ASCII 图标风格
3. 或禁用图标显示

## 下一步

- 查看 [开发计划](../.kiro/specs/cli-ux-optimization/tasks.md) 了解即将推出的功能
- 参与 [贡献](../README.md#贡献) 帮助改进 UI 系统
- 提交 [问题反馈](https://github.com/0green7hand0/AI-PowerShell/issues) 报告 bug 或建议新功能
