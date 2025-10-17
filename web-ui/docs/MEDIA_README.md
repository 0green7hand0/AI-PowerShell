# 媒体资源说明

本目录包含 AI PowerShell Assistant Web UI 的所有媒体资源，包括截图、演示视频和 GIF 动图。

## 目录结构

```
docs/
├── screenshots/     # 界面截图
├── videos/          # 演示视频
├── gifs/            # GIF 动图
└── MEDIA_README.md  # 本文件
```

## 截图列表

### 主界面

| 文件名 | 描述 | 尺寸 | 状态 |
|--------|------|------|------|
| `main-interface-light.png` | 浅色主题主界面 | 1920x1080 | 待创建 |
| `main-interface-dark.png` | 深色主题主界面 | 1920x1080 | 待创建 |

### Chat 功能

| 文件名 | 描述 | 尺寸 | 状态 |
|--------|------|------|------|
| `chat-translation.png` | 命令翻译界面 | 1920x1080 | 待创建 |
| `chat-execution.png` | 命令执行结果 | 1920x1080 | 待创建 |
| `chat-security-warning.png` | 安全警告对话框 | 800x600 | 待创建 |

### 历史记录

| 文件名 | 描述 | 尺寸 | 状态 |
|--------|------|------|------|
| `history-list.png` | 历史记录列表 | 1920x1080 | 待创建 |
| `history-detail.png` | 历史记录详情 | 800x600 | 待创建 |

### 模板管理

| 文件名 | 描述 | 尺寸 | 状态 |
|--------|------|------|------|
| `template-list.png` | 模板列表 | 1920x1080 | 待创建 |
| `template-use.png` | 模板使用对话框 | 800x600 | 待创建 |
| `template-create.png` | 模板创建对话框 | 800x600 | 待创建 |

### 日志和设置

| 文件名 | 描述 | 尺寸 | 状态 |
|--------|------|------|------|
| `logs-view.png` | 日志查看界面 | 1920x1080 | 待创建 |
| `settings-ai.png` | AI 设置页面 | 1920x1080 | 待创建 |
| `settings-security.png` | 安全设置页面 | 1920x1080 | 待创建 |

### 响应式设计

| 文件名 | 描述 | 尺寸 | 状态 |
|--------|------|------|------|
| `mobile-chat.png` | 移动端界面 | 375x812 | 待创建 |
| `tablet-view.png` | 平板端界面 | 768x1024 | 待创建 |

## 演示视频列表

| 文件名 | 描述 | 时长 | 状态 |
|--------|------|------|------|
| `quick-start.mp4` | 快速入门演示 | 2-3分钟 | 待创建 |
| `core-features.mp4` | 核心功能演示 | 5-7分钟 | 待创建 |
| `advanced-features.mp4` | 高级功能演示 | 5-7分钟 | 待创建 |

## GIF 动图列表

| 文件名 | 描述 | 时长 | 状态 |
|--------|------|------|------|
| `command-translation.gif` | 命令翻译过程 | 5-7秒 | 待创建 |
| `command-execution.gif` | 命令执行过程 | 3-5秒 | 待创建 |
| `history-search.gif` | 历史搜索功能 | 5-7秒 | 待创建 |
| `template-usage.gif` | 模板使用流程 | 8-10秒 | 待创建 |
| `theme-toggle.gif` | 主题切换动画 | 2-3秒 | 待创建 |
| `responsive-layout.gif` | 响应式布局演示 | 5-7秒 | 待创建 |

## 创建指南

详细的创建指南请参考 [DEMO_GUIDE.md](../DEMO_GUIDE.md)。

### 快速开始

1. **准备环境**
   ```bash
   # 启动开发服务器
   npm run dev
   cd backend && python app.py
   ```

2. **准备演示数据**
   - 创建一些示例命令历史
   - 准备几个模板
   - 确保所有功能正常工作

3. **截图**
   - 使用推荐的截图工具
   - 按照规范设置浏览器
   - 遵循命名约定

4. **录制视频/GIF**
   - 使用推荐的录屏工具
   - 按照脚本录制
   - 后期处理和优化

## 使用示例

### 在 Markdown 中引用

```markdown
# 功能展示

## 主界面

![主界面](./docs/screenshots/main-interface-light.png)

## 命令翻译

![命令翻译过程](./docs/gifs/command-translation.gif)
```

### 在 README 中使用

```markdown
# AI PowerShell Assistant Web UI

<p align="center">
  <img src="./docs/screenshots/main-interface-light.png" alt="主界面" width="800">
</p>

## 快速演示

<p align="center">
  <img src="./docs/gifs/command-translation.gif" alt="命令翻译" width="600">
</p>
```

## 文件规范

### 截图

- **格式**: PNG
- **分辨率**: 1920x1080（全屏）或实际大小（对话框）
- **文件大小**: < 2MB（优化后）
- **命名**: 小写字母，连字符分隔

### 视频

- **格式**: MP4 (H.264)
- **分辨率**: 1920x1080
- **帧率**: 30 FPS
- **文件大小**: < 50MB
- **命名**: 小写字母，连字符分隔

### GIF

- **格式**: GIF
- **尺寸**: 800x600 或更小
- **帧率**: 10-15 FPS
- **文件大小**: < 5MB
- **命名**: 小写字母，连字符分隔

## 优化工具

### 图片优化

```bash
# PNG 优化
pngquant --quality=80-90 input.png -o output.png

# 使用 ImageMagick
convert input.png -quality 85 output.png
```

### GIF 优化

```bash
# 使用 gifsicle
gifsicle -O3 --colors 256 input.gif -o output.gif

# 从视频创建 GIF
gifski -o output.gif --fps 15 --quality 90 input.mp4
```

### 视频压缩

```bash
# 使用 ffmpeg
ffmpeg -i input.mp4 -c:v libx264 -crf 23 -preset medium output.mp4
```

## 贡献

如果您想贡献媒体资源：

1. 遵循本文档的规范
2. 确保内容质量
3. 优化文件大小
4. 提供清晰的描述
5. 提交 Pull Request

## 版权和许可

所有媒体资源与项目使用相同的许可证。

---

**最后更新**: 2025-10-08
