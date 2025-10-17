# Backend Architecture

## Overview

The backend is built using Flask and follows a modular blueprint-based architecture. It provides RESTful APIs for the frontend to interact with the AI PowerShell Assistant.

## Architecture Layers

```
┌─────────────────────────────────────────┐
│         Frontend (Vue 3)                │
└─────────────────┬───────────────────────┘
                  │ HTTP/WebSocket
┌─────────────────▼───────────────────────┐
│         Flask Application               │
│  ┌─────────────────────────────────┐   │
│  │   CORS Middleware               │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │   API Blueprints                │   │
│  │  - Command API                  │   │
│  │  - History API                  │   │
│  │  - Template API                 │   │
│  │  - Config API                   │   │
│  │  - Logs API                     │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │   Pydantic Models               │   │
│  │  (Request/Response Validation)  │   │
│  └─────────────────────────────────┘   │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│   PowerShellAssistant (Existing)        │
│  - AI Engine                            │
│  - Security Engine                      │
│  - Execution Engine                     │
│  - Storage Engine                       │
│  - Template Engine                      │
│  - Config Manager                       │
└─────────────────────────────────────────┘
```

## Directory Structure

```
backend/
├── api/                    # API Blueprint modules
│   ├── __init__.py
│   ├── command.py         # Command translation & execution endpoints
│   ├── history.py         # History management endpoints
│   ├── template.py        # Template management endpoints
│   ├── config.py          # Configuration endpoints
│   └── logs.py            # Logging endpoints
│
├── models/                # Pydantic data models
│   ├── __init__.py
│   ├── command.py         # Command-related models
│   ├── history.py         # History-related models
│   ├── template.py        # Template-related models
│   └── config.py          # Configuration models
│
├── app.py                 # Flask application factory
├── requirements.txt       # Python dependencies
├── README.md             # Setup and usage guide
├── ARCHITECTURE.md       # This file
├── test_import.py        # Import verification script
├── run.bat               # Windows batch startup script
├── run.ps1               # PowerShell startup script
└── .gitignore            # Git ignore rules
```

## API Blueprints

### Command API (`api/command.py`)

Handles command translation and execution.

**Endpoints:**
- `POST /api/command/translate` - Translate natural language to PowerShell
- `POST /api/command/execute` - Execute PowerShell command

**Models:**
- `TranslateRequest` - Input for translation
- `TranslateResponse` - Translation result with security info
- `ExecuteRequest` - Command execution request
- `ExecuteResponse` - Execution result

### History API (`api/history.py`)

Manages command execution history.

**Endpoints:**
- `GET /api/history` - List history with pagination
- `GET /api/history/:id` - Get specific history item
- `DELETE /api/history/:id` - Delete history item

**Models:**
- `HistoryItem` - Single history record
- `HistoryListResponse` - Paginated history list

### Template API (`api/template.py`)

Manages PowerShell script templates.

**Endpoints:**
- `GET /api/templates` - List templates
- `GET /api/templates/:id` - Get template details
- `POST /api/templates` - Create new template
- `PUT /api/templates/:id` - Update template
- `DELETE /api/templates/:id` - Delete template
- `POST /api/templates/:id/generate` - Generate script from template

**Models:**
- `Template` - Template definition
- `TemplateParameter` - Template parameter definition
- `GenerateScriptRequest` - Script generation request

### Config API (`api/config.py`)

Manages application configuration.

**Endpoints:**
- `GET /api/config` - Get current configuration
- `PUT /api/config` - Update configuration

**Models:**
- `AppConfig` - Complete application configuration
- `AIConfig` - AI engine settings
- `SecurityConfig` - Security settings
- `ExecutionConfig` - Execution settings
- `GeneralConfig` - General settings

### Logs API (`api/logs.py`)

Provides access to system logs.

**Endpoints:**
- `GET /api/logs` - Get logs with filtering
- `WebSocket /ws/logs` - Real-time log streaming

## Data Models

All data models use Pydantic for validation and serialization.

### Benefits of Pydantic:
1. **Automatic validation** - Invalid data is rejected with clear error messages
2. **Type safety** - Ensures data types match expectations
3. **Documentation** - Models serve as API documentation
4. **Serialization** - Easy conversion to/from JSON

### Example Model:

```python
from pydantic import BaseModel, Field

class TranslateRequest(BaseModel):
    input: str = Field(..., description="Natural language input")
    context: Optional[dict] = Field(default=None, description="Context")
```

## Error Handling

All endpoints follow a consistent error response format:

```json
{
  "success": false,
  "error": {
    "message": "Error description",
    "code": 400,
    "details": {}  // Optional validation details
  }
}
```

### Error Types:
- **400 Bad Request** - Validation errors, invalid input
- **404 Not Found** - Resource not found
- **500 Internal Server Error** - Server-side errors

## CORS Configuration

CORS is configured to allow requests from:
- `http://localhost:5173` (Vite dev server)
- `http://localhost:3000` (Alternative frontend port)

Allowed methods: GET, POST, PUT, DELETE, OPTIONS

## WebSocket Support

Flask-SocketIO is used for real-time log streaming.

**Connection:**
```javascript
const socket = io('http://localhost:5000');
socket.on('log', (data) => {
  console.log('New log:', data);
});
```

## Integration Points

The backend is designed to integrate with the existing PowerShellAssistant:

### Command Translation
```python
from src.ai_engine import AIEngine

ai_engine = AIEngine()
result = ai_engine.translate(user_input)
```

### Command Execution
```python
from src.execution import Executor

executor = Executor()
result = executor.execute(command)
```

### History Storage
```python
from src.storage import StorageEngine

storage = StorageEngine()
history = storage.get_history()
```

### Template Management
```python
from src.template_engine import TemplateEngine

template_engine = TemplateEngine()
templates = template_engine.list_templates()
```

## Security Considerations

1. **Input Validation** - All inputs validated with Pydantic
2. **CORS** - Restricted to known origins
3. **Command Execution** - Security checks before execution
4. **Error Messages** - No sensitive information in errors
5. **Secret Key** - Must be changed in production

## Testing

### Manual Testing

Use the test script to verify imports:
```bash
python test_import.py
```

### API Testing

Use cURL, Postman, or the frontend to test endpoints:

```bash
# Health check
curl http://localhost:5000/api/health

# Translate command
curl -X POST http://localhost:5000/api/command/translate \
  -H "Content-Type: application/json" \
  -d '{"input": "显示当前时间"}'
```

## Deployment

### Development
```bash
python app.py
```

### Production
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker (Future)
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## Future Enhancements

1. **Authentication** - JWT-based authentication
2. **Rate Limiting** - Prevent API abuse
3. **Caching** - Redis for session/response caching
4. **Database** - PostgreSQL for persistent storage
5. **Monitoring** - Prometheus metrics
6. **API Documentation** - Swagger/OpenAPI
7. **Testing** - Unit and integration tests
8. **Logging** - Structured logging with rotation

## Development Guidelines

### Adding New Endpoints

1. Create/modify blueprint in `api/`
2. Define models in `models/`
3. Register blueprint in `app.py`
4. Update this documentation

### Code Style

- Follow PEP 8
- Use type hints
- Add docstrings to functions
- Keep functions small and focused
- Use meaningful variable names

### Commit Messages

- Use clear, descriptive messages
- Reference issue numbers
- Follow conventional commits format
