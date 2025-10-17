# Production start script for AI PowerShell Assistant Web UI (Windows)

$ErrorActionPreference = "Stop"

Write-Host "=========================================" -ForegroundColor Blue
Write-Host "Starting AI PowerShell Assistant Web UI" -ForegroundColor Blue
Write-Host "=========================================" -ForegroundColor Blue
Write-Host ""

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Load environment variables if .env file exists
$EnvFile = "backend\.env"
if (Test-Path $EnvFile) {
    Write-Host "Loading environment variables from $EnvFile"
    Get-Content $EnvFile | ForEach-Object {
        if ($_ -match '^([^#][^=]+)=(.*)$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            [Environment]::SetEnvironmentVariable($name, $value, "Process")
        }
    }
}

# Set production environment
$env:FLASK_ENV = "production"
$env:FLASK_DEBUG = "False"

# Start backend with gunicorn
Write-Host "Starting backend server..." -ForegroundColor Cyan
Set-Location backend

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "Error: Virtual environment not found. Run build.ps1 first." -ForegroundColor Red
    exit 1
}

# Activate virtual environment
& ".\venv\Scripts\Activate.ps1"

# Get host and port from environment or use defaults
$Host = if ($env:HOST) { $env:HOST } else { "0.0.0.0" }
$Port = if ($env:PORT) { $env:PORT } else { "5000" }

# Start gunicorn
Write-Host "Starting Gunicorn server on ${Host}:${Port}" -ForegroundColor Green
gunicorn -c gunicorn.conf.py wsgi:application

# Note: Frontend should be served by a web server like Nginx or IIS
# The built files are in ..\dist directory
