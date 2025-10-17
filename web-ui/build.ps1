# Build script for AI PowerShell Assistant Web UI (Windows)

$ErrorActionPreference = "Stop"

Write-Host "=========================================" -ForegroundColor Blue
Write-Host "Building AI PowerShell Assistant Web UI" -ForegroundColor Blue
Write-Host "=========================================" -ForegroundColor Blue
Write-Host ""

# Check if Node.js is installed
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Node.js is not installed" -ForegroundColor Red
    exit 1
}

# Check if Python is installed
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Python is not installed" -ForegroundColor Red
    exit 1
}

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Build frontend
Write-Host "Building frontend..." -ForegroundColor Cyan

# Install frontend dependencies
Write-Host "Installing frontend dependencies..."
npm install

# Run frontend tests (optional)
if ($env:SKIP_TESTS -ne "true") {
    Write-Host "Running frontend tests..."
    try {
        npm run test:run
    } catch {
        Write-Host "Warning: Some tests failed" -ForegroundColor Yellow
    }
}

# Build frontend
Write-Host "Building frontend for production..."
npm run build

Write-Host "✓ Frontend build complete" -ForegroundColor Green
Write-Host ""

# Setup backend
Write-Host "Setting up backend..." -ForegroundColor Cyan
Set-Location backend

# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "Creating Python virtual environment..."
    python -m venv venv
}

# Activate virtual environment
& ".\venv\Scripts\Activate.ps1"

# Install backend dependencies
Write-Host "Installing backend dependencies..."
pip install -r requirements.txt

# Run backend tests (optional)
if ($env:SKIP_TESTS -ne "true") {
    Write-Host "Running backend tests..."
    try {
        python -m pytest tests/
    } catch {
        Write-Host "Warning: Some tests failed" -ForegroundColor Yellow
    }
}

Write-Host "✓ Backend setup complete" -ForegroundColor Green

# Deactivate virtual environment
deactivate

Set-Location ..

Write-Host ""
Write-Host "=========================================" -ForegroundColor Green
Write-Host "Build complete!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Frontend build output: .\dist"
Write-Host "Backend is ready to run with: cd backend; .\venv\Scripts\Activate.ps1; gunicorn -c gunicorn.conf.py wsgi:application"
Write-Host ""
