# Simple GitHub Release Creation
$Token = $env:GITHUB_TOKEN
$Owner = "0green7hand0"
$Repo = "AI-PowerShell"
$Tag = "v1.1.0"

$releaseBody = @"
# 🎉 AI PowerShell 智能助手 v1.1.0 - 双版本完整发布

## 🌟 重大更新
**双版本架构发布！** 现在提供两个完全可用的版本，满足不同用户需求。

### 🚀 两个版本选择

#### 1️⃣ 实用版本 (推荐个人用户)
- ✅ **简单高效**: 单文件，无复杂依赖
- ✅ **快速启动**: < 1秒启动时间  
- ✅ **低资源**: 仅需 ~20MB 内存
- ✅ **开箱即用**: 下载即可使用

#### 2️⃣ 企业版本 (推荐企业用户)
- ✅ **企业架构**: 完整的模块化设计
- ✅ **高扩展性**: 支持插件和自定义
- ✅ **生产就绪**: Docker/K8s 部署支持
- ✅ **完整功能**: 日志、配置、监控

## 🔧 核心修复
- ✅ 修复执行引擎接口问题
- ✅ 改进 PowerShell 检测逻辑
- ✅ 优化中文编码处理
- ✅ 完善错误处理机制

## 🚀 快速开始

### Windows 用户
```powershell
git clone https://github.com/0green7hand0/AI-PowerShell.git
cd AI-PowerShell
python 实用版本.py "显示当前时间"
```

### Linux/macOS 用户
```bash
git clone https://github.com/0green7hand0/AI-PowerShell.git
cd AI-PowerShell
python 实用版本.py "显示当前时间"
```

## 💡 使用示例
```bash
python 实用版本.py "显示CPU使用率最高的5个进程"
python 实用版本.py "检查磁盘空间使用情况"
python 实用版本.py "列出所有正在运行的服务"
```

## 📊 版本对比
| 特性 | 实用版本 | 企业版本 |
|------|----------|----------|
| 启动时间 | < 1秒 | < 3秒 |
| 内存占用 | ~20MB | ~50MB |
| 文件数量 | 1个文件 | 完整架构 |
| 扩展性 | 有限 | 高度可扩展 |

## 🔧 系统要求
- Python 3.8+
- PowerShell 5.1+ 或 PowerShell Core 7+
- Windows 10+, Ubuntu 18.04+, macOS 10.15+

**🎉 立即开始使用 AI PowerShell 智能助手 v1.1.0！**
"@

$releaseData = @{
    tag_name = $Tag
    target_commitish = "main"
    name = "🎉 AI PowerShell 智能助手 v1.1.0 - 双版本完整发布"
    body = $releaseBody
    draft = $false
    prerelease = $false
} | ConvertTo-Json -Depth 10

$apiUrl = "https://api.github.com/repos/$Owner/$Repo/releases"
$headers = @{
    "Authorization" = "token $Token"
    "Accept" = "application/vnd.github.v3+json"
    "User-Agent" = "PowerShell-Script"
}

Write-Host "Creating GitHub Release v1.1.0..." -ForegroundColor Green

try {
    $response = Invoke-RestMethod -Uri $apiUrl -Method Post -Headers $headers -Body $releaseData -ContentType "application/json"
    
    Write-Host "✅ GitHub Release created successfully!" -ForegroundColor Green
    Write-Host "🔗 Release URL: $($response.html_url)" -ForegroundColor Yellow
    Write-Host "📦 Download ZIP: $($response.zipball_url)" -ForegroundColor Cyan
    Write-Host "📦 Download TAR: $($response.tarball_url)" -ForegroundColor Cyan
    
    # Open browser to view the release
    Start-Process $response.html_url
    
} catch {
    Write-Host "❌ Failed to create Release:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $stream = $_.Exception.Response.GetResponseStream()
        $reader = New-Object System.IO.StreamReader($stream)
        $errorBody = $reader.ReadToEnd()
        Write-Host "Error details: $errorBody" -ForegroundColor Red
    }
}