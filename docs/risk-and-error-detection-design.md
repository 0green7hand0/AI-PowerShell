# 风险度评分与错误检测设计文档

本文档详细说明 AI PowerShell 智能助手中风险度评分和错误检测的设计原理与实现细节。

---

## 目录

1. [风险度评分设计](#一风险度评分设计)
2. [错误检测与处理机制](#二错误检测与处理机制)
3. [代码实现参考](#三代码实现参考)

---

## 一、风险度评分设计

### 1.1 风险等级定义

风险等级是一个枚举类型，共 5 个级别：

```python
class RiskLevel(Enum):
    SAFE = "safe"           # 安全命令
    LOW = "low"             # 低风险
    MEDIUM = "medium"       # 中等风险
    HIGH = "high"           # 高风险
    CRITICAL = "critical"   # 严重风险
```

| 等级 | 图标 | 含义 | 是否需要确认 |
|------|------|------|-------------|
| SAFE | ✅ | 只读操作，无副作用 | 否 |
| LOW | ℹ️ | 轻微影响，可恢复 | 视配置 |
| MEDIUM | ⚠️ | 修改系统状态 | 是 |
| HIGH | 🚨 | 重大影响，难恢复 | 是 |
| CRITICAL | 💀 | 不可逆操作，危险 | 是 |

### 1.2 三层验证机制

风险度评分采用三层安全验证机制：

```
命令输入
    │
    ▼
┌─────────────────────────────────────┐
│  第一层：白名单验证                   │
│  - 检查危险命令模式                   │
│  - 检查安全命令前缀                   │
│  - 检查管道中的危险命令               │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  第二层：权限检查                     │
│  - 检查是否需要管理员权限             │
│  - 检查当前用户是否有足够权限         │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  第三层：沙箱执行（可选）              │
│  - 在隔离环境中执行                   │
└─────────────────────────────────────┘
```

### 1.3 危险命令模式匹配

系统预定义了多种危险命令模式（正则表达式匹配）：

#### CRITICAL 级别（严重风险）

| 模式 | 说明 |
|------|------|
| `Remove-Item.*-Recurse.*-Force` | 递归强制删除 |
| `Remove-Item.*C:\\Windows` | 删除系统目录 |
| `Format-Volume` | 格式化磁盘 |
| `Clear-Disk` | 清空磁盘 |
| `Invoke-WebRequest.*\|\s*Invoke-Expression` | 下载并执行代码 |

#### HIGH 级别（高风险）

| 模式 | 说明 |
|------|------|
| `Stop-Computer` | 关闭计算机 |
| `Restart-Computer` | 重启计算机 |
| `Remove-LocalUser` | 删除本地用户 |
| `Set-ExecutionPolicy.*Unrestricted` | 设置无限制执行策略 |
| `Stop-Process.*-Name explorer` | 终止资源管理器 |

#### MEDIUM 级别（中等风险）

| 模式 | 说明 |
|------|------|
| `Stop-Process.*-Force` | 强制终止进程 |
| `Set-ItemProperty.*HKLM:` | 修改注册表 |
| `Invoke-Expression` | 执行动态代码 |

### 1.4 安全命令识别

#### 安全命令前缀（只读操作）

```python
SAFE_PREFIXES = [
    "Get-", "Show-", "Test-", "Find-", "Search-",
    "Select-", "Where-", "Sort-", "Group-", "Measure-",
    "Compare-", "Format-", "Out-", "ConvertTo-", "ConvertFrom-",
    "Export-", "Import-",
    "Write-Host", "Write-Output", "echo",
]
```

#### 需要确认的命令前缀（修改操作）

```python
CONFIRMATION_PREFIXES = [
    "Set-", "New-", "Remove-", "Clear-", "Reset-",
    "Start-", "Stop-", "Restart-", "Enable-", "Disable-",
    "Add-", "Update-", "Install-", "Uninstall-",
    "Copy-", "Move-", "Rename-",
]
```

### 1.5 风险评估流程

```python
def validate(self, command: str) -> ValidationResult:
    # 1. 检查自定义安全命令列表
    if command in self.custom_safe_commands:
        return ValidationResult(risk_level=RiskLevel.SAFE)
    
    # 2. 检查危险模式匹配
    for pattern, description, risk_level in self._compiled_patterns:
        if pattern.search(command):
            return ValidationResult(
                is_valid=False,
                risk_level=risk_level,
                blocked_reasons=[f"检测到危险命令: {description}"]
            )
    
    # 3. 检查管道中是否有危险命令
    if '|' in command:
        for dangerous_cmd in PIPELINE_DANGEROUS_COMMANDS:
            if dangerous_cmd in command:
                return ValidationResult(
                    risk_level=RiskLevel.HIGH,
                    requires_confirmation=True
                )
    
    # 4. 检查安全前缀
    if command.startswith(any(SAFE_PREFIXES)):
        return ValidationResult(risk_level=RiskLevel.SAFE)
    
    # 5. 检查需要确认的前缀
    if command.startswith(any(CONFIRMATION_PREFIXES)):
        return ValidationResult(
            risk_level=RiskLevel.MEDIUM,
            requires_confirmation=True
        )
    
    # 6. 未知命令
    return ValidationResult(risk_level=RiskLevel.LOW)
```

### 1.6 具体示例

#### 示例1：安全命令

```
命令: Get-Process
风险等级: SAFE ✅
原因: 以 "Get-" 开头，只读操作
```

#### 示例2：中等风险命令

```
命令: New-Item -ItemType Directory -Name "test"
风险等级: MEDIUM ⚠️
原因: 以 "New-" 开头，会创建新目录
需要确认: 是
```

#### 示例3：高风险命令

```
命令: Stop-Computer
风险等级: HIGH 🚨
原因: 匹配危险模式 "关闭计算机"
需要确认: 是
```

#### 示例4：严重风险命令

```
命令: Remove-Item C:\Windows -Recurse -Force
风险等级: CRITICAL 💀
原因: 匹配危险模式 "递归强制删除系统目录"
直接阻止: 是
```

---

## 二、错误检测与处理机制

### 2.1 整体流程

```
AI 生成命令
    │
    ▼
┌─────────────────────────────────────┐
│  错误检测 (ErrorDetector)            │
│  - 检测各类语法错误                   │
│  - 返回错误列表                       │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  错误修正 (fix)                      │
│  - 尝试自动修正错误                   │
│  - 返回修正后的建议                   │
└─────────────────────────────────────┘
    │
    ▼
  返回最终命令
```

### 2.2 错误检测类型

| 错误类型 | 检测方法 | 示例 |
|---------|---------|------|
| 空命令 | 检查命令是否为空 | `""` |
| 引号不匹配 | 检查单/双引号数量是否为偶数 | `"test` |
| 括号不匹配 | 使用栈检查括号配对 | `Get-Process (` |
| 管道语法错误 | 检查管道符前后是否有内容 | `Get-Process |` |
| 参数格式错误 | 检查参数名是否有效 | `Get-Item -1path` |
| 拼写错误 | 匹配常见错误字典 | `Get-Childs` |

### 2.3 具体检测实现

#### 引号匹配检测

```python
def _check_quotes(self, command: str) -> bool:
    single_quotes = command.count("'")
    double_quotes = command.count('"')
    return single_quotes % 2 == 0 and double_quotes % 2 == 0
```

#### 括号匹配检测（栈算法）

```python
def _check_brackets(self, command: str) -> bool:
    stack = []
    pairs = {'(': ')', '{': '}', '[': ']'}
    
    for char in command:
        if char in pairs.keys():        # 遇到开括号，入栈
            stack.append(char)
        elif char in pairs.values():    # 遇到闭括号
            if not stack:               # 栈空，说明多了一个闭括号
                return False
            if pairs[stack[-1]] != char:  # 括号类型不匹配
                return False
            stack.pop()                 # 匹配成功，出栈
    
    return len(stack) == 0              # 栈空则完全匹配
```

#### 管道语法检测

```python
def _check_pipe_syntax(self, command: str) -> bool:
    if '|' in command:
        parts = command.split('|')
        for part in parts:
            if not part.strip():        # 管道符前后不能为空
                return False
    return True
```

#### 拼写错误检测

```python
common_errors = {
    'Get-Childs': 'Get-ChildItem',
    'Get-Child': 'Get-ChildItem',
    'Get-Dir': 'Get-ChildItem',
    'Get-Procs': 'Get-Process',
    'Get-Proc': 'Get-Process',
    'Get-Svc': 'Get-Service',
    '-Recursive': '-Recurse',
    '-Forced': '-Force',
}
```

### 2.4 自动修正机制

#### 修正流程

```python
def fix(self, suggestion: Suggestion) -> Suggestion:
    command = suggestion.generated_command
    errors = self.detect_errors(command)
    
    if not errors:
        return suggestion
    
    # 尝试修正每个错误
    fixed_command = command
    for error_type, error_desc in errors:
        fixed_command = self._fix_error(fixed_command, error_type)
    
    # 如果修正后仍有错误，返回原建议
    if self.has_errors(fixed_command):
        return suggestion
    
    # 返回修正后的建议，置信度降低 10%
    return Suggestion(
        generated_command=fixed_command,
        confidence_score=suggestion.confidence_score * 0.9,
        explanation=f"{suggestion.explanation} (已自动修正)",
    )
```

#### 修正方法

| 错误类型 | 修正方法 |
|---------|---------|
| 引号不匹配 | 在末尾添加缺失的引号 |
| 括号不匹配 | 在末尾添加缺失的闭括号 |
| 管道语法错误 | 移除空的管道段 |
| 拼写错误 | 替换为正确拼写 |

### 2.5 改进建议功能

系统还会提供命令改进建议：

```python
def suggest_improvements(self, command: str) -> List[str]:
    suggestions = []
    
    # 危险操作建议添加错误处理
    if 'Remove-Item' in command and '-ErrorAction' not in command:
        suggestions.append('考虑添加 -ErrorAction 参数处理错误')
    
    # 建议添加确认
    if 'Remove-Item' in command and '-Confirm' not in command:
        suggestions.append('考虑添加 -Confirm 参数以确认删除操作')
    
    # 建议使用 -WhatIf 预览
    if any(cmd in command for cmd in ['Remove-Item', 'Move-Item', 'Set-']):
        if '-WhatIf' not in command:
            suggestions.append('可以使用 -WhatIf 参数预览操作结果')
    
    return suggestions
```

### 2.6 处理示例

#### 示例1：引号不匹配

```
原始命令: Get-Content "test.txt
检测结果: ('quotes', '引号不匹配')
修正结果: Get-Content "test.txt"
置信度: 原置信度 × 0.9
```

#### 示例2：括号不匹配

```
原始命令: Get-Process | Where-Object {$_.CPU -gt 10
检测结果: ('brackets', '括号不匹配')
修正结果: Get-Process | Where-Object {$_.CPU -gt 10}
```

#### 示例3：拼写错误

```
原始命令: Get-Childs -Recursive
检测结果: ('spelling', 'Get-Childs -> Get-ChildItem')
         ('spelling', '-Recursive -> -Recurse')
修正结果: Get-ChildItem -Recurse
```

#### 示例4：管道语法错误

```
原始命令: Get-Process | | Stop-Process
检测结果: ('pipe', '管道语法错误')
修正结果: Get-Process | Stop-Process
```

---

## 三、代码实现参考

### 3.1 相关文件

| 文件路径 | 说明 |
|---------|------|
| `src/security/engine.py` | 安全引擎主类，三层验证协调 |
| `src/security/whitelist.py` | 白名单验证器，危险模式匹配 |
| `src/ai_engine/error_detection.py` | 错误检测器，语法检查与修正 |
| `src/interfaces/base.py` | RiskLevel 枚举、ValidationResult 数据模型 |

### 3.2 关键数据模型

#### ValidationResult

```python
@dataclass
class ValidationResult:
    is_valid: bool                    # 是否通过验证
    risk_level: RiskLevel             # 风险等级
    blocked_reasons: List[str]        # 阻止原因列表
    requires_confirmation: bool       # 是否需要用户确认
    requires_elevation: bool          # 是否需要权限提升
    warnings: List[str]               # 警告信息列表
```

---

## 四、总结

### 风险度评分

| 特性 | 说明 |
|------|------|
| 目的 | 评估命令危险性，保护系统安全 |
| 等级 | SAFE → LOW → MEDIUM → HIGH → CRITICAL |
| 机制 | 三层验证：白名单 + 权限 + 沙箱 |
| 依据 | 命令模式匹配 + 命令前缀识别 |

### 错误检测与处理

| 特性 | 说明 |
|------|------|
| 目的 | 检测并修正 AI 生成命令的语法错误 |
| 检测类型 | 引号、括号、管道、参数、拼写 |
| 修正策略 | 自动修正 + 降低置信度 |
| 改进建议 | 提供 -WhatIf、-Confirm 等建议 |
