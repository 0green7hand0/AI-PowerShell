# API Documentation

This document provides comprehensive reference for all MCP tools and interfaces in the AI PowerShell Assistant.

## Table of Contents

- [MCP Tools Overview](#mcp-tools-overview)
- [Tool Schemas](#tool-schemas)
- [Request/Response Formats](#requestresponse-formats)
- [Error Handling](#error-handling)
- [Authentication](#authentication)
- [Rate Limiting](#rate-limiting)

## MCP Tools Overview

The AI PowerShell Assistant provides three main MCP tools:

### 1. natural_language_to_powershell

Converts natural language descriptions into executable PowerShell commands using local AI models.

**Category**: Natural Language Processing  
**Status**: Available  
**Version**: 1.0.0

### 2. execute_powershell_command

Executes PowerShell commands with comprehensive security validation and returns formatted results.

**Category**: Command Execution  
**Status**: Available  
**Version**: 1.0.0

### 3. get_powershell_info

Retrieves PowerShell environment information, available modules, and system configuration.

**Category**: System Information  
**Status**: Available  
**Version**: 1.0.0

## Tool Schemas

### natural_language_to_powershell

#### Request Schema

```json
{
  "input_text": "string (required, 1-10000 chars)",
  "session_id": "string (optional)",
  "context": "object (optional)",
  "include_explanation": "boolean (default: true)",
  "include_alternatives": "boolean (default: true)",
  "confidence_threshold": "number (0.0-1.0, default: 0.5)"
}
```

#### Response Schema

```json
{
  "success": "boolean",
  "original_input": "string",
  "generated_command": "string",
  "confidence_score": "number (0.0-1.0)",
  "explanation": "string",
  "alternatives": ["string"],
  "session_id": "string",
  "correlation_id": "string",
  "processing_time_ms": "number",
  "warnings": ["string"],
  "error": "ToolError (if unsuccessful)"
}
```

#### Example Request

```json
{
  "input_text": "list all running processes sorted by CPU usage",
  "session_id": "sess_123",
  "include_explanation": true,
  "include_alternatives": true,
  "confidence_threshold": 0.7
}
```

#### Example Response

```json
{
  "success": true,
  "original_input": "list all running processes sorted by CPU usage",
  "generated_command": "Get-Process | Sort-Object CPU -Descending",
  "confidence_score": 0.95,
  "explanation": "This command gets all running processes and sorts them by CPU usage in descending order",
  "alternatives": [
    "Get-Process | Sort-Object CPU -Descending | Select-Object -First 10",
    "Get-Process | Where-Object {$_.CPU -gt 0} | Sort-Object CPU -Descending"
  ],
  "session_id": "sess_123",
  "correlation_id": "req_456789",
  "processing_time_ms": 245.7,
  "warnings": []
}
```

### execute_powershell_command

#### Request Schema

```json
{
  "command": "string (required, 1-50000 chars)",
  "session_id": "string (optional)",
  "timeout": "number (1-3600, default: 60)",
  "use_sandbox": "boolean (default: true)",
  "output_format": "string (JSON|TABLE|RAW, default: JSON)",
  "max_output_size": "number (1024-10485760, default: 1048576)",
  "working_directory": "string (optional)",
  "environment_variables": "object (optional)"
}
```

#### Response Schema

```json
{
  "success": "boolean",
  "return_code": "number",
  "stdout": "string",
  "stderr": "string",
  "execution_time": "number",
  "platform": "string",
  "sandbox_used": "boolean",
  "output_format": "string",
  "output_truncated": "boolean",
  "session_id": "string",
  "correlation_id": "string",
  "security_validation": "object",
  "performance_metrics": "object",
  "warnings": ["string"],
  "error": "ToolError (if unsuccessful)"
}
```

#### Example Request

```json
{
  "command": "Get-Process | Sort-Object CPU -Descending | Select-Object -First 5",
  "session_id": "sess_123",
  "timeout": 30,
  "use_sandbox": true,
  "output_format": "JSON"
}
```

#### Example Response

```json
{
  "success": true,
  "return_code": 0,
  "stdout": "[{\"ProcessName\":\"chrome\",\"CPU\":45.2},{\"ProcessName\":\"firefox\",\"CPU\":23.1}]",
  "stderr": "",
  "execution_time": 1.23,
  "platform": "Windows",
  "sandbox_used": true,
  "output_format": "JSON",
  "output_truncated": false,
  "session_id": "sess_123",
  "correlation_id": "req_789012",
  "security_validation": {
    "is_valid": true,
    "risk_level": "LOW",
    "rules_matched": ["safe_get_commands"]
  },
  "performance_metrics": {
    "memory_usage_mb": 45,
    "cpu_usage_percent": 12
  },
  "warnings": []
}
```

### get_powershell_info

#### Request Schema

```json
{
  "session_id": "string (optional)",
  "include_modules": "boolean (default: true)",
  "include_environment": "boolean (default: false)",
  "include_performance": "boolean (default: false)",
  "include_security": "boolean (default: false)",
  "module_filter": "string (optional)",
  "detailed_info": "boolean (default: false)"
}
```

#### Response Schema

```json
{
  "success": "boolean",
  "powershell": "object",
  "platform": "string",
  "server_version": "string",
  "modules": ["object"],
  "environment": "object",
  "performance": "object",
  "security": "object",
  "session_id": "string",
  "correlation_id": "string",
  "timestamp": "string",
  "warnings": ["string"],
  "error": "ToolError (if unsuccessful)"
}
```

#### Example Request

```json
{
  "session_id": "sess_123",
  "include_modules": true,
  "include_environment": false,
  "detailed_info": true
}
```

#### Example Response

```json
{
  "success": true,
  "powershell": {
    "version": "7.3.0",
    "edition": "Core",
    "platform": "Win32NT",
    "executable_path": "C:\\Program Files\\PowerShell\\7\\pwsh.exe"
  },
  "platform": "Windows",
  "server_version": "1.0.0",
  "modules": [
    {
      "name": "Microsoft.PowerShell.Management",
      "version": "7.3.0.0",
      "type": "Manifest"
    }
  ],
  "session_id": "sess_123",
  "correlation_id": "req_345678",
  "timestamp": "2024-01-15T10:30:45.123Z",
  "warnings": []
}
```

## Error Handling

All tools return standardized error responses when operations fail:

### ToolError Schema

```json
{
  "error_code": "string",
  "error_message": "string",
  "error_details": "object (optional)",
  "correlation_id": "string (optional)",
  "timestamp": "string",
  "recoverable": "boolean",
  "suggested_actions": ["string"]
}
```

### Common Error Codes

- `VALIDATION_ERROR`: Request validation failed
- `AI_MODEL_ERROR`: AI processing failed
- `SECURITY_VIOLATION`: Command blocked by security policy
- `EXECUTION_ERROR`: Command execution failed
- `TIMEOUT_ERROR`: Operation timed out
- `SANDBOX_ERROR`: Sandbox execution failed
- `PERMISSION_ERROR`: Insufficient permissions
- `UNKNOWN_TOOL`: Tool not found
- `SYSTEM_ERROR`: Internal system error

### Example Error Response

```json
{
  "success": false,
  "error": {
    "error_code": "SECURITY_VIOLATION",
    "error_message": "Command blocked by security policy",
    "error_details": {
      "blocked_reasons": ["Contains dangerous Remove-Item operation"],
      "risk_level": "HIGH"
    },
    "correlation_id": "req_123456",
    "timestamp": "2024-01-15T10:30:45.123Z",
    "recoverable": true,
    "suggested_actions": [
      "Use safer alternatives",
      "Request administrator approval",
      "Modify command to reduce risk"
    ]
  }
}
```

## Authentication

The MCP server uses session-based authentication:

1. **Session Creation**: Sessions are automatically created when not provided
2. **Session Tracking**: All requests are tracked by session ID
3. **Context Persistence**: User context is maintained across requests
4. **Session Expiry**: Sessions expire after configurable timeout

## Rate Limiting

Rate limiting is applied per session:

- **Default Limit**: 100 requests per minute per session
- **Burst Limit**: 10 requests per second
- **Timeout**: 429 status with retry-after header
- **Configuration**: Limits are configurable per tool

### Rate Limit Headers

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642248645
```

## Correlation IDs

All requests generate correlation IDs for tracing:

- **Format**: `req_` + 9-digit number
- **Usage**: Track requests through entire pipeline
- **Logging**: All log entries include correlation ID
- **Debugging**: Use correlation ID to trace issues

## Performance Considerations

- **AI Processing**: 100-500ms typical latency
- **Command Execution**: Varies by command complexity
- **Sandbox Overhead**: 50-200ms additional latency
- **Concurrent Requests**: Up to 10 concurrent per session
- **Memory Usage**: 50-200MB per active session

## Security Features

- **Input Validation**: All inputs validated against schemas
- **Command Filtering**: Three-tier security validation
- **Sandbox Execution**: Isolated execution environment
- **Audit Logging**: Complete audit trail maintained
- **Permission Checking**: Dynamic permission validation
- **Data Privacy**: All processing happens locally