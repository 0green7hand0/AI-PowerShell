<#
.SYNOPSIS
    用户活动报告生成器
    
.DESCRIPTION
    生成系统用户活动报告，包括登录历史、磁盘使用、进程信息等
    
.TEMPLATE_PARAMETERS
    {{USERNAME}} - 要查询的用户名（留空查询当前用户）
    {{INCLUDE_PROCESSES}} - 是否包含进程信息
    {{INCLUDE_DISK_USAGE}} - 是否包含磁盘使用信息
    {{SAVE_REPORT}} - 是否保存报告
    {{REPORT_FORMAT}} - 报告格式（txt/html/json）
    
.EXAMPLE
    生成当前用户的活动报告
    
.NOTES
    这是一个自定义模板示例，展示如何生成系统报告
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$Username = "{{USERNAME}}",
    
    [Parameter(Mandatory=$false)]
    [bool]$IncludeProcesses = ${{INCLUDE_PROCESSES}},
    
    [Parameter(Mandatory=$false)]
    [bool]$IncludeDiskUsage = ${{INCLUDE_DISK_USAGE}},
    
    [Parameter(Mandatory=$false)]
    [bool]$SaveReport = ${{SAVE_REPORT}},
    
    [Parameter(Mandatory=$false)]
    [ValidateSet("txt", "html", "json")]
    [string]$ReportFormat = "{{REPORT_FORMAT}}"
)

# 如果未指定用户名，使用当前用户
if ([string]::IsNullOrEmpty($Username)) {
    $Username = $env:USERNAME
}

Write-Host "📊 生成用户报告: $Username" -ForegroundColor Cyan
Write-Host "时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`n" -ForegroundColor Gray

# 收集基本信息
$computerInfo = Get-ComputerInfo
$reportData = [PSCustomObject]@{
    Username = $Username
    ComputerName = $env:COMPUTERNAME
    OSVersion = $computerInfo.OsVersion
    OSBuild = $computerInfo.OsBuildNumber
    LastBootTime = $computerInfo.OsLastBootUpTime
    Uptime = (Get-Date) - $computerInfo.OsLastBootUpTime
    GeneratedAt = Get-Date
}

Write-Host "✓ 基本信息收集完成" -ForegroundColor Green

# 收集进程信息
if ($IncludeProcesses) {
    Write-Host "收集进程信息..." -ForegroundColor Yellow
    
    $processes = Get-Process | Where-Object { $_.UserName -like "*$Username*" } | 
                 Select-Object Name, Id, CPU, WorkingSet, StartTime |
                 Sort-Object CPU -Descending |
                 Select-Object -First 10
    
    $reportData | Add-Member -MemberType NoteProperty -Name "TopProcesses" -Value $processes
    Write-Host "✓ 进程信息收集完成 (前10个)" -ForegroundColor Green
}

# 收集磁盘使用信息
if ($IncludeDiskUsage) {
    Write-Host "收集磁盘使用信息..." -ForegroundColor Yellow
    
    $disks = Get-PSDrive -PSProvider FileSystem | Where-Object { $_.Used -ne $null } |
             Select-Object @{N="Drive";E={$_.Name}},
                          @{N="UsedGB";E={[math]::Round($_.Used/1GB, 2)}},
                          @{N="FreeGB";E={[math]::Round($_.Free/1GB, 2)}},
                          @{N="TotalGB";E={[math]::Round(($_.Used + $_.Free)/1GB, 2)}},
                          @{N="UsedPercent";E={[math]::Round(($_.Used/($_.Used + $_.Free))*100, 2)}}
    
    $reportData | Add-Member -MemberType NoteProperty -Name "DiskUsage" -Value $disks
    Write-Host "✓ 磁盘使用信息收集完成" -ForegroundColor Green
}

# 收集用户配置文件大小
Write-Host "收集用户配置文件信息..." -ForegroundColor Yellow
$userProfile = $env:USERPROFILE
if (Test-Path $userProfile) {
    $profileSize = (Get-ChildItem -Path $userProfile -Recurse -File -ErrorAction SilentlyContinue | 
                   Measure-Object -Property Length -Sum).Sum / 1GB
    $reportData | Add-Member -MemberType NoteProperty -Name "ProfileSizeGB" -Value ([math]::Round($profileSize, 2))
}
Write-Host "✓ 用户配置文件信息收集完成" -ForegroundColor Green

# 生成报告
Write-Host "`n生成报告..." -ForegroundColor Cyan

switch ($ReportFormat) {
    "txt" {
        $report = @"
========================================
用户活动报告
========================================
用户名: $($reportData.Username)
计算机名: $($reportData.ComputerName)
操作系统: $($reportData.OSVersion) (Build $($reportData.OSBuild))
最后启动: $($reportData.LastBootTime)
运行时间: $($reportData.Uptime.Days) 天 $($reportData.Uptime.Hours) 小时
配置文件大小: $($reportData.ProfileSizeGB) GB
生成时间: $($reportData.GeneratedAt)

"@
        
        if ($IncludeProcesses) {
            $report += "`n========================================`n"
            $report += "前10个进程 (按CPU排序):`n"
            $report += "========================================`n"
            foreach ($proc in $reportData.TopProcesses) {
                $cpu = if ($proc.CPU) { [math]::Round($proc.CPU, 2) } else { 0 }
                $mem = [math]::Round($proc.WorkingSet / 1MB, 2)
                $report += "$($proc.Name) (PID: $($proc.Id))`n"
                $report += "  CPU: $cpu s | 内存: $mem MB`n"
            }
        }
        
        if ($IncludeDiskUsage) {
            $report += "`n========================================`n"
            $report += "磁盘使用情况:`n"
            $report += "========================================`n"
            foreach ($disk in $reportData.DiskUsage) {
                $report += "驱动器 $($disk.Drive):`n"
                $report += "  总容量: $($disk.TotalGB) GB`n"
                $report += "  已使用: $($disk.UsedGB) GB ($($disk.UsedPercent)%)`n"
                $report += "  可用: $($disk.FreeGB) GB`n"
            }
        }
        
        $report += "`n========================================`n"
        
        Write-Host $report
        
        if ($SaveReport) {
            $filename = "user_report_$($Username)_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"
            $report | Out-File -FilePath $filename -Encoding UTF8
            Write-Host "`n✓ 报告已保存: $filename" -ForegroundColor Green
        }
    }
    
    "json" {
        $json = $reportData | ConvertTo-Json -Depth 10
        Write-Host $json
        
        if ($SaveReport) {
            $filename = "user_report_$($Username)_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
            $json | Out-File -FilePath $filename -Encoding UTF8
            Write-Host "`n✓ 报告已保存: $filename" -ForegroundColor Green
        }
    }
    
    "html" {
        $html = @"
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>用户活动报告 - $($reportData.Username)</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1000px; margin: 0 auto; background: white; padding: 20px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        h1 { color: #333; border-bottom: 2px solid #007acc; padding-bottom: 10px; }
        h2 { color: #007acc; margin-top: 30px; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #007acc; color: white; }
        .info { background: #e7f3ff; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .info-item { margin: 5px 0; }
        .label { font-weight: bold; color: #555; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 用户活动报告</h1>
        
        <div class="info">
            <div class="info-item"><span class="label">用户名:</span> $($reportData.Username)</div>
            <div class="info-item"><span class="label">计算机名:</span> $($reportData.ComputerName)</div>
            <div class="info-item"><span class="label">操作系统:</span> $($reportData.OSVersion)</div>
            <div class="info-item"><span class="label">最后启动:</span> $($reportData.LastBootTime)</div>
            <div class="info-item"><span class="label">运行时间:</span> $($reportData.Uptime.Days) 天 $($reportData.Uptime.Hours) 小时</div>
            <div class="info-item"><span class="label">配置文件大小:</span> $($reportData.ProfileSizeGB) GB</div>
            <div class="info-item"><span class="label">生成时间:</span> $($reportData.GeneratedAt)</div>
        </div>
"@
        
        if ($IncludeProcesses) {
            $html += @"
        <h2>前10个进程 (按CPU排序)</h2>
        <table>
            <tr>
                <th>进程名</th>
                <th>PID</th>
                <th>CPU (秒)</th>
                <th>内存 (MB)</th>
                <th>启动时间</th>
            </tr>
"@
            foreach ($proc in $reportData.TopProcesses) {
                $cpu = if ($proc.CPU) { [math]::Round($proc.CPU, 2) } else { 0 }
                $mem = [math]::Round($proc.WorkingSet / 1MB, 2)
                $html += @"
            <tr>
                <td>$($proc.Name)</td>
                <td>$($proc.Id)</td>
                <td>$cpu</td>
                <td>$mem</td>
                <td>$($proc.StartTime)</td>
            </tr>
"@
            }
            $html += "        </table>`n"
        }
        
        if ($IncludeDiskUsage) {
            $html += @"
        <h2>磁盘使用情况</h2>
        <table>
            <tr>
                <th>驱动器</th>
                <th>总容量 (GB)</th>
                <th>已使用 (GB)</th>
                <th>可用 (GB)</th>
                <th>使用率</th>
            </tr>
"@
            foreach ($disk in $reportData.DiskUsage) {
                $html += @"
            <tr>
                <td>$($disk.Drive):</td>
                <td>$($disk.TotalGB)</td>
                <td>$($disk.UsedGB)</td>
                <td>$($disk.FreeGB)</td>
                <td>$($disk.UsedPercent)%</td>
            </tr>
"@
            }
            $html += "        </table>`n"
        }
        
        $html += @"
    </div>
</body>
</html>
"@
        
        if ($SaveReport) {
            $filename = "user_report_$($Username)_$(Get-Date -Format 'yyyyMMdd_HHmmss').html"
            $html | Out-File -FilePath $filename -Encoding UTF8
            Write-Host "✓ HTML报告已保存: $filename" -ForegroundColor Green
            Write-Host "  在浏览器中打开查看完整报告" -ForegroundColor Gray
        } else {
            Write-Host "HTML报告已生成（使用 -SaveReport 参数保存到文件）" -ForegroundColor Yellow
        }
    }
}

Write-Host "`n✓ 报告生成完成！" -ForegroundColor Green
return $reportData
