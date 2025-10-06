# AI PowerShell 智能助手 - 开发者指南

## 概述

本指南旨在帮助开发者理解项目结构、开发流程和最佳实践，以便能够有效地为项目做出贡献或进行定制开发。

## 开发环境设置

### 前置要求

- Python 3.8 或更高版本
- PowerShell Core 7.0+ 或 Windows PowerShell 5.1+
- Git
- Docker（可选，用于沙箱执行）

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

## 贡献流程

### 1. Fork 项目

在 GitHub 上 Fork 项目到你的账号。

### 2. 创建分支

```bash
git checkout -b feature/my-new-feature
```

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

## 常见问题

### Q: 如何添加新的配置选项？

A: 在 `src/config/models.py` 中添加配置模型，然后在 `config/default.yaml` 中添加默认值。

### Q: 如何调试 AI 翻译问题？

A: 启用调试日志，查看翻译过程：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Q: 如何测试沙箱执行？

A: 确保 Docker 已安装并运行，然后在配置中启用沙箱：

```yaml
security:
  sandbox_enabled: true
```

### Q: 如何添加新的命令行参数？

A: 在 `src/main.py` 的 `main()` 函数中添加参数解析。

## 资源链接

- [项目主页](https://github.com/0green7hand0/AI-PowerShell)
- [架构文档](architecture.md)
- [问题跟踪](https://github.com/0green7hand0/AI-PowerShell/issues)
- [讨论区](https://github.com/0green7hand0/AI-PowerShell/discussions)

## 联系方式

如有问题，请通过以下方式联系：

- GitHub Issues
- GitHub Discussions
- Email: support@example.com

---

感谢你对 AI PowerShell 智能助手项目的贡献！
