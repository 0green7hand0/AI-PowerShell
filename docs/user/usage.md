# Usage Guide

This guide covers basic usage patterns and common workflows for the AI PowerShell Assistant.

## Getting Started

### Starting the Server

```bash
# Start with default configuration
powershell-assistant start

# Start with custom configuration
powershell-assistant start --config /path/to/config.yaml

# Start in development mode
powershell-assistant start --dev

# Start with specific log level
powershell-assistant start --log-level DEBUG
```

### Basic Commands

```bash
# Check server status
powershell-assistant status

# Stop the server
powershell-assistant stop

# Restart the server
powershell-assistant restart

# View logs
powershell-assistant logs

# Show configuration
powershell-assistant config show
```

## Natural Language Processing

### Basic Translation

Convert natural language to PowerShell commands:

```bash
# Command line interface
powershell-assistant translate "list all running processes"
```

Output:
```json
{
  "success": true,
  "original_input": "list all running processes",
  "generated_command": "Get-Process",
  "confidence_score": 0.95,
  "explanation": "Gets all currently running processes on the system",
  "alternatives": [
    "Get-Process | Format-Table",
    "Get-Process | Sort-Object CPU -Descending"
  ]
}
```

### Advanced Translation Examples

#### System Administration
```bash
# Process management
powershell-assistant translate "show processes using more than 100MB memory"
# Output: Get-Process | Where-Object {$_.WorkingSet -gt 100MB}

# Service management
powershell-assistant translate "restart the web server service"
# Output: Restart-Service -Name W3SVC

# System information
powershell-assistant translate "show system uptime and performance"
# Output: Get-ComputerInfo | Select-Object TotalPhysicalMemory, CsProcessors, WindowsUpTime
```

#### File Management
```bash
# File operations
powershell-assistant translate "find all log files modified today"
# Output: Get-ChildItem -Path . -Filter "*.log" | Where-Object {$_.LastWriteTime -gt (Get-Date).Date}

# Directory operations
powershell-assistant translate "create a backup folder with today's date"
# Output: New-Item -ItemType Directory -Name "Backup_$(Get-Date -Format 'yyyy-MM-dd')"

# Permission management
powershell-assistant translate "show file permissions for the current directory"
# Output: Get-Acl -Path . | Format-List
```

#### Network Operations
```bash
# Network diagnostics
powershell-assistant translate "test network connectivity to google.com"
# Output: Test-NetConnection -ComputerName google.com -Port 80

# Network configuration
powershell-assistant translate "show all network adapters and their IP addresses"
# Output: Get-NetAdapter | Get-NetIPAddress | Format-Table
```

## Command Execution

### Direct Execution

Execute PowerShell commands directly:

```bash
# Execute a simple command
powershell-assistant exec "Get-Date"

# Execute with timeout
powershell-assistant exec "Get-Process" --timeout 30

# Execute in sandbox
powershell-assistant exec "Get-Service" --sandbox

# Execute with custom output format
powershell-assistant exec "Get-Process" --format json
```

### Execution Examples

#### System Monitoring
```bash
# CPU usage
powershell-assistant exec "Get-Counter '\Processor(_Total)\% Processor Time'"

# Memory usage
powershell-assistant exec "Get-Counter '\Memory\Available MBytes'"

# Disk space
powershell-assistant exec "Get-WmiObject -Class Win32_LogicalDisk | Select-Object DeviceID, Size, FreeSpace"
```

#### Service Management
```bash
# List services
powershell-assistant exec "Get-Service | Where-Object Status -eq 'Running'"

# Service details
powershell-assistant exec "Get-Service -Name 'Spooler' | Format-List *"

# Start a service (requires confirmation)
powershell-assistant exec "Start-Service -Name 'Spooler'"
```

#### Event Log Analysis
```bash
# Recent errors
powershell-assistant exec "Get-EventLog -LogName System -EntryType Error -Newest 10"

# Application events
powershell-assistant exec "Get-WinEvent -FilterHashtable @{LogName='Application'; Level=2} -MaxEvents 5"
```

## Session Management

### Working with Sessions

Sessions maintain context and history across requests:

```bash
# Create a new session
powershell-assistant session create --name "admin-session"

# List active sessions
powershell-assistant session list

# Use a specific session
powershell-assistant translate "list processes" --session admin-session

# View session history
powershell-assistant session history --session admin-session

# End a session
powershell-assistant session end --session admin-session
```

### Session Context

Sessions remember:
- Working directory
- Environment variables
- Command history
- User preferences
- Previous command results

Example workflow:
```bash
# Set working directory in session
powershell-assistant exec "Set-Location C:\Logs" --session log-analysis

# Subsequent commands use the context
powershell-assistant translate "list all error log files" --session log-analysis
# Output considers C:\Logs as current directory

# View current context
powershell-assistant session context --session log-analysis
```

## Security Features

### Command Validation

All commands go through security validation:

```bash
# Safe command (allowed)
powershell-assistant exec "Get-Process"
# ✓ Executed successfully

# Administrative command (requires confirmation)
powershell-assistant exec "Stop-Service -Name 'Spooler'"
# ? This command requires administrative privileges. Continue? (y/N)

# Dangerous command (blocked)
powershell-assistant exec "Remove-Item C:\* -Recurse -Force"
# ✗ Command blocked by security policy
```

### Sandbox Execution

Use sandbox for untrusted commands:

```bash
# Execute in sandbox
powershell-assistant exec "Get-ChildItem" --sandbox

# Sandbox with custom limits
powershell-assistant exec "Get-Process" --sandbox --memory-limit 256m --timeout 30
```

### Security Overrides

For authorized users:

```bash
# Bypass security (requires admin privileges)
powershell-assistant exec "Remove-Item temp.txt" --force --confirm

# Execute with elevated privileges
powershell-assistant exec "Get-Service" --elevated
```

## Output Formatting

### Format Options

```bash
# JSON output (default)
powershell-assistant exec "Get-Process" --format json

# Table output
powershell-assistant exec "Get-Process" --format table

# Raw PowerShell output
powershell-assistant exec "Get-Process" --format raw

# Custom format
powershell-assistant exec "Get-Process" --format custom --template "{{.Name}}: {{.CPU}}"
```

### Output Examples

#### JSON Format
```json
{
  "success": true,
  "return_code": 0,
  "stdout": "[{\"ProcessName\":\"chrome\",\"CPU\":45.2}]",
  "execution_time": 1.23,
  "platform": "Windows"
}
```

#### Table Format
```
ProcessName    CPU    Memory
-----------    ---    ------
chrome         45.2   234MB
firefox        23.1   156MB
notepad        0.1    12MB
```

### Output Filtering

```bash
# Limit output size
powershell-assistant exec "Get-Process" --max-output 1MB

# Filter output
powershell-assistant exec "Get-Process" --filter "CPU > 10"

# Sort output
powershell-assistant exec "Get-Process" --sort "CPU desc"
```

## Error Handling

### Common Error Scenarios

#### Command Not Found
```bash
powershell-assistant exec "Get-InvalidCommand"
```
Output:
```json
{
  "success": false,
  "error": "CommandNotFoundException: The term 'Get-InvalidCommand' is not recognized",
  "suggested_actions": [
    "Check command spelling",
    "Verify module is loaded",
    "Use Get-Command to find similar commands"
  ]
}
```

#### Permission Denied
```bash
powershell-assistant exec "Stop-Computer"
```
Output:
```json
{
  "success": false,
  "error": "Access denied: Insufficient privileges",
  "required_permissions": ["Administrator"],
  "suggested_actions": [
    "Run as administrator",
    "Request elevated privileges",
    "Use alternative command"
  ]
}
```

#### Timeout
```bash
powershell-assistant exec "Start-Sleep 120" --timeout 30
```
Output:
```json
{
  "success": false,
  "error": "Command execution timed out after 30 seconds",
  "partial_output": "...",
  "suggested_actions": [
    "Increase timeout value",
    "Optimize command performance",
    "Break command into smaller parts"
  ]
}
```

### Error Recovery

```bash
# Retry failed command
powershell-assistant retry --correlation-id req_123456

# Get error details
powershell-assistant error --correlation-id req_123456

# Suggest fixes
powershell-assistant fix --correlation-id req_123456
```

## Advanced Usage

### Batch Operations

Execute multiple commands:

```bash
# Batch file
cat commands.txt
Get-Date
Get-Process | Select-Object -First 5
Get-Service | Where-Object Status -eq 'Running'

# Execute batch
powershell-assistant batch --file commands.txt --session batch-session
```

### Scripting Integration

```bash
#!/bin/bash
# Monitor system resources

# Get CPU usage
CPU=$(powershell-assistant exec "Get-Counter '\Processor(_Total)\% Processor Time'" --format raw)

# Get memory usage
MEMORY=$(powershell-assistant exec "Get-Counter '\Memory\Available MBytes'" --format raw)

# Alert if resources are high
if [ "$CPU" -gt 80 ]; then
    echo "High CPU usage: $CPU%"
fi
```

### API Integration

```python
import requests

# Natural language processing
response = requests.post('http://localhost:8000/natural_language_to_powershell', 
    json={'input_text': 'list running services'})
result = response.json()

# Command execution
response = requests.post('http://localhost:8000/execute_powershell_command',
    json={'command': result['generated_command'], 'use_sandbox': True})
execution_result = response.json()
```

## Performance Tips

### Optimization Strategies

1. **Use Sessions**: Maintain context to avoid repeated setup
2. **Batch Commands**: Group related operations
3. **Limit Output**: Use filters and limits to reduce data transfer
4. **Cache Results**: Store frequently used command results
5. **Optimize AI Models**: Use appropriate model size for your hardware

### Performance Monitoring

```bash
# View performance metrics
powershell-assistant metrics

# Monitor resource usage
powershell-assistant monitor --duration 60

# Performance report
powershell-assistant report --type performance --period 24h
```

## Best Practices

### Security Best Practices

1. **Always use sandbox** for untrusted commands
2. **Review generated commands** before execution
3. **Keep security rules updated**
4. **Monitor audit logs** regularly
5. **Use least privilege principle**

### Usage Best Practices

1. **Use descriptive session names**
2. **Provide context in natural language**
3. **Test commands in development environment first**
4. **Keep command history for reference**
5. **Use appropriate output formats**

### Performance Best Practices

1. **Close unused sessions**
2. **Use appropriate timeouts**
3. **Monitor system resources**
4. **Optimize AI model parameters**
5. **Clean up logs regularly**

## Next Steps

- Explore [Advanced Features](advanced-features.md)
- Configure [Security Settings](security.md)
- Optimize [Performance](performance.md)
- Check [Troubleshooting](../troubleshooting/README.md) for issues