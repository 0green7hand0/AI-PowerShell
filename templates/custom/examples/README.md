# 自定义模板示例

本目录包含三个示例自定义模板，展示如何创建和使用自定义 PowerShell 脚本模板。

## 📋 示例模板列表

### 1. simple_backup.ps1 - 简单文件备份工具

**功能**: 将指定目录的文件备份到目标位置，支持增量备份和压缩

**参数**:
- `SOURCE_PATH` (path, 必需): 源文件夹路径
- `DEST_PATH` (path, 必需): 备份目标路径
- `COMPRESS` (boolean, 可选): 是否压缩备份，默认 false
- `INCREMENTAL` (boolean, 可选): 是否增量备份，默认 false

**使用场景**:
- 定期备份重要文件
- 项目文件备份
- 文档自动备份

**示例请求**:
```
帮我创建一个备份脚本，备份我的文档到D盘
生成一个压缩备份脚本
```

---

### 2. log_analyzer.ps1 - 日志文件分析工具

**功能**: 分析日志文件，统计错误、警告信息，生成分析报告

**参数**:
- `LOG_PATH` (path, 必需): 日志文件或目录路径
- `ERROR_PATTERN` (string, 可选): 错误匹配模式，默认 "error|exception|fail"
- `WARNING_PATTERN` (string, 可选): 警告匹配模式，默认 "warning|warn"
- `OUTPUT_REPORT` (boolean, 可选): 是否生成报告文件，默认 true
- `REPORT_PATH` (path, 可选): 报告保存路径

**使用场景**:
- 应用程序日志分析
- 系统日志监控
- 错误排查

**示例请求**:
```
分析系统日志，找出所有错误和警告
帮我分析应用日志文件
```

---

### 3. user_report.ps1 - 用户活动报告生成器

**功能**: 生成系统用户活动报告，包括登录历史、磁盘使用、进程信息等

**参数**:
- `USERNAME` (string, 可选): 要查询的用户名，默认当前用户
- `INCLUDE_PROCESSES` (boolean, 可选): 是否包含进程信息，默认 true
- `INCLUDE_DISK_USAGE` (boolean, 可选): 是否包含磁盘使用信息，默认 true
- `SAVE_REPORT` (boolean, 可选): 是否保存报告，默认 true
- `REPORT_FORMAT` (string, 可选): 报告格式 (txt/html/json)，默认 "txt"

**使用场景**:
- 系统使用情况统计
- 用户活动监控
- 资源使用分析

**示例请求**:
```
生成当前用户的活动报告
创建一个HTML格式的系统报告
```

---

## 🎯 如何使用这些示例

### 方法1: 通过 AI 助手使用

这些模板已经集成到系统中，您可以直接通过自然语言使用：

```bash
python src/main.py

# 然后输入类似的请求
💬 请输入 > 帮我备份文档文件夹到D盘
```

AI 会自动识别并使用相应的模板。

### 方法2: 直接执行

您也可以直接执行这些脚本（需要手动替换参数）：

```powershell
# 复制模板
cp templates/custom/examples/simple_backup.ps1 my_backup.ps1

# 编辑参数
# 将 {{SOURCE_PATH}} 替换为实际路径

# 执行
.\my_backup.ps1
```

### 方法3: 作为创建新模板的参考

这些示例展示了良好的模板编写实践：

- 详细的注释和文档
- 清晰的参数定义
- 用户友好的输出
- 完善的错误处理
- 进度提示和结果反馈

您可以参考这些示例创建自己的模板：

```bash
python src/main.py template create
```

---

## 📚 学习要点

### 1. 参数占位符格式

```powershell
# 字符串参数
[string]$Path = "{{PATH}}"

# 数字参数
[int]$Count = {{COUNT}}

# 布尔参数
[bool]$Enable = ${{ENABLE}}
```

### 2. 参数验证

```powershell
# 必需参数
[Parameter(Mandatory=$true)]

# 可选参数
[Parameter(Mandatory=$false)]

# 参数验证
[ValidateSet("txt", "html", "json")]
[string]$Format
```

### 3. 用户友好的输出

```powershell
# 使用颜色区分不同类型的消息
Write-Host "✓ 成功" -ForegroundColor Green
Write-Host "⚠️ 警告" -ForegroundColor Yellow
Write-Host "✗ 错误" -ForegroundColor Red
Write-Host "ℹ️ 信息" -ForegroundColor Cyan
```

### 4. 错误处理

```powershell
# 验证输入
if (-not (Test-Path $Path)) {
    Write-Error "路径不存在: $Path"
    exit 1
}

# Try-Catch 块
try {
    # 执行操作
} catch {
    Write-Error "操作失败: $($_.Exception.Message)"
    exit 1
}
```

### 5. 进度反馈

```powershell
# 显示进度
Write-Host "开始处理..." -ForegroundColor Cyan
# ... 执行操作 ...
Write-Host "✓ 处理完成" -ForegroundColor Green

# 显示统计信息
Write-Host "  处理文件数: $count" -ForegroundColor Gray
```

---

## 🔧 自定义这些模板

您可以基于这些示例创建自己的变体：

### 示例：创建增强版备份模板

```bash
# 1. 复制示例模板
cp templates/custom/examples/simple_backup.ps1 templates/custom/my_backups/enhanced_backup.ps1

# 2. 修改脚本，添加新功能
# - 添加邮件通知
# - 添加备份验证
# - 添加日志记录

# 3. 使用命令行工具注册
python src/main.py template create
# 选择"从文件导入"，指向您的新脚本
```

---

## 💡 最佳实践

1. **清晰的文档**: 使用 PowerShell 注释块 (`<# ... #>`) 提供详细说明
2. **参数验证**: 始终验证输入参数的有效性
3. **错误处理**: 使用 try-catch 和适当的错误消息
4. **用户反馈**: 提供清晰的进度和结果信息
5. **灵活性**: 使用参数而不是硬编码值
6. **可测试性**: 提供合理的默认值便于测试

---

## 📖 相关文档

- [自定义模板用户指南](../../../docs/custom-template-guide.md)
- [模板系统架构](../../../docs/architecture.md)
- [PowerShell 最佳实践](https://docs.microsoft.com/powershell/scripting/developer/cmdlet/cmdlet-development-guidelines)

---

**提示**: 这些示例模板可以直接使用，也可以作为创建您自己模板的起点。尝试修改它们以满足您的特定需求！
