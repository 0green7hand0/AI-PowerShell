# Tests Directory

This directory contains all frontend tests for the AI PowerShell Web UI application.

## Directory Structure

```
tests/
├── setup.ts                    # Test setup and global mocks
├── components/                 # Component unit tests
│   ├── SecurityBadge.spec.ts  # Security badge component tests
│   ├── CodeBlock.spec.ts      # Code block component tests
│   ├── InputBox.spec.ts       # Input box component tests
│   └── CommandCard.spec.ts    # Command card component tests
├── stores/                     # Pinia store tests
│   ├── chat.spec.ts           # Chat store tests
│   ├── history.spec.ts        # History store tests
│   └── template.spec.ts       # Template store tests
├── utils/                      # Utility function tests
│   ├── validation.spec.ts     # Validation utility tests
│   └── format.spec.ts         # Formatting utility tests
└── e2e/                        # End-to-end tests
    ├── chat.spec.ts           # Chat flow E2E tests
    ├── history.spec.ts        # History flow E2E tests
    └── template.spec.ts       # Template flow E2E tests
```

## Test Types

### Component Tests

Component tests verify that Vue components render correctly and handle user interactions properly.

**Location**: `tests/components/`

**What they test**:
- Component rendering
- Props handling
- Event emissions
- User interactions
- Conditional rendering
- Computed properties

**Example**:
```typescript
import { mount } from '@vue/test-utils'
import SecurityBadge from '@/components/SecurityBadge.vue'

it('renders safe badge', () => {
  const wrapper = mount(SecurityBadge, {
    props: { level: 'safe' }
  })
  expect(wrapper.find('.security-badge.safe').exists()).toBe(true)
})
```

### Store Tests

Store tests verify Pinia store state management, actions, and getters.

**Location**: `tests/stores/`

**What they test**:
- State initialization
- Action execution
- State mutations
- Async operations
- Error handling
- API integration (mocked)

**Example**:
```typescript
import { setActivePinia, createPinia } from 'pinia'
import { useChatStore } from '@/stores/chat'

beforeEach(() => {
  setActivePinia(createPinia())
})

it('sends message', async () => {
  const store = useChatStore()
  await store.sendMessage('test')
  expect(store.messages.length).toBeGreaterThan(0)
})
```

### Utility Tests

Utility tests verify helper functions and utilities.

**Location**: `tests/utils/`

**What they test**:
- Input validation
- Data formatting
- String manipulation
- Date/time utilities
- Error handling

**Example**:
```typescript
import { validateEmail } from '@/utils/validation'

it('validates email', () => {
  expect(validateEmail('test@example.com')).toBe(true)
  expect(validateEmail('invalid')).toBe(false)
})
```

### E2E Tests

E2E tests verify complete user workflows across the application.

**Location**: `tests/e2e/`

**What they test**:
- Complete user flows
- Multi-page interactions
- Real API calls (or mocked)
- Browser compatibility
- Mobile responsiveness

**Example**:
```typescript
test('sends message and receives response', async ({ page }) => {
  await page.goto('/')
  await page.locator('textarea').fill('test')
  await page.locator('.send-button').click()
  await expect(page.locator('.command-card')).toBeVisible()
})
```

## Running Tests

### All Unit Tests
```bash
npm run test              # Watch mode
npm run test:run          # Run once
npm run test:ui           # UI mode
npm run test:coverage     # With coverage
```

### Specific Test File
```bash
npm run test -- tests/components/SecurityBadge.spec.ts
```

### Specific Test
```bash
npm run test -- -t "should render safe badge"
```

### E2E Tests
```bash
npm run test:e2e          # All E2E tests
npm run test:e2e:ui       # UI mode
npm run test:e2e:headed   # See browser
```

## Test Setup

The `setup.ts` file contains global test configuration:

- **Element Plus Mocks**: Stubs for Element Plus components
- **Window Mocks**: matchMedia, localStorage, clipboard
- **Global Configuration**: Vue Test Utils global config

## Writing Tests

### Component Test Template

```typescript
import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import MyComponent from '@/components/MyComponent.vue'

describe('MyComponent', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(MyComponent, {
      props: {
        // component props
      }
    })
  })

  it('should render correctly', () => {
    expect(wrapper.find('.my-element').exists()).toBe(true)
  })

  it('should handle click', async () => {
    await wrapper.find('button').trigger('click')
    expect(wrapper.emitted('click')).toBeTruthy()
  })
})
```

### Store Test Template

```typescript
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useMyStore } from '@/stores/my'
import * as api from '@/api/my'

vi.mock('@/api/my')

describe('My Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('should fetch data', async () => {
    const store = useMyStore()
    vi.mocked(api.getData).mockResolvedValue({ data: 'test' })
    
    await store.fetchData()
    
    expect(store.data).toBe('test')
  })
})
```

### E2E Test Template

```typescript
import { test, expect } from '@playwright/test'

test.describe('My Feature', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/my-page')
  })

  test('should complete workflow', async ({ page }) => {
    // Arrange
    await page.locator('input').fill('test')
    
    // Act
    await page.locator('button').click()
    
    // Assert
    await expect(page.locator('.result')).toBeVisible()
  })
})
```

## Best Practices

1. **Test Naming**: Use descriptive names that explain what is being tested
2. **Test Structure**: Follow Arrange-Act-Assert pattern
3. **Test Isolation**: Each test should be independent
4. **Mock External Dependencies**: Mock API calls, file system, etc.
5. **Test One Thing**: Each test should verify one specific behavior
6. **Use Fixtures**: Reuse common test data and setup
7. **Async Handling**: Properly handle async operations with await
8. **Error Testing**: Test both success and failure cases
9. **Edge Cases**: Test boundary conditions and edge cases
10. **Keep Tests Fast**: Unit tests should run in milliseconds

## Common Patterns

### Testing Async Operations

```typescript
it('should handle async operation', async () => {
  const store = useMyStore()
  await store.asyncAction()
  expect(store.data).toBeDefined()
})
```

### Testing Events

```typescript
it('should emit event', async () => {
  await wrapper.find('button').trigger('click')
  expect(wrapper.emitted('myEvent')).toBeTruthy()
  expect(wrapper.emitted('myEvent')[0]).toEqual(['value'])
})
```

### Testing Conditional Rendering

```typescript
it('should show element when condition is true', async () => {
  await wrapper.setProps({ show: true })
  expect(wrapper.find('.element').exists()).toBe(true)
  
  await wrapper.setProps({ show: false })
  expect(wrapper.find('.element').exists()).toBe(false)
})
```

### Testing Form Input

```typescript
it('should update input value', async () => {
  const input = wrapper.find('input')
  await input.setValue('test value')
  expect(input.element.value).toBe('test value')
})
```

### Testing API Calls

```typescript
it('should call API', async () => {
  vi.mocked(api.getData).mockResolvedValue({ data: 'test' })
  
  await store.fetchData()
  
  expect(api.getData).toHaveBeenCalledWith({ id: 1 })
})
```

## Debugging Tests

### Frontend Unit Tests

```bash
# Run with debugger
npm run test -- --inspect-brk

# Then open chrome://inspect in Chrome
```

### E2E Tests

```bash
# Debug mode (step through)
npx playwright test --debug

# Headed mode (see browser)
npm run test:e2e:headed

# Specific test in debug mode
npx playwright test tests/e2e/chat.spec.ts --debug
```

## Coverage

View coverage reports:

```bash
# Generate coverage
npm run test:coverage

# Open HTML report
# Windows: start coverage/index.html
# macOS: open coverage/index.html
# Linux: xdg-open coverage/index.html
```

## Troubleshooting

### Tests Not Running

1. Clear cache: `rm -rf node_modules/.vite`
2. Reinstall: `npm install`
3. Run again: `npm run test:run`

### Import Errors

1. Check path aliases in `vite.config.ts`
2. Verify imports use `@/` prefix
3. Check file extensions

### Async Tests Timing Out

1. Increase timeout in test
2. Use proper `await` statements
3. Check for unresolved promises

### Mocks Not Working

1. Verify mock path matches import path
2. Clear mocks between tests: `vi.clearAllMocks()`
3. Check mock is called before assertion

## Resources

- [Vitest Documentation](https://vitest.dev/)
- [Vue Test Utils](https://test-utils.vuejs.org/)
- [Playwright Documentation](https://playwright.dev/)
- [Testing Best Practices](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)

## Contributing

When adding new features:

1. Write tests first (TDD)
2. Ensure all tests pass
3. Maintain or improve coverage
4. Follow existing patterns
5. Update this README if needed

## Questions?

See the main [TESTING_GUIDE.md](../TESTING_GUIDE.md) for more detailed information.
