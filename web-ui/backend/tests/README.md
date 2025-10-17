# Backend API Tests

## Overview
Comprehensive unit tests for the AI PowerShell Assistant Web UI backend API.

## Test Structure

```
tests/
├── __init__.py                 # Test package initialization
├── conftest.py                 # Pytest fixtures and configuration
├── test_command_api.py         # Command translation API tests (Task 2.2)
└── README.md                   # This file
```

## Prerequisites

### Install Dependencies
```bash
pip install -r requirements.txt
pip install -r requirements-test.txt
```

### Required Packages
- pytest>=7.4.0
- pytest-cov>=4.1.0
- pytest-mock>=3.11.1
- Flask==3.0.0
- Flask-CORS==4.0.0
- Flask-SocketIO==5.3.6
- pydantic==2.5.3

## Running Tests

### Run All Tests
```bash
cd web-ui/backend
python -m pytest tests/ -v
```

### Run Specific Test File
```bash
python -m pytest tests/test_command_api.py -v
```

### Run Specific Test Class
```bash
python -m pytest tests/test_command_api.py::TestTranslateEndpoint -v
```

### Run Specific Test
```bash
python -m pytest tests/test_command_api.py::TestTranslateEndpoint::test_translate_success -v
```

### Run with Coverage
```bash
python -m pytest tests/ --cov=api --cov=models --cov-report=html
```

### Run with Detailed Output
```bash
python -m pytest tests/ -v --tb=short
```

### Run in Quiet Mode
```bash
python -m pytest tests/ -q
```

## Test Coverage

### Current Coverage (Task 2.2)
- **Command Translation API:** 100% (20/20 tests passing)
- **Request/Response Models:** 100% (6/6 tests passing)
- **Error Handling:** 100% (8/8 tests passing)

### Test Categories

#### 1. API Endpoint Tests (14 tests)
Tests for `/api/command/translate` endpoint:
- Success scenarios
- Context handling
- Security checks
- Error handling
- Edge cases

#### 2. Model Validation Tests (6 tests)
Tests for Pydantic models:
- TranslateRequest validation
- TranslateResponse validation
- SecurityInfo validation
- Default values

## Test Fixtures

### Available Fixtures (conftest.py)
- `app` - Flask application instance
- `client` - Flask test client
- `mock_assistant` - Mock PowerShellAssistant
- `mock_suggestion` - Mock AI engine suggestion
- `mock_validation` - Mock security validation
- `mock_execution_result` - Mock execution result

### Using Fixtures
```python
def test_example(client, mock_assistant):
    """Example test using fixtures"""
    with patch('api.command.get_assistant', return_value=mock_assistant):
        response = client.post('/api/command/translate', json={
            'input': 'test command'
        })
        assert response.status_code == 200
```

## Writing New Tests

### Test Template
```python
class TestNewFeature:
    """Tests for new feature"""
    
    def test_success_case(self, client):
        """Test successful operation"""
        response = client.post('/api/endpoint', json={
            'data': 'value'
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
    
    def test_error_case(self, client):
        """Test error handling"""
        response = client.post('/api/endpoint', json={})
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
```

### Best Practices
1. Use descriptive test names
2. Test one thing per test
3. Use fixtures for common setup
4. Mock external dependencies
5. Test both success and error cases
6. Verify response structure
7. Check HTTP status codes
8. Validate error messages

## Continuous Integration

### GitHub Actions Example
```yaml
name: Backend Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt
      - name: Run tests
        run: |
          cd web-ui/backend
          python -m pytest tests/ -v --cov=api --cov=models
```

## Troubleshooting

### Common Issues

#### 1. ModuleNotFoundError: No module named 'flask'
**Solution:** Install Flask
```bash
pip install Flask==3.0.0
```

#### 2. Import errors for PowerShellAssistant
**Solution:** Ensure parent directory is in path (handled in conftest.py)

#### 3. Tests fail with "No data to report" coverage warning
**Solution:** This is normal when running model-only tests. Ignore or disable coverage.

#### 4. Fixture not found
**Solution:** Ensure conftest.py is in the tests directory

## Test Reports

### Generate HTML Coverage Report
```bash
python -m pytest tests/ --cov=api --cov=models --cov-report=html
# Open htmlcov/index.html in browser
```

### Generate XML Coverage Report (for CI)
```bash
python -m pytest tests/ --cov=api --cov=models --cov-report=xml
```

### Generate Terminal Coverage Report
```bash
python -m pytest tests/ --cov=api --cov=models --cov-report=term-missing
```

## Performance Testing

### Run with Timing
```bash
python -m pytest tests/ -v --durations=10
```

### Run with Profiling
```bash
python -m pytest tests/ --profile
```

## Debugging Tests

### Run with PDB on Failure
```bash
python -m pytest tests/ --pdb
```

### Run with Print Statements
```bash
python -m pytest tests/ -s
```

### Run Last Failed Tests
```bash
python -m pytest tests/ --lf
```

## Test Markers

### Define Custom Markers (pytest.ini)
```ini
[pytest]
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    unit: marks tests as unit tests
```

### Use Markers
```python
@pytest.mark.slow
def test_slow_operation(client):
    """This test takes a long time"""
    pass
```

### Run Specific Markers
```bash
python -m pytest tests/ -m "not slow"
```

## Contributing

### Adding New Tests
1. Create test file in `tests/` directory
2. Import necessary fixtures from conftest.py
3. Write test classes and methods
4. Run tests to verify
5. Update this README if needed

### Test Naming Convention
- Test files: `test_*.py`
- Test classes: `Test*`
- Test methods: `test_*`

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Flask Testing](https://flask.palletsprojects.com/en/2.3.x/testing/)
- [Pydantic Validation](https://docs.pydantic.dev/)
- [Mock Documentation](https://docs.python.org/3/library/unittest.mock.html)

## Contact

For questions or issues with tests, please refer to:
- Task documentation in `TASK_2.2_SUMMARY.md`
- Verification report in `TASK_2.2_VERIFICATION.md`
- Main README in `web-ui/backend/README.md`
