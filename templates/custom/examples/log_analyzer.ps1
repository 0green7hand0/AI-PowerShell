<#
.SYNOPSIS
    日志文件分析工具
    
.DESCRIPTION
    分析日志文件，统计错误、警告信息，生成分析报告
    
.TEMPLATE_PARAMETERS
    {{LOG_PATH}} - 日志文件或目录路径
    {{ERROR_PATTERN}} - 错误匹配模式
    {{WARNING_PATTERN}} - 警告匹配模式
    {{OUTPUT_REPORT}} - 是否生成报告文件
    {{REPORT_PATH}} - 报告保存路径
    
.EXAMPLE
    分析系统日志，找出所有错误和警告
    
.NOTES
    这是一个自定义模板示例，展示如何分析日志文件
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$LogPath = "{{LOG_PATH}}",
    
    [Parameter(Mandatory=$false)]
    [string]$ErrorPattern = "{{ERROR_PATTERN}}",
    
    [Parameter(Mandatory=$false)]
    [string]$WarningPattern = "{{WARNING_PATTERN}}",
    
    [Parameter(Mandatory=$false)]
    [bool]$OutputReport = ${{OUTPUT_REPORT}},
    
    [Parameter(Mandatory=$false)]
    [string]$ReportPath = "{{REPORT_PATH}}"
)

# 验证路径
if (-not (Test-Path $LogPath)) {
    Write-Error "路径不存在: $LogPath"
    exit 1
}

Write-Host "🔍 开始分析日志..." -ForegroundColor Cyan
Write-Host "路径: $LogPath`n" -ForegroundColor Gray

# 获取日志文件
$logFiles = @()
if (Test-Path $LogPath -PathType Container) {
    $logFiles = Get-ChildItem -Path $LogPath -Filter "*.log" -Recurse -File
} else {
    $logFiles = @(Get-Item $LogPath)
}

Write-Host "找到 $($logFiles.Count) 个日志文件`n" -ForegroundColor Gray

# 初始化统计
$totalLines = 0
$errorCount = 0
$warningCount = 0
$errors = @()
$warnings = @()

# 分析每个文件
foreach ($file in $logFiles) {
    Write-Host "分析: $($file.Name)" -ForegroundColor Yellow
    
    $content = Get-Content $file.FullName
    $totalLines += $content.Count
    
    # 查找错误
    $fileErrors = $content | Select-String -Pattern $ErrorPattern
    $errorCount += $fileErrors.Count
    foreach ($error in $fileErrors) {
        $errors += [PSCustomObject]@{
            File = $file.Name
            Line = $error.LineNumber
            Content = $error.Line.Trim()
        }
    }
    
    # 查找警告
    $fileWarnings = $content | Select-String -Pattern $WarningPattern
    $warningCount += $fileWarnings.Count
    foreach ($warning in $fileWarnings) {
        $warnings += [PSCustomObject]@{
            File = $file.Name
            Line = $warning.LineNumber
            Content = $warning.Line.Trim()
        }
    }
}

# 生成报告
$report = @"
========================================
日志分析报告
========================================
生成时间: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
分析路径: $LogPath

统计信息:
- 日志文件数: $($logFiles.Count)
- 总行数: $totalLines
- 错误数: $errorCount
- 警告数: $warningCount

========================================
错误详情 (前10条):
========================================
"@

if ($errors.Count -gt 0) {
    $topErrors = $errors | Select-Object -First 10
    foreach ($error in $topErrors) {
        $report += "`n[$($error.File):$($error.Line)] $($error.Content)"
    }
} else {
    $report += "`n未发现错误"
}

$report += @"

========================================
警告详情 (前10条):
========================================
"@

if ($warnings.Count -gt 0) {
    $topWarnings = $warnings | Select-Object -First 10
    foreach ($warning in $topWarnings) {
        $report += "`n[$($warning.File):$($warning.Line)] $($warning.Content)"
    }
} else {
    $report += "`n未发现警告"
}

$report += "`n========================================"

# 输出到控制台
Write-Host "`n$report" -ForegroundColor White

# 保存报告
if ($OutputReport) {
    if (-not $ReportPath) {
        $ReportPath = Join-Path (Get-Location) "log_analysis_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"
    }
    
    $report | Out-File -FilePath $ReportPath -Encoding UTF8
    Write-Host "`n✓ 报告已保存: $ReportPath" -ForegroundColor Green
}

# 返回统计对象
return [PSCustomObject]@{
    TotalFiles = $logFiles.Count
    TotalLines = $totalLines
    ErrorCount = $errorCount
    WarningCount = $warningCount
    Errors = $errors
    Warnings = $warnings
}
