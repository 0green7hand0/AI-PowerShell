# Development Guide - AI PowerShell Assistant Web UI

本文档提供详细的开发指南，帮助开发者快速上手项目开发。

## 目录

- [环境要求](#环境要求)
- [快速开始](#快速开始)
- [开发工具配置](#开发工具配置)
- [项目结构](#项目结构)
- [开发规范](#开发规范)
- [调试指南](#调试指南)
- [常见问题](#常见问题)

## 环境要求

### 必需软件

- **Node.js**: >= 16.0.0 (推荐使用 18.x 或 20.x LTS 版本)
- **npm**: >= 8.0.0 或 **pnpm**: >= 7.0.0
- **Git**: >= 2.30.0

### 推荐工具

- **VS Code**: 推荐的代码编辑器
- **Vue DevTools**: 浏览器扩展，用于调试 Vue 应用
- **Postman** 或 **Insomnia**: API 测试工具

### VS Code 扩展推荐

安装以下扩展以获得最佳开发体验：

- **Vue Language Features (Volar)** - Vue 3 语言支持
- **TypeScript Vue Plugin (Volar)** - Vue 中的 TypeScript 支持
- **ESLint** - 代码检查
- **Prettier** - 代码格式化
- **Tailwind CSS IntelliSense** - Tailwind CSS 智能提示
- **Path Intellisense** - 路径自动补全
- **Auto Rename Tag** - 自动重命名标签
- **GitLens** - Git 增强工具

## 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd ai-powershell-assistant/web-ui
```

### 2. 安装依赖

使用 npm:
```bash
npm install
```

或使用 pnpm (更快):
```bash
pnpm install
```

### 3. 配置环境变量

复制环境变量模板：
```bash
cp .env.example .env
```

根据需要修改 `.env` 文件中的配置。

### 4. 启动后端服务

在启动前端之前，确保后端服务已启动：

```bash
cd ../web-ui/backend
python app.py
```

后端服务将在 `http://localhost:5000` 运行。

### 5. 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:5173 查看应用。

## 开发工具配置

### Vite 配置

Vite 配置文件位于 `vite.config.ts`，主要配置包括：

#### 开发服务器

```typescript
server: {
  port: 5173,              // 开发服务器端口
  host: true,              // 监听所有地址
  open: false,             // 不自动打开浏览器
  cors: true,              // 启用 CORS
  proxy: {                 // API 代理配置
    '/api': {
      target: 'http://localhost:5000',
      changeOrigin: true
    }
  }
}
```

#### 路径别名

```typescript
resolve: {
  alias: {
    '@': resolve(__dirname, 'src')  // @ 指向 src 目录
  }
}
```

使用示例：
```typescript
import ChatView from '@/views/ChatView.vue'
import { useAppStore } from '@/stores/app'
```

#### 构建优化

```typescript
build: {
  outDir: 'dist',
  sourcemap: false,
  minify: 'terser',
  rollupOptions: {
    output: {
      manualChunks: {
        'vue-vendor': ['vue', 'vue-router', 'pinia'],
        'element-plus': ['element-plus']
      }
    }
  }
}
```

### 环境变量

环境变量必须以 `VITE_` 前缀开头才能在客户端代码中访问。

#### 可用环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `VITE_API_BASE_URL` | 后端 API 地址 | `http://localhost:5000/api` |
| `VITE_WS_URL` | WebSocket 地址 | `ws://localhost:5000/ws/logs` |
| `VITE_APP_TITLE` | 应用标题 | `AI PowerShell Assistant` |
| `VITE_APP_VERSION` | 应用版本 | `1.0.0` |
| `VITE_ENABLE_AUTH` | 启用认证 | `false` |
| `VITE_LOG_LEVEL` | 日志级别 | `info` |

#### 在代码中使用环境变量

```typescript
// 访问环境变量
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL
const appTitle = import.meta.env.VITE_APP_TITLE

// 检查开发模式
if (import.meta.env.DEV) {
  console.log('Development mode')
}

// 检查生产模式
if (import.meta.env.PROD) {
  console.log('Production mode')
}
```

### TypeScript 配置

TypeScript 配置文件位于 `tsconfig.json`，主要配置：

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "jsx": "preserve",
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

### ESLint 配置

ESLint 配置文件位于 `.eslintrc.cjs`，用于代码检查。

运行 ESLint:
```bash
npm run lint
```

自动修复问题:
```bash
npm run lint:fix
```

### Prettier 配置

Prettier 配置文件位于 `.prettierrc.json`，用于代码格式化。

格式化代码:
```bash
npm run format
```

## 项目结构

```
web-ui/
├── src/
│   ├── api/              # API 服务层
│   │   ├── command.ts    # 命令相关 API
│   │   ├── history.ts    # 历史记录 API
│   │   ├── template.ts   # 模板 API
│   │   ├── config.ts     # 配置 API
│   │   └── logs.ts       # 日志 API
│   │
│   ├── components/       # 可复用组件
│   │   ├── common/       # 通用组件
│   │   ├── chat/         # 聊天相关组件
│   │   ├── history/      # 历史记录组件
│   │   └── template/     # 模板组件
│   │
│   ├── stores/           # Pinia 状态管理
│   │   ├── app.ts        # 应用全局状态
│   │   ├── chat.ts       # 聊天状态
│   │   ├── history.ts    # 历史记录状态
│   │   └── template.ts   # 模板状态
│   │
│   ├── router/           # 路由配置
│   │   └── index.ts      # 路由定义
│   │
│   ├── utils/            # 工具函数
│   │   ├── axios.ts      # Axios 配置
│   │   ├── format.ts     # 格式化工具
│   │   └── storage.ts    # 本地存储工具
│   │
│   ├── views/            # 页面组件
│   │   ├── ChatView.vue
│   │   ├── HistoryView.vue
│   │   ├── TemplateView.vue
│   │   ├── LogsView.vue
│   │   └── SettingsView.vue
│   │
│   ├── types/            # TypeScript 类型定义
│   │   ├── api.ts        # API 类型
│   │   ├── store.ts      # Store 类型
│   │   └── common.ts     # 通用类型
│   │
│   ├── App.vue           # 根组件
│   ├── main.ts           # 应用入口
│   └── style.css         # 全局样式
│
├── public/               # 静态资源
├── .env                  # 环境变量（不提交到 Git）
├── .env.example          # 环境变量模板
├── .gitignore            # Git 忽略规则
├── index.html            # HTML 模板
├── package.json          # 项目依赖
├── vite.config.ts        # Vite 配置
├── tsconfig.json         # TypeScript 配置
├── tailwind.config.js    # Tailwind CSS 配置
├── README.md             # 项目说明
└── DEVELOPMENT.md        # 开发指南（本文档）
```

## 开发规范

### 代码风格

#### Vue 组件

使用 Composition API + `<script setup>` 语法：

```vue
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import type { Message } from '@/types/api'

// Props
interface Props {
  title?: string
  messages: Message[]
}

const props = withDefaults(defineProps<Props>(), {
  title: 'Chat'
})

// Emits
interface Emits {
  (e: 'send', message: string): void
  (e: 'delete', id: string): void
}

const emit = defineEmits<Emits>()

// State
const input = ref('')
const isLoading = ref(false)

// Computed
const messageCount = computed(() => props.messages.length)

// Methods
const handleSend = () => {
  if (input.value.trim()) {
    emit('send', input.value)
    input.value = ''
  }
}

// Lifecycle
onMounted(() => {
  console.log('Component mounted')
})
</script>

<template>
  <div class="chat-view">
    <h1>{{ title }}</h1>
    <p>Messages: {{ messageCount }}</p>
    <!-- Template content -->
  </div>
</template>

<style scoped>
.chat-view {
  /* Component styles */
}
</style>
```

#### TypeScript

使用严格的类型定义：

```typescript
// 定义接口
interface User {
  id: string
  name: string
  email: string
}

// 定义类型别名
type Status = 'idle' | 'loading' | 'success' | 'error'

// 使用泛型
function fetchData<T>(url: string): Promise<T> {
  return fetch(url).then(res => res.json())
}

// 使用类型守卫
function isUser(obj: any): obj is User {
  return obj && typeof obj.id === 'string'
}
```

### 命名规范

#### 文件命名

- **组件文件**: PascalCase
  - `ChatView.vue`
  - `MessageCard.vue`
  - `InputBox.vue`

- **工具文件**: camelCase
  - `formatDate.ts`
  - `apiClient.ts`
  - `storage.ts`

- **类型文件**: camelCase
  - `api.ts`
  - `store.ts`
  - `common.ts`

#### 变量命名

```typescript
// 常量: UPPER_SNAKE_CASE
const API_BASE_URL = 'http://localhost:5000'
const MAX_RETRY_COUNT = 3

// 变量和函数: camelCase
const userName = 'John'
const isLoading = false
function fetchUserData() {}

// 类和接口: PascalCase
class UserService {}
interface UserData {}

// 私有属性: 前缀 _
class MyClass {
  private _privateValue = 0
}
```

#### CSS 类命名

使用 BEM 命名规范或 kebab-case：

```css
/* BEM */
.chat-view {}
.chat-view__header {}
.chat-view__message {}
.chat-view__message--active {}

/* kebab-case */
.message-card {}
.input-box {}
.loading-spinner {}
```

### Git 提交规范

使用 Conventional Commits 规范：

```
<type>(<scope>): <subject>

<body>

<footer>
```

#### Type 类型

- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式调整（不影响功能）
- `refactor`: 代码重构
- `perf`: 性能优化
- `test`: 测试相关
- `chore`: 构建/工具相关
- `ci`: CI/CD 相关

#### 示例

```bash
# 新功能
git commit -m "feat(chat): add message search functionality"

# 修复 bug
git commit -m "fix(history): resolve pagination issue"

# 文档更新
git commit -m "docs: update development guide"

# 代码重构
git commit -m "refactor(api): simplify error handling logic"
```

## 调试指南

### Vue DevTools

1. 安装 Vue DevTools 浏览器扩展
2. 打开开发者工具
3. 切换到 Vue 标签页
4. 查看组件树、状态、事件等

### 浏览器调试

#### 断点调试

在代码中添加 `debugger` 语句：

```typescript
function handleSubmit() {
  debugger  // 程序会在这里暂停
  // Your code
}
```

#### Console 调试

```typescript
console.log('Debug info:', data)
console.error('Error:', error)
console.warn('Warning:', warning)
console.table(arrayData)  // 表格形式显示数组
```

### Network 调试

1. 打开开发者工具
2. 切换到 Network 标签页
3. 查看 API 请求和响应
4. 检查请求头、响应头、状态码等

### Vite 调试

查看 Vite 开发服务器日志：

```bash
npm run dev -- --debug
```

### 性能分析

使用 Vue DevTools 的 Performance 标签：

1. 点击 Record 按钮
2. 执行需要分析的操作
3. 停止录制
4. 查看组件渲染时间、更新频率等

## 常见问题

### 1. 端口被占用

**问题**: `Error: listen EADDRINUSE: address already in use :::5173`

**解决方案**:
```bash
# 查找占用端口的进程
netstat -ano | findstr :5173

# 杀死进程
taskkill /PID <PID> /F

# 或者修改端口
# 在 vite.config.ts 中修改 server.port
```

### 2. 模块找不到

**问题**: `Cannot find module '@/components/...'`

**解决方案**:
- 检查 `tsconfig.json` 中的 paths 配置
- 检查 `vite.config.ts` 中的 alias 配置
- 重启 VS Code 或开发服务器

### 3. 类型错误

**问题**: TypeScript 类型检查错误

**解决方案**:
```bash
# 清除 TypeScript 缓存
rm -rf node_modules/.vite

# 重新安装依赖
npm install

# 重启 TypeScript 服务器（VS Code）
Ctrl+Shift+P -> TypeScript: Restart TS Server
```

### 4. 样式不生效

**问题**: Tailwind CSS 样式不生效

**解决方案**:
- 检查 `tailwind.config.js` 中的 content 配置
- 确保在 `main.ts` 中导入了样式文件
- 清除浏览器缓存
- 重启开发服务器

### 5. API 请求失败

**问题**: API 请求返回 404 或 CORS 错误

**解决方案**:
- 确保后端服务已启动
- 检查 `.env` 中的 API 地址配置
- 检查 `vite.config.ts` 中的 proxy 配置
- 查看浏览器 Network 标签中的请求详情

### 6. 热更新不工作

**问题**: 修改代码后页面不自动刷新

**解决方案**:
```bash
# 清除缓存
rm -rf node_modules/.vite
rm -rf dist

# 重启开发服务器
npm run dev
```

## 有用的命令

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview

# 代码检查
npm run lint

# 自动修复代码问题
npm run lint:fix

# 代码格式化
npm run format

# 类型检查
npm run type-check

# 清除缓存
rm -rf node_modules/.vite
rm -rf dist

# 重新安装依赖
rm -rf node_modules
npm install
```

## 相关资源

- [Vue 3 文档](https://vuejs.org/)
- [Vite 文档](https://vitejs.dev/)
- [TypeScript 文档](https://www.typescriptlang.org/)
- [Element Plus 文档](https://element-plus.org/)
- [Tailwind CSS 文档](https://tailwindcss.com/)
- [Pinia 文档](https://pinia.vuejs.org/)
- [Vue Router 文档](https://router.vuejs.org/)

## 获取帮助

如果遇到问题：

1. 查看本文档的常见问题部分
2. 搜索项目 Issues
3. 查阅相关技术文档
4. 向团队成员寻求帮助
