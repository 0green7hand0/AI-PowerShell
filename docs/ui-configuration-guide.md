# UI 配置指南

## 概述

本指南详细介绍如何配置和自定义 AI PowerShell 智能助手的用户界面系统。

## 配置文件位置

UI 配置文件位于 `config/ui.yaml`。如果文件不存在，系统将使用默认配置。

## 配置结构

### 基本配置

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

## 颜色和主题

### 内置主题

系统提供四种内置主题：

#### 1. Default（默认主题）

适合大多数终端环境，使用标准 ANSI 颜色。

```yaml
themes:
  default:
    success: "bold green"
    error: "bold red"
    warning: "bold yellow"
    info: "bold blue"
    primary: "bold cyan"
    secondary: "bold magenta"
    muted: "dim white"
    highlight: "bold bright_cyan"
```

#### 2. Dark（深色主题）

适合深色背景终端，使用更亮的颜色。

```yaml
themes:
  dark:
    success: "bold bright_green"
    error: "bold bright_red"
    warning: "bold bright_yellow"
    info: "bold bright_blue"
    primary: "bold bright_cyan"
    secondary: "bold bright_magenta"
    muted: "dim bright_white"
    highlight: "bold bright_cyan on black"
```

#### 3. Light（浅色主题）

适合浅色背景终端。

```yaml
themes:
  light:
    success: "bold green"
    error: "bold red"
    warning: "bold yellow"
    info: "bold blue"
    primary: "bold blue"
    secondary: "bold magenta"
    muted: "dim black"
    highlight: "bold blue on white"
```

#### 4. Minimal（极简主题）

仅使用白色，适合不支持颜色的终端。

```yaml
themes:
  minimal:
    success: "white"
    error: "white"
    warning: "white"
    info: "white"
    primary: "white"
    secondary: "white"
    muted: "dim white"
    highlight: "bold white"
```

### 自定义主题

您可以创建自己的主题：

```yaml
themes:
  my_custom_theme:
    success: "bold green"
    error: "bold red"
    warning: "bold yellow"
    info: "bold cyan"
    primary: "bold magenta"
    secondary: "bold blue"
    muted: "dim white"
    highlight: "bold white on blue"
```

然后在配置中使用：

```yaml
ui:
  colors:
    theme: "my_custom_theme"
```

### 颜色语法

颜色配置支持以下语法：

- **基本颜色**: `red`, `green`, `blue`, `yellow`, `cyan`, `magenta`, `white`, `black`
- **亮色**: `bright_red`, `bright_green`, 等
- **样式**: `bold`, `dim`, `italic`, `underline`
- **背景色**: `on red`, `on blue`, 等
- **组合**: `bold red on white`, `dim cyan`, 等

## 图标配置

### 图标风格

系统支持四种图标风格：

#### 1. Emoji（表情符号）

使用 Unicode Emoji，视觉效果最佳。

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

#### 2. ASCII（ASCII 字符）

使用纯 ASCII 字符，兼容性最好。

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

#### 3. Unicode（Unicode 符号）

使用 Unicode 符号，平衡美观和兼容性。

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

#### 4. None（无图标）

不显示图标，仅显示文本。

```yaml
ui:
  icons:
    enabled: false
```

## 进度指示器配置

### 启用/禁用进度指示

```yaml
ui:
  progress:
    enabled: true        # 启用进度指示
    animations: true     # 启用动画效果
```

### 进度指示器类型

系统会根据任务类型自动选择合适的进度指示器：

- **Spinner**: 用于不确定时长的任务
- **Progress Bar**: 用于可以跟踪进度的任务
- **Status**: 用于简单的状态显示

## 交互式输入配置

### 自动补全

```yaml
ui:
  input:
    auto_complete: true  # 启用命令自动补全
```

启用后，输入命令时按 `Tab` 键可以自动补全。

### 命令历史

```yaml
ui:
  input:
    history_enabled: true              # 启用历史记录
    history_size: 1000                 # 最多保存 1000 条
    history_file: ".ai_powershell_history"  # 历史文件名
```

启用后，可以使用上下箭头键浏览历史命令。

## 显示配置

### 宽度和分页

```yaml
ui:
  display:
    max_width: 120       # 最大显示宽度（字符）
    page_size: 20        # 每页显示行数
    auto_pager: true     # 自动分页长列表
```

### 表格样式

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

## 终端兼容性

### 自动检测

系统会自动检测终端能力并调整配置：

- 不支持颜色的终端：自动禁用颜色
- 不支持 Unicode 的终端：自动切换到 ASCII 图标
- 窄终端：自动调整显示宽度

### 手动配置

如果自动检测不准确，可以手动配置：

```yaml
ui:
  colors:
    enabled: false       # 强制禁用颜色
  icons:
    style: "ascii"       # 强制使用 ASCII 图标
```

## 配置示例

### 示例 1：极简配置

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

### 示例 2：完整功能配置

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

### 示例 3：性能优先配置

减少视觉效果以提高性能：

```yaml
ui:
  colors:
    enabled: true
    theme: "minimal"
  icons:
    enabled: false
  progress:
    enabled: true
    animations: false
  input:
    auto_complete: true
    history_enabled: true
  display:
    max_width: 100
    show_lines: false
    box_style: "minimal"
```

## 编程方式配置

### 使用 Python 代码

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

## 故障排除

### 颜色不显示

**问题**: 终端不显示颜色

**解决方案**:
1. 检查 `config/ui.yaml` 中 `colors.enabled` 是否为 `true`
2. 确认终端支持 ANSI 颜色
3. Windows 用户：确保使用 Windows 10+ 或安装 colorama
4. 尝试切换到 `minimal` 主题

### 图标显示为方块

**问题**: 图标显示为 □ 或 ?

**解决方案**:
1. 确认终端字体支持 Unicode/Emoji
2. 切换到 ASCII 图标风格：`style: "ascii"`
3. 或禁用图标：`enabled: false`

### 进度指示器闪烁

**问题**: 进度指示器显示不稳定

**解决方案**:
1. 禁用动画：`animations: false`
2. 或完全禁用进度指示：`progress.enabled: false`

### 自动补全不工作

**问题**: 按 Tab 键没有反应

**解决方案**:
1. 检查 `input.auto_complete` 是否为 `true`
2. 确认使用交互模式：`python src/main.py --interactive`
3. 检查终端是否支持 readline

## 最佳实践

1. **测试配置**: 修改配置后运行 `python examples/ui_demo.py` 测试效果
2. **备份配置**: 修改前备份 `config/ui.yaml`
3. **渐进式启用**: 从基本功能开始，逐步启用高级功能
4. **考虑用户**: 如果分发给其他用户，使用保守的默认配置
5. **文档化定制**: 如果创建自定义主题，添加注释说明用途

## 相关文档

- [CLI UI 系统指南](ui-system-guide.md) - UI 系统使用说明
- [进度管理器指南](progress-manager-guide.md) - 进度指示详细说明
- [启动体验指南](startup-experience-guide.md) - 启动流程配置

## 反馈和支持

如有问题或建议，请：
- 查看 [常见问题](常见问题.md)
- 提交 [Issue](https://github.com/0green7hand0/AI-PowerShell/issues)
- 参与 [讨论](https://github.com/0green7hand0/AI-PowerShell/discussions)
