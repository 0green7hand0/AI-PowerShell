# Docker Deployment Guide

This guide covers deploying AI PowerShell Assistant using Docker and Docker Compose.

## Prerequisites

- Docker 20.10+ installed
- Docker Compose 1.29+ (or Docker Compose V2)
- At least 2GB of available RAM
- 5GB of available disk space

## Quick Start

### Build and Run with Docker

```bash
# Build the image
docker build -t ai-powershell:2.0.0 .

# Run interactively
docker run -it --rm \
  -v $(pwd)/config:/app/config:ro \
  -v ai-powershell-logs:/app/logs \
  -v ai-powershell-data:/app/data \
  ai-powershell:2.0.0
```

### Using Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Using Makefile

```bash
# Build Docker image
make docker-build

# Run container
make docker-run

# Start with docker-compose
make docker-compose-up

# View logs
make docker-compose-logs

# Stop services
make docker-compose-down
```

## Configuration

### Environment Variables

Configure the application using environment variables in `docker-compose.yml`:

```yaml
environment:
  # AI Engine
  - AI_ENGINE_PROVIDER=local
  - AI_ENGINE_MODEL=llama
  - AI_ENGINE_TEMPERATURE=0.7
  
  # Security
  - SECURITY_SANDBOX_ENABLED=false
  - SECURITY_REQUIRE_CONFIRMATION=true
  
  # Execution
  - EXECUTION_TIMEOUT=30
  - EXECUTION_ENCODING=utf-8
```

### Volume Mounts

The Docker setup uses several volumes for data persistence:

- **Configuration**: `./config:/app/config:ro` (read-only)
- **Logs**: `ai-powershell-logs:/app/logs` (persistent)
- **Data**: `ai-powershell-data:/app/data` (persistent)
- **Home**: `ai-powershell-home:/home/appuser` (persistent)

### Custom Configuration

1. Create a custom configuration file:

```bash
cp config/default.yaml config/user.yaml
# Edit config/user.yaml with your settings
```

2. Update docker-compose.yml to use it:

```yaml
environment:
  - AI_POWERSHELL_CONFIG=/app/config/user.yaml
```

## Architecture

### Multi-Stage Build

The Dockerfile uses a multi-stage build for optimization:

1. **Builder Stage**: Compiles dependencies and creates virtual environment
2. **Runtime Stage**: Minimal runtime image with only necessary components

Benefits:
- Smaller final image size (~500MB vs ~1.5GB)
- Faster deployment
- Reduced attack surface

### Security Features

- **Non-root user**: Runs as `appuser` (UID 1000)
- **Read-only filesystem**: Optional read-only root filesystem
- **Resource limits**: CPU and memory limits configured
- **Network isolation**: Sandbox container has no network access
- **Security options**: `no-new-privileges` enabled

## Services

### Main Service (ai-powershell)

The primary application service:

- **Image**: `ai-powershell:2.0.0`
- **Ports**: 8000 (MCP server)
- **Resources**: 2 CPU cores, 2GB RAM (limit)
- **Health Check**: Validates application startup

### Sandbox Service (sandbox)

Optional isolated execution environment:

- **Image**: `mcr.microsoft.com/powershell:latest`
- **Network**: Isolated (no network access)
- **Resources**: 0.5 CPU cores, 512MB RAM (limit)
- **Filesystem**: Read-only with tmpfs for execution

## Resource Management

### Resource Limits

Default resource limits in docker-compose.yml:

```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 2G
    reservations:
      cpus: '0.5'
      memory: 512M
```

Adjust based on your workload:

- **Light usage**: 0.5 CPU, 512MB RAM
- **Normal usage**: 1.0 CPU, 1GB RAM
- **Heavy usage**: 2.0 CPU, 2GB RAM
- **AI model inference**: 4.0 CPU, 4GB RAM

### Storage Management

Monitor volume usage:

```bash
# List volumes
docker volume ls | grep ai-powershell

# Inspect volume
docker volume inspect ai-powershell-logs

# Check volume size
docker system df -v
```

Clean up old data:

```bash
# Remove all volumes (WARNING: deletes all data)
docker-compose down -v

# Backup volumes before cleanup
docker run --rm -v ai-powershell-data:/data -v $(pwd):/backup \
  alpine tar czf /backup/data-backup.tar.gz -C /data .
```

## Networking

### Port Mapping

Default port mappings:

- **8000**: MCP server (if enabled)

Customize in docker-compose.yml:

```yaml
ports:
  - "8080:8000"  # Map to different host port
```

### Network Isolation

The sandbox service is completely isolated:

```yaml
network_mode: none  # No network access
```

For the main service, use custom networks:

```yaml
networks:
  ai-powershell-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.28.0.0/16
```

## Health Checks

### Application Health

The container includes a health check:

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.path.insert(0, '/app'); from src.main import PowerShellAssistant; print('healthy')" || exit 1
```

Check health status:

```bash
# View health status
docker ps

# Inspect health details
docker inspect ai-powershell-assistant | jq '.[0].State.Health'
```

### Manual Health Check

```bash
# Execute health check manually
docker exec ai-powershell-assistant \
  python -c "from src.main import PowerShellAssistant; print('healthy')"
```

## Logging

### Log Configuration

Logs are configured with rotation:

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

### View Logs

```bash
# View all logs
docker-compose logs

# Follow logs
docker-compose logs -f

# View specific service
docker-compose logs ai-powershell

# View last 100 lines
docker-compose logs --tail=100
```

### Log Files

Application logs are stored in the volume:

```bash
# Access log files
docker exec ai-powershell-assistant ls -la /app/logs

# View log file
docker exec ai-powershell-assistant cat /app/logs/assistant.log
```

## Troubleshooting

### Container Won't Start

1. Check logs:
```bash
docker-compose logs ai-powershell
```

2. Verify configuration:
```bash
docker-compose config
```

3. Check resource availability:
```bash
docker system df
docker stats
```

### PowerShell Not Found

Verify PowerShell installation in container:

```bash
docker exec ai-powershell-assistant pwsh --version
```

If missing, rebuild the image:

```bash
docker-compose build --no-cache
```

### Permission Issues

Ensure volumes have correct permissions:

```bash
# Fix volume permissions
docker exec -u root ai-powershell-assistant \
  chown -R appuser:appuser /app/logs /app/data
```

### Out of Memory

Increase memory limits in docker-compose.yml:

```yaml
deploy:
  resources:
    limits:
      memory: 4G  # Increase from 2G
```

### Network Issues

Check network connectivity:

```bash
# Test network
docker exec ai-powershell-assistant ping -c 3 google.com

# Check DNS
docker exec ai-powershell-assistant nslookup google.com
```

## Production Deployment

### Best Practices

1. **Use specific image tags**: Avoid `latest` tag
2. **Set resource limits**: Prevent resource exhaustion
3. **Enable health checks**: Automatic recovery
4. **Configure logging**: Centralized log management
5. **Use secrets**: Don't hardcode sensitive data
6. **Regular backups**: Backup volumes regularly
7. **Monitor resources**: Use monitoring tools
8. **Update regularly**: Keep images up to date

### Docker Secrets

For sensitive configuration:

```yaml
secrets:
  ai_config:
    file: ./secrets/config.yaml

services:
  ai-powershell:
    secrets:
      - ai_config
```

### Monitoring

Integrate with monitoring tools:

```yaml
services:
  ai-powershell:
    labels:
      - "prometheus.scrape=true"
      - "prometheus.port=8000"
```

### Scaling

Scale horizontally with Docker Swarm or Kubernetes:

```bash
# Docker Swarm
docker service scale ai-powershell=3

# Docker Compose (limited)
docker-compose up --scale ai-powershell=3
```

## Advanced Configuration

### Custom Dockerfile

Create a custom Dockerfile for specific needs:

```dockerfile
FROM ai-powershell:2.0.0

# Install additional tools
RUN apt-get update && apt-get install -y vim curl

# Add custom scripts
COPY custom-scripts/ /app/scripts/

# Custom entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
```

### Multi-Architecture Build

Build for multiple architectures:

```bash
# Enable buildx
docker buildx create --use

# Build for multiple platforms
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t ai-powershell:2.0.0 \
  --push .
```

### CI/CD Integration

Example GitHub Actions workflow:

```yaml
name: Docker Build and Push

on:
  push:
    tags:
      - 'v*'

jobs:
  docker:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: |
            ghcr.io/0green7hand0/ai-powershell:${{ github.ref_name }}
            ghcr.io/0green7hand0/ai-powershell:latest
```

## References

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PowerShell Docker Images](https://hub.docker.com/_/microsoft-powershell)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)

## Support

For issues or questions:
- GitHub Issues: https://github.com/0green7hand0/AI-PowerShell/issues
- Documentation: https://github.com/0green7hand0/AI-PowerShell/docs
