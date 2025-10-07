# 模板管理快速参考卡

## 常用命令速查

### 创建模板
```bash
python src/main.py template create
```

### 列出模板
```bash
# 所有模板
python src/main.py template list

# 仅自定义模板
python src/main.py template list --custom-only
```

### 查看详情
```bash
python src/main.py template info <template_name>
```

### 编辑模板
```bash
python src/main.py template edit <template_name>
```

### 删除模板
```bash
python src/main.py template delete <template_name>
```

### 导出/导入
```bash
# 导出
python src/main.py template export <template_name> -o file.zip

# 导入
python src/main.py template import file.zip
```

### 版本控制
```bash
# 查看历史
python src/main.py template history <template_name>

# 恢复版本
python src/main.py template restore <template_name> <version>
```

### 测试模板
```bash
python src/main.py template test <template_name>
```

## 参数类型

| 类型 | 用途 | 示例 |
|------|------|------|
| `string` | 文本 | 文件名、描述 |
| `integer` | 数字 | 数量、大小 |
| `boolean` | 开关 | 启用/禁用 |
| `path` | 路径 | 文件或目录 |

## 占位符格式

```powershell
# 字符串
[string]$Name = "{{NAME}}"

# 数字
[int]$Count = {{COUNT}}

# 布尔
[bool]$Enable = ${{ENABLE}}

# 路径
[string]$Path = "{{PATH}}"
```

## 文件结构

```
templates/
├── custom/              # 自定义模板
│   ├── examples/        # 示例
│   └── my_category/     # 用户分类
├── .history/            # 版本历史
└── README.md
```

## 配置文件

位置: `config/templates.yaml`

```yaml
templates:
  custom:
    template_name:
      name: "显示名称"
      file: "templates/custom/category/file.ps1"
      description: "描述"
      keywords: ["关键词"]
      parameters:
        PARAM_NAME:
          type: "string"
          default: "默认值"
          description: "参数描述"
          required: true
```

## 最佳实践

✅ **推荐**
- 使用描述性的模板名称
- 为参数提供合理默认值
- 添加详细的参数描述
- 使用关键词便于搜索
- 定期导出重要模板

❌ **避免**
- 硬编码敏感信息
- 使用模糊的参数名
- 跳过参数验证
- 忽略错误处理

## 获取帮助

```bash
# 命令帮助
python src/main.py template --help

# 子命令帮助
python src/main.py template create --help
```

## 相关文档

- [完整用户指南](custom-template-guide.md)
- [命令行参考](template-cli-reference.md)
- [示例模板](../templates/custom/examples/)
