# ============================================
# 此脚本由 AI PowerShell 智能助手生成
# 生成时间: 2025-10-07 12:00:43
# 用户需求: 批量重命名文件
# 基于模板: 批量重命名文件
# ============================================
<#
.SYNOPSIS
    批量重命名文件模板
    
.DESCRIPTION
    这是一个可定制的批量重命名脚本模板
    AI 会根据用户需求自动修改参数
    
.TEMPLATE_PARAMETERS
    "." - 源文件夹路径
    "*.*" - 文件匹配模式（如 *.jpg, *.pdf）
    "file" - 文件名前缀
    $false - 是否包含日期（true/false）
    "yyyyMMdd" - 日期格式（如 yyyyMMdd）
    1 - 起始序号
    3 - 序号位数（如 3 表示 001, 002）
    
.EXAMPLE
    用户需求：把桌面的jpg照片改成 vacation_2025_序号
    AI 修改后：
    - SOURCE_PATH = "$env:USERPROFILE\Desktop"
    - FILE_PATTERN = "*.jpg"
    - NAME_PREFIX = "vacation_2025"
    - START_NUMBER = 1
    - NUMBER_DIGITS = 3
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$SourcePath = ""."",
    
    [Parameter(Mandatory=$false)]
    [string]$FilePattern = ""*.*"",
    
    [Parameter(Mandatory=$false)]
    [string]$NamePrefix = ""file"",
    
    [Parameter(Mandatory=$false)]
    [bool]$UseDate = $$false,
    
    [Parameter(Mandatory=$false)]
    [string]$DateFormat = ""yyyyMMdd"",
    
    [Parameter(Mandatory=$false)]
    [int]$StartNumber = 1,
    
    [Parameter(Mandatory=$false)]
    [int]$NumberDigits = 3
)

# 脚本开始
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "批量重命名文件工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查源路径是否存在
if (-not (Test-Path $SourcePath)) {
    Write-Host "错误: 源路径不存在: $SourcePath" -ForegroundColor Red
    exit 1
}

# 获取所有匹配的文件
Write-Host "正在扫描文件..." -ForegroundColor Yellow
$files = Get-ChildItem -Path $SourcePath -Filter $FilePattern -File

if ($files.Count -eq 0) {
    Write-Host "未找到匹配的文件: $FilePattern" -ForegroundColor Yellow
    exit 0
}

Write-Host "找到 $($files.Count) 个文件" -ForegroundColor Green
Write-Host ""

# 预览重命名
Write-Host "重命名预览:" -ForegroundColor Cyan
Write-Host "----------------------------------------"

$counter = $StartNumber
$previewCount = [Math]::Min(5, $files.Count)

for ($i = 0; $i -lt $previewCount; $i++) {
    $file = $files[$i]
    
    # 构建新文件名
    $newName = $NamePrefix
    
    if ($UseDate) {
        $date = Get-Date -Format $DateFormat
        $newName += "_$date"
    }
    
    $numberStr = $counter.ToString("D$NumberDigits")
    $newName += "_$numberStr$($file.Extension)"
    
    Write-Host "$($file.Name) -> $newName" -ForegroundColor White
    $counter++
}

if ($files.Count -gt $previewCount) {
    Write-Host "... 还有 $($files.Count - $previewCount) 个文件" -ForegroundColor Gray
}

Write-Host "----------------------------------------"
Write-Host ""

# 确认执行
$confirmation = Read-Host "是否继续执行重命名? (y/N)"
if ($confirmation -ne 'y' -and $confirmation -ne 'Y') {
    Write-Host "操作已取消" -ForegroundColor Yellow
    exit 0
}

# 执行重命名
Write-Host ""
Write-Host "开始重命名..." -ForegroundColor Yellow

$counter = $StartNumber
$successCount = 0
$errorCount = 0

foreach ($file in $files) {
    try {
        # 构建新文件名
        $newName = $NamePrefix
        
        if ($UseDate) {
            $date = Get-Date -Format $DateFormat
            $newName += "_$date"
        }
        
        $numberStr = $counter.ToString("D$NumberDigits")
        $newName += "_$numberStr$($file.Extension)"
        
        # 构建完整路径
        $newPath = Join-Path $file.DirectoryName $newName
        
        # 检查目标文件是否已存在
        if (Test-Path $newPath) {
            Write-Host "跳过: $($file.Name) (目标文件已存在)" -ForegroundColor Yellow
            $errorCount++
        } else {
            # 执行重命名
            Rename-Item -Path $file.FullName -NewName $newName -ErrorAction Stop
            Write-Host "✓ $($file.Name) -> $newName" -ForegroundColor Green
            $successCount++
        }
        
        $counter++
    }
    catch {
        Write-Host "✗ 重命名失败: $($file.Name) - $($_.Exception.Message)" -ForegroundColor Red
        $errorCount++
    }
}

# 显示结果
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "重命名完成!" -ForegroundColor Cyan
Write-Host "成功: $successCount 个文件" -ForegroundColor Green
if ($errorCount -gt 0) {
    Write-Host "失败/跳过: $errorCount 个文件" -ForegroundColor Yellow
}
Write-Host "========================================" -ForegroundColor Cyan
