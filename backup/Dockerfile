# Multi-stage Docker build for AI PowerShell Assistant
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    gnupg2 \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install PowerShell
RUN wget -q https://packages.microsoft.com/config/debian/11/packages-microsoft-prod.deb \
    && dpkg -i packages-microsoft-prod.deb \
    && apt-get update \
    && apt-get install -y powershell \
    && rm packages-microsoft-prod.deb \
    && rm -rf /var/lib/apt/lists/*

# Install Docker CLI (for sandbox execution)
RUN curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian bullseye stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null \
    && apt-get update \
    && apt-get install -y docker-ce-cli \
    && rm -rf /var/lib/apt/lists/*

# Development stage
FROM base as development

# Install development dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements files
COPY requirements.txt test-requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt -r test-requirements.txt

# Copy source code
COPY src/ ./src/
COPY tests/ ./tests/
COPY setup.py pytest.ini ./

# Install package in development mode
RUN pip install -e .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Development command
CMD ["python", "-m", "src.main", "--dev"]

# Production stage
FROM base as production

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY setup.py ./

# Install package
RUN pip install .

# Create directories for data and configuration
RUN mkdir -p /app/data /app/config /app/logs /app/models

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Create default configuration
RUN python -c "
import os
from pathlib import Path
from src.config.models import ServerConfig

# Create default configuration
config_dir = Path('/app/config')
config_dir.mkdir(exist_ok=True)

# Generate minimal production configuration
config = ServerConfig.create_default()
config.save_to_file(config_dir / 'config.yaml')
"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Volume mounts
VOLUME ["/app/data", "/app/config", "/app/logs", "/app/models"]

# Production command
CMD ["python", "-m", "src.main", "--config", "/app/config/config.yaml"]

# Minimal stage for resource-constrained environments
FROM python:3.11-alpine as minimal

# Install minimal system dependencies
RUN apk add --no-cache \
    curl \
    bash

# Install PowerShell (minimal version)
RUN curl -L https://github.com/PowerShell/PowerShell/releases/download/v7.3.0/powershell-7.3.0-linux-musl-x64.tar.gz \
    | tar -xz -C /opt \
    && ln -s /opt/pwsh /usr/local/bin/pwsh

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt ./

# Install minimal Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY setup.py ./

# Install package
RUN pip install .

# Create non-root user
RUN adduser -D -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Minimal configuration
ENV POWERSHELL_ASSISTANT_LOG_LEVEL=WARNING \
    POWERSHELL_ASSISTANT_SANDBOX_ENABLED=false \
    POWERSHELL_ASSISTANT_AI_MODEL_TYPE=minimal

# Expose port
EXPOSE 8000

# Minimal command
CMD ["python", "-m", "src.main", "--minimal"]