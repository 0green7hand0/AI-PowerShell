#!/usr/bin/env pwsh
<#
.SYNOPSIS
    启动 AI PowerShell Web UI (前端 + 后端)

.DESCRIPTION
    自动启动后端Flask服务和前端Vue开发服务器
    
.EXAMPLE
    .\start-web.ps1
#>

# 设置错误处理
$ErrorActionPreference = "Stop"

# 颜色输出函数
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

# 显示标题
Write-ColorOutput "`n========================================" "Cyan"
Write-ColorOutput "  AI PowerShell Web UI 启动脚本" "Cyan"
Write-ColorOutput "========================================`n" "Cyan"

# 检查是否在项目根目录
if (-not (Test-Path "web-ui")) {
    Write-ColorOutput "❌ 错误: 请在项目根目录运行此脚本" "Red"
    exit 1
}

# 1. 检查 Python
Write-ColorOutput "📋 检查 Python 环境..." "Yellow"
try {
    $pythonVersion = python --version 2>&1
    Write-ColorOutput "✅ Python: $pythonVersion" "Green"
} catch {
    Write-ColorOutput "❌ 错误: 未找到 Python，请先安装 Python 3.8+" "Red"
    exit 1
}

# 2. 检查 Node.js
Write-ColorOutput "`n📋 检查 Node.js 环境..." "Yellow"
try {
    $nodeVersion = node --version 2>&1
    Write-ColorOutput "✅ Node.js: $nodeVersion" "Green"
} catch {
    Write-ColorOutput "❌ 错误: 未找到 Node.js，请先安装 Node.js" "Red"
    exit 1
}

# 3. 检查 Docker (可选)
Write-ColorOutput "`n📋 检查 Docker 状态..." "Yellow"
try {
    $dockerStatus = docker ps 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "✅ Docker: 运行中 (沙箱功能可用)" "Green"
    } else {
        Write-ColorOutput "⚠️  Docker: 未运行，正在尝试启动..." "Yellow"
        
        # 尝试启动 Docker Desktop
        $dockerPath = "C:\Program Files\Docker\Docker\Docker Desktop.exe"
        if (Test-Path $dockerPath) {
            Start-Process $dockerPath
            Write-ColorOutput "⏳ 等待 Docker 启动..." "Yellow"
            
            # 等待 Docker 启动（最多等待 60 秒）
            $maxWait = 60
            $waited = 0
            while ($waited -lt $maxWait) {
                Start-Sleep -Seconds 5
                $waited += 5
                try {
                    $null = docker ps 2>&1
                    if ($LASTEXITCODE -eq 0) {
                        Write-ColorOutput "✅ Docker: 启动成功 (沙箱功能可用)" "Green"
                        break
                    }
                } catch {}
                Write-ColorOutput "   等待中... ($waited/$maxWait 秒)" "Gray"
            }
            
            if ($waited -ge $maxWait) {
                Write-ColorOutput "⚠️  Docker 启动超时，沙箱功能不可用" "Yellow"
            }
        } else {
            Write-ColorOutput "⚠️  Docker Desktop 未安装 (沙箱功能不可用)" "Yellow"
        }
    }
} catch {
    Write-ColorOutput "⚠️  Docker: 未安装 (沙箱功能不可用)" "Yellow"
}

# 4. 检查后端依赖
Write-ColorOutput "`n📋 检查后端依赖..." "Yellow"
if (-not (Test-Path "web-ui/backend/venv")) {
    Write-ColorOutput "⚠️  虚拟环境不存在，正在创建..." "Yellow"
    Push-Location web-ui/backend
    python -m venv venv
    Pop-Location
}

# 5. 检查前端依赖
Write-ColorOutput "`n📋 检查前端依赖..." "Yellow"
if (-not (Test-Path "web-ui/node_modules")) {
    Write-ColorOutput "⚠️  前端依赖未安装，正在安装..." "Yellow"
    Push-Location web-ui
    npm install
    Pop-Location
    Write-ColorOutput "✅ 前端依赖安装完成" "Green"
} else {
    Write-ColorOutput "✅ 前端依赖已安装" "Green"
}

# 6. 启动后端服务
Write-ColorOutput "`n🚀 启动后端服务..." "Cyan"
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    Set-Location web-ui/backend
    
    # 激活虚拟环境并启动
    if ($IsWindows -or $env:OS -match "Windows") {
        & .\venv\Scripts\Activate.ps1
    } else {
        & ./venv/bin/Activate.ps1
    }
    
    python app.py
}

Write-ColorOutput "✅ 后端服务启动中... (Job ID: $($backendJob.Id))" "Green"
Write-ColorOutput "   后端地址: http://localhost:5000" "Gray"

# 等待后端启动
Write-ColorOutput "`n⏳ 等待后端服务启动..." "Yellow"
Start-Sleep -Seconds 5

# 检查后端是否启动成功
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/api/health" -TimeoutSec 5 -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        Write-ColorOutput "✅ 后端服务启动成功" "Green"
    }
} catch {
    Write-ColorOutput "⚠️  后端服务可能还在启动中..." "Yellow"
}

# 7. 启动前端服务
Write-ColorOutput "`n🚀 启动前端服务..." "Cyan"
$frontendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    Set-Location web-ui
    npm run dev
}

Write-ColorOutput "✅ 前端服务启动中... (Job ID: $($frontendJob.Id))" "Green"
Write-ColorOutput "   前端地址: http://localhost:5173" "Gray"

# 等待前端启动
Write-ColorOutput "`n⏳ 等待前端服务启动..." "Yellow"
Start-Sleep -Seconds 8

# 8. 显示启动信息
Write-ColorOutput "`n========================================" "Cyan"
Write-ColorOutput "  🎉 服务启动完成！" "Green"
Write-ColorOutput "========================================" "Cyan"
Write-ColorOutput "`n📍 访问地址:" "White"
Write-ColorOutput "   前端: http://localhost:5173" "Cyan"
Write-ColorOutput "   后端: http://localhost:5000" "Cyan"
Write-ColorOutput "`n📊 后台任务:" "White"
Write-ColorOutput "   后端 Job ID: $($backendJob.Id)" "Gray"
Write-ColorOutput "   前端 Job ID: $($frontendJob.Id)" "Gray"
Write-ColorOutput "`n💡 提示:" "White"
Write-ColorOutput "   - 按 Ctrl+C 停止此脚本" "Gray"
Write-ColorOutput "   - 查看后端日志: Receive-Job $($backendJob.Id)" "Gray"
Write-ColorOutput "   - 查看前端日志: Receive-Job $($frontendJob.Id)" "Gray"
Write-ColorOutput "   - 停止所有服务: Stop-Job $($backendJob.Id),$($frontendJob.Id); Remove-Job $($backendJob.Id),$($frontendJob.Id)" "Gray"
Write-ColorOutput "`n========================================`n" "Cyan"

# 9. 保持脚本运行并显示日志
Write-ColorOutput "📝 实时日志 (按 Ctrl+C 退出):`n" "Yellow"

try {
    while ($true) {
        # 显示后端日志
        $backendOutput = Receive-Job -Job $backendJob -ErrorAction SilentlyContinue
        if ($backendOutput) {
            Write-Host "[后端] " -ForegroundColor Blue -NoNewline
            Write-Host $backendOutput
        }
        
        # 显示前端日志
        $frontendOutput = Receive-Job -Job $frontendJob -ErrorAction SilentlyContinue
        if ($frontendOutput) {
            Write-Host "[前端] " -ForegroundColor Magenta -NoNewline
            Write-Host $frontendOutput
        }
        
        # 检查任务状态
        if ($backendJob.State -eq "Failed" -or $backendJob.State -eq "Stopped") {
            Write-ColorOutput "`n❌ 后端服务已停止" "Red"
            break
        }
        if ($frontendJob.State -eq "Failed" -or $frontendJob.State -eq "Stopped") {
            Write-ColorOutput "`n❌ 前端服务已停止" "Red"
            break
        }
        
        Start-Sleep -Milliseconds 500
    }
} finally {
    # 清理
    Write-ColorOutput "`n🛑 正在停止服务..." "Yellow"
    Stop-Job -Job $backendJob, $frontendJob -ErrorAction SilentlyContinue
    Remove-Job -Job $backendJob, $frontendJob -Force -ErrorAction SilentlyContinue
    Write-ColorOutput "✅ 服务已停止" "Green"
}
