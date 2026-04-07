<!-- 文档类型: 参考文档 | 最后更新: 2025-01-17 | 维护者: 项目团队 -->

# 配置参考文档

📍 [首页](../README.md) > [文档中心](README.md) > 配置参考文档

## 📋 目录

- [简介](#简介)
- [配置文件概述](#配置文件概述)
- [default.yaml - 主配置文件](#defaultyaml---主配置文件)
  - [AI 引擎配置](#ai-引擎配置)
  - [安全引擎配置](#安全引擎配置)
  - [执行引擎配置](#执行引擎配置)
  - [日志配置](#日志配置)
  - [存储配置](#存储配置)
  - [上下文管理配置](#上下文管理配置)
- [templates.yaml - 模板配置文件](#templatesyaml---模板配置文件)
- [ui.yaml - UI 配置文件](#uiyaml---ui-配置文件)
- [配置最佳实践](#配置最佳实践)
- [常见配置场景](#常见配置场景)
- [配置验证](#配置验证)
- [故障排除](#故障排除)

## 简介

AI PowerShell 智能助手使用 YAML 格式的配置文件来管理系统行为。本文档提供所有配置项的完整参考，包括名称、类型、默认值、说明和使用示例。

## 配置文件概述

系统使用三个主要配置文件：

| 配置文件 | 位置 | 用途 |
|---------|------|------|
| `default.yaml` | `config/default.yaml` | 主配置文件，包含所有核心系统设置 |
| `templates.yaml` | `config/templates.yaml` | 模板系统配置，定义脚本模板和匹配规则 |
| `ui.yaml` | `config/ui.yaml` | 用户界面配置，控制 CLI 外观和行为 |

**配置文件查找顺序**：
1. `config/default.yaml`
2. `config.yaml`
3. `~/.ai-powershell/config.yaml`

## default.yaml - 主配置文件

### AI 引擎配置

控制 AI 模型的行为和性能。

#### `ai.provider`

- **类型**: `string`
- **默认值**: `ollama`
- **可选值**: `local`, `ollama`, `openai`, `azure`
- **说明**: AI 提供商类型
- **示例**:
  ```yaml
  ai:
    provider: ollama
  ```

#### `ai.model_name`

- **类型**: `string`
- **默认值**: `qwen3:30b`
- **说明**: AI 模型名称，根据提供商不同而不同
- **示例**:
  - Ollama: `llama2`, `codellama`, `qwen3:30b`
  - OpenAI: `gpt-3.5-turbo`, `gpt-4`
  ```yaml
  ai:
    model_name: qwen3:30b
  ```

#### `ai.ollama_url`

- **类型**: `string`
- **默认值**: `http://localhost:11434`
- **说明**: Ollama 服务地址
- **示例**:
  ```yaml
  ai:
    ollama_url: http://localhost:11434
  ```

#### `ai.temperature`

- **类型**: `float`
- **默认值**: `0.7`
- **范围**: `0.0 - 2.0`
- **说明**: 生成温度，较低的值使输出更确定，较高的值使输出更随机
- **示例**:
  ```yaml
  ai:
    temperature: 0.7  # 平衡的创造性
  ```

#### `ai.max_tokens`

- **类型**: `integer`
- **默认值**: `256`
- **范围**: `1 - 4096`
- **说明**: 最大生成 token 数
- **示例**:
  ```yaml
  ai:
    max_tokens: 512  # 更长的响应
  ```

#### `ai.use_ai_provider`

- **类型**: `boolean`
- **默认值**: `true`
- **说明**: 是否启用 AI 提供商，设置为 false 时只使用规则匹配
- **示例**:
  ```yaml
  ai:
    use_ai_provider: true
  ```

#### `ai.cache_enabled`

- **类型**: `boolean`
- **默认值**: `true`
- **说明**: 是否启用翻译缓存，可加快重复查询的响应速度
- **示例**:
  ```yaml
  ai:
    cache_enabled: true
  ```

#### `ai.cache_size`

- **类型**: `integer`
- **默认值**: `100`
- **说明**: 缓存大小（条目数）
- **示例**:
  ```yaml
  ai:
    cache_size: 200  # 更大的缓存
  ```

### 安全引擎配置

控制命令执行的安全策略。

#### `security.sandbox_enabled`

- **类型**: `boolean`
- **默认值**: `false`
- **说明**: 是否启用沙箱执行
- **示例**:
  ```yaml
  security:
    sandbox_enabled: false
  ```

#### `security.require_confirmation`

- **类型**: `boolean`
- **默认值**: `true`
- **说明**: 执行命令前是否要求用户确认
- **示例**:
  ```yaml
  security:
    require_confirmation: true
  ```

#### `security.whitelist_mode`

- **类型**: `string`
- **默认值**: `strict`
- **可选值**: `strict` (严格), `moderate` (中等), `permissive` (宽松)
- **说明**: 白名单模式，控制安全检查的严格程度
- **示例**:
  ```yaml
  security:
    whitelist_mode: moderate
  ```

#### `security.dangerous_patterns`

- **类型**: `list[string]`
- **默认值**: 见下方
- **说明**: 危险命令模式列表，使用正则表达式匹配
- **示例**:
  ```yaml
  security:
    dangerous_patterns:
      - Remove-Item.*-Recurse.*-Force
      - Format-Volume
      - Stop-Computer
      - Restart-Computer
  ```

#### `security.safe_prefixes`

- **类型**: `list[string]`
- **默认值**: 见下方
- **说明**: 安全命令前缀列表，以这些前缀开头的命令被认为是安全的
- **示例**:
  ```yaml
  security:
    safe_prefixes:
      - Get-
      - Show-
      - Test-
      - Find-
  ```

#### `security.custom_rules`

- **类型**: `list`
- **默认值**: `[]`
- **说明**: 自定义安全规则
- **示例**:
  ```yaml
  security:
    custom_rules:
      - pattern: ".*dangerous.*"
        action: "block"
  ```

### 执行引擎配置

控制命令执行的行为。

#### `execution.timeout`

- **类型**: `integer`
- **默认值**: `30`
- **范围**: `1 - 300`
- **单位**: 秒
- **说明**: 命令执行超时时间
- **示例**:
  ```yaml
  execution:
    timeout: 60  # 1分钟超时
  ```

#### `execution.encoding`

- **类型**: `string`
- **默认值**: `gbk`
- **说明**: 输出编码格式，Windows 中文系统建议使用 gbk，Linux/macOS 建议使用 utf-8
- **示例**:
  ```yaml
  execution:
    encoding: utf-8
  ```

#### `execution.platform`

- **类型**: `string`
- **默认值**: `auto`
- **可选值**: `auto`, `windows`, `linux`, `macos`
- **说明**: 平台类型，auto 表示自动检测
- **示例**:
  ```yaml
  execution:
    platform: windows
  ```

#### `execution.powershell_path`

- **类型**: `string` 或 `null`
- **默认值**: `null`
- **说明**: PowerShell 可执行文件路径，null 表示自动检测
- **示例**:
  ```yaml
  execution:
    powershell_path: "C:\\Program Files\\PowerShell\\7\\pwsh.exe"
  ```

#### `execution.auto_detect_powershell`

- **类型**: `boolean`
- **默认值**: `true`
- **说明**: 是否自动检测 PowerShell，会自动查找 pwsh 或 powershell
- **示例**:
  ```yaml
  execution:
    auto_detect_powershell: true
  ```

### 日志配置

控制日志记录的行为。

#### `logging.level`

- **类型**: `string`
- **默认值**: `INFO`
- **可选值**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- **说明**: 日志级别
- **示例**:
  ```yaml
  logging:
    level: DEBUG  # 详细调试信息
  ```

#### `logging.file`

- **类型**: `string` 或 `null`
- **默认值**: `logs/assistant.log`
- **说明**: 日志文件路径，null 表示不写入文件
- **示例**:
  ```yaml
  logging:
    file: logs/app.log
  ```

#### `logging.max_size`

- **类型**: `string`
- **默认值**: `10MB`
- **说明**: 日志文件最大大小，支持单位 KB, MB, GB
- **示例**:
  ```yaml
  logging:
    max_size: 50MB
  ```

#### `logging.backup_count`

- **类型**: `integer`
- **默认值**: `5`
- **说明**: 日志文件备份数量，当日志文件达到最大大小时会创建备份
- **示例**:
  ```yaml
  logging:
    backup_count: 10
  ```

#### `logging.format`

- **类型**: `string`
- **默认值**: `'%(asctime)s - %(name)s - %(levelname)s - %(message)s'`
- **说明**: 日志格式，使用 Python logging 格式字符串
- **示例**:
  ```yaml
  logging:
    format: '%(asctime)s [%(levelname)s] %(message)s'
  ```

#### `logging.console_output`

- **类型**: `boolean`
- **默认值**: `true`
- **说明**: 是否输出到控制台
- **示例**:
  ```yaml
  logging:
    console_output: false  # 只写入文件
  ```

### 存储配置

控制数据存储的位置和行为。

#### `storage.base_path`

- **类型**: `string`
- **默认值**: `~/.ai-powershell`
- **说明**: 存储基础路径，支持 ~ 表示用户主目录
- **示例**:
  ```yaml
  storage:
    base_path: ~/Documents/ai-powershell
  ```

#### `storage.history_file`

- **类型**: `string`
- **默认值**: `history.json`
- **说明**: 历史记录文件名
- **示例**:
  ```yaml
  storage:
    history_file: command_history.json
  ```

#### `storage.config_file`

- **类型**: `string`
- **默认值**: `config.yaml`
- **说明**: 配置文件名
- **示例**:
  ```yaml
  storage:
    config_file: settings.yaml
  ```

#### `storage.cache_dir`

- **类型**: `string`
- **默认值**: `cache`
- **说明**: 缓存目录名
- **示例**:
  ```yaml
  storage:
    cache_dir: temp_cache
  ```

#### `storage.max_history_size`

- **类型**: `integer`
- **默认值**: `1000`
- **说明**: 最大历史记录数量，超过此数量会自动清理旧记录
- **示例**:
  ```yaml
  storage:
    max_history_size: 5000
  ```

### 上下文管理配置

控制会话上下文的管理。

#### `context.max_context_depth`

- **类型**: `integer`
- **默认值**: `5`
- **范围**: `1 - 50`
- **说明**: 最大上下文深度，保留最近 N 条命令作为上下文
- **示例**:
  ```yaml
  context:
    max_context_depth: 10  # 保留更多上下文
  ```

#### `context.session_timeout`

- **类型**: `integer`
- **默认值**: `3600`
- **单位**: 秒
- **说明**: 会话超时时间，超过此时间未活动的会话会被清理
- **示例**:
  ```yaml
  context:
    session_timeout: 7200  # 2小时
  ```

#### `context.enable_learning`

- **类型**: `boolean`
- **默认值**: `true`
- **说明**: 是否启用学习功能，启用后系统会从历史记录中学习
- **示例**:
  ```yaml
  context:
    enable_learning: true
  ```

## templates.yaml - 模板配置文件

### 模板定义

模板配置文件定义了可用的 PowerShell 脚本模板及其参数。

#### 模板结构

每个模板包含以下字段：

- **name**: 模板名称
- **file**: 模板文件路径
- **description**: 模板描述
- **keywords**: 关键词列表，用于匹配用户请求
- **parameters**: 参数定义
- **examples**: 使用示例

#### 文件管理类模板

##### `templates.file_management.batch_rename`

批量重命名文件模板。

**参数**:

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `SOURCE_PATH` | string | `.` | 源文件夹路径 |
| `FILE_PATTERN` | string | `*.*` | 文件匹配模式 |
| `NAME_PREFIX` | string | `file` | 文件名前缀 |
| `USE_DATE` | boolean | `false` | 是否包含日期 |
| `DATE_FORMAT` | string | `yyyyMMdd` | 日期格式 |
| `START_NUMBER` | integer | `1` | 起始序号 |
| `NUMBER_DIGITS` | integer | `3` | 序号位数 |

**示例**:
```yaml
templates:
  file_management:
    batch_rename:
      parameters:
        SOURCE_PATH: "C:\\Users\\Desktop"
        NAME_PREFIX: "photo"
        USE_DATE: true
```

##### `templates.file_management.file_organizer`

文件分类整理模板。

**参数**:

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `SOURCE_PATH` | string | `.` | 源文件夹路径 |
| `CREATE_SUBFOLDERS` | boolean | `true` | 是否创建子文件夹 |
| `MOVE_FILES` | string | `move` | 移动还是复制（move/copy） |

**示例**:
```yaml
templates:
  file_management:
    file_organizer:
      parameters:
        SOURCE_PATH: "C:\\Users\\Downloads"
        MOVE_FILES: "copy"
```

#### 系统监控类模板

##### `templates.system_monitoring.resource_monitor`

系统资源监控模板。

**参数**:

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `CPU_THRESHOLD` | integer | `80` | CPU使用率阈值（百分比） |
| `MEMORY_THRESHOLD` | integer | `85` | 内存使用率阈值（百分比） |
| `DISK_THRESHOLD` | integer | `90` | 磁盘使用率阈值（百分比） |
| `CHECK_INTERVAL` | integer | `30` | 检查间隔（秒） |
| `TOP_PROCESSES` | integer | `5` | 显示前N个进程 |
| `DURATION` | integer | `0` | 监控持续时间（秒，0表示持续监控） |

**示例**:
```yaml
templates:
  system_monitoring:
    resource_monitor:
      parameters:
        CPU_THRESHOLD: 90
        CHECK_INTERVAL: 60
```

#### 自动化任务类模板

##### `templates.automation.backup_files`

文件备份模板。

**参数**:

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `SOURCE_PATH` | string | `.` | 源文件夹路径 |
| `BACKUP_PATH` | string | `D:\\Backups` | 备份目标路径 |
| `INCLUDE_SUBFOLDERS` | boolean | `true` | 是否包含子文件夹 |
| `COMPRESS` | boolean | `true` | 是否压缩备份 |
| `KEEP_VERSIONS` | integer | `7` | 保留的备份版本数 |
| `EXCLUDE_PATTERNS` | string | `""` | 排除的文件模式（逗号分隔） |

**示例**:
```yaml
templates:
  automation:
    backup_files:
      parameters:
        SOURCE_PATH: "C:\\Projects"
        BACKUP_PATH: "D:\\Backups\\Projects"
        KEEP_VERSIONS: 14
```

##### `templates.automation.disk_cleanup`

磁盘清理模板。

**参数**:

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `CLEAN_TEMP` | boolean | `true` | 清理临时文件 |
| `CLEAN_RECYCLE_BIN` | boolean | `false` | 清空回收站 |
| `CLEAN_DOWNLOADS` | boolean | `false` | 清理下载文件夹 |
| `DAYS_OLD` | integer | `30` | 清理多少天前的文件 |
| `MIN_FILE_SIZE` | integer | `0` | 最小文件大小（MB） |

**示例**:
```yaml
templates:
  automation:
    disk_cleanup:
      parameters:
        CLEAN_TEMP: true
        DAYS_OLD: 60
```

### 模板匹配规则

#### `matching_rules.keyword_weights`

关键词权重配置。

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `exact_match` | integer | `10` | 完全匹配权重 |
| `partial_match` | integer | `5` | 部分匹配权重 |
| `category_match` | integer | `3` | 分类匹配权重 |

**示例**:
```yaml
matching_rules:
  keyword_weights:
    exact_match: 15
    partial_match: 8
```

#### `matching_rules.min_score`

- **类型**: `integer`
- **默认值**: `5`
- **说明**: 最小匹配分数，低于此分数的模板不会被推荐

#### `matching_rules.fuzzy_matching`

- **类型**: `boolean`
- **默认值**: `true`
- **说明**: 是否启用模糊匹配

### AI 生成配置

#### `ai_generation.prompt_template`

- **类型**: `string`
- **说明**: AI 生成脚本时使用的提示词模板
- **占位符**:
  - `{user_request}`: 用户需求
  - `{template_content}`: 模板内容

#### `ai_generation.temperature`

- **类型**: `float`
- **默认值**: `0.7`
- **说明**: AI 生成时的温度参数

#### `ai_generation.max_tokens`

- **类型**: `integer`
- **默认值**: `2048`
- **说明**: AI 生成的最大 token 数

#### `ai_generation.add_generation_comment`

- **类型**: `boolean`
- **默认值**: `true`
- **说明**: 是否在生成的脚本中添加生成说明注释

### 脚本保存配置

#### `script_saving.output_dir`

- **类型**: `string`
- **默认值**: `scripts/generated`
- **说明**: 生成脚本的保存目录

#### `script_saving.filename_template`

- **类型**: `string`
- **默认值**: `{template_name}_{timestamp}.ps1`
- **说明**: 文件名模板
- **占位符**:
  - `{template_name}`: 模板名称
  - `{timestamp}`: 时间戳

#### `script_saving.timestamp_format`

- **类型**: `string`
- **默认值**: `yyyyMMdd_HHmmss`
- **说明**: 时间戳格式

#### `script_saving.overwrite_existing`

- **类型**: `boolean`
- **默认值**: `false`
- **说明**: 是否覆盖已存在的文件

#### `script_saving.max_saved_scripts`

- **类型**: `integer`
- **默认值**: `100`
- **说明**: 最大保存数量，0 表示不限制

## ui.yaml - UI 配置文件

### UI 基本设置

#### `ui.colors.enabled`

- **类型**: `boolean`
- **默认值**: `true`
- **说明**: 是否启用颜色显示

#### `ui.colors.theme`

- **类型**: `string`
- **默认值**: `default`
- **可选值**: `default`, `dark`, `light`, `minimal`
- **说明**: UI 主题
- **示例**:
  ```yaml
  ui:
    colors:
      theme: dark
  ```

#### `ui.icons.enabled`

- **类型**: `boolean`
- **默认值**: `true`
- **说明**: 是否启用图标显示

#### `ui.icons.style`

- **类型**: `string`
- **默认值**: `emoji`
- **可选值**: `emoji`, `ascii`, `unicode`, `none`
- **说明**: 图标样式

#### `ui.progress.enabled`

- **类型**: `boolean`
- **默认值**: `true`
- **说明**: 是否启用进度指示器

#### `ui.progress.animations`

- **类型**: `boolean`
- **默认值**: `true`
- **说明**: 是否启用进度动画

### 交互式输入设置

#### `ui.input.auto_complete`

- **类型**: `boolean`
- **默认值**: `true`
- **说明**: 是否启用自动完成

#### `ui.input.history_enabled`

- **类型**: `boolean`
- **默认值**: `true`
- **说明**: 是否启用历史记录

#### `ui.input.history_size`

- **类型**: `integer`
- **默认值**: `1000`
- **说明**: 历史记录大小

#### `ui.input.history_file`

- **类型**: `string`
- **默认值**: `.ai_powershell_history`
- **说明**: 历史记录文件名

### 显示设置

#### `ui.display.max_width`

- **类型**: `integer`
- **默认值**: `120`
- **说明**: 最大显示宽度（字符数）

#### `ui.display.page_size`

- **类型**: `integer`
- **默认值**: `20`
- **说明**: 分页大小（每页显示的行数）

#### `ui.display.auto_pager`

- **类型**: `boolean`
- **默认值**: `true`
- **说明**: 是否自动启用分页器

#### `ui.display.show_lines`

- **类型**: `boolean`
- **默认值**: `false`
- **说明**: 表格是否显示行线

#### `ui.display.box_style`

- **类型**: `string`
- **默认值**: `rounded`
- **可选值**: `rounded`, `minimal`, `simple`
- **说明**: 边框样式

### 主题配置

系统提供四个预定义主题：`default`, `dark`, `light`, `minimal`。

每个主题定义以下颜色：

| 颜色名称 | 用途 |
|---------|------|
| `success` | 成功消息 |
| `error` | 错误消息 |
| `warning` | 警告消息 |
| `info` | 信息消息 |
| `primary` | 主要元素 |
| `secondary` | 次要元素 |
| `muted` | 弱化文本 |
| `highlight` | 高亮显示 |

**示例**:
```yaml
themes:
  custom:
    success: "bold green"
    error: "bold red"
    warning: "bold yellow"
    info: "bold blue"
```

## 配置最佳实践

### 1. 配置文件管理

**使用版本控制**
```bash
# 将配置文件加入 Git
git add config/default.yaml
git commit -m "Update configuration"
```

**创建环境特定配置**
```bash
# 开发环境
config/default.yaml

# 生产环境
config/production.yaml

# 测试环境
config/test.yaml
```

**备份配置文件**
```bash
# 定期备份配置
cp config/default.yaml config/.backups/default_$(date +%Y%m%d).yaml
```

### 2. 安全配置建议

**生产环境安全设置**
```yaml
security:
  sandbox_enabled: true          # 启用沙箱
  require_confirmation: true     # 要求确认
  whitelist_mode: strict         # 严格模式
```

**开发环境设置**
```yaml
security:
  sandbox_enabled: false         # 禁用沙箱以提高速度
  require_confirmation: false    # 快速测试
  whitelist_mode: permissive     # 宽松模式
```

### 3. 性能优化

**高性能配置**
```yaml
ai:
  cache_enabled: true
  cache_size: 500               # 更大的缓存

execution:
  timeout: 60                   # 更长的超时时间

context:
  max_context_depth: 10         # 更多上下文
```

**低资源配置**
```yaml
ai:
  cache_enabled: false          # 节省内存
  max_tokens: 128               # 减少 token 使用

storage:
  max_history_size: 100         # 减少历史记录

context:
  max_context_depth: 3          # 减少上下文
```

### 4. 日志配置建议

**详细调试**
```yaml
logging:
  level: DEBUG
  console_output: true
  file: logs/debug.log
  max_size: 50MB
```

**生产环境**
```yaml
logging:
  level: WARNING
  console_output: false
  file: logs/production.log
  max_size: 100MB
  backup_count: 10
```

### 5. 模板配置优化

**提高匹配准确度**
```yaml
matching_rules:
  keyword_weights:
    exact_match: 20             # 提高精确匹配权重
    partial_match: 8
  min_score: 10                 # 提高最小分数
  fuzzy_matching: true
```

**快速匹配**
```yaml
matching_rules:
  keyword_weights:
    exact_match: 10
    partial_match: 5
  min_score: 3                  # 降低门槛
  fuzzy_matching: false         # 禁用模糊匹配
```

## 常见配置场景

### 场景 1: 首次安装配置

```yaml
# 基本配置，适合新用户
ai:
  provider: ollama
  model_name: llama2
  temperature: 0.7

security:
  require_confirmation: true
  whitelist_mode: moderate

execution:
  timeout: 30
  auto_detect_powershell: true

logging:
  level: INFO
  console_output: true
```

### 场景 2: 企业环境配置

```yaml
# 企业级安全配置
ai:
  provider: azure
  model_name: gpt-4
  cache_enabled: true

security:
  sandbox_enabled: true
  require_confirmation: true
  whitelist_mode: strict
  dangerous_patterns:
    - Remove-Item.*-Recurse.*-Force
    - Format-Volume
    - Stop-Computer
    - Restart-Computer
    # 添加更多企业特定规则

execution:
  timeout: 60
  platform: windows

logging:
  level: WARNING
  file: logs/enterprise.log
  max_size: 100MB
  backup_count: 30

storage:
  base_path: "C:\\ProgramData\\AIAssistant"
  max_history_size: 10000
```

### 场景 3: 开发测试配置

```yaml
# 开发环境配置
ai:
  provider: local
  model_name: test-model
  temperature: 0.5

security:
  sandbox_enabled: false
  require_confirmation: false
  whitelist_mode: permissive

execution:
  timeout: 120
  encoding: utf-8

logging:
  level: DEBUG
  console_output: true
  file: logs/dev.log

context:
  max_context_depth: 20
  enable_learning: true
```

### 场景 4: 离线环境配置

```yaml
# 无网络环境配置
ai:
  provider: local
  model_name: local-model
  use_ai_provider: false        # 只使用规则匹配
  cache_enabled: true

security:
  require_confirmation: true
  whitelist_mode: strict

storage:
  base_path: ~/ai-assistant-offline
```

### 场景 5: 高性能服务器配置

```yaml
# 服务器环境配置
ai:
  provider: ollama
  model_name: qwen3:30b
  temperature: 0.7
  max_tokens: 1024
  cache_enabled: true
  cache_size: 1000

execution:
  timeout: 300
  platform: linux

logging:
  level: INFO
  file: /var/log/ai-assistant/app.log
  max_size: 500MB
  backup_count: 20

storage:
  base_path: /opt/ai-assistant/data
  max_history_size: 50000

context:
  max_context_depth: 30
  session_timeout: 7200
```

### 场景 6: 自定义 UI 配置

```yaml
# 自定义界面配置
ui:
  colors:
    enabled: true
    theme: dark
  
  icons:
    enabled: true
    style: unicode
  
  progress:
    enabled: true
    animations: true
  
  input:
    auto_complete: true
    history_enabled: true
    history_size: 5000
  
  display:
    max_width: 150
    page_size: 30
    auto_pager: true
    show_lines: true
    box_style: rounded
```

## 配置验证

### 使用 Python API 验证配置

```python
from src.config import ConfigManager

# 创建配置管理器
manager = ConfigManager()

# 验证配置文件
config_data = {
    "ai": {
        "provider": "ollama",
        "temperature": 0.7
    }
}

is_valid, error = manager.validate_config(config_data)
if is_valid:
    print("✓ 配置有效")
else:
    print(f"✗ 配置无效: {error}")
```

### 常见验证错误

**1. 值超出范围**
```yaml
# 错误
ai:
  temperature: 3.0  # 超出范围 (0.0-2.0)

# 正确
ai:
  temperature: 1.5
```

**2. 无效的枚举值**
```yaml
# 错误
security:
  whitelist_mode: invalid  # 无效值

# 正确
security:
  whitelist_mode: moderate
```

**3. 类型错误**
```yaml
# 错误
execution:
  timeout: "30"  # 应该是整数

# 正确
execution:
  timeout: 30
```

**4. 缺少必需字段**
```yaml
# 错误
ai:
  # 缺少 provider 字段

# 正确
ai:
  provider: ollama
  model_name: llama2
```

## 故障排除

### 配置文件未找到

**问题**: 系统提示找不到配置文件

**解决方案**:
1. 检查配置文件是否存在于以下位置之一：
   - `config/default.yaml`
   - `config.yaml`
   - `~/.ai-powershell/config.yaml`

2. 创建默认配置文件：
   ```python
   from src.config import ConfigManager
   ConfigManager.create_default_config_file("config/default.yaml")
   ```

### YAML 解析错误

**问题**: 配置文件格式错误

**解决方案**:
1. 检查 YAML 语法：
   - 确保缩进使用空格（不是 Tab）
   - 确保冒号后有空格
   - 确保字符串正确引用

2. 使用在线 YAML 验证器检查语法

3. 查看错误消息中的行号和列号

### 配置值不生效

**问题**: 修改配置后没有效果

**解决方案**:
1. 重启应用程序
2. 检查是否修改了正确的配置文件
3. 验证配置值的类型和范围
4. 检查日志文件中的错误信息

### 权限问题

**问题**: 无法写入配置文件

**解决方案**:
1. 检查文件权限：
   ```bash
   ls -l config/default.yaml
   ```

2. 修改权限：
   ```bash
   chmod 644 config/default.yaml
   ```

3. 使用用户目录配置：
   ```yaml
   storage:
     base_path: ~/.ai-powershell
   ```

### AI 模型连接失败

**问题**: 无法连接到 AI 提供商

**解决方案**:
1. 检查 Ollama 服务是否运行：
   ```bash
   curl http://localhost:11434/api/tags
   ```

2. 验证模型名称：
   ```bash
   ollama list
   ```

3. 检查网络连接和防火墙设置

4. 尝试使用本地模式：
   ```yaml
   ai:
     use_ai_provider: false
   ```

## 相关文档

- [用户指南](user-guide.md) - 了解如何使用系统
- [开发者指南](developer-guide.md) - 了解如何扩展配置
- [部署指南](deployment-guide.md) - 了解生产环境配置
- [故障排除指南](troubleshooting.md) - 解决常见问题

## 下一步

- 查看 [API 参考](api-reference.md) 了解如何通过代码管理配置
- 查看 [CLI 参考](cli-reference.md) 了解配置相关命令
- 查看 [模板指南](template-guide.md) 了解如何自定义模板

---

**需要帮助?** 查看 [故障排除指南](troubleshooting.md) 或 [提交 Issue](https://github.com/your-repo/issues)
