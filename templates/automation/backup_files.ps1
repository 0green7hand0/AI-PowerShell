<#
.SYNOPSIS
    文件备份模板
    
.DESCRIPTION
    自动备份指定文件夹到目标位置，支持增量备份
    
.TEMPLATE_PARAMETERS
    {{SOURCE_PATH}} - 源文件夹路径
    {{BACKUP_PATH}} - 备份目标路径
    {{INCLUDE_SUBFOLDERS}} - 是否包含子文件夹（true/false）
    {{COMPRESS}} - 是否压缩备份（true/false）
    {{KEEP_VERSIONS}} - 保留的备份版本数
    {{EXCLUDE_PATTERNS}} - 排除的文件模式（逗号分隔）
    
.EXAMPLE
    用户需求：每天备份文档文件夹到D盘
    AI 修改后：
    - SOURCE_PATH = "$env:USERPROFILE\Documents"
    - BACKUP_PATH = "D:\Backups"
    - COMPRESS = true
    - KEEP_VERSIONS = 7
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$SourcePath = "{{SOURCE_PATH}}",
    
    [Parameter(Mandatory=$false)]
    [string]$BackupPath = "{{BACKUP_PATH}}",
    
    [Parameter(Mandatory=$false)]
    [bool]$IncludeSubfolders = ${{INCLUDE_SUBFOLDERS}},
    
    [Parameter(Mandatory=$false)]
    [bool]$Compress = ${{COMPRESS}},
    
    [Parameter(Mandatory=$false)]
    [int]$KeepVersions = {{KEEP_VERSIONS}},
    
    [Parameter(Mandatory=$false)]
    [string]$ExcludePatterns = "{{EXCLUDE_PATTERNS}}"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "文件备份工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查源路径
if (-not (Test-Path $SourcePath)) {
    Write-Host "错误: 源路径不存在: $SourcePath" -ForegroundColor Red
    exit 1
}

# 创建备份目录
if (-not (Test-Path $BackupPath)) {
    Write-Host "创建备份目录: $BackupPath" -ForegroundColor Yellow
    New-Item -Path $BackupPath -ItemType Directory -Force | Out-Null
}

# 生成备份名称
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$sourceName = Split-Path $SourcePath -Leaf
$backupName = "${sourceName}_${timestamp}"

Write-Host "备份配置:" -ForegroundColor White
Write-Host "  源路径: $SourcePath" -ForegroundColor White
Write-Host "  备份路径: $BackupPath" -ForegroundColor White
Write-Host "  备份名称: $backupName" -ForegroundColor White
Write-Host "  包含子文件夹: $IncludeSubfolders" -ForegroundColor White
Write-Host "  压缩备份: $Compress" -ForegroundColor White
Write-Host "  保留版本数: $KeepVersions" -ForegroundColor White
Write-Host ""

# 解析排除模式
$excludeList = @()
if ($ExcludePatterns -and $ExcludePatterns -ne "{{EXCLUDE_PATTERNS}}") {
    $excludeList = $ExcludePatterns -split ','
    Write-Host "排除模式:" -ForegroundColor Yellow
    foreach ($pattern in $excludeList) {
        Write-Host "  - $pattern" -ForegroundColor White
    }
    Write-Host ""
}

# 确认执行
$confirmation = Read-Host "是否开始备份? (y/N)"
if ($confirmation -ne 'y' -and $confirmation -ne 'Y') {
    Write-Host "操作已取消" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "开始备份..." -ForegroundColor Yellow

try {
    if ($Compress) {
        # 压缩备份
        $zipPath = Join-Path $BackupPath "$backupName.zip"
        
        Write-Host "正在压缩文件..." -ForegroundColor Yellow
        
        # 使用 .NET 压缩
        Add-Type -AssemblyName System.IO.Compression.FileSystem
        
        if ($IncludeSubfolders) {
            [System.IO.Compression.ZipFile]::CreateFromDirectory($SourcePath, $zipPath)
        } else {
            # 只压缩顶层文件
            $tempFolder = Join-Path $env:TEMP "backup_temp_$timestamp"
            New-Item -Path $tempFolder -ItemType Directory -Force | Out-Null
            
            Get-ChildItem -Path $SourcePath -File | ForEach-Object {
                Copy-Item $_.FullName -Destination $tempFolder
            }
            
            [System.IO.Compression.ZipFile]::CreateFromDirectory($tempFolder, $zipPath)
            Remove-Item $tempFolder -Recurse -Force
        }
        
        $backupSize = (Get-Item $zipPath).Length / 1MB
        Write-Host "✓ 备份完成: $zipPath" -ForegroundColor Green
        Write-Host "  大小: $([Math]::Round($backupSize, 2)) MB" -ForegroundColor White
    }
    else {
        # 文件夹备份
        $targetPath = Join-Path $BackupPath $backupName
        
        Write-Host "正在复制文件..." -ForegroundColor Yellow
        
        if ($IncludeSubfolders) {
            Copy-Item -Path $SourcePath -Destination $targetPath -Recurse -Force
        } else {
            New-Item -Path $targetPath -ItemType Directory -Force | Out-Null
            Get-ChildItem -Path $SourcePath -File | ForEach-Object {
                Copy-Item $_.FullName -Destination $targetPath -Force
            }
        }
        
        $fileCount = (Get-ChildItem -Path $targetPath -Recurse -File).Count
        Write-Host "✓ 备份完成: $targetPath" -ForegroundColor Green
        Write-Host "  文件数: $fileCount" -ForegroundColor White
    }
    
    # 清理旧备份
    if ($KeepVersions -gt 0) {
        Write-Host ""
        Write-Host "清理旧备份..." -ForegroundColor Yellow
        
        $pattern = if ($Compress) { "${sourceName}_*.zip" } else { "${sourceName}_*" }
        $backups = Get-ChildItem -Path $BackupPath -Filter $pattern | Sort-Object LastWriteTime -Descending
        
        if ($backups.Count -gt $KeepVersions) {
            $toDelete = $backups | Select-Object -Skip $KeepVersions
            
            foreach ($backup in $toDelete) {
                Remove-Item $backup.FullName -Recurse -Force
                Write-Host "✓ 删除旧备份: $($backup.Name)" -ForegroundColor Gray
            }
            
            Write-Host "保留最新 $KeepVersions 个备份" -ForegroundColor Green
        }
    }
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "备份成功!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
}
catch {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "备份失败!" -ForegroundColor Red
    Write-Host "错误: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Cyan
    exit 1
}
