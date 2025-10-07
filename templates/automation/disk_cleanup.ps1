<#
.SYNOPSIS
    磁盘清理模板
    
.DESCRIPTION
    清理临时文件、缓存、回收站等，释放磁盘空间
    
.TEMPLATE_PARAMETERS
    {{CLEAN_TEMP}} - 清理临时文件（true/false）
    {{CLEAN_RECYCLE_BIN}} - 清空回收站（true/false）
    {{CLEAN_DOWNLOADS}} - 清理下载文件夹（true/false）
    {{DAYS_OLD}} - 清理多少天前的文件
    {{MIN_FILE_SIZE}} - 最小文件大小（MB）
    
.EXAMPLE
    用户需求：清理30天前的临时文件
    AI 修改后：
    - CLEAN_TEMP = true
    - DAYS_OLD = 30
    - MIN_FILE_SIZE = 0
#>

param(
    [Parameter(Mandatory=$false)]
    [bool]$CleanTemp = ${{CLEAN_TEMP}},
    
    [Parameter(Mandatory=$false)]
    [bool]$CleanRecycleBin = ${{CLEAN_RECYCLE_BIN}},
    
    [Parameter(Mandatory=$false)]
    [bool]$CleanDownloads = ${{CLEAN_DOWNLOADS}},
    
    [Parameter(Mandatory=$false)]
    [int]$DaysOld = {{DAYS_OLD}},
    
    [Parameter(Mandatory=$false)]
    [int]$MinFileSizeMB = {{MIN_FILE_SIZE}}
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "磁盘清理工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$totalFreed = 0
$cutoffDate = (Get-Date).AddDays(-$DaysOld)
$minSize = $MinFileSizeMB * 1MB

Write-Host "清理配置:" -ForegroundColor White
Write-Host "  清理临时文件: $CleanTemp" -ForegroundColor White
Write-Host "  清空回收站: $CleanRecycleBin" -ForegroundColor White
Write-Host "  清理下载文件夹: $CleanDownloads" -ForegroundColor White
Write-Host "  文件时间: $DaysOld 天前" -ForegroundColor White
Write-Host "  最小文件大小: $MinFileSizeMB MB" -ForegroundColor White
Write-Host ""

# 1. 清理临时文件
if ($CleanTemp) {
    Write-Host "清理临时文件..." -ForegroundColor Yellow
    
    $tempPaths = @(
        $env:TEMP,
        "C:\Windows\Temp",
        "$env:LOCALAPPDATA\Temp"
    )
    
    foreach ($tempPath in $tempPaths) {
        if (Test-Path $tempPath) {
            Write-Host "  检查: $tempPath" -ForegroundColor Gray
            
            try {
                $files = Get-ChildItem -Path $tempPath -Recurse -File -ErrorAction SilentlyContinue |
                         Where-Object { 
                             $_.LastWriteTime -lt $cutoffDate -and 
                             $_.Length -ge $minSize 
                         }
                
                $freedSpace = 0
                $fileCount = 0
                
                foreach ($file in $files) {
                    try {
                        $size = $file.Length
                        Remove-Item $file.FullName -Force -ErrorAction Stop
                        $freedSpace += $size
                        $fileCount++
                    }
                    catch {
                        # 忽略无法删除的文件
                    }
                }
                
                if ($fileCount -gt 0) {
                    $freedMB = [Math]::Round($freedSpace / 1MB, 2)
                    Write-Host "  ✓ 删除 $fileCount 个文件，释放 $freedMB MB" -ForegroundColor Green
                    $totalFreed += $freedSpace
                }
            }
            catch {
                Write-Host "  ✗ 清理失败: $($_.Exception.Message)" -ForegroundColor Red
            }
        }
    }
    Write-Host ""
}

# 2. 清空回收站
if ($CleanRecycleBin) {
    Write-Host "清空回收站..." -ForegroundColor Yellow
    
    try {
        # 获取回收站大小
        $shell = New-Object -ComObject Shell.Application
        $recycleBin = $shell.NameSpace(0x0a)
        $items = $recycleBin.Items()
        
        $binSize = 0
        foreach ($item in $items) {
            $binSize += $item.Size
        }
        
        if ($binSize -gt 0) {
            # 清空回收站
            Clear-RecycleBin -Force -ErrorAction Stop
            
            $binSizeMB = [Math]::Round($binSize / 1MB, 2)
            Write-Host "  ✓ 清空回收站，释放 $binSizeMB MB" -ForegroundColor Green
            $totalFreed += $binSize
        } else {
            Write-Host "  回收站已经是空的" -ForegroundColor Gray
        }
    }
    catch {
        Write-Host "  ✗ 清空回收站失败: $($_.Exception.Message)" -ForegroundColor Red
    }
    Write-Host ""
}

# 3. 清理下载文件夹
if ($CleanDownloads) {
    Write-Host "清理下载文件夹..." -ForegroundColor Yellow
    
    $downloadsPath = "$env:USERPROFILE\Downloads"
    
    if (Test-Path $downloadsPath) {
        try {
            $files = Get-ChildItem -Path $downloadsPath -File -ErrorAction SilentlyContinue |
                     Where-Object { 
                         $_.LastWriteTime -lt $cutoffDate -and 
                         $_.Length -ge $minSize 
                     }
            
            if ($files.Count -gt 0) {
                Write-Host "  找到 $($files.Count) 个符合条件的文件" -ForegroundColor White
                Write-Host "  预览前5个文件:" -ForegroundColor Gray
                
                $files | Select-Object -First 5 | ForEach-Object {
                    $sizeMB = [Math]::Round($_.Length / 1MB, 2)
                    Write-Host "    - $($_.Name) ($sizeMB MB)" -ForegroundColor Gray
                }
                
                $confirmation = Read-Host "  是否删除这些文件? (y/N)"
                
                if ($confirmation -eq 'y' -or $confirmation -eq 'Y') {
                    $freedSpace = 0
                    $fileCount = 0
                    
                    foreach ($file in $files) {
                        try {
                            $size = $file.Length
                            Remove-Item $file.FullName -Force -ErrorAction Stop
                            $freedSpace += $size
                            $fileCount++
                        }
                        catch {
                            Write-Host "    ✗ 无法删除: $($file.Name)" -ForegroundColor Red
                        }
                    }
                    
                    $freedMB = [Math]::Round($freedSpace / 1MB, 2)
                    Write-Host "  ✓ 删除 $fileCount 个文件，释放 $freedMB MB" -ForegroundColor Green
                    $totalFreed += $freedSpace
                } else {
                    Write-Host "  跳过下载文件夹清理" -ForegroundColor Yellow
                }
            } else {
                Write-Host "  没有找到符合条件的文件" -ForegroundColor Gray
            }
        }
        catch {
            Write-Host "  ✗ 清理失败: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    Write-Host ""
}

# 显示结果
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "清理完成!" -ForegroundColor Cyan

if ($totalFreed -gt 0) {
    $totalFreedMB = [Math]::Round($totalFreed / 1MB, 2)
    $totalFreedGB = [Math]::Round($totalFreed / 1GB, 2)
    
    Write-Host "总共释放空间: $totalFreedMB MB ($totalFreedGB GB)" -ForegroundColor Green
} else {
    Write-Host "没有释放空间" -ForegroundColor Yellow
}

Write-Host "========================================" -ForegroundColor Cyan
