#!/bin/bash

# Production start script for AI PowerShell Assistant Web UI

set -e

echo "========================================="
echo "Starting AI PowerShell Assistant Web UI"
echo "========================================="

# Load environment variables if .env file exists
if [ -f "backend/.env" ]; then
    echo "Loading environment variables from backend/.env"
    export $(cat backend/.env | grep -v '^#' | xargs)
fi

# Set production environment
export FLASK_ENV=production
export FLASK_DEBUG=False

# Start backend with gunicorn
echo "Starting backend server..."
cd backend

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Error: Virtual environment not found. Run build.sh first."
    exit 1
fi

# Start gunicorn
echo "Starting Gunicorn server on ${HOST:-0.0.0.0}:${PORT:-5000}"
gunicorn -c gunicorn.conf.py wsgi:application

# Note: Frontend should be served by a web server like Nginx
# The built files are in ../dist directory
