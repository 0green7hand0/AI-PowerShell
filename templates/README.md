# PowerShell 脚本模板库

这个目录包含了各种实用的 PowerShell 脚本模板，可以通过 AI PowerShell 智能助手快速生成和使用。

## 📁 模板分类

### 1. 文件管理 (file_management)

#### batch_rename.ps1 - 批量重命名文件
- 按规则批量重命名文件
- 支持自定义前缀、日期、序号
- 示例：`批量重命名桌面的jpg文件为photo_日期_序号`

#### file_organizer.ps1 - 文件分类整理
- 按文件类型自动分类到不同文件夹
- 支持移动或复制
- 示例：`整理下载文件夹，按类型分类`

### 2. 系统监控 (system_monitoring)

#### resource_monitor.ps1 - 系统资源监控
- 监控 CPU、内存、磁盘使用情况
- 可设置阈值告警
- 显示资源占用最高的进程
- 示例：`每30秒检查一次CPU，超过80%就警告`

### 3. 自动化任务 (automation)

#### backup_files.ps1 - 文件备份
- 自动备份文件到指定位置
- 支持压缩和版本管理
- 可排除特定文件
- 示例：`每天备份文档文件夹到D盘`

#### disk_cleanup.ps1 - 磁盘清理
- 清理临时文件、缓存、回收站
- 可设置清理规则
- 示例：`清理30天前的临时文件`

### 4. 进程管理 (process_management) ⭐ 新增

#### process_manager.ps1 - 进程管理工具
- 列出进程并按 CPU/内存排序
- 查找特定进程
- 终止进程
- 监控高资源占用进程
- 示例：
  - `列出CPU占用最高的10个进程`
  - `查找chrome进程`
  - `终止notepad进程`
  - `监控高资源占用进程`

### 5. 网络诊断 (network_diagnostics) ⭐ 新增

#### network_check.ps1 - 网络连接诊断
- 测试网络连通性（Ping）
- DNS 解析检查
- 端口连接测试
- 路由追踪
- 本地网络接口信息
- 示例：
  - `测试到百度的网络连接`
  - `检查DNS解析和80、443端口`
  - `诊断网络连接问题，包含路由追踪`

### 6. 日志分析 (log_analysis) ⭐ 新增

#### log_analyzer.ps1 - 日志分析工具
- 分析日志文件
- 提取错误、警告信息
- 统计日志级别分布
- 搜索特定模式
- 导出分析结果
- 示例：
  - `分析日志文件，提取所有错误`
  - `统计日志中的错误和警告数量`
  - `搜索包含特定关键词的日志`

### 7. 定时任务 (scheduled_tasks) ⭐ 新增

#### task_scheduler.ps1 - 定时任务管理
- 创建 Windows 计划任务
- 查看所有任务
- 查询任务详情
- 启用/禁用/删除任务
- 支持多种计划类型（每天、每周、每小时、间隔、启动时、登录时）
- 示例：
  - `列出所有计划任务`
  - `创建每天9点执行的备份任务`
  - `创建每周一三五执行的清理任务`

## 🚀 使用方法

### 方法 1: 通过 AI 自然语言

直接用中文描述你的需求，AI 会自动匹配合适的模板并生成脚本：

```bash
python -m src.main

# 然后输入：
生成脚本：列出CPU占用最高的10个进程
生成脚本：测试到百度的网络连接
生成脚本：分析日志文件，提取所有错误
```

### 方法 2: 通过命令行

```bash
# 列出所有模板
python -m src.main template list

# 测试特定模板
python -m src.main template test process_manager

# 查看模板详情
python -m src.main template info process_manager
```

### 方法 3: 直接运行脚本

```powershell
# 进程管理
.\templates\process_management\process_manager.ps1 -ACTION list -TOP_COUNT 10

# 网络诊断
.\templates\network_diagnostics\network_check.ps1 -TARGET_HOST "www.baidu.com" -CHECK_DNS $true

# 日志分析
.\templates\log_analysis\log_analyzer.ps1 -LOG_FILE "logs\assistant.log" -LOG_LEVEL ERROR

# 定时任务
.\templates\scheduled_tasks\task_scheduler.ps1 -ACTION list
```

## 📝 模板参数说明

每个模板都有可配置的参数，使用 `{{参数名}}` 占位符表示。AI 会根据你的需求自动填充这些参数。

### 进程管理参数

- `ACTION`: 操作类型（list/find/kill/monitor）
- `PROCESS_NAME`: 进程名称
- `TOP_COUNT`: 显示前N个进程
- `SORT_BY`: 排序字段（cpu/memory/name）
- `CPU_THRESHOLD`: CPU阈值（%）
- `MEMORY_THRESHOLD`: 内存阈值（MB）

### 网络诊断参数

- `TARGET_HOST`: 目标主机
- `PING_COUNT`: Ping次数
- `CHECK_DNS`: 是否检查DNS
- `CHECK_PORTS`: 是否检查端口
- `PORTS`: 端口列表（逗号分隔）
- `TRACE_ROUTE`: 是否路由追踪

### 日志分析参数

- `LOG_FILE`: 日志文件路径
- `LOG_LEVEL`: 日志级别（ERROR/WARNING/INFO/DEBUG/ALL）
- `TAIL_LINES`: 读取行数（0=全部）
- `SEARCH_PATTERN`: 搜索模式
- `SHOW_STATS`: 显示统计
- `EXPORT_RESULTS`: 导出结果

### 定时任务参数

- `ACTION`: 操作类型（create/list/info/delete/enable/disable）
- `TASK_NAME`: 任务名称
- `SCRIPT_PATH`: 脚本路径
- `SCHEDULE_TYPE`: 计划类型（daily/weekly/hourly/interval/startup/logon）
- `START_TIME`: 开始时间
- `RUN_AS_ADMIN`: 管理员权限

## 🎯 使用示例

### 示例 1: 监控系统资源

```
用户输入：监控CPU和内存，超过80%就警告

AI 生成：
- 使用 process_manager.ps1
- ACTION = monitor
- CPU_THRESHOLD = 80
- MEMORY_THRESHOLD = 80
```

### 示例 2: 诊断网络问题

```
用户输入：检查到百度的网络连接，包括DNS和端口

AI 生成：
- 使用 network_check.ps1
- TARGET_HOST = www.baidu.com
- CHECK_DNS = true
- CHECK_PORTS = true
- PORTS = 80,443
```

### 示例 3: 分析错误日志

```
用户输入：分析日志文件，只看错误信息

AI 生成：
- 使用 log_analyzer.ps1
- LOG_FILE = logs/assistant.log
- LOG_LEVEL = ERROR
- SHOW_STATS = true
```

### 示例 4: 创建定时备份

```
用户输入：创建每天早上9点执行的备份任务

AI 生成：
- 使用 task_scheduler.ps1
- ACTION = create
- TASK_NAME = DailyBackup
- SCHEDULE_TYPE = daily
- START_TIME = 09:00
```

## 🔧 自定义模板

你可以创建自己的模板：

1. 在相应分类目录下创建 `.ps1` 文件
2. 使用 `{{参数名}}` 作为占位符
3. 在 `config/templates.yaml` 中注册模板
4. 定义参数和关键词

详细说明请参考 [模板开发指南](../docs/template-guide.md)

## 📊 模板统计

- 总模板数: 9 个
- 文件管理: 2 个
- 系统监控: 1 个
- 自动化任务: 2 个
- 进程管理: 1 个 ⭐
- 网络诊断: 1 个 ⭐
- 日志分析: 1 个 ⭐
- 定时任务: 1 个 ⭐

## 🆕 最近更新

**2025-02-18**
- ✅ 新增进程管理模板
- ✅ 新增网络诊断模板
- ✅ 新增日志分析模板
- ✅ 新增定时任务管理模板

## 📚 相关文档

- [模板系统指南](../docs/template-guide.md)
- [用户使用指南](../docs/user-guide.md)
- [配置参考](../docs/config-reference.md)

---

**提示**: 所有模板都经过测试，可以直接使用。如果遇到问题，请查看 [故障排除指南](../docs/troubleshooting.md)。
