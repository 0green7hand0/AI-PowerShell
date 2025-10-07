<#
.SYNOPSIS
    文件分类整理模板
    
.DESCRIPTION
    按文件类型自动分类整理文件到不同文件夹
    
.TEMPLATE_PARAMETERS
    {{SOURCE_PATH}} - 源文件夹路径
    {{CREATE_SUBFOLDERS}} - 是否创建子文件夹（true/false）
    {{MOVE_FILES}} - 移动还是复制文件（move/copy）
    
.EXAMPLE
    用户需求：整理下载文件夹，按类型分类
    AI 修改后：
    - SOURCE_PATH = "$env:USERPROFILE\Downloads"
    - CREATE_SUBFOLDERS = true
    - MOVE_FILES = "move"
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$SourcePath = "{{SOURCE_PATH}}",
    
    [Parameter(Mandatory=$false)]
    [bool]$CreateSubfolders = ${{CREATE_SUBFOLDERS}},
    
    [Parameter(Mandatory=$false)]
    [ValidateSet("move", "copy")]
    [string]$Operation = "{{MOVE_FILES}}"
)

# 文件类型分类规则
$fileCategories = @{
    "图片" = @(".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico")
    "文档" = @(".doc", ".docx", ".pdf", ".txt", ".rtf", ".odt", ".xls", ".xlsx", ".ppt", ".pptx")
    "视频" = @(".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm")
    "音频" = @(".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a")
    "压缩包" = @(".zip", ".rar", ".7z", ".tar", ".gz", ".bz2")
    "程序" = @(".exe", ".msi", ".dmg", ".app", ".deb", ".rpm")
    "代码" = @(".py", ".js", ".java", ".cpp", ".c", ".cs", ".php", ".html", ".css", ".json", ".xml")
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "文件分类整理工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查源路径
if (-not (Test-Path $SourcePath)) {
    Write-Host "错误: 源路径不存在: $SourcePath" -ForegroundColor Red
    exit 1
}

Write-Host "源文件夹: $SourcePath" -ForegroundColor White
Write-Host "操作模式: $Operation" -ForegroundColor White
Write-Host ""

# 获取所有文件
Write-Host "正在扫描文件..." -ForegroundColor Yellow
$files = Get-ChildItem -Path $SourcePath -File

if ($files.Count -eq 0) {
    Write-Host "文件夹为空" -ForegroundColor Yellow
    exit 0
}

Write-Host "找到 $($files.Count) 个文件" -ForegroundColor Green
Write-Host ""

# 分析文件分布
$fileStats = @{}
foreach ($file in $files) {
    $ext = $file.Extension.ToLower()
    $category = "其他"
    
    foreach ($cat in $fileCategories.Keys) {
        if ($fileCategories[$cat] -contains $ext) {
            $category = $cat
            break
        }
    }
    
    if (-not $fileStats.ContainsKey($category)) {
        $fileStats[$category] = 0
    }
    $fileStats[$category]++
}

# 显示统计
Write-Host "文件分布统计:" -ForegroundColor Cyan
Write-Host "----------------------------------------"
foreach ($category in $fileStats.Keys | Sort-Object) {
    Write-Host "$category : $($fileStats[$category]) 个文件" -ForegroundColor White
}
Write-Host "----------------------------------------"
Write-Host ""

# 确认执行
$confirmation = Read-Host "是否继续整理文件? (y/N)"
if ($confirmation -ne 'y' -and $confirmation -ne 'Y') {
    Write-Host "操作已取消" -ForegroundColor Yellow
    exit 0
}

# 创建分类文件夹
Write-Host ""
Write-Host "创建分类文件夹..." -ForegroundColor Yellow

foreach ($category in $fileStats.Keys) {
    $categoryPath = Join-Path $SourcePath $category
    if (-not (Test-Path $categoryPath)) {
        New-Item -Path $categoryPath -ItemType Directory -Force | Out-Null
        Write-Host "✓ 创建文件夹: $category" -ForegroundColor Green
    }
}

# 整理文件
Write-Host ""
Write-Host "开始整理文件..." -ForegroundColor Yellow

$successCount = 0
$errorCount = 0

foreach ($file in $files) {
    try {
        $ext = $file.Extension.ToLower()
        $category = "其他"
        
        # 确定分类
        foreach ($cat in $fileCategories.Keys) {
            if ($fileCategories[$cat] -contains $ext) {
                $category = $cat
                break
            }
        }
        
        # 目标路径
        $targetFolder = Join-Path $SourcePath $category
        $targetPath = Join-Path $targetFolder $file.Name
        
        # 检查目标文件是否已存在
        if (Test-Path $targetPath) {
            Write-Host "跳过: $($file.Name) (目标位置已存在)" -ForegroundColor Yellow
            $errorCount++
            continue
        }
        
        # 执行操作
        if ($Operation -eq "move") {
            Move-Item -Path $file.FullName -Destination $targetPath -ErrorAction Stop
            Write-Host "✓ 移动: $($file.Name) -> $category/" -ForegroundColor Green
        } else {
            Copy-Item -Path $file.FullName -Destination $targetPath -ErrorAction Stop
            Write-Host "✓ 复制: $($file.Name) -> $category/" -ForegroundColor Green
        }
        
        $successCount++
    }
    catch {
        Write-Host "✗ 处理失败: $($file.Name) - $($_.Exception.Message)" -ForegroundColor Red
        $errorCount++
    }
}

# 显示结果
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "整理完成!" -ForegroundColor Cyan
Write-Host "成功: $successCount 个文件" -ForegroundColor Green
if ($errorCount -gt 0) {
    Write-Host "失败/跳过: $errorCount 个文件" -ForegroundColor Yellow
}
Write-Host "========================================" -ForegroundColor Cyan
