# 自定义模板快速入门

## 5分钟快速开始

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

---

## 常用命令速查

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

---

## 参数类型速查

### String (字符串)
```powershell
[string]$Name = "{{NAME}}"
```
用于：文本、名称、描述

### Integer (整数)
```powershell
[int]$Count = {{COUNT}}
```
用于：数量、大小、时间（秒）

### Boolean (布尔值)
```powershell
[bool]$Enable = ${{ENABLE}}
```
用于：开关、标志、是否选项

### Path (路径)
```powershell
[string]$Path = "{{PATH}}"
```
用于：文件路径、目录路径

---

## 3个实用模板示例

### 示例1: 快速备份
```powershell
param(
    [string]$Source = "{{SOURCE}}",
    [string]$Dest = "{{DEST}}"
)
Copy-Item -Path $Source -Destination $Dest -Recurse -Force
Write-Host "✓ 备份完成" -ForegroundColor Green
```

### 示例2: 清理临时文件
```powershell
param(
    [string]$Path = "{{PATH}}",
    [int]$Days = {{DAYS}}
)
$cutoff = (Get-Date).AddDays(-$Days)
Get-ChildItem $Path | Where-Object { $_.LastWriteTime -lt $cutoff } | Remove-Item -Force
Write-Host "✓ 清理完成" -ForegroundColor Green
```

### 示例3: 系统信息
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

## 最佳实践 Top 5

1. **使用描述性名称**: `database_backup` 而不是 `db_bak`
2. **添加详细注释**: 帮助他人（和未来的你）理解模板
3. **提供合理默认值**: 让模板开箱即用
4. **验证输入参数**: 使用 `Test-Path` 等检查有效性
5. **友好的输出**: 使用颜色和图标让输出更清晰

---

## 需要帮助？

- 📖 [完整用户指南](custom-template-guide.md)
- 📋 [模板列表](../templates/README.md)
- 💡 [示例模板](../templates/custom/examples/)
- 🔧 [CLI 参考](template-cli-reference.md)

---

**提示**: 从简单开始，逐步添加功能。每个伟大的模板都是从一个简单的脚本开始的！ 🚀
