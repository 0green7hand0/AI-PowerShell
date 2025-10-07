# PowerShell 脚本模板库

## 📚 模板分类

本项目包含两类模板：

- **系统模板**: 预定义的通用模板，位于 `automation/`, `file_management/`, `system_monitoring/` 等目录
- **自定义模板**: 用户创建的个性化模板，位于 `custom/` 目录

## 📚 系统模板列表

### 文件管理 (file_management/)

#### 1. batch_rename.ps1 - 批量重命名文件
**功能：** 按规则批量重命名文件

**使用示例：**
```
帮我生成一个脚本，把桌面的jpg照片重命名为 vacation_2025_序号.jpg
```

**参数：**
- SOURCE_PATH: 源文件夹路径
- FILE_PATTERN: 文件匹配模式（如 *.jpg）
- NAME_PREFIX: 文件名前缀
- USE_DATE: 是否包含日期
- START_NUMBER: 起始序号

---

#### 2. file_organizer.ps1 - 文件分类整理
**功能：** 按文件类型自动分类到不同文件夹

**使用示例：**
```
帮我整理下载文件夹，按文件类型分类
```

**参数：**
- SOURCE_PATH: 源文件夹路径
- CREATE_SUBFOLDERS: 是否创建子文件夹
- MOVE_FILES: 移动还是复制（move/copy）

---

### 系统监控 (system_monitoring/)

#### 3. resource_monitor.ps1 - 系统资源监控
**功能：** 监控CPU、内存、磁盘使用情况

**使用示例：**
```
生成一个监控脚本，每30秒检查一次CPU，超过80%就警告
```

**参数：**
- CPU_THRESHOLD: CPU使用率阈值
- MEMORY_THRESHOLD: 内存使用率阈值
- DISK_THRESHOLD: 磁盘使用率阈值
- CHECK_INTERVAL: 检查间隔（秒）
- TOP_PROCESSES: 显示前N个进程

---

### 自动化任务 (automation/)

#### 4. backup_files.ps1 - 文件备份
**功能：** 自动备份文件到指定位置

**使用示例：**
```
帮我生成一个备份脚本，每天备份文档文件夹到D盘
```

**参数：**
- SOURCE_PATH: 源文件夹路径
- BACKUP_PATH: 备份目标路径
- INCLUDE_SUBFOLDERS: 是否包含子文件夹
- COMPRESS: 是否压缩备份
- KEEP_VERSIONS: 保留的备份版本数

---

#### 5. disk_cleanup.ps1 - 磁盘清理
**功能：** 清理临时文件、缓存、回收站

**使用示例：**
```
生成一个清理脚本，清理30天前的临时文件
```

**参数：**
- CLEAN_TEMP: 清理临时文件
- CLEAN_RECYCLE_BIN: 清空回收站
- CLEAN_DOWNLOADS: 清理下载文件夹
- DAYS_OLD: 清理多少天前的文件
- MIN_FILE_SIZE: 最小文件大小（MB）

---

## 🎯 如何使用

### 方式1：通过AI助手（推荐）

```bash
# 启动程序
python -m src.main

# 用中文描述需求
💬 请输入 > 生成一个脚本，批量重命名桌面的照片
```

### 方式2：直接使用模板

```powershell
# 复制模板
cp templates/file_management/batch_rename.ps1 my_rename.ps1

# 手动修改参数
# 编辑 my_rename.ps1，替换 {{参数}} 占位符

# 执行脚本
.\my_rename.ps1
```

---

## 🎨 自定义模板功能

### 创建自定义模板

您可以创建自己的模板来满足特定需求：

```bash
# 交互式创建模板
python src/main.py template create
```

系统会引导您完成：
1. 输入模板基本信息（名称、描述、分类）
2. 提供脚本内容（从文件或直接输入）
3. 识别和配置参数
4. 验证并保存模板

### 管理自定义模板

```bash
# 列出所有模板
python src/main.py template list

# 只列出自定义模板
python src/main.py template list --custom-only

# 编辑模板
python src/main.py template edit <template_name>

# 删除模板
python src/main.py template delete <template_name>

# 查看模板详情
python src/main.py template info <template_name>
```

### 导入导出模板

```bash
# 导出模板（可分享给他人）
python src/main.py template export <template_name> -o template.zip

# 导入模板
python src/main.py template import template.zip
```

### 版本控制

系统自动保存模板修改历史：

```bash
# 查看历史版本
python src/main.py template history <template_name>

# 恢复到指定版本
python src/main.py template restore <template_name> <version>
```

### 自定义模板目录结构

```
templates/custom/
├── examples/              # 示例模板
│   ├── simple_backup.ps1
│   ├── log_analyzer.ps1
│   └── user_report.ps1
├── my_category/           # 用户自定义分类
│   └── my_template.ps1
└── ...
```

详细使用指南请参考：[自定义模板用户指南](../docs/custom-template-guide.md)

---

## 📝 模板规范

### 模板结构

```powershell
<#
.SYNOPSIS
    简短描述
    
.DESCRIPTION
    详细描述
    
.TEMPLATE_PARAMETERS
    {{PARAM1}} - 参数1说明
    {{PARAM2}} - 参数2说明
    
.EXAMPLE
    使用示例
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$Param1 = "{{PARAM1}}",
    ...
)

# 脚本逻辑
...
```

### 参数占位符

使用 `{{参数名}}` 格式，AI会自动替换：

```powershell
$SourcePath = "{{SOURCE_PATH}}"  # AI会替换为实际路径
$Threshold = {{CPU_THRESHOLD}}    # AI会替换为数字
$Enable = ${{USE_FEATURE}}        # AI会替换为 $true 或 $false
```

---

## 🔧 添加新模板

### 方式1：使用命令行工具（推荐）

```bash
# 交互式创建，系统会自动处理所有步骤
python src/main.py template create
```

优势：
- 自动识别参数
- 自动验证语法
- 自动更新配置
- 支持版本控制

### 方式2：手动创建（高级用户）

#### 1. 创建模板文件

```bash
# 在对应分类下创建
touch templates/分类名/模板名.ps1
```

#### 2. 编写模板

- 添加详细的注释
- 使用参数占位符 `{{PARAM_NAME}}`
- 添加错误处理
- 添加用户友好的输出

#### 3. 更新配置文件

在 `config/templates.yaml` 中添加模板配置：

```yaml
templates:
  分类名:
    模板名:
      name: "模板显示名称"
      file: "templates/分类名/模板名.ps1"
      description: "模板描述"
      keywords: ["关键词1", "关键词2"]
      parameters:
        PARAM_NAME:
          type: "string"
          default: "默认值"
          description: "参数描述"
          required: true
```

---

## 💡 最佳实践

### 1. 参数设计

- 使用有意义的参数名
- 提供合理的默认值
- 添加参数验证

### 2. 用户体验

- 显示清晰的进度信息
- 使用颜色区分不同类型的输出
- 在执行前显示预览
- 重要操作需要用户确认

### 3. 错误处理

- 使用 try-catch 捕获错误
- 提供有用的错误信息
- 优雅地处理失败情况

### 4. 日志记录

- 记录关键操作
- 显示执行结果统计
- 便于问题排查

---

## 📊 模板统计

| 分类 | 模板数 | 说明 |
|------|--------|------|
| 文件管理 | 2 | 文件操作相关 |
| 系统监控 | 1 | 系统资源监控 |
| 自动化任务 | 2 | 自动化脚本 |
| 自定义模板 | 3 | 示例自定义模板 |
| **总计** | **8** | **系统 + 自定义模板** |

---

## 🚀 未来计划

### 即将添加的模板

- [ ] 网络诊断工具
- [ ] 日志分析脚本
- [ ] Excel数据处理
- [ ] 邮件自动化
- [ ] 定时任务管理
- [ ] 文件同步工具
- [ ] 系统信息收集
- [ ] 性能测试工具

---

## 📞 贡献模板

欢迎贡献新模板！请确保：

1. 遵循模板规范
2. 添加详细注释
3. 测试脚本功能
4. 更新README文档

---

**让PowerShell脚本更智能、更易用！** 🎉
