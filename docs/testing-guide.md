# AI PowerShell 智能助手测试指南

本文档提供 AI PowerShell 智能助手的完整测试指南，帮助用户了解如何运行、编写和维护测试。

## 目录

- [概述](#概述)
- [快速开始](#快速开始)
- [测试环境配置](#测试环境配置)
- [测试类型](#测试类型)
- [运行测试](#运行测试)
- [编写测试](#编写测试)
- [测试覆盖率](#测试覆盖率)
- [测试报告](#测试报告)
- [常见问题](#常见问题)

---

## 概述

AI PowerShell 智能助手采用多层次测试策略，确保系统质量和稳定性：

```
┌─────────────────────────────────────────────────────────────┐
│                      测试金字塔                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                        ┌─────┐                              │
│                       /  E2E  \                             │
│                      / 测试    \                            │
│                     ├──────────┤                            │
│                    /  集成测试   \                           │
│                   /              \                          │
│                  ├────────────────┤                         │
│                 /     单元测试      \                        │
│                /                    \                       │
│               └──────────────────────┘                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 测试统计

| 测试类型 | 文件数量 | 测试用例数 | 覆盖目标 |
|---------|---------|-----------|---------|
| 单元测试 | 40+ | 300+ | > 80% |
| 集成测试 | 12 | 80+ | > 70% |
| E2E 测试 | 3 | 20+ | 关键流程 |
| 性能测试 | 3 | 30+ | 性能基准 |

---

## 快速开始

### 一键运行所有测试

```bash
# 运行所有测试
make test

# 或者使用 pytest
python -m pytest -v

# 运行测试并生成覆盖率报告
make coverage
```

### 快速验证

```bash
# 验证系统基本功能
python -m pytest tests/test_main.py -v

# 验证安全功能
python -m pytest tests/integration/test_security.py -v

# 验证性能
python -m pytest tests/integration/test_performance.py -v
```

---

## 测试环境配置

### 系统要求

- Python 3.8+
- PowerShell 5.1+ 或 PowerShell Core 7+
- Git

### 安装测试依赖

```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 或者使用 pip 安装测试工具
pip install pytest pytest-cov pytest-asyncio
```

### 测试依赖包

```
pytest>=7.4.0           # 测试框架
pytest-cov>=4.1.0       # 覆盖率插件
pytest-asyncio>=0.21.0  # 异步测试支持
black>=23.0.0           # 代码格式化
flake8>=6.0.0           # 代码检查
mypy>=1.5.0             # 类型检查
isort>=5.12.0           # 导入排序
bandit>=1.7.5           # 安全检查
```

### 配置文件

测试配置位于 `pyproject.toml`：

```toml
[tool.pytest.ini_options]
minversion = "7.0"
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "-v",
    "--strict-markers",
    "--tb=short",
    "--cov=src",
    "--cov-report=term-missing",
    "--cov-report=html",
]
markers = [
    "slow: marks tests as slow",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
]
```

---

## 测试类型

### 1. 单元测试 (Unit Tests)

单元测试验证单个函数或类的行为，是最基础的测试层次。

**位置**: `tests/` 目录下各模块子目录

**结构**:
```
tests/
├── ai_engine/           # AI 引擎测试
│   ├── test_engine.py
│   ├── test_translation.py
│   └── test_providers.py
├── security/            # 安全模块测试
│   ├── test_engine.py
│   ├── test_permissions.py
│   └── test_whitelist.py
├── template_engine/     # 模板引擎测试
│   ├── test_template_manager.py
│   └── test_template_validator.py
├── execution/           # 执行模块测试
│   └── test_executor.py
├── ui/                  # UI 模块测试
│   └── test_ui_manager.py
└── storage/             # 存储模块测试
    └── test_file_storage.py
```

**示例**:
```python
import pytest
from unittest.mock import Mock, patch
from src.ai_engine.engine import AIEngine

class TestAIEngine:
    """AI 引擎单元测试"""
    
    @pytest.fixture
    def engine(self):
        """创建测试用的引擎实例"""
        config = Mock()
        config.ai.model_path = "test_model"
        return AIEngine(config)
    
    def test_translate_simple_command(self, engine):
        """测试简单命令翻译"""
        result = engine.translate_natural_language("显示当前时间")
        
        assert result.generated_command == "Get-Date"
        assert result.confidence_score > 0.8
    
    def test_translate_with_context(self, engine):
        """测试带上下文的翻译"""
        context = Mock()
        context.command_history = ["Get-Process"]
        
        result = engine.translate_natural_language(
            "停止上一个进程", 
            context=context
        )
        
        assert "Stop-Process" in result.generated_command
```

### 2. 集成测试 (Integration Tests)

集成测试验证多个模块协作时的行为。

**位置**: `tests/integration/`

**测试文件**:
```
tests/integration/
├── test_end_to_end.py              # 端到端流程测试
├── test_security.py                # 安全集成测试
├── test_performance.py             # 性能测试
├── test_main_integration.py        # 主控制器集成测试
├── test_ui_integration.py          # UI 集成测试
├── test_custom_template_integration.py  # 自定义模板集成测试
├── test_chinese_language_support.py     # 中文支持测试
├── test_command_translation_accuracy.py # 命令翻译准确性测试
├── test_dangerous_command_blocking.py   # 危险命令阻止测试
├── test_response_time.py           # 响应时间测试
└── test_resource_usage.py          # 资源使用测试
```

**示例**:
```python
import pytest
from src.main import PowerShellAssistant
from src.interfaces.base import RiskLevel

class TestEndToEndFlow:
    """端到端流程测试"""
    
    @pytest.fixture
    def assistant(self):
        """创建测试用的助手实例"""
        return PowerShellAssistant()
    
    def test_complete_safe_command_flow(self, assistant):
        """测试安全命令的完整处理流程"""
        # 1. 用户输入
        user_input = "显示当前日期"
        
        # 2. 处理请求
        result = assistant.process_request(user_input, auto_execute=True)
        
        # 3. 验证结果
        assert result.success is True
        assert result.command == "Get-Date"
        assert result.output is not None
        
    def test_dangerous_command_blocked(self, assistant):
        """测试危险命令被阻止"""
        user_input = "删除所有文件"
        
        result = assistant.process_request(user_input, auto_execute=True)
        
        assert result.success is False
        assert "安全" in result.error or "阻止" in result.error
```

### 3. E2E 测试 (End-to-End Tests)

E2E 测试验证完整的用户场景。

**位置**: `tests/e2e/`

**示例**:
```python
import pytest
from src.main import PowerShellAssistant

class TestCustomTemplateWorkflow:
    """自定义模板工作流 E2E 测试"""
    
    def test_create_and_use_template(self, tmp_path):
        """测试创建和使用自定义模板"""
        assistant = PowerShellAssistant()
        
        # 1. 创建模板
        template_name = "test_backup"
        template_content = "Copy-Item -Path $source -Destination $dest"
        
        result = assistant.template_manager.create_template(
            name=template_name,
            content=template_content,
            variables=["source", "dest"]
        )
        assert result.success is True
        
        # 2. 使用模板
        use_result = assistant.template_manager.use_template(
            template_name,
            variables={"source": "C:/data", "dest": "D:/backup"}
        )
        assert use_result.success is True
        
        # 3. 验证生成的命令
        assert "Copy-Item" in use_result.generated_command
```

### 4. 性能测试

性能测试验证系统性能指标。

**位置**: `tests/integration/test_performance.py`

**性能指标**:
| 指标 | 目标值 | 说明 |
|-----|-------|------|
| AI 翻译延迟 | < 1秒 | 单次翻译响应时间 |
| 安全验证延迟 | < 100ms | 安全检查响应时间 |
| 命令执行延迟 | < 2秒 | 简单命令执行时间 |
| 完整请求延迟 | < 3秒 | 从输入到输出的总时间 |
| 内存使用 | < 100MB | 正常运行时内存占用 |

**示例**:
```python
import pytest
import time

class TestPerformance:
    """性能测试"""
    
    def test_translation_latency(self, assistant):
        """测试翻译延迟"""
        start_time = time.time()
        
        result = assistant.process_request("显示时间")
        
        elapsed = time.time() - start_time
        assert elapsed < 1.0, f"翻译延迟过高: {elapsed:.2f}秒"
        assert result.success is True
    
    def test_throughput(self, assistant):
        """测试吞吐量"""
        commands = ["显示时间", "列出进程", "检查网络"] * 10
        
        start_time = time.time()
        for cmd in commands:
            assistant.process_request(cmd)
        elapsed = time.time() - start_time
        
        throughput = len(commands) / elapsed
        assert throughput > 5, f"吞吐量过低: {throughput:.2f} 请求/秒"
```

### 5. 安全测试

安全测试验证系统的安全机制。

**位置**: `tests/integration/test_security.py`, `tests/security/`

**测试场景**:
- 危险命令阻止
- 权限检查
- 沙箱隔离
- 命令注入防护

**示例**:
```python
import pytest
from src.interfaces.base import RiskLevel

class TestSecurity:
    """安全测试"""
    
    @pytest.mark.parametrize("dangerous_command,expected_risk", [
        ("Remove-Item * -Recurse", RiskLevel.CRITICAL),
        ("Format-Volume C:", RiskLevel.CRITICAL),
        ("Stop-Computer", RiskLevel.HIGH),
        ("Get-Process", RiskLevel.SAFE),
    ])
    def test_risk_assessment(self, assistant, dangerous_command, expected_risk):
        """测试风险评估"""
        validation = assistant.security_engine.validate_command(dangerous_command)
        
        assert validation.risk_level == expected_risk
    
    def test_command_injection_prevention(self, assistant):
        """测试命令注入防护"""
        malicious_input = "显示时间; Remove-Item *"
        
        result = assistant.process_request(malicious_input)
        
        # 确保恶意部分被阻止或清理
        assert "Remove-Item" not in result.command or result.success is False
```

---

## 运行测试

### 使用 Makefile（推荐）

```bash
# 显示帮助
make help

# 运行所有测试
make test

# 只运行单元测试
make test-unit

# 只运行集成测试
make test-integration

# 运行测试并生成覆盖率报告
make coverage

# 运行代码质量检查
make quality
```

### 使用 pytest

```bash
# 运行所有测试
pytest

# 详细输出
pytest -v

# 显示打印输出
pytest -s

# 运行特定文件
pytest tests/test_main.py

# 运行特定测试类
pytest tests/test_main.py::TestProcessRequest

# 运行特定测试方法
pytest tests/test_main.py::TestProcessRequest::test_successful_request_processing

# 使用标记过滤
pytest -m unit          # 只运行单元测试
pytest -m integration   # 只运行集成测试
pytest -m "not slow"    # 跳过慢速测试

# 并行运行
pytest -n auto

# 失败时停止
pytest -x

# 只运行上次失败的测试
pytest --lf

# 生成覆盖率报告
pytest --cov=src --cov-report=html --cov-report=term
```

### 运行特定模块测试

```bash
# AI 引擎测试
pytest tests/ai_engine/ -v

# 安全模块测试
pytest tests/security/ -v

# 模板引擎测试
pytest tests/template_engine/ -v

# UI 模块测试
pytest tests/ui/ -v
```

### 运行 Web UI 测试

```bash
# 进入 web-ui 目录
cd web-ui

# 安装依赖
npm install

# 运行前端单元测试
npm run test

# 运行前端测试（单次）
npm run test:run

# 运行 E2E 测试
npm run test:e2e

# 运行后端测试
cd backend
pytest -v
```

---

## 编写测试

### 测试命名规范

```python
# 文件命名: test_<模块名>.py
# 例如: test_engine.py, test_template_manager.py

# 类命名: Test<功能描述>
class TestAIEngine:
    pass

# 方法命名: test_<场景>_<预期结果>
def test_translate_simple_command_returns_correct_result():
    pass

def test_invalid_input_raises_exception():
    pass
```

### 测试结构：AAA 模式

```python
def test_template_creation():
    # Arrange (准备)
    manager = TemplateManager()
    template_name = "test_template"
    template_content = "Get-Date"
    
    # Act (执行)
    result = manager.create_template(template_name, template_content)
    
    # Assert (断言)
    assert result.success is True
    assert manager.template_exists(template_name)
```

### 使用 Fixtures

```python
import pytest
from unittest.mock import Mock, MagicMock

@pytest.fixture
def mock_config():
    """Mock 配置对象"""
    config = Mock()
    config.ai.model_path = "test_model"
    config.security.strict_mode = True
    return config

@pytest.fixture
def assistant(mock_config):
    """创建测试用的助手实例"""
    with patch('src.main.ConfigManager') as mock_cm:
        mock_cm.return_value.load_config.return_value = mock_config
        return PowerShellAssistant()

@pytest.fixture
def temp_template_dir(tmp_path):
    """创建临时模板目录"""
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    return template_dir

def test_with_fixtures(assistant, temp_template_dir):
    """使用 fixtures 的测试"""
    assert assistant is not None
    assert temp_template_dir.exists()
```

### 参数化测试

```python
@pytest.mark.parametrize("input_text,expected_command", [
    ("显示时间", "Get-Date"),
    ("列出进程", "Get-Process"),
    ("检查网络", "Test-Connection"),
    ("查看服务", "Get-Service"),
])
def test_translation_accuracy(assistant, input_text, expected_command):
    """测试翻译准确性"""
    result = assistant.process_request(input_text)
    assert expected_command in result.command

@pytest.mark.parametrize("risk_level,should_block", [
    (RiskLevel.SAFE, False),
    (RiskLevel.LOW, False),
    (RiskLevel.MEDIUM, False),
    (RiskLevel.HIGH, True),
    (RiskLevel.CRITICAL, True),
])
def test_risk_level_blocking(assistant, risk_level, should_block):
    """测试风险等级阻止逻辑"""
    # ... 测试代码
```

### Mock 和 Patch

```python
from unittest.mock import Mock, MagicMock, patch, call

def test_with_mock():
    """使用 Mock 对象"""
    # 创建 Mock
    mock_engine = Mock()
    mock_engine.translate.return_value = "Get-Date"
    
    # 使用 Mock
    result = mock_engine.translate("显示时间")
    
    # 验证调用
    mock_engine.translate.assert_called_once_with("显示时间")
    assert result == "Get-Date"

def test_with_patch():
    """使用 patch 替换对象"""
    with patch('src.ai_engine.engine.AIEngine') as MockEngine:
        mock_instance = MockEngine.return_value
        mock_instance.translate.return_value = "Get-Process"
        
        engine = AIEngine(config)
        result = engine.translate("列出进程")
        
        assert result == "Get-Process"

def test_patch_decorator():
    """使用 patch 装饰器"""
    with patch('module.function') as mock_func:
        mock_func.return_value = 42
        
        result = module.function()
        
        assert result == 42
        mock_func.assert_called_once()
```

### 异步测试

```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_async_operation():
    """测试异步操作"""
    result = await async_function()
    assert result is not None

@pytest.mark.asyncio
async def test_async_with_timeout():
    """带超时的异步测试"""
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(
            slow_async_function(),
            timeout=1.0
        )
```

### 异常测试

```python
import pytest

def test_exception_raised():
    """测试异常被抛出"""
    with pytest.raises(ValueError) as exc_info:
        raise ValueError("测试异常")
    
    assert "测试异常" in str(exc_info.value)

def test_specific_exception():
    """测试特定异常"""
    with pytest.raises(FileNotFoundError):
        open("nonexistent_file.txt")

@pytest.mark.parametrize("invalid_input,expected_exception", [
    ("", ValueError),
    (None, TypeError),
    (-1, ValueError),
])
def test_input_validation(invalid_input, expected_exception):
    """测试输入验证"""
    with pytest.raises(expected_exception):
        validate_input(invalid_input)
```

---

## 测试覆盖率

### 生成覆盖率报告

```bash
# 生成覆盖率报告
pytest --cov=src --cov-report=html --cov-report=term

# 查看报告
# Windows
start htmlcov/index.html

# macOS
open htmlcov/index.html

# Linux
xdg-open htmlcov/index.html
```

### 覆盖率目标

| 模块 | 目标覆盖率 | 说明 |
|-----|-----------|------|
| 核心模块 | > 90% | AI引擎、安全引擎、执行器 |
| 工具模块 | > 80% | 存储引擎、日志引擎 |
| UI 模块 | > 70% | 用户界面组件 |
| 配置模块 | > 85% | 配置管理 |

### 覆盖率配置

```toml
# pyproject.toml
[tool.coverage.run]
source = ["src"]
omit = [
    "*/tests/*",
    "*/test_*.py",
    "*/__pycache__/*",
]

[tool.coverage.report]
precision = 2
show_missing = true
skip_covered = false
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
]
```

---

## 测试报告

### 自动生成测试报告

```bash
# 运行测试并生成报告
python run_all_tests.py

# 报告位置
# test_results/test_results_latest.json
# test_reports/test_report_latest.md
```

### 测试报告结构

```
test_reports/
├── test_report_latest.md          # 最新测试报告
├── test_report_20260220_122708.md # 历史报告
└── ...

test_results/
├── test_results_latest.json       # 最新测试结果
├── test_results_20260220_122222.json
└── ...
```

### 测试报告内容

测试报告包含以下信息：

1. **测试摘要**
   - 总测试数
   - 通过/失败数
   - 执行时间

2. **详细结果**
   - 每个测试文件的状态
   - 失败测试的错误信息
   - 性能指标

3. **覆盖率统计**
   - 模块覆盖率
   - 分支覆盖率
   - 未覆盖代码行

---

## 常见问题

### Q1: 测试运行失败怎么办？

```bash
# 1. 检查依赖是否安装
pip install -r requirements-dev.txt

# 2. 清理缓存
pytest --cache-clear

# 3. 查看详细错误
pytest -v --tb=long

# 4. 只运行失败的测试
pytest --lf -v
```

### Q2: 如何跳过某些测试？

```python
import pytest

@pytest.mark.skip(reason="功能尚未实现")
def test_future_feature():
    pass

@pytest.mark.skipif(sys.version_info < (3, 8), reason="需要 Python 3.8+")
def test_python38_feature():
    pass

# 运行时跳过
pytest -m "not slow"  # 跳过标记为 slow 的测试
```

### Q3: 如何测试需要 PowerShell 的功能？

```python
import pytest
import subprocess

@pytest.fixture
def powershell_available():
    """检查 PowerShell 是否可用"""
    try:
        subprocess.run(["pwsh", "-c", "echo test"], capture_output=True)
        return True
    except FileNotFoundError:
        return False

@pytest.mark.skipif(not powershell_available(), reason="PowerShell 不可用")
def test_powershell_execution():
    """测试 PowerShell 执行"""
    # ... 测试代码
```

### Q4: 如何调试测试？

```bash
# 使用 pdb 调试
pytest --pdb

# 在代码中设置断点
import pdb; pdb.set_trace()

# 使用 pytest 的 verbose 模式
pytest -v -s

# 只运行特定测试并显示输出
pytest tests/test_main.py::test_specific -v -s
```

### Q5: 如何处理测试中的临时文件？

```python
def test_with_temp_file(tmp_path):
    """使用 pytest 提供的临时目录"""
    # tmp_path 是 pytest 提供的临时目录
    temp_file = tmp_path / "test.txt"
    temp_file.write_text("test content")
    
    # 测试代码...
    
    # 临时文件会在测试结束后自动清理

def test_with_temp_dir(tmp_path):
    """创建临时目录结构"""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    
    config_file = config_dir / "config.yaml"
    config_file.write_text("key: value")
    
    # 使用临时配置目录
    manager = ConfigManager(config_path=str(config_file))
```

### Q6: 如何模拟用户输入？

```python
from unittest.mock import patch
from io import StringIO

def test_user_input():
    """测试用户输入"""
    with patch('builtins.input', return_value='y'):
        result = get_user_confirmation()
        assert result is True

def test_multiple_inputs():
    """测试多次用户输入"""
    with patch('builtins.input', side_effect=['input1', 'input2', 'exit']):
        interactive_mode()
```

---

## 持续集成

### GitHub Actions 配置

项目使用 GitHub Actions 进行持续集成测试：

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Run tests
        run: pytest -v --cov=src --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### 本地 CI 模拟

```bash
# 运行完整的 CI 检查
make ci

# 这将运行：
# 1. 代码格式检查
# 2. 代码质量检查
# 3. 类型检查
# 4. 所有测试
# 5. 覆盖率报告
```

---

## 最佳实践

### 1. 测试原则

- **独立性**: 每个测试应该独立运行，不依赖其他测试
- **可重复性**: 测试结果应该可重复
- **自验证**: 测试应该自动判断通过/失败
- **及时性**: 测试应该快速运行

### 2. 测试组织

```
tests/
├── conftest.py           # 共享 fixtures
├── test_main.py          # 主模块测试
├── ai_engine/            # AI 引擎测试
│   ├── __init__.py
│   ├── conftest.py       # 模块特定 fixtures
│   └── test_engine.py
└── integration/          # 集成测试
    ├── __init__.py
    └── test_end_to_end.py
```

### 3. 测试数据管理

```python
# 使用 fixtures 管理测试数据
@pytest.fixture
def sample_template():
    return {
        "name": "test_template",
        "content": "Get-Date",
        "variables": []
    }

@pytest.fixture
def sample_commands():
    return [
        {"input": "显示时间", "expected": "Get-Date"},
        {"input": "列出进程", "expected": "Get-Process"},
    ]
```

### 4. 清理测试环境

```python
@pytest.fixture
def clean_environment():
    """确保测试环境干净"""
    # 设置
    original_env = os.environ.copy()
    
    yield
    
    # 清理
    os.environ.clear()
    os.environ.update(original_env)
```

---

## 参考资源

- [Pytest 官方文档](https://docs.pytest.org/)
- [Python 测试最佳实践](https://docs.python-guide.org/writing/tests/)
- [测试驱动开发 (TDD)](https://en.wikipedia.org/wiki/Test-driven_development)
- [覆盖率工具 Coverage.py](https://coverage.readthedocs.io/)

---

## 联系支持

如果在测试过程中遇到问题：

1. 查看 [常见问题](#常见问题) 部分
2. 查看项目 [Issues](https://github.com/0green7hand0/AI-PowerShell/issues)
3. 提交新的 Issue 并附上详细错误信息
