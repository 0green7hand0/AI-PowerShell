<!-- 文档类型: 用户指南 | 最后更新: 2025-10-17 | 维护者: 项目团队 -->

# 模板系统完整指南

📍 [首页](../README.md) > [文档中心](README.md) > 模板系统完整指南

## 📋 目录

- [简介](#简介)
- [快速入门（5分钟）](#快速入门5分钟)
- [模板系统详解](#模板系统详解)
- [CLI完整参考](#cli完整参考)
- [最佳实践](#最佳实践)
- [故障排除](#故障排除)
- [相关文档](#相关文档)

---

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

---

## 快速入门（5分钟）

### 1️⃣ 创建你的第一个模板

```bash
python src/main.py template create
```

按照提示输入：
- **名称**: my_first_template
- **描述**: 我的第一个自定义模板
- **分类**: 选择 [2] 创建新分类 → 输入 "my_templates"
- **关键词**: 测试,示例
- **脚本来源**: 选择 [2] 直接输入内容

输入简单的脚本：
```powershell
param(
    [string]$Message = "{{MESSAGE}}"
)

Write-Host "Hello, $Message!" -ForegroundColor Green
```

配置参数：
- **类型**: [1] string
- **默认值**: World
- **描述**: 要显示的消息
- **必需**: n

✅ 完成！你的第一个模板已创建。

### 2️⃣ 使用你的模板

```bash
python src/main.py

# 输入自然语言请求
💬 请输入 > 使用我的模板显示 "Kiro"
```

AI 会自动识别并使用你的模板生成脚本。

### 3️⃣ 查看和管理模板

```bash
# 列出所有模板
python src/main.py template list

# 查看模板详情
python src/main.py template info my_first_template

# 编辑模板
python src/main.py template edit my_first_template

# 导出模板（分享给他人）
python src/main.py template export my_first_template -o my_template.zip
```

### 常用命令速查表

| 命令 | 说明 | 示例 |
|------|------|------|
| `template create` | 创建新模板 | `python src/main.py template create` |
| `template list` | 列出所有模板 | `python src/main.py template list` |
| `template list --custom-only` | 只列出自定义模板 | `python src/main.py template list --custom-only` |
| `template info <id>` | 查看模板详情 | `python src/main.py template info my_template` |
| `template edit <id>` | 编辑模板 | `python src/main.py template edit my_template` |
| `template delete <id>` | 删除模板 | `python src/main.py template delete my_template` |
| `template export <id> -o <file>` | 导出模板 | `python src/main.py template export my_template -o template.zip` |
| `template import <file>` | 导入模板 | `python src/main.py template import template.zip` |
| `template history <id>` | 查看历史版本 | `python src/main.py template history my_template` |
| `template restore <id> <ver>` | 恢复历史版本 | `python src/main.py template restore my_template 2` |
| `template test <id>` | 测试模板 | `python src/main.py template test my_template` |

### 参数类型速查

#### String (字符串)
```powershell
[string]$Name = "{{NAME}}"
```
用于：文本、名称、描述

#### Integer (整数)
```powershell
[int]$Count = {{COUNT}}
```
用于：数量、大小、时间（秒）

#### Boolean (布尔值)
```powershell
[bool]$Enable = ${{ENABLE}}
```
用于：开关、标志、是否选项

#### Path (路径)
```powershell
[string]$Path = "{{PATH}}"
```
用于：文件路径、目录路径

### 3个实用模板示例

#### 示例1: 快速备份
```powershell
param(
    [string]$Source = "{{SOURCE}}",
    [string]$Dest = "{{DEST}}"
)
Copy-Item -Path $Source -Destination $Dest -Recurse -Force
Write-Host "✓ 备份完成" -ForegroundColor Green
```

#### 示例2: 清理临时文件
```powershell
param(
    [string]$Path = "{{PATH}}",
    [int]$Days = {{DAYS}}
)
$cutoff = (Get-Date).AddDays(-$Days)
Get-ChildItem $Path | Where-Object { $_.LastWriteTime -lt $cutoff } | Remove-Item -Force
Write-Host "✓ 清理完成" -ForegroundColor Green
```

#### 示例3: 系统信息
```powershell
param(
    [bool]$Detailed = ${{DETAILED}}
)
$info = Get-ComputerInfo
Write-Host "计算机: $($info.CsName)"
Write-Host "OS: $($info.OsName)"
if ($Detailed) {
    Write-Host "内存: $([math]::Round($info.CsTotalPhysicalMemory/1GB, 2)) GB"
}
```

---

## 模板系统详解

### 创建自定义模板

#### 方法一：从现有脚本创建

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

#### 方法二：直接输入脚本内容

选择"直接输入内容"选项，然后输入您的 PowerShell 脚本。系统会自动识别参数并引导您完成配置。

#### 模板文件格式

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

### 参数配置详解

#### 参数类型选择

##### 1. String (字符串)
适用于文本、名称、描述等：

```yaml
parameters:
  FILE_NAME:
    type: string
    default: "output.txt"
    description: "输出文件名"
    required: true
```

##### 2. Integer (整数)
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

##### 3. Boolean (布尔值)
适用于开关、标志等：

```yaml
parameters:
  ENABLE_LOG:
    type: boolean
    default: true
    description: "是否启用日志记录"
    required: false
```

##### 4. Path (路径)
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

#### 参数命名规范

- 使用大写字母和下划线: `SOURCE_PATH`, `MAX_COUNT`
- 名称要有描述性: `FILE_PATTERN` 而不是 `FP`
- 避免使用保留字: 不要使用 `PATH`, `HOME` 等系统变量名

#### 默认值设置

- 为非必需参数提供合理的默认值
- 默认值应该是最常用的值
- 路径默认值使用相对路径或通用路径

#### 参数描述编写

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

### 管理模板

#### 列出模板

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

#### 查看模板详情

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

#### 编辑模板

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

#### 删除模板

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

### 高级功能

#### 版本控制

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

#### 模板导出和导入

##### 导出模板

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

##### 导入模板

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

#### 分类管理

##### 创建新分类

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

##### 移动模板到其他分类

```bash
python src/main.py template move daily_backup database_tools
```

##### 删除空分类

```bash
python src/main.py template category delete my_old_category
```

#### 模板测试

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

### 常见场景示例

#### 示例 1: 数据库备份模板

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

#### 示例 2: 日志清理模板

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

#### 示例 3: 系统健康检查模板

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

---

## CLI完整参考

### 通用选项

这些选项适用于所有模板命令：

| 选项 | 说明 |
|------|------|
| `-h, --help` | 显示帮助信息 |
| `-v, --verbose` | 显示详细输出 |
| `--debug` | 启用调试模式 |

### 命令详解

#### create - 创建新模板

创建一个新的自定义模板。

**语法**:
```bash
python src/main.py template create [options]
```

**选项**:

| 选项 | 类型 | 说明 |
|------|------|------|
| `--name` | string | 模板名称 |
| `--description` | string | 模板描述 |
| `--category` | string | 模板分类 |
| `--keywords` | string | 关键词（逗号分隔） |
| `--from-file` | path | 从文件导入脚本 |
| `--interactive` | flag | 交互式创建（默认） |

**示例**:

```bash
# 交互式创建（推荐）
python src/main.py template create

# 从文件创建
python src/main.py template create --from-file backup.ps1 --name daily_backup

# 指定基本信息
python src/main.py template create --name my_template --category my_scripts --keywords "backup,automation"
```

#### list - 列出模板

列出所有可用的模板。

**语法**:
```bash
python src/main.py template list [options]
```

**选项**:

| 选项 | 类型 | 说明 |
|------|------|------|
| `--custom-only` | flag | 只显示自定义模板 |
| `--category` | string | 按分类筛选 |
| `--keyword` | string | 按关键词搜索 |
| `--format` | string | 输出格式 (table/json/yaml) |

**示例**:

```bash
# 列出所有模板
python src/main.py template list

# 只列出自定义模板
python src/main.py template list --custom-only

# 按分类筛选
python src/main.py template list --category automation

# 搜索关键词
python src/main.py template list --keyword backup
```

#### info - 查看模板详情

显示模板的详细信息。

**语法**:
```bash
python src/main.py template info <template_name> [options]
```

**选项**:

| 选项 | 类型 | 说明 |
|------|------|------|
| `--show-content` | flag | 显示模板脚本内容 |
| `--format` | string | 输出格式 (text/json/yaml) |

#### edit - 编辑模板

编辑现有模板的配置或内容。

**语法**:
```bash
python src/main.py template edit <template_name> [options]
```

**选项**:

| 选项 | 类型 | 说明 |
|------|------|------|
| `--name` | string | 更新模板名称 |
| `--description` | string | 更新描述 |
| `--keywords` | string | 更新关键词 |
| `--interactive` | flag | 交互式编辑（默认） |

#### delete - 删除模板

删除自定义模板。

**语法**:
```bash
python src/main.py template delete <template_name> [options]
```

**选项**:

| 选项 | 类型 | 说明 |
|------|------|------|
| `--force` | flag | 跳过确认提示 |
| `--keep-backup` | flag | 保留备份副本 |

#### export - 导出模板

将模板导出为 ZIP 包，便于分享或备份。

**语法**:
```bash
python src/main.py template export <template_name> [options]
```

**选项**:

| 选项 | 类型 | 说明 |
|------|------|------|
| `-o, --output` | path | 输出文件路径 |
| `--include-history` | flag | 包含版本历史 |

**示例**:

```bash
# 导出单个模板
python src/main.py template export daily_backup -o backup.zip

# 导出多个模板
python src/main.py template export daily_backup log_analyzer -o my_templates.zip
```

#### import - 导入模板

从 ZIP 包导入模板。

**语法**:
```bash
python src/main.py template import <package_path> [options]
```

**选项**:

| 选项 | 类型 | 说明 |
|------|------|------|
| `--overwrite` | flag | 覆盖同名模板 |
| `--rename` | string | 重命名导入的模板 |
| `--category` | string | 指定导入分类 |

#### history - 查看版本历史

查看模板的修改历史。

**语法**:
```bash
python src/main.py template history <template_name> [options]
```

**选项**:

| 选项 | 类型 | 说明 |
|------|------|------|
| `--limit` | int | 显示的版本数量 |
| `--show-diff` | flag | 显示版本差异 |

#### restore - 恢复历史版本

将模板恢复到指定的历史版本。

**语法**:
```bash
python src/main.py template restore <template_name> <version> [options]
```

**选项**:

| 选项 | 类型 | 说明 |
|------|------|------|
| `--force` | flag | 跳过确认提示 |
| `--preview` | flag | 预览版本内容 |

#### test - 测试模板

使用示例参数测试模板生成。

**语法**:
```bash
python src/main.py template test <template_name> [options]
```

**选项**:

| 选项 | 类型 | 说明 |
|------|------|------|
| `--params` | string | 自定义参数 (JSON格式) |
| `--execute` | flag | 执行生成的脚本 |
| `--save` | path | 保存生成的脚本 |

#### validate - 验证模板

验证模板的语法和配置。

**语法**:
```bash
python src/main.py template validate <template_name> [options]
```

**选项**:

| 选项 | 类型 | 说明 |
|------|------|------|
| `--strict` | flag | 严格模式验证 |
| `--fix` | flag | 自动修复问题 |

#### category - 分类管理

管理模板分类。

**语法**:
```bash
python src/main.py template category <action> [options]
```

**子命令**:

- `create` - 创建分类
- `list` - 列出分类
- `delete` - 删除分类
- `move` - 移动模板

**示例**:

```bash
# 创建新分类
python src/main.py template category create database_tools --description "数据库管理工具"

# 列出所有分类
python src/main.py template category list

# 移动模板
python src/main.py template category move daily_backup automation

# 删除空分类
python src/main.py template category delete old_category
```

### 环境变量

可以通过环境变量配置模板系统的行为：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `TEMPLATE_DIR` | 模板目录路径 | `templates/` |
| `TEMPLATE_CONFIG` | 配置文件路径 | `config/templates.yaml` |
| `TEMPLATE_HISTORY_MAX` | 最大历史版本数 | `10` |
| `TEMPLATE_AUTO_BACKUP` | 自动备份 | `true` |

**示例**:

```bash
# Windows
set TEMPLATE_HISTORY_MAX=20
python src/main.py template create

# Linux/macOS
export TEMPLATE_HISTORY_MAX=20
python src/main.py template create
```

### 配置文件

模板配置存储在 `config/templates.yaml` 中：

```yaml
templates:
  custom:
    my_backup:
      name: "我的备份模板"
      file: "templates/custom/my_tools/my_backup.ps1"
      description: "自定义备份工具"
      keywords: ["backup", "files"]
      parameters:
        SOURCE_PATH:
          type: "path"
          default: "C:\\Documents"
          description: "源目录"
          required: true
      is_custom: true
      created_at: "2025-10-07T10:00:00"
      author: "user"
```

---

## 最佳实践

### 命名规范

✅ **推荐做法**
- 使用描述性的模板名称: `database_backup` 而不是 `db_bak`
- 参数名使用大写和下划线: `SOURCE_PATH`, `MAX_COUNT`
- 分类名使用小写和下划线: `database_tools`, `my_scripts`

❌ **避免做法**
- 使用模糊的名称: `script1`, `temp`
- 使用特殊字符: `my-template!`, `test@script`
- 使用保留字: `PATH`, `HOME`, `USER`

### 参数设计

✅ **推荐做法**
- 为常用参数提供合理默认值
- 使用正确的参数类型（string, integer, boolean, path）
- 添加详细的参数描述，包含单位和范围
- 验证输入参数（使用 `Test-Path` 等）

❌ **避免做法**
- 所有参数都设为必需
- 使用错误的参数类型
- 参数描述过于简单或缺失
- 跳过参数验证

### 文档化

✅ **推荐做法**
- 在脚本开头添加注释说明用途
- 为每个参数添加清晰的描述
- 使用有意义的关键词便于搜索
- 添加使用示例和注意事项

❌ **避免做法**
- 没有任何注释
- 关键词过于宽泛或无关
- 缺少使用说明

### 测试

✅ **推荐做法**
- 创建后立即测试模板
- 使用不同参数值测试
- 在实际环境中验证
- 使用 `template test` 命令预览生成结果

❌ **避免做法**
- 不测试直接使用
- 只测试默认参数
- 跳过错误处理测试

### 版本管理

✅ **推荐做法**
- 重大修改前查看历史版本
- 定期导出重要模板作为备份
- 记录修改原因（在版本历史中）
- 使用版本控制跟踪变更

❌ **避免做法**
- 直接覆盖重要模板
- 不保留备份
- 忽略版本历史功能

### 安全性

✅ **推荐做法**
- 避免在模板中硬编码敏感信息
- 使用参数传递密码和凭据
- 定期审查模板内容
- 验证用户输入

❌ **避免做法**
- 在模板中存储密码
- 执行未验证的用户输入
- 忽略安全警告

### Top 5 最佳实践总结

1. **使用描述性名称**: `database_backup` 而不是 `db_bak`
2. **添加详细注释**: 帮助他人（和未来的你）理解模板
3. **提供合理默认值**: 让模板开箱即用
4. **验证输入参数**: 使用 `Test-Path` 等检查有效性
5. **友好的输出**: 使用颜色和图标让输出更清晰

---

## 故障排除

### 常见问题

#### 1. 语法验证失败

**问题**: 保存模板时提示 PowerShell 语法错误

**症状**:
```
Error: PowerShell syntax error at line 10
```

**解决方案**:
- 在 PowerShell ISE 或 VS Code 中先测试脚本
- 检查是否有未闭合的括号、引号
- 确保所有变量都已定义
- 使用 `--debug` 选项查看详细错误信息

#### 2. 参数占位符不匹配

**问题**: 提示占位符与参数配置不一致

**症状**:
```
Error: Parameter 'PATH' is not defined in template
```

**解决方案**:
- 确保所有 `{{参数名}}` 都在配置中定义
- 参数名使用大写字母和下划线
- 检查是否有拼写错误
- 使用 `template validate` 命令检查一致性

#### 3. 模板无法被 AI 匹配

**问题**: 使用自然语言请求时，AI 没有选择您的模板

**症状**:
- AI 生成通用脚本而不是使用自定义模板
- 提示找不到匹配的模板

**解决方案**:
- 添加更多相关关键词
- 完善模板描述，使用清晰的语言
- 确保关键词与您的请求相关
- 在请求中明确提到模板名称或关键词

#### 4. 导入模板失败

**问题**: 导入 ZIP 包时失败

**症状**:
```
Error: Failed to import template package
```

**解决方案**:
- 确保 ZIP 包是通过系统导出功能创建的
- 检查 ZIP 包是否损坏
- 验证文件权限
- 使用 `--verbose` 选项查看详细错误

#### 5. 模板执行错误

**问题**: 生成的脚本执行时出错

**症状**:
- 参数值不正确
- 路径不存在
- 权限不足

**解决方案**:
- 使用 `template test` 命令先测试
- 检查参数默认值是否合理
- 验证路径是否存在
- 确保有足够的执行权限

### 调试技巧

#### 启用详细日志

```bash
python src/main.py template create --verbose
```

#### 查看模板配置

```bash
# 查看 templates.yaml 中的配置
python src/main.py template info daily_backup --format yaml
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

#### 测试参数替换

```bash
# 使用自定义参数测试
python src/main.py template test daily_backup --params '{"SOURCE_PATH":"C:\\Test"}'
```

### 获取帮助

```bash
# 查看命令帮助
python src/main.py template --help

# 查看子命令帮助
python src/main.py template create --help

# 启用详细输出
python src/main.py template create --verbose

# 启用调试模式
python src/main.py template create --debug
```

### 常见错误代码

| 错误代码 | 说明 | 解决方案 |
|---------|------|---------|
| `TEMPLATE_NOT_FOUND` | 模板不存在 | 使用 `template list` 查看可用模板 |
| `SYNTAX_ERROR` | PowerShell 语法错误 | 在 PowerShell ISE 中检查语法 |
| `PARAM_MISMATCH` | 参数不匹配 | 确保占位符与配置一致 |
| `IMPORT_FAILED` | 导入失败 | 检查 ZIP 包完整性 |
| `PERMISSION_DENIED` | 权限不足 | 以管理员身份运行 |

---

## 相关文档

- [用户指南](user-guide.md) - 系统整体使用指南
- [架构文档](architecture.md) - 模板引擎架构设计
- [开发者指南](developer-guide.md) - 扩展模板系统
- [CLI 参考](cli-reference.md) - 完整命令行参考
- [故障排除指南](troubleshooting.md) - 更多问题解决方案

## 下一步

- 📖 阅读 [用户指南](user-guide.md) 了解系统其他功能
- 💡 查看 [示例模板](../templates/custom/examples/) 获取灵感
- 🔧 探索 [高级配置](config-reference.md) 自定义模板系统
- 🚀 开始创建您的第一个自定义模板

---

**需要帮助?** 查看 [故障排除指南](troubleshooting.md) 或访问 [GitHub Issues](https://github.com/0green7hand0/AI-PowerShell/issues)

**提示**: 从简单开始，逐步添加功能。每个伟大的模板都是从一个简单的脚本开始的！ 🚀
