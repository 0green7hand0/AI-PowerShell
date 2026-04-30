# 安全规则库、设计模式与测试体系文档

本文档总结 AI PowerShell 智能助手的安全规则库、主控制器设计模式和测试体系。

---

## 目录

1. [安全规则库统计](#一安全规则库统计)
2. [主控制器设计模式](#二主控制器设计模式)
3. [测试体系概览](#三测试体系概览)

---

## 一、安全规则库统计

### 1.1 规则数量总览

| 规则类型 | 数量 |
|---------|------|
| **危险命令模式 (DANGEROUS_PATTERNS)** | 27 条 |
| **安全命令前缀 (SAFE_PREFIXES)** | 18 条 |
| **管道危险命令 (PIPELINE_DANGEROUS_COMMANDS)** | 11 条 |
| **需确认命令前缀 (CONFIRMATION_PREFIXES)** | 16 条 |

### 1.2 危险命令模式分类

#### 按风险等级分布

| 风险等级 | 数量 | 占比 |
|---------|------|------|
| CRITICAL | 10 条 | 37% |
| HIGH | 13 条 | 48% |
| MEDIUM | 4 条 | 15% |

#### 按操作类别分布

| 类别 | 数量 | 具体规则 |
|------|------|---------|
| **文件系统操作** | 6 条 | 递归强制删除、删除系统目录、格式化磁盘、清空磁盘等 |
| **系统控制** | 4 条 | 关闭/重启计算机、强制停止服务、禁用系统功能 |
| **注册表操作** | 3 条 | 删除/修改系统级注册表项 |
| **网络和防火墙** | 3 条 | 禁用网络适配器、禁用防火墙、添加防火墙规则 |
| **进程和任务** | 3 条 | 强制终止进程、终止资源管理器/登录进程 |
| **用户和权限** | 3 条 | 删除/禁用用户、添加管理员 |
| **脚本执行** | 3 条 | 设置无限制执行策略、执行动态代码、远程执行脚本 |
| **数据下载和执行** | 5 条 | 下载并执行代码、绕过执行策略等 |

### 1.3 详细规则列表

#### CRITICAL 级别（10条）

```python
# 文件系统
r"Remove-Item.*-Recurse.*-Force"      # 递归强制删除
r"Remove-Item.*C:\\Windows"           # 删除系统目录
r"Remove-Item.*C:\\Program Files"     # 删除程序目录
r"Format-Volume"                       # 格式化磁盘
r"Clear-Disk"                          # 清空磁盘

# 进程
r"Stop-Process.*-Name\s+winlogon"     # 终止登录进程

# 数据下载执行
r"Invoke-WebRequest.*\|\s*Invoke-Expression"  # 下载并执行
r"wget.*\|\s*iex"                      # 下载并执行（简写）
r"curl.*\|\s*iex"                      # 下载并执行（简写）
r"Start-Process.*powershell.*-e"      # 执行编码命令
```

#### HIGH 级别（13条）

```python
# 文件系统
r"Remove-Item.*\*.*-Recurse"          # 递归删除所有文件

# 系统控制
r"Stop-Computer"                       # 关闭计算机
r"Restart-Computer"                    # 重启计算机
r"Stop-Service.*-Force"                # 强制停止服务
r"Disable-WindowsOptionalFeature"      # 禁用系统功能

# 注册表
r"Remove-Item.*HKLM:"                  # 删除注册表（系统级）
r"Remove-ItemProperty.*HKLM:"          # 删除注册表值（系统级）

# 网络
r"Disable-NetAdapter"                  # 禁用网络适配器
r"Set-NetFirewallProfile.*-Enabled\s+False"  # 禁用防火墙

# 进程
r"Stop-Process.*-Name\s+explorer"      # 终止资源管理器

# 用户权限
r"Remove-LocalUser"                    # 删除本地用户
r"Add-LocalGroupMember.*Administrators"  # 添加管理员

# 脚本执行
r"Set-ExecutionPolicy.*Unrestricted"   # 无限制执行策略
r"powershell.*-ExecutionPolicy.*Bypass"  # 绕过执行策略
r"powershell.*-ep.*bypass"             # 绕过执行策略（简写）
```

#### MEDIUM 级别（4条）

```python
# 注册表
r"Set-ItemProperty.*HKLM:.*-Force"    # 强制修改注册表

# 网络
r"New-NetFirewallRule.*-Action\s+Allow"  # 添加防火墙规则

# 进程
r"Stop-Process.*-Force"                # 强制终止进程

# 脚本
r"Invoke-Expression"                   # 执行动态代码
r"Invoke-Command.*-ScriptBlock"        # 远程执行脚本
```

### 1.4 安全命令识别

#### 安全命令前缀（18条）

```python
SAFE_PREFIXES = [
    "Get-", "Show-", "Test-", "Find-", "Search-",
    "Select-", "Where-", "Sort-", "Group-", "Measure-",
    "Compare-", "Format-", "Out-", "ConvertTo-", "ConvertFrom-",
    "Export-", "Import-",
    "Write-Host", "Write-Output", "echo",
]
```

#### 需要确认的命令前缀（16条）

```python
CONFIRMATION_PREFIXES = [
    "Set-", "New-", "Remove-", "Clear-", "Reset-",
    "Start-", "Stop-", "Restart-", "Enable-", "Disable-",
    "Add-", "Update-", "Install-", "Uninstall-",
    "Copy-", "Move-", "Rename-",
]
```

### 1.5 覆盖的高危操作类别

| 类别 | 风险 | 覆盖情况 |
|------|------|---------|
| ✅ 文件系统破坏 | CRITICAL | 递归删除、格式化、清空磁盘 |
| ✅ 系统关机/重启 | HIGH | 关机、重启、禁用功能 |
| ✅ 注册表篡改 | HIGH/MEDIUM | 删除/修改系统级注册表 |
| ✅ 网络安全 | HIGH | 禁用网卡、防火墙 |
| ✅ 进程终止 | CRITICAL/HIGH | 终止关键系统进程 |
| ✅ 用户管理 | HIGH | 删除用户、提权 |
| ✅ 恶意代码执行 | CRITICAL | 下载执行、绕过策略 |
| ✅ 远程执行 | MEDIUM | 远程命令、动态代码 |

---

## 二、主控制器设计模式

### 2.1 核心设计模式：外观模式

主控制器 `PowerShellAssistant` 采用外观模式作为核心设计模式。

```python
class PowerShellAssistant:
    def __init__(self, config_path: Optional[str] = None):
        # 统一初始化所有子系统
        self.config_manager = ConfigManager(config_path)
        self.log_engine = LogEngine(self.config.logging)
        self.storage = StorageFactory.create_storage(...)
        self.context_manager = ContextManager(storage=self.storage)
        self.ai_engine = AIEngine(...)
        self.security_engine = SecurityEngine(...)
        self.executor = CommandExecutor(...)
        self.template_engine = TemplateEngine(...)
        self.ui_manager = UIManager(...)
        # ... 更多组件
```

#### 外观模式的优势

| 优势 | 说明 |
|------|------|
| **简化接口** | 用户只需与 `PowerShellAssistant` 交互，无需了解内部 10+ 个子系统 |
| **解耦** | 客户端与子系统解耦，子系统可独立变化 |
| **分层** | 将复杂的初始化和协调逻辑封装在内部 |

### 2.2 其他设计模式

#### 依赖注入模式

```python
def __init__(self, config_path: Optional[str] = None):
    self.config = self.config_manager.load_config()
    self.ai_engine = AIEngine(self.config.ai.model_dump())
    self.security_engine = SecurityEngine(self.config.security.model_dump())
    self.executor = CommandExecutor(executor_config)
```

**优势：**
- 组件之间松耦合
- 便于单元测试（可注入 Mock 对象）
- 配置集中管理

#### 模板方法模式

```python
def process_request(self, user_input: str, auto_execute: bool = False):
    # 固定的处理步骤
    # 1. 记录请求
    # 2. 获取上下文
    # 3. AI 翻译
    # 4. 安全验证
    # 5. 用户确认
    # 6. 执行命令
    # 7. 保存历史
    # 8. 更新上下文
```

**优势：**
- 定义了算法骨架，步骤固定
- 子类可重写特定步骤

#### 策略模式

```python
def process_request(self, user_input: str, auto_execute: bool = False):
    if self._is_script_generation_request(user_input):
        return self._handle_script_generation(...)  # 策略A
    return self._handle_command_translation(...)    # 策略B
```

**优势：**
- 运行时动态选择处理策略
- 新增策略不影响现有代码

### 2.3 设计模式组合图

```
┌─────────────────────────────────────────────────────────────┐
│                    PowerShellAssistant                      │
│                      (外观模式 Facade)                       │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐   │
│  │           process_request() - 模板方法               │   │
│  │  ┌─────────────────┐    ┌─────────────────────────┐ │   │
│  │  │ 命令翻译策略     │    │ 脚本生成策略            │ │   │
│  │  │ (Strategy A)    │    │ (Strategy B)            │ │   │
│  │  └─────────────────┘    └─────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                    依赖注入 (DI)                            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │AIEngine  │ │Security  │ │Executor  │ │Storage   │      │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### 2.4 设计模式总结

| 设计模式 | 作用 | 应用场景 |
|---------|------|---------|
| **外观模式** | 统一入口，封装复杂性 | 协调 10+ 个子系统 |
| **依赖注入** | 解耦组件，便于测试 | 初始化各引擎组件 |
| **模板方法** | 定义处理流程骨架 | `process_request` 流程 |
| **策略模式** | 动态选择处理方式 | 命令翻译 vs 脚本生成 |
| **工厂模式** | 创建复杂对象 | `StorageFactory` |

---

## 三、测试体系概览

### 3.1 测试文件统计

| 测试类型 | 目录 | 文件数 | 测试类数（估算） |
|---------|------|--------|-----------------|
| **单元测试** | `tests/*/` | 45+ 个 | 100+ 个 |
| **集成测试** | `tests/integration/` | 11 个 | 30+ 个 |
| **端到端测试** | `tests/e2e/` | 1 个 | 3 个 |
| **Web UI 测试** | `web-ui/backend/tests/` | 9 个 | 20+ 个 |

**总计：约 66+ 个测试文件**

### 3.2 单元测试覆盖

#### AI 引擎模块

| 测试文件 | 测试内容 |
|---------|---------|
| `test_engine.py` | AI 引擎核心功能、缓存机制 |
| `test_translation.py` | 自然语言翻译、规则匹配 |
| `test_error_detection.py` | 语法错误检测、自动修正 |
| `test_providers.py` | AI 提供商接口 |

#### 安全模块

| 测试文件 | 测试内容 |
|---------|---------|
| `test_whitelist.py` | 白名单验证、危险命令检测（20+ 测试用例） |
| `test_engine.py` | 安全引擎三层验证 |
| `test_permissions.py` | 权限检查 |
| `test_sandbox.py` | 沙箱隔离 |

#### 执行模块

| 测试文件 | 测试内容 |
|---------|---------|
| `test_executor.py` | 命令执行、超时处理 |
| `test_platform_adapter.py` | 平台适配 |
| `test_output_formatter.py` | 输出格式化 |

#### 其他模块

| 模块 | 测试文件数 |
|------|-----------|
| 配置管理 | 2 |
| 上下文管理 | 3 |
| 存储引擎 | 4 |
| 日志引擎 | 3 |
| UI 系统 | 10 |
| 模板引擎 | 10 |

### 3.3 集成测试覆盖

| 测试文件 | 测试场景 | 测试用例数 |
|---------|---------|-----------|
| `test_end_to_end.py` | 端到端流程、模块协作、错误处理 | 12+ |
| `test_performance.py` | AI 翻译性能、安全验证性能、执行性能 | 15+ |
| `test_security.py` | 危险命令阻止、权限检查、沙箱隔离 | 20+ |
| `test_main_integration.py` | 主控制器集成 | 5+ |
| `test_command_translation_accuracy.py` | 命令翻译准确率 | 102 个场景 |
| `test_dangerous_command_blocking.py` | 危险命令拦截 | 60+ |
| `test_chinese_language_support.py` | 中文语言支持 | 32 个场景 |
| `test_response_time.py` | 响应时间测试 | 5 |
| `test_resource_usage.py` | 资源占用测试 | 4 |

### 3.4 测试覆盖率目标

| 测试类型 | 覆盖率目标 |
|---------|-----------|
| 端到端流程 | > 90% |
| 模块协作 | > 85% |
| 错误处理 | > 80% |
| 性能测试 | 所有关键路径 |
| 安全测试 | 所有安全机制 |

### 3.5 性能基准测试结果

| 指标 | 目标 | 实测 |
|------|------|------|
| AI 翻译延迟 | < 1秒 | ~1.5ms（规则匹配） |
| 安全验证延迟 | < 100ms | - |
| 命令执行延迟 | < 2秒 | - |
| 完整请求延迟 | < 3秒 | - |
| 空闲内存占用 | < 100MB | 78MB |
| 空闲 CPU 占用 | < 5% | 0.0% |

### 3.6 测试运行命令

```bash
# 运行所有单元测试
python -m pytest tests/ -v

# 运行集成测试
python -m pytest tests/integration/ -v

# 运行特定模块测试
python -m pytest tests/security/ -v
python -m pytest tests/ai_engine/ -v

# 生成覆盖率报告
python -m pytest tests/ --cov=src --cov-report=html

# 运行性能测试
python -m pytest tests/integration/test_performance.py -v -s
```

### 3.7 测试覆盖情况总结

| 维度 | 覆盖情况 |
|------|---------|
| **核心模块** | ✅ AI引擎、安全引擎、执行器、存储 |
| **安全机制** | ✅ 白名单、权限、沙箱、危险命令 |
| **错误处理** | ✅ 语法检测、自动修正、异常处理 |
| **性能测试** | ✅ 响应时间、资源占用、吞吐量 |
| **中文支持** | ✅ 32 个中文场景测试 |
| **模板引擎** | ✅ 创建、编辑、删除、验证、版本控制 |
| **Web UI** | ✅ API、认证、历史、配置 |

**估计总体测试覆盖率：约 70-80%**（核心模块覆盖率更高）
