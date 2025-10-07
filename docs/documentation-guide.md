# 📚 文档编写指南

本指南说明如何为 AI PowerShell 智能助手项目编写和维护文档。

## 📋 文档结构

### 根目录文档
- **README.md** - 项目主文档（英文）
- **中文项目说明.md** - 完整中文说明
- **快速开始.md** - 快速上手指南
- **DOCUMENTATION.md** - 完整文档索引
- **CHANGELOG.md** - 版本更新日志
- **RELEASE_NOTES.md** - 发布说明
- **LICENSE** - MIT 许可证

### docs/ 目录
- **README.md** - 文档中心导航
- **用户文档** - 面向最终用户
- **开发者文档** - 面向开发者
- **部署文档** - 面向运维人员

## ✍️ 文档编写规范

### 1. 文件命名

使用小写字母和连字符：
```
✅ good-example.md
✅ user-guide.md
❌ BadExample.md
❌ user_guide.md
```

中文文档可以使用中文名：
```
✅ 快速开始.md
✅ 中文项目说明.md
```

### 2. 文档结构

每个文档应包含：

```markdown
# 文档标题

简短的文档描述（1-2句话）

## 目录（可选，长文档需要）

## 主要内容

### 二级标题

内容...

### 另一个二级标题

内容...

## 相关文档

- [相关文档1](link1.md)
- [相关文档2](link2.md)

## 获取帮助

- 问题反馈
- 讨论链接
```

### 3. 标题层级

- H1 (#) - 文档标题，每个文档只有一个
- H2 (##) - 主要章节
- H3 (###) - 子章节
- H4 (####) - 详细说明
- 不要使用 H5 和 H6

### 4. 代码块

使用语言标识：

````markdown
```bash
# Bash 命令
python src/main.py
```

```python
# Python 代码
from src.main import PowerShellAssistant
```

```yaml
# YAML 配置
ai:
  provider: ollama
```

```powershell
# PowerShell 命令
Get-Process | Sort-Object CPU
```
````

### 5. 链接

使用相对路径：

```markdown
✅ [快速开始](../快速开始.md)
✅ [架构文档](architecture.md)
❌ [文档](https://github.com/.../docs/file.md)
```

### 6. 图片

图片放在 `docs/images/` 目录：

```markdown
![架构图](images/architecture.png)
```

### 7. 表格

使用 Markdown 表格：

```markdown
| 列1 | 列2 | 列3 |
|-----|-----|-----|
| 值1 | 值2 | 值3 |
```

### 8. 列表

有序列表用于步骤：

```markdown
1. 第一步
2. 第二步
3. 第三步
```

无序列表用于要点：

```markdown
- 要点1
- 要点2
- 要点3
```

### 9. 强调

```markdown
**粗体** - 重要内容
*斜体* - 强调
`代码` - 命令或代码
```

### 10. 提示框

使用 emoji 和引用：

```markdown
💡 **提示：** 这是一个有用的提示

⚠️ **警告：** 这是一个警告

❌ **错误：** 这是一个错误示例

✅ **成功：** 这是一个成功示例
```

## 📝 文档类型

### 用户文档

**目标读者：** 最终用户

**内容要求：**
- 简单易懂
- 提供实际示例
- 避免技术术语
- 包含截图或示例输出

**示例：**
- 快速开始.md
- template-quick-start.md
- security-checker-guide.md

### 开发者文档

**目标读者：** 开发者和贡献者

**内容要求：**
- 技术细节
- 代码示例
- API 说明
- 架构图

**示例：**
- architecture.md
- developer-guide.md
- api-reference.md

### 部署文档

**目标读者：** 运维人员

**内容要求：**
- 部署步骤
- 配置说明
- 故障排除
- 最佳实践

**示例：**
- docker-deployment.md
- ci-cd-setup.md
- release-process.md

## 🔄 文档维护

### 更新频率

- **README.md** - 每次重大更新
- **CHANGELOG.md** - 每次发布
- **快速开始.md** - 功能变更时
- **API 文档** - 接口变更时
- **配置文档** - 配置变更时

### 版本控制

在文档中标注版本：

```markdown
> 本文档适用于 v2.0.0 及以上版本
```

### 废弃说明

标注废弃内容：

```markdown
> ⚠️ **已废弃：** 此功能在 v2.0.0 中已废弃，请使用 [新功能](new-feature.md)
```

## ✅ 文档检查清单

提交文档前检查：

- [ ] 标题清晰准确
- [ ] 内容完整无误
- [ ] 代码示例可运行
- [ ] 链接正确有效
- [ ] 格式规范统一
- [ ] 拼写检查通过
- [ ] 相关文档已更新
- [ ] 添加到文档索引

## 🎯 最佳实践

### 1. 保持简洁

```markdown
❌ 不好：
这个功能是一个非常强大的功能，它可以帮助你做很多事情，
包括但不限于创建、编辑、删除等各种操作...

✅ 好：
此功能支持创建、编辑和删除操作。
```

### 2. 使用示例

```markdown
❌ 不好：
使用 template create 命令创建模板。

✅ 好：
创建模板：
\`\`\`bash
python src/main.py template create
\`\`\`
```

### 3. 提供上下文

```markdown
❌ 不好：
运行命令。

✅ 好：
在项目根目录运行以下命令：
\`\`\`bash
python src/main.py --version
\`\`\`
```

### 4. 解释原因

```markdown
❌ 不好：
设置 temperature 为 0.7。

✅ 好：
设置 temperature 为 0.7 以平衡创造性和准确性：
- 较低值（0.1-0.5）：更确定性的输出
- 较高值（0.8-1.0）：更有创造性的输出
```

### 5. 提供替代方案

```markdown
如果方法A不起作用，可以尝试方法B：
\`\`\`bash
# 方法A
command-a

# 方法B（如果A失败）
command-b
\`\`\`
```

## 📊 文档模板

### 功能文档模板

```markdown
# 功能名称

功能简短描述。

## 概述

详细说明功能的作用和用途。

## 使用方法

### 基本用法

\`\`\`bash
# 示例命令
\`\`\`

### 高级用法

\`\`\`bash
# 高级示例
\`\`\`

## 配置

\`\`\`yaml
# 配置示例
\`\`\`

## 示例

### 示例1：场景描述

\`\`\`bash
# 示例代码
\`\`\`

## 故障排除

### 问题1

**症状：** 问题描述

**解决方案：** 解决步骤

## 相关文档

- [相关文档1](link1.md)
- [相关文档2](link2.md)
```

### API 文档模板

```markdown
# API 名称

API 简短描述。

## 语法

\`\`\`python
function_name(param1, param2)
\`\`\`

## 参数

- **param1** (type): 参数描述
- **param2** (type): 参数描述

## 返回值

返回值类型和描述。

## 示例

\`\`\`python
# 示例代码
result = function_name("value1", "value2")
\`\`\`

## 异常

- **ExceptionType**: 异常描述

## 相关

- [相关API](related-api.md)
```

## 🔍 文档审查

提交前自我审查：

1. **准确性** - 信息是否正确？
2. **完整性** - 是否遗漏重要信息？
3. **清晰性** - 是否易于理解？
4. **一致性** - 格式是否统一？
5. **可用性** - 示例是否可运行？

## 📞 获取帮助

文档相关问题：
- 查看现有文档作为参考
- 提交 Issue 讨论
- 在 PR 中请求审查

## 🎓 学习资源

- [Markdown 指南](https://www.markdownguide.org/)
- [技术写作最佳实践](https://developers.google.com/tech-writing)
- [文档即代码](https://www.writethedocs.org/guide/docs-as-code/)
