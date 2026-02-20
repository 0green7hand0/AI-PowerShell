# ============================================
# 网络连接诊断脚本
# 功能：检查网络连接、DNS解析、延迟测试
# ============================================

param(
    [string]$TARGET_HOST = "{{TARGET_HOST}}",
    [int]$PING_COUNT = {{PING_COUNT}},
    [int]$TIMEOUT = {{TIMEOUT}},
    [bool]$CHECK_DNS = ${{CHECK_DNS}},
    [bool]$CHECK_PORTS = ${{CHECK_PORTS}},
    [string]$PORTS = "{{PORTS}}",
    [bool]$TRACE_ROUTE = ${{TRACE_ROUTE}}
)

# 颜色输出函数
function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

function Write-Success { param([string]$Message) Write-ColorOutput "✓ $Message" "Green" }
function Write-Error { param([string]$Message) Write-ColorOutput "✗ $Message" "Red" }
function Write-Info { param([string]$Message) Write-ColorOutput "ℹ $Message" "Cyan" }

# 显示标题
Write-Host ""
Write-ColorOutput "╔════════════════════════════════════════════════╗" "Cyan"
Write-ColorOutput "║        网络连接诊断工具                        ║" "Cyan"
Write-ColorOutput "╚════════════════════════════════════════════════╝" "Cyan"
Write-Host ""

Write-Info "目标主机: $TARGET_HOST"
Write-Host ""

# 1. 基本连通性测试
Write-Info "1. 测试网络连通性..."
try {
    $pingResult = Test-Connection -ComputerName $TARGET_HOST -Count $PING_COUNT -ErrorAction Stop
    
    $avgLatency = ($pingResult | Measure-Object -Property ResponseTime -Average).Average
    $successRate = ($pingResult | Where-Object { $_.StatusCode -eq 0 }).Count / $PING_COUNT * 100
    
    Write-Success "网络连通正常"
    Write-Host "  平均延迟: $([math]::Round($avgLatency, 2)) ms" -ForegroundColor Gray
    Write-Host "  成功率: $successRate%" -ForegroundColor Gray
    
    # 显示详细结果
    foreach ($ping in $pingResult) {
        $status = if ($ping.StatusCode -eq 0) { "✓" } else { "✗" }
        Write-Host "  $status $($ping.Address) - $($ping.ResponseTime) ms" -ForegroundColor Gray
    }
} catch {
    Write-Error "网络连接失败: $($_.Exception.Message)"
}

Write-Host ""

# 2. DNS 解析测试
if ($CHECK_DNS) {
    Write-Info "2. 测试 DNS 解析..."
    try {
        $dnsResult = Resolve-DnsName -Name $TARGET_HOST -ErrorAction Stop
        Write-Success "DNS 解析成功"
        
        foreach ($record in $dnsResult) {
            if ($record.Type -eq "A") {
                Write-Host "  IPv4: $($record.IPAddress)" -ForegroundColor Gray
            } elseif ($record.Type -eq "AAAA") {
                Write-Host "  IPv6: $($record.IPAddress)" -ForegroundColor Gray
            }
        }
    } catch {
        Write-Error "DNS 解析失败: $($_.Exception.Message)"
    }
    Write-Host ""
}

# 3. 端口连接测试
if ($CHECK_PORTS -and $PORTS) {
    Write-Info "3. 测试端口连接..."
    $portList = $PORTS -split ","
    
    foreach ($port in $portList) {
        $port = $port.Trim()
        try {
            $tcpClient = New-Object System.Net.Sockets.TcpClient
            $tcpClient.ReceiveTimeout = $TIMEOUT * 1000
            $tcpClient.SendTimeout = $TIMEOUT * 1000
            
            $result = $tcpClient.BeginConnect($TARGET_HOST, $port, $null, $null)
            $success = $result.AsyncWaitHandle.WaitOne($TIMEOUT * 1000)
            
            if ($success) {
                Write-Success "端口 $port 开放"
                $tcpClient.EndConnect($result)
            } else {
                Write-Error "端口 $port 关闭或超时"
            }
            
            $tcpClient.Close()
        } catch {
            Write-Error "端口 $port 无法连接: $($_.Exception.Message)"
        }
    }
    Write-Host ""
}

# 4. 路由追踪
if ($TRACE_ROUTE) {
    Write-Info "4. 路由追踪..."
    try {
        $traceResult = Test-NetConnection -ComputerName $TARGET_HOST -TraceRoute -ErrorAction Stop
        
        Write-Success "路由追踪完成"
        Write-Host "  跳数: $($traceResult.TraceRoute.Count)" -ForegroundColor Gray
        
        $hopNumber = 1
        foreach ($hop in $traceResult.TraceRoute) {
            Write-Host "  $hopNumber. $hop" -ForegroundColor Gray
            $hopNumber++
        }
    } catch {
        Write-Error "路由追踪失败: $($_.Exception.Message)"
    }
    Write-Host ""
}

# 5. 网络接口信息
Write-Info "5. 本地网络接口信息..."
$adapters = Get-NetAdapter | Where-Object { $_.Status -eq "Up" }

foreach ($adapter in $adapters) {
    Write-Host "  接口: $($adapter.Name)" -ForegroundColor Gray
    Write-Host "    状态: $($adapter.Status)" -ForegroundColor Gray
    Write-Host "    速度: $($adapter.LinkSpeed)" -ForegroundColor Gray
    
    $ipConfig = Get-NetIPAddress -InterfaceIndex $adapter.InterfaceIndex -AddressFamily IPv4 -ErrorAction SilentlyContinue
    if ($ipConfig) {
        Write-Host "    IP: $($ipConfig.IPAddress)" -ForegroundColor Gray
    }
}

Write-Host ""
Write-ColorOutput "════════════════════════════════════════════════" "Cyan"
Write-Success "诊断完成"
