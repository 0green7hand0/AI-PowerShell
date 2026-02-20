# 文档质量检查指南

本指南说明如何使用自动化脚本进行文档质量检查。

## 概述

文档质量检查包含四个主要方面:

1. **内容完整性检查** - 检查所有章节、图表编号、参考文献和附录材料
2. **技术准确性检查** - 检查技术描述、代码示例、测试数据和结论
3. **语言质量检查** - 检查语法错误、表述清晰度、术语规范性和逻辑连贯性
4. **格式规范性检查** - 检查标题格式、图表格式、代码格式

## 快速开始

### 运行所有检查

```bash
python scripts/quality_check_all.py
```

这将依次运行所有四个检查脚本，并生成综合报告。

### 运行单个检查

如果只需要运行特定的检查，可以单独执行:

```bash
# 内容完整性检查
python scripts/quality_check_completeness.py

# 技术准确性检查
python scripts/quality_check_technical.py

# 语言质量检查
python scripts/quality_check_language.py

# 格式规范性检查
python scripts/quality_check_format.py
```

## 检查详情

### 1. 内容完整性检查

**检查项目:**
- 所有章节是否完成
- 图表编号是否连续
- 参考文献是否完整
- 附录材料是否齐全

**输出报告:** `thesis/quality-check-completeness-report.md`

**常见问题:**
- 图表编号不连续: 检查是否有遗漏或重复的编号
- 参考文献编号不连续: 确保所有引用都有对应的文献条目
- 章节内容较少: 补充章节内容，确保每章至少500字符

### 2. 技术准确性检查

**检查项目:**
- 技术术语使用是否准确
- 代码示例是否可运行
- 测试数据是否一致
- 结论是否有数据支撑

**输出报告:** `thesis/quality-check-technical-report.md`

**常见问题:**
- Python代码语法错误: 检查代码块中的语法问题
- 数据不一致: 确保同一指标在不同位置的数值一致
- 结论缺少支撑: 在结论附近添加数据、图表或表格

### 3. 语言质量检查

**检查项目:**
- 常见语法错误（重复字、标点错误等）
- 表述清晰度（模糊表述、冗余表述、句子长度）
- 术语使用规范性
- 逻辑连贯性（连接词使用、章节引用）

**输出报告:** `thesis/quality-check-language-report.md`

**常见问题:**
- 中英文标点混用: 统一使用中文标点或英文标点
- 括号不匹配: 检查所有括号、引号是否成对出现
- 模糊表述过多: 减少"可能"、"大概"等不确定词汇
- 术语不一致: 统一术语的写法（如PowerShell vs powershell）

### 4. 格式规范性检查

**检查项目:**
- 标题格式（层级、大小写、空格）
- 图格式（编号、标题、图片引用）
- 表格式（编号、标题、表格内容）
- 代码格式（语言标注、代码长度）

**输出报告:** `thesis/quality-check-format-report.md`

**常见问题:**
- 标题全大写: 使用正常的大小写格式
- 代码块未指定语言: 在代码块开始处添加语言标识（如```python）
- 图表标题过长: 简化标题，将详细说明放在正文中
- 代码行过长: 将长代码行拆分为多行

## 报告说明

### 报告结构

每个检查报告包含以下部分:

1. **检查摘要** - 成功、警告、错误的数量统计
2. **错误详情** - 必须修复的错误列表
3. **警告详情** - 建议改进的警告列表
4. **检查结果** - 成功通过的检查项

### 严重程度

- **✗ 错误 (Error)**: 必须修复的问题，会导致检查失败
- **⚠ 警告 (Warning)**: 建议改进的问题，不影响检查通过
- **✓ 成功 (Success)**: 通过的检查项

### 综合报告

运行 `quality_check_all.py` 后，会生成综合报告:

**文件位置:** `thesis/quality-check-summary.md`

**内容包括:**
- 所有检查的概览
- 总体统计信息
- 最终结论
- 各子报告的链接

## 修复建议

### 优先级

1. **高优先级**: 修复所有错误（✗）
2. **中优先级**: 修复影响阅读的警告（如语法错误、格式问题）
3. **低优先级**: 优化建议（如表述改进、术语统一）

### 修复流程

1. 查看综合报告，了解整体情况
2. 按优先级查看各子报告
3. 根据报告中的文件名和行号定位问题
4. 修复问题
5. 重新运行检查验证修复效果

### 批量修复

对于某些类型的问题，可以使用批量替换:

**示例: 统一术语**
```bash
# 将所有 "powershell" 替换为 "PowerShell"
# 使用编辑器的查找替换功能
```

**示例: 修复标点**
```bash
# 将中英文混用的逗号统一
# 查找: ,([a-zA-Z])
# 替换: ，$1
```

## 持续改进

### 定期检查

建议在以下时机运行质量检查:

- 完成每个章节后
- 提交给导师审阅前
- 最终定稿前
- 答辩准备阶段

### 自定义检查

如果需要添加自定义检查规则，可以修改相应的检查脚本:

- `scripts/quality_check_completeness.py` - 完整性检查
- `scripts/quality_check_technical.py` - 技术准确性检查
- `scripts/quality_check_language.py` - 语言质量检查
- `scripts/quality_check_format.py` - 格式规范性检查

### 检查规则配置

某些检查规则可以通过修改脚本中的配置来调整:

**示例: 调整句子长度阈值**
```python
# 在 quality_check_language.py 中
long_sentences = [s for s in sentences if len(s) > 100]  # 修改100为其他值
```

**示例: 添加新的术语检查**
```python
# 在 quality_check_language.py 中
common_terms = {
    "powershell": ["PowerShell", "Powershell", "powershell"],
    "新术语": ["变体1", "变体2", "变体3"]  # 添加新术语
}
```

## 常见问题

### Q: 检查脚本运行失败怎么办？

A: 检查以下几点:
1. 确保Python环境正确安装
2. 确保在项目根目录运行脚本
3. 检查文件路径是否正确
4. 查看错误信息，根据提示修复

### Q: 警告太多，是否都需要修复？

A: 不一定。警告是建议性的，可以根据实际情况选择性修复。优先修复影响阅读和理解的警告。

### Q: 如何忽略某些检查？

A: 可以注释掉检查脚本中相应的检查代码，或者在综合检查脚本中移除不需要的检查。

### Q: 检查结果不准确怎么办？

A: 自动化检查可能存在误报。如果确认某个警告或错误是误报，可以忽略它，或者修改检查规则。

## 附录

### 检查脚本依赖

所有检查脚本仅依赖Python标准库，无需安装额外依赖:

- `os`, `re`, `pathlib` - 文件和路径操作
- `ast` - Python代码语法检查
- `subprocess` - 运行子进程
- `datetime` - 时间戳生成

### 文件结构

```
scripts/
├── quality_check_all.py           # 综合检查脚本
├── quality_check_completeness.py  # 完整性检查
├── quality_check_technical.py     # 技术准确性检查
├── quality_check_language.py      # 语言质量检查
└── quality_check_format.py        # 格式规范性检查

thesis/
├── quality-check-summary.md              # 综合报告
├── quality-check-completeness-report.md  # 完整性报告
├── quality-check-technical-report.md     # 技术准确性报告
├── quality-check-language-report.md      # 语言质量报告
├── quality-check-format-report.md        # 格式规范性报告
└── quality-check-guide.md                # 本指南
```

### 参考资料

- [GB/T 7714-2015 参考文献著录规则](https://www.gb688.cn/bzgk/gb/newGbInfo?hcno=7FA63E9BBA56E60471AEDAEBDE44B14C)
- [学术论文写作规范](https://www.example.com)
- [Markdown格式规范](https://www.markdownguide.org/)

---

*最后更新: 2024年*
