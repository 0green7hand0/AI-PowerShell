# GitHub Release 创建脚本
# 使用 GitHub API 创建 v1.1.0 Release

param(
    [string]$Token = $env:GITHUB_TOKEN,
    [string]$Owner = "0green7hand0",
    [string]$Repo = "AI-PowerShell",
    [string]$Tag = "v1.1.0"
)

# 检查 GitHub Token
if (-not $Token) {
    Write-Host "❌ 错误: 需要设置 GITHUB_TOKEN 环境变量" -ForegroundColor Red
    Write-Host "请先设置: `$env:GITHUB_TOKEN = 'your_github_token'" -ForegroundColor Yellow
    exit 1
}

# 读取 Release Notes
$releaseNotesFile = "v1.1.0-Release-Notes.md"
if (-not (Test-Path $releaseNotesFile)) {
    Write-Host "❌ 错误: 找不到 $releaseNotesFile 文件" -ForegroundColor Red
    exit 1
}

$releaseNotes = Get-Content $releaseNotesFile -Raw -Encoding UTF8

# 准备 API 请求数据
$releaseData = @{
    tag_name = $Tag
    target_commitish = "main"
    name = "🎉 AI PowerShell 智能助手 v1.1.0 - 双版本完整发布"
    body = $releaseNotes
    draft = $false
    prerelease = $false
} | ConvertTo-Json -Depth 10

# GitHub API URL
$apiUrl = "https://api.github.com/repos/$Owner/$Repo/releases"

# 设置请求头
$headers = @{
    "Authorization" = "token $Token"
    "Accept" = "application/vnd.github.v3+json"
    "User-Agent" = "PowerShell-Script"
}

Write-Host "🚀 正在创建 GitHub Release..." -ForegroundColor Green
Write-Host "📍 仓库: $Owner/$Repo" -ForegroundColor Cyan
Write-Host "🏷️  标签: $Tag" -ForegroundColor Cyan

try {
    # 发送 API 请求
    $response = Invoke-RestMethod -Uri $apiUrl -Method Post -Headers $headers -Body $releaseData -ContentType "application/json"
    
    Write-Host "✅ GitHub Release 创建成功!" -ForegroundColor Green
    Write-Host "🔗 Release URL: $($response.html_url)" -ForegroundColor Yellow
    Write-Host "📦 下载链接:" -ForegroundColor Cyan
    Write-Host "   ZIP: $($response.zipball_url)" -ForegroundColor White
    Write-Host "   TAR: $($response.tarball_url)" -ForegroundColor White
    
    # 打开浏览器查看 Release
    Start-Process $response.html_url
    
} catch {
    Write-Host "❌ 创建 Release 失败:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $errorResponse = $_.Exception.Response.GetResponseStream()
        $reader = New-Object System.IO.StreamReader($errorResponse)
        $errorBody = $reader.ReadToEnd()
        Write-Host "错误详情: $errorBody" -ForegroundColor Red
    }
    exit 1
}