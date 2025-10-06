# Makefile for AI PowerShell Assistant
# Provides convenient commands for development tasks

.PHONY: help install install-dev test test-unit test-integration coverage lint format type-check clean docs

# Default target
help:
	@echo "AI PowerShell Assistant - Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install          Install production dependencies"
	@echo "  make install-dev      Install development dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  make test             Run all tests"
	@echo "  make test-unit        Run unit tests only"
	@echo "  make test-integration Run integration tests only"
	@echo "  make coverage         Run tests with coverage report"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint             Run all linters (flake8, pylint)"
	@echo "  make format           Format code with black and isort"
	@echo "  make type-check       Run type checking with mypy"
	@echo "  make quality          Run all quality checks"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build     Build Docker image"
	@echo "  make docker-run       Run Docker container interactively"
	@echo "  make docker-compose-up   Start all services"
	@echo "  make docker-compose-down Stop all services"
	@echo "  make docker-test      Test Docker image"
	@echo "  make docker-clean     Clean Docker resources"
	@echo ""
	@echo "Release:"
	@echo "  make release-check    Check release readiness"
	@echo "  make release-build    Build release artifacts"
	@echo "  make release-tag      Create and push release tag"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean            Clean build artifacts and cache"
	@echo "  make docs             Generate documentation"
	@echo "  make security         Run security checks"

# Installation
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt
	pre-commit install

# Testing
test:
	pytest -v

test-unit:
	pytest tests/ -v --ignore=tests/integration/

test-integration:
	pytest tests/integration/ -v

coverage:
	pytest --cov=src --cov-report=term-missing --cov-report=html --cov-report=xml
	@echo ""
	@echo "Coverage report generated: htmlcov/index.html"

# Code Quality
lint:
	@echo "Running flake8..."
	flake8 src/ tests/
	@echo ""
	@echo "Running pylint..."
	pylint src/ --exit-zero

format:
	@echo "Formatting with black..."
	black src/ tests/
	@echo ""
	@echo "Sorting imports with isort..."
	isort src/ tests/

format-check:
	@echo "Checking formatting with black..."
	black --check --diff src/ tests/
	@echo ""
	@echo "Checking import sorting with isort..."
	isort --check-only --diff src/ tests/

type-check:
	mypy src/ --ignore-missing-imports --no-strict-optional

quality: format-check lint type-check
	@echo ""
	@echo "✅ All quality checks passed!"

# Security
security:
	@echo "Checking dependencies for vulnerabilities..."
	safety check
	@echo ""
	@echo "Running bandit security linter..."
	bandit -r src/ -f json -o bandit-report.json
	@echo "Security report generated: bandit-report.json"

# Maintenance
clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/ dist/ *.egg-info
	rm -rf .pytest_cache/ .mypy_cache/ .coverage htmlcov/
	rm -rf coverage.xml coverage.json bandit-report.json
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "✅ Cleaned!"

# Documentation
docs:
	@echo "Generating documentation..."
	sphinx-build -b html docs/ docs/_build/
	@echo "Documentation generated: docs/_build/index.html"

# Pre-commit
pre-commit:
	pre-commit run --all-files

# CI simulation
ci: quality test coverage
	@echo ""
	@echo "✅ CI checks completed successfully!"

# Docker commands
docker-build:
	@echo "Building Docker image..."
	docker build -t ai-powershell:2.0.0 -t ai-powershell:latest .
	@echo "✅ Docker image built successfully!"

docker-build-no-cache:
	@echo "Building Docker image (no cache)..."
	docker build --no-cache -t ai-powershell:2.0.0 -t ai-powershell:latest .
	@echo "✅ Docker image built successfully!"

docker-run:
	@echo "Running Docker container..."
	docker run -it --rm \
		-v $(PWD)/config:/app/config:ro \
		-v ai-powershell-logs:/app/logs \
		-v ai-powershell-data:/app/data \
		ai-powershell:2.0.0

docker-compose-up:
	@echo "Starting services with docker-compose..."
	docker-compose up -d
	@echo "✅ Services started!"
	@echo "View logs: docker-compose logs -f"

docker-compose-down:
	@echo "Stopping services..."
	docker-compose down
	@echo "✅ Services stopped!"

docker-compose-logs:
	docker-compose logs -f

docker-compose-restart:
	@echo "Restarting services..."
	docker-compose restart
	@echo "✅ Services restarted!"

docker-test:
	@echo "Testing Docker image..."
	docker run --rm ai-powershell:2.0.0 python -c "from src.main import PowerShellAssistant; print('✅ Docker image test passed!')"

docker-clean:
	@echo "Cleaning Docker resources..."
	docker-compose down -v
	docker rmi ai-powershell:2.0.0 ai-powershell:latest || true
	@echo "✅ Docker resources cleaned!"

docker-push:
	@echo "Pushing Docker image to registry..."
	docker tag ai-powershell:2.0.0 ghcr.io/0green7hand0/ai-powershell:2.0.0
	docker tag ai-powershell:2.0.0 ghcr.io/0green7hand0/ai-powershell:latest
	docker push ghcr.io/0green7hand0/ai-powershell:2.0.0
	docker push ghcr.io/0green7hand0/ai-powershell:latest
	@echo "✅ Docker images pushed!"

# Release commands
release-check:
	@echo "Checking release readiness..."
	@echo "1. Running tests..."
	@make test
	@echo "2. Running quality checks..."
	@make quality
	@echo "3. Checking coverage..."
	@make coverage
	@echo "4. Building Docker image..."
	@make docker-build
	@echo "5. Testing Docker image..."
	@make docker-test
	@echo ""
	@echo "✅ Release checks completed successfully!"

release-build: release-check
	@echo "Building release artifacts..."
	python -m build
	@echo "✅ Release artifacts built in dist/"

release-tag:
	@echo "Creating release tag..."
	git tag -a v2.0.0 -m "Release version 2.0.0"
	git push origin v2.0.0
	@echo "✅ Release tag created and pushed!"
