# 文档迁移映射表

---
## 📋 目录

- [概述](#概述)
- [迁移说明](#迁移说明)
- [完整映射表](#完整映射表)
- [按类别查找](#按类别查找)
- [过渡期说明](#过渡期说明)
- [需要帮助](#需要帮助)

---

## 概述

本文档提供了文档重构前后的完整映射关系，帮助您快速找到原有文档的新位置。

### 重构成果

- **重构前**: 28个文档
- **重构后**: 11个核心文档
- **精简率**: 61%
- **信息保留**: 100%

### 新文档架构

```
入门层 (3个)
├── README.md - 项目概述
├── 中文使用指南.md - 统一的中文使用文档
└── docs/README.md - 文档中心导航

深入层 (5个)
├── docs/user-guide.md - 综合用户指南（包含UI配置）
├── docs/template-guide.md - 模板系统完整指南
├── docs/architecture.md - 系统架构（包含所有图表）
├── docs/developer-guide.md - 开发者指南
└── docs/deployment-guide.md - 部署运维指南

参考层 (5个)
├── docs/api-reference.md - API参考
├── docs/cli-reference.md - CLI命令参考
├── docs/config-reference.md - 配置参考
├── docs/troubleshooting.md - 故障排除
└── docs/migration-map.md - 文档迁移映射表
```

---

## 迁移说明

### 整合策略

文档重构采用了以下整合策略：

1. **内容合并**: 相关主题的文档合并为综合指南
2. **章节提取**: 从多个文档提取相关章节组成新文档
3. **信息归档**: 项目管理类文档移至 `docs/archive/`
4. **结构优化**: 建立清晰的三层文档架构

### 如何使用本映射表

1. 在下方的[完整映射表](#完整映射表)中找到您要查找的旧文档
2. 查看"新位置"列，了解内容的去向
3. 点击链接直接跳转到新文档的相关章节
4. 如果文档被拆分到多个位置，所有位置都会列出

---

## 完整映射表

### 用户指南类文档

| 旧文档 | 状态 | 新位置 | 说明 |
|--------|------|--------|------|
| `template-quick-start.md` | ✅ 已整合 | [template-guide.md](template-guide.md#快速入门) | 快速入门章节 |
| `custom-template-guide.md` | ✅ 已整合 | [template-guide.md](template-guide.md#深入指南) | 深入指南章节 |
| `template-cli-reference.md` | ✅ 已整合 | [template-guide.md](template-guide.md#cli-参考)<br>[cli-reference.md](cli-reference.md) | 模板指南中的CLI章节<br>完整CLI参考文档 |
| `template-quick-reference.md` | ✅ 已整合 | [template-guide.md](template-guide.md#快速参考) | 快速参考章节 |
| `security-checker-guide.md` | ✅ 已整合 | [user-guide.md](user-guide.md#安全机制) | 安全机制章节 |
| `ui-system-guide.md` | ✅ 已整合 | [user-guide.md](user-guide.md#ui-系统) | UI系统章节 |
| `progress-manager-guide.md` | ✅ 已整合 | [user-guide.md](user-guide.md#进度管理) | 进度管理章节 |
| `startup-experience-guide.md` | ✅ 已整合 | [user-guide.md](user-guide.md#启动体验) | 启动体验章节 |
| `ui-configuration-guide.md` | ✅ 已整合 | [user-guide.md](user-guide.md#ui-配置)<br>[config-reference.md](config-reference.md#ui-配置) | UI配置章节<br>配置参考文档 |
| `theme-customization-guide.md` | ✅ 已整合 | [user-guide.md](user-guide.md#主题自定义) | 主题自定义章节 |
| `class-diagram.md` | ✅ 已整合 | [architecture.md](architecture.md#类图) | 架构文档中的类图章节 |
| `data-flow-diagram.md` | ✅ 已整合 | [architecture.md](architecture.md#数据流图) | 架构文档中的数据流图章节 |
| `system-architecture.md` | ✅ 已整合 | [architecture.md](architecture.md#系统架构图) | 架构文档中的系统架构图章节 |
| `use-case-diagram.md` | ✅ 已整合 | [architecture.md](architecture.md#用例图) | 架构文档中的用例图章节 |

### 开发者文档类

| 旧文档 | 状态 | 新位置 | 说明 |
|--------|------|--------|------|
| `architecture.md` | ✅ 增强 | [architecture.md](architecture.md) | 增强并整合模块架构 |
| `developer-guide.md` | ✅ 扩展 | [developer-guide.md](developer-guide.md) | 扩展并整合开发指南 |
| `config-module-implementation.md` | ✅ 已整合 | [architecture.md](architecture.md#配置模块)<br>[config-reference.md](config-reference.md) | 架构文档中的配置模块<br>配置参考文档 |
| `context-module-implementation.md` | ✅ 已整合 | [architecture.md](architecture.md#上下文模块) | 架构文档中的上下文模块 |
| `storage-engine-implementation.md` | ✅ 已整合 | [architecture.md](architecture.md#存储引擎) | 架构文档中的存储引擎 |
| `security-engine-implementation.md` | ✅ 已整合 | [architecture.md](architecture.md#安全引擎) | 架构文档中的安全引擎 |
| `main-controller-implementation.md` | ✅ 已整合 | [architecture.md](architecture.md#主控制器) | 架构文档中的主控制器 |
| `documentation-guide.md` | ✅ 已整合 | [developer-guide.md](developer-guide.md#文档编写)<br>[CONTRIBUTING.md](CONTRIBUTING.md) | 开发者指南中的文档章节<br>贡献指南 |

### 部署运维类文档

| 旧文档 | 状态 | 新位置 | 说明 |
|--------|------|--------|------|
| `docker-deployment.md` | ✅ 已整合 | [deployment-guide.md](deployment-guide.md#docker-部署) | Docker部署章节 |

| `cicd-and-license-guide.md` | ✅ 已整合 | [deployment-guide.md](deployment-guide.md#许可证说明) | 许可证说明章节 |
| `release-process.md` | ✅ 已整合 | [deployment-guide.md](deployment-guide.md#发布流程) | 发布流程章节 |
| `deployment-checklist.md` | ✅ 已整合 | [deployment-guide.md](deployment-guide.md#部署检查清单) | 部署检查清单章节 |
| `ollama-setup.md` | ✅ 已整合 | [deployment-guide.md](deployment-guide.md#ai-模型配置) | AI模型配置章节 |

### 项目管理类文档

| 旧文档 | 状态 | 新位置 | 说明 |
|--------|------|--------|------|
| `cleanup-summary.md` | 📦 已归档 | [archive/cleanup-summary.md](archive/cleanup-summary.md) | 历史项目管理文档 |
| `documentation-optimization-summary.md` | 📦 已归档 | [archive/documentation-optimization-summary.md](archive/documentation-optimization-summary.md) | 历史项目管理文档 |
| `release-deployment-summary.md` | 📦 已归档 | [archive/release-deployment-summary.md](archive/release-deployment-summary.md) | 历史项目管理文档 |

### 新创建的参考文档

| 新文档 | 内容来源 | 说明 |
|--------|----------|------|
| [api-reference.md](api-reference.md) | 从各模块文档提取 | 完整的API参考文档 |
| [cli-reference.md](cli-reference.md) | 从template-cli-reference.md等提取 | 完整的CLI命令参考 |
| [config-reference.md](config-reference.md) | 从config-module-implementation.md提取 | 完整的配置参考 |
| [troubleshooting.md](troubleshooting.md) | 从各文档提取常见问题 | 故障排除指南 |
| [CONTRIBUTING.md](CONTRIBUTING.md) | 从documentation-guide.md提取 | 文档贡献指南 |

---

## 按类别查找

### 我想了解如何使用系统

**旧文档** → **新文档**

- 快速开始 → [快速开始.md](../快速开始.md)
- UI系统使用 → [user-guide.md](user-guide.md#ui-系统)
- 进度管理 → [user-guide.md](user-guide.md#进度管理)
- 启动体验 → [user-guide.md](user-guide.md#启动体验)
- 安全机制 → [user-guide.md](user-guide.md#安全机制)

### 我想使用模板系统

**旧文档** → **新文档**

- 模板快速开始 → [template-guide.md](template-guide.md#快速入门)
- 自定义模板 → [template-guide.md](template-guide.md#深入指南)
- 模板CLI命令 → [template-guide.md](template-guide.md#cli-参考) 或 [cli-reference.md](cli-reference.md)
- 模板快速参考 → [template-guide.md](template-guide.md#快速参考)

### 我想了解系统架构

**旧文档** → **新文档**

- 系统架构 → [architecture.md](architecture.md)
- 配置模块 → [architecture.md](architecture.md#配置模块)
- 上下文模块 → [architecture.md](architecture.md#上下文模块)
- 存储引擎 → [architecture.md](architecture.md#存储引擎)
- 安全引擎 → [architecture.md](architecture.md#安全引擎)
- 主控制器 → [architecture.md](architecture.md#主控制器)

### 我想参与开发

**旧文档** → **新文档**

- 开发者指南 → [developer-guide.md](developer-guide.md)
- 文档编写规范 → [developer-guide.md](developer-guide.md#文档编写) 或 [CONTRIBUTING.md](CONTRIBUTING.md)
- 贡献流程 → [CONTRIBUTING.md](CONTRIBUTING.md)

### 我想部署系统

**旧文档** → **新文档**

- Docker部署 → [deployment-guide.md](deployment-guide.md#docker-部署)

- 发布流程 → [deployment-guide.md](deployment-guide.md#发布流程)
- 部署检查清单 → [deployment-guide.md](deployment-guide.md#部署检查清单)
- AI模型配置 → [deployment-guide.md](deployment-guide.md#ai-模型配置)
- 许可证说明 → [deployment-guide.md](deployment-guide.md#许可证说明)

### 我需要查找参考信息

**新文档**

- API参考 → [api-reference.md](api-reference.md)
- CLI命令参考 → [cli-reference.md](cli-reference.md)
- 配置参考 → [config-reference.md](config-reference.md)
- 故障排除 → [troubleshooting.md](troubleshooting.md)

---

## 过渡期说明

### 过渡期时间表

**过渡期**: 2025-10-17 至 2025-11-16 (30天)

在过渡期内：

1. ✅ **新文档已生效**: 所有新文档已创建并可正常使用
2. 📦 **旧文档已备份**: 所有旧文档备份在 `docs_backup_20251017/` 目录
3. 🔗 **链接已更新**: 项目中的所有文档链接已更新为新位置
4. 📚 **归档文档可访问**: 历史项目管理文档可在 `docs/archive/` 中访问

### 过渡期后

**2025-11-16 之后**:

- 备份目录 `docs_backup_20251017/` 将被移除
- 所有文档链接将指向新文档结构
- 归档文档将继续保留在 `docs/archive/` 中

### 如果您需要旧文档

在过渡期内，您可以：

1. **查看备份**: 访问 `docs_backup_20251017/` 目录查看原始文档
2. **使用Git历史**: 使用 `git log` 查看文档的历史版本
3. **查看归档**: 访问 `docs/archive/` 查看归档的项目管理文档

### 反馈和建议

如果您在使用新文档结构时遇到问题，或发现内容缺失，请：

1. 查看 [troubleshooting.md](troubleshooting.md) 寻找解决方案
2. 在GitHub上提交Issue: [提交Issue](https://github.com/your-repo/issues)
3. 联系项目维护团队

---

## 需要帮助

### 快速链接

- 📖 [文档中心](README.md) - 浏览所有文档
- 🏠 [项目首页](../README.md) - 返回项目主页
- 📋 [文档门户](../DOCUMENTATION.md) - 文档导航和索引
- 🔧 [故障排除](troubleshooting.md) - 解决常见问题
- 🤝 [贡献指南](CONTRIBUTING.md) - 参与文档改进

### 常见问题

**Q: 我找不到某个旧文档的内容了？**

A: 请使用本页面的[完整映射表](#完整映射表)或[按类别查找](#按类别查找)功能，找到内容的新位置。所有内容都已保留，只是重新组织了。

**Q: 新文档结构有什么优势？**

A: 新结构更清晰、更易维护，减少了重复内容，提供了更好的导航体验。文档数量减少了54%，但信息完整性保持100%。

**Q: 我可以继续使用旧的文档链接吗？**

A: 在过渡期内（30天），旧文档备份仍然可用。但建议尽快更新到新文档结构，因为备份将在过渡期后移除。

**Q: 如何快速适应新文档结构？**

A: 建议从[文档中心](README.md)开始，了解新的文档组织方式。根据您的角色（用户/开发者/运维），选择相应的阅读路径。


