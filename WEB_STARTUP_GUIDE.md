# Web UI 启动指南

## 🚀 快速启动

### Windows 用户

**方法1: PowerShell 脚本（推荐）**
```powershell
.\start-web.ps1
```

**方法2: CMD 批处理**
```cmd
start-web.bat
```

### Linux/macOS 用户

```bash
# 启动服务
./start-web.sh

# 停止服务
./stop-web.sh
```

## 📋 启动脚本功能

### 自动检查
- ✅ Python 环境
- ✅ Node.js 环境
- ✅ Docker 状态（可选）
- ✅ 后端依赖
- ✅ 前端依赖

### 自动启动
- 🔧 后端 Flask 服务 (http://localhost:5000)
- 🎨 前端 Vue 开发服务器 (http://localhost:5173)

### 实时监控
- 📝 显示实时日志
- 🔍 监控服务状态
- ⚠️ 自动错误检测

## 📁 脚本文件说明

| 文件 | 平台 | 说明 |
|------|------|------|
| `start-web.ps1` | Windows PowerShell | 功能最完整，支持实时日志 |
| `start-web.bat` | Windows CMD | 简单易用，打开独立窗口 |
| `start-web.sh` | Linux/macOS | 后台运行，保存日志到文件 |
| `stop-web.sh` | Linux/macOS | 停止所有服务 |

## 🎯 使用场景

### 场景1: 开发调试（推荐 PowerShell）

```powershell
# 启动并查看实时日志
.\start-web.ps1

# 按 Ctrl+C 停止所有服务
```

**优点**:
- 实时查看前后端日志
- 一键启动和停止
- 自动检测环境

### 场景2: 快速测试（推荐 CMD）

```cmd
# 启动服务（打开独立窗口）
start-web.bat

# 关闭窗口即可停止服务
```

**优点**:
- 前后端独立窗口
- 可以分别查看日志
- 简单直观

### 场景3: 后台运行（Linux/macOS）

```bash
# 启动服务（后台运行）
./start-web.sh

# 查看日志
tail -f logs/backend.log
tail -f logs/frontend.log

# 停止服务
./stop-web.sh
```

**优点**:
- 后台运行不占用终端
- 日志保存到文件
- 适合长时间运行

## 🔧 手动启动（高级）

如果脚本无法使用，可以手动启动：

### 启动后端

```bash
# Windows
cd web-ui\backend
venv\Scripts\activate
python app.py

# Linux/macOS
cd web-ui/backend
source venv/bin/activate
python app.py
```

### 启动前端

```bash
cd web-ui
npm run dev
```

## 📊 服务端口

| 服务 | 端口 | 地址 |
|------|------|------|
| 前端 | 5173 | http://localhost:5173 |
| 后端 | 5000 | http://localhost:5000 |
| 后端健康检查 | 5000 | http://localhost:5000/api/health |

## 🐛 故障排除

### 问题1: 端口被占用

**错误**: `Address already in use`

**解决方案**:
```powershell
# Windows - 查找占用端口的进程
netstat -ano | findstr :5000
netstat -ano | findstr :5173

# 结束进程
taskkill /PID <进程ID> /F

# Linux/macOS
lsof -ti:5000 | xargs kill -9
lsof -ti:5173 | xargs kill -9
```

### 问题2: Python 虚拟环境未激活

**错误**: `ModuleNotFoundError`

**解决方案**:
```bash
# 重新创建虚拟环境
cd web-ui/backend
python -m venv venv

# 激活并安装依赖
# Windows
venv\Scripts\activate
pip install -r requirements.txt

# Linux/macOS
source venv/bin/activate
pip install -r requirements.txt
```

### 问题3: 前端依赖未安装

**错误**: `Cannot find module`

**解决方案**:
```bash
cd web-ui
npm install
```

### 问题4: Docker 未运行

**警告**: `Docker: 未运行 (沙箱功能不可用)`

**解决方案**:
```powershell
# 启动 Docker Desktop
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"

# 等待30-60秒
# 验证
docker ps
```

## 💡 最佳实践

### 开发环境

1. **使用 PowerShell 脚本**
   ```powershell
   .\start-web.ps1
   ```
   - 实时查看日志
   - 快速调试问题

2. **保持 Docker 运行**
   - 启用沙箱功能
   - 测试高危命令

3. **定期更新依赖**
   ```bash
   # 后端
   cd web-ui/backend
   pip install -r requirements.txt --upgrade
   
   # 前端
   cd web-ui
   npm update
   ```

### 生产环境

不要使用这些开发脚本！请参考 `DEPLOYMENT.md` 使用生产级部署方案。

## 📝 日志位置

### PowerShell 脚本
- 实时显示在终端

### CMD 批处理
- 显示在独立窗口

### Linux/macOS 脚本
- 后端: `logs/backend.log`
- 前端: `logs/frontend.log`
- PID: `logs/backend.pid`, `logs/frontend.pid`

## 🎉 启动成功标志

看到以下信息表示启动成功：

```
========================================
  🎉 服务启动完成！
========================================

📍 访问地址:
   前端: http://localhost:5173
   后端: http://localhost:5000
```

现在可以在浏览器中访问 http://localhost:5173 开始使用！

## 🔗 相关文档

- [SANDBOX_GUIDE.md](SANDBOX_GUIDE.md) - 沙箱功能指南
- [web-ui/README.md](web-ui/README.md) - Web UI 详细文档
- [web-ui/backend/README.md](web-ui/backend/README.md) - 后端 API 文档
- [DEPLOYMENT.md](web-ui/DEPLOYMENT.md) - 生产部署指南
