# 模板管理命令行参考

本文档提供自定义模板管理的完整命令行参考。

## 目录

- [概述](#概述)
- [通用选项](#通用选项)
- [命令列表](#命令列表)
- [使用示例](#使用示例)

## 概述

模板管理功能通过 `template` 子命令提供，支持创建、编辑、删除、导入导出等操作。

**基本语法**:
```bash
python src/main.py template <command> [options]
```

## 通用选项

这些选项适用于所有模板命令：

| 选项 | 说明 |
|------|------|
| `-h, --help` | 显示帮助信息 |
| `-v, --verbose` | 显示详细输出 |
| `--debug` | 启用调试模式 |

## 命令列表

### create - 创建新模板

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

**交互流程**:

1. 输入模板基本信息
2. 选择脚本来源（文件或直接输入）
3. 系统自动识别参数
4. 配置每个参数的类型和属性
5. 验证并保存

---

### list - 列出模板

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

# JSON 格式输出
python src/main.py template list --format json
```

**输出示例**:

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
```

---

### info - 查看模板详情

显示模板的详细信息。

**语法**:
```bash
python src/main.py template info <template_name> [options]
```

**参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| `template_name` | string | 模板名称或ID |

**选项**:

| 选项 | 类型 | 说明 |
|------|------|------|
| `--show-content` | flag | 显示模板脚本内容 |
| `--format` | string | 输出格式 (text/json/yaml) |

**示例**:

```bash
# 查看模板详情
python src/main.py template info daily_backup

# 包含脚本内容
python src/main.py template info daily_backup --show-content

# JSON 格式
python src/main.py template info daily_backup --format json
```

**输出示例**:

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
```

---

### edit - 编辑模板

编辑现有模板的配置或内容。

**语法**:
```bash
python src/main.py template edit <template_name> [options]
```

**参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| `template_name` | string | 模板名称或ID |

**选项**:

| 选项 | 类型 | 说明 |
|------|------|------|
| `--name` | string | 更新模板名称 |
| `--description` | string | 更新描述 |
| `--keywords` | string | 更新关键词 |
| `--interactive` | flag | 交互式编辑（默认） |

**示例**:

```bash
# 交互式编辑
python src/main.py template edit daily_backup

# 更新描述
python src/main.py template edit daily_backup --description "新的描述"

# 更新关键词
python src/main.py template edit daily_backup --keywords "backup,daily,files"
```

**交互菜单**:

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

---

### delete - 删除模板

删除自定义模板。

**语法**:
```bash
python src/main.py template delete <template_name> [options]
```

**参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| `template_name` | string | 模板名称或ID |

**选项**:

| 选项 | 类型 | 说明 |
|------|------|------|
| `--force` | flag | 跳过确认提示 |
| `--keep-backup` | flag | 保留备份副本 |

**示例**:

```bash
# 删除模板（需要确认）
python src/main.py template delete daily_backup

# 强制删除（跳过确认）
python src/main.py template delete daily_backup --force

# 删除但保留备份
python src/main.py template delete daily_backup --keep-backup
```

**确认提示**:

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

---

### export - 导出模板

将模板导出为 ZIP 包，便于分享或备份。

**语法**:
```bash
python src/main.py template export <template_name> [options]
```

**参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| `template_name` | string | 模板名称或ID（可多个） |

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

# 包含版本历史
python src/main.py template export daily_backup --include-history -o backup_full.zip

# 导出到默认位置
python src/main.py template export daily_backup
```

**输出**:

```
📦 导出模板
===========

正在导出: daily_backup
✓ 模板文件已添加
✓ 配置文件已添加
✓ 元数据已添加

导出完成: daily_backup_20251007.zip
大小: 15.3 KB
```

---

### import - 导入模板

从 ZIP 包导入模板。

**语法**:
```bash
python src/main.py template import <package_path> [options]
```

**参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| `package_path` | path | ZIP 包路径 |

**选项**:

| 选项 | 类型 | 说明 |
|------|------|------|
| `--overwrite` | flag | 覆盖同名模板 |
| `--rename` | string | 重命名导入的模板 |
| `--category` | string | 指定导入分类 |

**示例**:

```bash
# 导入模板
python src/main.py template import backup.zip

# 覆盖同名模板
python src/main.py template import backup.zip --overwrite

# 重命名导入
python src/main.py template import backup.zip --rename new_backup

# 指定分类
python src/main.py template import backup.zip --category my_tools
```

**冲突处理**:

```
⚠️ 模板冲突
===========

模板 'daily_backup' 已存在

[1] 覆盖现有模板
[2] 重命名为 'daily_backup_imported'
[3] 取消导入

选择操作:
```

---

### history - 查看版本历史

查看模板的修改历史。

**语法**:
```bash
python src/main.py template history <template_name> [options]
```

**参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| `template_name` | string | 模板名称或ID |

**选项**:

| 选项 | 类型 | 说明 |
|------|------|------|
| `--limit` | int | 显示的版本数量 |
| `--show-diff` | flag | 显示版本差异 |

**示例**:

```bash
# 查看历史
python src/main.py template history daily_backup

# 限制显示数量
python src/main.py template history daily_backup --limit 5

# 显示差异
python src/main.py template history daily_backup --show-diff
```

**输出示例**:

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

---

### restore - 恢复历史版本

将模板恢复到指定的历史版本。

**语法**:
```bash
python src/main.py template restore <template_name> <version> [options]
```

**参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| `template_name` | string | 模板名称或ID |
| `version` | int | 版本号 |

**选项**:

| 选项 | 类型 | 说明 |
|------|------|------|
| `--force` | flag | 跳过确认提示 |
| `--preview` | flag | 预览版本内容 |

**示例**:

```bash
# 恢复到版本 2
python src/main.py template restore daily_backup 2

# 预览版本
python src/main.py template restore daily_backup 2 --preview

# 强制恢复
python src/main.py template restore daily_backup 2 --force
```

**确认提示**:

```
⚠️ 恢复确认
============

将模板 'daily_backup' 恢复到版本 2

版本信息:
  时间: 2025-10-07 12:00:00
  修改: 更新了默认备份路径

当前版本将被保存为新的历史版本

确认恢复? [y/n]:
```

---

### test - 测试模板

使用示例参数测试模板生成。

**语法**:
```bash
python src/main.py template test <template_name> [options]
```

**参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| `template_name` | string | 模板名称或ID |

**选项**:

| 选项 | 类型 | 说明 |
|------|------|------|
| `--params` | string | 自定义参数 (JSON格式) |
| `--execute` | flag | 执行生成的脚本 |
| `--save` | path | 保存生成的脚本 |

**示例**:

```bash
# 使用默认参数测试
python src/main.py template test daily_backup

# 使用自定义参数
python src/main.py template test daily_backup --params '{"SOURCE_PATH":"C:\\Test"}'

# 测试并执行
python src/main.py template test daily_backup --execute

# 保存生成的脚本
python src/main.py template test daily_backup --save test_backup.ps1
```

**输出示例**:

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

✓ 语法验证通过

是否执行测试脚本? [y/n]:
```

---

### validate - 验证模板

验证模板的语法和配置。

**语法**:
```bash
python src/main.py template validate <template_name> [options]
```

**参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| `template_name` | string | 模板名称或ID |

**选项**:

| 选项 | 类型 | 说明 |
|------|------|------|
| `--strict` | flag | 严格模式验证 |
| `--fix` | flag | 自动修复问题 |

**示例**:

```bash
# 验证模板
python src/main.py template validate daily_backup

# 严格模式
python src/main.py template validate daily_backup --strict

# 自动修复
python src/main.py template validate daily_backup --fix
```

**输出示例**:

```
✓ PowerShell 语法检查通过
✓ 参数配置有效
✓ 占位符一致性检查通过
✓ 安全检查通过

模板验证通过！
```

---

### category - 分类管理

管理模板分类。

**语法**:
```bash
python src/main.py template category <action> [options]
```

**子命令**:

#### create - 创建分类

```bash
python src/main.py template category create <category_name> [--description "描述"]
```

#### list - 列出分类

```bash
python src/main.py template category list
```

#### delete - 删除分类

```bash
python src/main.py template category delete <category_name>
```

#### move - 移动模板

```bash
python src/main.py template category move <template_name> <target_category>
```

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

---

## 使用示例

### 场景1: 创建并使用自定义备份模板

```bash
# 1. 创建模板
python src/main.py template create --from-file my_backup.ps1

# 2. 查看模板
python src/main.py template info my_backup

# 3. 测试模板
python src/main.py template test my_backup

# 4. 使用 AI 生成脚本
python src/main.py
💬 请输入 > 使用我的备份模板备份文档
```

### 场景2: 分享模板给团队

```bash
# 1. 导出模板
python src/main.py template export my_backup -o team_backup.zip

# 2. 团队成员导入
python src/main.py template import team_backup.zip

# 3. 查看导入的模板
python src/main.py template list --custom-only
```

### 场景3: 管理模板版本

```bash
# 1. 编辑模板
python src/main.py template edit my_backup

# 2. 查看历史
python src/main.py template history my_backup

# 3. 如果需要，恢复旧版本
python src/main.py template restore my_backup 2
```

### 场景4: 组织模板分类

```bash
# 1. 创建新分类
python src/main.py template category create my_tools

# 2. 移动模板到新分类
python src/main.py template category move my_backup my_tools

# 3. 查看分类下的模板
python src/main.py template list --category my_tools
```

---

## 环境变量

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

---

## 配置文件

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

## 故障排除

### 常见错误

#### 错误: 模板不存在

```
Error: Template 'my_template' not found
```

**解决**: 使用 `template list` 查看可用模板

#### 错误: 语法验证失败

```
Error: PowerShell syntax error at line 10
```

**解决**: 在 PowerShell ISE 中检查脚本语法

#### 错误: 参数冲突

```
Error: Parameter 'PATH' is not defined in template
```

**解决**: 确保所有占位符都在配置中定义

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

---

## 相关文档

- [自定义模板用户指南](custom-template-guide.md)
- [模板系统架构](architecture.md)
- [开发者指南](developer-guide.md)

---

**提示**: 使用 `--help` 选项查看任何命令的详细帮助信息。
