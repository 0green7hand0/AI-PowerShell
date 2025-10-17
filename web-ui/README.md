# AI PowerShell Assistant - Web UI

现代化的 Web 可视化界面，用于 AI PowerShell 智能助手。

## 技术栈

- **Vue 3** - 渐进式 JavaScript 框架
- **TypeScript** - 类型安全的 JavaScript 超集
- **Vite** - 下一代前端构建工具
- **Element Plus** - Vue 3 UI 组件库
- **Tailwind CSS** - 实用优先的 CSS 框架
- **Pinia** - Vue 3 状态管理
- **Vue Router** - Vue 官方路由
- **Axios** - HTTP 客户端

## 项目结构

```
web-ui/
├── src/
│   ├── api/           # API 服务层
│   ├── components/    # 可复用组件
│   ├── stores/        # Pinia 状态管理
│   ├── utils/         # 工具函数
│   ├── views/         # 页面组件
│   ├── router/        # 路由配置
│   ├── App.vue        # 根组件
│   ├── main.ts        # 应用入口
│   └── style.css      # 全局样式
├── public/            # 静态资源
├── index.html         # HTML 模板
├── vite.config.ts     # Vite 配置
├── tsconfig.json      # TypeScript 配置
├── tailwind.config.js # Tailwind 配置
└── package.json       # 项目依赖
```

## 快速开始

### 1. 安装依赖

```bash
cd web-ui
npm install
```

### 2. 配置环境变量

复制 `.env.example` 到 `.env`：

```bash
cp .env.example .env
```

根据需要修改配置项。

### 3. 启动后端服务

确保后端服务已启动：

```bash
cd backend
python app.py
```

### 4. 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:5173

## 开发指南

详细的开发指南请参考：

- **[开发指南](./DEVELOPMENT.md)** - 完整的开发文档，包括环境配置、调试技巧、常见问题等
- **[API 文档](./API.md)** - 后端 API 接口文档
- **[后端文档](./backend/README.md)** - 后端服务说明

### 常用命令

```bash
# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview

# 代码检查
npm run lint

# 代码格式化
npm run format

# 类型检查
npm run type-check
```

## 环境变量

主要配置项：
- `VITE_API_BASE_URL` - 后端 API 地址（默认: http://localhost:5000/api）
- `VITE_WS_URL` - WebSocket 地址（默认: ws://localhost:5000/ws/logs）
- `VITE_APP_TITLE` - 应用标题
- `VITE_ENABLE_AUTH` - 是否启用认证
- `VITE_LOG_LEVEL` - 日志级别

完整的环境变量说明请参考 [开发指南](./DEVELOPMENT.md#环境变量)

## 功能模块

- **对话界面** (`/chat`) - 类似 ChatGPT 的对话式命令翻译和执行
- **历史记录** (`/history`) - 查看和管理命令历史
- **模板管理** (`/templates`) - 管理 PowerShell 脚本模板
- **日志监控** (`/logs`) - 实时查看系统日志
- **系统设置** (`/settings`) - 配置系统参数

## 开发规范

### 代码风格

- 使用 TypeScript 进行类型检查
- 遵循 ESLint 规则
- 使用 Prettier 格式化代码
- 组件使用 Composition API + `<script setup>`

### 命名规范

- 组件文件：PascalCase (e.g., `ChatView.vue`)
- 工具函数：camelCase (e.g., `formatDate`)
- 常量：UPPER_SNAKE_CASE (e.g., `API_BASE_URL`)
- CSS 类：kebab-case (e.g., `chat-view`)

### Git 提交规范

- `feat:` 新功能
- `fix:` 修复 bug
- `docs:` 文档更新
- `style:` 代码格式调整
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建/工具相关

## 浏览器支持

- Chrome >= 90
- Firefox >= 88
- Edge >= 90
- Safari >= 14

## License

MIT
