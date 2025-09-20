# AI PowerShell Assistant Installation Script for Windows
# Supports PowerShell 5.1+ and PowerShell Core 7+

param(
    [switch]$NoDocker,
    [switch]$Dev,
    [switch]$Help,
    [string]$InstallPath = "$env:USERPROFILE\.powershell-assistant"
)

# Configuration
$RepoUrl = "https://github.com/0green7hand0/AI-PowerShell.git"
$PythonMinVersion = [Version]"3.8"
$RequiredCommands = @("python", "pip", "git")

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

function Test-PythonVersion {
    param([string]$PythonCommand)
    
    try {
        $versionOutput = & $PythonCommand --version 2>&1
        $versionString = $versionOutput -replace "Python ", ""
        $version = [Version]$versionString
        
        return $version -ge $PythonMinVersion
    }
    catch {
        return $false
    }
}

function Install-Dependencies {
    Write-Info "Installing dependencies for Windows..."
    
    # Check if running as Administrator
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
    
    # Install Chocolatey if not present
    if (-not (Test-Command "choco")) {
        Write-Info "Installing Chocolatey package manager..."
        if (-not $isAdmin) {
            Write-Warning "Administrator privileges recommended for Chocolatey installation"
        }
        
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        
        # Refresh environment variables
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    }
    
    # Install Python if not present or version is too old
    $pythonCommand = $null
    if (Test-Command "python" -and (Test-PythonVersion "python")) {
        $pythonCommand = "python"
    }
    elseif (Test-Command "python3" -and (Test-PythonVersion "python3")) {
        $pythonCommand = "python3"
    }
    else {
        Write-Info "Installing Python 3.11..."
        if ($isAdmin) {
            choco install python311 -y
        }
        else {
            Write-Warning "Please install Python 3.8+ manually from python.org or Microsoft Store"
            Write-Warning "Or run this script as Administrator to install automatically"
            return $false
        }
        
        # Refresh PATH
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        $pythonCommand = "python"
    }
    
    # Install Git if not present
    if (-not (Test-Command "git")) {
        Write-Info "Installing Git..."
        if ($isAdmin) {
            choco install git -y
        }
        else {
            Write-Warning "Please install Git manually from git-scm.com"
            Write-Warning "Or run this script as Administrator to install automatically"
            return $false
        }
        
        # Refresh PATH
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    }
    
    # Check PowerShell version
    $psVersion = $PSVersionTable.PSVersion
    if ($psVersion.Major -lt 5 -or ($psVersion.Major -eq 5 -and $psVersion.Minor -lt 1)) {
        Write-Warning "PowerShell 5.1+ or PowerShell Core 7+ is recommended"
        Write-Warning "Current version: $($psVersion.ToString())"
    }
    
    # Install PowerShell Core if not present
    if (-not (Test-Command "pwsh")) {
        Write-Info "Installing PowerShell Core..."
        if ($isAdmin) {
            choco install powershell-core -y
        }
        else {
            Write-Info "You can install PowerShell Core from Microsoft Store or GitHub releases"
        }
    }
    
    return $true
}

function Install-Docker {
    if ($NoDocker) {
        Write-Info "Skipping Docker installation (--NoDocker specified)"
        return
    }
    
    if (Test-Command "docker") {
        Write-Info "Docker is already installed"
        return
    }
    
    Write-Info "Installing Docker Desktop..."
    
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
    
    if ($isAdmin) {
        choco install docker-desktop -y
        Write-Warning "Please restart your computer after Docker Desktop installation completes"
    }
    else {
        Write-Warning "Please install Docker Desktop manually from docker.com"
        Write-Warning "Or run this script as Administrator to install automatically"
    }
}

function New-VirtualEnvironment {
    Write-Info "Creating Python virtual environment..."
    
    # Determine Python command
    $pythonCommand = $null
    if (Test-Command "python" -and (Test-PythonVersion "python")) {
        $pythonCommand = "python"
    }
    elseif (Test-Command "python3" -and (Test-PythonVersion "python3")) {
        $pythonCommand = "python3"
    }
    else {
        Write-Error "Python 3.8+ not found. Please install Python 3.8 or higher."
        return $false
    }
    
    # Create virtual environment
    $venvPath = Join-Path $InstallPath "venv"
    & $pythonCommand -m venv $venvPath
    
    if (-not $?) {
        Write-Error "Failed to create virtual environment"
        return $false
    }
    
    # Activate virtual environment
    $activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
    if (Test-Path $activateScript) {
        & $activateScript
    }
    else {
        Write-Error "Failed to find activation script"
        return $false
    }
    
    # Upgrade pip
    python -m pip install --upgrade pip
    
    return $true
}

function Install-Package {
    Write-Info "Installing AI PowerShell Assistant..."
    
    # Try to install from PyPI first
    try {
        pip install ai-powershell-assistant
        Write-Success "Installed from PyPI"
        return $true
    }
    catch {
        Write-Info "PyPI installation failed, installing from source..."
    }
    
    # Install from source
    $srcPath = Join-Path $InstallPath "src"
    if (Test-Path $srcPath) {
        Remove-Item $srcPath -Recurse -Force
    }
    
    git clone $RepoUrl $srcPath
    if (-not $?) {
        Write-Error "Failed to clone repository"
        return $false
    }
    
    Push-Location $srcPath
    try {
        pip install -r requirements.txt
        pip install -e .
        Write-Success "Installed from source"
        return $true
    }
    catch {
        Write-Error "Failed to install from source"
        return $false
    }
    finally {
        Pop-Location
    }
}

function New-Configuration {
    Write-Info "Creating default configuration..."
    
    $configPath = Join-Path $InstallPath "config"
    New-Item -ItemType Directory -Path $configPath -Force | Out-Null
    
    # Initialize configuration
    powershell-assistant init --config-dir $configPath
    
    if ($?) {
        Write-Success "Configuration created at $configPath"
        return $true
    }
    else {
        Write-Error "Failed to create configuration"
        return $false
    }
}

function New-LauncherScript {
    Write-Info "Creating launcher script..."
    
    # Create a PowerShell script launcher
    $launcherPath = Join-Path $env:USERPROFILE "AppData\Local\Microsoft\WindowsApps\powershell-assistant.ps1"
    $launcherDir = Split-Path $launcherPath -Parent
    
    if (-not (Test-Path $launcherDir)) {
        New-Item -ItemType Directory -Path $launcherDir -Force | Out-Null
    }
    
    $launcherContent = @"
# AI PowerShell Assistant Launcher
param([Parameter(ValueFromRemainingArguments=`$true)]`$Arguments)

`$InstallDir = "$InstallPath"
`$VenvDir = Join-Path `$InstallDir "venv"
`$ActivateScript = Join-Path `$VenvDir "Scripts\Activate.ps1"

# Activate virtual environment
if (Test-Path `$ActivateScript) {
    & `$ActivateScript
} else {
    Write-Error "Virtual environment not found at `$VenvDir"
    exit 1
}

# Run the application
& python -m src.main @Arguments
"@
    
    Set-Content -Path $launcherPath -Value $launcherContent
    
    # Create a batch file launcher for compatibility
    $batchLauncherPath = Join-Path $env:USERPROFILE "AppData\Local\Microsoft\WindowsApps\powershell-assistant.cmd"
    $batchContent = @"
@echo off
powershell.exe -ExecutionPolicy Bypass -File "$launcherPath" %*
"@
    
    Set-Content -Path $batchLauncherPath -Value $batchContent
    
    Write-Success "Launcher scripts created"
    Write-Info "You can now run 'powershell-assistant' from any PowerShell or Command Prompt"
}

function Test-Installation {
    Write-Info "Running installation tests..."
    
    # Test basic functionality
    try {
        $version = powershell-assistant --version 2>&1
        Write-Success "Basic functionality test passed"
    }
    catch {
        Write-Error "Basic functionality test failed"
        return $false
    }
    
    # Test PowerShell detection
    try {
        powershell-assistant test --powershell | Out-Null
        Write-Success "PowerShell detection test passed"
    }
    catch {
        Write-Warning "PowerShell detection test failed - PowerShell may not be properly configured"
    }
    
    # Test AI model (if available)
    try {
        powershell-assistant test --ai | Out-Null
        Write-Success "AI model test passed"
    }
    catch {
        Write-Warning "AI model test failed - you may need to download AI models"
    }
    
    # Test Docker (if available)
    if ((Test-Command "docker") -and (-not $NoDocker)) {
        try {
            powershell-assistant test --sandbox | Out-Null
            Write-Success "Docker sandbox test passed"
        }
        catch {
            Write-Warning "Docker sandbox test failed - Docker may not be running"
        }
    }
    
    return $true
}

function Show-NextSteps {
    Write-Success "Installation completed successfully!"
    Write-Host ""
    Write-Host "Next steps:"
    Write-Host "1. Open a new PowerShell window"
    Write-Host "2. Download AI models: powershell-assistant download-model"
    Write-Host "3. Start the server: powershell-assistant start"
    Write-Host "4. Test functionality: powershell-assistant test"
    Write-Host ""
    Write-Host "Configuration directory: $InstallPath\config"
    Write-Host "Documentation: https://github.com/0green7hand0/AI-PowerShell/docs"
    Write-Host ""
    Write-Host "For help: powershell-assistant --help"
}

function Show-Help {
    Write-Host "AI PowerShell Assistant Installation Script for Windows"
    Write-Host ""
    Write-Host "Usage: .\install.ps1 [OPTIONS]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -Help          Show this help message"
    Write-Host "  -NoDocker      Skip Docker installation"
    Write-Host "  -Dev           Install development version"
    Write-Host "  -InstallPath   Custom installation path (default: %USERPROFILE%\.powershell-assistant)"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\install.ps1"
    Write-Host "  .\install.ps1 -NoDocker"
    Write-Host "  .\install.ps1 -InstallPath C:\Tools\PowerShellAssistant"
}

# Main installation process
function Main {
    if ($Help) {
        Show-Help
        return
    }
    
    Write-Host "AI PowerShell Assistant Installation Script for Windows"
    Write-Host "====================================================="
    Write-Host ""
    
    # Check if already installed
    if (Test-Path $InstallPath) {
        Write-Warning "Installation directory already exists: $InstallPath"
        $response = Read-Host "Do you want to reinstall? (y/N)"
        if ($response -notmatch "^[Yy]$") {
            Write-Info "Installation cancelled"
            return
        }
        Remove-Item $InstallPath -Recurse -Force
    }
    
    # Create installation directory
    New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
    
    # Install system dependencies
    if (-not (Install-Dependencies)) {
        Write-Error "Failed to install dependencies"
        return
    }
    
    # Install Docker (optional)
    Install-Docker
    
    # Create virtual environment
    if (-not (New-VirtualEnvironment)) {
        Write-Error "Failed to create virtual environment"
        return
    }
    
    # Install the package
    if (-not (Install-Package)) {
        Write-Error "Failed to install package"
        return
    }
    
    # Create configuration
    if (-not (New-Configuration)) {
        Write-Error "Failed to create configuration"
        return
    }
    
    # Create launcher script
    New-LauncherScript
    
    # Run tests
    Test-Installation | Out-Null
    
    # Show next steps
    Show-NextSteps
}

# Run main installation
Main
