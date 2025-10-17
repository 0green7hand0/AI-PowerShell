# Configuration Management API - Quick Reference

## Endpoints

### GET /api/config
Get current application configuration.

**Response:**
```json
{
  "success": true,
  "data": {
    "ai": {
      "provider": "openai",
      "model_name": "gpt-4",
      "temperature": 0.7,
      "max_tokens": 2000
    },
    "security": {
      "whitelist_mode": true,
      "require_confirmation": true,
      "dangerous_patterns": []
    },
    "execution": {
      "timeout": 30,
      "shell_type": "powershell",
      "encoding": "utf-8"
    },
    "general": {
      "language": "zh-CN",
      "theme": "light",
      "log_level": "INFO"
    }
  }
}
```

### PUT /api/config
Update application configuration (partial updates supported).

**Request:**
```json
{
  "ai": {
    "temperature": 0.8
  },
  "security": {
    "require_confirmation": false
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": { /* updated config */ },
  "message": "Configuration updated successfully. Some changes may require restart."
}
```

## Configuration Fields

### AI Configuration
| Field | Type | Description | Example |
|-------|------|-------------|---------|
| provider | string | AI provider | "openai", "ollama" |
| model_name | string | Model name | "gpt-4", "llama2" |
| temperature | float | Generation temperature (0.0-1.0) | 0.7 |
| max_tokens | integer | Maximum tokens | 2000 |

### Security Configuration
| Field | Type | Description | Example |
|-------|------|-------------|---------|
| whitelist_mode | boolean | Enable strict whitelist | true, false |
| require_confirmation | boolean | Require confirmation for dangerous commands | true, false |
| dangerous_patterns | array | List of dangerous patterns | [] |

### Execution Configuration
| Field | Type | Description | Example |
|-------|------|-------------|---------|
| timeout | integer | Execution timeout (seconds) | 30 |
| shell_type | string | Shell type | "powershell", "pwsh" |
| encoding | string | Output encoding | "utf-8", "utf-16" |

### General Configuration
| Field | Type | Description | Example |
|-------|------|-------------|---------|
| language | string | UI language | "zh-CN", "en-US" |
| theme | string | UI theme | "light", "dark" |
| log_level | string | Logging level | "DEBUG", "INFO", "WARNING", "ERROR" |

## Error Responses

### 400 Bad Request
```json
{
  "success": false,
  "error": {
    "message": "Invalid JSON in request body",
    "code": 400
  }
}
```

### 400 Validation Error
```json
{
  "success": false,
  "error": {
    "message": "Validation error",
    "details": [
      {
        "loc": ["temperature"],
        "msg": "value must be between 0 and 1",
        "type": "value_error"
      }
    ],
    "code": 400
  }
}
```

### 500 Internal Server Error
```json
{
  "success": false,
  "error": {
    "message": "Failed to update configuration: ...",
    "code": 500
  }
}
```

## Usage Examples

### JavaScript/TypeScript (Axios)

```typescript
// Get configuration
const getConfig = async () => {
  const response = await axios.get('/api/config');
  return response.data.data;
};

// Update configuration
const updateConfig = async (updates: Partial<AppConfig>) => {
  const response = await axios.put('/api/config', updates);
  return response.data;
};

// Example: Update AI settings
await updateConfig({
  ai: {
    temperature: 0.8,
    max_tokens: 3000
  }
});
```

### Python (requests)

```python
import requests

# Get configuration
response = requests.get('http://localhost:5000/api/config')
config = response.json()['data']

# Update configuration
updates = {
    'ai': {
        'temperature': 0.8
    },
    'security': {
        'require_confirmation': False
    }
}
response = requests.put('http://localhost:5000/api/config', json=updates)
```

### cURL

```bash
# Get configuration
curl http://localhost:5000/api/config

# Update configuration
curl -X PUT http://localhost:5000/api/config \
  -H "Content-Type: application/json" \
  -d '{
    "ai": {
      "temperature": 0.8
    }
  }'
```

## Notes

- **Partial Updates:** Only send fields you want to update
- **Restart Required:** Some changes may require application restart
- **Whitelist Mode:** Stored as 'strict'/'permissive' internally, exposed as boolean
- **Validation:** All values are validated before being applied
- **Unknown Fields:** Safely ignored, won't cause errors
- **Atomic Updates:** All updates in a single request are applied together

## Testing

```bash
# Run unit tests
cd web-ui/backend
python -m pytest tests/test_config_api.py -v

# Run verification script
python verify_config_api.py
```
