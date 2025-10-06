#!/bin/bash
# AI PowerShell Assistant Installation Script
# Supports Linux, macOS, and Windows (via WSL/Git Bash)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_URL="https://github.com/0green7hand0/AI-PowerShell.git"
INSTALL_DIR="$HOME/.powershell-assistant"
PYTHON_MIN_VERSION="3.8"
REQUIRED_COMMANDS=("python3" "pip3" "git")

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

check_command() {
    if command -v "$1" >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

check_python_version() {
    local python_cmd="$1"
    local version=$($python_cmd --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
    local major=$(echo "$version" | cut -d. -f1)
    local minor=$(echo "$version" | cut -d. -f2)
    
    if [ "$major" -gt 3 ] || ([ "$major" -eq 3 ] && [ "$minor" -ge 8 ]); then
        return 0
    else
        return 1
    fi
}

detect_os() {
    case "$(uname -s)" in
        Linux*)     echo "linux";;
        Darwin*)    echo "macos";;
        CYGWIN*|MINGW*|MSYS*) echo "windows";;
        *)          echo "unknown";;
    esac
}

install_dependencies_linux() {
    log_info "Installing dependencies for Linux..."
    
    # Detect package manager
    if check_command "apt-get"; then
        sudo apt-get update
        sudo apt-get install -y python3 python3-pip python3-venv git curl wget
        
        # Install PowerShell
        if ! check_command "pwsh"; then
            log_info "Installing PowerShell..."
            wget -q https://packages.microsoft.com/config/ubuntu/20.04/packages-microsoft-prod.deb
            sudo dpkg -i packages-microsoft-prod.deb
            sudo apt-get update
            sudo apt-get install -y powershell
            rm packages-microsoft-prod.deb
        fi
        
    elif check_command "yum"; then
        sudo yum install -y python3 python3-pip git curl wget
        
        # Install PowerShell
        if ! check_command "pwsh"; then
            log_info "Installing PowerShell..."
            curl https://packages.microsoft.com/config/rhel/7/prod.repo | sudo tee /etc/yum.repos.d/microsoft.repo
            sudo yum install -y powershell
        fi
        
    elif check_command "pacman"; then
        sudo pacman -S --noconfirm python python-pip git curl wget
        
        # Install PowerShell from AUR (if available)
        if ! check_command "pwsh"; then
            log_warning "Please install PowerShell manually from AUR or official releases"
        fi
    else
        log_error "Unsupported package manager. Please install dependencies manually."
        exit 1
    fi
}

install_dependencies_macos() {
    log_info "Installing dependencies for macOS..."
    
    # Check if Homebrew is installed
    if ! check_command "brew"; then
        log_info "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    
    # Install dependencies
    brew install python@3.11 git curl wget
    
    # Install PowerShell
    if ! check_command "pwsh"; then
        log_info "Installing PowerShell..."
        brew install powershell/tap/powershell
    fi
}

install_dependencies_windows() {
    log_info "Installing dependencies for Windows..."
    
    # Check if running in WSL
    if grep -q Microsoft /proc/version 2>/dev/null; then
        log_info "Detected WSL environment"
        install_dependencies_linux
        return
    fi
    
    # For Git Bash/MSYS2 environment
    log_warning "Please ensure the following are installed:"
    log_warning "- Python 3.8+ (from python.org or Microsoft Store)"
    log_warning "- PowerShell 7+ (from Microsoft Store or GitHub releases)"
    log_warning "- Git for Windows"
    
    # Check if Python is available
    if ! check_command "python" && ! check_command "python3"; then
        log_error "Python not found. Please install Python 3.8+ and try again."
        exit 1
    fi
}

install_docker() {
    local os="$1"
    
    log_info "Installing Docker (optional but recommended)..."
    
    case "$os" in
        "linux")
            if check_command "apt-get"; then
                curl -fsSL https://get.docker.com -o get-docker.sh
                sudo sh get-docker.sh
                sudo usermod -aG docker "$USER"
                rm get-docker.sh
                log_warning "Please log out and back in for Docker group membership to take effect"
            else
                log_warning "Please install Docker manually for your Linux distribution"
            fi
            ;;
        "macos")
            if check_command "brew"; then
                brew install --cask docker
                log_info "Please start Docker Desktop from Applications"
            else
                log_warning "Please install Docker Desktop from docker.com"
            fi
            ;;
        "windows")
            log_warning "Please install Docker Desktop from docker.com"
            ;;
    esac
}

create_virtual_environment() {
    log_info "Creating Python virtual environment..."
    
    # Determine Python command
    local python_cmd=""
    if check_command "python3" && check_python_version "python3"; then
        python_cmd="python3"
    elif check_command "python" && check_python_version "python"; then
        python_cmd="python"
    else
        log_error "Python 3.8+ not found. Please install Python 3.8 or higher."
        exit 1
    fi
    
    # Create virtual environment
    "$python_cmd" -m venv "$INSTALL_DIR/venv"
    
    # Activate virtual environment
    source "$INSTALL_DIR/venv/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip
}

install_package() {
    log_info "Installing AI PowerShell Assistant..."
    
    # Install from PyPI (when available)
    if pip install ai-powershell-assistant 2>/dev/null; then
        log_success "Installed from PyPI"
    else
        # Install from source
        log_info "Installing from source..."
        
        if [ -d "$INSTALL_DIR/src" ]; then
            rm -rf "$INSTALL_DIR/src"
        fi
        
        git clone "$REPO_URL" "$INSTALL_DIR/src"
        cd "$INSTALL_DIR/src"
        pip install -r requirements.txt
        pip install -e .
    fi
}

create_configuration() {
    log_info "Creating default configuration..."
    
    # Create configuration directory
    mkdir -p "$INSTALL_DIR/config"
    
    # Initialize configuration
    powershell-assistant init --config-dir "$INSTALL_DIR/config"
    
    log_success "Configuration created at $INSTALL_DIR/config"
}

create_launcher_script() {
    log_info "Creating launcher script..."
    
    # Create bin directory
    mkdir -p "$HOME/.local/bin"
    
    # Create launcher script
    cat > "$HOME/.local/bin/powershell-assistant" << 'EOF'
#!/bin/bash
# AI PowerShell Assistant Launcher

INSTALL_DIR="$HOME/.powershell-assistant"
VENV_DIR="$INSTALL_DIR/venv"

# Activate virtual environment
if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
else
    echo "Error: Virtual environment not found at $VENV_DIR"
    exit 1
fi

# Run the application (new modular structure)
cd "$INSTALL_DIR/src" || exit 1
exec python -m src.main "$@"
EOF
    
    chmod +x "$HOME/.local/bin/powershell-assistant"
    
    # Add to PATH if not already there
    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc" 2>/dev/null || true
        log_info "Added $HOME/.local/bin to PATH in shell configuration"
        log_warning "Please restart your shell or run: source ~/.bashrc"
    fi
}

run_tests() {
    log_info "Running installation tests..."
    
    # Test basic functionality
    if powershell-assistant --version >/dev/null 2>&1; then
        log_success "Basic functionality test passed"
    else
        log_error "Basic functionality test failed"
        return 1
    fi
    
    # Test PowerShell detection
    if powershell-assistant test --powershell >/dev/null 2>&1; then
        log_success "PowerShell detection test passed"
    else
        log_warning "PowerShell detection test failed - PowerShell may not be properly installed"
    fi
    
    # Test AI model (if available)
    if powershell-assistant test --ai >/dev/null 2>&1; then
        log_success "AI model test passed"
    else
        log_warning "AI model test failed - you may need to download AI models"
    fi
    
    # Test Docker (if available)
    if check_command "docker" && powershell-assistant test --sandbox >/dev/null 2>&1; then
        log_success "Docker sandbox test passed"
    else
        log_warning "Docker sandbox test failed - Docker may not be available"
    fi
}

print_next_steps() {
    log_success "Installation completed successfully!"
    echo
    echo "Next steps:"
    echo "1. Restart your shell or run: source ~/.bashrc"
    echo "2. Download AI models: powershell-assistant download-model"
    echo "3. Start the server: powershell-assistant start"
    echo "4. Test functionality: powershell-assistant test"
    echo
    echo "Configuration directory: $INSTALL_DIR/config"
    echo "Documentation: https://github.com/0green7hand0/AI-PowerShell/docs"
    echo
    echo "For help: powershell-assistant --help"
}

# Main installation process
main() {
    echo "AI PowerShell Assistant Installation Script"
    echo "=========================================="
    echo
    
    # Detect operating system
    local os=$(detect_os)
    log_info "Detected OS: $os"
    
    # Check if already installed
    if [ -d "$INSTALL_DIR" ]; then
        log_warning "Installation directory already exists: $INSTALL_DIR"
        read -p "Do you want to reinstall? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Installation cancelled"
            exit 0
        fi
        rm -rf "$INSTALL_DIR"
    fi
    
    # Create installation directory
    mkdir -p "$INSTALL_DIR"
    
    # Install system dependencies
    case "$os" in
        "linux")   install_dependencies_linux ;;
        "macos")   install_dependencies_macos ;;
        "windows") install_dependencies_windows ;;
        *)         log_error "Unsupported operating system: $os"; exit 1 ;;
    esac
    
    # Ask about Docker installation
    if ! check_command "docker"; then
        read -p "Install Docker for sandbox execution? (Y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            install_docker "$os"
        fi
    fi
    
    # Create virtual environment
    create_virtual_environment
    
    # Install the package
    install_package
    
    # Create configuration
    create_configuration
    
    # Create launcher script
    create_launcher_script
    
    # Run tests
    run_tests
    
    # Print next steps
    print_next_steps
}

# Handle script arguments
case "${1:-}" in
    "--help"|"-h")
        echo "Usage: $0 [OPTIONS]"
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --no-docker    Skip Docker installation"
        echo "  --dev          Install development version"
        exit 0
        ;;
    "--no-docker")
        SKIP_DOCKER=1
        ;;
    "--dev")
        REPO_URL="https://github.com/0green7hand0/AI-PowerShell.git"
        DEV_INSTALL=1
        ;;
esac

# Run main installation
main "$@"
