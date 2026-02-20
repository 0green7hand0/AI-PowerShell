# ============================================
# 日志分析脚本
# 功能：分析日志文件，提取错误、警告、统计信息
# ============================================

param(
    [string]$LOG_FILE = "{{LOG_FILE}}",
    [string]$LOG_LEVEL = "{{LOG_LEVEL}}",
    [int]$TAIL_LINES = {{TAIL_LINES}},
    [string]$SEARCH_PATTERN = "{{SEARCH_PATTERN}}",
    [bool]$SHOW_STATS = ${{SHOW_STATS}},
    [bool]$EXPORT_RESULTS = ${{EXPORT_RESULTS}},
    [string]$OUTPUT_FILE = "{{OUTPUT_FILE}}"
)

# 颜色输出函数
function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

function Write-Success { param([string]$Message) Write-ColorOutput "✓ $Message" "Green" }
function Write-Error { param([string]$Message) Write-ColorOutput "✗ $Message" "Red" }
function Write-Info { param([string]$Message) Write-ColorOutput "ℹ $Message" "Cyan" }
function Write-Warning { param([string]$Message) Write-ColorOutput "⚠ $Message" "Yellow" }

# 显示标题
Write-Host ""
Write-ColorOutput "╔════════════════════════════════════════════════╗" "Cyan"
Write-ColorOutput "║           日志分析工具                         ║" "Cyan"
Write-ColorOutput "╚════════════════════════════════════════════════╝" "Cyan"
Write-Host ""

# 检查文件是否存在
if (-not (Test-Path $LOG_FILE)) {
    Write-Error "日志文件不存在: $LOG_FILE"
    exit 1
}

Write-Info "分析日志文件: $LOG_FILE"
$fileInfo = Get-Item $LOG_FILE
Write-Host "  文件大小: $([math]::Round($fileInfo.Length / 1MB, 2)) MB" -ForegroundColor Gray
Write-Host "  最后修改: $($fileInfo.LastWriteTime)" -ForegroundColor Gray
Write-Host ""

# 读取日志内容
Write-Info "读取日志内容..."
try {
    if ($TAIL_LINES -gt 0) {
        $logContent = Get-Content $LOG_FILE -Tail $TAIL_LINES -ErrorAction Stop
        Write-Info "读取最后 $TAIL_LINES 行"
    } else {
        $logContent = Get-Content $LOG_FILE -ErrorAction Stop
        Write-Info "读取全部内容 ($($logContent.Count) 行)"
    }
} catch {
    Write-Error "读取文件失败: $($_.Exception.Message)"
    exit 1
}

Write-Host ""

# 统计信息
$stats = @{
    Total = $logContent.Count
    Error = 0
    Warning = 0
    Info = 0
    Debug = 0
    Other = 0
}

$results = @()

# 分析每一行
foreach ($line in $logContent) {
    # 统计日志级别
    if ($line -match "ERROR|error|Error") {
        $stats.Error++
        if ($LOG_LEVEL -eq "ERROR" -or $LOG_LEVEL -eq "ALL") {
            $results += [PSCustomObject]@{
                Level = "ERROR"
                Content = $line
            }
        }
    } elseif ($line -match "WARN|warn|Warning|WARNING") {
        $stats.Warning++
        if ($LOG_LEVEL -eq "WARNING" -or $LOG_LEVEL -eq "ALL") {
            $results += [PSCustomObject]@{
                Level = "WARNING"
                Content = $line
            }
        }
    } elseif ($line -match "INFO|info|Info") {
        $stats.Info++
        if ($LOG_LEVEL -eq "INFO" -or $LOG_LEVEL -eq "ALL") {
            $results += [PSCustomObject]@{
                Level = "INFO"
                Content = $line
            }
        }
    } elseif ($line -match "DEBUG|debug|Debug") {
        $stats.Debug++
        if ($LOG_LEVEL -eq "DEBUG" -or $LOG_LEVEL -eq "ALL") {
            $results += [PSCustomObject]@{
                Level = "DEBUG"
                Content = $line
            }
        }
    } else {
        $stats.Other++
    }
    
    # 搜索特定模式
    if ($SEARCH_PATTERN -and $line -match $SEARCH_PATTERN) {
        $results += [PSCustomObject]@{
            Level = "MATCH"
            Content = $line
        }
    }
}

# 显示统计信息
if ($SHOW_STATS) {
    Write-Info "日志统计信息:"
    Write-Host ""
    Write-Host "  总行数: $($stats.Total)" -ForegroundColor Gray
    Write-Host "  错误: $($stats.Error)" -ForegroundColor Red
    Write-Host "  警告: $($stats.Warning)" -ForegroundColor Yellow
    Write-Host "  信息: $($stats.Info)" -ForegroundColor Cyan
    Write-Host "  调试: $($stats.Debug)" -ForegroundColor Gray
    Write-Host "  其他: $($stats.Other)" -ForegroundColor Gray
    Write-Host ""
    
    # 计算百分比
    if ($stats.Total -gt 0) {
        $errorRate = [math]::Round($stats.Error / $stats.Total * 100, 2)
        $warningRate = [math]::Round($stats.Warning / $stats.Total * 100, 2)
        
        Write-Host "  错误率: $errorRate%" -ForegroundColor $(if ($errorRate -gt 5) { "Red" } else { "Green" })
        Write-Host "  警告率: $warningRate%" -ForegroundColor $(if ($warningRate -gt 10) { "Yellow" } else { "Green" })
    }
    Write-Host ""
}

# 显示筛选结果
if ($results.Count -gt 0) {
    Write-Info "筛选结果 ($($results.Count) 条):"
    Write-Host ""
    
    $displayCount = [Math]::Min(50, $results.Count)
    for ($i = 0; $i -lt $displayCount; $i++) {
        $result = $results[$i]
        $color = switch ($result.Level) {
            "ERROR" { "Red" }
            "WARNING" { "Yellow" }
            "INFO" { "Cyan" }
            "DEBUG" { "Gray" }
            "MATCH" { "Green" }
            default { "White" }
        }
        
        Write-Host "[$($result.Level)] " -ForegroundColor $color -NoNewline
        Write-Host $result.Content -ForegroundColor Gray
    }
    
    if ($results.Count -gt $displayCount) {
        Write-Host ""
        Write-Info "... 还有 $($results.Count - $displayCount) 条结果未显示"
    }
} else {
    Write-Warning "没有找到匹配的日志条目"
}

# 导出结果
if ($EXPORT_RESULTS -and $results.Count -gt 0) {
    Write-Host ""
    Write-Info "导出结果到文件..."
    
    try {
        $exportPath = if ($OUTPUT_FILE) { $OUTPUT_FILE } else { "log_analysis_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt" }
        
        # 创建导出内容
        $exportContent = @()
        $exportContent += "=" * 60
        $exportContent += "日志分析报告"
        $exportContent += "生成时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
        $exportContent += "源文件: $LOG_FILE"
        $exportContent += "=" * 60
        $exportContent += ""
        
        # 添加统计信息
        $exportContent += "统计信息:"
        $exportContent += "  总行数: $($stats.Total)"
        $exportContent += "  错误: $($stats.Error)"
        $exportContent += "  警告: $($stats.Warning)"
        $exportContent += "  信息: $($stats.Info)"
        $exportContent += "  调试: $($stats.Debug)"
        $exportContent += ""
        
        # 添加筛选结果
        $exportContent += "筛选结果 ($($results.Count) 条):"
        $exportContent += "-" * 60
        foreach ($result in $results) {
            $exportContent += "[$($result.Level)] $($result.Content)"
        }
        
        $exportContent | Out-File -FilePath $exportPath -Encoding UTF8
        Write-Success "结果已导出到: $exportPath"
    } catch {
        Write-Error "导出失败: $($_.Exception.Message)"
    }
}

Write-Host ""
Write-ColorOutput "════════════════════════════════════════════════" "Cyan"
Write-Success "分析完成"
