# ============================================
# 定时任务管理脚本
# 功能：创建、查看、删除 Windows 计划任务
# ============================================

param(
    [string]$ACTION = "{{ACTION}}",
    [string]$TASK_NAME = "{{TASK_NAME}}",
    [string]$SCRIPT_PATH = "{{SCRIPT_PATH}}",
    [string]$SCHEDULE_TYPE = "{{SCHEDULE_TYPE}}",
    [string]$START_TIME = "{{START_TIME}}",
    [string]$INTERVAL = "{{INTERVAL}}",
    [string]$DAYS_OF_WEEK = "{{DAYS_OF_WEEK}}",
    [bool]$RUN_AS_ADMIN = ${{RUN_AS_ADMIN}},
    [string]$DESCRIPTION = "{{DESCRIPTION}}"
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
Write-ColorOutput "║         定时任务管理工具                       ║" "Cyan"
Write-ColorOutput "╚════════════════════════════════════════════════╝" "Cyan"
Write-Host ""

# 执行操作
switch ($ACTION.ToLower()) {
    "create" {
        if (-not $TASK_NAME) {
            Write-Error "请指定任务名称"
            exit 1
        }
        
        if (-not $SCRIPT_PATH) {
            Write-Error "请指定脚本路径"
            exit 1
        }
        
        if (-not (Test-Path $SCRIPT_PATH)) {
            Write-Error "脚本文件不存在: $SCRIPT_PATH"
            exit 1
        }
        
        Write-Info "创建定时任务: $TASK_NAME"
        
        try {
            # 创建任务动作
            $action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-ExecutionPolicy Bypass -File `"$SCRIPT_PATH`""
            
            # 创建触发器
            $trigger = switch ($SCHEDULE_TYPE.ToLower()) {
                "daily" {
                    New-ScheduledTaskTrigger -Daily -At $START_TIME
                }
                "weekly" {
                    $days = $DAYS_OF_WEEK -split "," | ForEach-Object { $_.Trim() }
                    New-ScheduledTaskTrigger -Weekly -DaysOfWeek $days -At $START_TIME
                }
                "hourly" {
                    $trigger = New-ScheduledTaskTrigger -Once -At $START_TIME
                    $trigger.Repetition = New-ScheduledTaskTrigger -Once -At $START_TIME -RepetitionInterval (New-TimeSpan -Hours 1)
                    $trigger
                }
                "interval" {
                    $trigger = New-ScheduledTaskTrigger -Once -At $START_TIME
                    $trigger.Repetition = New-ScheduledTaskTrigger -Once -At $START_TIME -RepetitionInterval (New-TimeSpan -Minutes $INTERVAL)
                    $trigger
                }
                "startup" {
                    New-ScheduledTaskTrigger -AtStartup
                }
                "logon" {
                    New-ScheduledTaskTrigger -AtLogOn
                }
                default {
                    Write-Error "未知的计划类型: $SCHEDULE_TYPE"
                    exit 1
                }
            }
            
            # 创建任务设置
            $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
            
            # 创建任务主体
            if ($RUN_AS_ADMIN) {
                $principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
            } else {
                $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive
            }
            
            # 注册任务
            Register-ScheduledTask -TaskName $TASK_NAME -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description $DESCRIPTION -Force | Out-Null
            
            Write-Success "任务创建成功"
            Write-Host "  任务名称: $TASK_NAME" -ForegroundColor Gray
            Write-Host "  脚本路径: $SCRIPT_PATH" -ForegroundColor Gray
            Write-Host "  计划类型: $SCHEDULE_TYPE" -ForegroundColor Gray
            Write-Host "  开始时间: $START_TIME" -ForegroundColor Gray
            if ($RUN_AS_ADMIN) {
                Write-Host "  权限: 管理员" -ForegroundColor Gray
            }
        } catch {
            Write-Error "创建任务失败: $($_.Exception.Message)"
            exit 1
        }
    }
    
    "list" {
        Write-Info "列出所有计划任务..."
        Write-Host ""
        
        try {
            $tasks = Get-ScheduledTask | Where-Object { $_.State -ne "Disabled" }
            
            Write-Host ("{0,-30} {1,-15} {2,-20} {3}" -f "任务名称", "状态", "下次运行", "描述") -ForegroundColor Yellow
            Write-Host ("-" * 100) -ForegroundColor Gray
            
            foreach ($task in $tasks) {
                $info = Get-ScheduledTaskInfo -TaskName $task.TaskName -ErrorAction SilentlyContinue
                $nextRun = if ($info.NextRunTime) { $info.NextRunTime.ToString("yyyy-MM-dd HH:mm") } else { "N/A" }
                $desc = if ($task.Description) { $task.Description.Substring(0, [Math]::Min(30, $task.Description.Length)) } else { "" }
                
                $color = switch ($task.State) {
                    "Ready" { "Green" }
                    "Running" { "Cyan" }
                    "Disabled" { "Gray" }
                    default { "White" }
                }
                
                Write-Host ("{0,-30} {1,-15} {2,-20} {3}" -f `
                    $task.TaskName.Substring(0, [Math]::Min(30, $task.TaskName.Length)), `
                    $task.State, `
                    $nextRun, `
                    $desc) -ForegroundColor $color
            }
            
            Write-Host ""
            Write-Info "共 $($tasks.Count) 个活动任务"
        } catch {
            Write-Error "获取任务列表失败: $($_.Exception.Message)"
        }
    }
    
    "info" {
        if (-not $TASK_NAME) {
            Write-Error "请指定任务名称"
            exit 1
        }
        
        Write-Info "查询任务信息: $TASK_NAME"
        Write-Host ""
        
        try {
            $task = Get-ScheduledTask -TaskName $TASK_NAME -ErrorAction Stop
            $info = Get-ScheduledTaskInfo -TaskName $TASK_NAME
            
            Write-Host "任务名称: $($task.TaskName)" -ForegroundColor Cyan
            Write-Host "  状态: $($task.State)" -ForegroundColor Gray
            Write-Host "  描述: $($task.Description)" -ForegroundColor Gray
            Write-Host "  上次运行: $($info.LastRunTime)" -ForegroundColor Gray
            Write-Host "  下次运行: $($info.NextRunTime)" -ForegroundColor Gray
            Write-Host "  上次结果: $($info.LastTaskResult)" -ForegroundColor Gray
            
            Write-Host "`n触发器:" -ForegroundColor Yellow
            foreach ($trigger in $task.Triggers) {
                Write-Host "  类型: $($trigger.CimClass.CimClassName)" -ForegroundColor Gray
                if ($trigger.StartBoundary) {
                    Write-Host "  开始时间: $($trigger.StartBoundary)" -ForegroundColor Gray
                }
            }
            
            Write-Host "`n动作:" -ForegroundColor Yellow
            foreach ($action in $task.Actions) {
                Write-Host "  执行: $($action.Execute)" -ForegroundColor Gray
                if ($action.Arguments) {
                    Write-Host "  参数: $($action.Arguments)" -ForegroundColor Gray
                }
            }
        } catch {
            Write-Error "任务不存在或查询失败: $($_.Exception.Message)"
        }
    }
    
    "delete" {
        if (-not $TASK_NAME) {
            Write-Error "请指定任务名称"
            exit 1
        }
        
        Write-Warning "准备删除任务: $TASK_NAME"
        $confirm = Read-Host "确认删除? (y/N)"
        
        if ($confirm -eq "y" -or $confirm -eq "Y") {
            try {
                Unregister-ScheduledTask -TaskName $TASK_NAME -Confirm:$false
                Write-Success "任务已删除"
            } catch {
                Write-Error "删除任务失败: $($_.Exception.Message)"
            }
        } else {
            Write-Info "操作已取消"
        }
    }
    
    "enable" {
        if (-not $TASK_NAME) {
            Write-Error "请指定任务名称"
            exit 1
        }
        
        try {
            Enable-ScheduledTask -TaskName $TASK_NAME | Out-Null
            Write-Success "任务已启用: $TASK_NAME"
        } catch {
            Write-Error "启用任务失败: $($_.Exception.Message)"
        }
    }
    
    "disable" {
        if (-not $TASK_NAME) {
            Write-Error "请指定任务名称"
            exit 1
        }
        
        try {
            Disable-ScheduledTask -TaskName $TASK_NAME | Out-Null
            Write-Success "任务已禁用: $TASK_NAME"
        } catch {
            Write-Error "禁用任务失败: $($_.Exception.Message)"
        }
    }
    
    default {
        Write-Error "未知操作: $ACTION"
        Write-Info "支持的操作: create, list, info, delete, enable, disable"
        exit 1
    }
}

Write-Host ""
Write-ColorOutput "════════════════════════════════════════════════" "Cyan"
Write-Success "操作完成"
