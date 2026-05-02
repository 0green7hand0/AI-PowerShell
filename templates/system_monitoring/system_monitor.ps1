<#
.SYNOPSIS
    系统监控脚本 - 实时监控系统资源使用情况

.DESCRIPTION
    此脚本提供系统监控功能，支持：
    - 监控CPU使用率
    - 监控内存使用情况
    - 监控磁盘使用情况
    - 监控网络活动
    - 设置阈值告警

.PARAMETER MonitorCPU
    监控CPU使用率

.PARAMETER MonitorMemory
    监控内存使用

.PARAMETER MonitorDisk
    监控磁盘使用

.PARAMETER MonitorNetwork
    监控网络活动

.PARAMETER AlertThreshold
    告警阈值（百分比）

.PARAMETER IntervalSeconds
    监控间隔（秒）

.EXAMPLE
    .\system_monitor.ps1 -MonitorCPU $true -MonitorMemory $true -AlertThreshold 80 -IntervalSeconds 5
#>

param(
    [bool]$MonitorCPU = {{MONITOR_CPU}},
    [bool]$MonitorMemory = {{MONITOR_MEMORY}},
    [bool]$MonitorDisk = {{MONITOR_DISK}},
    [bool]$MonitorNetwork = {{MONITOR_NETWORK}},
    [int]$AlertThreshold = {{ALERT_THRESHOLD}},
    [int]$IntervalSeconds = {{INTERVAL_SECONDS}}
)

$ErrorActionPreference = "Stop"

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $color = switch ($Level) {
        "ERROR" { "Red" }
        "WARNING" { "Yellow" }
        "SUCCESS" { "Green" }
        default { "White" }
    }
    Write-Host "[$timestamp] [$Level] $Message" -ForegroundColor $color
}

function Get-CPUUsage {
    $cpu = Get-WmiObject Win32_Processor | Measure-Object -Property LoadPercentage -Average
    return [math]::Round($cpu.Average, 2)
}

function Get-MemoryUsage {
    $os = Get-WmiObject Win32_OperatingSystem
    $totalMem = $os.TotalVisibleMemorySize
    $freeMem = $os.FreePhysicalMemory
    $usedMem = $totalMem - $freeMem
    $percentUsed = [math]::Round(($usedMem / $totalMem) * 100, 2)
    
    return @{
        TotalGB   = [math]::Round($totalMem / 1MB, 2)
        UsedGB    = [math]::Round($usedMem / 1MB, 2)
        FreeGB    = [math]::Round($freeMem / 1MB, 2)
        PercentUsed = $percentUsed
    }
}

function Get-DiskUsage {
    $disks = Get-WmiObject Win32_LogicalDisk | Where-Object { $_.DriveType -eq 3 }
    $result = @()
    
    foreach ($disk in $disks) {
        $totalGB = [math]::Round($disk.Size / 1GB, 2)
        $freeGB = [math]::Round($disk.FreeSpace / 1GB, 2)
        $usedGB = $totalGB - $freeGB
        $percentUsed = [math]::Round(($usedGB / $totalGB) * 100, 2)
        
        $result += @{
            Drive       = $disk.DeviceID
            TotalGB     = $totalGB
            UsedGB      = $usedGB
            FreeGB      = $freeGB
            PercentUsed = $percentUsed
        }
    }
    
    return $result
}

function Get-NetworkActivity {
    $netAdapter = Get-WmiObject Win32_PerformanceFormattedData_Tcpip_NetworkInterface | 
                  Where-Object { $_.Name -notlike "*Loopback*" } | 
                  Select-Object -First 1
    
    if ($netAdapter) {
        return @{
            BytesReceivedPerSec = [math]::Round($netAdapter.BytesReceivedPerSec / 1KB, 2)
            BytesSentPerSec     = [math]::Round($netAdapter.BytesSentPerSec / 1KB, 2)
            TotalBytesPerSec    = [math]::Round(($netAdapter.BytesReceivedPerSec + $netAdapter.BytesSentPerSec) / 1KB, 2)
        }
    }
    
    return $null
}

Write-Log "开始系统监控..." "INFO"
Write-Log "监控CPU: $MonitorCPU"
Write-Log "监控内存: $MonitorMemory"
Write-Log "监控磁盘: $MonitorDisk"
Write-Log "监控网络: $MonitorNetwork"
Write-Log "告警阈值: $AlertThreshold%"
Write-Log "监控间隔: $IntervalSeconds 秒"
Write-Log "按 Ctrl+C 停止监控`n" "INFO"

try {
    while ($true) {
        $timestamp = Get-Date -Format "HH:mm:ss"
        Write-Host "`n[$timestamp] 系统状态:" -ForegroundColor Cyan
        
        # CPU监控
        if ($MonitorCPU) {
            $cpuUsage = Get-CPUUsage
            $color = if ($cpuUsage -ge $AlertThreshold) { "Red" } else { "Green" }
            Write-Host "  CPU使用率: $cpuUsage%" -ForegroundColor $color
            
            if ($cpuUsage -ge $AlertThreshold) {
                Write-Log "CPU使用率超过阈值!" "WARNING"
            }
        }
        
        # 内存监控
        if ($MonitorMemory) {
            $mem = Get-MemoryUsage
            $color = if ($mem.PercentUsed -ge $AlertThreshold) { "Red" } else { "Green" }
            Write-Host "  内存使用: $($mem.UsedGB)GB / $($mem.TotalGB)GB ($($mem.PercentUsed)%)" -ForegroundColor $color
            
            if ($mem.PercentUsed -ge $AlertThreshold) {
                Write-Log "内存使用率超过阈值!" "WARNING"
            }
        }
        
        # 磁盘监控
        if ($MonitorDisk) {
            $disks = Get-DiskUsage
            foreach ($disk in $disks) {
                $color = if ($disk.PercentUsed -ge $AlertThreshold) { "Red" } else { "Green" }
                Write-Host "  磁盘 $($disk.Drive): $($disk.UsedGB)GB / $($disk.TotalGB)GB ($($disk.PercentUsed)%)" -ForegroundColor $color
                
                if ($disk.PercentUsed -ge $AlertThreshold) {
                    Write-Log "磁盘 $($disk.Drive) 使用率超过阈值!" "WARNING"
                }
            }
        }
        
        # 网络监控
        if ($MonitorNetwork) {
            $net = Get-NetworkActivity
            if ($net) {
                Write-Host "  网络活动: 接收 $($net.BytesReceivedPerSec) KB/s, 发送 $($net.BytesSentPerSec) KB/s" -ForegroundColor Green
            }
        }
        
        Start-Sleep -Seconds $IntervalSeconds
    }
}
catch [System.Management.Automation.HaltCommandException] {
    Write-Log "`n监控已停止" "INFO"
}
catch {
    Write-Log "监控出错: $_" "ERROR"
}
