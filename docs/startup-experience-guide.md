# 启动体验优化指南

## 概述

启动体验优化模块提供了完整的首次启动向导、系统检查和交互模式启动体验增强功能。

## 主要组件

### 1. StartupWizard (启动向导)

位置: `src/ui/startup_wizard.py`

**功能:**
- 首次运行检测
- 系统环境检查
- 配置问题自动检测和修复
- 欢迎向导流程

**系统检查项:**
- Python 版本检查
- PowerShell 可用性检查
- 配置文件完整性检查
- 日志目录检查
- 模板目录检查
- 存储目录检查
- 依赖包检查

**使用示例:**

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

### 2. StartupExperience (启动体验)

位置: `src/ui/startup_experience.py`

**功能:**
- 启动序列管理
- 功能概览显示
- 快速使用提示
- 就绪状态指示
- 会话摘要显示

**使用示例:**

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

### 3. StartupPerformanceOptimizer (性能优化器)

位置: `src/ui/startup_experience.py`

**功能:**
- 延迟导入重型模块
- 预加载常用数据
- 缓存系统信息

## 集成到主程序

启动体验已集成到 `src/main.py` 的 `interactive_mode()` 方法中:

```python
def interactive_mode(self):
    # 启动新会话
    self.context_manager.start_session()
    session_start_time = time.time()
    
    # 运行启动体验
    from src.ui.startup_experience import StartupExperience
    startup = StartupExperience()
    startup_success = startup.run_startup_sequence()
    
    # ... 交互循环 ...
    
    # 显示会话摘要
    session_duration = time.time() - session_start_time
    startup.display_session_summary({
        'commands_executed': commands_executed,
        'successful_commands': successful_commands,
        'failed_commands': failed_commands,
        'session_duration': session_duration,
    })
```

## 首次运行流程

1. **检测首次运行**: 检查 `.ai_powershell_initialized` 标记文件
2. **显示欢迎信息**: 展示欢迎横幅和程序介绍
3. **运行系统检查**: 执行完整的系统环境检查
4. **显示检查结果**: 以表格形式展示所有检查项
5. **自动修复问题**: 询问用户是否修复可修复的问题
6. **标记已初始化**: 创建标记文件，避免重复运行

## 常规启动流程

1. **快速系统检查**: 仅检查关键项（Python、配置、日志）
2. **显示启动横幅**: 展示程序标题和版本
3. **显示功能概览**: 列出主要功能
4. **显示快速提示**: 提供使用建议
5. **显示就绪状态**: 显示启动耗时和就绪消息

## 系统检查状态

- **PASSED** (✓): 检查通过
- **WARNING** (⚠): 有警告但不影响运行
- **FAILED** (✗): 检查失败，可能影响功能
- **SKIPPED** (-): 跳过检查

## 自动修复功能

支持自动修复的问题:
- 创建缺失的配置目录
- 创建缺失的日志目录
- 创建缺失的模板目录
- 创建缺失的存储目录

不支持自动修复的问题:
- Python 版本过低
- PowerShell 未安装
- 依赖包缺失（需要手动运行 pip install）

## 配置选项

可以通过 `config/ui.yaml` 配置启动体验:

```yaml
ui:
  startup:
    show_welcome: true
    run_system_check: true
    auto_fix_issues: false
    show_feature_overview: true
    show_quick_tips: true
```

## 性能优化

启动性能优化策略:
1. **延迟导入**: 仅在需要时导入重型模块
2. **快速检查**: 常规启动仅检查关键项
3. **缓存信息**: 缓存系统信息避免重复检查
4. **并行检查**: 可能的情况下并行执行检查

## 测试

运行测试:

```bash
# 测试启动向导
python -m pytest tests/ui/test_startup_wizard.py -v

# 测试启动体验
python -m pytest tests/ui/test_startup_experience.py -v

# 运行演示
python examples/startup_demo.py
```

## 故障排除

### 问题: 首次运行向导重复出现

**解决方案**: 删除 `.ai_powershell_initialized` 文件会触发首次运行向导。如果不想再次运行，确保该文件存在。

### 问题: 系统检查失败

**解决方案**: 
1. 查看具体的失败项
2. 根据提示修复问题
3. 使用自动修复功能（如果可用）
4. 手动创建缺失的目录或安装依赖

### 问题: 启动速度慢

**解决方案**:
1. 跳过首次运行向导: `startup.run_startup_sequence(skip_wizard=True)`
2. 使用快速检查而非完整检查
3. 禁用不必要的检查项

## 最佳实践

1. **首次运行**: 让用户完成首次运行向导，确保环境正确配置
2. **常规启动**: 使用快速检查，提供良好的启动体验
3. **错误处理**: 即使检查失败也允许程序继续运行
4. **用户反馈**: 清晰地显示检查结果和修复建议
5. **性能优化**: 避免在启动时执行耗时操作

## 扩展

可以通过以下方式扩展启动体验:

1. **添加新的检查项**: 在 `StartupWizard` 中添加新的 `_check_*` 方法
2. **自定义修复逻辑**: 在 `_fix_issues` 方法中添加新的修复命令
3. **自定义启动流程**: 继承 `StartupExperience` 并重写相关方法
4. **添加配置选项**: 在 `config/ui.yaml` 中添加新的配置项

## 相关文档

- [UI 系统指南](ui-system-guide.md)
- [进度管理器指南](progress-manager-guide.md)
- [错误处理指南](../src/ui/error_handler.py)
