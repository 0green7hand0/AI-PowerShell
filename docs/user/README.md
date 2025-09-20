# User Guide

This guide covers installation, configuration, and usage of the AI PowerShell Assistant.

## Table of Contents

- [Installation](installation.md)
- [Configuration](configuration.md)
- [Basic Usage](usage.md)
- [Advanced Features](advanced-features.md)
- [Security Settings](security.md)
- [Performance Tuning](performance.md)

## Overview

The AI PowerShell Assistant is an intelligent command-line interaction system that:

- Converts natural language to PowerShell commands
- Provides comprehensive security validation
- Executes commands safely across platforms
- Maintains detailed audit logs
- Learns from your usage patterns

## Quick Start

1. **Install Prerequisites**
   ```bash
   # Install Python 3.8+
   python --version
   
   # Install Docker (for sandbox execution)
   docker --version
   ```

2. **Install the Assistant**
   ```bash
   pip install ai-powershell-assistant
   ```

3. **Initialize Configuration**
   ```bash
   powershell-assistant init
   ```

4. **Start the Server**
   ```bash
   powershell-assistant start
   ```

5. **Test Basic Functionality**
   ```bash
   # Test natural language processing
   curl -X POST http://localhost:8000/natural_language_to_powershell \
     -H "Content-Type: application/json" \
     -d '{"input_text": "list running processes"}'
   ```

## Key Concepts

### Sessions
- Each interaction creates or uses a session
- Sessions maintain context and history
- Sessions expire after inactivity

### Security Tiers
1. **Whitelist Validation**: Commands checked against security rules
2. **Permission Checking**: Administrative commands require confirmation
3. **Sandbox Execution**: Commands run in isolated Docker containers

### AI Processing
- Local AI models process natural language
- No data sent to external services
- Fallback to rule-based processing if AI unavailable

### Cross-Platform Support
- Automatic PowerShell detection (Core vs Windows PowerShell)
- Path separator conversion
- Platform-specific command adaptation

## Common Use Cases

### System Administration
```json
{
  "input_text": "show me processes using more than 100MB of memory",
  "session_id": "admin_session"
}
```

### File Management
```json
{
  "input_text": "find all log files modified in the last 24 hours",
  "session_id": "file_session"
}
```

### Service Management
```json
{
  "input_text": "restart the web server service",
  "session_id": "service_session"
}
```

### Performance Monitoring
```json
{
  "input_text": "show CPU and memory usage for the last hour",
  "session_id": "monitor_session"
}
```

## Best Practices

### Security
- Always use sandbox execution for untrusted commands
- Review generated commands before execution
- Configure appropriate security rules for your environment
- Monitor audit logs regularly

### Performance
- Use session IDs to maintain context
- Set appropriate timeouts for long-running commands
- Configure AI model parameters for your hardware
- Monitor resource usage

### Reliability
- Test commands in sandbox before production use
- Keep security rules updated
- Backup configuration and logs
- Monitor system health

## Integration Examples

### MCP Client Integration
```python
from mcp import Client

client = Client("ai-powershell-assistant")
response = await client.call_tool(
    "natural_language_to_powershell",
    {"input_text": "list all services"}
)
```

### REST API Integration
```bash
curl -X POST http://localhost:8000/execute_powershell_command \
  -H "Content-Type: application/json" \
  -d '{
    "command": "Get-Service | Where-Object Status -eq Running",
    "session_id": "api_session",
    "use_sandbox": true
  }'
```

### Command Line Integration
```bash
# Direct command execution
powershell-assistant exec "Get-Process | Sort-Object CPU -Descending"

# Natural language processing
powershell-assistant translate "show me running services"
```

## Next Steps

- [Configure](configuration.md) the system for your environment
- Learn about [Advanced Features](advanced-features.md)
- Set up [Security Settings](security.md)
- Optimize [Performance](performance.md)
- Check [Troubleshooting](../troubleshooting/README.md) if you encounter issues