$token = $env:GITHUB_TOKEN
$owner = "0green7hand0"
$repo = "AI-PowerShell"
$tag = "v1.1.0"

$releaseBody = "# AI PowerShell v1.1.0 - Dual Version Release

## Major Updates
**Dual Version Architecture!** Now provides two fully functional versions for different user needs.

### Two Version Options

#### 1. Practical Version (Recommended for Personal Users)
- Simple and efficient: Single file, no complex dependencies
- Fast startup: < 1 second startup time
- Low resource: Only ~20MB memory required
- Ready to use: Download and run immediately

#### 2. Enterprise Version (Recommended for Enterprise Users)
- Enterprise architecture: Complete modular design
- High scalability: Plugin and customization support
- Production ready: Docker/K8s deployment support
- Complete features: Logging, configuration, monitoring

## Core Fixes
- Fixed execution engine interface issues
- Improved PowerShell detection logic
- Optimized Chinese encoding processing
- Enhanced error handling mechanisms

## Quick Start

### Windows Users
``````powershell
git clone https://github.com/0green7hand0/AI-PowerShell.git
cd AI-PowerShell
python 实用版本.py `"显示当前时间`"
``````

### Linux/macOS Users
``````bash
git clone https://github.com/0green7hand0/AI-PowerShell.git
cd AI-PowerShell
python 实用版本.py `"显示当前时间`"
``````

## Usage Examples
``````bash
python 实用版本.py `"显示CPU使用率最高的5个进程`"
python 实用版本.py `"检查磁盘空间使用情况`"
python 实用版本.py `"列出所有正在运行的服务`"
``````

## System Requirements
- Python 3.8+
- PowerShell 5.1+ or PowerShell Core 7+
- Windows 10+, Ubuntu 18.04+, macOS 10.15+

Start using AI PowerShell Assistant v1.1.0 now!"

$releaseData = @{
    tag_name = $tag
    target_commitish = "main"
    name = "AI PowerShell v1.1.0 - Dual Version Release"
    body = $releaseBody
    draft = $false
    prerelease = $false
}

$json = $releaseData | ConvertTo-Json -Depth 10
$apiUrl = "https://api.github.com/repos/$owner/$repo/releases"

$headers = @{
    "Authorization" = "token $token"
    "Accept" = "application/vnd.github.v3+json"
    "User-Agent" = "PowerShell-Script"
}

Write-Host "Creating GitHub Release v1.1.0..." -ForegroundColor Green

try {
    $response = Invoke-RestMethod -Uri $apiUrl -Method Post -Headers $headers -Body $json -ContentType "application/json"
    
    Write-Host "SUCCESS: GitHub Release created!" -ForegroundColor Green
    Write-Host "Release URL: $($response.html_url)" -ForegroundColor Yellow
    Write-Host "Download ZIP: $($response.zipball_url)" -ForegroundColor Cyan
    Write-Host "Download TAR: $($response.tarball_url)" -ForegroundColor Cyan
    
    Start-Process $response.html_url
    
} catch {
    Write-Host "ERROR: Failed to create Release" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}