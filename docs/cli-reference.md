<!-- 文档类型: 参考文档 | 最后更新: 2025-10-17 | 维护者: 项目团队 -->

# CLI 命令参考

> **文档类型**: 参考文档 | **最后更新**: 2025-10-17 | **维护者**: 项目团队

📍 [首页](../README.md) > [文档中心](README.md) > CLI 命令参考

## 📋 目录

- [简介](#简介)
- [通用选项](#通用选项)
- [主命令](#主命令)
- [模板管理命令](#模板管理命令)
- [命令分类索引](#命令分类索引)
- [环境变量](#环境变量)
- [配置文件](#配置文件)
- [使用示例](#使用示例)
- [故障排除](#故障排除)

---

## 简介

AI PowerShell 智能助手提供丰富的命令行接口，支持交互模式、单命令执行和模板管理等功能。本文档提供所有 CLI 命令的完整参考。

### 基本语法

```bash
python src/main.py [全局选项] [命令] [命令选项] [参数]
```

### 快速开始

```bash
# 显示帮助
python src/main.py --help

# 启动交互模式
python src/main.py --interactive

# 执行单个命令
python src/main.py --command "显示当前时间"

# 查看版本
python src/main.py --version
```

---

## 通用选项

这些选项适用于所有命令：

| 选项 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| `--help` | `-h` | 显示帮助信息 | - |
| `--version` | `-v` | 显示版本信息 | - |
| `--verbose` | - | 显示详细输出 | False |
| `--debug` | - | 启用调试模式 | False |
| `--config` | `-c` | 指定配置文件路径 | config/default.yaml |
| `--log-level` | - | 设置日志级别 | INFO |


**示例**:

```bash
# 显示帮助
python src/main.py --help

# 启用详细输出
python src/main.py --verbose --interactive

# 使用自定义配置
python src/main.py --config my-config.yaml --interactive

# 设置日志级别
python src/main.py --log-level DEBUG --interactive
```

---

## 主命令

### --interactive (交互模式)

启动交互式命令行界面，允许连续输入自然语言命令。

**语法**:
```bash
python src/main.py --interactive [选项]
```

**选项**:

| 选项 | 说明 | 默认值 |
|------|------|--------|
| `--no-color` | 禁用彩色输出 | False |
| `--no-icons` | 禁用图标显示 | False |
| `--theme` | 指定 UI 主题 | default |

**示例**:

```bash
# 启动交互模式
python src/main.py --interactive

# 使用深色主题
python src/main.py --interactive --theme dark

# 禁用彩色输出
python src/main.py --interactive --no-color
```

**交互模式命令**:

在交互模式中，可以使用以下特殊命令：

| 命令 | 说明 |
|------|------|
| `exit` 或 `quit` | 退出交互模式 |
| `help` | 显示帮助信息 |
| `history` | 显示命令历史 |
| `clear` | 清空屏幕 |
| `config` | 显示当前配置 |


### --command (单命令执行)

执行单个自然语言命令并退出。

**语法**:
```bash
python src/main.py --command "<自然语言命令>" [选项]
```

**选项**:

| 选项 | 说明 | 默认值 |
|------|------|--------|
| `--auto-execute` | 自动执行生成的命令 | False |
| `--no-confirm` | 跳过确认提示 | False |
| `--output` | 指定输出文件 | - |

**示例**:

```bash
# 执行单个命令
python src/main.py --command "显示当前时间"

# 自动执行（跳过确认）
python src/main.py --command "列出所有文件" --auto-execute

# 保存输出到文件
python src/main.py --command "获取系统信息" --output system-info.txt
```

### --version (版本信息)

显示程序版本信息。

**语法**:
```bash
python src/main.py --version
```

**输出示例**:
```
AI PowerShell 智能助手 v2.0.0
Python 3.10.0
PowerShell 7.3.0
```

### --help (帮助信息)

显示命令行帮助信息。

**语法**:
```bash
python src/main.py --help
python src/main.py <command> --help
```

**示例**:

```bash
# 显示主帮助
python src/main.py --help

# 显示模板命令帮助
python src/main.py template --help

# 显示特定子命令帮助
python src/main.py template create --help
```


---

## 模板管理命令

模板管理功能通过 `template` 子命令提供。

**基本语法**:
```bash
python src/main.py template <子命令> [选项] [参数]
```

### template create (创建模板)

创建一个新的自定义模板。

**语法**:
```bash
python src/main.py template create [选项]
```

**选项**:

| 选项 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| `--name` | string | 模板名称 | - |
| `--description` | string | 模板描述 | - |
| `--category` | string | 模板分类 | - |
| `--keywords` | string | 关键词（逗号分隔） | - |
| `--from-file` | path | 从文件导入脚本 | - |
| `--interactive` | flag | 交互式创建（默认） | True |

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

1. 输入模板基本信息（名称、描述、分类、关键词）
2. 选择脚本来源（文件或直接输入）
3. 系统自动识别参数
4. 配置每个参数的类型和属性
5. 验证并保存


### template list (列出模板)

列出所有可用的模板。

**语法**:
```bash
python src/main.py template list [选项]
```

**选项**:

| 选项 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| `--custom-only` | flag | 只显示自定义模板 | False |
| `--category` | string | 按分类筛选 | - |
| `--keyword` | string | 按关键词搜索 | - |
| `--format` | string | 输出格式 (table/json/yaml) | table |

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


### template info (查看模板详情)

显示模板的详细信息。

**语法**:
```bash
python src/main.py template info <template_name> [选项]
```

**参数**:

| 参数 | 类型 | 说明 | 必需 |
|------|------|------|------|
| `template_name` | string | 模板名称或ID | 是 |

**选项**:

| 选项 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| `--show-content` | flag | 显示模板脚本内容 | False |
| `--format` | string | 输出格式 (text/json/yaml) | text |

**示例**:

```bash
# 查看模板详情
python src/main.py template info daily_backup

# 包含脚本内容
python src/main.py template info daily_backup --show-content

# JSON 格式
python src/main.py template info daily_backup --format json
```

### template edit (编辑模板)

编辑现有模板的配置或内容。

**语法**:
```bash
python src/main.py template edit <template_name> [选项]
```

**参数**:

| 参数 | 类型 | 说明 | 必需 |
|------|------|------|------|
| `template_name` | string | 模板名称或ID | 是 |

**选项**:

| 选项 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| `--name` | string | 更新模板名称 | - |
| `--description` | string | 更新描述 | - |
| `--keywords` | string | 更新关键词 | - |
| `--interactive` | flag | 交互式编辑（默认） | True |

**示例**:

```bash
# 交互式编辑
python src/main.py template edit daily_backup

# 更新描述
python src/main.py template edit daily_backup --description "新的描述"

# 更新关键词
python src/main.py template edit daily_backup --keywords "backup,daily,files"
```


### template delete (删除模板)

删除自定义模板。

**语法**:
```bash
python src/main.py template delete <template_name> [选项]
```

**参数**:

| 参数 | 类型 | 说明 | 必需 |
|------|------|------|------|
| `template_name` | string | 模板名称或ID | 是 |

**选项**:

| 选项 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| `--force` | flag | 跳过确认提示 | False |
| `--keep-backup` | flag | 保留备份副本 | False |

**示例**:

```bash
# 删除模板（需要确认）
python src/main.py template delete daily_backup

# 强制删除（跳过确认）
python src/main.py template delete daily_backup --force

# 删除但保留备份
python src/main.py template delete daily_backup --keep-backup
```

### template export (导出模板)

将模板导出为 ZIP 包，便于分享或备份。

**语法**:
```bash
python src/main.py template export <template_name> [选项]
```

**参数**:

| 参数 | 类型 | 说明 | 必需 |
|------|------|------|------|
| `template_name` | string | 模板名称或ID（可多个） | 是 |

**选项**:

| 选项 | 简写 | 类型 | 说明 | 默认值 |
|------|------|------|------|--------|
| `--output` | `-o` | path | 输出文件路径 | - |
| `--include-history` | - | flag | 包含版本历史 | False |

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


### template import (导入模板)

从 ZIP 包导入模板。

**语法**:
```bash
python src/main.py template import <package_path> [选项]
```

**参数**:

| 参数 | 类型 | 说明 | 必需 |
|------|------|------|------|
| `package_path` | path | ZIP 包路径 | 是 |

**选项**:

| 选项 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| `--overwrite` | flag | 覆盖同名模板 | False |
| `--rename` | string | 重命名导入的模板 | - |
| `--category` | string | 指定导入分类 | - |

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

### template history (查看版本历史)

查看模板的修改历史。

**语法**:
```bash
python src/main.py template history <template_name> [选项]
```

**参数**:

| 参数 | 类型 | 说明 | 必需 |
|------|------|------|------|
| `template_name` | string | 模板名称或ID | 是 |

**选项**:

| 选项 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| `--limit` | int | 显示的版本数量 | 10 |
| `--show-diff` | flag | 显示版本差异 | False |

**示例**:

```bash
# 查看历史
python src/main.py template history daily_backup

# 限制显示数量
python src/main.py template history daily_backup --limit 5

# 显示差异
python src/main.py template history daily_backup --show-diff
```


### template restore (恢复历史版本)

将模板恢复到指定的历史版本。

**语法**:
```bash
python src/main.py template restore <template_name> <version> [选项]
```

**参数**:

| 参数 | 类型 | 说明 | 必需 |
|------|------|------|------|
| `template_name` | string | 模板名称或ID | 是 |
| `version` | int | 版本号 | 是 |

**选项**:

| 选项 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| `--force` | flag | 跳过确认提示 | False |
| `--preview` | flag | 预览版本内容 | False |

**示例**:

```bash
# 恢复到版本 2
python src/main.py template restore daily_backup 2

# 预览版本
python src/main.py template restore daily_backup 2 --preview

# 强制恢复
python src/main.py template restore daily_backup 2 --force
```

### template test (测试模板)

使用示例参数测试模板生成。

**语法**:
```bash
python src/main.py template test <template_name> [选项]
```

**参数**:

| 参数 | 类型 | 说明 | 必需 |
|------|------|------|------|
| `template_name` | string | 模板名称或ID | 是 |

**选项**:

| 选项 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| `--params` | string | 自定义参数 (JSON格式) | - |
| `--execute` | flag | 执行生成的脚本 | False |
| `--save` | path | 保存生成的脚本 | - |

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


### template validate (验证模板)

验证模板的语法和配置。

**语法**:
```bash
python src/main.py template validate <template_name> [选项]
```

**参数**:

| 参数 | 类型 | 说明 | 必需 |
|------|------|------|------|
| `template_name` | string | 模板名称或ID | 是 |

**选项**:

| 选项 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| `--strict` | flag | 严格模式验证 | False |
| `--fix` | flag | 自动修复问题 | False |

**示例**:

```bash
# 验证模板
python src/main.py template validate daily_backup

# 严格模式
python src/main.py template validate daily_backup --strict

# 自动修复
python src/main.py template validate daily_backup --fix
```

### template category (分类管理)

管理模板分类。

**语法**:
```bash
python src/main.py template category <action> [选项]
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

## 命令分类索引

### 按功能分类

#### 交互和执行
- [`--interactive`](#--interactive-交互模式) - 启动交互模式
- [`--command`](#--command-单命令执行) - 执行单个命令

#### 信息查询
- [`--version`](#--version-版本信息) - 显示版本信息
- [`--help`](#--help-帮助信息) - 显示帮助信息

#### 模板创建和编辑
- [`template create`](#template-create-创建模板) - 创建新模板
- [`template edit`](#template-edit-编辑模板) - 编辑模板
- [`template delete`](#template-delete-删除模板) - 删除模板

#### 模板查询
- [`template list`](#template-list-列出模板) - 列出模板
- [`template info`](#template-info-查看模板详情) - 查看模板详情

#### 模板导入导出
- [`template export`](#template-export-导出模板) - 导出模板
- [`template import`](#template-import-导入模板) - 导入模板

#### 模板版本管理
- [`template history`](#template-history-查看版本历史) - 查看历史
- [`template restore`](#template-restore-恢复历史版本) - 恢复版本

#### 模板测试和验证
- [`template test`](#template-test-测试模板) - 测试模板
- [`template validate`](#template-validate-验证模板) - 验证模板

#### 分类管理
- [`template category create`](#template-category-分类管理) - 创建分类
- [`template category list`](#template-category-分类管理) - 列出分类
- [`template category delete`](#template-category-分类管理) - 删除分类
- [`template category move`](#template-category-分类管理) - 移动模板

### 按字母顺序

| 命令 | 说明 |
|------|------|
| `--command` | 执行单个命令 |
| `--help` | 显示帮助信息 |
| `--interactive` | 启动交互模式 |
| `--version` | 显示版本信息 |
| `template category create` | 创建分类 |
| `template category delete` | 删除分类 |
| `template category list` | 列出分类 |
| `template category move` | 移动模板 |
| `template create` | 创建模板 |
| `template delete` | 删除模板 |
| `template edit` | 编辑模板 |
| `template export` | 导出模板 |
| `template history` | 查看历史 |
| `template import` | 导入模板 |
| `template info` | 查看详情 |
| `template list` | 列出模板 |
| `template restore` | 恢复版本 |
| `template test` | 测试模板 |
| `template validate` | 验证模板 |


---

## 环境变量

可以通过环境变量配置系统行为：

| 变量 | 说明 | 默认值 | 示例 |
|------|------|--------|------|
| `AI_POWERSHELL_CONFIG` | 配置文件路径 | `config/default.yaml` | `config/custom.yaml` |
| `AI_POWERSHELL_LOG_LEVEL` | 日志级别 | `INFO` | `DEBUG`, `WARNING` |
| `AI_POWERSHELL_LOG_DIR` | 日志目录 | `logs/` | `/var/log/ai-powershell/` |
| `TEMPLATE_DIR` | 模板目录路径 | `templates/` | `/custom/templates/` |
| `TEMPLATE_CONFIG` | 模板配置文件 | `config/templates.yaml` | `config/my-templates.yaml` |
| `TEMPLATE_HISTORY_MAX` | 最大历史版本数 | `10` | `20` |
| `TEMPLATE_AUTO_BACKUP` | 自动备份 | `true` | `false` |
| `STORAGE_DIR` | 存储目录 | `~/.ai-powershell/` | `/data/ai-powershell/` |

**Windows 示例**:

```cmd
# 设置环境变量
set AI_POWERSHELL_LOG_LEVEL=DEBUG
set TEMPLATE_HISTORY_MAX=20

# 运行程序
python src/main.py --interactive
```

**Linux/macOS 示例**:

```bash
# 设置环境变量
export AI_POWERSHELL_LOG_LEVEL=DEBUG
export TEMPLATE_HISTORY_MAX=20

# 运行程序
python src/main.py --interactive

# 或一次性设置
AI_POWERSHELL_LOG_LEVEL=DEBUG python src/main.py --interactive
```

---

## 配置文件

### 配置文件位置

配置文件按以下优先级加载：

1. 命令行指定: `--config <path>`
2. 环境变量: `$AI_POWERSHELL_CONFIG`
3. 项目配置: `config/default.yaml`
4. 用户配置: `~/.ai-powershell/config.yaml`

### 配置文件格式

```yaml
# config/default.yaml

# AI 引擎配置
ai:
  provider: "ollama"
  model_name: "llama3"
  temperature: 0.7
  max_tokens: 256

# 安全配置
security:
  whitelist_mode: "strict"
  require_confirmation: true
  sandbox_enabled: false

# 执行配置
execution:
  timeout: 30
  max_retries: 3
  shell: "powershell"

# 日志配置
logging:
  level: "INFO"
  format: "detailed"
  max_file_size: 10485760  # 10MB
  backup_count: 5

# 模板配置
templates:
  auto_backup: true
  history_max: 10
  validation_strict: false

# UI 配置
ui:
  colors:
    enabled: true
    theme: "default"
  icons:
    enabled: true
    style: "emoji"
  display:
    max_width: 120
    page_size: 20
```


---

## 使用示例

### 场景 1: 日常使用

```bash
# 启动交互模式
python src/main.py --interactive

# 在交互模式中输入命令
> 显示当前时间
> 列出所有正在运行的进程
> 检查网络连接状态
> exit
```

### 场景 2: 创建和使用自定义模板

```bash
# 1. 创建模板
python src/main.py template create --from-file my_backup.ps1

# 2. 查看模板
python src/main.py template info my_backup

# 3. 测试模板
python src/main.py template test my_backup

# 4. 使用 AI 生成脚本
python src/main.py --interactive
> 使用我的备份模板备份文档
```

### 场景 3: 分享模板给团队

```bash
# 1. 导出模板
python src/main.py template export my_backup -o team_backup.zip

# 2. 团队成员导入
python src/main.py template import team_backup.zip

# 3. 查看导入的模板
python src/main.py template list --custom-only
```

### 场景 4: 管理模板版本

```bash
# 1. 编辑模板
python src/main.py template edit my_backup

# 2. 查看历史
python src/main.py template history my_backup

# 3. 如果需要，恢复旧版本
python src/main.py template restore my_backup 2
```

### 场景 5: 组织模板分类

```bash
# 1. 创建新分类
python src/main.py template category create my_tools

# 2. 移动模板到新分类
python src/main.py template category move my_backup my_tools

# 3. 查看分类下的模板
python src/main.py template list --category my_tools
```

### 场景 6: 批量操作

```bash
# 导出多个模板
python src/main.py template export backup1 backup2 backup3 -o all_backups.zip

# 使用自定义配置运行
python src/main.py --config production.yaml --interactive

# 执行命令并保存输出
python src/main.py --command "获取系统信息" --output system-info.txt
```

### 场景 7: 调试和开发

```bash
# 启用调试模式
python src/main.py --debug --verbose --interactive

# 验证模板
python src/main.py template validate my_template --strict

# 测试模板并保存结果
python src/main.py template test my_template --save test_output.ps1
```


---

## 故障排除

### 常见错误

#### 错误: 模板不存在

```
Error: Template 'my_template' not found
```

**解决方案**:
```bash
# 列出所有可用模板
python src/main.py template list

# 检查模板名称拼写
python src/main.py template list --keyword my
```

#### 错误: 语法验证失败

```
Error: PowerShell syntax error at line 10
```

**解决方案**:
```bash
# 使用验证命令检查
python src/main.py template validate my_template

# 在 PowerShell ISE 中检查脚本语法
# 或使用 --fix 选项自动修复
python src/main.py template validate my_template --fix
```

#### 错误: 参数冲突

```
Error: Parameter 'PATH' is not defined in template
```

**解决方案**:
- 确保所有占位符都在配置中定义
- 参数名使用大写字母和下划线
- 检查是否有拼写错误

#### 错误: 导入失败

```
Error: Failed to import template package
```

**解决方案**:
```bash
# 检查 ZIP 包是否损坏
# 使用 --verbose 查看详细错误
python src/main.py template import backup.zip --verbose

# 确保 ZIP 包是通过系统导出功能创建的
```

#### 错误: 权限不足

```
Error: Permission denied
```

**解决方案**:
```bash
# Windows: 以管理员身份运行
# Linux/macOS: 使用 sudo
sudo python src/main.py --interactive
```

### 调试技巧

#### 启用详细日志

```bash
# 使用 --verbose 选项
python src/main.py --verbose template create

# 或设置日志级别
python src/main.py --log-level DEBUG --interactive
```

#### 查看配置

```bash
# 在交互模式中
python src/main.py --interactive
> config

# 或使用环境变量
set AI_POWERSHELL_LOG_LEVEL=DEBUG
python src/main.py --interactive
```

#### 测试模板

```bash
# 使用测试命令
python src/main.py template test my_template

# 使用自定义参数测试
python src/main.py template test my_template --params '{"PATH":"C:\\Test"}'

# 保存测试结果
python src/main.py template test my_template --save test_output.ps1
```

### 获取帮助

```bash
# 查看命令帮助
python src/main.py --help

# 查看子命令帮助
python src/main.py template --help

# 查看特定命令帮助
python src/main.py template create --help
```

### 常见问题解答

**Q: 如何更改默认配置？**

A: 创建自定义配置文件并使用 `--config` 选项：
```bash
python src/main.py --config my-config.yaml --interactive
```

**Q: 如何禁用彩色输出？**

A: 使用 `--no-color` 选项：
```bash
python src/main.py --interactive --no-color
```

**Q: 如何查看所有可用的模板？**

A: 使用 `template list` 命令：
```bash
python src/main.py template list
```

**Q: 如何备份所有模板？**

A: 导出所有自定义模板：
```bash
# 列出所有自定义模板
python src/main.py template list --custom-only

# 导出所有模板
python src/main.py template export template1 template2 template3 -o all_templates.zip
```

**Q: 如何重置配置？**

A: 删除用户配置文件：
```bash
# Windows
del %USERPROFILE%\.ai-powershell\config.yaml

# Linux/macOS
rm ~/.ai-powershell/config.yaml
```

---

## 相关文档

- [用户指南](user-guide.md) - 系统整体使用指南
- [模板系统指南](template-guide.md) - 详细的模板使用和创建指南
- [配置参考](config-reference.md) - 完整的配置选项说明
- [API 参考](api-reference.md) - API 接口文档
- [故障排除指南](troubleshooting.md) - 更多问题解决方案

## 下一步

- 📖 阅读 [模板系统指南](template-guide.md) 学习如何创建自定义模板
- 🔧 查看 [配置参考](config-reference.md) 了解所有配置选项
- 💻 参考 [开发者指南](developer-guide.md) 参与项目开发
- 🐛 遇到问题？查看 [故障排除指南](troubleshooting.md)

---

**需要帮助?** 查看 [故障排除指南](troubleshooting.md) 或访问 [GitHub Issues](https://github.com/0green7hand0/AI-PowerShell/issues)

**提示**: 使用 `--help` 选项查看任何命令的详细帮助信息。

