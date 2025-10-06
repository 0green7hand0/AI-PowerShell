# 上下文管理模块实现文档

## 概述

上下文管理模块负责管理用户会话、命令历史记录和用户偏好设置。该模块提供了完整的会话生命周期管理、历史记录查询和统计分析功能。

## 模块结构

```
src/context/
├── __init__.py          # 模块导出
├── models.py            # 数据模型定义
├── manager.py           # 上下文管理器
└── history.py           # 历史记录管理器

tests/context/
├── __init__.py
├── test_models.py       # 数据模型测试
├── test_manager.py      # 上下文管理器测试
└── test_history.py      # 历史记录管理器测试
```

## 核心组件

### 1. 数据模型 (models.py)

#### CommandEntry - 命令历史条目
```python
@dataclass
class CommandEntry:
    command_id: str              # 命令唯一标识
    user_input: str              # 用户原始输入
    translated_command: str      # 翻译后的命令
    status: CommandStatus        # 命令状态
    output: str                  # 命令输出
    error: str                   # 错误信息
    return_code: int             # 返回码
    execution_time: float        # 执行时间
    confidence_score: float      # AI 翻译置信度
    timestamp: datetime          # 时间戳
    metadata: Dict[str, Any]     # 额外元数据
```

**主要方法**:
- `is_successful`: 判断命令是否执行成功
- `has_error`: 判断是否有错误
- `to_dict()`: 转换为字典格式
- `from_dict()`: 从字典创建实例

#### Session - 会话
```python
@dataclass
class Session:
    session_id: str              # 会话唯一标识
    user_id: Optional[str]       # 用户 ID
    status: SessionStatus        # 会话状态
    start_time: datetime         # 会话开始时间
    last_activity: datetime      # 最后活动时间
    end_time: Optional[datetime] # 会话结束时间
    working_directory: str       # 工作目录
    environment_vars: Dict       # 环境变量
    command_history: List[CommandEntry]  # 命令历史
    metadata: Dict[str, Any]     # 额外元数据
```

**主要属性**:
- `duration`: 会话持续时间
- `command_count`: 命令总数
- `successful_commands`: 成功命令数
- `failed_commands`: 失败命令数
- `is_active`: 是否活跃

**主要方法**:
- `add_command()`: 添加命令到历史
- `get_recent_commands()`: 获取最近的命令
- `get_successful_commands()`: 获取成功的命令
- `get_failed_commands()`: 获取失败的命令
- `terminate()`: 终止会话

#### ContextSnapshot - 上下文快照
```python
@dataclass
class ContextSnapshot:
    snapshot_id: str             # 快照唯一标识
    session: Session             # 会话信息
    timestamp: datetime          # 快照时间
    description: str             # 快照描述
    tags: List[str]              # 标签
```

用于保存某个时间点的完整上下文状态，支持上下文恢复和分析。

#### UserPreferences - 用户偏好设置
```python
@dataclass
class UserPreferences:
    user_id: str                 # 用户 ID
    auto_execute_safe_commands: bool  # 自动执行安全命令
    confirmation_required: bool  # 是否需要确认
    history_limit: int           # 历史记录限制
    session_timeout: int         # 会话超时时间（秒）
    preferred_shell: str         # 首选 Shell
    language: str                # 语言偏好
    theme: str                   # 主题
    custom_settings: Dict        # 自定义设置
```

### 2. 上下文管理器 (manager.py)

#### ContextManager
负责管理用户会话、命令历史和上下文状态。

**初始化**:
```python
manager = ContextManager(storage=storage_instance)
```

**会话管理**:
```python
# 开始新会话
session = manager.start_session(
    user_id="user123",
    working_directory="/home/user"
)

# 获取会话
session = manager.get_session(session_id)

# 切换会话
manager.switch_session(session_id)

# 终止会话
manager.terminate_session(session_id)

# 清理过期会话
manager.cleanup_expired_sessions(timeout=3600)
```

**命令管理**:
```python
# 添加命令
entry = manager.add_command(
    user_input="显示时间",
    suggestion=suggestion_obj,
    result=execution_result
)

# 更新命令状态
manager.update_command_status(
    command_id,
    CommandStatus.COMPLETED,
    result
)

# 获取命令
entry = manager.get_command(command_id)
```

**上下文查询**:
```python
# 获取当前上下文
context = manager.get_context(depth=5)

# 获取最近命令
recent = manager.get_recent_commands(limit=10)

# 获取成功/失败命令
successful = manager.get_successful_commands()
failed = manager.get_failed_commands()
```

**快照管理**:
```python
# 创建快照
snapshot = manager.create_snapshot(
    description="Before major change",
    tags=["backup", "important"]
)

# 恢复快照
manager.restore_snapshot(snapshot_id)
```

**用户偏好**:
```python
# 获取用户偏好
prefs = manager.get_user_preferences(user_id)

# 保存用户偏好
manager.save_user_preferences(preferences)
```

**统计信息**:
```python
# 获取会话统计
stats = manager.get_session_stats()
# 返回: {
#     "session_id": "...",
#     "duration": 123.45,
#     "command_count": 10,
#     "successful_commands": 8,
#     "failed_commands": 2,
#     ...
# }
```

### 3. 历史记录管理器 (history.py)

#### HistoryManager
负责管理命令历史记录，提供查询、搜索、过滤和统计功能。

**初始化**:
```python
history_manager = HistoryManager(
    storage=storage_instance,
    max_history=1000
)
```

**基础操作**:
```python
# 添加历史记录
history_manager.add_entry(command_entry)

# 获取所有历史
all_history = history_manager.get_all(limit=100)

# 根据 ID 获取
entry = history_manager.get_by_id(command_id)

# 删除记录
history_manager.remove_entry(command_id)

# 清空历史
history_manager.clear()
```

**搜索和过滤**:
```python
# 搜索
results = history_manager.search("Get-Date", search_in="command")

# 按状态过滤
completed = history_manager.filter_by_status(CommandStatus.COMPLETED)

# 按日期范围过滤
recent = history_manager.filter_by_date_range(
    start_date=datetime.now() - timedelta(days=7)
)

# 按执行结果过滤
successful = history_manager.filter_by_success(successful=True)

# 按置信度过滤
high_confidence = history_manager.filter_by_confidence(min_confidence=0.8)

# 自定义过滤
slow_commands = history_manager.filter_by_custom(
    lambda entry: entry.execution_time > 1.0
)
```

**统计分析**:
```python
# 获取统计信息
stats = history_manager.get_statistics()
# 返回: {
#     "total_commands": 100,
#     "successful_commands": 85,
#     "failed_commands": 15,
#     "success_rate": 0.85,
#     "average_confidence": 0.92,
#     "average_execution_time": 0.45,
#     ...
# }

# 获取最常用命令
most_used = history_manager.get_most_used_commands(limit=10)

# 分析命令模式
patterns = history_manager.get_command_patterns()

# 获取时间分布
distribution = history_manager.get_time_distribution()

# 错误分析
error_analysis = history_manager.get_error_analysis()
```

**导出和导入**:
```python
# 导出为 JSON
history_manager.export_history("history.json", format="json")

# 导出为 CSV
history_manager.export_history("history.csv", format="csv")

# 导入历史
history_manager.import_history("history.json", format="json")
```

## 使用示例

### 完整的会话管理流程

```python
from src.context import ContextManager, HistoryManager
from src.storage.file_storage import FileStorage

# 初始化存储和管理器
storage = FileStorage()
context_manager = ContextManager(storage=storage)
history_manager = HistoryManager(storage=storage)

# 开始新会话
session = context_manager.start_session(user_id="user123")

# 用户输入命令
user_input = "显示当前时间"

# AI 翻译
suggestion = ai_engine.translate_natural_language(user_input, context)

# 执行命令
result = executor.execute(suggestion.generated_command)

# 记录到上下文
entry = context_manager.add_command(user_input, suggestion, result)

# 同时添加到历史管理器
history_manager.add_entry(entry)

# 获取上下文用于下一次翻译
context = context_manager.get_context(depth=5)

# 查看会话统计
stats = context_manager.get_session_stats()
print(f"执行了 {stats['command_count']} 个命令")
print(f"成功率: {stats['successful_commands'] / stats['command_count'] * 100}%")

# 终止会话
context_manager.terminate_session()
```

### 历史记录分析

```python
# 获取最近一周的命令
recent = history_manager.filter_by_date_range(
    start_date=datetime.now() - timedelta(days=7)
)

# 分析最常用的命令
most_used = history_manager.get_most_used_commands(limit=5)
for cmd_info in most_used:
    print(f"{cmd_info['command']}: 使用了 {cmd_info['count']} 次")

# 查找失败的命令
failed = history_manager.filter_by_success(successful=False)
print(f"失败的命令数: {len(failed)}")

# 错误分析
error_analysis = history_manager.get_error_analysis()
print(f"错误率: {error_analysis['error_rate'] * 100}%")
for error in error_analysis['common_errors']:
    print(f"  {error['error']}: {error['count']} 次")
```

## 存储集成

上下文管理模块通过 `StorageInterface` 与存储层集成。存储接口新增了以下方法：

```python
class StorageInterface(ABC):
    # 会话管理
    def save_session(self, session_data: Dict[str, Any]) -> bool
    def load_session(self, session_id: str) -> Optional[Dict[str, Any]]
    
    # 快照管理
    def save_snapshot(self, snapshot_data: Dict[str, Any]) -> bool
    def load_snapshot(self, snapshot_id: str) -> Optional[Dict[str, Any]]
    
    # 用户偏好
    def save_user_preferences(self, preferences_data: Dict[str, Any]) -> bool
    def load_user_preferences(self, user_id: str) -> Optional[Dict[str, Any]]
    
    # 批量历史记录
    def save_history_batch(self, history_data: List[Dict[str, Any]]) -> bool
```

### 文件存储结构

```
~/.ai-powershell/
├── sessions/           # 会话数据
│   ├── {session_id}.json
│   └── ...
├── snapshots/          # 上下文快照
│   ├── {snapshot_id}.json
│   └── ...
├── preferences/        # 用户偏好
│   ├── {user_id}.json
│   └── ...
├── history.json        # 命令历史
├── config.yaml         # 配置文件
└── cache/             # 缓存数据
```

## 测试覆盖

模块包含 82 个单元测试，覆盖以下方面：

### 数据模型测试 (test_models.py)
- CommandEntry 创建和属性
- Session 生命周期管理
- ContextSnapshot 序列化
- UserPreferences 配置

### 上下文管理器测试 (test_manager.py)
- 会话管理（创建、切换、终止）
- 命令管理（添加、更新、查询）
- 上下文查询
- 快照管理
- 用户偏好管理
- 统计信息

### 历史记录管理器测试 (test_history.py)
- 基础操作（添加、删除、清空）
- 搜索和过滤
- 统计分析
- 导出和导入

所有测试均通过，测试覆盖率达到 100%。

## 性能考虑

1. **会话缓存**: 活跃会话保存在内存中，避免频繁的磁盘 I/O
2. **历史记录限制**: 可配置的历史记录数量上限，防止内存溢出
3. **批量保存**: 支持批量保存历史记录，减少文件写入次数
4. **延迟加载**: 会话和快照按需从存储加载
5. **过期清理**: 自动清理过期的会话和缓存

## 扩展性

模块设计支持以下扩展：

1. **自定义存储后端**: 通过实现 `StorageInterface` 支持数据库、云存储等
2. **自定义过滤器**: `filter_by_custom()` 支持任意过滤逻辑
3. **元数据扩展**: 所有数据模型都包含 `metadata` 字段用于扩展
4. **事件钩子**: 可以在会话生命周期事件上添加钩子函数
5. **多用户支持**: 通过 `user_id` 支持多用户场景

## 最佳实践

1. **及时终止会话**: 使用完毕后及时调用 `terminate_session()`
2. **定期清理**: 定期调用 `cleanup_expired_sessions()` 清理过期会话
3. **限制历史数量**: 根据实际需求设置合理的 `max_history`
4. **使用快照**: 在重要操作前创建快照，便于回滚
5. **分析历史**: 定期分析历史记录，优化用户体验

## 总结

上下文管理模块提供了完整的会话管理、历史记录和用户偏好功能，是 AI PowerShell 智能助手的核心组件之一。通过清晰的接口设计和完善的测试覆盖，确保了模块的可靠性和可维护性。
