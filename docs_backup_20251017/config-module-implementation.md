# 配置管理模块实现文档

## 概述

配置管理模块已成功实现，提供了完整的配置数据模型、配置管理器和单元测试。该模块使用 Pydantic 进行数据验证，支持 YAML 配置文件加载和保存。

## 实现的组件

### 1. 配置数据模型 (src/config/models.py)

实现了以下配置类，所有类都使用 Pydantic 进行数据验证：

#### AIConfig - AI 引擎配置
- `provider`: AI 提供商 (local, ollama, openai, azure)
- `model_name`: AI 模型名称
- `temperature`: 生成温度 (0.0-2.0)
- `max_tokens`: 最大生成 token 数 (1-4096)
- `cache_enabled`: 是否启用翻译缓存
- `cache_size`: 缓存大小

#### SecurityConfig - 安全引擎配置
- `sandbox_enabled`: 是否启用沙箱执行
- `require_confirmation`: 是否需要用户确认
- `whitelist_mode`: 白名单模式 (strict, moderate, permissive)
- `dangerous_patterns`: 危险命令模式列表
- `safe_prefixes`: 安全命令前缀列表
- `custom_rules`: 自定义安全规则

#### ExecutionConfig - 执行引擎配置
- `timeout`: 命令执行超时时间 (1-300 秒)
- `encoding`: 输出编码格式
- `platform`: 平台类型 (auto, windows, linux, macos)
- `powershell_path`: PowerShell 可执行文件路径
- `auto_detect_powershell`: 是否自动检测 PowerShell

#### LoggingConfig - 日志配置
- `level`: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `file`: 日志文件路径
- `max_size`: 日志文件最大大小
- `backup_count`: 日志文件备份数量
- `format`: 日志格式
- `console_output`: 是否输出到控制台

#### StorageConfig - 存储配置
- `base_path`: 存储基础路径
- `history_file`: 历史记录文件名
- `config_file`: 配置文件名
- `cache_dir`: 缓存目录名
- `max_history_size`: 最大历史记录数量

#### ContextConfig - 上下文管理配置
- `max_context_depth`: 最大上下文深度 (1-50)
- `session_timeout`: 会话超时时间 (≥60 秒)
- `enable_learning`: 是否启用学习功能

#### AppConfig - 应用总配置
包含所有子配置的顶层配置类，具有以下特性：
- 验证赋值 (`validate_assignment`)
- 禁止额外字段 (`extra='forbid'`)

### 2. 配置管理器 (src/config/manager.py)

实现了 `ConfigManager` 类，提供以下功能：

#### 核心方法

- `load_config(config_path)`: 从文件加载配置
  - 支持指定路径或默认路径
  - 自动验证配置数据
  - 处理文件不存在、YAML 解析错误、验证错误

- `get_config()`: 获取当前配置
  - 懒加载机制
  - 返回缓存的配置对象

- `save_config(config, file_path)`: 保存配置到文件
  - 自动创建目录
  - 格式化 YAML 输出
  - 支持中文

- `update_config(updates)`: 更新配置
  - 深度合并配置
  - 保持未更新的值不变
  - 自动验证更新后的配置

- `reset_to_defaults()`: 重置为默认配置

- `validate_config(config_data)`: 验证配置数据
  - 返回验证结果和错误信息

- `create_default_config_file(file_path)`: 创建默认配置文件
  - 静态方法
  - 生成包含所有默认值的配置文件

#### 默认配置路径

配置管理器会按以下顺序查找配置文件：
1. `config/default.yaml`
2. `config.yaml`
3. `~/.ai-powershell/config.yaml`

### 3. 默认配置文件 (config/default.yaml)

创建了完整的默认配置文件模板，包含：
- 所有配置选项及其默认值
- 详细的中文注释说明
- 配置项的可选值和范围说明
- 使用建议和最佳实践

### 4. 单元测试

实现了全面的单元测试，覆盖率达到 100%：

#### tests/config/test_models.py (29 个测试)
- 测试所有配置类的默认值
- 测试字段验证（范围、枚举值、类型）
- 测试自定义验证器
- 测试嵌套配置
- 测试额外字段禁止

#### tests/config/test_manager.py (17 个测试)
- 测试配置加载（文件、默认路径）
- 测试配置保存
- 测试配置更新和深度合并
- 测试配置验证
- 测试错误处理（文件不存在、YAML 错误、验证错误）
- 测试默认配置文件创建

## 使用示例

### 基本使用

```python
from src.config import ConfigManager

# 创建配置管理器
manager = ConfigManager()

# 加载配置（使用默认路径）
config = manager.get_config()

# 访问配置
print(f"AI Provider: {config.ai.provider}")
print(f"Timeout: {config.execution.timeout}")
```

### 加载指定配置文件

```python
manager = ConfigManager('config/default.yaml')
config = manager.load_config()
```

### 更新配置

```python
# 更新部分配置
updates = {
    "ai": {
        "temperature": 0.9
    },
    "execution": {
        "timeout": 60
    }
}
config = manager.update_config(updates)
```

### 保存配置

```python
from src.config import AppConfig, AIConfig

# 创建自定义配置
config = AppConfig(
    ai=AIConfig(provider="ollama", model_name="llama2")
)

# 保存到文件
manager.save_config(config, "my_config.yaml")
```

### 验证配置

```python
config_data = {
    "ai": {
        "provider": "openai",
        "temperature": 0.8
    }
}

is_valid, error = manager.validate_config(config_data)
if is_valid:
    print("配置有效")
else:
    print(f"配置无效: {error}")
```

### 创建默认配置文件

```python
ConfigManager.create_default_config_file("config/my_default.yaml")
```

## 测试结果

所有 46 个单元测试全部通过：
- 29 个配置模型测试
- 17 个配置管理器测试
- 测试覆盖率: 100%

```
================================================= 46 passed in 0.14s ==================================================
```

## 设计特点

1. **类型安全**: 使用 Pydantic 进行严格的类型检查和数据验证
2. **灵活性**: 支持多种配置来源和格式
3. **可扩展性**: 易于添加新的配置项和验证规则
4. **用户友好**: 提供详细的中文注释和错误信息
5. **健壮性**: 完善的错误处理和验证机制
6. **可测试性**: 100% 的测试覆盖率

## 与其他模块的集成

配置管理模块可以被其他模块使用：

```python
# AI 引擎使用配置
from src.config import ConfigManager
from src.ai_engine import AIEngine

manager = ConfigManager()
config = manager.get_config()
ai_engine = AIEngine(config.ai)

# 安全引擎使用配置
from src.security import SecurityEngine

security_engine = SecurityEngine(config.security)

# 执行引擎使用配置
from src.execution import CommandExecutor

executor = CommandExecutor(config.execution)
```

## 下一步

配置管理模块已完成，可以继续实现：
- 任务 7: 实现日志引擎模块
- 任务 8: 实现存储引擎模块
- 任务 9: 实现上下文管理模块
- 任务 10: 实现主入口和控制器

这些模块都将使用配置管理模块来获取和管理配置。
