<!-- 文档类型: 贡献指南 | 最后更新: 2025-01-17 | 维护者: 项目团队 -->

# 文档贡献指南

> **文档类型**: 贡献指南 | **最后更新**: 2025-01-17 | **维护者**: 项目团队

📍 [首页](../README.md) > [文档中心](README.md) > 文档贡献指南

## 📋 目录

- [简介](#简介)
- [文档编写规范](#文档编写规范)
- [文档风格指南](#文档风格指南)
- [文档模板](#文档模板)
- [文档提交流程](#文档提交流程)
- [文档审查标准](#文档审查标准)
- [文档维护最佳实践](#文档维护最佳实践)
- [常见问题](#常见问题)

---

## 简介

欢迎为 AI PowerShell 智能助手项目贡献文档！良好的文档是项目成功的关键。本指南将帮助您了解如何编写、提交和维护高质量的文档。

### 为什么文档很重要

- **降低学习曲线**: 帮助新用户快速上手
- **提高开发效率**: 为开发者提供清晰的技术参考
- **减少支持成本**: 减少重复性问题
- **促进协作**: 统一团队对系统的理解

### 文档类型

本项目包含以下类型的文档：

1. **用户指南**: 面向最终用户，介绍功能使用
2. **开发者文档**: 面向开发者，说明技术实现
3. **API 参考**: 详细的接口文档和代码示例
4. **配置参考**: 系统配置选项说明
5. **部署指南**: 安装、部署和运维说明
6. **故障排除**: 常见问题和解决方案

---

## 文档编写规范

### 文件命名

- 使用小写字母和连字符: `user-guide.md`, `api-reference.md`
- 使用描述性名称: `deployment-guide.md` 而不是 `guide.md`
- 避免使用空格和特殊字符

### 文档结构

每个文档应包含以下部分：


```markdown
<!-- 文档元数据 -->
<!-- 文档类型: [类型] | 最后更新: [日期] | 维护者: [维护者] -->

# 文档标题

> **文档类型**: [类型] | **最后更新**: [日期] | **维护者**: [维护者]

📍 [首页](../README.md) > [文档中心](README.md) > [当前位置]

## 📋 目录

[自动生成或手动维护的目录]

---

## 简介

[1-2 段简短介绍，说明文档目的和内容概述]

## 主要内容

[文档的核心内容，使用清晰的章节结构]

## 相关文档

- [相关文档1](link) - 简短描述
- [相关文档2](link) - 简短描述

## 下一步

- 📖 [推荐阅读1](link)
- 🔧 [推荐阅读2](link)

---

**需要帮助?** 查看 [故障排除指南](troubleshooting.md) 或 [提交 Issue](https://github.com/0green7hand0/AI-PowerShell/issues)
```

### 标题层级

使用清晰的标题层级结构：

- **H1 (`#`)**: 文档标题（每个文档只有一个）
- **H2 (`##`)**: 主要章节
- **H3 (`###`)**: 子章节
- **H4 (`####`)**: 更细的分类（谨慎使用）

**示例**:
```markdown
# 用户指南

## 快速开始

### 安装步骤

#### Windows 系统

#### Linux 系统
```

### 段落和换行

- 段落之间使用空行分隔
- 避免过长的段落（建议不超过 5-7 行）
- 使用列表来组织多个要点
- 重要内容可以单独成段

### 列表格式

**无序列表**:
```markdown
- 第一项
- 第二项
  - 子项 1
  - 子项 2
- 第三项
```

**有序列表**:
```markdown
1. 第一步
2. 第二步
3. 第三步
```

**任务列表**:
```markdown
- [x] 已完成的任务
- [ ] 待完成的任务
```

### 代码块

始终为代码块指定语言标识符：

````markdown
```python
# Python 代码示例
from src.main import PowerShellAssistant

assistant = PowerShellAssistant()
result = assistant.process_request("显示当前时间")
```

```bash
# Bash 命令示例
python run.py --help
```

```yaml
# YAML 配置示例
ai:
  provider: ollama
  model_name: llama3
```

```powershell
# PowerShell 脚本示例
Get-Date -Format "yyyy-MM-dd HH:mm:ss"
```
````

### 内联代码

使用反引号标记内联代码、文件名、命令等：

```markdown
使用 `ConfigManager` 类来加载配置文件 `config/default.yaml`。
运行 `python run.py` 命令启动程序。
```

### 链接

**内部链接**（相对路径）:
```markdown
查看 [用户指南](user-guide.md) 了解更多信息。
参考 [API 文档](api-reference.md#configmanager) 中的 ConfigManager 部分。
```

**外部链接**:
```markdown
访问 [Python 官方文档](https://docs.python.org/) 了解更多。
```

**锚点链接**:
```markdown
跳转到 [配置章节](#配置管理)
```

### 表格

使用 Markdown 表格展示结构化数据：

```markdown
| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| provider | string | "local" | AI 提供商 |
| temperature | float | 0.7 | 生成温度 |
| max_tokens | int | 256 | 最大令牌数 |
```

### 引用块

使用引用块突出显示重要信息：

```markdown
> **注意**: 这是一条重要提示信息。

> **警告**: 此操作可能导致数据丢失。

> **提示**: 建议先备份数据再进行操作。
```

### 图片

```markdown
![图片描述](images/screenshot.png)

<!-- 带链接的图片 -->
[![图片描述](images/logo.png)](https://example.com)
```

---

## 文档风格指南

### 语言风格

#### 1. 使用清晰简洁的语言

**❌ 不好**:
```
本系统提供了一个非常强大且功能丰富的配置管理机制，
它能够让用户以一种极其灵活的方式来定制和调整各种各样的系统参数。
```

**✅ 好**:
```
配置管理系统支持灵活的参数定制。
```

#### 2. 使用主动语态

**❌ 不好**:
```
配置文件被系统加载后，参数会被验证。
```

**✅ 好**:
```
系统加载配置文件后验证参数。
```

#### 3. 使用第二人称

**❌ 不好**:
```
用户应该首先安装依赖包。
```

**✅ 好**:
```
首先安装依赖包。
或
您需要首先安装依赖包。
```

#### 4. 保持一致性

- 术语使用一致（如统一使用"配置文件"而不是混用"配置文件"和"config 文件"）
- 格式一致（如代码示例的缩进、注释风格）
- 结构一致（如所有 API 文档使用相同的格式）

### 技术术语

#### 中英文混排

- 专有名词保持英文: `PowerShell`, `Python`, `Docker`
- 技术术语首次出现时提供中英文对照: "配置管理器 (ConfigManager)"
- 代码相关内容使用英文: `class`, `function`, `variable`

#### 术语表

在文档开头或专门章节定义关键术语：

```markdown
## 术语表

- **AI 引擎 (AI Engine)**: 负责将自然语言翻译为 PowerShell 命令的模块
- **安全引擎 (Security Engine)**: 负责验证命令安全性的模块
- **上下文管理器 (Context Manager)**: 管理用户会话和命令历史的模块
```

### 格式增强

#### 使用 Emoji 图标

适度使用 emoji 提高可读性：

- 📖 文档/阅读
- 🔧 配置/工具
- ⚠️ 警告
- ✅ 成功/正确
- ❌ 失败/错误
- 💡 提示/建议
- 🚀 快速开始
- 🐛 Bug/问题
- 📝 示例
- 🔒 安全

**示例**:
```markdown
## 🚀 快速开始

### ✅ 正确做法

### ❌ 错误做法

> 💡 **提示**: 建议使用虚拟环境。

> ⚠️ **警告**: 此操作不可逆。
```

#### 使用标注块

```markdown
> **注意**: 普通提示信息

> **重要**: 重要信息

> **警告**: 警告信息

> **危险**: 危险操作警告
```

#### 使用分隔线

使用 `---` 分隔不同的主要部分：

```markdown
## 第一部分

内容...

---

## 第二部分

内容...
```

### 代码示例规范

#### 1. 提供完整可运行的示例

**❌ 不好**:
```python
config = get_config()
```

**✅ 好**:
```python
from src.config import ConfigManager

# 创建配置管理器
manager = ConfigManager()

# 加载配置
config = manager.get_config()

# 访问配置项
print(f"AI Provider: {config.ai.provider}")
```

#### 2. 添加注释说明

```python
# 初始化 AI 引擎
ai_engine = AIEngine(config)

# 翻译自然语言为命令
suggestion = ai_engine.translate_natural_language(
    "显示当前时间",  # 用户输入
    context          # 上下文信息
)

# 输出结果
print(f"生成的命令: {suggestion.generated_command}")
```

#### 3. 展示预期输出

```python
# 示例代码
result = assistant.process_request("显示当前时间")
print(result.command)

# 输出:
# Get-Date -Format "yyyy-MM-dd HH:mm:ss"
```

#### 4. 包含错误处理

```python
try:
    result = assistant.process_request(user_input)
    if result.success:
        print(f"执行成功: {result.output}")
    else:
        print(f"执行失败: {result.error}")
except Exception as e:
    print(f"发生错误: {e}")
```

---

## 文档模板

### 用户指南模板


```markdown
<!-- 文档类型: 用户指南 | 最后更新: YYYY-MM-DD | 维护者: 项目团队 -->

# [功能名称] 用户指南

> **文档类型**: 用户指南 | **最后更新**: YYYY-MM-DD | **维护者**: 项目团队

📍 [首页](../README.md) > [文档中心](README.md) > [功能名称]用户指南

## 📋 目录

- [简介](#简介)
- [快速开始](#快速开始)
- [基本使用](#基本使用)
- [高级功能](#高级功能)
- [配置选项](#配置选项)
- [最佳实践](#最佳实践)
- [故障排除](#故障排除)

---

## 简介

[1-2 段介绍功能的目的、主要特性和适用场景]

### 主要特性

- 特性 1
- 特性 2
- 特性 3

---

## 快速开始

### 前置要求

- 要求 1
- 要求 2

### 基本示例

```python
# 最简单的使用示例
from src.module import Feature

feature = Feature()
result = feature.do_something()
```

---

## 基本使用

### 功能 1

[详细说明]

```python
# 代码示例
```

### 功能 2

[详细说明]

```python
# 代码示例
```

---

## 高级功能

### 高级功能 1

[详细说明和示例]

### 高级功能 2

[详细说明和示例]

---

## 配置选项

| 选项名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| option1 | string | "default" | 选项说明 |
| option2 | int | 10 | 选项说明 |

---

## 最佳实践

1. **实践 1**: 说明
2. **实践 2**: 说明
3. **实践 3**: 说明

---

## 故障排除

### 问题 1

**症状**: 问题描述

**原因**: 原因分析

**解决方案**:
1. 步骤 1
2. 步骤 2

---

## 相关文档

- [相关文档1](link) - 简短描述
- [相关文档2](link) - 简短描述

## 下一步

- 📖 [推荐阅读1](link)
- 🔧 [推荐阅读2](link)

---

**需要帮助?** 查看 [故障排除指南](troubleshooting.md) 或 [提交 Issue](https://github.com/0green7hand0/AI-PowerShell/issues)
```

### API 参考模板

```markdown
<!-- 文档类型: API 参考 | 最后更新: YYYY-MM-DD | 维护者: 项目团队 -->

# [模块名称] API 参考

> **文档类型**: API 参考 | **最后更新**: YYYY-MM-DD | **维护者**: 项目团队

📍 [首页](../README.md) > [文档中心](README.md) > [模块名称] API 参考

## 📋 目录

- [概述](#概述)
- [类](#类)
- [函数](#函数)
- [常量](#常量)
- [异常](#异常)

---

## 概述

[模块的简短描述和用途]

---

## 类

### ClassName

[类的描述]

**继承**: `BaseClass`

**参数**:
- `param1` (type): 参数说明
- `param2` (type, optional): 参数说明，默认值为 `default`

**属性**:
- `attribute1` (type): 属性说明
- `attribute2` (type): 属性说明

**方法**:

#### `method_name(param1, param2)`

[方法描述]

**参数**:
- `param1` (type): 参数说明
- `param2` (type, optional): 参数说明，默认值为 `default`

**返回值**:
- `return_type`: 返回值说明

**异常**:
- `ValueError`: 异常说明
- `RuntimeError`: 异常说明

**示例**:
```python
# 使用示例
instance = ClassName(param1="value")
result = instance.method_name("arg1", "arg2")
print(result)
```

---

## 函数

### `function_name(param1, param2)`

[函数描述]

**参数**:
- `param1` (type): 参数说明
- `param2` (type, optional): 参数说明，默认值为 `default`

**返回值**:
- `return_type`: 返回值说明

**异常**:
- `ValueError`: 异常说明

**示例**:
```python
result = function_name("value1", "value2")
```

---

## 常量

### `CONSTANT_NAME`

**类型**: `type`

**值**: `value`

**说明**: 常量说明

---

## 异常

### `CustomException`

**继承**: `Exception`

**说明**: 异常说明

**使用场景**: 何时抛出此异常

---

## 相关文档

- [用户指南](user-guide.md) - 功能使用说明
- [开发者指南](developer-guide.md) - 开发和扩展

---

**需要帮助?** 查看 [故障排除指南](troubleshooting.md) 或 [提交 Issue](https://github.com/0green7hand0/AI-PowerShell/issues)
```

### 配置参考模板

```markdown
<!-- 文档类型: 配置参考 | 最后更新: YYYY-MM-DD | 维护者: 项目团队 -->

# [配置文件名] 配置参考

> **文档类型**: 配置参考 | **最后更新**: YYYY-MM-DD | **维护者**: 项目团队

📍 [首页](../README.md) > [文档中心](README.md) > [配置文件名]配置参考

## 📋 目录

- [概述](#概述)
- [配置文件位置](#配置文件位置)
- [配置项](#配置项)
- [配置示例](#配置示例)
- [最佳实践](#最佳实践)

---

## 概述

[配置文件的用途和作用范围]

---

## 配置文件位置

1. `config/default.yaml` - 默认配置
2. `config.yaml` - 项目配置（覆盖默认配置）
3. `~/.ai-powershell/config.yaml` - 用户配置（优先级最高）

---

## 配置项

### 配置组 1

#### `config.option1`

**类型**: `string`

**默认值**: `"default_value"`

**说明**: 配置项的详细说明

**可选值**:
- `value1`: 值说明
- `value2`: 值说明

**示例**:
```yaml
config:
  option1: "custom_value"
```

#### `config.option2`

**类型**: `int`

**默认值**: `10`

**范围**: `1-100`

**说明**: 配置项的详细说明

**示例**:
```yaml
config:
  option2: 20
```

---

## 配置示例

### 基本配置

```yaml
# 基本配置示例
config:
  option1: "value1"
  option2: 10
```

### 高级配置

```yaml
# 高级配置示例
config:
  option1: "value1"
  option2: 20
  advanced:
    feature1: true
    feature2: false
```

---

## 最佳实践

1. **不要修改默认配置**: 在 `config.yaml` 中覆盖需要的配置项
2. **使用环境变量**: 敏感信息使用环境变量
3. **验证配置**: 修改后运行系统检查验证配置

---

## 相关文档

- [用户指南](user-guide.md) - 功能使用说明
- [部署指南](deployment-guide.md) - 部署和配置

---

**需要帮助?** 查看 [故障排除指南](troubleshooting.md) 或 [提交 Issue](https://github.com/0green7hand0/AI-PowerShell/issues)
```

---

## 文档提交流程

### 1. 准备工作

#### Fork 项目

在 GitHub 上 Fork 项目到您的账号。

#### 克隆仓库

```bash
git clone https://github.com/YOUR_USERNAME/AI-PowerShell.git
cd AI-PowerShell
```

#### 创建分支

```bash
# 创建文档分支
git checkout -b docs/your-doc-name

# 分支命名规范:
# docs/add-feature-guide - 添加新文档
# docs/update-api-ref - 更新现有文档
# docs/fix-typo - 修复错误
```

### 2. 编写文档

#### 选择合适的位置

- 用户文档: `docs/`
- 开发者文档: `docs/`
- 示例代码: `examples/`
- 配置示例: `config/`

#### 使用模板

根据文档类型选择合适的模板（见上文）。

#### 遵循规范

- 遵循文档编写规范
- 遵循风格指南
- 添加代码示例
- 包含相关链接

### 3. 本地预览

#### 检查 Markdown 格式

使用 Markdown 编辑器或预览工具检查格式：

- VS Code: Markdown Preview
- Typora
- 在线工具: https://dillinger.io/

#### 检查链接

确保所有内部链接正确：

```bash
# 使用项目提供的链接检查脚本
python scripts/verify_links.py
```

### 4. 提交更改

#### 添加文件

```bash
git add docs/your-new-doc.md
```

#### 提交

```bash
git commit -m "Docs: 添加 [功能名称] 用户指南"

# 提交信息格式:
# Docs: 添加 XXX 文档
# Docs: 更新 XXX 文档
# Docs: 修复 XXX 文档中的错误
# Docs: 改进 XXX 文档的示例
```

#### 推送

```bash
git push origin docs/your-doc-name
```

### 5. 创建 Pull Request

#### 在 GitHub 上创建 PR

1. 访问您的 Fork 仓库
2. 点击 "Pull Request"
3. 选择您的分支
4. 填写 PR 描述

#### PR 描述模板

```markdown
## 变更类型
- [ ] 新增文档
- [ ] 更新文档
- [ ] 修复错误
- [ ] 改进示例

## 变更说明

简要描述您的文档变更...

## 检查清单

- [ ] 遵循文档编写规范
- [ ] 遵循风格指南
- [ ] 代码示例可运行
- [ ] 链接检查通过
- [ ] 拼写检查通过
- [ ] 添加到文档索引

## 相关 Issue

Closes #123 (如果有相关 Issue)
```

### 6. 响应审查

#### 及时响应

- 查看审查意见
- 回答问题
- 进行必要的修改

#### 更新 PR

```bash
# 修改文档
git add docs/your-new-doc.md
git commit -m "Docs: 根据审查意见更新文档"
git push origin docs/your-doc-name
```

### 7. 合并

审查通过后，维护者会合并您的 PR。

---

## 文档审查标准

### 内容质量

- [ ] **准确性**: 信息准确无误
- [ ] **完整性**: 涵盖所有必要内容
- [ ] **清晰性**: 表达清晰易懂
- [ ] **相关性**: 内容与主题相关
- [ ] **时效性**: 信息是最新的

### 格式规范

- [ ] **标题层级**: 使用正确的标题层级
- [ ] **代码块**: 所有代码块有语言标识符
- [ ] **链接**: 所有链接有效
- [ ] **列表**: 列表格式正确
- [ ] **表格**: 表格对齐美观

### 代码示例

- [ ] **可运行**: 代码示例可以直接运行
- [ ] **完整**: 包含必要的导入和初始化
- [ ] **注释**: 有适当的注释说明
- [ ] **输出**: 展示预期输出
- [ ] **错误处理**: 包含错误处理示例

### 结构组织

- [ ] **目录**: 长文档有目录
- [ ] **章节**: 章节划分合理
- [ ] **导航**: 有面包屑导航
- [ ] **相关文档**: 链接到相关文档
- [ ] **下一步**: 提供后续阅读建议

### 语言风格

- [ ] **简洁**: 语言简洁明了
- [ ] **主动**: 使用主动语态
- [ ] **一致**: 术语使用一致
- [ ] **友好**: 语气友好专业
- [ ] **无错**: 无拼写和语法错误

---

## 文档维护最佳实践

### 定期更新

#### 跟踪代码变更

- 代码重大变更时更新相关文档
- 新功能发布时添加文档
- API 变更时更新 API 参考

#### 设置提醒

- 每季度审查文档时效性
- 检查是否有过时信息
- 更新版本号和日期

### 收集反馈

#### 用户反馈

- 关注 GitHub Issues 中的文档问题
- 收集用户使用反馈
- 改进不清楚的部分

#### 团队反馈

- 定期团队文档审查
- 讨论文档改进建议
- 分享最佳实践

### 保持一致性

#### 使用模板

- 新文档使用标准模板
- 保持格式一致
- 统一术语使用

#### 交叉引用

- 添加相关文档链接
- 避免内容重复
- 保持信息同步

### 版本管理

#### 文档版本

- 在文档元数据中记录更新日期
- 重大变更记录在 CHANGELOG
- 保留历史版本（如需要）

#### 弃用说明

```markdown
> **已弃用**: 此功能已在 v2.0 中弃用，请使用 [新功能](link) 替代。
```

### 可访问性

#### 清晰的语言

- 避免行话和缩写
- 解释技术术语
- 提供示例说明

#### 多种格式

- 文字说明
- 代码示例
- 图表（如适用）
- 视频教程（如适用）

---

## 常见问题

### Q: 我应该在哪里添加新文档？

A: 根据文档类型选择位置：
- 用户指南: `docs/user-guide.md` 或新建独立文档
- API 参考: `docs/api-reference.md`
- 配置说明: `docs/config-reference.md`
- 故障排除: `docs/troubleshooting.md`

如果是全新的主题，可以创建新文档并添加到 `docs/README.md` 索引中。

### Q: 如何处理中英文混排？

A: 遵循以下原则：
- 专有名词保持英文: `PowerShell`, `Python`, `Docker`
- 技术术语首次出现提供对照: "配置管理器 (ConfigManager)"
- 代码相关保持英文: `class`, `function`, `variable`
- 中英文之间添加空格: "使用 `ConfigManager` 类"

### Q: 代码示例应该多详细？

A: 代码示例应该：
- 完整可运行（包含必要的导入）
- 有适当的注释
- 展示实际用例
- 包含错误处理
- 显示预期输出

避免过于简化或过于复杂的示例。

### Q: 如何确保链接不会失效？

A: 
- 使用相对路径而不是绝对路径
- 定期运行链接检查脚本
- 文档重构时更新所有相关链接
- 在 PR 中检查链接有效性

### Q: 文档应该多长？

A: 没有固定长度，但建议：
- 简短文档: 1000-2000 字
- 中等文档: 2000-5000 字
- 长文档: 5000+ 字（需要详细目录）

如果文档过长，考虑拆分成多个文档。

### Q: 如何处理敏感信息？

A: 
- 不要在文档中包含真实的密钥、密码
- 使用占位符: `YOUR_API_KEY`, `your-password`
- 提供获取凭证的说明
- 建议使用环境变量

### Q: 文档审查需要多长时间？

A: 通常 1-3 个工作日，取决于：
- 文档的长度和复杂度
- 维护者的可用时间
- 是否需要多轮审查

### Q: 我可以直接修改别人的文档吗？

A: 可以，但建议：
- 小改动（错别字、格式）: 直接提 PR
- 大改动（重写章节）: 先开 Issue 讨论
- 尊重原作者的工作
- 在 PR 中说明改动原因

---

## 相关文档

- [用户指南](user-guide.md) - 了解系统功能
- [开发者指南](developer-guide.md) - 参与代码开发
- [API 参考](api-reference.md) - 查看 API 文档
- [故障排除指南](troubleshooting.md) - 解决常见问题

## 下一步

- 📖 阅读 [文档中心](README.md) 了解现有文档
- 🔧 查看 [开发者指南](developer-guide.md) 了解项目结构
- 💻 访问 [GitHub 仓库](https://github.com/0green7hand0/AI-PowerShell) 开始贡献

---

**需要帮助?** 查看 [故障排除指南](troubleshooting.md) 或 [提交 Issue](https://github.com/0green7hand0/AI-PowerShell/issues)

**感谢您的贡献！** 🎉
