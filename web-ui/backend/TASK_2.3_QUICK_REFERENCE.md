# Task 2.3 Quick Reference: Command Execute API

## Endpoint
```
POST /api/command/execute
```

## Request Format
```json
{
  "command": "Get-Date",
  "session_id": "web-session-001",
  "timeout": 30  // optional, default: 30
}
```

## Response Format (Success)
```json
{
  "success": true,
  "data": {
    "output": "2025-10-08 14:30:00",
    "error": null,
    "execution_time": 0.234,
    "return_code": 0
  }
}
```

## Response Format (Error)
```json
{
  "success": false,
  "error": {
    "message": "Validation error",
    "code": 400
  }
}
```

## Status Codes
- `200` - Success (command executed, check return_code)
- `400` - Bad Request (invalid JSON or missing fields)
- `500` - Internal Server Error (execution failed)
- `503` - Service Unavailable (assistant not initialized)

## Testing
```bash
# Run unit tests
cd web-ui/backend
python -m pytest tests/test_command_api.py::TestExecuteEndpoint -v

# Run verification script
python verify_execute_api.py
```

## Files
- **Implementation:** `web-ui/backend/api/command.py`
- **Models:** `web-ui/backend/models/command.py`
- **Tests:** `web-ui/backend/tests/test_command_api.py`
- **Verification:** `web-ui/backend/verify_execute_api.py`

## Key Features
✅ Timeout control (default 30s, customizable)
✅ Execution time measurement
✅ Comprehensive error handling
✅ Execution logging
✅ 23 unit tests (all passing)
