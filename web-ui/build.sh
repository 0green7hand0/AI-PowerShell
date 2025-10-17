#!/bin/bash

# Build script for AI PowerShell Assistant Web UI

set -e

echo "========================================="
echo "Building AI PowerShell Assistant Web UI"
echo "========================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed"
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Build frontend
echo -e "${BLUE}Building frontend...${NC}"
cd "$(dirname "$0")"

# Install frontend dependencies
echo "Installing frontend dependencies..."
npm install

# Run frontend tests (optional)
if [ "$SKIP_TESTS" != "true" ]; then
    echo "Running frontend tests..."
    npm run test:run || echo "Warning: Some tests failed"
fi

# Build frontend
echo "Building frontend for production..."
npm run build

echo -e "${GREEN}✓ Frontend build complete${NC}"

# Setup backend
echo -e "${BLUE}Setting up backend...${NC}"
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install backend dependencies
echo "Installing backend dependencies..."
pip install -r requirements.txt

# Run backend tests (optional)
if [ "$SKIP_TESTS" != "true" ]; then
    echo "Running backend tests..."
    python -m pytest tests/ || echo "Warning: Some tests failed"
fi

echo -e "${GREEN}✓ Backend setup complete${NC}"

# Deactivate virtual environment
deactivate

cd ..

echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}Build complete!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo "Frontend build output: ./dist"
echo "Backend is ready to run with: cd backend && source venv/bin/activate && gunicorn -c gunicorn.conf.py wsgi:application"
echo ""
