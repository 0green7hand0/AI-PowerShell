<#
.SYNOPSIS
    简单文件备份工具
    
.DESCRIPTION
    将指定目录的文件备份到目标位置，支持增量备份和压缩
    
.TEMPLATE_PARAMETERS
    {{SOURCE_PATH}} - 源文件夹路径
    {{DEST_PATH}} - 备份目标路径
    {{COMPRESS}} - 是否压缩备份
    {{INCREMENTAL}} - 是否增量备份
    
.EXAMPLE
    帮我创建一个备份脚本，备份我的文档到D盘
    
.NOTES
    这是一个自定义模板示例
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$SourcePath = "{{SOURCE_PATH}}",
    
    [Parameter(Mandatory=$true)]
    [string]$DestPath = "{{DEST_PATH}}",
    
    [Parameter(Mandatory=$false)]
    [bool]$Compress = ${{COMPRESS}},
    
    [Parameter(Mandatory=$false)]
    [bool]$Incremental = ${{INCREMENTAL}}
)

# 验证源路径
if (-not (Test-Path $SourcePath)) {
    Write-Error "源路径不存在: $SourcePath"
    exit 1
}

# 创建目标目录
if (-not (Test-Path $DestPath)) {
    New-Item -ItemType Directory -Path $DestPath -Force | Out-Null
    Write-Host "✓ 创建目标目录: $DestPath" -ForegroundColor Green
}

# 生成备份文件名
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupName = "backup_$timestamp"

if ($Compress) {
    # 压缩备份
    $zipPath = Join-Path $DestPath "$backupName.zip"
    Write-Host "开始压缩备份..." -ForegroundColor Cyan
    
    Compress-Archive -Path $SourcePath -DestinationPath $zipPath -Force
    
    $zipSize = (Get-Item $zipPath).Length / 1MB
    Write-Host "✓ 备份完成: $zipPath" -ForegroundColor Green
    Write-Host "  大小: $([math]::Round($zipSize, 2)) MB" -ForegroundColor Gray
} else {
    # 直接复制
    $backupPath = Join-Path $DestPath $backupName
    Write-Host "开始复制文件..." -ForegroundColor Cyan
    
    if ($Incremental) {
        # 增量备份：只复制新文件或修改过的文件
        $sourceFiles = Get-ChildItem -Path $SourcePath -Recurse -File
        $copiedCount = 0
        
        foreach ($file in $sourceFiles) {
            $relativePath = $file.FullName.Substring($SourcePath.Length)
            $destFile = Join-Path $backupPath $relativePath
            
            # 检查文件是否需要复制
            $needCopy = $false
            if (-not (Test-Path $destFile)) {
                $needCopy = $true
            } elseif ($file.LastWriteTime -gt (Get-Item $destFile).LastWriteTime) {
                $needCopy = $true
            }
            
            if ($needCopy) {
                $destDir = Split-Path $destFile -Parent
                if (-not (Test-Path $destDir)) {
                    New-Item -ItemType Directory -Path $destDir -Force | Out-Null
                }
                Copy-Item -Path $file.FullName -Destination $destFile -Force
                $copiedCount++
            }
        }
        
        Write-Host "✓ 增量备份完成: $backupPath" -ForegroundColor Green
        Write-Host "  复制文件数: $copiedCount" -ForegroundColor Gray
    } else {
        # 完整备份
        Copy-Item -Path $SourcePath -Destination $backupPath -Recurse -Force
        
        $fileCount = (Get-ChildItem -Path $backupPath -Recurse -File).Count
        Write-Host "✓ 完整备份完成: $backupPath" -ForegroundColor Green
        Write-Host "  文件数: $fileCount" -ForegroundColor Gray
    }
}

Write-Host "`n备份任务完成！" -ForegroundColor Green
