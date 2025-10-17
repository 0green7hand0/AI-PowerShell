# Testing Guide

This document provides comprehensive information about testing the AI PowerShell Web UI application.

## Table of Contents

- [Overview](#overview)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Frontend Unit Tests](#frontend-unit-tests)
- [Backend Unit Tests](#backend-unit-tests)
- [E2E Tests](#e2e-tests)
- [Test Coverage](#test-coverage)
- [Writing Tests](#writing-tests)
- [CI/CD Integration](#cicd-integration)

## Overview

The project uses a comprehensive testing strategy with three layers:

1. **Frontend Unit Tests** - Component and store tests using Vitest and Vue Test Utils
2. **Backend Unit Tests** - API and model tests using pytest
3. **E2E Tests** - End-to-end user flow tests using Playwright

## Test Structure

```
web-ui/
├── tests/
│   ├── setup.ts                    # Vitest setup
│   ├── components/                 # Component tests
│   │   ├── SecurityBadge.spec.ts
│   │   ├── CodeBlock.spec.ts
│   │   ├── InputBox.spec.ts
│   │   └── CommandCard.spec.ts
│   ├── stores/                     # Store tests
│   │   ├── chat.spec.ts
│   │   ├── history.spec.ts
│   │   └── template.spec.ts
│   ├── utils/                      # Utility tests
│   │   ├── validation.spec.ts
│   │   └── format.spec.ts
│   └── e2e/                        # E2E tests
│       ├── chat.spec.ts
│       ├── history.spec.ts
│       └── template.spec.ts
├── backend/tests/
│   ├── conftest.py                 # Pytest fixtures
│   ├── test_command_api.py         # Command API tests
│   ├── test_history_api.py         # History API tests
│   ├── test_template_api.py        # Template API tests
│   ├── test_config_api.py          # Config API tests
│   ├── test_logs_api.py            # Logs API tests
│   ├── test_auth_api.py            # Auth API tests
│   ├── test_models.py              # Model validation tests
│   └── test_validation.py          # Validation tests
└── playwright.config.ts            # Playwright configuration
```

## Running Tests

### Frontend Unit Tests

```bash
# Run all unit tests
npm run test

# Run tests in watch mode
npm run test

# Run tests once
npm run test:run

# Run with UI
npm run test:ui

# Run with coverage
npm run test:coverage
```

### Backend Unit Tests

```bash
# Navigate to backend directory
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_command_api.py

# Run specific test
pytest tests/test_command_api.py::TestTranslateEndpoint::test_translate_success

# Run with verbose output
pytest -v

# Run with output
pytest -s
```

### E2E Tests

```bash
# Install Playwright browsers (first time only)
npx playwright install

# Run all E2E tests
npm run test:e2e

# Run with UI mode
npm run test:e2e:ui

# Run in headed mode (see browser)
npm run test:e2e:headed

# Run specific test file
npx playwright test tests/e2e/chat.spec.ts

# Run specific test
npx playwright test tests/e2e/chat.spec.ts -g "should send message"

# Debug mode
npx playwright test --debug
```

## Frontend Unit Tests

### Component Tests

Component tests verify that Vue components render correctly and handle user interactions.

**Example: SecurityBadge.spec.ts**
```typescript
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import SecurityBadge from '@/components/SecurityBadge.vue'

describe('SecurityBadge', () => {
  it('renders safe badge with correct color', () => {
    const wrapper = mount(SecurityBadge, {
      props: { level: 'safe', size: 'medium' }
    })
    
    expect(wrapper.find('.security-badge.safe').exists()).toBe(true)
    expect(wrapper.text()).toContain('安全')
  })
})
```

### Store Tests

Store tests verify Pinia store actions, getters, and state management.

**Example: chat.spec.ts**
```typescript
import { setActivePinia, createPinia } from 'pinia'
import { useChatStore } from '@/stores/chat'

describe('Chat Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('adds user message when sending', async () => {
    const store = useChatStore()
    await store.sendMessage('test')
    
    expect(store.messages.length).toBeGreaterThan(0)
    expect(store.messages[0].type).toBe('user')
  })
})
```

### Utility Tests

Utility tests verify helper functions and utilities.

**Example: validation.spec.ts**
```typescript
import { validateEmail } from '@/utils/validation'

describe('validateEmail', () => {
  it('validates correct email addresses', () => {
    expect(validateEmail('test@example.com')).toBe(true)
  })

  it('rejects invalid email addresses', () => {
    expect(validateEmail('invalid')).toBe(false)
  })
})
```

## Backend Unit Tests

### API Tests

API tests verify endpoint behavior, request/response handling, and error cases.

**Example: test_command_api.py**
```python
def test_translate_success(client, mock_assistant, mock_suggestion, mock_validation):
    """Test successful command translation"""
    mock_assistant.ai_engine.translate_natural_language.return_value = mock_suggestion
    mock_assistant.security_engine.validate_command.return_value = mock_validation
    
    with patch('api.command.get_assistant', return_value=mock_assistant):
        response = client.post('/api/command/translate', 
            json={'input': '显示当前时间'}
        )
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert data['data']['command'] == 'Get-Date'
```

### Model Tests

Model tests verify Pydantic model validation and serialization.

**Example: test_models.py**
```python
def test_translate_request_valid():
    """Test valid TranslateRequest"""
    from models.command import TranslateRequest
    
    request = TranslateRequest(input='显示当前时间')
    assert request.input == '显示当前时间'
```

## E2E Tests

E2E tests verify complete user workflows across the application.

### Chat Flow Test

```typescript
test('should send message and receive response', async ({ page }) => {
  await page.goto('/')
  
  // Type message
  await page.locator('textarea').fill('显示当前时间')
  
  // Send message
  await page.locator('.send-button').click()
  
  // Verify user message
  await expect(page.locator('.message-card.user').last())
    .toContainText('显示当前时间')
  
  // Verify AI response
  await expect(page.locator('.command-card').last())
    .toBeVisible({ timeout: 10000 })
})
```

### History Flow Test

```typescript
test('should view and re-execute history', async ({ page }) => {
  await page.goto('/history')
  
  // Click on history item
  await page.locator('.history-card').first().click()
  
  // View details
  await expect(page.locator('.history-detail-dialog')).toBeVisible()
  
  // Re-execute
  await page.locator('.rerun-button').click()
  await expect(page).toHaveURL(/\/chat/)
})
```

### Template Flow Test

```typescript
test('should create and use template', async ({ page }) => {
  await page.goto('/templates')
  
  // Create template
  await page.locator('.create-template-button').click()
  await page.locator('input[name="name"]').fill('Test Template')
  await page.locator('.submit-button').click()
  
  // Use template
  await page.locator('.template-card').first().locator('.use-button').click()
  await expect(page.locator('.template-use-dialog')).toBeVisible()
})
```

## Test Coverage

### Viewing Coverage Reports

**Frontend:**
```bash
npm run test:coverage
# Open htmlcov/index.html in browser
```

**Backend:**
```bash
cd backend
pytest --cov=. --cov-report=html
# Open htmlcov/index.html in browser
```

### Coverage Goals

- **Overall Coverage**: > 80%
- **Critical Paths**: > 90%
- **API Endpoints**: 100%
- **Models**: 100%
- **Components**: > 85%
- **Stores**: > 90%

## Writing Tests

### Best Practices

1. **Test Naming**
   - Use descriptive names: `test_translate_success`, `should display chat interface`
   - Follow pattern: `should [expected behavior] when [condition]`

2. **Test Structure**
   - Arrange: Set up test data and mocks
   - Act: Execute the code being tested
   - Assert: Verify the results

3. **Mocking**
   - Mock external dependencies (API calls, file system, etc.)
   - Use fixtures for common test data
   - Keep mocks simple and focused

4. **Assertions**
   - Test one thing per test
   - Use specific assertions
   - Include helpful error messages

5. **Test Data**
   - Use realistic test data
   - Cover edge cases
   - Test error conditions

### Example Test Template

**Frontend:**
```typescript
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import MyComponent from '@/components/MyComponent.vue'

describe('MyComponent', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(MyComponent, {
      props: { /* props */ }
    })
  })

  it('should render correctly', () => {
    expect(wrapper.find('.my-element').exists()).toBe(true)
  })

  it('should handle user interaction', async () => {
    await wrapper.find('button').trigger('click')
    expect(wrapper.emitted('event')).toBeTruthy()
  })
})
```

**Backend:**
```python
import pytest
from unittest.mock import patch, MagicMock

class TestMyEndpoint:
    """Tests for /api/my-endpoint"""
    
    def test_success_case(self, client, mock_assistant):
        """Test successful request"""
        # Arrange
        mock_assistant.method.return_value = expected_result
        
        # Act
        with patch('api.module.get_assistant', return_value=mock_assistant):
            response = client.post('/api/my-endpoint', json={'data': 'test'})
        
        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
    
    def test_error_case(self, client, mock_assistant):
        """Test error handling"""
        mock_assistant.method.side_effect = Exception('Error')
        
        with patch('api.module.get_assistant', return_value=mock_assistant):
            response = client.post('/api/my-endpoint', json={'data': 'test'})
        
        assert response.status_code == 500
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run test:run
      - run: npm run test:coverage

  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements-test.txt
      - run: pytest --cov=. --cov-report=xml

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npx playwright install --with-deps
      - run: npm run test:e2e
```

## Troubleshooting

### Common Issues

**Frontend Tests:**
- **Issue**: Component not rendering
  - **Solution**: Check if all dependencies are mocked in setup.ts

- **Issue**: Async tests timing out
  - **Solution**: Increase timeout or use `waitFor` utilities

**Backend Tests:**
- **Issue**: Import errors
  - **Solution**: Check sys.path configuration in conftest.py

- **Issue**: Mock not working
  - **Solution**: Verify patch path matches actual import path

**E2E Tests:**
- **Issue**: Element not found
  - **Solution**: Add explicit waits with `waitForSelector`

- **Issue**: Tests flaky
  - **Solution**: Use `waitForLoadState('networkidle')` and increase timeouts

## Resources

- [Vitest Documentation](https://vitest.dev/)
- [Vue Test Utils](https://test-utils.vuejs.org/)
- [Playwright Documentation](https://playwright.dev/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Testing Best Practices](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)

## Contributing

When adding new features:

1. Write tests first (TDD approach recommended)
2. Ensure all tests pass before submitting PR
3. Maintain or improve code coverage
4. Update this guide if adding new test patterns
