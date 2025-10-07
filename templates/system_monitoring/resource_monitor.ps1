<#
.SYNOPSIS
    系统资源监控模板
    
.DESCRIPTION
    监控CPU、内存、磁盘使用情况，超过阈值时发出警告
    
.TEMPLATE_PARAMETERS
    {{CPU_THRESHOLD}} - CPU使用率阈值（百分比）
    {{MEMORY_THRESHOLD}} - 内存使用率阈值（百分比）
    {{DISK_THRESHOLD}} - 磁盘使用率阈值（百分比）
    {{CHECK_INTERVAL}} - 检查间隔（秒）
    {{TOP_PROCESSES}} - 显示前N个进程
    {{DURATION}} - 监控持续时间（秒，0表示持续监控）
    
.EXAMPLE
    用户需求：每30秒检查一次，CPU超过80%就警告
    AI 修改后：
    - CPU_THRESHOLD = 80
    - CHECK_INTERVAL = 30
    - TOP_PROCESSES = 5
#>

param(
    [Parameter(Mandatory=$false)]
    [int]$CpuThreshold = {{CPU_THRESHOLD}},
    
    [Parameter(Mandatory=$false)]
    [int]$MemoryThreshold = {{MEMORY_THRESHOLD}},
    
    [Parameter(Mandatory=$false)]
    [int]$DiskThreshold = {{DISK_THRESHOLD}},
    
    [Parameter(Mandatory=$false)]
    [int]$CheckInterval = {{CHECK_INTERVAL}},
    
    [Parameter(Mandatory=$false)]
    [int]$TopProcesses = {{TOP_PROCESSES}},
    
    [Parameter(Mandatory=$false)]
    [int]$Duration = {{DURATION}}
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "系统资源监控工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "监控配置:" -ForegroundColor White
Write-Host "  CPU 阈值: $CpuThreshold%" -ForegroundColor White
Write-Host "  内存阈值: $MemoryThreshold%" -ForegroundColor White
Write-Host "  磁盘阈值: $DiskThreshold%" -ForegroundColor White
Write-Host "  检查间隔: $CheckInterval 秒" -ForegroundColor White
Write-Host ""
Write-Host "按 Ctrl+C 停止监控" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$startTime = Get-Date
$checkCount = 0

while ($true) {
    $checkCount++
    $currentTime = Get-Date
    
    # 检查是否超过持续时间
    if ($Duration -gt 0) {
        $elapsed = ($currentTime - $startTime).TotalSeconds
        if ($elapsed -gt $Duration) {
            Write-Host ""
            Write-Host "监控时间已到，退出监控" -ForegroundColor Yellow
            break
        }
    }
    
    Write-Host "[$($currentTime.ToString('yyyy-MM-dd HH:mm:ss'))] 检查 #$checkCount" -ForegroundColor Cyan
    Write-Host "----------------------------------------"
    
    # 1. CPU 监控
    $cpuUsage = (Get-Counter '\Processor(_Total)\% Processor Time').CounterSamples.CookedValue
    $cpuUsage = [Math]::Round($cpuUsage, 2)
    
    if ($cpuUsage -gt $CpuThreshold) {
        Write-Host "⚠️  CPU 使用率: $cpuUsage% (超过阈值 $CpuThreshold%)" -ForegroundColor Red
        
        # 显示CPU占用最高的进程
        Write-Host "   CPU 占用最高的进程:" -ForegroundColor Yellow
        Get-Process | Sort-Object CPU -Descending | Select-Object -First $TopProcesses | ForEach-Object {
            Write-Host "   - $($_.Name): $([Math]::Round($_.CPU, 2))s" -ForegroundColor White
        }
    } else {
        Write-Host "✓ CPU 使用率: $cpuUsage%" -ForegroundColor Green
    }
    
    # 2. 内存监控
    $os = Get-CimInstance Win32_OperatingSystem
    $totalMemory = $os.TotalVisibleMemorySize / 1MB
    $freeMemory = $os.FreePhysicalMemory / 1MB
    $usedMemory = $totalMemory - $freeMemory
    $memoryUsage = [Math]::Round(($usedMemory / $totalMemory) * 100, 2)
    
    if ($memoryUsage -gt $MemoryThreshold) {
        Write-Host "⚠️  内存使用率: $memoryUsage% (超过阈值 $MemoryThreshold%)" -ForegroundColor Red
        Write-Host "   已用: $([Math]::Round($usedMemory, 2)) GB / $([Math]::Round($totalMemory, 2)) GB" -ForegroundColor White
        
        # 显示内存占用最高的进程
        Write-Host "   内存占用最高的进程:" -ForegroundColor Yellow
        Get-Process | Sort-Object WorkingSet -Descending | Select-Object -First $TopProcesses | ForEach-Object {
            $memMB = [Math]::Round($_.WorkingSet / 1MB, 2)
            Write-Host "   - $($_.Name): $memMB MB" -ForegroundColor White
        }
    } else {
        Write-Host "✓ 内存使用率: $memoryUsage% ($([Math]::Round($usedMemory, 2)) GB / $([Math]::Round($totalMemory, 2)) GB)" -ForegroundColor Green
    }
    
    # 3. 磁盘监控
    $drives = Get-PSDrive -PSProvider FileSystem | Where-Object { $_.Used -ne $null }
    
    foreach ($drive in $drives) {
        $total = ($drive.Used + $drive.Free) / 1GB
        $used = $drive.Used / 1GB
        $free = $drive.Free / 1GB
        $usage = [Math]::Round(($used / $total) * 100, 2)
        
        if ($usage -gt $DiskThreshold) {
            Write-Host "⚠️  磁盘 $($drive.Name): $usage% (超过阈值 $DiskThreshold%)" -ForegroundColor Red
            Write-Host "   已用: $([Math]::Round($used, 2)) GB / $([Math]::Round($total, 2)) GB" -ForegroundColor White
        } else {
            Write-Host "✓ 磁盘 $($drive.Name): $usage% ($([Math]::Round($free, 2)) GB 可用)" -ForegroundColor Green
        }
    }
    
    Write-Host ""
    
    # 等待下一次检查
    Start-Sleep -Seconds $CheckInterval
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "监控结束" -ForegroundColor Cyan
Write-Host "总检查次数: $checkCount" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
