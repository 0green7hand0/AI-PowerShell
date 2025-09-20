# Configuration Guide

This guide covers configuring the AI PowerShell Assistant for your environment and needs.

## Configuration Files

The system uses several configuration files:

- `config.yaml` - Main system configuration
- `security-rules.yaml` - Security policies and rules
- `logging.yaml` - Logging and audit configuration
- `ai-models.yaml` - AI model settings

Default location: `~/.powershell-assistant/` (or `%USERPROFILE%\.powershell-assistant\` on Windows)

## Main Configuration (config.yaml)

### Basic Configuration

```yaml
# System Information
version: "1.0.0"
platform: "auto"  # auto, windows, linux, macos

# Server Configuration
server:
  host: "localhost"
  port: 8000
  max_concurrent_sessions: 10
  session_timeout: 3600  # seconds
  enable_cors: true
  cors_origins: ["*"]

# MCP Server Settings
mcp_server:
  name: "AI PowerShell Assistant"
  version: "1.0.0"
  enable_natural_language_tool: true
  enable_execute_command_tool: true
  enable_system_info_tool: true
  max_request_size: 10485760  # 10MB
  request_timeout: 300  # seconds

# PowerShell Configuration
powershell:
  executable: "auto"  # auto, pwsh, powershell
  version_preference: "core"  # core, desktop, any
  default_timeout: 60  # seconds
  max_output_size: 1048576  # 1MB
  encoding: "utf-8"
  
# AI Model Configuration
ai_model:
  type: "llama-cpp"  # llama-cpp, ollama, transformers
  model_path: "~/.powershell-assistant/models/llama-7b-chat.bin"
  context_length: 4096
  temperature: 0.7
  max_tokens: 512
  batch_size: 8
  threads: 4  # CPU threads for inference
  gpu_layers: 0  # GPU layers (0 = CPU only)
  
# Security Configuration
security:
  sandbox_enabled: true
  docker_image: "mcr.microsoft.com/powershell:ubuntu-20.04"
  sandbox_timeout: 300  # seconds
  sandbox_memory_limit: "512m"
  sandbox_cpu_limit: "1.0"
  whitelist_enabled: true
  whitelist_path: "~/.powershell-assistant/security-rules.yaml"
  require_confirmation_for_admin: true
  audit_enabled: true
  
# Storage Configuration
storage:
  data_directory: "~/.powershell-assistant/data"
  log_directory: "~/.powershell-assistant/logs"
  backup_enabled: true
  backup_interval: 86400  # seconds (24 hours)
  retention_days: 30
  
# Logging Configuration
logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
  format: "json"  # json, text, structured
  outputs: ["file", "console"]  # file, console, syslog
  correlation_tracking: true
  performance_monitoring: true
  audit_trail: true
  sensitive_data_masking: true
```

### Environment-Specific Configuration

#### Development Environment

```yaml
# config-dev.yaml
server:
  host: "0.0.0.0"
  port: 8000
  
logging:
  level: "DEBUG"
  outputs: ["console", "file"]
  
security:
  sandbox_enabled: false  # Disable for faster development
  require_confirmation_for_admin: false
  
ai_model:
  temperature: 0.9  # More creative responses
  max_tokens: 1024
```

#### Production Environment

```yaml
# config-prod.yaml
server:
  host: "127.0.0.1"
  port: 8000
  max_concurrent_sessions: 50
  
logging:
  level: "WARNING"
  outputs: ["file", "syslog"]
  
security:
  sandbox_enabled: true
  require_confirmation_for_admin: true
  audit_enabled: true
  
ai_model:
  temperature: 0.5  # More deterministic responses
  max_tokens: 256
  gpu_layers: 32  # Use GPU acceleration
```

## Security Rules Configuration (security-rules.yaml)

### Rule Structure

```yaml
version: "1.0.0"
last_updated: "2024-01-15T10:30:45Z"

# Global Security Settings
global:
  default_action: "block"  # allow, block, confirm
  risk_threshold: "medium"  # low, medium, high, critical
  enable_learning: true
  
# Command Categories
categories:
  safe_commands:
    description: "Safe read-only commands"
    action: "allow"
    risk_level: "low"
    patterns:
      - "^Get-"
      - "^Show-"
      - "^Test-Connection"
      - "^Measure-"
      
  administrative_commands:
    description: "Administrative commands requiring confirmation"
    action: "confirm"
    risk_level: "high"
    patterns:
      - "^Set-"
      - "^New-"
      - "^Remove-"
      - "^Start-Service"
      - "^Stop-Service"
      - "^Restart-"
      
  dangerous_commands:
    description: "Potentially dangerous commands"
    action: "block"
    risk_level: "critical"
    patterns:
      - "Remove-Item.*-Recurse"
      - "Format-Volume"
      - "Clear-Host"
      - "rm -rf"
      - "del /s"

# Specific Rules (override categories)
rules:
  - name: "allow_process_management"
    pattern: "^Get-Process"
    action: "allow"
    risk_level: "low"
    description: "Allow process listing"
    
  - name: "block_system_shutdown"
    pattern: "Stop-Computer|Restart-Computer|shutdown"
    action: "block"
    risk_level: "critical"
    description: "Block system shutdown commands"
    
  - name: "confirm_service_changes"
    pattern: "(Start|Stop|Restart)-Service"
    action: "confirm"
    risk_level: "high"
    description: "Require confirmation for service changes"
    confirmation_message: "This command will modify system services. Continue?"

# User-Specific Rules
user_rules:
  admin_users:
    - "administrator"
    - "root"
    additional_permissions:
      - "administrative_commands"
      
  standard_users:
    - "*"  # All other users
    restrictions:
      - "dangerous_commands"
      
# Context-Based Rules
context_rules:
  working_directory:
    system_directories:
      paths: ["/system", "C:\\Windows", "/etc"]
      additional_restrictions: ["administrative_commands"]
      
  time_based:
    business_hours:
      start: "09:00"
      end: "17:00"
      timezone: "UTC"
      relaxed_rules: true
```

### Custom Security Rules

```yaml
# Add custom rules for your environment
custom_rules:
  - name: "allow_company_scripts"
    pattern: ".*\\CompanyScripts\\.*"
    action: "allow"
    risk_level: "low"
    description: "Allow execution of approved company scripts"
    
  - name: "block_external_downloads"
    pattern: "Invoke-WebRequest|wget|curl.*http"
    action: "block"
    risk_level: "high"
    description: "Block external download commands"
    
  - name: "monitor_registry_access"
    pattern: ".*Registry.*"
    action: "confirm"
    risk_level: "medium"
    description: "Monitor registry access"
    audit_level: "detailed"
```

## AI Model Configuration (ai-models.yaml)

### Model Definitions

```yaml
models:
  llama-7b-chat:
    type: "llama-cpp"
    path: "~/.powershell-assistant/models/llama-7b-chat.bin"
    context_length: 4096
    parameters:
      temperature: 0.7
      top_p: 0.9
      top_k: 40
      repeat_penalty: 1.1
    system_prompt: |
      You are an AI assistant that converts natural language to PowerShell commands.
      Always provide safe, accurate commands with explanations.
      
  codellama-13b:
    type: "llama-cpp"
    path: "~/.powershell-assistant/models/codellama-13b.bin"
    context_length: 8192
    parameters:
      temperature: 0.5
      top_p: 0.95
    system_prompt: |
      You are a PowerShell expert. Generate precise, efficient commands.
      
  ollama-mistral:
    type: "ollama"
    model_name: "mistral:7b"
    endpoint: "http://localhost:11434"
    parameters:
      temperature: 0.6
      num_predict: 256

# Model Selection Strategy
selection:
  primary: "llama-7b-chat"
  fallback: ["codellama-13b", "ollama-mistral"]
  auto_switch: true
  performance_threshold: 2.0  # seconds
  
# Model Management
management:
  auto_download: true
  update_check: true
  cleanup_old_models: true
  max_models: 3
```

## Logging Configuration (logging.yaml)

### Logging Setup

```yaml
version: "1.0.0"

# Root Logger Configuration
root:
  level: "INFO"
  handlers: ["console", "file", "audit"]
  
# Handler Definitions
handlers:
  console:
    type: "console"
    level: "INFO"
    format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
  file:
    type: "rotating_file"
    level: "DEBUG"
    filename: "~/.powershell-assistant/logs/app.log"
    max_bytes: 10485760  # 10MB
    backup_count: 5
    format: "%(asctime)s - %(name)s - %(levelname)s - %(correlation_id)s - %(message)s"
    
  audit:
    type: "rotating_file"
    level: "INFO"
    filename: "~/.powershell-assistant/logs/audit.log"
    max_bytes: 52428800  # 50MB
    backup_count: 10
    format: "%(asctime)s - AUDIT - %(correlation_id)s - %(message)s"
    
  syslog:
    type: "syslog"
    level: "WARNING"
    address: ["localhost", 514]
    facility: "local0"

# Component-Specific Logging
loggers:
  ai_engine:
    level: "INFO"
    handlers: ["file"]
    propagate: false
    
  security_engine:
    level: "WARNING"
    handlers: ["file", "audit"]
    propagate: false
    
  execution_engine:
    level: "INFO"
    handlers: ["file", "audit"]
    propagate: false
    
  mcp_server:
    level: "INFO"
    handlers: ["console", "file"]
    propagate: false

# Audit Configuration
audit:
  enabled: true
  events:
    - "user_input"
    - "ai_processing"
    - "security_validation"
    - "command_execution"
    - "error_events"
  correlation_tracking: true
  performance_metrics: true
  sensitive_data_masking:
    enabled: true
    patterns:
      - "password"
      - "secret"
      - "token"
      - "key"
```

## Environment Variables

Override configuration with environment variables:

```bash
# Server Configuration
export POWERSHELL_ASSISTANT_HOST="0.0.0.0"
export POWERSHELL_ASSISTANT_PORT="8080"

# AI Model Configuration
export POWERSHELL_ASSISTANT_AI_MODEL_PATH="/custom/path/model.bin"
export POWERSHELL_ASSISTANT_AI_TEMPERATURE="0.8"

# Security Configuration
export POWERSHELL_ASSISTANT_SANDBOX_ENABLED="true"
export POWERSHELL_ASSISTANT_DOCKER_IMAGE="custom/powershell:latest"

# Logging Configuration
export POWERSHELL_ASSISTANT_LOG_LEVEL="DEBUG"
export POWERSHELL_ASSISTANT_LOG_DIR="/var/log/powershell-assistant"
```

## Configuration Validation

### Validate Configuration

```bash
# Validate all configuration files
powershell-assistant validate-config

# Validate specific configuration
powershell-assistant validate-config --type security
powershell-assistant validate-config --type ai-model
powershell-assistant validate-config --type logging

# Test configuration
powershell-assistant test-config
```

### Configuration Templates

Generate configuration templates:

```bash
# Generate default configuration
powershell-assistant generate-config --type default

# Generate production configuration
powershell-assistant generate-config --type production

# Generate development configuration
powershell-assistant generate-config --type development

# Generate minimal configuration
powershell-assistant generate-config --type minimal
```

## Advanced Configuration

### Custom AI Prompts

```yaml
# Custom prompts for different scenarios
ai_prompts:
  system_administration:
    prompt: |
      You are a Windows system administrator. Generate PowerShell commands for:
      - System monitoring and diagnostics
      - User and group management
      - Service management
      - Performance optimization
      
  file_management:
    prompt: |
      You are a file management expert. Generate PowerShell commands for:
      - File and directory operations
      - Permission management
      - Search and filtering
      - Backup and archival
```

### Performance Tuning

```yaml
performance:
  ai_processing:
    batch_size: 8
    parallel_requests: 4
    cache_size: 1000
    
  command_execution:
    pool_size: 10
    timeout_buffer: 5  # seconds
    retry_attempts: 3
    
  memory_management:
    max_memory_usage: "2GB"
    garbage_collection_interval: 300  # seconds
    cache_cleanup_interval: 600  # seconds
```

### Integration Settings

```yaml
integrations:
  prometheus:
    enabled: true
    endpoint: "/metrics"
    port: 9090
    
  elasticsearch:
    enabled: false
    hosts: ["localhost:9200"]
    index_pattern: "powershell-assistant-{date}"
    
  webhook:
    enabled: false
    url: "https://your-webhook-endpoint.com"
    events: ["security_violation", "error"]
```

## Configuration Management

### Version Control

```bash
# Initialize configuration repository
cd ~/.powershell-assistant
git init
git add *.yaml
git commit -m "Initial configuration"

# Track configuration changes
git add -A
git commit -m "Updated security rules"
```

### Backup and Restore

```bash
# Backup configuration
powershell-assistant backup-config --output config-backup.tar.gz

# Restore configuration
powershell-assistant restore-config --input config-backup.tar.gz

# Export configuration
powershell-assistant export-config --format yaml --output exported-config.yaml
```

## Next Steps

- Learn about [Basic Usage](usage.md)
- Set up [Security Settings](security.md) in detail
- Explore [Advanced Features](advanced-features.md)
- Optimize [Performance](performance.md)