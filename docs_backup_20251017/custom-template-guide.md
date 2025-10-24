# 自定义模板用户指南

## 目录

- [简介](#简介)
- [快速开始](#快速开始)
- [创建自定义模板](#创建自定义模板)
- [参数配置最佳实践](#参数配置最佳实践)
- [管理模板](#管理模板)
- [常见场景示例](#常见场景示例)
- [高级功能](#高级功能)
- [故障排除](#故障排除)

## 简介

自定义模板功能允许您将常用的 PowerShell 脚本保存为可复用的模板，并通过 AI 助手智能生成基于这些模板的脚本。这大大提高了工作效率，特别是对于重复性任务。

### 核心优势

- **提高效率**: 将常用脚本保存为模板，避免重复编写
- **智能生成**: AI 助手可以基于您的模板生成定制化脚本
- **参数化**: 支持灵活的参数配置，适应不同场景
- **版本控制**: 自动保存模板修改历史，可随时恢复
- **分类管理**: 按分类组织模板，便于查找和管理
- **导入导出**: 轻松分享模板或在不同环境间迁移

### 模板系统架构

```
templates/
├── automation/          # 系统预定义：自动化任务
├── file_management/     # 系统预定义：文件管理
├── system_monitoring/   # 系统预定义：系统监控
├── custom/              # 用户自定义模板目录
│   ├── examples/        # 示例模板
│   ├── my_category/     # 用户自定义分类
│   └── ...
└── .history/            # 模板版本历史
```

## 快速开始

### 创建第一个模板

```bash
# 启动交互式创建流程
python src/main.py template create
```

系统会引导您完成以下步骤：

1. **输入基本信息**: 名称、描述、分类、关键词
2. **提供脚本内容**: 从文件导入或直接输入
3. **识别参数**: 系统自动识别脚本中的变量
4. **配置参数**: 设置参数类型、默认值、描述
5. **验证保存**: 自动验证语法并保存模板

### 使用自定义模板

创建模板后，您可以通过自然语言请求使用它：

```bash
# AI 会自动匹配您的自定义模板
python src/main.py "使用我的备份模板备份文档文件夹"
```

## 创建自定义模板

### 方法一：从现有脚本创建

如果您已经有一个 PowerShell 脚本，可以直接将其转换为模板：

```bash
python src/main.py template create
```

**交互式流程示例**:

```
🎨 创建自定义模板
==================

模板名称: daily_backup
描述: 每日备份重要文件到指定位置
分类: [1] 选择现有分类 [2] 创建新分类
选择: 2
新分类名称: my_backups
关键词 (逗号分隔): 备份,文件,每日

脚本来源:
[1] 从文件导入
[2] 直接输入内容
选择: 1
脚本文件路径: C:\Scripts\backup.ps1

✓ 脚本加载成功

系统识别到以下参数:
1. $SourcePath (第3行) - 当前值: "C:\Documents"
2. $DestPath (第4行) - 当前值: "D:\Backup"
3. $DaysToKeep (第5行) - 当前值: 7

是否将这些参数设为模板参数? [y/n]: y

配置参数 1/3: SOURCE_PATH
类型: [1] string [2] integer [3] boolean [4] path
选择: 4
默认值: C:\Documents
描述: 要备份的源目录
必需: [y/n]: y

配置参数 2/3: DEST_PATH
类型: [1] string [2] integer [3] boolean [4] path
选择: 4
默认值: D:\Backup
描述: 备份目标目录
必需: [y/n]: y

配置参数 3/3: DAYS_TO_KEEP
类型: [1] string [2] integer [3] boolean [4] path
选择: 2
默认值: 7
描述: 保留备份的天数
必需: [y/n]: n

验证中...
✓ PowerShell 语法检查通过
✓ 参数配置有效
✓ 占位符一致性检查通过

保存中...
✓ 模板已保存: templates/custom/my_backups/daily_backup.ps1
✓ 配置已更新: config/templates.yaml

创建成功！
```

### 方法二：直接输入脚本内容

```bash
python src/main.py template create
```

选择"直接输入内容"选项，然后输入您的 PowerShell 脚本。

### 模板文件格式

创建后的模板文件使用占位符格式：

```powershell
# daily_backup.ps1
# 描述: 每日备份重要文件到指定位置

param(
    [Parameter(Mandatory=$true)]
    [string]$SourcePath = "{{SOURCE_PATH}}",
    
    [Parameter(Mandatory=$true)]
    [string]$DestPath = "{{DEST_PATH}}",
    
    [Parameter(Mandatory=$false)]
    [int]$DaysToKeep = {{DAYS_TO_KEEP}}
)

# 创建备份
Write-Host "开始备份: $SourcePath -> $DestPath"
Copy-Item -Path $SourcePath -Destination $DestPath -Recurse -Force

# 清理旧备份
$cutoffDate = (Get-Date).AddDays(-$DaysToKeep)
Get-ChildItem $DestPath | Where-Object { $_.LastWriteTime -lt $cutoffDate } | Remove-Item -Recurse -Force

Write-Host "备份完成"
```

## 参数配置最佳实践

### 参数类型选择

#### 1. String (字符串)
适用于文本、名称、描述等：

```yaml
parameters:
  FILE_NAME:
    type: string
    default: "output.txt"
    description: "输出文件名"
    required: true
```

#### 2. Integer (整数)
适用于数量、大小、时间等数值：

```yaml
parameters:
  MAX_SIZE:
    type: integer
    default: 100
    description: "最大文件大小 (MB)"
    required: false
    min: 1
    max: 1000
```

#### 3. Boolean (布尔值)
适用于开关、标志等：

```yaml
parameters:
  ENABLE_LOG:
    type: boolean
    default: true
    description: "是否启用日志记录"
    required: false
```

#### 4. Path (路径)
适用于文件或目录路径：

```yaml
parameters:
  TARGET_DIR:
    type: path
    default: "C:\\Temp"
    description: "目标目录路径"
    required: true
    validate: exists  # 可选：验证路径是否存在
```

### 参数命名规范

- 使用大写字母和下划线: `SOURCE_PATH`, `MAX_COUNT`
- 名称要有描述性: `FILE_PATTERN` 而不是 `FP`
- 避免使用保留字: 不要使用 `PATH`, `HOME` 等系统变量名

### 默认值设置

- 为非必需参数提供合理的默认值
- 默认值应该是最常用的值
- 路径默认值使用相对路径或通用路径

### 参数描述编写

好的参数描述应该：

```yaml
parameters:
  THRESHOLD:
    type: integer
    default: 80
    description: "CPU 使用率阈值 (0-100)，超过此值将触发警告"
    required: false
```

- 说明参数的用途
- 包含有效值范围
- 提供单位信息（如 MB、秒、百分比）
- 解释参数的影响

## 管理模板

### 列出模板

```bash
# 列出所有模板（系统 + 自定义）
python src/main.py template list

# 只列出自定义模板
python src/main.py template list --custom-only

# 按分类列出
python src/main.py template list --category my_backups
```

输出示例：

```
📋 模板列表
===========

[系统模板]
- file_management/batch_rename: 批量重命名文件
- automation/disk_cleanup: 磁盘清理工具

[自定义模板]
- my_backups/daily_backup: 每日备份重要文件
  关键词: 备份, 文件, 每日
  创建时间: 2025-10-07 10:30:00
  
- my_scripts/log_analyzer: 日志分析工具
  关键词: 日志, 分析, 监控
  创建时间: 2025-10-06 15:20:00
```

### 查看模板详情

```bash
python src/main.py template info daily_backup
```

输出示例：

```
📄 模板详情
===========

名称: daily_backup
描述: 每日备份重要文件到指定位置
分类: my_backups
文件: templates/custom/my_backups/daily_backup.ps1
关键词: 备份, 文件, 每日
创建时间: 2025-10-07 10:30:00
更新时间: 2025-10-07 10:30:00
作者: user
版本: 1.0.0

参数:
  SOURCE_PATH (path, 必需)
    默认值: C:\Documents
    描述: 要备份的源目录
    
  DEST_PATH (path, 必需)
    默认值: D:\Backup
    描述: 备份目标目录
    
  DAYS_TO_KEEP (integer, 可选)
    默认值: 7
    描述: 保留备份的天数
```

### 编辑模板

```bash
python src/main.py template edit daily_backup
```

交互式编辑菜单：

```
✏️ 编辑模板: daily_backup
=========================

[1] 更新基本信息 (名称、描述、关键词)
[2] 修改参数配置
[3] 更新脚本内容
[4] 移动到其他分类
[5] 查看当前配置
[0] 保存并退出

选择操作:
```

### 删除模板

```bash
python src/main.py template delete daily_backup
```

确认提示：

```
⚠️ 删除确认
============

您确定要删除以下模板吗？

名称: daily_backup
描述: 每日备份重要文件到指定位置
文件: templates/custom/my_backups/daily_backup.ps1

此操作不可撤销！

确认删除? [y/n]:
```

## 常见场景示例

### 示例 1: 数据库备份模板

**场景**: 定期备份 SQL Server 数据库

```powershell
# database_backup.ps1
param(
    [Parameter(Mandatory=$true)]
    [string]$ServerName = "{{SERVER_NAME}}",
    
    [Parameter(Mandatory=$true)]
    [string]$DatabaseName = "{{DATABASE_NAME}}",
    
    [Parameter(Mandatory=$true)]
    [string]$BackupPath = "{{BACKUP_PATH}}",
    
    [Parameter(Mandatory=$false)]
    [bool]$Compress = {{COMPRESS}}
)

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupFile = Join-Path $BackupPath "${DatabaseName}_${timestamp}.bak"

$query = "BACKUP DATABASE [$DatabaseName] TO DISK = '$backupFile'"
if ($Compress) {
    $query += " WITH COMPRESSION"
}

Invoke-Sqlcmd -ServerInstance $ServerName -Query $query
Write-Host "数据库备份完成: $backupFile"
```

**参数配置**:

```yaml
parameters:
  SERVER_NAME:
    type: string
    default: "localhost"
    description: "SQL Server 实例名称"
    required: true
    
  DATABASE_NAME:
    type: string
    default: "MyDatabase"
    description: "要备份的数据库名称"
    required: true
    
  BACKUP_PATH:
    type: path
    default: "C:\\Backups\\Database"
    description: "备份文件保存路径"
    required: true
    
  COMPRESS:
    type: boolean
    default: true
    description: "是否压缩备份文件"
    required: false
```

### 示例 2: 日志清理模板

**场景**: 清理指定天数之前的日志文件

```powershell
# log_cleanup.ps1
param(
    [Parameter(Mandatory=$true)]
    [string]$LogPath = "{{LOG_PATH}}",
    
    [Parameter(Mandatory=$false)]
    [int]$DaysToKeep = {{DAYS_TO_KEEP}},
    
    [Parameter(Mandatory=$false)]
    [string]$FilePattern = "{{FILE_PATTERN}}",
    
    [Parameter(Mandatory=$false)]
    [bool]$WhatIf = {{WHAT_IF}}
)

$cutoffDate = (Get-Date).AddDays(-$DaysToKeep)
$files = Get-ChildItem -Path $LogPath -Filter $FilePattern -Recurse | 
         Where-Object { $_.LastWriteTime -lt $cutoffDate }

$totalSize = ($files | Measure-Object -Property Length -Sum).Sum / 1MB

Write-Host "找到 $($files.Count) 个文件，总大小: $([math]::Round($totalSize, 2)) MB"

if ($WhatIf) {
    Write-Host "预览模式 - 将删除以下文件:"
    $files | ForEach-Object { Write-Host "  - $($_.FullName)" }
} else {
    $files | Remove-Item -Force
    Write-Host "清理完成"
}
```

**参数配置**:

```yaml
parameters:
  LOG_PATH:
    type: path
    default: "C:\\Logs"
    description: "日志文件目录"
    required: true
    
  DAYS_TO_KEEP:
    type: integer
    default: 30
    description: "保留日志的天数"
    required: false
    min: 1
    max: 365
    
  FILE_PATTERN:
    type: string
    default: "*.log"
    description: "日志文件匹配模式"
    required: false
    
  WHAT_IF:
    type: boolean
    default: true
    description: "预览模式（不实际删除）"
    required: false
```

### 示例 3: 系统健康检查模板

**场景**: 检查系统资源使用情况并生成报告

```powershell
# system_health_check.ps1
param(
    [Parameter(Mandatory=$false)]
    [int]$CpuThreshold = {{CPU_THRESHOLD}},
    
    [Parameter(Mandatory=$false)]
    [int]$MemoryThreshold = {{MEMORY_THRESHOLD}},
    
    [Parameter(Mandatory=$false)]
    [int]$DiskThreshold = {{DISK_THRESHOLD}},
    
    [Parameter(Mandatory=$false)]
    [string]$ReportPath = "{{REPORT_PATH}}"
)

$report = @()

# CPU 检查
$cpu = (Get-Counter '\Processor(_Total)\% Processor Time').CounterSamples.CookedValue
$cpuStatus = if ($cpu -gt $CpuThreshold) { "⚠️ 警告" } else { "✓ 正常" }
$report += "CPU 使用率: $([math]::Round($cpu, 2))% - $cpuStatus"

# 内存检查
$os = Get-CimInstance Win32_OperatingSystem
$memoryUsed = [math]::Round((($os.TotalVisibleMemorySize - $os.FreePhysicalMemory) / $os.TotalVisibleMemorySize) * 100, 2)
$memoryStatus = if ($memoryUsed -gt $MemoryThreshold) { "⚠️ 警告" } else { "✓ 正常" }
$report += "内存使用率: $memoryUsed% - $memoryStatus"

# 磁盘检查
$disks = Get-PSDrive -PSProvider FileSystem | Where-Object { $_.Used -ne $null }
foreach ($disk in $disks) {
    $diskUsed = [math]::Round(($disk.Used / ($disk.Used + $disk.Free)) * 100, 2)
    $diskStatus = if ($diskUsed -gt $DiskThreshold) { "⚠️ 警告" } else { "✓ 正常" }
    $report += "磁盘 $($disk.Name): $diskUsed% - $diskStatus"
}

# 输出报告
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$fullReport = "系统健康检查报告 - $timestamp`n" + ($report -join "`n")

Write-Host $fullReport

if ($ReportPath) {
    $fullReport | Out-File -FilePath $ReportPath -Encoding UTF8
    Write-Host "`n报告已保存: $ReportPath"
}
```

**参数配置**:

```yaml
parameters:
  CPU_THRESHOLD:
    type: integer
    default: 80
    description: "CPU 使用率警告阈值 (%)"
    required: false
    min: 0
    max: 100
    
  MEMORY_THRESHOLD:
    type: integer
    default: 85
    description: "内存使用率警告阈值 (%)"
    required: false
    min: 0
    max: 100
    
  DISK_THRESHOLD:
    type: integer
    default: 90
    description: "磁盘使用率警告阈值 (%)"
    required: false
    min: 0
    max: 100
    
  REPORT_PATH:
    type: path
    default: ""
    description: "报告保存路径（留空则不保存）"
    required: false
```

### 示例 4: 批量用户管理模板

**场景**: 从 CSV 文件批量创建 Active Directory 用户

```powershell
# bulk_user_creation.ps1
param(
    [Parameter(Mandatory=$true)]
    [string]$CsvPath = "{{CSV_PATH}}",
    
    [Parameter(Mandatory=$true)]
    [string]$OUPath = "{{OU_PATH}}",
    
    [Parameter(Mandatory=$false)]
    [string]$DefaultPassword = "{{DEFAULT_PASSWORD}}",
    
    [Parameter(Mandatory=$false)]
    [bool]$SendEmail = {{SEND_EMAIL}}
)

Import-Module ActiveDirectory

$users = Import-Csv -Path $CsvPath
$successCount = 0
$failCount = 0

foreach ($user in $users) {
    try {
        $params = @{
            Name = "$($user.FirstName) $($user.LastName)"
            GivenName = $user.FirstName
            Surname = $user.LastName
            SamAccountName = $user.Username
            UserPrincipalName = "$($user.Username)@domain.com"
            Path = $OUPath
            AccountPassword = (ConvertTo-SecureString $DefaultPassword -AsPlainText -Force)
            Enabled = $true
            ChangePasswordAtLogon = $true
        }
        
        New-ADUser @params
        Write-Host "✓ 创建用户: $($user.Username)"
        $successCount++
        
        if ($SendEmail -and $user.Email) {
            # 发送欢迎邮件逻辑
            Send-MailMessage -To $user.Email -Subject "欢迎" -Body "您的账户已创建"
        }
    }
    catch {
        Write-Host "✗ 创建失败: $($user.Username) - $($_.Exception.Message)"
        $failCount++
    }
}

Write-Host "`n总结: 成功 $successCount, 失败 $failCount"
```

## 高级功能

### 版本控制

每次编辑模板时，系统会自动保存历史版本：

```bash
# 查看模板历史
python src/main.py template history daily_backup
```

输出：

```
📜 模板历史: daily_backup
========================

版本 3 - 2025-10-07 14:30:00 (当前)
  修改: 添加了压缩选项参数

版本 2 - 2025-10-07 12:00:00
  修改: 更新了默认备份路径

版本 1 - 2025-10-07 10:30:00
  修改: 初始创建
```

恢复到历史版本：

```bash
python src/main.py template restore daily_backup 2
```

### 模板导出和导入

#### 导出模板

```bash
# 导出单个模板
python src/main.py template export daily_backup -o daily_backup.zip

# 导出多个模板
python src/main.py template export daily_backup log_cleanup -o my_templates.zip
```

导出的 ZIP 包包含：
- 模板脚本文件
- 参数配置
- 元数据信息

#### 导入模板

```bash
# 导入模板
python src/main.py template import daily_backup.zip
```

如果模板名称冲突：

```
⚠️ 模板冲突
===========

模板 'daily_backup' 已存在

[1] 覆盖现有模板
[2] 重命名为 'daily_backup_imported'
[3] 取消导入

选择操作:
```

### 分类管理

#### 创建新分类

```bash
python src/main.py template category create
```

```
📁 创建新分类
=============

分类名称: database_tools
描述: 数据库管理相关工具

✓ 分类已创建: templates/custom/database_tools/
```

#### 移动模板到其他分类

```bash
python src/main.py template move daily_backup database_tools
```

#### 删除空分类

```bash
python src/main.py template category delete my_old_category
```

### 模板测试

在保存模板前测试生成效果：

```bash
python src/main.py template test daily_backup
```

系统会使用示例参数生成测试脚本：

```
🧪 测试模板: daily_backup
========================

使用以下测试参数:
  SOURCE_PATH: C:\Documents
  DEST_PATH: D:\Backup
  DAYS_TO_KEEP: 7

生成的脚本预览:
---
# daily_backup.ps1
param(
    [string]$SourcePath = "C:\Documents",
    [string]$DestPath = "D:\Backup",
    [int]$DaysToKeep = 7
)
...
---

是否执行测试脚本? [y/n]:
```

## 故障排除

### 常见问题

#### 1. 语法验证失败

**问题**: 保存模板时提示 PowerShell 语法错误

**解决方案**:
- 在 PowerShell ISE 或 VS Code 中先测试脚本
- 检查是否有未闭合的括号、引号
- 确保所有变量都已定义

#### 2. 参数占位符不匹配

**问题**: 提示占位符与参数配置不一致

**解决方案**:
- 确保所有 `{{参数名}}` 都在配置中定义
- 参数名使用大写字母和下划线
- 检查是否有拼写错误

#### 3. 模板无法被 AI 匹配

**问题**: 使用自然语言请求时，AI 没有选择您的模板

**解决方案**:
- 添加更多相关关键词
- 完善模板描述，使用清晰的语言
- 确保关键词与您的请求相关

#### 4. 导入模板失败

**问题**: 导入 ZIP 包时失败

**解决方案**:
- 确保 ZIP 包是通过系统导出功能创建的
- 检查 ZIP 包是否损坏
- 验证文件权限

### 调试技巧

#### 启用详细日志

```bash
python src/main.py template create --verbose
```

#### 查看模板配置

```bash
# 查看 templates.yaml 中的配置
python src/main.py template config daily_backup
```

#### 验证模板

```bash
# 手动验证模板
python src/main.py template validate daily_backup
```

输出：

```
✓ PowerShell 语法检查通过
✓ 参数配置有效
✓ 占位符一致性检查通过
✓ 安全检查通过
```

### 获取帮助

```bash
# 查看命令帮助
python src/main.py template --help

# 查看子命令帮助
python src/main.py template create --help
```

## 最佳实践总结

1. **命名规范**
   - 使用描述性的模板名称
   - 参数名使用大写和下划线
   - 分类名使用小写和下划线

2. **参数设计**
   - 为常用参数提供合理默认值
   - 使用正确的参数类型
   - 添加详细的参数描述

3. **文档化**
   - 在脚本开头添加注释说明用途
   - 为每个参数添加描述
   - 使用有意义的关键词

4. **测试**
   - 创建后立即测试模板
   - 使用不同参数值测试
   - 在实际环境中验证

5. **版本管理**
   - 重大修改前查看历史版本
   - 定期导出重要模板作为备份
   - 记录修改原因

6. **安全性**
   - 避免在模板中硬编码敏感信息
   - 使用参数传递密码和凭据
   - 定期审查模板内容

## 相关资源

- [PowerShell 文档](https://docs.microsoft.com/powershell/)
- [模板引擎架构](architecture.md)
- [开发者指南](developer-guide.md)
- [安全检查指南](security-checker-guide.md)

---

如有问题或建议，请访问 [GitHub Issues](https://github.com/0green7hand0/AI-PowerShell/issues)
