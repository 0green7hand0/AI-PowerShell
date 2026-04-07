<!-- 文档类型: 开发者文档 | 最后更新: 2025-10-17 | 维护者: 项目团队 -->

# AI PowerShell 智能助手 - 开发者指南

---
📍 [首页](../README.md) > [文档中心](README.md) > 开发者指南

## 概述

本指南旨在帮助开发者理解项目结构、开发流程和最佳实践，以便能够有效地为项目做出贡献或进行定制开发。本文档涵盖环境设置、项目结构、开发规范、模块开发指南、测试指南、文档编写和贡献流程。

## 开发环境设置

### 前置要求

- Python 3.8 或更高版本
- PowerShell Core 7.0+ 或 Windows PowerShell 5.1+
- Git


### 环境配置

```bash
# 1. 克隆仓库
git clone https://github.com/0green7hand0/AI-PowerShell.git
cd AI-PowerShell

# 2. 创建虚拟环境
python -m venv venv

# 3. 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# 4. 安装依赖
pip install -r requirements.txt

# 5. 安装开发依赖
pip install pytest pytest-cov black flake8 mypy

# 6. 运行测试确认环境
pytest tests/
```

## 项目结构

```
AI-PowerShell/
├── src/                   # 源代码
│   ├── interfaces/        # 接口定义
│   ├── ai_engine/         # AI 引擎
│   ├── security/          # 安全引擎
│   ├── execution/         # 执行引擎
│   ├── config/            # 配置管理
│   ├── log_engine/        # 日志引擎
│   ├── storage/           # 存储引擎
│   ├── context/           # 上下文管理
│   └── main.py            # 主入口
├── tests/                 # 测试代码
│   ├── ai_engine/
│   ├── security/
│   ├── execution/
│   ├── config/
│   ├── log_engine/
│   ├── storage/
│   ├── context/
│   └── integration/
├── config/                # 配置文件
├── docs/                  # 文档
├── scripts/               # 脚本
└── logs/                  # 日志
```

## 代码规范

### Python 代码风格

遵循 PEP 8 规范：

```python
# 1. 导入顺序
import os  # 标准库
import sys

from typing import Dict, List, Optional  # 类型提示

from src.interfaces.base import AIEngineInterface  # 项目内部导入

# 2. 类定义
class MyClass:
    """类的文档字符串
    
    详细说明类的用途和功能。
    """
    
    def __init__(self, param: str):
        """初始化方法
        
        Args:
            param: 参数说明
        """
        self.param = param
    
    def my_method(self, arg: int) -> str:
        """方法的文档字符串
        
        Args:
            arg: 参数说明
            
        Returns:
            返回值说明
            
        Raises:
            ValueError: 错误说明
        """
        return f"Result: {arg}"

# 3. 函数定义
def my_function(param1: str, param2: int = 0) -> bool:
    """函数的文档字符串
    
    Args:
        param1: 第一个参数
        param2: 第二个参数，默认为 0
        
    Returns:
        布尔值结果
    """
    return len(param1) > param2
```

### 类型提示

使用类型提示提高代码可读性：

```python
from typing import Dict, List, Optional, Union

def process_data(
    data: List[str],
    config: Dict[str, any],
    timeout: Optional[int] = None
) -> Union[str, None]:
    """处理数据"""
    pass
```

### 文档字符串

使用 Google 风格的文档字符串：

```python
def complex_function(param1: str, param2: int) -> Dict[str, any]:
    """执行复杂操作
    
    这是一个更详细的说明，解释函数的具体行为。
    
    Args:
        param1: 第一个参数的说明
        param2: 第二个参数的说明
        
    Returns:
        包含结果的字典，格式为：
        {
            'status': 'success' 或 'error',
            'data': 处理后的数据,
            'message': 状态消息
        }
        
    Raises:
        ValueError: 当 param2 为负数时
        RuntimeError: 当处理失败时
        
    Example:
        >>> result = complex_function("test", 10)
        >>> print(result['status'])
        'success'
    """
    pass
```

## 添加新功能

### 1. 添加新的 AI 提供商

创建新的 AI 提供商类：

```python
# src/ai_engine/providers.py

from abc import ABC, abstractmethod
from src.interfaces.base import Suggestion, Context

class AIProvider(ABC):
    """AI 提供商抽象基类"""
    
    @abstractmethod
    def generate(self, text: str, context: Context) -> Suggestion:
        """生成命令建议"""
        pass

class CustomAIProvider(AIProvider):
    """自定义 AI 提供商"""
    
    def __init__(self, config: dict):
        """初始化提供商
        
        Args:
            config: 配置字典，包含模型路径、参数等
        """
        self.config = config
        self.model = self._load_model()
    
    def _load_model(self):
        """加载 AI 模型"""
        # 实现模型加载逻辑
        pass
    
    def generate(self, text: str, context: Context) -> Suggestion:
        """生成命令建议
        
        Args:
            text: 用户输入的自然语言
            context: 上下文信息
            
        Returns:
            命令建议对象
        """
        # 1. 构建提示词
        prompt = self._build_prompt(text, context)
        
        # 2. 调用模型生成
        result = self.model.generate(prompt)
        
        # 3. 解析结果
        return self._parse_result(result)
    
    def _build_prompt(self, text: str, context: Context) -> str:
        """构建提示词"""
        return f"将以下中文转换为 PowerShell 命令：{text}"
    
    def _parse_result(self, result: str) -> Suggestion:
        """解析模型输出"""
        return Suggestion(
            original_input=text,
            generated_command=result,
            confidence_score=0.8,
            explanation="AI 生成",
            alternatives=[]
        )
```

在配置中注册：

```yaml
# config/default.yaml
ai:
  provider: "custom"  # 使用自定义提供商
  custom:
    model_path: "/path/to/model"
    temperature: 0.7
    max_tokens: 256
```

### 2. 扩展安全规则

添加自定义安全规则：

```python
# src/security/whitelist.py

class CommandWhitelist:
    """命令白名单"""
    
    def __init__(self, config):
        self.config = config
        self.dangerous_patterns = self._load_dangerous_patterns()
        self.safe_prefixes = self._load_safe_prefixes()
        self.custom_rules = self._load_custom_rules()
    
    def _load_custom_rules(self) -> List[Dict]:
        """加载自定义规则"""
        return self.config.get('custom_rules', [])
    
    def validate(self, command: str) -> ValidationResult:
        """验证命令"""
        # 1. 检查自定义规则
        for rule in self.custom_rules:
            if self._match_rule(command, rule):
                return ValidationResult(
                    is_valid=rule['action'] == 'allow',
                    risk_level=rule.get('risk_level', 'medium'),
                    blocked_reasons=[rule['description']]
                )
        
        # 2. 检查危险模式
        for pattern in self.dangerous_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return ValidationResult(
                    is_valid=False,
                    risk_level='high',
                    blocked_reasons=[f"匹配危险模式: {pattern}"]
                )
        
        # 3. 检查安全前缀
        for prefix in self.safe_prefixes:
            if command.startswith(prefix):
                return ValidationResult(
                    is_valid=True,
                    risk_level='low',
                    blocked_reasons=[]
                )
        
        # 4. 默认需要确认
        return ValidationResult(
            is_valid=True,
            risk_level='medium',
            blocked_reasons=[],
            requires_confirmation=True
        )
```

在配置中添加规则：

```yaml
# config/default.yaml
security:
  custom_rules:
    - pattern: ".*\\company_scripts\\.*"
      action: "allow"
      risk_level: "low"
      description: "允许执行公司批准的脚本"
    
    - pattern: "Remove-Item.*important_files"
      action: "block"
      risk_level: "critical"
      description: "阻止删除重要文件"
```

### 3. 添加翻译规则

扩展翻译规则：

```python
# src/ai_engine/translation.py

class NaturalLanguageTranslator:
    """自然语言翻译器"""
    
    def _load_rules(self) -> Dict[str, str]:
        """加载翻译规则"""
        return {
            # 文件操作
            r"(显示|列出|查看).*文件": "Get-ChildItem",
            r"(创建|新建).*文件夹": "New-Item -ItemType Directory",
            r"(删除|移除).*文件": "Remove-Item",
            
            # 进程管理
            r"(显示|列出|查看).*进程": "Get-Process",
            r"(结束|停止|终止).*进程": "Stop-Process",
            
            # 服务管理
            r"(显示|列出|查看).*服务": "Get-Service",
            r"(启动|开始).*服务": "Start-Service",
            r"(停止|结束).*服务": "Stop-Service",
            
            # 网络相关
            r"(测试|检查).*网络.*连接": "Test-NetConnection",
            r"(显示|查看).*IP.*地址": "Get-NetIPAddress",
            
            # 系统信息
            r"(显示|查看).*(时间|日期)": "Get-Date",
            r"(显示|查看).*系统.*信息": "Get-ComputerInfo",
            
            # 自定义规则
            # 在这里添加你的规则
        }
```

### 4. 添加新的存储后端

实现存储接口：

```python
# src/storage/database_storage.py

from src.storage.interfaces import StorageInterface

class DatabaseStorage(StorageInterface):
    """数据库存储实现"""
    
    def __init__(self, connection_string: str):
        """初始化数据库连接
        
        Args:
            connection_string: 数据库连接字符串
        """
        self.connection_string = connection_string
        self.connection = self._connect()
    
    def _connect(self):
        """建立数据库连接"""
        # 实现数据库连接逻辑
        pass
    
    def save(self, key: str, value: any) -> bool:
        """保存数据"""
        try:
            # 实现保存逻辑
            return True
        except Exception as e:
            logger.error(f"保存失败: {e}")
            return False
    
    def load(self, key: str) -> any:
        """加载数据"""
        try:
            # 实现加载逻辑
            return data
        except Exception as e:
            logger.error(f"加载失败: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """删除数据"""
        try:
            # 实现删除逻辑
            return True
        except Exception as e:
            logger.error(f"删除失败: {e}")
            return False
```

在工厂中注册：

```python
# src/storage/factory.py

class StorageFactory:
    """存储工厂"""
    
    @staticmethod
    def create(storage_type: str, config: dict) -> StorageInterface:
        """创建存储实例"""
        if storage_type == "file":
            return FileStorage(config['base_path'])
        elif storage_type == "database":
            return DatabaseStorage(config['connection_string'])
        else:
            raise ValueError(f"不支持的存储类型: {storage_type}")
```

## 测试

### 单元测试

编写单元测试：

```python
# tests/ai_engine/test_translation.py

import pytest
from src.ai_engine.translation import NaturalLanguageTranslator
from src.interfaces.base import Context

class TestNaturalLanguageTranslator:
    """测试自然语言翻译器"""
    
    def setup_method(self):
        """测试前设置"""
        self.translator = NaturalLanguageTranslator()
    
    def test_translate_simple_command(self):
        """测试简单命令翻译"""
        # Arrange
        text = "显示所有文件"
        context = Context()
        
        # Act
        result = self.translator.translate(text, context)
        
        # Assert
        assert result.generated_command == "Get-ChildItem"
        assert result.confidence_score > 0.9
    
    def test_translate_complex_command(self):
        """测试复杂命令翻译"""
        text = "显示CPU使用率最高的5个进程"
        context = Context()
        
        result = self.translator.translate(text, context)
        
        assert "Get-Process" in result.generated_command
        assert "Sort-Object" in result.generated_command
        assert "Select-Object" in result.generated_command
    
    def test_translate_with_context(self):
        """测试带上下文的翻译"""
        text = "显示它们的详细信息"
        context = Context(
            previous_commands=["Get-Process"]
        )
        
        result = self.translator.translate(text, context)
        
        assert result.generated_command is not None
```

运行测试：

```bash
# 运行所有测试
pytest tests/

# 运行特定测试文件
pytest tests/ai_engine/test_translation.py

# 运行特定测试方法
pytest tests/ai_engine/test_translation.py::TestNaturalLanguageTranslator::test_translate_simple_command

# 生成覆盖率报告
pytest --cov=src tests/

# 生成 HTML 覆盖率报告
pytest --cov=src --cov-report=html tests/
```

### 集成测试

编写集成测试：

```python
# tests/integration/test_main_integration.py

import pytest
from src.main import PowerShellAssistant

class TestPowerShellAssistantIntegration:
    """测试主控制器集成"""
    
    def setup_method(self):
        """测试前设置"""
        self.assistant = PowerShellAssistant()
    
    def test_full_request_flow(self):
        """测试完整请求流程"""
        # Arrange
        user_input = "显示当前时间"
        
        # Act
        result = self.assistant.process_request(user_input)
        
        # Assert
        assert result.success
        assert result.output is not None
        assert "Get-Date" in result.command
    
    def test_dangerous_command_blocked(self):
        """测试危险命令被阻止"""
        user_input = "删除所有文件"
        
        result = self.assistant.process_request(user_input)
        
        assert not result.success
        assert "危险" in result.error or "阻止" in result.error
```

## 代码质量工具

### Black - 代码格式化

```bash
# 格式化所有代码
black src/ tests/

# 检查但不修改
black --check src/ tests/

# 格式化特定文件
black src/main.py
```

### Flake8 - 代码检查

```bash
# 检查所有代码
flake8 src/ tests/

# 检查特定文件
flake8 src/main.py

# 忽略特定错误
flake8 --ignore=E501,W503 src/
```

### Mypy - 类型检查

```bash
# 类型检查
mypy src/

# 严格模式
mypy --strict src/

# 检查特定文件
mypy src/main.py
```

## 调试技巧

### 使用日志

```python
from src.log_engine.engine import LogEngine

logger = LogEngine.get_logger(__name__)

def my_function(param):
    logger.debug(f"函数调用: param={param}")
    
    try:
        result = process(param)
        logger.info(f"处理成功: result={result}")
        return result
    except Exception as e:
        logger.error(f"处理失败: {e}", exc_info=True)
        raise
```

### 使用断点

```python
# 使用 pdb 调试器
import pdb

def my_function(param):
    pdb.set_trace()  # 设置断点
    result = process(param)
    return result
```

### 使用 pytest 调试

```bash
# 在失败时进入调试器
pytest --pdb tests/

# 在第一个失败时停止
pytest -x tests/

# 显示详细输出
pytest -v tests/

# 显示打印输出
pytest -s tests/
```

## 性能优化

### 使用缓存

```python
from functools import lru_cache

class MyClass:
    @lru_cache(maxsize=128)
    def expensive_operation(self, param: str) -> str:
        """昂贵的操作，使用缓存"""
        # 执行耗时操作
        return result
```

### 使用异步

```python
import asyncio

async def async_operation():
    """异步操作"""
    result = await some_async_call()
    return result

# 运行异步函数
result = asyncio.run(async_operation())
```

### 性能分析

```python
import cProfile
import pstats

# 性能分析
profiler = cProfile.Profile()
profiler.enable()

# 执行代码
my_function()

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)  # 显示前 10 个最耗时的函数
```

## 模块开发指南

### 配置管理模块

配置管理模块使用 Pydantic 进行数据验证，提供完整的配置加载、保存和验证功能。

**核心组件**:
- `ConfigManager`: 配置管理器，负责加载和保存配置
- `AppConfig`: 应用总配置，包含所有子配置
- 子配置类: `AIConfig`, `SecurityConfig`, `ExecutionConfig`, `LoggingConfig`, `StorageConfig`, `ContextConfig`

**使用示例**:
```python
from src.config import ConfigManager

# 创建配置管理器
manager = ConfigManager()

# 加载配置
config = manager.get_config()

# 访问配置
print(f"AI Provider: {config.ai.provider}")
print(f"Timeout: {config.execution.timeout}")

# 更新配置
updates = {
    "ai": {"temperature": 0.9},
    "execution": {"timeout": 60}
}
config = manager.update_config(updates)

# 保存配置
manager.save_config(config, "my_config.yaml")
```

**配置验证**:
- 所有配置类使用 Pydantic 进行类型检查和数据验证
- 支持范围验证（如 temperature: 0.0-2.0）
- 支持枚举验证（如 provider: local, ollama, openai, azure）
- 自动验证赋值（`validate_assignment=True`）

**配置文件路径**:
1. `config/default.yaml` - 默认配置
2. `config.yaml` - 项目配置
3. `~/.ai-powershell/config.yaml` - 用户配置

### 存储引擎模块

存储引擎提供数据持久化功能，支持历史记录、配置和缓存的存储。

**核心组件**:
- `StorageInterface`: 存储接口定义
- `FileStorage`: 文件存储实现
- `StorageFactory`: 存储工厂

**使用示例**:
```python
from src.storage.factory import StorageFactory

# 获取默认存储
storage = StorageFactory.get_default_storage()

# 保存历史记录
storage.save_history({
    "input": "显示当前时间",
    "command": "Get-Date",
    "success": True
})

# 加载历史记录
history = storage.load_history(limit=10)

# 保存缓存（带过期时间）
storage.save_cache("translation_cache", {"显示时间": "Get-Date"}, ttl=3600)

# 加载缓存
cache = storage.load_cache("translation_cache")
```

**存储结构**:
```
~/.ai-powershell/
├── history.json         # 命令历史
├── config.yaml          # 用户配置
├── sessions/            # 会话数据
├── snapshots/           # 上下文快照
├── preferences/         # 用户偏好
└── cache/              # 缓存目录
```

**扩展存储后端**:
```python
from src.storage.interfaces import StorageInterface

class DatabaseStorage(StorageInterface):
    """数据库存储实现"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.connection = self._connect()
    
    def save_history(self, entry: dict) -> bool:
        # 实现数据库保存逻辑
        pass
    
    def load_history(self, limit: int = 100) -> list:
        # 实现数据库加载逻辑
        pass
```

### 上下文管理模块

上下文管理模块负责管理用户会话、命令历史和用户偏好设置。

**核心组件**:
- `ContextManager`: 上下文管理器
- `HistoryManager`: 历史记录管理器
- 数据模型: `Session`, `CommandEntry`, `ContextSnapshot`, `UserPreferences`

**使用示例**:
```python
from src.context import ContextManager, HistoryManager
from src.storage.file_storage import FileStorage

# 初始化
storage = FileStorage()
context_manager = ContextManager(storage=storage)
history_manager = HistoryManager(storage=storage)

# 开始新会话
session = context_manager.start_session(user_id="user123")

# 添加命令
entry = context_manager.add_command(user_input, suggestion, result)

# 获取上下文
context = context_manager.get_context(depth=5)

# 查看会话统计
stats = context_manager.get_session_stats()

# 终止会话
context_manager.terminate_session()
```

**历史记录分析**:
```python
# 搜索历史
results = history_manager.search("Get-Date", search_in="command")

# 按状态过滤
completed = history_manager.filter_by_status(CommandStatus.COMPLETED)

# 获取统计信息
stats = history_manager.get_statistics()

# 获取最常用命令
most_used = history_manager.get_most_used_commands(limit=10)

# 导出历史
history_manager.export_history("history.json", format="json")
```

### 安全引擎模块

安全引擎提供三层安全验证机制，确保命令执行的安全性。

**核心组件**:
- `SecurityEngine`: 安全引擎主类
- `CommandWhitelist`: 命令白名单验证器
- `PermissionChecker`: 权限检查器
- `SandboxExecutor`: 沙箱执行器

**三层验证机制**:
1. **白名单验证**: 检测危险命令模式（30+ 种模式）
2. **权限检查**: 检测命令所需的管理员权限
3. **沙箱执行**: 安全隔离执行

**使用示例**:
```python
from src.security import SecurityEngine
from src.interfaces.base import Context

# 初始化安全引擎
config = {
    'whitelist_mode': 'strict',
    'require_confirmation': True,
    'sandbox_enabled': False
}
security_engine = SecurityEngine(config)

# 验证命令
context = Context(session_id="test-session")
result = security_engine.validate_command("Get-Date", context)

if result.is_valid:
    if result.requires_confirmation:
        # 需要用户确认
        confirmed = security_engine.get_user_confirmation("Get-Date", result.risk_level)
    else:
        # 可以直接执行
        pass
else:
    # 命令被阻止
    print(f"命令被阻止: {result.blocked_reasons}")
```

**自定义安全规则**:
```python
from src.security import CommandWhitelist
from src.interfaces.base import RiskLevel

whitelist = CommandWhitelist()

# 添加自定义危险模式
whitelist.add_custom_rule(
    r"My-DangerousCommand",
    "自定义危险命令",
    RiskLevel.HIGH
)

# 添加自定义安全命令
whitelist.add_safe_command("My-SafeCommand")
```

**风险等级**:
- `SAFE`: 安全命令（Get-*, Show-*, Test-* 等）
- `LOW`: 低风险命令
- `MEDIUM`: 中等风险（需要确认）
- `HIGH`: 高风险（需要管理员权限或特别危险）
- `CRITICAL`: 严重风险（可能造成系统损坏）

### 主控制器模块

主控制器是整个系统的核心，负责协调各个模块的工作。

**核心组件**:
- `PowerShellAssistant`: 主控制器类

**请求处理流程**:
```python
from src.main import PowerShellAssistant

# 初始化
assistant = PowerShellAssistant()

# 处理单个请求
result = assistant.process_request("显示当前时间", auto_execute=True)

# 启动交互模式
assistant.interactive_mode()
```

**完整流程**:
1. 生成关联 ID 并记录请求
2. 获取当前上下文
3. AI 翻译自然语言
4. 安全验证
5. 用户确认（如需要）
6. 执行命令
7. 保存历史记录
8. 更新上下文

**依赖注入**:
```python
# 所有子模块通过构造函数注入
self.ai_engine = AIEngine(config)
self.security_engine = SecurityEngine(config)
self.executor = CommandExecutor(config)
self.context_manager = ContextManager(storage=storage)
```

## 测试指南

### 测试结构

```
tests/
├── ai_engine/           # AI 引擎测试
├── security/            # 安全引擎测试
├── execution/           # 执行引擎测试
├── config/              # 配置管理测试
├── storage/             # 存储引擎测试
├── context/             # 上下文管理测试
├── integration/         # 集成测试
└── e2e/                # 端到端测试
```

### 编写单元测试

**测试命名规范**:
```python
class TestMyClass:
    """测试 MyClass 类"""
    
    def setup_method(self):
        """每个测试前的设置"""
        self.instance = MyClass()
    
    def test_basic_functionality(self):
        """测试基本功能"""
        # Arrange
        input_data = "test"
        
        # Act
        result = self.instance.process(input_data)
        
        # Assert
        assert result is not None
        assert result.success
    
    def test_error_handling(self):
        """测试错误处理"""
        with pytest.raises(ValueError):
            self.instance.process(None)
```

### 运行测试

```bash
# 运行所有测试
pytest tests/

# 运行特定测试文件
pytest tests/config/test_manager.py

# 运行特定测试方法
pytest tests/config/test_manager.py::TestConfigManager::test_load_config

# 生成覆盖率报告
pytest --cov=src tests/

# 生成 HTML 覆盖率报告
pytest --cov=src --cov-report=html tests/

# 显示详细输出
pytest -v tests/

# 显示打印输出
pytest -s tests/

# 在失败时进入调试器
pytest --pdb tests/
```

### 测试覆盖率目标

- 核心模块: ≥ 90%
- 工具模块: ≥ 80%
- 总体覆盖率: ≥ 85%

### Mock 和 Fixture

```python
import pytest
from unittest.mock import Mock, patch

@pytest.fixture
def mock_storage():
    """Mock 存储"""
    storage = Mock()
    storage.save_history.return_value = True
    storage.load_history.return_value = []
    return storage

def test_with_mock(mock_storage):
    """使用 mock 的测试"""
    manager = ContextManager(storage=mock_storage)
    # 测试逻辑
```

## 文档编写

### 文档类型

1. **用户文档**: 面向最终用户，简单易懂
2. **开发者文档**: 面向开发者，包含技术细节
3. **API 文档**: 接口说明和代码示例
4. **部署文档**: 面向运维人员，部署和配置说明

### 文档结构

每个文档应包含：

```markdown
# 文档标题

简短的文档描述（1-2句话）

## 目录（可选，长文档需要）

## 主要内容

### 二级标题

内容...

## 相关文档

- [系统架构文档](architecture.md) - 了解系统设计和模块关系
- [API 参考](api-reference.md) - 查找具体 API 接口
- [配置参考](config-reference.md) - 配置系统参数
- [部署运维指南](deployment-guide.md) - 部署和发布流程

## 获取帮助

- 问题反馈
- 讨论链接
```

### 代码示例

使用语言标识：

````markdown
```python
# Python 代码
from src.main import PowerShellAssistant
```

```bash
# Bash 命令
python src/main.py
```

```yaml
# YAML 配置
ai:
  provider: ollama
```
````

### 文档规范

- 使用相对路径链接
- 代码块包含语言标识
- 提供实际可运行的示例
- 使用 emoji 增强可读性（💡 ⚠️ ✅ ❌）
- 保持格式统一

### 文档检查清单

提交文档前检查：

- [ ] 标题清晰准确
- [ ] 内容完整无误
- [ ] 代码示例可运行
- [ ] 链接正确有效
- [ ] 格式规范统一
- [ ] 拼写检查通过
- [ ] 相关文档已更新
- [ ] 添加到文档索引

## 贡献流程

### 1. Fork 项目

在 GitHub 上 Fork 项目到你的账号。

### 2. 创建分支

```bash
git checkout -b feature/my-new-feature
```

分支命名规范：
- `feature/` - 新功能
- `fix/` - Bug 修复
- `docs/` - 文档更新
- `refactor/` - 代码重构
- `test/` - 测试相关

### 3. 开发和测试

```bash
# 编写代码
# 编写测试
pytest tests/

# 代码格式化
black src/ tests/

# 代码检查
flake8 src/ tests/
mypy src/
```

### 4. 提交更改

```bash
git add .
git commit -m "Add: 添加新功能的描述"
```

提交信息格式：
- `Add:` 添加新功能
- `Fix:` 修复 bug
- `Update:` 更新功能
- `Refactor:` 重构代码
- `Docs:` 更新文档
- `Test:` 添加测试

### 5. 推送到 GitHub

```bash
git push origin feature/my-new-feature
```

### 6. 创建 Pull Request

在 GitHub 上创建 Pull Request，描述你的更改。

**PR 描述模板**:
```markdown
## 变更类型
- [ ] 新功能
- [ ] Bug 修复
- [ ] 文档更新
- [ ] 代码重构

## 变更说明
简要描述你的变更...

## 测试
- [ ] 添加了单元测试
- [ ] 所有测试通过
- [ ] 代码覆盖率 ≥ 85%

## 相关 Issue
Closes #123
```

### 7. 代码审查

- 响应审查意见
- 及时更新代码
- 保持沟通

### 8. 合并

审查通过后，维护者会合并你的 PR。

## 开发规范

### 代码风格

遵循 PEP 8 规范和项目约定。

**导入顺序**:
```python
# 1. 标准库
import os
import sys

# 2. 第三方库
from typing import Dict, List, Optional

# 3. 项目内部导入
from src.interfaces.base import AIEngineInterface
```

**类型提示**:
```python
from typing import Dict, List, Optional, Union

def process_data(
    data: List[str],
    config: Dict[str, any],
    timeout: Optional[int] = None
) -> Union[str, None]:
    """处理数据"""
    pass
```

**文档字符串**:

使用 Google 风格的文档字符串：

```python
def complex_function(param1: str, param2: int) -> Dict[str, any]:
    """执行复杂操作
    
    这是一个更详细的说明，解释函数的具体行为。
    
    Args:
        param1: 第一个参数的说明
        param2: 第二个参数的说明
        
    Returns:
        包含结果的字典，格式为：
        {
            'status': 'success' 或 'error',
            'data': 处理后的数据,
            'message': 状态消息
        }
        
    Raises:
        ValueError: 当 param2 为负数时
        RuntimeError: 当处理失败时
        
    Example:
        >>> result = complex_function("test", 10)
        >>> print(result['status'])
        'success'
    """
    pass
```

**命名规范**:
- 类名: `PascalCase`
- 函数名: `snake_case`
- 常量: `UPPER_CASE`
- 私有方法: `_leading_underscore`

### 错误处理

**使用具体的异常类型**:
```python
# ❌ 不好
try:
    result = process()
except:
    pass

# ✅ 好
try:
    result = process()
except ValueError as e:
    logger.error(f"Invalid value: {e}")
    raise
except FileNotFoundError as e:
    logger.error(f"File not found: {e}")
    return None
```

**提供有用的错误信息**:
```python
# ❌ 不好
raise ValueError("Invalid input")

# ✅ 好
raise ValueError(f"Invalid temperature value: {temp}. Must be between 0.0 and 2.0")
```

### 日志记录

**使用适当的日志级别**:
```python
from src.log_engine.engine import LogEngine

logger = LogEngine.get_logger(__name__)

# DEBUG: 详细的调试信息
logger.debug(f"Processing input: {input_data}")

# INFO: 一般信息
logger.info(f"Command executed successfully: {command}")

# WARNING: 警告信息
logger.warning(f"High confidence score: {score}")

# ERROR: 错误信息
logger.error(f"Failed to execute command: {error}", exc_info=True)

# CRITICAL: 严重错误
logger.critical(f"System failure: {error}")
```

### 性能优化

**使用缓存**:
```python
from functools import lru_cache

class MyClass:
    @lru_cache(maxsize=128)
    def expensive_operation(self, param: str) -> str:
        """昂贵的操作，使用缓存"""
        # 执行耗时操作
        return result
```

**使用生成器**:
```python
# ❌ 不好 - 一次性加载所有数据
def get_all_records():
    records = []
    for item in large_dataset:
        records.append(process(item))
    return records

# ✅ 好 - 使用生成器
def get_all_records():
    for item in large_dataset:
        yield process(item)
```

**避免重复计算**:
```python
# ❌ 不好
for i in range(len(items)):
    if items[i].value > calculate_threshold():
        process(items[i])

# ✅ 好
threshold = calculate_threshold()
for item in items:
    if item.value > threshold:
        process(item)
```

## 常见问题

### Q: 如何添加新的配置选项？

A: 在 `src/config/models.py` 中添加配置模型字段，然后在 `config/default.yaml` 中添加默认值。

```python
# src/config/models.py
class AIConfig(BaseModel):
    provider: str = "local"
    model_name: str = "llama"
    # 添加新配置
    new_option: str = "default_value"
```

```yaml
# config/default.yaml
ai:
  provider: local
  model_name: llama
  new_option: default_value
```

### Q: 如何调试 AI 翻译问题？

A: 启用调试日志，查看翻译过程：

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# 或在配置中设置
# config/default.yaml
logging:
  level: DEBUG
```

### Q: 如何测试沙箱执行？

A: 在配置中启用沙箱：

```yaml
security:
  sandbox:
    enabled: true
```

### Q: 如何添加新的命令行参数？

A: 在 `src/main.py` 的 `main()` 函数中添加参数解析：

```python
parser.add_argument('--my-option', help='My new option')
```

### Q: 如何扩展存储后端？

A: 实现 `StorageInterface` 接口并在 `StorageFactory` 中注册：

```python
# 1. 实现接口
class MyStorage(StorageInterface):
    def save_history(self, entry: dict) -> bool:
        # 实现逻辑
        pass

# 2. 在工厂中注册
class StorageFactory:
    @staticmethod
    def create_storage(storage_type: str, config: dict):
        if storage_type == "my_storage":
            return MyStorage(config)
```

### Q: 如何添加新的 AI 提供商？

A: 在 `src/ai_engine/providers.py` 中创建新的提供商类：

```python
class CustomAIProvider(AIProvider):
    def generate(self, text: str, context: Context) -> Suggestion:
        # 实现生成逻辑
        pass
```

### Q: 如何调试测试失败？

A: 使用 pytest 的调试选项：

```bash
# 在失败时进入调试器
pytest --pdb tests/

# 显示详细输出
pytest -vv tests/

# 显示打印输出
pytest -s tests/

# 只运行失败的测试
pytest --lf tests/
```

## 最佳实践

### 1. 依赖注入

使用依赖注入提高可测试性：

```python
# ❌ 不好 - 硬编码依赖
class MyClass:
    def __init__(self):
        self.storage = FileStorage()  # 硬编码

# ✅ 好 - 依赖注入
class MyClass:
    def __init__(self, storage: StorageInterface):
        self.storage = storage  # 注入依赖
```

### 2. 接口设计

使用抽象基类定义接口：

```python
from abc import ABC, abstractmethod

class StorageInterface(ABC):
    @abstractmethod
    def save(self, data: dict) -> bool:
        """保存数据"""
        pass
    
    @abstractmethod
    def load(self) -> dict:
        """加载数据"""
        pass
```

### 3. 配置管理

使用配置文件而不是硬编码：

```python
# ❌ 不好
timeout = 30
max_retries = 3

# ✅ 好
config = ConfigManager().get_config()
timeout = config.execution.timeout
max_retries = config.execution.max_retries
```

### 4. 错误恢复

提供优雅的错误恢复机制：

```python
def process_with_retry(data, max_retries=3):
    """带重试的处理"""
    for attempt in range(max_retries):
        try:
            return process(data)
        except TemporaryError as e:
            if attempt == max_retries - 1:
                raise
            logger.warning(f"Attempt {attempt + 1} failed, retrying...")
            time.sleep(2 ** attempt)  # 指数退避
```

### 5. 资源管理

使用上下文管理器管理资源：

```python
# ✅ 好
with open('file.txt', 'r') as f:
    data = f.read()

# 或自定义上下文管理器
class SessionContext:
    def __enter__(self):
        self.session = start_session()
        return self.session
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()
```

### 6. 单一职责

每个类和函数应该只有一个职责：

```python
# ❌ 不好 - 职责过多
class DataProcessor:
    def load_and_process_and_save(self, file_path):
        data = self.load(file_path)
        result = self.process(data)
        self.save(result)

# ✅ 好 - 职责分离
class DataLoader:
    def load(self, file_path):
        pass

class DataProcessor:
    def process(self, data):
        pass

class DataSaver:
    def save(self, data):
        pass
```

### 7. 测试驱动开发

先写测试，再写实现：

```python
# 1. 先写测试
def test_calculate_sum():
    assert calculate_sum([1, 2, 3]) == 6
    assert calculate_sum([]) == 0

# 2. 再写实现
def calculate_sum(numbers):
    return sum(numbers)
```

## 开发工具

### 代码格式化

```bash
# Black - 代码格式化
black src/ tests/

# 检查但不修改
black --check src/ tests/
```

### 代码检查

```bash
# Flake8 - 代码检查
flake8 src/ tests/

# 忽略特定错误
flake8 --ignore=E501,W503 src/
```

### 类型检查

```bash
# Mypy - 类型检查
mypy src/

# 严格模式
mypy --strict src/
```

### 性能分析

```python
import cProfile
import pstats

# 性能分析
profiler = cProfile.Profile()
profiler.enable()

# 执行代码
my_function()

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)  # 显示前 10 个最耗时的函数
```

### 调试工具

```python
# 使用 pdb 调试器
import pdb

def my_function(param):
    pdb.set_trace()  # 设置断点
    result = process(param)
    return result

# 或使用 breakpoint() (Python 3.7+)
def my_function(param):
    breakpoint()  # 设置断点
    result = process(param)
    return result
```



## 版本发布

### 版本号规范

遵循语义化版本 (Semantic Versioning):
- `MAJOR.MINOR.PATCH`
- `MAJOR`: 不兼容的 API 变更
- `MINOR`: 向后兼容的功能新增
- `PATCH`: 向后兼容的问题修正

### 发布流程

1. 更新版本号
2. 更新 CHANGELOG.md
3. 创建 Git 标签
4. 推送到 GitHub
5. 创建 GitHub Release
6. 发布到 PyPI（如适用）

```bash
# 更新版本号
# 编辑 pyproject.toml

# 更新 CHANGELOG
# 编辑 CHANGELOG.md

# 提交更改
git add .
git commit -m "Release: v2.0.0"

# 创建标签
git tag -a v2.0.0 -m "Release v2.0.0"

# 推送
git push origin main --tags
```

## 资源链接

- [项目主页](https://github.com/0green7hand0/AI-PowerShell)
- [架构文档](architecture.md)
- [用户指南](user-guide.md)
- [模板指南](template-guide.md)
- [问题跟踪](https://github.com/0green7hand0/AI-PowerShell/issues)
- [讨论区](https://github.com/0green7hand0/AI-PowerShell/discussions)

## 相关文档

- [系统架构](architecture.md) - 了解系统整体架构
- [用户指南](user-guide.md) - 用户使用指南
- [部署指南](deployment-guide.md) - 部署和运维指南
- [API 参考](api-reference.md) - API 完整参考
- [故障排除](troubleshooting.md) - 常见问题解决

## 获取帮助

如有问题，请通过以下方式联系：

- **GitHub Issues**: 报告 Bug 或请求新功能
- **GitHub Discussions**: 技术讨论和问答
- **文档**: 查看完整文档获取更多信息

## 下一步

- 阅读[系统架构文档](architecture.md)了解系统设计
- 查看[用户指南](user-guide.md)了解功能使用
- 浏览[API 参考](api-reference.md)了解接口详情
- 参考[部署指南](deployment-guide.md)进行部署

---

**感谢你对 AI PowerShell 智能助手项目的贡献！** 🎉

我们欢迎所有形式的贡献，包括但不限于：
- 代码贡献
- 文档改进
- Bug 报告
- 功能建议
- 使用反馈

让我们一起让这个项目变得更好！
