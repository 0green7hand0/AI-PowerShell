# Backend API Quick Start Guide

## Prerequisites

1. Python 3.8 or higher
2. PowerShellAssistant installed and configured
3. Required Python packages

## Installation

### 1. Install Dependencies

```bash
cd web-ui/backend
pip install flask flask-cors flask-socketio pydantic
```

### 2. Verify PowerShellAssistant

Make sure the PowerShellAssistant is accessible:

```bash
# From the backend directory
python -c "import sys; sys.path.insert(0, '../..'); from src.main import PowerShellAssistant; print('✓ PowerShellAssistant found')"
```

## Running the Backend

### Development Mode

```bash
cd web-ui/backend
python app.py
```

The server will start on `http://localhost:5000`

### Using the Run Scripts

**Windows (PowerShell):**
```powershell
.\run.ps1
```

**Windows (Batch):**
```cmd
run.bat
```

## Testing the API

### 1. Run the Test Suite

```bash
python test_api.py
```

### 2. Manual Testing with curl

**Health Check:**
```bash
curl http://localhost:5000/api/health
```

**Translate Command:**
```bash
curl -X POST http://localhost:5000/api/command/translate \
  -H "Content-Type: application/json" \
  -d "{\"input\": \"显示当前时间\"}"
```

**Get History:**
```bash
curl http://localhost:5000/api/history?page=1&limit=10
```

**Get Templates:**
```bash
curl http://localhost:5000/api/templates
```

**Get Configuration:**
```bash
curl http://localhost:5000/api/config
```

**Get Logs:**
```bash
curl http://localhost:5000/api/logs?limit=10
```

### 3. Using Postman or Insomnia

Import the following endpoints:

- `GET  /api/health` - Health check
- `POST /api/command/translate` - Translate natural language
- `POST /api/command/execute` - Execute command
- `GET  /api/history` - Get history list
- `GET  /api/history/:id` - Get history detail
- `DELETE /api/history/:id` - Delete history item
- `GET  /api/templates` - Get templates list
- `GET  /api/templates/:id` - Get template detail
- `POST /api/templates` - Create template
- `PUT  /api/templates/:id` - Update template
- `DELETE /api/templates/:id` - Delete template
- `POST /api/templates/:id/generate` - Generate script
- `GET  /api/config` - Get configuration
- `PUT  /api/config` - Update configuration
- `GET  /api/logs` - Get logs

## API Documentation

See `API.md` for detailed API documentation.

## Troubleshooting

### Issue: "Failed to initialize PowerShellAssistant"

**Solution:** Make sure you're running from the correct directory and PowerShellAssistant is installed:

```bash
cd web-ui/backend
python -c "import sys; sys.path.insert(0, '../..'); from src.main import PowerShellAssistant"
```

### Issue: "Module not found"

**Solution:** Install missing dependencies:

```bash
pip install flask flask-cors flask-socketio pydantic
```

### Issue: "Port 5000 already in use"

**Solution:** Change the port in `app.py`:

```python
if __name__ == '__main__':
    app, socketio = create_app()
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)  # Changed to 5001
```

### Issue: "CORS errors from frontend"

**Solution:** Update CORS origins in `app.py`:

```python
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5173", "http://localhost:3000", "http://your-frontend-url"],
        ...
    }
})
```

## Development Tips

### Enable Debug Mode

Debug mode is enabled by default. To disable:

```python
app.config['DEBUG'] = False
```

### View Logs

Logs are written to the file specified in PowerShellAssistant config (default: `logs/assistant.log`)

```bash
tail -f ../../logs/assistant.log
```

### Hot Reload

Flask automatically reloads when you save changes in debug mode.

## Next Steps

1. Start the backend server
2. Run the test suite to verify everything works
3. Proceed to frontend development (Task 3+)
4. Integrate frontend with backend APIs

## Support

For issues or questions:
1. Check the logs in `logs/assistant.log`
2. Review `TASK_2_SUMMARY.md` for implementation details
3. See `API.md` for API documentation
