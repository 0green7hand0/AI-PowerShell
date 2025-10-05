# AI PowerShell 助手 GitHub 上传脚本 (Windows PowerShell 版本)

# 颜色函数
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    
    $colorMap = @{
        "Red" = "Red"
        "Green" = "Green"
        "Yellow" = "Yellow"
        "Blue" = "Blue"
        "White" = "White"
    }
    
    Write-Host $Message -ForegroundColor $colorMap[$Color]
}

Write-ColorOutput "🚀 AI PowerShell 助手 GitHub 上传脚本" "Blue"
Write-Host "=================================="

# 检查是否在正确的目录
if (-not (Test-Path "中文项目说明.md")) {
    Write-ColorOutput "❌ 错误：请在项目根目录运行此脚本" "Red"
    exit 1
}

# 检查 Git 状态
if (-not (Test-Path ".git")) {
    Write-ColorOutput "📁 初始化 Git 仓库..." "Yellow"
    git init
}

# 添加所有文件
Write-ColorOutput "📝 添加文件到 Git..." "Yellow"
git add .

# 检查是否有更改
$hasChanges = git diff --cached --quiet
if ($LASTEXITCODE -eq 0) {
    Write-ColorOutput "⚠️ 没有检测到文件更改" "Yellow"
} else {
    # 创建提交
    Write-ColorOutput "💾 创建提交..." "Yellow"
    git commit -m "🎉 AI PowerShell 智能助手完整项目

✨ 功能特性：
- 🤖 中文自然语言到 PowerShell 命令转换
- 🔒 三层安全保护（白名单+权限+沙箱）
- 🌐 跨平台支持（Windows/Linux/macOS）
- 📊 完整的审计日志和性能监控
- 🐳 Docker 和 Kubernetes 部署支持
- 📚 完整的中文文档和使用示例

🏗️ 项目结构：
- src/ - 核心源代码（6大组件）
- docs/ - 完整文档系统
- examples/ - 中文使用示例
- config/ - 配置模板和说明
- scripts/ - 安装和部署脚本
- k8s/ - Kubernetes 部署配置

📊 项目统计：
- 总文件数: 100+ 个文件
- 代码行数: 10,000+ 行
- 文档页数: 50+ 页中文文档
- 测试文件: 30+ 个测试文件"
}

# 检查远程仓库
try {
    git remote get-url origin | Out-Null
} catch {
    Write-ColorOutput "🔗 添加远程仓库..." "Yellow"
    git remote add origin https://github.com/0green7hand0/AI-PowerShell.git
}

# 设置主分支
Write-ColorOutput "🌿 设置主分支..." "Yellow"
git branch -M main

# 推送到 GitHub
Write-ColorOutput "📤 推送到 GitHub..." "Yellow"
Write-ColorOutput "正在上传到: https://github.com/0green7hand0/AI-PowerShell" "Blue"

try {
    git push -u origin main
    
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "✅ 上传成功！" "Green"
        Write-Host ""
        Write-ColorOutput "🎉 项目已成功上传到 GitHub！" "Green"
        Write-Host ""
        Write-Host "📋 下一步操作："
        Write-Host "1. 访问 https://github.com/0green7hand0/AI-PowerShell 查看项目"
        Write-Host "2. 添加项目描述和标签"
        Write-Host "3. 测试在线安装脚本"
        Write-Host "4. 创建第一个 Release"
        Write-Host ""
        Write-Host "🔗 项目链接："
        Write-Host "- 仓库地址: https://github.com/0green7hand0/AI-PowerShell"
        Write-Host "- 问题报告: https://github.com/0green7hand0/AI-PowerShell/issues"
        Write-Host "- 讨论交流: https://github.com/0green7hand0/AI-PowerShell/discussions"
        Write-Host ""
        Write-Host "🚀 现在用户可以使用以下命令安装："
        Write-Host "git clone https://github.com/0green7hand0/AI-PowerShell.git"
    } else {
        throw "Push failed"
    }
} catch {
    Write-ColorOutput "❌ 上传失败" "Red"
    Write-Host ""
    Write-Host "可能的原因："
    Write-Host "1. 网络连接问题"
    Write-Host "2. GitHub 认证问题"
    Write-Host "3. 仓库权限问题"
    Write-Host ""
    Write-Host "解决方案："
    Write-Host "1. 检查网络连接"
    Write-Host "2. 配置 GitHub 认证: git config --global user.name 'Your Name'"
    Write-Host "3. 配置 GitHub 邮箱: git config --global user.email 'your.email@example.com'"
    Write-Host "4. 设置 GitHub Token 或 SSH 密钥"
    exit 1
}