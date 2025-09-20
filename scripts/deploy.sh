#!/bin/bash
# AI PowerShell Assistant Deployment Script
# Supports Docker, Kubernetes, and systemd deployments

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DEPLOYMENT_TYPE=""
ENVIRONMENT="production"
CONFIG_DIR=""
DATA_DIR=""
NAMESPACE="default"
REPLICAS=3
DOCKER_IMAGE="ai-powershell-assistant:latest"
SERVICE_NAME="ai-powershell-assistant"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

show_help() {
    cat << EOF
AI PowerShell Assistant Deployment Script

Usage: $0 [OPTIONS] DEPLOYMENT_TYPE

Deployment Types:
  docker      Deploy using Docker Compose
  k8s         Deploy to Kubernetes cluster
  systemd     Deploy as systemd service
  local       Deploy locally for development

Options:
  -e, --environment ENV     Deployment environment (dev/staging/production)
  -c, --config-dir DIR      Configuration directory
  -d, --data-dir DIR        Data directory
  -n, --namespace NS        Kubernetes namespace (k8s only)
  -r, --replicas NUM        Number of replicas (k8s only)
  -i, --image IMAGE         Docker image to deploy
  -h, --help               Show this help message

Examples:
  $0 docker -e production
  $0 k8s -n ai-assistant -r 5
  $0 systemd -c /etc/powershell-assistant
  $0 local -e development

EOF
}

check_requirements() {
    local deployment_type="$1"
    
    case "$deployment_type" in
        "docker")
            if ! command -v docker >/dev/null 2>&1; then
                log_error "Docker is required for Docker deployment"
                return 1
            fi
            if ! command -v docker-compose >/dev/null 2>&1; then
                log_error "Docker Compose is required for Docker deployment"
                return 1
            fi
            ;;
        "k8s")
            if ! command -v kubectl >/dev/null 2>&1; then
                log_error "kubectl is required for Kubernetes deployment"
                return 1
            fi
            if ! kubectl cluster-info >/dev/null 2>&1; then
                log_error "No Kubernetes cluster connection found"
                return 1
            fi
            ;;
        "systemd")
            if ! command -v systemctl >/dev/null 2>&1; then
                log_error "systemd is required for systemd deployment"
                return 1
            fi
            ;;
        "local")
            if ! command -v python3 >/dev/null 2>&1; then
                log_error "Python 3 is required for local deployment"
                return 1
            fi
            ;;
        *)
            log_error "Unknown deployment type: $deployment_type"
            return 1
            ;;
    esac
    
    return 0
}

prepare_configuration() {
    local env="$1"
    local config_dir="$2"
    
    log_info "Preparing configuration for $env environment..."
    
    # Create configuration directory if it doesn't exist
    mkdir -p "$config_dir"
    
    # Generate environment-specific configuration
    case "$env" in
        "development")
            cat > "$config_dir/config.yaml" << EOF
version: "1.0.0"
platform: "auto"

server:
  host: "0.0.0.0"
  port: 8000
  max_concurrent_sessions: 5

logging:
  level: "DEBUG"
  outputs: ["console", "file"]

security:
  sandbox_enabled: false
  require_confirmation_for_admin: false

ai_model:
  temperature: 0.9
  max_tokens: 1024
EOF
            ;;
        "staging")
            cat > "$config_dir/config.yaml" << EOF
version: "1.0.0"
platform: "auto"

server:
  host: "0.0.0.0"
  port: 8000
  max_concurrent_sessions: 20

logging:
  level: "INFO"
  outputs: ["file", "syslog"]

security:
  sandbox_enabled: true
  require_confirmation_for_admin: true
  audit_enabled: true

ai_model:
  temperature: 0.7
  max_tokens: 512
EOF
            ;;
        "production")
            cat > "$config_dir/config.yaml" << EOF
version: "1.0.0"
platform: "auto"

server:
  host: "0.0.0.0"
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
  temperature: 0.5
  max_tokens: 256
  gpu_layers: 32

performance:
  cache_enabled: true
  connection_pool_size: 20
EOF
            ;;
    esac
    
    # Generate security rules
    cat > "$config_dir/security-rules.yaml" << EOF
version: "1.0.0"
global:
  default_action: "block"
  risk_threshold: "medium"

categories:
  safe_commands:
    action: "allow"
    risk_level: "low"
    patterns:
      - "^Get-"
      - "^Show-"
      - "^Test-Connection"

  administrative_commands:
    action: "confirm"
    risk_level: "high"
    patterns:
      - "^Set-"
      - "^New-"
      - "^Remove-"

  dangerous_commands:
    action: "block"
    risk_level: "critical"
    patterns:
      - "Remove-Item.*-Recurse"
      - "Format-Volume"
      - "Stop-Computer"
EOF
    
    log_success "Configuration prepared at $config_dir"
}

deploy_docker() {
    local env="$1"
    local config_dir="$2"
    local data_dir="$3"
    
    log_info "Deploying with Docker Compose..."
    
    # Create docker-compose override for environment
    cat > "docker-compose.$env.yml" << EOF
version: '3.8'

services:
  ai-powershell-assistant:
    image: $DOCKER_IMAGE
    environment:
      - POWERSHELL_ASSISTANT_ENV=$env
    volumes:
      - $config_dir:/app/config:ro
      - $data_dir:/app/data
    restart: unless-stopped

EOF
    
    # Deploy with Docker Compose
    docker-compose -f docker-compose.yml -f "docker-compose.$env.yml" up -d
    
    # Wait for service to be ready
    log_info "Waiting for service to be ready..."
    for i in {1..30}; do
        if curl -f http://localhost:8000/health >/dev/null 2>&1; then
            log_success "Service is ready"
            break
        fi
        sleep 2
    done
    
    log_success "Docker deployment completed"
    log_info "Service URL: http://localhost:8000"
    log_info "Logs: docker-compose logs -f ai-powershell-assistant"
}

deploy_kubernetes() {
    local env="$1"
    local config_dir="$2"
    local data_dir="$3"
    local namespace="$4"
    local replicas="$5"
    
    log_info "Deploying to Kubernetes..."
    
    # Create namespace if it doesn't exist
    kubectl create namespace "$namespace" --dry-run=client -o yaml | kubectl apply -f -
    
    # Create ConfigMap for configuration
    kubectl create configmap ai-powershell-assistant-config \
        --from-file="$config_dir" \
        --namespace="$namespace" \
        --dry-run=client -o yaml | kubectl apply -f -
    
    # Create PersistentVolumeClaim for data
    cat << EOF | kubectl apply -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: ai-powershell-assistant-data
  namespace: $namespace
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
EOF
    
    # Create Deployment
    cat << EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-powershell-assistant
  namespace: $namespace
  labels:
    app: ai-powershell-assistant
spec:
  replicas: $replicas
  selector:
    matchLabels:
      app: ai-powershell-assistant
  template:
    metadata:
      labels:
        app: ai-powershell-assistant
    spec:
      containers:
      - name: ai-powershell-assistant
        image: $DOCKER_IMAGE
        ports:
        - containerPort: 8000
        env:
        - name: POWERSHELL_ASSISTANT_ENV
          value: "$env"
        - name: POWERSHELL_ASSISTANT_HOST
          value: "0.0.0.0"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        volumeMounts:
        - name: config
          mountPath: /app/config
          readOnly: true
        - name: data
          mountPath: /app/data
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: config
        configMap:
          name: ai-powershell-assistant-config
      - name: data
        persistentVolumeClaim:
          claimName: ai-powershell-assistant-data
EOF
    
    # Create Service
    cat << EOF | kubectl apply -f -
apiVersion: v1
kind: Service
metadata:
  name: ai-powershell-assistant
  namespace: $namespace
  labels:
    app: ai-powershell-assistant
spec:
  selector:
    app: ai-powershell-assistant
  ports:
  - port: 8000
    targetPort: 8000
    protocol: TCP
  type: ClusterIP
EOF
    
    # Create Ingress (optional)
    cat << EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ai-powershell-assistant
  namespace: $namespace
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: powershell-assistant.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: ai-powershell-assistant
            port:
              number: 8000
EOF
    
    # Wait for deployment to be ready
    log_info "Waiting for deployment to be ready..."
    kubectl wait --for=condition=available --timeout=300s deployment/ai-powershell-assistant -n "$namespace"
    
    log_success "Kubernetes deployment completed"
    log_info "Namespace: $namespace"
    log_info "Pods: kubectl get pods -n $namespace"
    log_info "Logs: kubectl logs -f deployment/ai-powershell-assistant -n $namespace"
}

deploy_systemd() {
    local env="$1"
    local config_dir="$2"
    local data_dir="$3"
    
    log_info "Deploying as systemd service..."
    
    # Create service user
    if ! id "powershell-assistant" >/dev/null 2>&1; then
        sudo useradd -r -s /bin/false -d /var/lib/powershell-assistant powershell-assistant
    fi
    
    # Create directories
    sudo mkdir -p /var/lib/powershell-assistant
    sudo mkdir -p /var/log/powershell-assistant
    sudo mkdir -p /etc/powershell-assistant
    
    # Copy configuration
    sudo cp -r "$config_dir"/* /etc/powershell-assistant/
    
    # Set permissions
    sudo chown -R powershell-assistant:powershell-assistant /var/lib/powershell-assistant
    sudo chown -R powershell-assistant:powershell-assistant /var/log/powershell-assistant
    sudo chown -R root:powershell-assistant /etc/powershell-assistant
    sudo chmod -R 640 /etc/powershell-assistant
    
    # Create systemd service file
    sudo tee /etc/systemd/system/powershell-assistant.service > /dev/null << EOF
[Unit]
Description=AI PowerShell Assistant
After=network.target
Wants=network.target

[Service]
Type=simple
User=powershell-assistant
Group=powershell-assistant
WorkingDirectory=/var/lib/powershell-assistant
ExecStart=/usr/local/bin/powershell-assistant start --config /etc/powershell-assistant/config.yaml
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=powershell-assistant

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/lib/powershell-assistant /var/log/powershell-assistant

# Environment
Environment=POWERSHELL_ASSISTANT_ENV=$env
Environment=POWERSHELL_ASSISTANT_DATA_DIR=/var/lib/powershell-assistant
Environment=POWERSHELL_ASSISTANT_LOG_DIR=/var/log/powershell-assistant

[Install]
WantedBy=multi-user.target
EOF
    
    # Reload systemd and enable service
    sudo systemctl daemon-reload
    sudo systemctl enable powershell-assistant
    sudo systemctl start powershell-assistant
    
    # Wait for service to be ready
    log_info "Waiting for service to be ready..."
    for i in {1..30}; do
        if sudo systemctl is-active --quiet powershell-assistant; then
            log_success "Service is running"
            break
        fi
        sleep 2
    done
    
    log_success "Systemd deployment completed"
    log_info "Status: sudo systemctl status powershell-assistant"
    log_info "Logs: sudo journalctl -u powershell-assistant -f"
}

deploy_local() {
    local env="$1"
    local config_dir="$2"
    local data_dir="$3"
    
    log_info "Deploying locally for development..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    pip install -r requirements.txt
    pip install -e .
    
    # Create development configuration
    mkdir -p "$config_dir"
    prepare_configuration "$env" "$config_dir"
    
    # Start the application in background
    nohup python -m src.main --config "$config_dir/config.yaml" --dev > "$data_dir/app.log" 2>&1 &
    echo $! > "$data_dir/app.pid"
    
    # Wait for service to be ready
    log_info "Waiting for service to be ready..."
    for i in {1..30}; do
        if curl -f http://localhost:8000/health >/dev/null 2>&1; then
            log_success "Service is ready"
            break
        fi
        sleep 2
    done
    
    log_success "Local deployment completed"
    log_info "Service URL: http://localhost:8000"
    log_info "PID: $(cat $data_dir/app.pid)"
    log_info "Logs: tail -f $data_dir/app.log"
    log_info "Stop: kill $(cat $data_dir/app.pid)"
}

verify_deployment() {
    local deployment_type="$1"
    
    log_info "Verifying deployment..."
    
    # Test health endpoint
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        log_success "Health check passed"
    else
        log_error "Health check failed"
        return 1
    fi
    
    # Test basic functionality
    local test_response=$(curl -s -X POST http://localhost:8000/natural_language_to_powershell \
        -H "Content-Type: application/json" \
        -d '{"input_text": "get current date"}')
    
    if echo "$test_response" | grep -q "success.*true"; then
        log_success "Functionality test passed"
    else
        log_warning "Functionality test failed - service may still be initializing"
    fi
    
    log_success "Deployment verification completed"
}

cleanup_deployment() {
    local deployment_type="$1"
    
    log_info "Cleaning up previous deployment..."
    
    case "$deployment_type" in
        "docker")
            docker-compose down --remove-orphans || true
            ;;
        "k8s")
            kubectl delete deployment ai-powershell-assistant -n "$NAMESPACE" --ignore-not-found=true
            kubectl delete service ai-powershell-assistant -n "$NAMESPACE" --ignore-not-found=true
            kubectl delete ingress ai-powershell-assistant -n "$NAMESPACE" --ignore-not-found=true
            ;;
        "systemd")
            sudo systemctl stop powershell-assistant || true
            sudo systemctl disable powershell-assistant || true
            ;;
        "local")
            if [ -f "app.pid" ]; then
                kill "$(cat app.pid)" || true
                rm app.pid
            fi
            ;;
    esac
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -c|--config-dir)
            CONFIG_DIR="$2"
            shift 2
            ;;
        -d|--data-dir)
            DATA_DIR="$2"
            shift 2
            ;;
        -n|--namespace)
            NAMESPACE="$2"
            shift 2
            ;;
        -r|--replicas)
            REPLICAS="$2"
            shift 2
            ;;
        -i|--image)
            DOCKER_IMAGE="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            if [ -z "$DEPLOYMENT_TYPE" ]; then
                DEPLOYMENT_TYPE="$1"
            else
                log_error "Unknown option: $1"
                show_help
                exit 1
            fi
            shift
            ;;
    esac
done

# Validate deployment type
if [ -z "$DEPLOYMENT_TYPE" ]; then
    log_error "Deployment type is required"
    show_help
    exit 1
fi

# Set default directories if not specified
if [ -z "$CONFIG_DIR" ]; then
    CONFIG_DIR="./config"
fi

if [ -z "$DATA_DIR" ]; then
    DATA_DIR="./data"
fi

# Main deployment process
main() {
    echo "AI PowerShell Assistant Deployment Script"
    echo "========================================"
    echo "Deployment Type: $DEPLOYMENT_TYPE"
    echo "Environment: $ENVIRONMENT"
    echo "Config Directory: $CONFIG_DIR"
    echo "Data Directory: $DATA_DIR"
    echo ""
    
    # Check requirements
    if ! check_requirements "$DEPLOYMENT_TYPE"; then
        exit 1
    fi
    
    # Create directories
    mkdir -p "$CONFIG_DIR" "$DATA_DIR"
    
    # Prepare configuration
    prepare_configuration "$ENVIRONMENT" "$CONFIG_DIR"
    
    # Clean up previous deployment
    cleanup_deployment "$DEPLOYMENT_TYPE"
    
    # Deploy based on type
    case "$DEPLOYMENT_TYPE" in
        "docker")
            deploy_docker "$ENVIRONMENT" "$CONFIG_DIR" "$DATA_DIR"
            ;;
        "k8s")
            deploy_kubernetes "$ENVIRONMENT" "$CONFIG_DIR" "$DATA_DIR" "$NAMESPACE" "$REPLICAS"
            ;;
        "systemd")
            deploy_systemd "$ENVIRONMENT" "$CONFIG_DIR" "$DATA_DIR"
            ;;
        "local")
            deploy_local "$ENVIRONMENT" "$CONFIG_DIR" "$DATA_DIR"
            ;;
        *)
            log_error "Unknown deployment type: $DEPLOYMENT_TYPE"
            exit 1
            ;;
    esac
    
    # Verify deployment
    verify_deployment "$DEPLOYMENT_TYPE"
    
    log_success "Deployment completed successfully!"
}

# Run main function
main "$@"