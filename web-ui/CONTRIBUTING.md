# 贡献指南

感谢您对 AI PowerShell Assistant Web UI 项目的关注！我们欢迎各种形式的贡献。

## 目录

- [行为准则](#行为准则)
- [如何贡献](#如何贡献)
- [开发流程](#开发流程)
- [代码规范](#代码规范)
- [提交规范](#提交规范)
- [Pull Request 流程](#pull-request-流程)
- [报告问题](#报告问题)

---

## 行为准则

### 我们的承诺

为了营造一个开放和友好的环境，我们承诺：

- 使用友好和包容的语言
- 尊重不同的观点和经验
- 优雅地接受建设性批评
- 关注对社区最有利的事情
- 对其他社区成员表示同理心

### 不可接受的行为

- 使用性化的语言或图像
- 人身攻击或侮辱性评论
- 公开或私下骚扰
- 未经许可发布他人的私人信息
- 其他不道德或不专业的行为

---

## 如何贡献

### 贡献类型

我们欢迎以下类型的贡献：

1. **代码贡献**
   - 新功能开发
   - Bug 修复
   - 性能优化
   - 代码重构

2. **文档贡献**
   - 改进现有文档
   - 添加示例和教程
   - 翻译文档

3. **测试贡献**
   - 编写单元测试
   - 编写集成测试
   - 改进测试覆盖率

4. **设计贡献**
   - UI/UX 改进
   - 图标和插图
   - 主题设计

5. **其他贡献**
   - 报告 Bug
   - 提出功能建议
   - 回答问题
   - 代码审查

### 开始之前

1. **查看现有 Issues**：确保您的想法还没有被提出
2. **创建 Issue**：讨论您的想法或计划
3. **等待反馈**：获得维护者的认可后再开始工作
4. **Fork 项目**：创建您自己的副本

---

## 开发流程

### 1. 设置开发环境

```bash
# Fork 并克隆项目
git clone https://github.com/YOUR_USERNAME/ai-powershell-assistant.git
cd ai-powershell-assistant/web-ui

# 添加上游仓库
git remote add upstream https://github.com/ORIGINAL_OWNER/ai-powershell-assistant.git

# 安装依赖
npm install
cd backend && pip install -r requirements.txt
```

### 2. 创建功能分支

```bash
# 从 main 分支创建新分支
git checkout -b feature/your-feature-name

# 或修复 bug
git checkout -b fix/bug-description
```

### 3. 进行更改

- 编写代码
- 添加测试
- 更新文档
- 确保代码通过所有检查

### 4. 提交更改

```bash
# 添加更改
git add .

# 提交（遵循提交规范）
git commit -m "feat: add new feature"

# 推送到您的 Fork
git push origin feature/your-feature-name
```

### 5. 创建 Pull Request

1. 访问 GitHub 上的原始仓库
2. 点击 "New Pull Request"
3. 选择您的分支
4. 填写 PR 模板
5. 提交 PR

---

## 代码规范

### 前端代码规范

#### TypeScript/Vue

```typescript
// ✅ 好的示例
import { ref, computed } from 'vue';

interface User {
  id: string;
  name: string;
}

export function useUser() {
  const user = ref<User | null>(null);
  const isLoggedIn = computed(() => user.value !== null);
  
  return { user, isLoggedIn };
}

// ❌ 不好的示例
export function useUser() {
  const user = ref(null);  // 缺少类型
  const isLoggedIn = computed(() => user.value != null);  // 使用 != 而非 !==
  
  return { user, isLoggedIn };
}
```

#### 命名约定

- **组件**：PascalCase（`MyComponent.vue`）
- **文件**：kebab-case（`my-utils.ts`）
- **变量/函数**：camelCase（`myFunction`）
- **常量**：UPPER_SNAKE_CASE（`MAX_RETRIES`）
- **类型/接口**：PascalCase（`UserData`）

#### 代码格式

```bash
# 运行 ESLint
npm run lint

# 自动修复
npm run lint:fix

# 格式化代码
npm run format
```

### 后端代码规范

#### Python

```python
# ✅ 好的示例
from typing import List, Optional

def get_users(limit: int = 10) -> List[User]:
    """
    获取用户列表
    
    Args:
        limit: 返回的最大用户数
        
    Returns:
        用户列表
    """
    return []

# ❌ 不好的示例
def get_users(limit=10):  # 缺少类型提示
    return []  # 缺少文档字符串
```

#### 命名约定

- **类**：PascalCase（`UserManager`）
- **函数/变量**：snake_case（`get_user_data`）
- **常量**：UPPER_SNAKE_CASE（`MAX_RETRIES`）
- **私有**：前缀下划线（`_internal_method`）

#### 代码格式

```bash
# 格式化代码
black .

# 检查代码
flake8 .

# 类型检查
mypy .
```

### 通用规范

1. **保持简洁**：函数不超过 50 行
2. **单一职责**：每个函数只做一件事
3. **有意义的命名**：变量名要清晰表达意图
4. **添加注释**：复杂逻辑需要注释说明
5. **避免魔法数字**：使用常量代替硬编码的数字

---

## 提交规范

我们使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范。

### 提交格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type 类型

- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `perf`: 性能优化
- `test`: 测试相关
- `chore`: 构建/工具相关
- `ci`: CI/CD 相关

### 示例

```bash
# 新功能
git commit -m "feat(chat): add message search functionality"

# Bug 修复
git commit -m "fix(history): resolve pagination issue"

# 文档更新
git commit -m "docs: update API documentation"

# 重构
git commit -m "refactor(store): simplify state management"

# 性能优化
git commit -m "perf(list): implement virtual scrolling"

# 破坏性更改
git commit -m "feat(api): change response format

BREAKING CHANGE: API response structure has changed"
```

### 提交信息规则

1. **使用现在时**："add feature" 而非 "added feature"
2. **首字母小写**：除非是专有名词
3. **不要以句号结尾**
4. **简洁明了**：主题行不超过 50 字符
5. **详细说明**：正文部分可以详细描述

---

## Pull Request 流程

### PR 检查清单

在提交 PR 之前，请确保：

- [ ] 代码符合项目规范
- [ ] 添加了必要的测试
- [ ] 所有测试通过
- [ ] 更新了相关文档
- [ ] 提交信息清晰明确
- [ ] 没有合并冲突
- [ ] 代码已经过自我审查
- [ ] 添加了必要的注释

### PR 模板

```markdown
## 描述

简要描述这个 PR 的目的和内容。

## 相关 Issue

Closes #123

## 更改类型

- [ ] Bug 修复
- [ ] 新功能
- [ ] 破坏性更改
- [ ] 文档更新
- [ ] 代码重构
- [ ] 性能优化
- [ ] 测试相关

## 测试

描述您如何测试这些更改：

- [ ] 单元测试
- [ ] 集成测试
- [ ] 手动测试

## 截图（如适用）

添加截图以帮助解释您的更改。

## 检查清单

- [ ] 我的代码遵循项目的代码规范
- [ ] 我已经进行了自我审查
- [ ] 我已经添加了必要的注释
- [ ] 我已经更新了相关文档
- [ ] 我的更改没有产生新的警告
- [ ] 我已经添加了测试
- [ ] 所有测试都通过了
```

### 代码审查

PR 提交后：

1. **自动检查**：CI/CD 会自动运行测试
2. **代码审查**：维护者会审查您的代码
3. **反馈处理**：根据反馈进行修改
4. **批准合并**：获得批准后合并到主分支

### 审查标准

审查者会检查：

- **功能性**：代码是否正确实现了功能
- **可读性**：代码是否易于理解
- **可维护性**：代码是否易于修改
- **性能**：是否有性能问题
- **安全性**：是否有安全隐患
- **测试**：测试是否充分

---

## 报告问题

### Bug 报告

使用 Bug 报告模板：

```markdown
## Bug 描述

清晰简洁地描述 bug。

## 复现步骤

1. 访问 '...'
2. 点击 '...'
3. 滚动到 '...'
4. 看到错误

## 预期行为

描述您期望发生什么。

## 实际行为

描述实际发生了什么。

## 截图

如果适用，添加截图以帮助解释问题。

## 环境信息

- OS: [e.g. Windows 11]
- Browser: [e.g. Chrome 120]
- Version: [e.g. 1.0.0]

## 附加信息

添加任何其他相关信息。
```

### 功能请求

使用功能请求模板：

```markdown
## 功能描述

清晰简洁地描述您想要的功能。

## 问题背景

描述这个功能要解决什么问题。

## 建议的解决方案

描述您希望如何实现这个功能。

## 替代方案

描述您考虑过的其他解决方案。

## 附加信息

添加任何其他相关信息或截图。
```

---

## 开发技巧

### 保持同步

定期同步上游更改：

```bash
# 获取上游更改
git fetch upstream

# 合并到本地 main
git checkout main
git merge upstream/main

# 推送到您的 Fork
git push origin main

# 更新功能分支
git checkout feature/your-feature
git rebase main
```

### 调试技巧

**前端调试：**
```typescript
// 使用 Vue Devtools
// 使用 console.log
console.log('Debug:', data);

// 使用 debugger
debugger;
```

**后端调试：**
```python
# 使用 pdb
import pdb; pdb.set_trace()

# 使用日志
import logging
logger = logging.getLogger(__name__)
logger.debug('Debug message')
```

### 性能优化

- 使用 Chrome DevTools 分析性能
- 使用 Lighthouse 检查性能指标
- 使用 pytest-benchmark 测试后端性能

---

## 获取帮助

如果您需要帮助：

1. **查看文档**：[用户指南](./USER_GUIDE.md)、[开发者文档](./DEVELOPER_GUIDE.md)
2. **搜索 Issues**：可能已经有人遇到相同问题
3. **提问**：在 GitHub Discussions 中提问
4. **联系维护者**：通过邮件或其他方式

---

## 许可证

通过贡献代码，您同意您的贡献将在与项目相同的许可证下发布。

---

## 致谢

感谢所有贡献者！您的贡献使这个项目变得更好。

---

**最后更新**: 2025-10-08
