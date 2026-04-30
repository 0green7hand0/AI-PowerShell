@echo off
REM AI PowerShell Web UI 启动脚本 (Windows CMD)
REM 同时启动前端和后端服务

echo ========================================
echo   AI PowerShell Web UI 启动脚本
echo ========================================
echo.

REM 检查是否在项目根目录
if not exist "web-ui" (
    echo [错误] 请在项目根目录运行此脚本
    pause
    exit /b 1
)

REM 检查 Python
echo [检查] Python 环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)
echo [成功] Python 已安装

REM 检查 Node.js
echo [检查] Node.js 环境...
node --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Node.js，请先安装 Node.js
    pause
    exit /b 1
)
echo [成功] Node.js 已安装

REM 启动后端服务
echo.
echo [启动] 后端服务...
start "AI PowerShell Backend" cmd /k "cd web-ui\backend && python app.py"
echo [成功] 后端服务启动中...
echo         后端地址: http://localhost:5000

REM 等待后端启动
echo [等待] 后端服务启动 (5秒)...
timeout /t 5 /nobreak >nul

REM 启动前端服务
echo.
echo [启动] 前端服务...
start "AI PowerShell Frontend" cmd /k "cd web-ui && npm run dev"
echo [成功] 前端服务启动中...
echo         前端地址: http://localhost:5173

echo.
echo ========================================
echo   服务启动完成！
echo ========================================
echo.
echo 访问地址:
echo   前端: http://localhost:5173
echo   后端: http://localhost:5000
echo.
echo 提示:
echo   - 两个命令窗口已打开
echo   - 关闭窗口即可停止对应服务
echo   - 按任意键退出此脚本
echo.
echo ========================================
pause
