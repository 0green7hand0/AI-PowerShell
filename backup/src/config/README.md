# Configuration System Documentation

The AI PowerShell Assistant uses a comprehensive configuration system that supports multiple configuration sources, environment-based overrides, and validation.

## Configuration Files

### Main Configuration File

The main configuration file is located at `~/.ai-powershell-assistant/config/config.yaml` by default. It supports both YAML and JSON formats.

**Example configuration file:**
```yaml
# AI Model Configuration
model:
  model_type: "llama-cpp"
  model_path: "~/.ai-powershell-assistant/models/default.gguf"
  context_length: 4096
  temperature: 0.7

# Security Configuration
security:
  sandbox_enabled: true
  require_confirmation_for_admin: true
  
# Logging Configuration
logging:
  log_level: "info"
  log_format: "json"
```

### Security Whitelist Configuration

The security whitelist is configured in `~/.ai-powershell-assistant/config/security_whitelist.json`. This file defines which PowerShell commands are allowed, require confirmation, or are blocked.

### User Preferences

User preferences are stored in `~/.ai-powershell-assistant/data/user_preferences.json` and include interface settings, AI behavior preferences, and command history.

## Configuration Sections

### Model Configuration (`model`)

Controls AI model behavior and settings:

- `model_type`: Type of AI model ("llama-cpp", "ollama", "transformers")
- `model_path`: Path to model file or model name
- `context_length`: Maximum context length for the model
- `temperature`: Creativity level (0.0-2.0)
- `max_tokens`: Maximum tokens to generate
- `gpu_layers`: Number of GPU layers to use
- `threads`: Number of CPU threads

### Security Configuration (`security`)

Controls security and sandbox settings:

- `sandbox_enabled`: Enable Docker sandbox execution
- `sandbox_image`: Docker image for sandbox
- `require_confirmation_for_admin`: Require confirmation for admin commands
- `whitelist_path`: Path to security whitelist file
- `max_sandbox_memory`: Memory limit for sandbox
- `sandbox_timeout`: Execution timeout in seconds

### Logging Configuration (`logging`)

Controls logging behavior:

- `log_level`: Minimum log level ("debug", "info", "warning", "error", "critical")
- `log_format`: Log format ("json", "text", "structured")
- `log_output`: Output destinations (["file", "console", "syslog", "elasticsearch"])
- `enable_correlation_tracking`: Enable request correlation IDs
- `sensitive_data_masking`: Mask sensitive data in logs

### Storage Configuration (`storage`)

Controls data storage settings:

- `data_directory`: Directory for application data
- `history_max_entries`: Maximum command history entries
- `backup_enabled`: Enable automatic backups
- `backup_interval_hours`: Backup frequency

### Execution Configuration (`execution`)

Controls PowerShell execution:

- `default_timeout`: Default command timeout in seconds
- `max_output_size`: Maximum output size to capture
- `powershell_executable`: Path to PowerShell executable
- `environment_variables`: Additional environment variables

### MCP Server Configuration (`mcp_server`)

Controls MCP server settings:

- `host`: Server bind address
- `port`: Server port
- `max_concurrent_requests`: Maximum concurrent requests
- `enable_cors`: Enable CORS for web clients

## Environment Variable Overrides

Configuration values can be overridden using environment variables with the prefix `AI_PS_`:

### Model Configuration
- `AI_PS_MODEL_TYPE`: Override model type
- `AI_PS_MODEL_PATH`: Override model path
- `AI_PS_MODEL_CONTEXT_LENGTH`: Override context length
- `AI_PS_MODEL_TEMPERATURE`: Override temperature
- `AI_PS_MODEL_MAX_TOKENS`: Override max tokens

### Security Configuration
- `AI_PS_SECURITY_SANDBOX_ENABLED`: Enable/disable sandbox (true/false)
- `AI_PS_SECURITY_SANDBOX_IMAGE`: Override sandbox Docker image
- `AI_PS_SECURITY_WHITELIST_PATH`: Override whitelist file path
- `AI_PS_SECURITY_REQUIRE_ADMIN_CONFIRMATION`: Require admin confirmation (true/false)

### Logging Configuration
- `AI_PS_LOG_LEVEL`: Override log level (debug/info/warning/error/critical)
- `AI_PS_LOG_FORMAT`: Override log format (json/text/structured)
- `AI_PS_AUDIT_LOG_PATH`: Override audit log path

### Storage Configuration
- `AI_PS_DATA_DIRECTORY`: Override data directory
- `AI_PS_CACHE_DIRECTORY`: Override cache directory

### Execution Configuration
- `AI_PS_POWERSHELL_EXECUTABLE`: Override PowerShell executable path
- `AI_PS_DEFAULT_TIMEOUT`: Override default timeout

### MCP Server Configuration
- `AI_PS_MCP_HOST`: Override server host
- `AI_PS_MCP_PORT`: Override server port

### Global Settings
- `AI_PS_DEBUG_MODE`: Enable debug mode (true/false)
- `AI_PS_PLATFORM`: Override platform detection (windows/linux/macos)

## Configuration Loading Order

The configuration system loads settings in the following order (later sources override earlier ones):

1. **Default values** - Built-in defaults for all settings
2. **Configuration file** - Values from the main config file
3. **Environment variables** - Environment variable overrides

## Configuration Validation

The system validates all configuration values:

- **Model settings**: Context length must be positive, temperature between 0.0-2.0
- **Security settings**: Timeout values must be positive
- **Network settings**: Port numbers must be valid (1-65535)
- **File paths**: Paths are validated for accessibility

## Using the Configuration System

### Loading Configuration

```python
from config.manager import load_config, get_config

# Load configuration from default location
config = load_config()

# Load from specific file
config = load_config("/path/to/config.yaml")

# Get current configuration
config = get_config()
```

### Updating Configuration

```python
from config.manager import config_manager

# Update specific values
updates = {
    'model': {
        'temperature': 0.8,
        'max_tokens': 256
    },
    'security': {
        'sandbox_enabled': False
    }
}

config_manager.update_config(updates)
```

### Accessing Configuration Values

```python
config = get_config()

# Access model settings
model_type = config.model.model_type
temperature = config.model.temperature

# Access security settings
sandbox_enabled = config.security.sandbox_enabled
require_confirmation = config.security.require_confirmation_for_admin

# Access logging settings
log_level = config.logging.log_level
log_format = config.logging.log_format
```

## Configuration Templates

Template files are provided in the `templates/` directory:

- `config.yaml.template`: Main configuration template
- `security_whitelist.json.template`: Security whitelist template
- `user_preferences.json.template`: User preferences template

Copy these templates to create your initial configuration files.

## Directory Structure

The configuration system creates the following directory structure:

```
~/.ai-powershell-assistant/
├── config/
│   ├── config.yaml
│   └── security_whitelist.json
├── data/
│   └── user_preferences.json
├── logs/
│   ├── audit.log
│   └── performance.log
├── cache/
└── models/
    └── default.gguf
```

## Best Practices

1. **Use environment variables** for deployment-specific settings
2. **Keep sensitive data** out of configuration files
3. **Validate configuration** after making changes
4. **Backup configuration** files before major changes
5. **Use templates** as starting points for new configurations
6. **Monitor logs** for configuration-related errors
7. **Test configuration changes** in a safe environment first

## Troubleshooting

### Configuration Not Loading
- Check file permissions and accessibility
- Verify YAML/JSON syntax is valid
- Check for typos in environment variable names
- Review logs for specific error messages

### Invalid Configuration Values
- Ensure numeric values are within valid ranges
- Check that file paths exist and are accessible
- Verify enum values match expected options
- Use the validation system to identify issues

### Environment Variables Not Working
- Ensure variable names match the expected format
- Check that values are properly formatted for their types
- Verify environment variables are set in the correct scope
- Use boolean values: "true"/"false", "1"/"0", "yes"/"no"