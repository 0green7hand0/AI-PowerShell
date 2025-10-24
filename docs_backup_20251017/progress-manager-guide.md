# 进度管理器使用指南

## 概述

进度管理器（ProgressManager）是 CLI 用户体验优化的核心组件之一，提供了丰富的进度指示功能，包括：

- **Spinner 加载动画** - 用于不确定时长的操作
- **进度条** - 用于可量化进度的操作
- **多任务并发** - 同时显示多个进度任务
- **上下文管理器** - 自动管理进度的开始和结束
- **异步进度更新** - 支持实时更新进度状态

## 快速开始

### 基本使用

```python
from src.ui import UIManager

# 创建 UI 管理器
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

### 使用 Spinner

```python
# 启动 spinner（用于不确定时长的操作）
pm.start_spinner("loading", "正在加载数据...")

# 执行操作
# ...

# 完成
pm.finish_progress("loading", success=True)
```

### 使用上下文管理器

```python
# 自动管理进度的开始和结束
with pm.progress_context("backup", "备份数据...", total=100) as progress:
    for i in range(100):
        # 执行任务
        progress.update_progress("backup", advance=1)
# 退出上下文时自动完成进度
```

## 核心功能

### 1. 启动进度任务

#### 启动进度条

```python
pm.start_progress(
    task_id="task1",           # 任务唯一标识
    description="处理中...",    # 任务描述
    total=100                   # 总步骤数
)
```

#### 启动 Spinner

```python
pm.start_spinner(
    task_id="task1",           # 任务唯一标识
    description="加载中..."     # 任务描述
)
```

### 2. 更新进度

#### 使用绝对值更新

```python
# 设置完成数量为 50
pm.update_progress("task1", completed=50)
```

#### 使用相对值更新

```python
# 前进 10 步
pm.update_progress("task1", advance=10)
```

#### 更新描述

```python
# 更新任务描述
pm.update_progress("task1", description="新的描述")
```

#### 组合更新

```python
# 同时更新进度和描述
pm.update_progress(
    "task1",
    completed=75,
    description="即将完成..."
)
```

### 3. 完成进度

```python
# 成功完成
pm.finish_progress("task1", success=True)

# 失败完成
pm.finish_progress("task1", success=False)
```

### 4. 多任务管理

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

### 5. 查询任务状态

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

### 6. 停止所有任务

```python
# 停止所有进度显示
pm.stop_all()
```

## 与其他模块集成

### 与 AI 引擎集成

AI 引擎的 `translate_natural_language` 方法支持进度回调：

```python
from src.ai_engine import AIEngine
from src.interfaces.base import Context

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

# 完成进度
pm.finish_progress("ai_translate", success=True)
```

### 与模板引擎集成

模板引擎的 `process_request` 方法支持进度回调：

```python
from src.template_engine import TemplateEngine

template_engine = TemplateEngine(config={})
pm = ui.progress_manager

# 启动进度
pm.start_progress("template", "模板处理中...", total=3)

# 定义进度回调
def progress_callback(step, total, description):
    pm.update_progress("template", completed=step, description=description)

# 处理请求
script = template_engine.process_request(
    "创建备份脚本",
    progress_callback=progress_callback
)

# 完成进度
pm.finish_progress("template", success=True)
```

### 与命令执行器集成

命令执行器的 `execute` 方法支持进度回调：

```python
from src.execution import CommandExecutor

executor = CommandExecutor()
pm = ui.progress_manager

# 启动 spinner
pm.start_spinner("execute", "执行命令中...")

# 定义进度回调
def progress_callback(description):
    pm.update_progress("execute", description=description)

# 执行命令
result = executor.execute(
    "Get-Process",
    progress_callback=progress_callback
)

# 完成进度
pm.finish_progress("execute", success=result.success)
```

## 配置选项

### 禁用进度功能

```python
from src.ui.models import UIConfig

# 创建禁用进度的配置
config = UIConfig(enable_progress=False)
ui = UIManager(config)
pm = ui.progress_manager

# 此时所有进度操作都不会显示
pm.start_progress("task1", "处理中...", total=100)  # 不会显示
```

### 自定义主题

进度管理器使用 UI 管理器的主题配置：

```python
from src.ui.models import UIConfig

# 使用暗色主题
config = UIConfig(theme="dark")
ui = UIManager(config)
pm = ui.progress_manager
```

## 最佳实践

### 1. 使用上下文管理器

推荐使用上下文管理器来自动管理进度的生命周期：

```python
# 推荐 ✓
with pm.progress_context("task1", "处理中", total=100) as progress:
    for i in range(100):
        progress.update_progress("task1", advance=1)

# 不推荐 ✗
pm.start_progress("task1", "处理中", total=100)
for i in range(100):
    pm.update_progress("task1", advance=1)
pm.finish_progress("task1")  # 容易忘记调用
```

### 2. 选择合适的进度类型

- **Spinner**: 用于不确定时长的操作（如网络请求、AI 处理）
- **进度条**: 用于可量化进度的操作（如文件处理、批量操作）

```python
# 不确定时长 - 使用 Spinner
pm.start_spinner("api_call", "调用 API...")

# 可量化进度 - 使用进度条
pm.start_progress("file_process", "处理文件", total=len(files))
```

### 3. 提供有意义的描述

```python
# 好的描述 ✓
pm.start_progress("backup", "备份 1000 个文件...", total=1000)
pm.update_progress("backup", completed=500, description="已备份 500/1000 个文件")

# 不好的描述 ✗
pm.start_progress("task", "处理中...", total=1000)
pm.update_progress("task", completed=500)
```

### 4. 及时清理任务

```python
try:
    pm.start_progress("task1", "处理中", total=100)
    # 执行任务
    pm.finish_progress("task1", success=True)
except Exception as e:
    pm.finish_progress("task1", success=False)
    raise
```

### 5. 避免过度更新

```python
# 好的做法 ✓ - 批量更新
for i in range(0, 1000, 10):
    # 处理 10 个项目
    pm.update_progress("task1", advance=10)

# 不好的做法 ✗ - 每次都更新
for i in range(1000):
    # 处理 1 个项目
    pm.update_progress("task1", advance=1)  # 太频繁
```

## 示例代码

完整的示例代码请参考：

- `examples/progress_demo.py` - 进度管理器功能演示
- `tests/ui/test_progress_manager.py` - 单元测试示例

## 故障排除

### 进度不显示

检查配置是否启用了进度功能：

```python
config = UIConfig(enable_progress=True)  # 确保为 True
ui = UIManager(config)
```

### 进度卡住不动

确保调用了 `finish_progress` 或使用上下文管理器：

```python
# 使用上下文管理器自动完成
with pm.progress_context("task1", "处理中", total=100) as progress:
    # ...
```

### 多个进度条重叠

确保每个任务使用唯一的 task_id：

```python
pm.start_progress("task1", "任务1", total=100)  # ✓
pm.start_progress("task2", "任务2", total=50)   # ✓
pm.start_progress("task1", "任务3", total=75)   # ✗ task_id 重复
```

## 相关文档

- [UI 系统指南](ui-system-guide.md)
- [主题管理器指南](theme-manager-guide.md)
- [错误处理指南](error-handler-guide.md)
