# 🎓 AI PowerShell Assistant 学习中心

欢迎来到 AI PowerShell Assistant 的学习中心！这里为你提供了系统性的学习路径，帮助你从零开始掌握这个项目。

## 🗺️ 学习路径

### 🚀 快速开始（推荐新手）

如果你是第一次接触这个项目，建议按以下顺序学习：

1. **[基础概念演示](01_basic_example.py)** - 了解项目的核心概念
2. **[组件导览](02_component_tour.py)** - 认识各个核心组件
3. **[集成演示](03_integration_demo.py)** - 看组件如何协同工作
4. **[实践指南](04_hands_on_guide.md)** - 完整的动手实践教程

### 📚 学习资源

#### 核心文档
- **[项目总览](../README.md)** - 项目介绍和快速开始
- **[需求文档](../.kiro/specs/ai-powershell-assistant/requirements.md)** - 了解项目要解决什么问题
- **[设计文档](../.kiro/specs/ai-powershell-assistant/design.md)** - 了解系统架构设计
- **[任务列表](../.kiro/specs/ai-powershell-assistant/tasks.md)** - 了解实现过程

#### 用户文档
- **[用户指南](../docs/user/README.md)** - 如何安装和使用
- **[API文档](../docs/api/README.md)** - 完整的API参考
- **[配置指南](../docs/user/configuration.md)** - 如何配置系统
- **[故障排除](../docs/troubleshooting/README.md)** - 常见问题解决

#### 开发者文档
- **[开发者指南](../docs/developer/README.md)** - 如何参与开发
- **[架构文档](../docs/developer/architecture.md)** - 深入了解系统架构

## 🎯 按角色学习

### 👤 普通用户
如果你只是想使用这个系统：

1. 阅读 [用户指南](../docs/user/README.md)
2. 按照 [安装指南](../docs/user/installation.md) 安装系统
3. 学习 [基本使用方法](../docs/user/usage.md)
4. 查看 [FAQ](../docs/faq/README.md) 了解常见问题

### 🔧 系统管理员
如果你需要部署和管理这个系统：

1. 了解 [系统架构](../docs/developer/README.md#architecture-overview)
2. 学习 [部署方法](04_hands_on_guide.md#阶段3运行和测试60分钟)
3. 掌握 [配置管理](../docs/user/configuration.md)
4. 了解 [监控和维护](../docs/troubleshooting/README.md)

### 👨‍💻 开发者
如果你想了解代码或参与开发：

1. 运行所有学习示例（01-03）
2. 阅读 [实践指南](04_hands_on_guide.md)
3. 查看 [开发者指南](../docs/developer/README.md)
4. 了解 [贡献流程](../docs/developer/contributing.md)

### 🔒 安全专家
如果你关注系统安全：

1. 了解 [安全架构](../.kiro/specs/ai-powershell-assistant/design.md#security-engine)
2. 查看 [安全配置](../docs/user/security.md)
3. 学习 [安全规则定制](04_hands_on_guide.md#52-安全规则定制)
4. 了解 [审计功能](../docs/api/README.md#audit-logging)

## 🛠️ 实践练习

### 练习1：基础使用
```bash
# 运行基础示例
python 01_basic_example.py

# 目标：理解项目的核心概念
# 检查点：能够解释什么是MCP、AI引擎、安全引擎
```

### 练习2：组件理解
```bash
# 运行组件导览
python 02_component_tour.py

# 目标：了解各个组件的作用
# 检查点：能够说出每个组件的职责
```

### 练习3：系统集成
```bash
# 运行集成演示
python 03_integration_demo.py

# 目标：理解组件如何协同工作
# 检查点：能够描述完整的请求处理流程
```

### 练习4：实际部署
```bash
# 按照实践指南部署系统
# 参考：04_hands_on_guide.md

# 目标：成功运行完整系统
# 检查点：能够通过API与系统交互
```

### 练习5：功能定制
```bash
# 修改配置文件
# 添加自定义安全规则
# 测试自定义功能

# 目标：掌握系统定制方法
# 检查点：能够根据需求调整系统行为
```

## 📊 学习进度跟踪

使用这个检查清单跟踪你的学习进度：

### 基础理解 (25%)
- [ ] 理解项目目标和核心功能
- [ ] 了解MCP协议基本概念
- [ ] 知道系统的主要组件
- [ ] 理解自然语言到PowerShell的转换流程

### 组件掌握 (50%)
- [ ] 了解AI引擎的作用和工作原理
- [ ] 理解三层安全验证机制
- [ ] 掌握PowerShell执行引擎
- [ ] 了解日志和审计系统
- [ ] 理解配置管理机制

### 实践能力 (75%)
- [ ] 能够成功安装和运行系统
- [ ] 能够通过API与系统交互
- [ ] 能够阅读和理解日志
- [ ] 能够进行基本的故障排除
- [ ] 能够修改基本配置

### 高级应用 (100%)
- [ ] 能够部署到生产环境
- [ ] 能够定制安全规则
- [ ] 能够扩展系统功能
- [ ] 能够进行性能优化
- [ ] 能够为项目贡献代码

## 🤝 获得帮助

学习过程中遇到问题？这里有一些获得帮助的方式：

### 📖 查阅文档
- [故障排除指南](../docs/troubleshooting/README.md)
- [FAQ](../docs/faq/README.md)
- [API参考](../docs/api/README.md)

### 🔍 自助调试
```bash
# 检查系统状态
python -m src.main_integration --status

# 运行诊断
python -m src.validate_setup

# 查看日志
tail -f logs/app.log
```

### 💬 社区支持
- GitHub Issues: 报告问题或请求功能
- GitHub Discussions: 技术讨论和经验分享
- 项目文档: 查找详细的技术信息

## 🎉 学习完成后

恭喜你完成了 AI PowerShell Assistant 的学习！现在你可以：

1. **使用系统** - 在日常工作中使用这个AI助手
2. **部署系统** - 为团队或组织部署这个系统
3. **定制功能** - 根据特定需求定制系统功能
4. **贡献代码** - 为开源项目贡献你的力量
5. **分享经验** - 帮助其他人学习和使用这个系统

## 📝 反馈和建议

你的反馈对改进这个学习资源非常重要：

- 哪些部分最有帮助？
- 哪些地方需要更详细的解释？
- 你希望看到哪些额外的学习资源？
- 有什么改进建议？

欢迎通过 GitHub Issues 或 Discussions 分享你的想法！

---

**开始你的学习之旅吧！** 🚀