# PDF文档生成指南

本指南说明如何将Markdown文档转换为PDF格式。

## 需要转换的文档

1. **毕业论文** (`thesis/01-论文/thesis.md`)
   - 输出: `01-毕业论文.pdf`

2. **系统设计文档** (`thesis/02-设计文档/design-doc.md`)
   - 输出: `02-系统设计文档.pdf`

3. **用户手册** (`thesis/03-用户手册/user-manual.md`)
   - 输出: `03-用户手册.pdf`

4. **开发文档** (`thesis/05-开发文档/developer-guide.md`)
   - 输出: `04-开发文档.pdf`

5. **答辩PPT** (`thesis/04-答辩材料/defense-presentation.md`)
   - 输出: `05-答辩PPT.pdf`
   - 注意: 如果有PowerPoint版本，直接导出为PDF

## 方法一: 使用Pandoc (推荐)

### 1. 安装依赖

**Windows:**
```powershell
# 安装Pandoc
choco install pandoc

# 安装MiKTeX (LaTeX引擎)
choco install miktex
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt-get install pandoc texlive-xetex texlive-lang-chinese

# CentOS/RHEL
sudo yum install pandoc texlive-xetex
```

**macOS:**
```bash
brew install pandoc
brew install --cask mactex
```

### 2. 转换命令

**基本命令:**
```bash
pandoc input.md -o output.pdf --pdf-engine=xelatex -V CJKmainfont=SimSun -V geometry:margin=2.54cm --toc --toc-depth=3
```

**批量转换脚本 (Windows PowerShell):**
```powershell
# 进入项目根目录
cd path\to\AI-PowerShell

# 运行生成脚本
python scripts\generate_pdfs.py
```

**批量转换脚本 (Linux/macOS):**
```bash
# 进入项目根目录
cd path/to/AI-PowerShell

# 运行生成脚本
python3 scripts/generate_pdfs.py
```

### 3. 参数说明

- `--pdf-engine=xelatex`: 使用XeLaTeX引擎，支持中文
- `-V CJKmainfont=SimSun`: 设置中文字体为宋体
- `-V geometry:margin=2.54cm`: 设置页边距
- `--toc`: 生成目录
- `--toc-depth=3`: 目录深度为3级

## 方法二: 使用Typora

Typora是一个Markdown编辑器，支持直接导出PDF。

### 1. 安装Typora

访问 https://typora.io/ 下载安装

### 2. 导出步骤

1. 用Typora打开Markdown文件
2. 点击菜单: 文件 → 导出 → PDF
3. 选择保存位置
4. 点击保存

### 3. 设置中文字体

1. 点击菜单: 文件 → 偏好设置
2. 选择"外观"标签
3. 点击"打开主题文件夹"
4. 编辑CSS文件，添加中文字体设置

## 方法三: 使用VS Code

如果使用VS Code编辑Markdown，可以安装插件导出PDF。

### 1. 安装插件

在VS Code中搜索并安装:
- Markdown PDF
- Markdown All in One

### 2. 导出步骤

1. 打开Markdown文件
2. 按 `Ctrl+Shift+P` (macOS: `Cmd+Shift+P`)
3. 输入 "Markdown PDF: Export (pdf)"
4. 选择保存位置

## 方法四: 在线转换

如果无法安装本地工具，可以使用在线转换服务。

### 推荐网站

1. **Markdown to PDF** (https://www.markdowntopdf.com/)
2. **CloudConvert** (https://cloudconvert.com/md-to-pdf)
3. **Dillinger** (https://dillinger.io/)

### 注意事项

- 在线转换可能不支持复杂的中文排版
- 注意保护文档隐私
- 建议先用小文件测试

## PDF质量检查清单

生成PDF后，请检查以下项目:

### 1. 内容完整性
- [ ] 所有章节都已包含
- [ ] 图片正常显示
- [ ] 表格格式正确
- [ ] 代码块格式正确

### 2. 中文显示
- [ ] 中文字符正常显示
- [ ] 没有乱码
- [ ] 字体清晰可读

### 3. 格式规范
- [ ] 页边距正确 (2.54cm)
- [ ] 行距合适 (1.5倍)
- [ ] 标题层次清晰
- [ ] 页码连续

### 4. 目录和引用
- [ ] 目录完整
- [ ] 目录页码正确
- [ ] 图表编号正确
- [ ] 参考文献格式规范

### 5. 图表质量
- [ ] 图片清晰
- [ ] 图表标题完整
- [ ] 图表编号连续
- [ ] 图表在文中有引用

## 常见问题

### Q1: 中文显示乱码

**原因:** 未设置中文字体或字体不存在

**解决方案:**
```bash
# 检查系统字体
fc-list :lang=zh

# 使用其他中文字体
pandoc input.md -o output.pdf --pdf-engine=xelatex -V CJKmainfont="Microsoft YaHei"
```

### Q2: 图片无法显示

**原因:** 图片路径不正确或图片格式不支持

**解决方案:**
- 使用相对路径
- 确保图片文件存在
- 使用PNG或JPG格式

### Q3: 代码块格式错误

**原因:** 代码块语法不正确

**解决方案:**
- 使用三个反引号包裹代码
- 指定代码语言: ```python

### Q4: PDF文件过大

**原因:** 包含大量高分辨率图片

**解决方案:**
- 压缩图片
- 降低图片分辨率
- 使用矢量图

### Q5: 转换速度慢

**原因:** 文档过大或包含复杂内容

**解决方案:**
- 分章节转换
- 简化复杂表格
- 减少图片数量

## 推荐配置

### Pandoc配置文件

创建 `pandoc-config.yaml`:

```yaml
pdf-engine: xelatex
variables:
  CJKmainfont: SimSun
  geometry: margin=2.54cm
  linestretch: 1.5
  fontsize: 12pt
  documentclass: article
toc: true
toc-depth: 3
number-sections: true
```

使用配置文件:
```bash
pandoc input.md -o output.pdf --defaults=pandoc-config.yaml
```

## 批量处理脚本

### Windows PowerShell

```powershell
# convert-all-pdfs.ps1

$documents = @(
    @{Input="thesis\01-论文\thesis.md"; Output="thesis\00-提交材料\PDF文档\01-毕业论文.pdf"},
    @{Input="thesis\02-设计文档\design-doc.md"; Output="thesis\00-提交材料\PDF文档\02-系统设计文档.pdf"},
    @{Input="thesis\03-用户手册\user-manual.md"; Output="thesis\00-提交材料\PDF文档\03-用户手册.pdf"},
    @{Input="thesis\05-开发文档\developer-guide.md"; Output="thesis\00-提交材料\PDF文档\04-开发文档.pdf"}
)

foreach ($doc in $documents) {
    Write-Host "Converting $($doc.Input)..."
    pandoc $doc.Input -o $doc.Output `
        --pdf-engine=xelatex `
        -V CJKmainfont=SimSun `
        -V geometry:margin=2.54cm `
        --toc --toc-depth=3
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Success: $($doc.Output)" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed: $($doc.Input)" -ForegroundColor Red
    }
}
```

### Linux/macOS Bash

```bash
#!/bin/bash
# convert-all-pdfs.sh

declare -a documents=(
    "thesis/01-论文/thesis.md:thesis/00-提交材料/PDF文档/01-毕业论文.pdf"
    "thesis/02-设计文档/design-doc.md:thesis/00-提交材料/PDF文档/02-系统设计文档.pdf"
    "thesis/03-用户手册/user-manual.md:thesis/00-提交材料/PDF文档/03-用户手册.pdf"
    "thesis/05-开发文档/developer-guide.md:thesis/00-提交材料/PDF文档/04-开发文档.pdf"
)

for doc in "${documents[@]}"; do
    IFS=':' read -r input output <<< "$doc"
    echo "Converting $input..."
    
    pandoc "$input" -o "$output" \
        --pdf-engine=xelatex \
        -V CJKmainfont=SimSun \
        -V geometry:margin=2.54cm \
        --toc --toc-depth=3
    
    if [ $? -eq 0 ]; then
        echo "✓ Success: $output"
    else
        echo "✗ Failed: $input"
    fi
done
```

## 总结

1. **推荐方法**: 使用Pandoc + XeLaTeX，支持自动化批量转换
2. **简单方法**: 使用Typora，适合单个文档转换
3. **备用方法**: 使用在线工具，无需安装软件

选择适合自己的方法，确保生成的PDF质量符合要求。
