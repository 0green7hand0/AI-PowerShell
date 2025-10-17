# AI PowerShell Assistant - Backend API

Flask-based REST API for the AI PowerShell Assistant Web UI.

## Setup

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. Create a virtual environment (recommended):
```bash
python -m venv venv
```

2. Activate the virtual environment:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Server

### Development Mode

```bash
python app.py
```

The server will start on `http://localhost:5000`

### Production Mode

For production deployment, use a WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## API Endpoints

### Health Check
- `GET /api/health` - Check if the API is running

### Command API
- `POST /api/command/translate` - Translate natural language to PowerShell
- `POST /api/command/execute` - Execute PowerShell command

### History API
- `GET /api/history` - Get command history list
- `GET /api/history/:id` - Get specific history item
- `DELETE /api/history/:id` - Delete history item

### Template API
- `GET /api/templates` - Get template list
- `GET /api/templates/:id` - Get specific template
- `POST /api/templates` - Create new template
- `PUT /api/templates/:id` - Update template
- `DELETE /api/templates/:id` - Delete template
- `POST /api/templates/:id/generate` - Generate script from template

### Config API
- `GET /api/config` - Get current configuration
- `PUT /api/config` - Update configuration

### Logs API
- `GET /api/logs` - Get system logs
- `WebSocket /ws/logs` - Real-time log streaming

## Project Structure

```
backend/
├── api/                    # API blueprints
│   ├── __init__.py
│   ├── command.py         # Command translation and execution
│   ├── history.py         # History management
│   ├── template.py        # Template management
│   ├── config.py          # Configuration management
│   └── logs.py            # Logs and monitoring
├── models/                # Pydantic data models
│   ├── __init__.py
│   ├── command.py
│   ├── history.py
│   ├── template.py
│   └── config.py
├── app.py                 # Flask application factory
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Configuration

The application can be configured through environment variables or by modifying the `app.py` file:

- `SECRET_KEY` - Flask secret key (change in production!)
- `DEBUG` - Enable/disable debug mode
- `CORS_ORIGINS` - Allowed CORS origins

## Integration with PowerShellAssistant

The API endpoints currently return placeholder responses. To integrate with the existing PowerShellAssistant:

1. Import the necessary modules from the main application
2. Replace placeholder responses with actual calls to:
   - `PowerShellAssistant.ai_engine` for command translation
   - `PowerShellAssistant.executor` for command execution
   - `PowerShellAssistant.storage` for history management
   - `PowerShellAssistant.template_engine` for template operations
   - `PowerShellAssistant.config_manager` for configuration
   - `PowerShellAssistant.log_engine` for logging

## Development

### Adding New Endpoints

1. Create or modify a blueprint in the `api/` directory
2. Define request/response models in the `models/` directory
3. Register the blueprint in `app.py`

### Error Handling

All endpoints follow a consistent error response format:

```json
{
  "success": false,
  "error": {
    "message": "Error description",
    "code": 400
  }
}
```

## Testing

To test the API endpoints, you can use:

- cURL
- Postman
- Python requests library
- The frontend application

Example cURL request:

```bash
curl -X POST http://localhost:5000/api/command/translate \
  -H "Content-Type: application/json" \
  -d '{"input": "显示当前时间"}'
```
