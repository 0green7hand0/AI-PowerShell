# 文档备份清单

**备份日期**: 2025-10-17  
**备份目录**: docs_backup_20251017  
**Git 分支**: docs-refactoring

## 备份说明

此备份在文档重构项目开始前创建，包含所有原始文档的完整副本。

## 文档列表

### 总计: 28个文档

#### 用户指南类 (8个)
1. template-quick-start.md
2. custom-template-guide.md
3. template-cli-reference.md
4. template-quick-reference.md
5. security-checker-guide.md
6. ui-system-guide.md
7. progress-manager-guide.md
8. startup-experience-guide.md

#### 开发者文档类 (7个)
9. architecture.md
10. developer-guide.md
11. config-module-implementation.md
12. context-module-implementation.md
13. storage-engine-implementation.md
14. security-engine-implementation.md
15. main-controller-implementation.md

#### 部署运维类 (6个)
16. docker-deployment.md
17. ci-cd-setup.md
18. cicd-and-license-guide.md
19. release-process.md
20. deployment-checklist.md
21. ollama-setup.md

#### 项目管理类 (3个)
22. cleanup-summary.md
23. documentation-optimization-summary.md
24. release-deployment-summary.md

#### 其他文档 (4个)
25. documentation-guide.md
26. README.md
27. theme-customization-guide.md
28. ui-configuration-guide.md

## 目录结构

```
docs/
├── architecture.md
├── ci-cd-setup.md
├── cicd-and-license-guide.md
├── cleanup-summary.md
├── config-module-implementation.md
├── context-module-implementation.md
├── custom-template-guide.md
├── deployment-checklist.md
├── developer-guide.md
├── docker-deployment.md
├── documentation-guide.md
├── documentation-optimization-summary.md
├── main-controller-implementation.md
├── ollama-setup.md
├── progress-manager-guide.md
├── README.md
├── release-deployment-summary.md
├── release-process.md
├── security-checker-guide.md
├── security-engine-implementation.md
├── startup-experience-guide.md
├── storage-engine-implementation.md
├── template-cli-reference.md
├── template-quick-reference.md
├── template-quick-start.md
├── theme-customization-guide.md
├── ui-configuration-guide.md
└── ui-system-guide.md
```

## 恢复说明

如需恢复到备份状态：

1. 切换回主分支: `git checkout main`
2. 删除当前 docs 目录: `Remove-Item -Recurse -Force docs`
3. 恢复备份: `Copy-Item -Recurse docs_backup_20251017 docs`
4. 删除备份清单: `Remove-Item docs/BACKUP_INVENTORY.md`

## 相关信息

- **需求文档**: .kiro/specs/documentation-refactoring/requirements.md
- **设计文档**: .kiro/specs/documentation-refactoring/design.md
- **任务列表**: .kiro/specs/documentation-refactoring/tasks.md
