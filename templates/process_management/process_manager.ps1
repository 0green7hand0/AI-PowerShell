# ============================================
# 进程管理脚本
# 功能：查看、筛选、终止进程
# ============================================

param(
    [string]$ACTION = "{{ACTION}}",
    [string]$PROCESS_NAME = "{{PROCESS_NAME}}",
    [int]$TOP_COUNT = {{TOP_COUNT}},
    [string]$SORT_BY = "{{SORT_BY}}",
    [int]$CPU_THRESHOLD = {{CPU_THRESHOLD}},
    [int]$MEMORY_THRESHOLD = {{MEMORY_THRESHOLD}},
    [bool]$SHOW_DETAILS = ${{SHOW_DETAILS}}
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
Write-ColorOutput "║           进程管理工具                         ║" "Cyan"
Write-ColorOutput "╚════════════════════════════════════════════════╝" "Cyan"
Write-Host ""

# 格式化内存大小
function Format-MemorySize {
    param([long]$Bytes)
    
    if ($Bytes -ge 1GB) {
        return "{0:N2} GB" -f ($Bytes / 1GB)
    } elseif ($Bytes -ge 1MB) {
        return "{0:N2} MB" -f ($Bytes / 1MB)
    } elseif ($Bytes -ge 1KB) {
        return "{0:N2} KB" -f ($Bytes / 1KB)
    } else {
        return "$Bytes B"
    }
}

# 执行操作
switch ($ACTION.ToLower()) {
    "list" {
        Write-Info "列出进程..."
        
        # 获取所有进程
        $processes = Get-Process | Where-Object { $_.ProcessName -ne "Idle" }
        
        # 按指定字段排序
        switch ($SORT_BY.ToLower()) {
            "cpu" { $processes = $processes | Sort-Object CPU -Descending }
            "memory" { $processes = $processes | Sort-Object WorkingSet64 -Descending }
            "name" { $processes = $processes | Sort-Object ProcessName }
            default { $processes = $processes | Sort-Object CPU -Descending }
        }
        
        # 限制显示数量
        if ($TOP_COUNT -gt 0) {
            $processes = $processes | Select-Object -First $TOP_COUNT
        }
        
        Write-Host ""
        Write-Host ("{0,-8} {1,-30} {2,10} {3,12} {4,10}" -f "PID", "进程名", "CPU(%)", "内存", "线程数") -ForegroundColor Yellow
        Write-Host ("-" * 75) -ForegroundColor Gray
        
        foreach ($proc in $processes) {
            $cpu = if ($proc.CPU) { "{0:N2}" -f $proc.CPU } else { "0.00" }
            $memory = Format-MemorySize $proc.WorkingSet64
            
            Write-Host ("{0,-8} {1,-30} {2,10} {3,12} {4,10}" -f `
                $proc.Id, `
                $proc.ProcessName.Substring(0, [Math]::Min(30, $proc.ProcessName.Length)), `
                $cpu, `
                $memory, `
                $proc.Threads.Count)
        }
        
        Write-Host ""
        Write-Info "共 $($processes.Count) 个进程"
    }
    
    "find" {
        if (-not $PROCESS_NAME) {
            Write-Error "请指定进程名称"
            exit 1
        }
        
        Write-Info "查找进程: $PROCESS_NAME"
        
        $processes = Get-Process -Name "*$PROCESS_NAME*" -ErrorAction SilentlyContinue
        
        if ($processes) {
            Write-Success "找到 $($processes.Count) 个匹配的进程"
            Write-Host ""
            
            foreach ($proc in $processes) {
                Write-Host "进程: $($proc.ProcessName)" -ForegroundColor Cyan
                Write-Host "  PID: $($proc.Id)" -ForegroundColor Gray
                Write-Host "  CPU: $($proc.CPU)" -ForegroundColor Gray
                Write-Host "  内存: $(Format-MemorySize $proc.WorkingSet64)" -ForegroundColor Gray
                Write-Host "  启动时间: $($proc.StartTime)" -ForegroundColor Gray
                
                if ($SHOW_DETAILS) {
                    Write-Host "  路径: $($proc.Path)" -ForegroundColor Gray
                    Write-Host "  线程数: $($proc.Threads.Count)" -ForegroundColor Gray
                    Write-Host "  句柄数: $($proc.HandleCount)" -ForegroundColor Gray
                }
                Write-Host ""
            }
        } else {
            Write-Warning "未找到匹配的进程"
        }
    }
    
    "kill" {
        if (-not $PROCESS_NAME) {
            Write-Error "请指定进程名称"
            exit 1
        }
        
        Write-Warning "准备终止进程: $PROCESS_NAME"
        
        $processes = Get-Process -Name "*$PROCESS_NAME*" -ErrorAction SilentlyContinue
        
        if ($processes) {
            Write-Host "找到 $($processes.Count) 个匹配的进程:" -ForegroundColor Yellow
            foreach ($proc in $processes) {
                Write-Host "  - $($proc.ProcessName) (PID: $($proc.Id))" -ForegroundColor Gray
            }
            
            $confirm = Read-Host "`n确认终止这些进程? (y/N)"
            if ($confirm -eq "y" -or $confirm -eq "Y") {
                foreach ($proc in $processes) {
                    try {
                        Stop-Process -Id $proc.Id -Force
                        Write-Success "已终止: $($proc.ProcessName) (PID: $($proc.Id))"
                    } catch {
                        Write-Error "终止失败: $($proc.ProcessName) - $($_.Exception.Message)"
                    }
                }
            } else {
                Write-Info "操作已取消"
            }
        } else {
            Write-Warning "未找到匹配的进程"
        }
    }
    
    "monitor" {
        Write-Info "监控高资源占用进程..."
        Write-Info "CPU 阈值: $CPU_THRESHOLD%"
        Write-Info "内存阈值: $MEMORY_THRESHOLD MB"
        Write-Host ""
        
        $processes = Get-Process | Where-Object {
            ($_.CPU -gt $CPU_THRESHOLD) -or 
            (($_.WorkingSet64 / 1MB) -gt $MEMORY_THRESHOLD)
        } | Sort-Object CPU -Descending
        
        if ($processes) {
            Write-Warning "发现 $($processes.Count) 个高资源占用进程:"
            Write-Host ""
            
            Write-Host ("{0,-8} {1,-30} {2,10} {3,12}" -f "PID", "进程名", "CPU(%)", "内存") -ForegroundColor Yellow
            Write-Host ("-" * 65) -ForegroundColor Gray
            
            foreach ($proc in $processes) {
                $cpu = if ($proc.CPU) { "{0:N2}" -f $proc.CPU } else { "0.00" }
                $memory = Format-MemorySize $proc.WorkingSet64
                
                $color = "White"
                if ($proc.CPU -gt $CPU_THRESHOLD * 2) { $color = "Red" }
                elseif ($proc.CPU -gt $CPU_THRESHOLD) { $color = "Yellow" }
                
                Write-Host ("{0,-8} {1,-30} {2,10} {3,12}" -f `
                    $proc.Id, `
                    $proc.ProcessName.Substring(0, [Math]::Min(30, $proc.ProcessName.Length)), `
                    $cpu, `
                    $memory) -ForegroundColor $color
            }
        } else {
            Write-Success "所有进程资源占用正常"
        }
    }
    
    default {
        Write-Error "未知操作: $ACTION"
        Write-Info "支持的操作: list, find, kill, monitor"
        exit 1
    }
}

Write-Host ""
Write-ColorOutput "════════════════════════════════════════════════" "Cyan"
Write-Success "操作完成"
