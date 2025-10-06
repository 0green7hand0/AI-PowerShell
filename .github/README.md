# CI/CD Configuration

This directory contains the Continuous Integration and Continuous Deployment (CI/CD) configuration for the AI PowerShell Assistant project.

## Workflows

### 1. CI Workflow (`ci.yml`)

Main continuous integration workflow that runs on every push and pull request.

**Jobs:**
- **test**: Runs tests on multiple OS (Ubuntu, Windows, macOS) and Python versions (3.8-3.11)
- **code-quality**: Runs code quality checks (black, flake8, mypy)
- **integration-tests**: Runs integration tests
- **security-scan**: Scans for security vulnerabilities

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

### 2. Code Quality Workflow (`code-quality.yml`)

Dedicated workflow for code quality checks.

**Jobs:**
- **black**: Code formatting check
- **flake8**: Linting
- **mypy**: Type checking
- **pylint**: Code analysis
- **isort**: Import sorting check

### 3. Coverage Workflow (`coverage.yml`)

Test coverage reporting and enforcement.

**Jobs:**
- **coverage**: Generate coverage reports and enforce 80% threshold
- **coverage-diff**: Show coverage changes in pull requests
- **module-coverage**: Per-module coverage checks

**Features:**
- Uploads coverage to Codecov
- Comments coverage on pull requests
- Generates HTML, XML, and JSON reports
- Enforces 80% coverage threshold

## Configuration Files

### `.flake8`
Flake8 linter configuration:
- Max line length: 127
- Max complexity: 10
- Ignores: E203, W503, E501

### `pyproject.toml`
Configuration for:
- **black**: Code formatter (line length: 127)
- **mypy**: Type checker
- **pytest**: Test runner with coverage
- **isort**: Import sorter
- **bandit**: Security linter
- **pylint**: Code analyzer

### `.coveragerc`
Coverage configuration:
- Source: `src/`
- Fail under: 80%
- Excludes test files and backup directory

### `.pre-commit-config.yaml`
Pre-commit hooks for local development:
- Trailing whitespace removal
- End-of-file fixer
- YAML/JSON/TOML validation
- Black formatting
- isort import sorting
- flake8 linting
- mypy type checking
- bandit security checks

## Local Development

### Setup Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### Run Tests Locally

```bash
# All tests
pytest

# With coverage
pytest --cov=src --cov-report=html

# Or use the script
./scripts/run-coverage.sh      # Linux/macOS
.\scripts\run-coverage.ps1     # Windows
```

### Code Quality Checks

```bash
# Format code
black src/ tests/
isort src/ tests/

# Check formatting
black --check src/ tests/

# Lint
flake8 src/ tests/

# Type check
mypy src/

# Or use Makefile
make format
make lint
make type-check
make quality  # Run all checks
```

### Using Makefile

```bash
# Show all commands
make help

# Install dependencies
make install-dev

# Run tests
make test
make coverage

# Code quality
make format
make lint
make type-check
make quality

# Clean artifacts
make clean

# Simulate CI
make ci
```

## Coverage Requirements

The project enforces an 80% code coverage threshold:

- **Overall coverage**: Must be ≥ 80%
- **Module coverage**: Each module should aim for ≥ 80%
- **New code**: Pull requests should not decrease coverage

Coverage reports are:
- Uploaded to Codecov
- Available as HTML artifacts
- Commented on pull requests

## Security Scanning

Security checks include:

1. **Safety**: Checks dependencies for known vulnerabilities
2. **Bandit**: Scans Python code for security issues
3. **Pre-commit**: Detects private keys and sensitive data

## Badge Status

Add these badges to your README:

```markdown
![CI](https://github.com/0green7hand0/AI-PowerShell/workflows/CI/badge.svg)
![Coverage](https://codecov.io/gh/0green7hand0/AI-PowerShell/branch/main/graph/badge.svg)
![Code Quality](https://github.com/0green7hand0/AI-PowerShell/workflows/Code%20Quality/badge.svg)
```

## Troubleshooting

### Tests Failing Locally but Passing in CI

- Check Python version (CI uses 3.8-3.11)
- Ensure all dependencies are installed
- Check for platform-specific issues

### Coverage Below Threshold

- Run `pytest --cov=src --cov-report=term-missing` to see uncovered lines
- Add tests for uncovered code
- Use `# pragma: no cover` for code that shouldn't be tested

### Pre-commit Hooks Failing

- Run `pre-commit run --all-files` to see all issues
- Fix formatting: `make format`
- Fix linting: Address flake8 warnings
- Update hooks: `pre-commit autoupdate`

## Contributing

When contributing:

1. Install pre-commit hooks: `pre-commit install`
2. Run tests locally: `make test`
3. Check coverage: `make coverage`
4. Run quality checks: `make quality`
5. Ensure all checks pass before pushing

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [pytest Documentation](https://docs.pytest.org/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [Black Documentation](https://black.readthedocs.io/)
- [Flake8 Documentation](https://flake8.pycqa.org/)
- [mypy Documentation](https://mypy.readthedocs.io/)
