<!-- 文档类型: 参考文档 | 最后更新: 2025-10-17 | 维护者: 项目团队 -->

# AI PowerShell 智能助手 - API 参考文档

> **文档类型**: 参考文档 | **最后更新**: 2025-10-17 | **维护者**: 项目团队

📍 [首页](../README.md) > [文档中心](README.md) > API 参考文档

## 📋 目录

- [概述](#概述)
- [AI 引擎 API](#ai-引擎-api)
- [安全引擎 API](#安全引擎-api)
- [执行引擎 API](#执行引擎-api)
- [配置管理 API](#配置管理-api)
- [日志引擎 API](#日志引擎-api)
- [存储引擎 API](#存储引擎-api)
- [上下文管理 API](#上下文管理-api)
- [数据模型](#数据模型)
- [接口定义](#接口定义)

---

## 概述

本文档提供 AI PowerShell 智能助手所有核心模块的 API 参考。每个 API 包含函数签名、参数说明、返回值和使用示例。

### 模块索引

| 模块 | 位置 | 主要功能 |
|------|------|---------|
| AI 引擎 | `src/ai_engine/` | 自然语言翻译、命令生成 |
| 安全引擎 | `src/security/` | 三层安全验证、风险评估 |
| 执行引擎 | `src/execution/` | PowerShell 命令执行 |
| 配置管理 | `src/config/` | 配置加载、验证、保存 |
| 日志引擎 | `src/log_engine/` | 结构化日志、关联追踪 |
| 存储引擎 | `src/storage/` | 数据持久化、缓存管理 |
| 上下文管理 | `src/context/` | 会话管理、历史记录 |

---

## AI 引擎 API

### AIEngine

**位置**: `src/ai_engine/engine.py`

AI 引擎主类，负责协调自然语言到 PowerShell 命令的翻译流程。

#### 构造函数

```python
def __init__(self, config: Optional[Dict] = None)
```

**参数**:
- `config` (Optional[Dict]): AI 引擎配置字典
  - `cache_max_size` (int): 缓存最大条目数，默认 100
  - `cache_ttl` (int): 缓存过期时间（秒），默认 3600
  - `provider` (str): AI 提供商 (local, ollama, openai, azure)
  - `model_name` (str): AI 模型名称

**示例**:
```python
from src.ai_engine.engine import AIEngine

config = {
    'cache_max_size': 200,
    'cache_ttl': 7200,
    'provider': 'ollama',
    'model_name': 'llama2'
}
ai_engine = AIEngine(config)
```


#### translate_natural_language()

```python
def translate_natural_language(
    self, 
    text: str, 
    context: Context,
    progress_callback=None
) -> Suggestion
```

将自然语言翻译为 PowerShell 命令。

**参数**:
- `text` (str): 用户输入的自然语言文本
- `context` (Context): 当前上下文信息
- `progress_callback` (Optional[Callable]): 进度回调函数，接收 (step, total, description) 参数

**返回值**:
- `Suggestion`: 包含生成命令和相关信息的建议对象

**异常**:
- `ValueError`: 当输入文本为空或无效时
- `RuntimeError`: 当 AI 引擎不可用时

**示例**:
```python
from src.interfaces.base import Context

context = Context(session_id="session-123", working_directory="/home/user")
suggestion = ai_engine.translate_natural_language("显示当前时间", context)

print(f"生成的命令: {suggestion.generated_command}")
print(f"置信度: {suggestion.confidence_score}")
print(f"解释: {suggestion.explanation}")
```

#### validate_command()

```python
def validate_command(self, command: str) -> bool
```

验证生成的命令是否有效。

**参数**:
- `command` (str): 待验证的 PowerShell 命令

**返回值**:
- `bool`: 命令是否有效

**示例**:
```python
is_valid = ai_engine.validate_command("Get-Date")
print(f"命令有效: {is_valid}")
```


#### get_command_explanation()

```python
def get_command_explanation(self, command: str) -> str
```

获取命令的详细解释。

**参数**:
- `command` (str): PowerShell 命令

**返回值**:
- `str`: 命令的详细解释

**示例**:
```python
explanation = ai_engine.get_command_explanation("Get-Process | Where-Object CPU -gt 100")
print(explanation)
```

#### clear_cache()

```python
def clear_cache(self)
```

清空翻译缓存。

**示例**:
```python
ai_engine.clear_cache()
```

#### get_cache_stats()

```python
def get_cache_stats(self) -> Dict[str, int]
```

获取缓存统计信息。

**返回值**:
- `Dict[str, int]`: 包含缓存大小等统计信息
  - `size`: 当前缓存条目数
  - `max_size`: 最大缓存条目数

**示例**:
```python
stats = ai_engine.get_cache_stats()
print(f"缓存使用: {stats['size']}/{stats['max_size']}")
```

---


## 安全引擎 API

### SecurityEngine

**位置**: `src/security/engine.py`

安全引擎主类，实现三层安全验证机制。

#### 构造函数

```python
def __init__(self, config: Optional[dict] = None)
```

**参数**:
- `config` (Optional[dict]): 安全配置字典
  - `whitelist_mode` (str): 白名单模式 ("strict", "moderate", "permissive")
  - `require_confirmation` (bool): 是否需要用户确认
  - `sandbox_enabled` (bool): 是否启用沙箱执行

**示例**:
```python
from src.security.engine import SecurityEngine

config = {
    'whitelist_mode': 'strict',
    'require_confirmation': True,
    'sandbox_enabled': False
}
security_engine = SecurityEngine(config)
```

#### validate_command()

```python
def validate_command(self, command: str, context: Context) -> ValidationResult
```

验证命令的安全性（三层验证）。

**参数**:
- `command` (str): 待验证的 PowerShell 命令
- `context` (Context): 当前上下文信息

**返回值**:
- `ValidationResult`: 包含验证结果和风险评估的对象

**示例**:
```python
from src.interfaces.base import Context

context = Context(session_id="session-123")
result = security_engine.validate_command("Get-Process", context)

print(f"验证通过: {result.is_valid}")
print(f"风险等级: {result.risk_level.value}")
print(f"需要确认: {result.requires_confirmation}")
```


#### check_permissions()

```python
def check_permissions(self, command: str) -> bool
```

检查命令所需的权限。

**参数**:
- `command` (str): PowerShell 命令

**返回值**:
- `bool`: 当前用户是否有足够权限执行该命令

**示例**:
```python
has_permission = security_engine.check_permissions("Stop-Service")
if not has_permission:
    print("需要管理员权限")
```

#### is_dangerous_command()

```python
def is_dangerous_command(self, command: str) -> bool
```

判断命令是否危险。

**参数**:
- `command` (str): PowerShell 命令

**返回值**:
- `bool`: 命令是否被认为是危险的

**示例**:
```python
if security_engine.is_dangerous_command("Remove-Item -Recurse C:\\"):
    print("警告: 这是一个危险命令!")
```

#### get_user_confirmation()

```python
def get_user_confirmation(self, command: str, risk_level: RiskLevel) -> bool
```

获取用户确认。

**参数**:
- `command` (str): 待执行的命令
- `risk_level` (RiskLevel): 风险等级

**返回值**:
- `bool`: 用户是否确认执行

**示例**:
```python
from src.interfaces.base import RiskLevel

confirmed = security_engine.get_user_confirmation(
    "Stop-Computer", 
    RiskLevel.HIGH
)
if confirmed:
    print("用户已确认执行")
```

---


## 执行引擎 API

### CommandExecutor

**位置**: `src/execution/executor.py`

命令执行器主类，负责 PowerShell 命令的实际执行。

#### 构造函数

```python
def __init__(self, config: Optional[dict] = None)
```

**参数**:
- `config` (Optional[dict]): 配置字典
  - `encoding` (str): 输出编码格式，默认 "utf-8"
  - `timeout` (int): 默认超时时间（秒），默认 30

**示例**:
```python
from src.execution.executor import CommandExecutor

config = {
    'encoding': 'utf-8',
    'timeout': 60
}
executor = CommandExecutor(config)
```

#### execute()

```python
def execute(
    self, 
    command: str, 
    timeout: Optional[int] = None,
    progress_callback=None
) -> ExecutionResult
```

执行 PowerShell 命令（同步）。

**参数**:
- `command` (str): 要执行的 PowerShell 命令
- `timeout` (Optional[int]): 超时时间（秒），如果为 None 则使用默认超时时间
- `progress_callback` (Optional[Callable]): 进度回调函数

**返回值**:
- `ExecutionResult`: 包含执行结果的对象

**异常**:
- `RuntimeError`: 当 PowerShell 不可用时

**示例**:
```python
result = executor.execute("Get-Date", timeout=10)

if result.success:
    print(f"输出: {result.output}")
    print(f"执行时间: {result.execution_time:.3f}秒")
else:
    print(f"错误: {result.error}")
    print(f"返回码: {result.return_code}")
```


#### execute_async()

```python
async def execute_async(
    self, 
    command: str, 
    timeout: Optional[int] = None
) -> ExecutionResult
```

异步执行 PowerShell 命令。

**参数**:
- `command` (str): 要执行的 PowerShell 命令
- `timeout` (Optional[int]): 超时时间（秒）

**返回值**:
- `ExecutionResult`: 包含执行结果的对象

**示例**:
```python
import asyncio

async def run_command():
    result = await executor.execute_async("Get-Process")
    print(result.output)

asyncio.run(run_command())
```

#### is_available()

```python
def is_available(self) -> bool
```

检查 PowerShell 是否可用。

**返回值**:
- `bool`: PowerShell 是否在系统中可用

**示例**:
```python
if executor.is_available():
    print("PowerShell 可用")
else:
    print("请安装 PowerShell")
```

#### get_powershell_version()

```python
def get_powershell_version(self) -> Optional[str]
```

获取 PowerShell 版本信息。

**返回值**:
- `Optional[str]`: PowerShell 版本字符串，如果不可用则返回 None

**示例**:
```python
version = executor.get_powershell_version()
print(f"PowerShell 版本: {version}")
```


#### execute_script_file()

```python
def execute_script_file(
    self, 
    script_path: str, 
    timeout: Optional[int] = None
) -> ExecutionResult
```

执行 PowerShell 脚本文件。

**参数**:
- `script_path` (str): 脚本文件路径
- `timeout` (Optional[int]): 超时时间（秒）

**返回值**:
- `ExecutionResult`: 执行结果

**示例**:
```python
result = executor.execute_script_file("./scripts/backup.ps1", timeout=120)
if result.success:
    print("脚本执行成功")
```

---

## 配置管理 API

### ConfigManager

**位置**: `src/config/manager.py`

配置管理器类，负责加载、验证和管理应用配置。

#### 构造函数

```python
def __init__(self, config_path: Optional[str] = None)
```

**参数**:
- `config_path` (Optional[str]): 配置文件路径，如果为 None 则使用默认路径

**示例**:
```python
from src.config.manager import ConfigManager

# 使用默认配置路径
config_manager = ConfigManager()

# 使用自定义配置路径
config_manager = ConfigManager("./my-config.yaml")
```


#### load_config()

```python
def load_config(self, config_path: Optional[str] = None) -> AppConfig
```

加载配置文件。

**参数**:
- `config_path` (Optional[str]): 配置文件路径

**返回值**:
- `AppConfig`: 应用配置对象

**异常**:
- `FileNotFoundError`: 配置文件不存在
- `ValidationError`: 配置验证失败
- `yaml.YAMLError`: YAML 解析失败

**示例**:
```python
config = config_manager.load_config("config/custom.yaml")
print(f"AI 提供商: {config.ai.provider}")
print(f"日志级别: {config.logging.level}")
```

#### save_config()

```python
def save_config(self, config: AppConfig, file_path: Optional[str] = None) -> None
```

保存配置到文件。

**参数**:
- `config` (AppConfig): 应用配置对象
- `file_path` (Optional[str]): 保存路径，如果为 None 则使用当前配置路径

**示例**:
```python
config = config_manager.get_config()
config.ai.temperature = 0.8
config_manager.save_config(config, "config/updated.yaml")
```

#### update_config()

```python
def update_config(self, updates: Dict[str, Any]) -> AppConfig
```

更新配置。

**参数**:
- `updates` (Dict[str, Any]): 要更新的配置项字典

**返回值**:
- `AppConfig`: 更新后的配置对象

**示例**:
```python
updated_config = config_manager.update_config({
    'ai': {'temperature': 0.9},
    'security': {'require_confirmation': False}
})
```


#### get_config()

```python
def get_config(self) -> AppConfig
```

获取当前配置。

**返回值**:
- `AppConfig`: 应用配置对象

**示例**:
```python
config = config_manager.get_config()
print(f"超时时间: {config.execution.timeout}秒")
```

#### reset_to_defaults()

```python
def reset_to_defaults(self) -> AppConfig
```

重置为默认配置。

**返回值**:
- `AppConfig`: 默认配置对象

**示例**:
```python
default_config = config_manager.reset_to_defaults()
```

#### validate_config()

```python
def validate_config(self, config_data: Dict[str, Any]) -> tuple[bool, Optional[str]]
```

验证配置数据。

**参数**:
- `config_data` (Dict[str, Any]): 配置数据字典

**返回值**:
- `tuple[bool, Optional[str]]`: (是否有效, 错误信息)

**示例**:
```python
config_data = {'ai': {'provider': 'ollama'}}
is_valid, error = config_manager.validate_config(config_data)
if not is_valid:
    print(f"配置无效: {error}")
```

---


## 日志引擎 API

### LogEngine

**位置**: `src/log_engine/engine.py`

日志引擎主类，提供结构化日志记录和关联追踪功能。

#### 构造函数

```python
def __init__(self, config: LoggingConfig)
```

**参数**:
- `config` (LoggingConfig): 日志配置对象

**示例**:
```python
from src.log_engine.engine import LogEngine
from src.config.models import LoggingConfig

log_config = LoggingConfig(
    level="INFO",
    file="logs/app.log",
    console_output=True
)
log_engine = LogEngine(log_config)
```

#### start_correlation()

```python
def start_correlation(self, correlation_id: Optional[str] = None) -> str
```

开始一个新的关联追踪。

**参数**:
- `correlation_id` (Optional[str]): 可选的关联 ID，如果不提供则自动生成

**返回值**:
- `str`: 关联 ID

**示例**:
```python
correlation_id = log_engine.start_correlation()
print(f"关联 ID: {correlation_id}")
```

#### get_correlation_id()

```python
def get_correlation_id(self) -> Optional[str]
```

获取当前的关联 ID。

**返回值**:
- `Optional[str]`: 当前关联 ID，如果没有则返回 None

**示例**:
```python
current_id = log_engine.get_correlation_id()
```


#### end_correlation()

```python
def end_correlation(self)
```

结束当前的关联追踪。

**示例**:
```python
log_engine.end_correlation()
```

#### info()

```python
def info(self, message: str, **kwargs)
```

记录 INFO 级别日志。

**参数**:
- `message` (str): 日志消息
- `**kwargs`: 额外的上下文信息

**示例**:
```python
log_engine.info("用户登录成功", user_id="user123", ip="192.168.1.1")
```

#### warning()

```python
def warning(self, message: str, **kwargs)
```

记录 WARNING 级别日志。

**参数**:
- `message` (str): 日志消息
- `**kwargs`: 额外的上下文信息

**示例**:
```python
log_engine.warning("缓存即将满", cache_size=950, max_size=1000)
```

#### error()

```python
def error(self, message: str, exc_info: bool = False, **kwargs)
```

记录 ERROR 级别日志。

**参数**:
- `message` (str): 日志消息
- `exc_info` (bool): 是否包含异常信息
- `**kwargs`: 额外的上下文信息

**示例**:
```python
try:
    # 某些操作
    pass
except Exception as e:
    log_engine.error("操作失败", exc_info=True, operation="backup")
```


#### log_request()

```python
def log_request(self, user_input: str, **kwargs)
```

记录用户请求。

**参数**:
- `user_input` (str): 用户输入
- `**kwargs`: 额外的上下文信息

**示例**:
```python
log_engine.log_request("显示当前时间", session_id="session-123")
```

#### log_translation()

```python
def log_translation(self, input_text: str, command: str, confidence: float, **kwargs)
```

记录 AI 翻译。

**参数**:
- `input_text` (str): 输入文本
- `command` (str): 生成的命令
- `confidence` (float): 置信度
- `**kwargs`: 额外的上下文信息

**示例**:
```python
log_engine.log_translation(
    "显示进程", 
    "Get-Process", 
    0.95,
    provider="ollama"
)
```

#### log_execution()

```python
def log_execution(
    self, 
    command: str, 
    success: bool, 
    return_code: int = 0, 
    execution_time: float = 0.0, 
    **kwargs
)
```

记录命令执行。

**参数**:
- `command` (str): 执行的命令
- `success` (bool): 是否成功
- `return_code` (int): 返回码
- `execution_time` (float): 执行时间（秒）
- `**kwargs`: 额外的上下文信息

**示例**:
```python
log_engine.log_execution(
    "Get-Date", 
    True, 
    return_code=0, 
    execution_time=0.123
)
```

---


## 存储引擎 API

### StorageInterface

**位置**: `src/storage/interfaces.py`

存储接口抽象基类，定义存储引擎的核心功能。

#### save_history()

```python
def save_history(self, entry: Dict[str, Any]) -> bool
```

保存历史记录。

**参数**:
- `entry` (Dict[str, Any]): 历史记录条目，包含 input, command, success 等字段

**返回值**:
- `bool`: 保存是否成功

**示例**:
```python
from src.storage.factory import StorageFactory

storage = StorageFactory.get_default_storage()
entry = {
    'input': '显示时间',
    'command': 'Get-Date',
    'success': True,
    'timestamp': '2025-10-17T10:30:00'
}
storage.save_history(entry)
```

#### load_history()

```python
def load_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]
```

加载历史记录。

**参数**:
- `limit` (Optional[int]): 返回的最大记录数，None 表示返回所有记录

**返回值**:
- `List[Dict[str, Any]]`: 历史记录列表

**示例**:
```python
# 加载最近 10 条历史记录
history = storage.load_history(limit=10)
for entry in history:
    print(f"{entry['input']} -> {entry['command']}")
```


#### save_cache()

```python
def save_cache(self, key: str, value: Any, ttl: Optional[int] = None) -> bool
```

保存缓存数据。

**参数**:
- `key` (str): 缓存键
- `value` (Any): 缓存值
- `ttl` (Optional[int]): 过期时间（秒），None 表示永不过期

**返回值**:
- `bool`: 保存是否成功

**示例**:
```python
# 缓存翻译结果，1小时后过期
storage.save_cache("translation:显示时间", "Get-Date", ttl=3600)
```

#### load_cache()

```python
def load_cache(self, key: str) -> Optional[Any]
```

加载缓存数据。

**参数**:
- `key` (str): 缓存键

**返回值**:
- `Optional[Any]`: 缓存值，如果不存在或已过期返回 None

**示例**:
```python
cached_command = storage.load_cache("translation:显示时间")
if cached_command:
    print(f"从缓存获取: {cached_command}")
```

#### save_session()

```python
def save_session(self, session_data: Dict[str, Any]) -> bool
```

保存会话数据。

**参数**:
- `session_data` (Dict[str, Any]): 会话数据字典

**返回值**:
- `bool`: 保存是否成功

**示例**:
```python
session_data = {
    'session_id': 'session-123',
    'user_id': 'user-456',
    'start_time': '2025-10-17T10:00:00',
    'command_history': []
}
storage.save_session(session_data)
```


#### load_session()

```python
def load_session(self, session_id: str) -> Optional[Dict[str, Any]]
```

加载会话数据。

**参数**:
- `session_id` (str): 会话 ID

**返回值**:
- `Optional[Dict[str, Any]]`: 会话数据字典，如果不存在返回 None

**示例**:
```python
session = storage.load_session("session-123")
if session:
    print(f"会话用户: {session['user_id']}")
```

#### get_storage_info()

```python
def get_storage_info(self) -> Dict[str, Any]
```

获取存储信息。

**返回值**:
- `Dict[str, Any]`: 存储信息，包括路径、大小等

**示例**:
```python
info = storage.get_storage_info()
print(f"存储路径: {info['base_path']}")
print(f"历史记录数: {info['history_count']}")
```

---

## 上下文管理 API

### ContextManager

**位置**: `src/context/manager.py`

上下文管理器类，负责会话管理、命令历史记录和用户偏好设置。

#### 构造函数

```python
def __init__(self, storage: Optional[StorageInterface] = None)
```

**参数**:
- `storage` (Optional[StorageInterface]): 存储接口实例，用于持久化会话数据

**示例**:
```python
from src.context.manager import ContextManager
from src.storage.factory import StorageFactory

storage = StorageFactory.get_default_storage()
context_manager = ContextManager(storage)
```


#### start_session()

```python
def start_session(
    self, 
    user_id: Optional[str] = None, 
    working_directory: str = ".",
    environment_vars: Optional[Dict[str, str]] = None
) -> Session
```

开始新会话。

**参数**:
- `user_id` (Optional[str]): 用户 ID
- `working_directory` (str): 工作目录
- `environment_vars` (Optional[Dict[str, str]]): 环境变量

**返回值**:
- `Session`: 新创建的会话对象

**示例**:
```python
session = context_manager.start_session(
    user_id="user-123",
    working_directory="/home/user",
    environment_vars={'LANG': 'zh_CN.UTF-8'}
)
print(f"会话 ID: {session.session_id}")
```

#### get_current_session()

```python
def get_current_session(self) -> Optional[Session]
```

获取当前活跃会话。

**返回值**:
- `Optional[Session]`: 当前会话对象

**示例**:
```python
session = context_manager.get_current_session()
if session:
    print(f"当前会话: {session.session_id}")
```

#### terminate_session()

```python
def terminate_session(self, session_id: Optional[str] = None)
```

终止会话。

**参数**:
- `session_id` (Optional[str]): 会话 ID，如果为 None 则终止当前会话

**示例**:
```python
context_manager.terminate_session()  # 终止当前会话
```


#### add_command()

```python
def add_command(
    self, 
    user_input: str, 
    suggestion: Suggestion, 
    result: Optional[ExecutionResult] = None
) -> CommandEntry
```

添加命令到当前会话。

**参数**:
- `user_input` (str): 用户原始输入
- `suggestion` (Suggestion): AI 翻译建议
- `result` (Optional[ExecutionResult]): 执行结果（可选）

**返回值**:
- `CommandEntry`: 命令条目对象

**示例**:
```python
from src.interfaces.base import Suggestion, ExecutionResult

suggestion = Suggestion(
    original_input="显示时间",
    generated_command="Get-Date",
    confidence_score=0.95,
    explanation="获取当前日期和时间"
)

result = ExecutionResult(
    success=True,
    command="Get-Date",
    output="2025-10-17 10:30:00"
)

entry = context_manager.add_command("显示时间", suggestion, result)
print(f"命令 ID: {entry.command_id}")
```

#### get_context()

```python
def get_context(self, depth: int = 5) -> Context
```

获取当前上下文。

**参数**:
- `depth` (int): 历史深度，返回最近的 N 条命令

**返回值**:
- `Context`: 上下文对象

**示例**:
```python
context = context_manager.get_context(depth=10)
print(f"会话 ID: {context.session_id}")
print(f"最近命令: {context.command_history}")
```


#### get_recent_commands()

```python
def get_recent_commands(self, limit: int = 10) -> List[CommandEntry]
```

获取最近的命令。

**参数**:
- `limit` (int): 返回的命令数量

**返回值**:
- `List[CommandEntry]`: 命令列表

**示例**:
```python
recent = context_manager.get_recent_commands(limit=5)
for cmd in recent:
    print(f"{cmd.user_input} -> {cmd.translated_command}")
```

#### create_snapshot()

```python
def create_snapshot(
    self, 
    description: str = "", 
    tags: Optional[List[str]] = None
) -> ContextSnapshot
```

创建上下文快照。

**参数**:
- `description` (str): 快照描述
- `tags` (Optional[List[str]]): 标签列表

**返回值**:
- `ContextSnapshot`: 快照对象

**示例**:
```python
snapshot = context_manager.create_snapshot(
    description="备份前的状态",
    tags=["backup", "important"]
)
print(f"快照 ID: {snapshot.snapshot_id}")
```

#### restore_snapshot()

```python
def restore_snapshot(self, snapshot_id: str) -> bool
```

恢复上下文快照。

**参数**:
- `snapshot_id` (str): 快照 ID

**返回值**:
- `bool`: 恢复是否成功

**示例**:
```python
success = context_manager.restore_snapshot("snapshot-123")
if success:
    print("快照恢复成功")
```


#### get_session_stats()

```python
def get_session_stats(self) -> Dict[str, Any]
```

获取当前会话统计信息。

**返回值**:
- `Dict[str, Any]`: 统计信息字典

**示例**:
```python
stats = context_manager.get_session_stats()
print(f"命令总数: {stats['command_count']}")
print(f"成功命令: {stats['successful_commands']}")
print(f"失败命令: {stats['failed_commands']}")
print(f"会话时长: {stats['duration']}秒")
```

---

## 数据模型

### Suggestion

**位置**: `src/interfaces/base.py`

AI 翻译建议数据模型。

**字段**:
- `original_input` (str): 原始用户输入
- `generated_command` (str): 生成的 PowerShell 命令
- `confidence_score` (float): 置信度分数 (0.0-1.0)
- `explanation` (str): 命令解释说明
- `alternatives` (List[str]): 备选命令列表
- `timestamp` (datetime): 生成时间

**示例**:
```python
from src.interfaces.base import Suggestion

suggestion = Suggestion(
    original_input="显示进程",
    generated_command="Get-Process",
    confidence_score=0.95,
    explanation="获取当前运行的所有进程",
    alternatives=["ps", "Get-Process | Format-Table"]
)
```


### ValidationResult

**位置**: `src/interfaces/base.py`

安全验证结果数据模型。

**字段**:
- `is_valid` (bool): 是否通过验证
- `risk_level` (RiskLevel): 风险等级
- `blocked_reasons` (List[str]): 阻止原因列表
- `requires_confirmation` (bool): 是否需要用户确认
- `requires_elevation` (bool): 是否需要权限提升
- `warnings` (List[str]): 警告信息列表
- `timestamp` (datetime): 验证时间

**属性**:
- `is_dangerous` (bool): 判断是否为危险命令

**示例**:
```python
from src.interfaces.base import ValidationResult, RiskLevel

result = ValidationResult(
    is_valid=True,
    risk_level=RiskLevel.MEDIUM,
    requires_confirmation=True,
    warnings=["此命令将修改系统设置"]
)

if result.is_dangerous:
    print("警告: 危险命令!")
```

### ExecutionResult

**位置**: `src/interfaces/base.py`

命令执行结果数据模型。

**字段**:
- `success` (bool): 执行是否成功
- `command` (str): 执行的命令
- `output` (str): 标准输出
- `error` (str): 错误输出
- `return_code` (int): 返回码
- `execution_time` (float): 执行时间（秒）
- `status` (ExecutionStatus): 执行状态
- `timestamp` (datetime): 执行时间
- `metadata` (Dict[str, Any]): 额外元数据

**属性**:
- `has_output` (bool): 判断是否有输出
- `has_error` (bool): 判断是否有错误

**示例**:
```python
from src.interfaces.base import ExecutionResult, ExecutionStatus

result = ExecutionResult(
    success=True,
    command="Get-Date",
    output="2025-10-17 10:30:00",
    return_code=0,
    execution_time=0.123,
    status=ExecutionStatus.SUCCESS
)

if result.has_output:
    print(result.output)
```


### Context

**位置**: `src/interfaces/base.py`

上下文数据模型。

**字段**:
- `session_id` (str): 会话 ID
- `user_id` (Optional[str]): 用户 ID
- `working_directory` (str): 工作目录
- `environment_vars` (Dict[str, str]): 环境变量
- `command_history` (List[str]): 命令历史
- `timestamp` (datetime): 上下文创建时间
- `metadata` (Dict[str, Any]): 额外元数据

**方法**:
- `add_command(command: str)`: 添加命令到历史记录
- `get_recent_commands(limit: int = 5)`: 获取最近的命令

**示例**:
```python
from src.interfaces.base import Context

context = Context(
    session_id="session-123",
    user_id="user-456",
    working_directory="/home/user",
    environment_vars={'LANG': 'zh_CN.UTF-8'}
)

context.add_command("Get-Date")
recent = context.get_recent_commands(limit=3)
```

### RiskLevel

**位置**: `src/interfaces/base.py`

风险等级枚举。

**值**:
- `SAFE`: 安全命令
- `LOW`: 低风险
- `MEDIUM`: 中等风险
- `HIGH`: 高风险
- `CRITICAL`: 严重风险

**示例**:
```python
from src/interfaces.base import RiskLevel

if risk_level == RiskLevel.CRITICAL:
    print("严重风险，禁止执行!")
```


### ExecutionStatus

**位置**: `src/interfaces/base.py`

执行状态枚举。

**值**:
- `SUCCESS`: 执行成功
- `FAILED`: 执行失败
- `TIMEOUT`: 执行超时
- `CANCELLED`: 用户取消

**示例**:
```python
from src.interfaces.base import ExecutionStatus

if result.status == ExecutionStatus.TIMEOUT:
    print("命令执行超时")
```

---

## 接口定义

### AIEngineInterface

**位置**: `src/interfaces/base.py`

AI 引擎接口，定义 AI 引擎的核心功能。

**抽象方法**:
- `translate_natural_language(text: str, context: Context) -> Suggestion`
- `validate_command(command: str) -> bool`
- `get_command_explanation(command: str) -> str`

### SecurityEngineInterface

**位置**: `src/interfaces/base.py`

安全引擎接口，定义安全引擎的核心功能。

**抽象方法**:
- `validate_command(command: str, context: Context) -> ValidationResult`
- `check_permissions(command: str) -> bool`
- `is_dangerous_command(command: str) -> bool`

### ExecutorInterface

**位置**: `src/interfaces/base.py`

执行器接口，定义执行器的核心功能。

**抽象方法**:
- `execute(command: str, timeout: int = 30) -> ExecutionResult`
- `execute_async(command: str, timeout: int = 30) -> Any`
- `is_available() -> bool`


### StorageInterface

**位置**: `src/storage/interfaces.py`

存储接口，定义存储引擎的核心功能。

**抽象方法**:
- `save_history(entry: Dict[str, Any]) -> bool`
- `load_history(limit: Optional[int] = None) -> List[Dict[str, Any]]`
- `clear_history() -> bool`
- `save_config(config: Dict[str, Any]) -> bool`
- `load_config() -> Optional[Dict[str, Any]]`
- `save_cache(key: str, value: Any, ttl: Optional[int] = None) -> bool`
- `load_cache(key: str) -> Optional[Any]`
- `clear_cache() -> bool`
- `save_session(session_data: Dict[str, Any]) -> bool`
- `load_session(session_id: str) -> Optional[Dict[str, Any]]`
- `save_snapshot(snapshot_data: Dict[str, Any]) -> bool`
- `load_snapshot(snapshot_id: str) -> Optional[Dict[str, Any]]`
- `save_user_preferences(preferences_data: Dict[str, Any]) -> bool`
- `load_user_preferences(user_id: str) -> Optional[Dict[str, Any]]`
- `get_storage_info() -> Dict[str, Any]`

---

## 相关文档

- [系统架构](architecture.md) - 系统架构和设计模式
- [开发者指南](developer-guide.md) - 开发环境设置和开发规范
- [用户指南](user-guide.md) - 用户使用指南和功能说明
- [配置参考](config-reference.md) - 配置项详细说明
- [CLI 参考](cli-reference.md) - CLI 命令参考

## 下一步

- 如果你想了解系统架构，建议阅读 [系统架构文档](architecture.md)
- 如果你想开发扩展，建议阅读 [开发者指南](developer-guide.md)
- 如果你想配置系统，建议阅读 [配置参考](config-reference.md)

---

**需要帮助?** 查看 [故障排除指南](troubleshooting.md) 或 [提交 Issue](https://github.com/your-repo/ai-powershell/issues)
