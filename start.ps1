#!/usr/bin/env pwsh
# AI PowerShell 智能助手 - 启动脚本 (Windows/PowerShell)
# 自动检测并启动所有必要的服务

$ErrorActionPreference = "Stop"

# 颜色输出函数
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Write-Success { param([string]$Message) Write-ColorOutput "✓ $Message" "Green" }
function Write-Error { param([string]$Message) Write-ColorOutput "✗ $Message" "Red" }
function Write-Warning { param([string]$Message) Write-ColorOutput "⚠ $Message" "Yellow" }
function Write-Info { param([string]$Message) Write-ColorOutput "ℹ $Message" "Cyan" }

# 显示标题
Write-Host ""
Write-ColorOutput "╔════════════════════════════════════════════════╗" "Cyan"
Write-ColorOutput "║   AI PowerShell 智能助手 - 启动检测脚本       ║" "Cyan"
Write-ColorOutput "╚════════════════════════════════════════════════╝" "Cyan"
Write-Host ""

# 1. 检查 Python
Write-Info "检查 Python 环境..."
try {
    $pythonVersion = python --version 2>&1
    Write-Success "Python 已安装: $pythonVersion"
} catch {
    Write-Error "Python 未安装或不在 PATH 中"
    Write-Warning "请安装 Python 3.8+ 后重试"
    exit 1
}

# 2. 检查 Node.js (用于 Web UI)
Write-Info "检查 Node.js 环境..."
try {
    $nodeVersion = node --version 2>&1
    Write-Success "Node.js 已安装: $nodeVersion"
} catch {
    Write-Warning "Node.js 未安装，Web UI 将无法启动"
    $skipWebUI = $true
}

# 3. 检查 Ollama 服务
Write-Info "检查 Ollama AI 服务..."
try {
    $ollamaResponse = Invoke-WebRequest -Uri "http://localhost:11434/api/version" -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
    $ollamaVersion = ($ollamaResponse.Content | ConvertFrom-Json).version
    Write-Success "Ollama 服务运行中 (版本: $ollamaVersion)"
    
    # 检查模型
    Write-Info "检查已安装的 AI 模型..."
    $modelsResponse = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing -ErrorAction Stop
    $models = ($modelsResponse.Content | ConvertFrom-Json).models
    
    if ($models.Count -gt 0) {
        Write-Success "已安装 $($models.Count) 个模型:"
        foreach ($model in $models) {
            $sizeGB = [math]::Round($model.size / 1GB, 2)
            Write-Host "  • $($model.name) ($sizeGB GB)" -ForegroundColor Gray
        }
        
        # 检查配置的模型是否存在
        $configModel = "qwen3:30b"
        $modelExists = $models | Where-Object { $_.name -eq $configModel }
        if ($modelExists) {
            Write-Success "配置的模型 '$configModel' 已就绪"
        } else {
            Write-Warning "配置的模型 '$configModel' 未找到"
            Write-Info "可用模型: $($models.name -join ', ')"
        }
    } else {
        Write-Warning "未安装任何模型，请先安装模型"
        Write-Info "示例: ollama pull qwen3:30b"
    }
} catch {
    Write-Error "Ollama 服务未运行"
    Write-Warning "请先启动 Ollama 服务"
    Write-Info "Windows: 从开始菜单启动 Ollama"
    Write-Info "或访问: https://ollama.ai/download"
    
    $response = Read-Host "是否继续启动项目? (y/n)"
    if ($response -ne "y") {
        exit 1
    }
}

Write-Host ""
Write-ColorOutput "════════════════════════════════════════════════" "Cyan"
Write-Host ""

# 4. 询问启动模式
Write-Info "请选择启动模式:"
Write-Host "  1. 仅启动命令行界面 (CLI)"
Write-Host "  2. 仅启动 Web 界面"
Write-Host "  3. 同时启动 CLI 和 Web 界面"
Write-Host ""

$choice = Read-Host "请输入选项 (1-3)"

switch ($choice) {
    "1" {
        # 启动 CLI
        Write-Info "启动命令行界面..."
        python run.py
    }
    "2" {
        if ($skipWebUI) {
            Write-Error "Node.js 未安装，无法启动 Web UI"
            exit 1
        }
        
        # 检查依赖
        Write-Info "检查 Web UI 依赖..."
        if (-not (Test-Path "web-ui/node_modules")) {
            Write-Warning "Web UI 依赖未安装，正在安装..."
            Set-Location web-ui
            npm install
            Set-Location ..
        }
        
        # 启动后端
        Write-Info "启动后端服务..."
        Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd web-ui/backend; python app.py"
        Start-Sleep -Seconds 3
        
        # 启动前端
        Write-Info "启动前端服务..."
        Set-Location web-ui
        npm run dev
    }
    "3" {
        if ($skipWebUI) {
            Write-Error "Node.js 未安装，无法启动 Web UI"
            Write-Info "将仅启动 CLI 模式"
            python run.py
            exit 0
        }
        
        # 检查依赖
        Write-Info "检查 Web UI 依赖..."
        if (-not (Test-Path "web-ui/node_modules")) {
            Write-Warning "Web UI 依赖未安装，正在安装..."
            Set-Location web-ui
            npm install
            Set-Location ..
        }
        
        # 启动后端
        Write-Info "启动后端服务..."
        Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd web-ui/backend; python app.py"
        Start-Sleep -Seconds 3
        
        # 启动前端
        Write-Info "启动前端服务..."
        Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd web-ui; npm run dev"
        Start-Sleep -Seconds 3
        
        # 启动 CLI
        Write-Info "启动命令行界面..."
        python run.py
    }
    default {
        Write-Error "无效的选项"
        exit 1
    }
}
