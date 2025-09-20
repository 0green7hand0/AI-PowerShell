# AI PowerShell 助手网址更新脚本 (Windows PowerShell 版本)
# 使用方法: .\scripts\update_urls.ps1 [您的GitHub用户名] [项目名称]

param(
    [Parameter(Mandatory=$false)]
    [string]$GitHubUser,
    
    [Parameter(Mandatory=$false)]
    [string]$ProjectName,
    
    [switch]$Help
)

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

function Write-Info {
    param([string]$Message)
    Write-ColorOutput "[INFO] $Message" "Blue"
}

function Write-Success {
    param([string]$Message)
    Write-ColorOutput "[SUCCESS] $Message" "Green"
}

function Write-Warning {
    param([string]$Message)
    Write-ColorOutput "[WARNING] $Message" "Yellow"
}

function Write-Error {
    param([string]$Message)
    Write-ColorOutput "[ERROR] $Message" "Red"
}

# 显示帮助信息
function Show-Help {
    Write-Host @"
AI PowerShell 助手网址更新脚本

使用方法:
  .\scripts\update_urls.ps1 [GitHub用户名] [项目名称]

示例:
  .\scripts\update_urls.ps1 myusername ai-powershell-assistant
  .\scripts\update_urls.ps1 mycompany powershell-ai-helper

参数说明:
  GitHub用户名: 您的 GitHub 用户名或组织名
  项目名称:     您的项目仓库名称

选项:
  -Help         显示此帮助信息

注意:
  - 此脚本会更新所有文档中的占位符网址
  - 建议在运行前备份项目文件
  - 运行后请检查更新结果

"@
}

# 检查参数
if ($Help -or (-not $GitHubUser) -or (-not $ProjectName)) {
    Show-Help
    exit 0
}

# 验证参数格式
if ($GitHubUser -notmatch '^[a-zA-Z0-9_-]+$') {
    Write-Error "GitHub用户名格式不正确: $GitHubUser"
    exit 1
}

if ($ProjectName -notmatch '^[a-zA-Z0-9_-]+$') {
    Write-Error "项目名称格式不正确: $ProjectName"
    exit 1
}

# 定义新的网址
$NewRepoUrl = "https://github.com/$GitHubUser/$ProjectName.git"
$NewRawUrl = "https://raw.githubusercontent.com/$GitHubUser/$ProjectName/main"
$NewIssuesUrl = "https://github.com/$GitHubUser/$ProjectName/issues"
$NewDiscussionsUrl = "https://github.com/$GitHubUser/$ProjectName/discussions"
$NewDocsUrl = "https://github.com/$GitHubUser/$ProjectName/docs"

Write-Info "开始更新项目网址..."
Write-Info "GitHub用户: $GitHubUser"
Write-Info "项目名称: $ProjectName"
Write-Info "新仓库地址: $NewRepoUrl"

# 创建备份目录
$BackupDir = "backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
Write-Info "创建备份目录: $BackupDir"
New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null

# 需要更新的文件列表
$FilesToUpdate = @(
    "README.md",
    "中文项目说明.md",
    "learning\中文学习指南.md",
    "docs\user\installation.md",
    "docs\faq\README.md",
    "scripts\install.sh",
    "scripts\install.ps1",
    "setup.py"
)

# 备份文件
foreach ($file in $FilesToUpdate) {
    if (Test-Path $file) {
        Copy-Item $file $BackupDir
        Write-Info "已备份: $file"
    }
}

# 更新文件函数
function Update-File {
    param([string]$FilePath)
    
    if (-not (Test-Path $FilePath)) {
        Write-Warning "文件不存在，跳过: $FilePath"
        return
    }
    
    Write-Info "更新文件: $FilePath"
    
    try {
        $content = Get-Content $FilePath -Raw -Encoding UTF8
        
        # 替换占位符网址
        $content = $content -replace 'https://github\.com/your-org/ai-powershell-assistant\.git', $NewRepoUrl
        $content = $content -replace 'https://raw\.githubusercontent\.com/your-org/ai-powershell-assistant/main', $NewRawUrl
        $content = $content -replace 'https://github\.com/your-org/ai-powershell-assistant/issues', $NewIssuesUrl
        $content = $content -replace 'https://github\.com/your-org/ai-powershell-assistant/discussions', $NewDiscussionsUrl
        $content = $content -replace 'https://github\.com/your-org/ai-powershell-assistant/docs', $NewDocsUrl
        $content = $content -replace 'https://github\.com/your-org/ai-powershell-assistant', "https://github.com/$GitHubUser/$ProjectName"
        
        # 保存更新后的内容
        Set-Content $FilePath $content -Encoding UTF8
    }
    catch {
        Write-Error "更新文件失败: $FilePath - $($_.Exception.Message)"
    }
}

# 更新所有文件
foreach ($file in $FilesToUpdate) {
    Update-File $file
}

# 验证更新结果
Write-Info "验证更新结果..."
$RemainingPlaceholders = 0

foreach ($file in $FilesToUpdate) {
    if (Test-Path $file) {
        $content = Get-Content $file -Raw
        if ($content -match 'your-org/ai-powershell-assistant') {
            $RemainingPlaceholders++
            Write-Warning "文件 $file 中仍有占位符未更新"
        }
    }
}

if ($RemainingPlaceholders -eq 0) {
    Write-Success "所有占位符网址已成功更新！"
} else {
    Write-Warning "仍有 $RemainingPlaceholders 个文件包含未更新的占位符，请手动检查"
}

# 显示更新摘要
Write-Success "网址更新完成！"
Write-Host ""
Write-Host "更新摘要:"
Write-Host "  GitHub用户: $GitHubUser"
Write-Host "  项目名称: $ProjectName"
Write-Host "  新仓库地址: $NewRepoUrl"
Write-Host "  备份目录: $BackupDir"
Write-Host ""
Write-Host "下一步操作:"
Write-Host "1. 检查更新后的文件内容"
Write-Host "2. 测试安装脚本是否正常工作"
Write-Host "3. 提交更改到Git仓库"
Write-Host "4. 如有问题，可从备份目录恢复文件"

Write-Info "更新脚本执行完成！"