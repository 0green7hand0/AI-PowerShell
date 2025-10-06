# AI PowerShell Assistant Release Script for Windows
# Automates the release process

param(
    [Parameter(Mandatory=$true)]
    [string]$Version,
    
    [switch]$SkipTests,
    [switch]$SkipDocker,
    [switch]$Help
)

# Functions
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    
    $colorMap = @{
        "Red" = "Red"
        "Green" = "Green"
        "Yellow" = "Yellow"
        "Blue" = "Blue"
        "White" = "White"
    }
    
    Write-Host $Message -ForegroundColor $colorMap[$Color]
}

function Write-Info {
    param([string]$Message)
    Write-ColorOutput "[INFO] $Message" "Blue"
}

function Write-Success {
    param([string]$Message)
    Write-ColorOutput "[SUCCESS] $Message" "Green"
}

function Write-Warning {
    param([string]$Message)
    Write-ColorOutput "[WARNING] $Message" "Yellow"
}

function Write-Error {
    param([string]$Message)
    Write-ColorOutput "[ERROR] $Message" "Red"
}

function Test-Command {
    param([string]$Command)
    
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

function Test-VersionFormat {
    param([string]$Version)
    
    if ($Version -notmatch '^\d+\.\d+\.\d+$') {
        Write-Error "Invalid version format: $Version (expected: X.Y.Z)"
        return $false
    }
    return $true
}

function Test-GitClean {
    $status = git status --porcelain
    if ($status) {
        Write-Error "Git working directory is not clean"
        git status --short
        return $false
    }
    return $true
}

function Invoke-Tests {
    Write-Info "Running tests..."
    
    $result = & make test
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Tests failed"
        return $false
    }
    
    Write-Success "Tests passed"
    return $true
}

function Invoke-QualityChecks {
    Write-Info "Running quality checks..."
    
    $result = & make quality
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Quality checks failed"
        return $false
    }
    
    Write-Success "Quality checks passed"
    return $true
}

function Test-Coverage {
    Write-Info "Checking test coverage..."
    
    $result = & make coverage
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Coverage check failed"
        return $false
    }
    
    Write-Success "Coverage check completed"
    return $true
}

function Update-Version {
    param([string]$Version)
    
    Write-Info "Updating version to $Version..."
    
    # Update pyproject.toml
    $content = Get-Content pyproject.toml -Raw
    $content = $content -replace 'version = ".*"', "version = `"$Version`""
    Set-Content pyproject.toml -Value $content -NoNewline
    
    # Update src/__init__.py if it exists
    if (Test-Path "src\__init__.py") {
        $content = Get-Content "src\__init__.py" -Raw
        $content = $content -replace '__version__ = ".*"', "__version__ = `"$Version`""
        Set-Content "src\__init__.py" -Value $content -NoNewline
    }
    
    Write-Success "Version updated to $Version"
}

function Build-DockerImage {
    param([string]$Version)
    
    Write-Info "Building Docker image..."
    
    docker build -t "ai-powershell:$Version" -t "ai-powershell:latest" .
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Docker build failed"
        return $false
    }
    
    Write-Success "Docker image built successfully"
    return $true
}

function Test-DockerImage {
    param([string]$Version)
    
    Write-Info "Testing Docker image..."
    
    docker run --rm "ai-powershell:$Version" python -c "from src.main import PowerShellAssistant; print('OK')"
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Docker image test failed"
        return $false
    }
    
    Write-Success "Docker image test passed"
    return $true
}

function Build-Package {
    Write-Info "Building Python package..."
    
    python -m build
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Package build failed"
        return $false
    }
    
    Write-Success "Package built successfully"
    return $true
}

function New-GitTag {
    param(
        [string]$Version,
        [string]$Message
    )
    
    Write-Info "Creating git tag v$Version..."
    
    git tag -a "v$Version" -m $Message
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to create tag"
        return $false
    }
    
    Write-Success "Tag created successfully"
    return $true
}

function Push-GitTag {
    param([string]$Version)
    
    Write-Info "Pushing tag v$Version..."
    
    git push origin "v$Version"
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to push tag"
        return $false
    }
    
    Write-Success "Tag pushed successfully"
    return $true
}

function New-GitHubRelease {
    param([string]$Version)
    
    Write-Info "Creating GitHub release..."
    
    if (-not (Test-Command "gh")) {
        Write-Warning "GitHub CLI not installed, skipping GitHub release"
        Write-Info "Create release manually at: https://github.com/0green7hand0/AI-PowerShell/releases/new"
        return $true
    }
    
    gh release create "v$Version" `
        --title "AI PowerShell $Version" `
        --notes-file RELEASE_NOTES.md `
        dist/*
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to create GitHub release"
        return $false
    }
    
    Write-Success "GitHub release created successfully"
    return $true
}

function Push-DockerImages {
    param([string]$Version)
    
    Write-Info "Pushing Docker images..."
    
    # Tag for GitHub Container Registry
    docker tag "ai-powershell:$Version" "ghcr.io/0green7hand0/ai-powershell:$Version"
    docker tag "ai-powershell:$Version" "ghcr.io/0green7hand0/ai-powershell:latest"
    
    # Push to GitHub Container Registry
    docker push "ghcr.io/0green7hand0/ai-powershell:$Version"
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to push Docker image (version tag)"
        return $false
    }
    
    docker push "ghcr.io/0green7hand0/ai-powershell:latest"
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to push Docker image (latest tag)"
        return $false
    }
    
    Write-Success "Docker images pushed successfully"
    return $true
}

function Start-Release {
    param(
        [string]$Version,
        [bool]$SkipTests,
        [bool]$SkipDocker
    )
    
    Write-Info "Starting release process for version $Version"
    Write-Host ""
    
    # Validate version
    if (-not (Test-VersionFormat $Version)) {
        exit 1
    }
    
    # Check prerequisites
    Write-Info "Checking prerequisites..."
    if (-not (Test-Command "git")) {
        Write-Error "Git is not installed"
        exit 1
    }
    if (-not (Test-Command "python")) {
        Write-Error "Python is not installed"
        exit 1
    }
    if (-not (Test-Command "docker")) {
        Write-Warning "Docker not found, skipping Docker steps"
        $SkipDocker = $true
    }
    
    # Check git status
    if (-not (Test-GitClean)) {
        Write-Error "Please commit or stash your changes first"
        exit 1
    }
    
    # Run tests
    if (-not $SkipTests) {
        if (-not (Invoke-Tests)) { exit 1 }
        if (-not (Invoke-QualityChecks)) { exit 1 }
        if (-not (Test-Coverage)) {
            Write-Warning "Coverage check had warnings"
        }
    }
    else {
        Write-Warning "Skipping tests (--SkipTests)"
    }
    
    # Update version
    Update-Version $Version
    
    # Commit version changes
    git add pyproject.toml
    if (Test-Path "src\__init__.py") {
        git add "src\__init__.py"
    }
    git commit -m "chore: bump version to $Version"
    
    # Build package
    if (-not (Build-Package)) { exit 1 }
    
    # Docker steps
    if (-not $SkipDocker) {
        if (-not (Build-DockerImage $Version)) { exit 1 }
        if (-not (Test-DockerImage $Version)) { exit 1 }
    }
    else {
        Write-Warning "Skipping Docker steps"
    }
    
    # Create and push tag
    if (-not (New-GitTag $Version "Release version $Version")) { exit 1 }
    
    # Push changes
    Write-Info "Pushing changes to remote..."
    git push origin main
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to push changes"
        exit 1
    }
    
    if (-not (Push-GitTag $Version)) { exit 1 }
    
    # Create GitHub release
    New-GitHubRelease $Version | Out-Null
    
    # Push Docker images
    if (-not $SkipDocker) {
        $response = Read-Host "Push Docker images to registry? (y/N)"
        if ($response -match '^[Yy]$') {
            Push-DockerImages $Version | Out-Null
        }
    }
    
    Write-Host ""
    Write-Success "Release $Version completed successfully!"
    Write-Host ""
    Write-Host "Next steps:"
    Write-Host "1. Verify GitHub release: https://github.com/0green7hand0/AI-PowerShell/releases/tag/v$Version"
    Write-Host "2. Announce release in GitHub Discussions"
    Write-Host "3. Update documentation if needed"
    Write-Host "4. Monitor for issues"
}

function Show-Help {
    Write-Host "AI PowerShell Release Script"
    Write-Host ""
    Write-Host "Usage: .\release.ps1 -Version <version> [options]"
    Write-Host ""
    Write-Host "Parameters:"
    Write-Host "  -Version <string>   Version number (e.g., 2.0.0) [Required]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -SkipTests          Skip running tests"
    Write-Host "  -SkipDocker         Skip Docker build and push"
    Write-Host "  -Help               Show this help message"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\release.ps1 -Version 2.0.0"
    Write-Host "  .\release.ps1 -Version 2.0.1 -SkipTests"
    Write-Host "  .\release.ps1 -Version 2.1.0 -SkipDocker"
}

# Main execution
if ($Help) {
    Show-Help
    exit 0
}

if (-not $Version) {
    Write-Error "Version number is required"
    Show-Help
    exit 1
}

Start-Release -Version $Version -SkipTests $SkipTests -SkipDocker $SkipDocker
