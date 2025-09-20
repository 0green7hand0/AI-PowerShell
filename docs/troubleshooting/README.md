# Troubleshooting Guide

This guide helps you diagnose and resolve common issues with the AI PowerShell Assistant.

## Table of Contents

- [Common Issues](#common-issues)
- [Installation Problems](#installation-problems)
- [Configuration Issues](#configuration-issues)
- [Runtime Errors](#runtime-errors)
- [Performance Problems](#performance-problems)
- [Security Issues](#security-issues)
- [Diagnostic Tools](#diagnostic-tools)
- [Getting Help](#getting-help)

## Common Issues

### Server Won't Start

#### Symptoms
- Server fails to start
- Port binding errors
- Configuration validation errors

#### Diagnosis
```bash
# Check server status
powershell-assistant status

# Validate configuration
powershell-assistant validate-config

# Check port availability
netstat -an | grep 8000  # Linux/macOS
netstat -an | findstr 8000  # Windows
```

#### Solutions

**Port Already in Use**
```bash
# Find process using port
lsof -i :8000  # Linux/macOS
netstat -ano | findstr :8000  # Windows

# Kill process or use different port
powershell-assistant start --port 8001
```

**Configuration Errors**
```bash
# Generate new configuration
powershell-assistant init --force

# Use minimal configuration
powershell-assistant start --config minimal
```

**Permission Issues**
```bash
# Run with appropriate permissions
sudo powershell-assistant start  # Linux/macOS (if needed)

# Check file permissions
ls -la ~/.powershell-assistant/  # Linux/macOS
```

### AI Model Not Loading

#### Symptoms
- Natural language processing fails
- "AI model not available" errors
- Slow response times

#### Diagnosis
```bash
# Check AI model status
powershell-assistant test --ai

# View AI engine logs
powershell-assistant logs --component ai_engine

# Check model file
ls -la ~/.powershell-assistant/models/
```

#### Solutions

**Model File Missing**
```bash
# Download default model
powershell-assistant download-model --model llama-7b-chat

# Verify download
powershell-assistant test --ai
```

**Insufficient Memory**
```bash
# Check system memory
free -h  # Linux
Get-ComputerInfo | Select-Object TotalPhysicalMemory  # PowerShell

# Use smaller model
powershell-assistant config set ai_model.model_path "path/to/smaller/model.bin"

# Reduce context length
powershell-assistant config set ai_model.context_length 2048
```

**GPU Issues**
```bash
# Disable GPU acceleration
powershell-assistant config set ai_model.gpu_layers 0

# Check CUDA availability
nvidia-smi  # If using NVIDIA GPU
```

### PowerShell Not Found

#### Symptoms
- "PowerShell executable not found" errors
- Command execution failures
- Platform detection issues

#### Diagnosis
```bash
# Check PowerShell installation
which pwsh  # Linux/macOS
where pwsh  # Windows
pwsh --version

# Test PowerShell execution
powershell-assistant test --powershell
```

#### Solutions

**Install PowerShell**
```bash
# Windows (PowerShell Core)
winget install Microsoft.PowerShell

# Linux (Ubuntu/Debian)
sudo apt-get install -y powershell

# macOS
brew install powershell/tap/powershell
```

**Configure PowerShell Path**
```bash
# Set custom PowerShell executable
powershell-assistant config set powershell.executable "/usr/local/bin/pwsh"

# Auto-detect PowerShell
powershell-assistant config set powershell.executable "auto"
```

### Docker/Sandbox Issues

#### Symptoms
- Sandbox execution failures
- Docker connection errors
- Container startup problems

#### Diagnosis
```bash
# Check Docker status
docker --version
docker ps

# Test sandbox execution
powershell-assistant test --sandbox

# Check Docker permissions
docker run hello-world
```

#### Solutions

**Docker Not Running**
```bash
# Start Docker service
sudo systemctl start docker  # Linux
# Start Docker Desktop on Windows/macOS

# Enable Docker service
sudo systemctl enable docker  # Linux
```

**Permission Issues**
```bash
# Add user to docker group (Linux)
sudo usermod -aG docker $USER
newgrp docker

# Test Docker access
docker run hello-world
```

**Disable Sandbox (Temporary)**
```bash
# Disable sandbox for testing
powershell-assistant config set security.sandbox_enabled false

# Re-enable after fixing Docker
powershell-assistant config set security.sandbox_enabled true
```

## Installation Problems

### Python Version Issues

#### Problem
```
ERROR: Python 3.7 is not supported. Please upgrade to Python 3.8 or higher.
```

#### Solution
```bash
# Check Python version
python --version

# Install Python 3.8+ (Ubuntu/Debian)
sudo apt update
sudo apt install python3.8 python3.8-pip

# Use pyenv for version management
pyenv install 3.11.0
pyenv global 3.11.0
```

### Package Installation Failures

#### Problem
```
ERROR: Could not install packages due to an EnvironmentError
```

#### Solutions
```bash
# Use virtual environment
python -m venv ai-powershell-assistant
source ai-powershell-assistant/bin/activate  # Linux/macOS
ai-powershell-assistant\Scripts\activate  # Windows

# Upgrade pip
pip install --upgrade pip

# Install with user flag
pip install --user ai-powershell-assistant

# Clear pip cache
pip cache purge
```

### Dependency Conflicts

#### Problem
```
ERROR: pip's dependency resolver does not currently consider all the packages that are installed
```

#### Solutions
```bash
# Create fresh virtual environment
python -m venv fresh_env
source fresh_env/bin/activate

# Install specific versions
pip install ai-powershell-assistant==1.0.0

# Use requirements.txt
pip install -r requirements.txt --force-reinstall
```

## Configuration Issues

### Invalid Configuration Format

#### Problem
```
ERROR: Configuration validation failed: Invalid YAML format
```

#### Solutions
```bash
# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('config.yaml'))"

# Generate new configuration
powershell-assistant init --force

# Use JSON format instead
powershell-assistant config export --format json
```

### Missing Configuration Files

#### Problem
```
ERROR: Configuration file not found: ~/.powershell-assistant/config.yaml
```

#### Solutions
```bash
# Initialize configuration
powershell-assistant init

# Create minimal configuration
powershell-assistant generate-config --type minimal

# Specify custom config path
powershell-assistant start --config /path/to/config.yaml
```

### Security Rules Errors

#### Problem
```
ERROR: Security rules validation failed
```

#### Solutions
```bash
# Generate default security rules
powershell-assistant generate-security-rules

# Validate security rules
powershell-assistant validate-config --type security

# Use permissive rules for testing
powershell-assistant config set security.whitelist_enabled false
```

## Runtime Errors

### Memory Issues

#### Symptoms
- Out of memory errors
- Slow performance
- System freezing

#### Solutions
```bash
# Monitor memory usage
powershell-assistant monitor --resource memory

# Reduce AI model size
powershell-assistant config set ai_model.context_length 1024

# Limit concurrent sessions
powershell-assistant config set server.max_concurrent_sessions 5

# Enable garbage collection
powershell-assistant config set performance.garbage_collection_interval 60
```

### Timeout Errors

#### Symptoms
- Command execution timeouts
- AI processing timeouts
- Network timeouts

#### Solutions
```bash
# Increase timeouts
powershell-assistant config set powershell.default_timeout 120
powershell-assistant config set mcp_server.request_timeout 600

# Optimize AI model parameters
powershell-assistant config set ai_model.max_tokens 256
powershell-assistant config set ai_model.batch_size 4

# Use faster model
powershell-assistant download-model --model llama-7b-fast
```

### Network Connectivity Issues

#### Symptoms
- Model download failures
- External service timeouts
- Connection refused errors

#### Solutions
```bash
# Check internet connectivity
ping google.com

# Use proxy settings
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080

# Use local model files
powershell-assistant config set ai_model.model_path "/local/path/model.bin"

# Disable external dependencies
powershell-assistant config set ai_model.auto_download false
```

## Performance Problems

### Slow AI Processing

#### Symptoms
- Long response times for natural language processing
- High CPU usage
- Memory consumption

#### Diagnosis
```bash
# Profile AI performance
powershell-assistant profile --component ai_engine --duration 60

# Monitor resource usage
powershell-assistant monitor --component ai_engine

# Check model size
ls -lh ~/.powershell-assistant/models/
```

#### Solutions
```bash
# Use GPU acceleration
powershell-assistant config set ai_model.gpu_layers 32

# Optimize CPU usage
powershell-assistant config set ai_model.threads 8

# Use smaller model
powershell-assistant download-model --model llama-7b-q4

# Enable caching
powershell-assistant config set performance.cache_enabled true
```

### High Memory Usage

#### Symptoms
- System running out of memory
- Swap usage increasing
- Application crashes

#### Solutions
```bash
# Reduce model context length
powershell-assistant config set ai_model.context_length 2048

# Limit batch size
powershell-assistant config set ai_model.batch_size 4

# Enable memory cleanup
powershell-assistant config set performance.memory_cleanup_interval 300

# Use memory-efficient model
powershell-assistant download-model --model llama-7b-q8
```

### Slow Command Execution

#### Symptoms
- PowerShell commands take long time to execute
- Sandbox overhead
- Network delays

#### Solutions
```bash
# Optimize PowerShell execution
powershell-assistant config set powershell.version_preference "core"

# Reduce sandbox overhead
powershell-assistant config set security.sandbox_memory_limit "256m"

# Use connection pooling
powershell-assistant config set performance.connection_pool_size 10

# Cache command results
powershell-assistant config set performance.command_cache_enabled true
```

## Security Issues

### Command Blocked by Security Policy

#### Problem
```
ERROR: Command blocked by security policy: Remove-Item -Recurse
```

#### Solutions
```bash
# Review security rules
powershell-assistant config show security

# Add exception for specific command
powershell-assistant security add-rule --pattern "Remove-Item.*temp" --action allow

# Use safer alternative
powershell-assistant translate "safely delete temporary files"

# Request administrator approval
powershell-assistant exec "Remove-Item temp.txt" --force --confirm
```

### Sandbox Escape Attempts

#### Problem
```
WARNING: Potential sandbox escape attempt detected
```

#### Solutions
```bash
# Review audit logs
powershell-assistant logs --type audit --filter security

# Update security rules
powershell-assistant security update-rules

# Strengthen sandbox configuration
powershell-assistant config set security.sandbox_cpu_limit "0.5"
powershell-assistant config set security.sandbox_memory_limit "128m"

# Enable additional monitoring
powershell-assistant config set security.audit_enabled true
```

### Permission Denied Errors

#### Problem
```
ERROR: Access denied: Insufficient privileges for administrative command
```

#### Solutions
```bash
# Run with elevated privileges
sudo powershell-assistant exec "Get-Service"  # Linux/macOS

# Configure permission requirements
powershell-assistant config set security.require_confirmation_for_admin false

# Use alternative commands
powershell-assistant translate "show running services without admin rights"

# Request permission elevation
powershell-assistant exec "Get-Service" --elevated
```

## Diagnostic Tools

### Built-in Diagnostics

```bash
# Comprehensive system check
powershell-assistant diagnose

# Component-specific diagnostics
powershell-assistant diagnose --component ai_engine
powershell-assistant diagnose --component security_engine
powershell-assistant diagnose --component execution_engine

# Performance diagnostics
powershell-assistant diagnose --performance

# Security diagnostics
powershell-assistant diagnose --security
```

### Log Analysis

```bash
# View recent logs
powershell-assistant logs --tail 100

# Filter logs by component
powershell-assistant logs --component ai_engine --level ERROR

# Search logs for specific errors
powershell-assistant logs --search "timeout" --since "1 hour ago"

# Export logs for analysis
powershell-assistant logs --export --format json --output debug.json
```

### Health Checks

```bash
# Basic health check
curl http://localhost:8000/health

# Detailed health status
powershell-assistant health --detailed

# Component health
powershell-assistant health --component all

# Performance metrics
powershell-assistant metrics --format json
```

### Debug Mode

```bash
# Start in debug mode
powershell-assistant start --debug

# Enable verbose logging
powershell-assistant config set logging.level DEBUG

# Enable correlation tracking
powershell-assistant config set logging.correlation_tracking true

# Enable performance monitoring
powershell-assistant config set logging.performance_monitoring true
```

## Getting Help

### Information Gathering

Before seeking help, gather the following information:

```bash
# System information
powershell-assistant info --system

# Configuration summary
powershell-assistant config summary

# Recent error logs
powershell-assistant logs --level ERROR --since "24 hours ago"

# Diagnostic report
powershell-assistant diagnose --full --output diagnostic-report.json
```

### Support Channels

1. **Documentation**: Check the [User Guide](../user/README.md) and [FAQ](../faq/README.md)
2. **GitHub Issues**: Search existing issues or create a new one
3. **Community Forums**: Join the community discussion
4. **Professional Support**: Contact support team for enterprise users

### Bug Reports

When reporting bugs, include:

1. **System Information**
   - Operating system and version
   - Python version
   - PowerShell version
   - Docker version (if using sandbox)

2. **Configuration**
   - Relevant configuration sections
   - Custom security rules
   - AI model information

3. **Error Details**
   - Complete error messages
   - Stack traces
   - Correlation IDs
   - Steps to reproduce

4. **Logs**
   - Recent error logs
   - Diagnostic output
   - Performance metrics

### Example Bug Report

```markdown
## Bug Report

### Environment
- OS: Ubuntu 20.04
- Python: 3.11.0
- PowerShell: 7.3.0
- Docker: 20.10.0
- AI Assistant: 1.0.0

### Issue
Natural language processing fails with timeout error

### Steps to Reproduce
1. Start server: `powershell-assistant start`
2. Send request: `powershell-assistant translate "list processes"`
3. Wait for timeout

### Expected Behavior
Should return PowerShell command within 5 seconds

### Actual Behavior
Request times out after 30 seconds with error:
```
ERROR: AI processing timeout after 30 seconds
Correlation ID: req_123456789
```

### Logs
```
2024-01-15 10:30:45 - ai_engine - ERROR - req_123456789 - Model inference timeout
2024-01-15 10:30:45 - ai_engine - ERROR - req_123456789 - Failed to load model: /path/to/model.bin
```

### Configuration
```yaml
ai_model:
  type: llama-cpp
  model_path: ~/.powershell-assistant/models/llama-7b-chat.bin
  context_length: 4096
  temperature: 0.7
```
```

## Prevention Tips

### Regular Maintenance

```bash
# Update to latest version
pip install --upgrade ai-powershell-assistant

# Clean up old logs
powershell-assistant cleanup --logs --older-than 30d

# Update AI models
powershell-assistant update-models

# Backup configuration
powershell-assistant backup-config --output backup-$(date +%Y%m%d).tar.gz
```

### Monitoring

```bash
# Set up health monitoring
powershell-assistant monitor --continuous --alert-on-error

# Configure log rotation
powershell-assistant config set logging.max_log_file_size "100MB"
powershell-assistant config set logging.backup_count 10

# Enable performance tracking
powershell-assistant config set logging.performance_monitoring true
```

### Best Practices

1. **Keep software updated**
2. **Monitor system resources**
3. **Review security logs regularly**
4. **Test configuration changes in development**
5. **Maintain backup configurations**
6. **Document custom modifications**

## Next Steps

- Review [FAQ](../faq/README.md) for additional common questions
- Check [User Guide](../user/README.md) for usage best practices
- Consult [Developer Guide](../developer/README.md) for technical details
- Join the community for ongoing support