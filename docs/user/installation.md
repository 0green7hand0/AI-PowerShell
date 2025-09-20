# Installation Guide

This guide covers installing the AI PowerShell Assistant on different platforms.

## System Requirements

### Minimum Requirements
- **Operating System**: Windows 10+, Ubuntu 18.04+, macOS 10.15+
- **Python**: 3.8 or higher
- **Memory**: 4GB RAM (8GB recommended)
- **Storage**: 2GB free space (5GB recommended for AI models)
- **PowerShell**: PowerShell Core 7.0+ or Windows PowerShell 5.1+

### Recommended Requirements
- **Memory**: 8GB+ RAM for optimal AI performance
- **Storage**: 10GB+ for models and logs
- **CPU**: Multi-core processor for concurrent processing
- **Docker**: For sandbox execution (highly recommended)

## Prerequisites

### 1. Install Python

#### Windows
```powershell
# Using winget
winget install Python.Python.3.11

# Or download from python.org
# Verify installation
python --version
pip --version
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
python3 --version
pip3 --version
```

#### macOS
```bash
# Using Homebrew
brew install python@3.11

# Or using pyenv
pyenv install 3.11.0
pyenv global 3.11.0

python --version
pip --version
```

### 2. Install PowerShell

#### Windows
PowerShell is pre-installed. For PowerShell Core:
```powershell
winget install Microsoft.PowerShell
```

#### Linux
```bash
# Ubuntu/Debian
wget -q https://packages.microsoft.com/config/ubuntu/20.04/packages-microsoft-prod.deb
sudo dpkg -i packages-microsoft-prod.deb
sudo apt-get update
sudo apt-get install -y powershell

# Verify installation
pwsh --version
```

#### macOS
```bash
brew install powershell/tap/powershell
pwsh --version
```

### 3. Install Docker (Optional but Recommended)

#### Windows
```powershell
# Install Docker Desktop
winget install Docker.DockerDesktop

# Or download from docker.com
# Verify installation
docker --version
```

#### Linux
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

docker --version
```

#### macOS
```bash
# Install Docker Desktop
brew install --cask docker

# Or download from docker.com
docker --version
```

## Installation Methods

### Method 1: pip Install (Recommended)

```bash
# Create virtual environment
python -m venv ai-powershell-assistant
source ai-powershell-assistant/bin/activate  # Linux/macOS
# ai-powershell-assistant\Scripts\activate  # Windows

# Install the package
pip install ai-powershell-assistant

# Verify installation
powershell-assistant --version
```

### Method 2: From Source

```bash
# Clone the repository
git clone https://github.com/0green7hand0/AI-PowerShell.git
cd ai-powershell-assistant

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .

# Verify installation
python -m src.main --version
```

### Method 3: Docker Container

```bash
# Pull the image
docker pull ai-powershell-assistant:latest

# Run the container
docker run -d \
  --name powershell-assistant \
  -p 8000:8000 \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/data:/app/data \
  ai-powershell-assistant:latest

# Verify installation
docker logs powershell-assistant
```

## Post-Installation Setup

### 1. Initialize Configuration

```bash
# Create default configuration
powershell-assistant init

# This creates:
# ~/.powershell-assistant/config.yaml
# ~/.powershell-assistant/security-rules.yaml
# ~/.powershell-assistant/logging.yaml
```

### 2. Download AI Models

```bash
# Download default model (LLaMA-CPP)
powershell-assistant download-model --model llama-7b-chat

# Or specify custom model
powershell-assistant download-model --model custom-model --url https://example.com/model.bin
```

### 3. Configure Security Rules

```bash
# Generate default security rules
powershell-assistant generate-security-rules

# Edit security rules
powershell-assistant edit-config security
```

### 4. Test Installation

```bash
# Test basic functionality
powershell-assistant test

# Test AI processing
powershell-assistant test --ai

# Test sandbox execution
powershell-assistant test --sandbox

# Test all components
powershell-assistant test --all
```

## Platform-Specific Configuration

### Windows Configuration

```yaml
# config.yaml
platform: windows
powershell:
  executable: "powershell.exe"  # or "pwsh.exe" for Core
  version_preference: "core"    # or "desktop"
  
security:
  sandbox_enabled: true
  docker_image: "mcr.microsoft.com/powershell:windowsservercore"
  
ai_model:
  path: "C:\\Users\\%USERNAME%\\.powershell-assistant\\models"
  type: "llama-cpp"
```

### Linux Configuration

```yaml
# config.yaml
platform: linux
powershell:
  executable: "pwsh"
  version_preference: "core"
  
security:
  sandbox_enabled: true
  docker_image: "mcr.microsoft.com/powershell:ubuntu-20.04"
  
ai_model:
  path: "~/.powershell-assistant/models"
  type: "llama-cpp"
```

### macOS Configuration

```yaml
# config.yaml
platform: macos
powershell:
  executable: "pwsh"
  version_preference: "core"
  
security:
  sandbox_enabled: true
  docker_image: "mcr.microsoft.com/powershell:ubuntu-20.04"
  
ai_model:
  path: "~/.powershell-assistant/models"
  type: "llama-cpp"
```

## Verification Steps

### 1. Check System Status

```bash
powershell-assistant status
```

Expected output:
```
✓ Python 3.11.0 installed
✓ PowerShell 7.3.0 detected
✓ Docker 20.10.0 available
✓ AI model loaded (llama-7b-chat)
✓ Security rules configured
✓ MCP server ready
```

### 2. Test Natural Language Processing

```bash
powershell-assistant translate "list running processes"
```

Expected output:
```json
{
  "success": true,
  "generated_command": "Get-Process",
  "confidence_score": 0.95,
  "explanation": "Lists all currently running processes"
}
```

### 3. Test Command Execution

```bash
powershell-assistant exec "Get-Date"
```

Expected output:
```json
{
  "success": true,
  "return_code": 0,
  "stdout": "Monday, January 15, 2024 10:30:45 AM",
  "execution_time": 0.123
}
```

## Troubleshooting Installation

### Common Issues

#### Python Version Issues
```bash
# Check Python version
python --version

# If version is too old, upgrade
pip install --upgrade python
```

#### PowerShell Not Found
```bash
# Check PowerShell installation
which pwsh  # Linux/macOS
where pwsh  # Windows

# Install if missing (see prerequisites)
```

#### Docker Permission Issues (Linux)
```bash
# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Test docker access
docker run hello-world
```

#### AI Model Download Issues
```bash
# Check internet connection
ping huggingface.co

# Use alternative model source
powershell-assistant download-model --model llama-7b-chat --source local --path /path/to/model
```

#### Permission Issues
```bash
# Fix file permissions
chmod +x ~/.local/bin/powershell-assistant

# Fix directory permissions
chmod -R 755 ~/.powershell-assistant
```

### Getting Help

If you encounter issues:

1. Check the [Troubleshooting Guide](../troubleshooting/README.md)
2. Review logs: `powershell-assistant logs`
3. Run diagnostics: `powershell-assistant diagnose`
4. Check system requirements
5. Consult the [FAQ](../faq/README.md)

## Next Steps

After successful installation:

1. [Configure](configuration.md) the system for your needs
2. Learn [Basic Usage](usage.md) patterns
3. Set up [Security Settings](security.md)
4. Explore [Advanced Features](advanced-features.md)