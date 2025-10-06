#!/bin/bash
# AI PowerShell Assistant Release Script
# Automates the release process

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Check if command exists
check_command() {
    if ! command -v "$1" >/dev/null 2>&1; then
        log_error "$1 is not installed"
        return 1
    fi
    return 0
}

# Validate version format
validate_version() {
    if [[ ! $1 =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        log_error "Invalid version format: $1 (expected: X.Y.Z)"
        return 1
    fi
    return 0
}

# Check if git working directory is clean
check_git_clean() {
    if [[ -n $(git status --porcelain) ]]; then
        log_error "Git working directory is not clean"
        git status --short
        return 1
    fi
    return 0
}

# Run tests
run_tests() {
    log_info "Running tests..."
    
    if ! make test; then
        log_error "Tests failed"
        return 1
    fi
    
    log_success "Tests passed"
    return 0
}

# Run quality checks
run_quality_checks() {
    log_info "Running quality checks..."
    
    if ! make quality; then
        log_error "Quality checks failed"
        return 1
    fi
    
    log_success "Quality checks passed"
    return 0
}

# Check coverage
check_coverage() {
    log_info "Checking test coverage..."
    
    if ! make coverage; then
        log_error "Coverage check failed"
        return 1
    fi
    
    # Extract coverage percentage
    coverage_pct=$(coverage report | grep TOTAL | awk '{print $4}' | sed 's/%//')
    
    if (( $(echo "$coverage_pct < 80" | bc -l) )); then
        log_warning "Coverage is below 80%: ${coverage_pct}%"
    else
        log_success "Coverage is ${coverage_pct}%"
    fi
    
    return 0
}

# Update version in files
update_version() {
    local version=$1
    
    log_info "Updating version to $version..."
    
    # Update pyproject.toml
    sed -i.bak "s/^version = \".*\"/version = \"$version\"/" pyproject.toml
    rm pyproject.toml.bak
    
    # Update src/__init__.py if it exists
    if [ -f "src/__init__.py" ]; then
        sed -i.bak "s/__version__ = \".*\"/__version__ = \"$version\"/" src/__init__.py
        rm src/__init__.py.bak
    fi
    
    log_success "Version updated to $version"
}

# Build Docker image
build_docker() {
    local version=$1
    
    log_info "Building Docker image..."
    
    if ! docker build -t "ai-powershell:$version" -t "ai-powershell:latest" .; then
        log_error "Docker build failed"
        return 1
    fi
    
    log_success "Docker image built successfully"
    return 0
}

# Test Docker image
test_docker() {
    local version=$1
    
    log_info "Testing Docker image..."
    
    if ! docker run --rm "ai-powershell:$version" python -c "from src.main import PowerShellAssistant; print('OK')"; then
        log_error "Docker image test failed"
        return 1
    fi
    
    log_success "Docker image test passed"
    return 0
}

# Build Python package
build_package() {
    log_info "Building Python package..."
    
    if ! python -m build; then
        log_error "Package build failed"
        return 1
    fi
    
    log_success "Package built successfully"
    return 0
}

# Create git tag
create_tag() {
    local version=$1
    local message=$2
    
    log_info "Creating git tag v$version..."
    
    if git tag -a "v$version" -m "$message"; then
        log_success "Tag created successfully"
        return 0
    else
        log_error "Failed to create tag"
        return 1
    fi
}

# Push tag
push_tag() {
    local version=$1
    
    log_info "Pushing tag v$version..."
    
    if git push origin "v$version"; then
        log_success "Tag pushed successfully"
        return 0
    else
        log_error "Failed to push tag"
        return 1
    fi
}

# Create GitHub release
create_github_release() {
    local version=$1
    
    log_info "Creating GitHub release..."
    
    if ! check_command "gh"; then
        log_warning "GitHub CLI not installed, skipping GitHub release"
        log_info "Create release manually at: https://github.com/0green7hand0/AI-PowerShell/releases/new"
        return 0
    fi
    
    if gh release create "v$version" \
        --title "AI PowerShell $version" \
        --notes-file RELEASE_NOTES.md \
        dist/*; then
        log_success "GitHub release created successfully"
        return 0
    else
        log_error "Failed to create GitHub release"
        return 1
    fi
}

# Push Docker images
push_docker() {
    local version=$1
    
    log_info "Pushing Docker images..."
    
    # Tag for GitHub Container Registry
    docker tag "ai-powershell:$version" "ghcr.io/0green7hand0/ai-powershell:$version"
    docker tag "ai-powershell:$version" "ghcr.io/0green7hand0/ai-powershell:latest"
    
    # Push to GitHub Container Registry
    if docker push "ghcr.io/0green7hand0/ai-powershell:$version" && \
       docker push "ghcr.io/0green7hand0/ai-powershell:latest"; then
        log_success "Docker images pushed successfully"
        return 0
    else
        log_error "Failed to push Docker images"
        return 1
    fi
}

# Main release function
release() {
    local version=$1
    local skip_tests=${2:-false}
    local skip_docker=${3:-false}
    
    log_info "Starting release process for version $version"
    echo ""
    
    # Validate version
    if ! validate_version "$version"; then
        exit 1
    fi
    
    # Check prerequisites
    log_info "Checking prerequisites..."
    check_command "git" || exit 1
    check_command "python" || exit 1
    check_command "docker" || log_warning "Docker not found, skipping Docker steps"
    
    # Check git status
    if ! check_git_clean; then
        log_error "Please commit or stash your changes first"
        exit 1
    fi
    
    # Run tests
    if [ "$skip_tests" != "true" ]; then
        run_tests || exit 1
        run_quality_checks || exit 1
        check_coverage || log_warning "Coverage check had warnings"
    else
        log_warning "Skipping tests (--skip-tests)"
    fi
    
    # Update version
    update_version "$version"
    
    # Commit version changes
    git add pyproject.toml src/__init__.py 2>/dev/null || true
    git commit -m "chore: bump version to $version"
    
    # Build package
    build_package || exit 1
    
    # Docker steps
    if [ "$skip_docker" != "true" ] && check_command "docker"; then
        build_docker "$version" || exit 1
        test_docker "$version" || exit 1
    else
        log_warning "Skipping Docker steps"
    fi
    
    # Create and push tag
    create_tag "$version" "Release version $version" || exit 1
    
    # Push changes
    log_info "Pushing changes to remote..."
    git push origin main || exit 1
    push_tag "$version" || exit 1
    
    # Create GitHub release
    create_github_release "$version"
    
    # Push Docker images
    if [ "$skip_docker" != "true" ] && check_command "docker"; then
        read -p "Push Docker images to registry? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            push_docker "$version"
        fi
    fi
    
    echo ""
    log_success "Release $version completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Verify GitHub release: https://github.com/0green7hand0/AI-PowerShell/releases/tag/v$version"
    echo "2. Announce release in GitHub Discussions"
    echo "3. Update documentation if needed"
    echo "4. Monitor for issues"
}

# Show help
show_help() {
    cat << EOF
AI PowerShell Release Script

Usage: $0 <version> [options]

Arguments:
  version           Version number (e.g., 2.0.0)

Options:
  --skip-tests      Skip running tests
  --skip-docker     Skip Docker build and push
  --help            Show this help message

Examples:
  $0 2.0.0
  $0 2.0.1 --skip-tests
  $0 2.1.0 --skip-docker

EOF
}

# Parse arguments
VERSION=""
SKIP_TESTS=false
SKIP_DOCKER=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h)
            show_help
            exit 0
            ;;
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --skip-docker)
            SKIP_DOCKER=true
            shift
            ;;
        *)
            if [ -z "$VERSION" ]; then
                VERSION=$1
            else
                log_error "Unknown argument: $1"
                show_help
                exit 1
            fi
            shift
            ;;
    esac
done

# Check if version is provided
if [ -z "$VERSION" ]; then
    log_error "Version number is required"
    show_help
    exit 1
fi

# Run release
release "$VERSION" "$SKIP_TESTS" "$SKIP_DOCKER"
