# AI PowerShell Assistant - Docker Image
# Multi-stage build for optimized image size

# Stage 1: Builder
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /build

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt requirements-dev.txt ./

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

# Set metadata
LABEL maintainer="AI PowerShell Team <contact@ai-powershell.dev>"
LABEL description="AI-powered PowerShell assistant with natural language support"
LABEL version="2.0.0"

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    wget \
    apt-transport-https \
    software-properties-common \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install PowerShell Core
RUN wget -q https://packages.microsoft.com/config/debian/11/packages-microsoft-prod.deb && \
    dpkg -i packages-microsoft-prod.deb && \
    rm packages-microsoft-prod.deb && \
    apt-get update && \
    apt-get install -y --no-install-recommends powershell && \
    rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    AI_POWERSHELL_CONFIG=/app/config/default.yaml \
    AI_POWERSHELL_LOG_DIR=/app/logs \
    AI_POWERSHELL_DATA_DIR=/app/data

# Create application user
RUN useradd -m -u 1000 -s /bin/bash appuser && \
    mkdir -p /app /app/logs /app/data /app/config && \
    chown -R appuser:appuser /app

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser config/ ./config/
COPY --chown=appuser:appuser pyproject.toml ./
COPY --chown=appuser:appuser README.md ./
COPY --chown=appuser:appuser LICENSE ./

# Switch to non-root user
USER appuser

# Create necessary directories
RUN mkdir -p ~/.ai-powershell/cache ~/.ai-powershell/history

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.path.insert(0, '/app'); from src.main import PowerShellAssistant; print('healthy')" || exit 1

# Expose ports (if running as MCP server)
EXPOSE 8000

# Default command - interactive mode
CMD ["python", "-m", "src.main", "--interactive"]
