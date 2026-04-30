# 🚀 AI PowerShell Web UI - 快速启动

## 一键启动

### Windows

```powershell
# 方法1: PowerShell（推荐，实时日志）
.\start-web.ps1

# 方法2: CMD（简单，独立窗口）
start-web.bat
```

### Linux/macOS

```bash
# 启动
./start-web.sh

# 停止
./stop-web.sh
```

## 访问地址

- 🎨 **前端**: http://localhost:5173
- 🔧 **后端**: http://localhost:5000

## 功能特性

✅ 自然语言转PowerShell命令  
✅ 智能沙箱（高危命令自动隔离）  
✅ 三层安全保护  
✅ 命令历史记录  
✅ 模板管理  
✅ 实时日志监控  

## 测试命令

### 低风险（正常执行）
- "显示当前进程"
- "在桌面新建两个文件夹"
- "查看当前时间"

### 高危（沙箱执行）🔒
- "删除桌面上的临时文件"
- "停止记事本进程"

## 需要帮助？

📖 详细文档:
- [WEB_STARTUP_GUIDE.md](WEB_STARTUP_GUIDE.md) - 启动指南
- [SANDBOX_GUIDE.md](SANDBOX_GUIDE.md) - 沙箱功能
- [README.md](README.md) - 项目说明

🐛 遇到问题？查看 [WEB_STARTUP_GUIDE.md](WEB_STARTUP_GUIDE.md#故障排除)
