# 测试在线安装脚本
Write-Host "🧪 测试 AI PowerShell 助手在线安装脚本" -ForegroundColor Blue
Write-Host "=========================================="

# 测试脚本可访问性
Write-Host "📡 测试脚本可访问性..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "https://raw.githubusercontent.com/0green7hand0/AI-PowerShell/main/scripts/install.ps1" -Method Head
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ 安装脚本可正常访问" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ 安装脚本访问失败: $($_.Exception.Message)" -ForegroundColor Red
}

# 测试帮助信息
Write-Host "📖 测试帮助信息..." -ForegroundColor Yellow
try {
    $helpContent = Invoke-WebRequest -Uri "https://raw.githubusercontent.com/0green7hand0/AI-PowerShell/main/scripts/install.ps1" -UseBasicParsing
    if ($helpContent.Content -match "param\(") {
        Write-Host "✅ 脚本参数定义正确" -ForegroundColor Green
    }
    if ($helpContent.Content -match "function.*Help") {
        Write-Host "✅ 帮助函数存在" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ 脚本内容检查失败: $($_.Exception.Message)" -ForegroundColor Red
}

# 测试 Linux 脚本
Write-Host "🐧 测试 Linux 安装脚本..." -ForegroundColor Yellow
try {
    $linuxResponse = Invoke-WebRequest -Uri "https://raw.githubusercontent.com/0green7hand0/AI-PowerShell/main/scripts/install.sh" -Method Head
    if ($linuxResponse.StatusCode -eq 200) {
        Write-Host "✅ Linux 安装脚本可正常访问" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Linux 安装脚本访问失败: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "🎉 在线安装脚本测试完成！" -ForegroundColor Green
Write-Host ""
Write-Host "📋 用户可以使用以下命令安装："
Write-Host "Windows: Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/0green7hand0/AI-PowerShell/main/scripts/install.ps1' -OutFile 'install.ps1'; .\install.ps1"
Write-Host "Linux/macOS: curl -fsSL https://raw.githubusercontent.com/0green7hand0/AI-PowerShell/main/scripts/install.sh | bash"