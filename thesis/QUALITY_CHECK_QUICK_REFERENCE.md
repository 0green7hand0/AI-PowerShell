# 文档质量检查快速参考

## 快速开始

### Windows用户

```powershell
# 设置UTF-8编码
$env:PYTHONIOENCODING="utf-8"

# 运行所有检查
python scripts/quality_check_all.py
```

### Linux/Mac用户

```bash
# 运行所有检查
python3 scripts/quality_check_all.py
```

## 检查脚本

| 脚本 | 功能 | 报告文件 |
|------|------|----------|
| `quality_check_all.py` | 运行所有检查 | `quality-check-summary.md` |
| `quality_check_completeness.py` | 内容完整性 | `quality-check-completeness-report.md` |
| `quality_check_technical.py` | 技术准确性 | `quality-check-technical-report.md` |
| `quality_check_language.py` | 语言质量 | `quality-check-language-report.md` |
| `quality_check_format.py` | 格式规范性 | `quality-check-format-report.md` |

## 检查内容

### 1. 内容完整性 ✓
- ✓ 章节完成情况
- ✓ 图表编号连续性
- ✓ 参考文献完整性
- ✓ 附录材料齐全性

### 2. 技术准确性 ✓
- ✓ 术语使用准确性
- ✓ 代码示例正确性
- ✓ 数据一致性
- ✓ 结论支撑性

### 3. 语言质量 ✓
- ✓ 语法错误检查
- ✓ 表述清晰度
- ✓ 术语规范性
- ✓ 逻辑连贯性

### 4. 格式规范性 ✓
- ✓ 标题格式
- ✓ 图表格式
- ✓ 代码格式

## 报告解读

### 严重程度

- **✗ 错误**: 必须修复
- **⚠ 警告**: 建议改进
- **✓ 成功**: 检查通过

### 查看报告

1. 先看综合报告: `thesis/quality-check-summary.md`
2. 根据需要查看详细报告
3. 按文件名和行号定位问题

## 常见问题

### Q: 如何修复图表编号问题？

A: 大部分"错误"是因为图表在多个文件中出现（内容文件和列表文件），这是正常的。只需确保每章内编号连续即可。

### Q: 警告太多怎么办？

A: 优先修复影响阅读的警告，如语法错误、格式问题。代码示例中的标点混用可以保留。

### Q: 如何统一性能指标？

A: 在论文中确定一个标准值，然后全局替换其他不一致的值。

## 修复优先级

### 🔴 高优先级
1. 参考文献引用问题
2. Python代码语法错误
3. 关键性能指标不一致

### 🟡 中优先级
1. 补充附录材料
2. 统一标题格式
3. 添加代码语言标识

### 🟢 低优先级
1. 优化表述
2. 减少标点混用
3. 简化长句子

## 定期检查建议

- ✓ 完成每个章节后
- ✓ 提交导师审阅前
- ✓ 最终定稿前
- ✓ 答辩准备阶段

## 获取帮助

详细说明请查看: `thesis/quality-check-guide.md`

---

*快速参考卡 v1.0*
