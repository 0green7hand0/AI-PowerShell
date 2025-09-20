# AI PowerShell 智能助手

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![PowerShell](https://img.shields.io/badge/powershell-core%207.0+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-windows%20%7C%20linux%20%7C%20macos-lightgrey.svg)
![AI Model](https://img.shields.io/badge/ai-local%20processing-orange.svg)
![Language](https://img.shields.io/badge/language-中文%20%7C%20english-red.svg)
![Version](https://img.shields.io/badge/version-v1.0.0-brightgreen.svg)

一个智能的命令行交互系统，在自然语言和 PowerShell 命令之间架起桥梁。该系统利用本地 AI 模型提供直观的命令生成，通过三层保护系统实施全面的安全措施，并确保无缝的跨平台兼容性。

## 📚 快速导航

- [🚀 快速开始](#快速开始)
- [📖 中文文档](中文项目说明.md)
- [🔧 安装指南](docs/user/installation.md)
- [💡 使用示例](examples/中文使用示例.py)
- [🔒 安全说明](docs/troubleshooting/README.md)
- [🐳 Docker部署](docker-compose.yml)

## 核心特性

- **自然语言处理**: 使用本地 AI 模型将中文/英文转换为 PowerShell 命令
- **安全验证**: 三层安全保护，包括命令白名单、权限检查和沙箱执行
- **跨平台支持**: 在 Windows、Linux 和 macOS 上与 PowerShell Core 协同工作
- **本地 AI 处理**: 注重隐私的本地模型执行 - 不向外部服务发送数据
- **全面日志记录**: 完整的审计跟踪和性能监控，支持关联追踪
- **MCP 协议**: 基于模型上下文协议构建，实现无缝集成

## 快速开始

### 安装

```bash
# 通过 pip 安装（可用时）
pip install ai-powershell-assistant

# 或从源码安装
git clone https://github.com/0green7hand0/AI-PowerShell.git
cd ai-powershell-assistant
pip install -r requirements.txt
pip install -e .
```

### 基本使用

```bash
# 启动服务器
powershell-assistant start

# 将自然语言转换为 PowerShell
curl -X POST http://localhost:8000/natural_language_to_powershell \
  -H "Content-Type: application/json" \
  -d '{"input_text": "列出正在运行的进程"}'

# 执行 PowerShell 命令
curl -X POST http://localhost:8000/execute_powershell_command \
  -H "Content-Type: application/json" \
  -d '{"command": "Get-Process", "use_sandbox": true}'
```

## 文档

- **[用户指南](docs/user/README.md)** - 安装、配置和使用说明
- **[API 文档](docs/api/README.md)** - 完整的 MCP 工具参考
- **[开发者指南](docs/developer/README.md)** - 扩展和维护系统
- **[故障排除](docs/troubleshooting/README.md)** - 常见问题和解决方案
- **[常见问题](docs/faq/README.md)** - 常见问题解答

## 系统架构

系统由六个主要组件组成：

1. **MCP 服务器核心** - 基于 FastMCP 的工具注册和通信
2. **AI 引擎** - 用于自然语言处理的本地 AI 模型集成
3. **安全引擎** - 三层验证和执行保护
4. **执行引擎** - 跨平台 PowerShell 命令执行
5. **日志引擎** - 全面的审计跟踪和监控
6. **存储引擎** - 本地数据持久化和配置管理

## 系统要求

### 最低要求
- **操作系统**: Windows 10+, Ubuntu 18.04+, macOS 10.15+
- **Python**: 3.8 或更高版本
- **内存**: 4GB RAM（推荐 8GB）
- **存储**: 2GB 可用空间（AI 模型推荐 5GB）
- **PowerShell**: PowerShell Core 7.0+ 或 Windows PowerShell 5.1+

### 推荐配置
- **内存**: 8GB+ RAM 以获得最佳 AI 性能
- **存储**: 10GB+ 用于模型和日志
- **CPU**: 多核处理器以支持并发处理
- **Docker**: 用于沙箱执行（强烈推荐）

## Deployment Options

### Docker Deployment

```bash
# Using Docker Compose
docker-compose up -d

# Using Docker directly
docker run -d \
  --name ai-powershell-assistant \
  -p 8000:8000 \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/data:/app/data \
  ai-powershell-assistant:latest
```

### Kubernetes Deployment

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -n ai-powershell-assistant
```

### Systemd Service

```bash
# Install as systemd service
sudo ./scripts/deploy.sh systemd -e production

# Check service status
sudo systemctl status powershell-assistant
```

## Configuration

### Basic Configuration

```yaml
# config.yaml
server:
  host: "0.0.0.0"
  port: 8000

ai_model:
  type: "llama-cpp"
  model_path: "./models/llama-7b-chat.bin"
  temperature: 0.7

security:
  sandbox_enabled: true
  whitelist_enabled: true
  require_confirmation_for_admin: true

logging:
  level: "INFO"
  outputs: ["console", "file"]
```

### Security Rules

```yaml
# security-rules.yaml
categories:
  safe_commands:
    action: "allow"
    patterns:
      - "^Get-"
      - "^Show-"
      - "^Test-"

  dangerous_commands:
    action: "block"
    patterns:
      - "Remove-Item.*-Recurse"
      - "Format-Volume"
```

## Development

### Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/0green7hand0/AI-PowerShell.git
cd ai-powershell-assistant

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt -r test-requirements.txt
pip install -e .

# Run tests
pytest tests/

# Start development server
python -m src.main --dev
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/end_to_end/

# Run with coverage
pytest --cov=src tests/
```

## Security

### Three-Tier Security System

1. **Command Whitelist Validation**
   - Commands checked against configurable security rules
   - Pattern matching for dangerous operations
   - Risk assessment and categorization

2. **Dynamic Permission Checking**
   - Administrative command detection
   - User confirmation workflows
   - Permission escalation logging

3. **Sandbox Execution Environment**
   - Docker container isolation
   - Resource limits and network restrictions
   - Secure file system access

### Security Best Practices

- Always use sandbox execution for untrusted commands
- Review generated commands before execution
- Keep security rules updated for your environment
- Monitor audit logs regularly
- Use least privilege principle

## Performance

### Optimization Tips

- Use appropriate AI model size for your hardware
- Enable GPU acceleration when available
- Configure caching for frequently used commands
- Monitor resource usage and adjust limits
- Use session management for context persistence

### Monitoring

```bash
# Check system health
curl http://localhost:8000/health

# View performance metrics
curl http://localhost:8000/metrics

# Monitor logs
tail -f logs/app.log
```

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](docs/developer/contributing.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Make your changes and add tests
4. Run the test suite: `pytest`
5. Submit a pull request

### Code Style

- Follow PEP 8 for Python code
- Use type hints for all functions
- Write comprehensive docstrings
- Maintain test coverage above 90%

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/0green7hand0/AI-PowerShell/issues)
- **Discussions**: [GitHub Discussions](https://github.com/0green7hand0/AI-PowerShell/discussions)
- **Security**: Report security issues to security@example.com

## Acknowledgments

- Built on the [FastMCP](https://github.com/jlowin/fastmcp) framework
- Powered by local AI models (LLaMA, Ollama, etc.)
- Cross-platform PowerShell support
- Docker containerization for security

---

**Note**: This is an open-source project focused on privacy and security. All AI processing happens locally on your machine - no data is sent to external services.
