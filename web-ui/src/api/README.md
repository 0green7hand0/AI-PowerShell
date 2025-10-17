# API Service Layer

This directory contains the API service layer for the frontend application. It provides a clean interface for communicating with the backend API.

## Overview

The API service layer is built on top of Axios and provides:

- **Type-safe API methods** with TypeScript interfaces
- **Automatic error handling** with user-friendly messages
- **Request/response interceptors** for authentication and logging
- **Centralized configuration** for base URL and timeouts

## Architecture

```
api/
├── client.ts          # Axios instance with interceptors
├── command.ts         # Command translation and execution
├── history.ts         # History management
├── template.ts        # Template management
├── config.ts          # Configuration management
├── logs.ts            # Logs and monitoring
├── index.ts           # Barrel export
└── __tests__/         # Unit tests
```

## Usage

### Basic Usage

```typescript
import { commandApi } from '@/api'

// Translate natural language to PowerShell
const result = await commandApi.translate({
  input: '显示CPU使用率最高的5个进程'
})

console.log(result.data.command)
// Output: Get-Process | Sort-Object CPU -Descending | Select-Object -First 5
```

### With Context

```typescript
import { commandApi } from '@/api'

// Include session context for better translations
const result = await commandApi.translate({
  input: '再显示一次',
  context: {
    sessionId: 'session-123',
    history: [
      {
        input: '显示当前时间',
        command: 'Get-Date',
        timestamp: '2024-01-01T00:00:00Z'
      }
    ]
  }
})
```

### Execute Commands

```typescript
import { commandApi } from '@/api'

// Execute a PowerShell command
const result = await commandApi.execute({
  command: 'Get-Process | Select-Object -First 5',
  sessionId: 'session-123',
  timeout: 30 // Optional timeout in seconds
})

if (result.data.returnCode === 0) {
  console.log('Success:', result.data.output)
} else {
  console.error('Error:', result.data.error)
}
```

### Error Handling

Errors are automatically handled by the axios interceptor and displayed to users via Element Plus messages. You can also catch errors for custom handling:

```typescript
import { commandApi } from '@/api'

try {
  const result = await commandApi.translate({
    input: 'invalid input'
  })
} catch (error) {
  // Custom error handling
  console.error('Translation failed:', error)
}
```

## API Methods

### Command API

#### `commandApi.translate(data: TranslateRequest): Promise<TranslateResponse>`

Translates natural language to PowerShell commands.

**Request:**
```typescript
interface TranslateRequest {
  input: string
  context?: {
    sessionId: string
    history?: Array<{
      input: string
      command: string
      timestamp: string
    }>
  }
}
```

**Response:**
```typescript
interface TranslateResponse {
  success: boolean
  data: {
    command: string
    confidence: number
    explanation: string
    security: {
      level: 'safe' | 'low' | 'medium' | 'high' | 'critical'
      warnings: string[]
      requiresConfirmation: boolean
      requiresElevation?: boolean
    }
  }
}
```

#### `commandApi.execute(data: ExecuteRequest): Promise<ExecuteResponse>`

Executes a PowerShell command.

**Request:**
```typescript
interface ExecuteRequest {
  command: string
  sessionId: string
  timeout?: number
}
```

**Response:**
```typescript
interface ExecuteResponse {
  success: boolean
  data: {
    output: string | null
    error: string | null
    executionTime: number
    returnCode: number
  }
}
```

## Helper Functions

### `requiresConfirmation(security: SecurityInfo): boolean`

Checks if a command requires user confirmation based on security level.

```typescript
import { requiresConfirmation } from '@/api'

const security = {
  level: 'high',
  warnings: ['High risk operation'],
  requiresConfirmation: false
}

if (requiresConfirmation(security)) {
  // Show confirmation dialog
}
```

### `getSecurityLevelColor(level: SecurityLevel): string`

Returns the color class for a security level.

```typescript
import { getSecurityLevelColor } from '@/api'

const color = getSecurityLevelColor('high')
// Returns: 'danger'
```

### `getSecurityLevelText(level: SecurityLevel): string`

Returns the display text for a security level.

```typescript
import { getSecurityLevelText } from '@/api'

const text = getSecurityLevelText('high')
// Returns: '高风险'
```

## Configuration

### Environment Variables

Configure the API base URL using environment variables:

```env
# .env.development
VITE_API_BASE_URL=http://localhost:5000/api

# .env.production
VITE_API_BASE_URL=/api
```

### Timeout

The default timeout is 30 seconds. You can modify it in `client.ts`:

```typescript
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json'
  }
})
```

## Interceptors

### Request Interceptor

The request interceptor:
- Adds authentication tokens from localStorage
- Logs requests in development mode

```typescript
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  }
)
```

### Response Interceptor

The response interceptor:
- Unwraps response data (returns `response.data`)
- Handles errors and shows user-friendly messages
- Logs responses in development mode

```typescript
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    handleApiError(error)
    return Promise.reject(error)
  }
)
```

## Error Handling

Errors are handled automatically and displayed to users:

- **400 Bad Request**: "请求参数错误"
- **401 Unauthorized**: "未授权，请登录"
- **403 Forbidden**: "没有权限访问"
- **404 Not Found**: "请求的资源不存在"
- **500 Internal Server Error**: "服务器内部错误"
- **503 Service Unavailable**: "服务暂时不可用"
- **Network Error**: "网络错误，请检查网络连接"

## Testing

Run tests with:

```bash
npm run test
```

Test files are located in `__tests__/` directory:

- `command.spec.ts` - Tests for command API
- `client.spec.ts` - Tests for axios client

## Best Practices

1. **Always use the API methods** instead of calling axios directly
2. **Handle errors gracefully** in your components
3. **Use TypeScript types** for type safety
4. **Include context** when translating commands for better results
5. **Set appropriate timeouts** for long-running commands
6. **Check security levels** before executing commands

## Examples

### Complete Translation and Execution Flow

```typescript
import { commandApi, requiresConfirmation } from '@/api'
import { ElMessageBox } from 'element-plus'

async function translateAndExecute(input: string) {
  try {
    // Step 1: Translate
    const translation = await commandApi.translate({
      input,
      context: {
        sessionId: 'my-session'
      }
    })

    const { command, security } = translation.data

    // Step 2: Check if confirmation is needed
    if (requiresConfirmation(security)) {
      await ElMessageBox.confirm(
        `此命令存在风险：${security.warnings.join(', ')}`,
        '确认执行',
        {
          type: 'warning'
        }
      )
    }

    // Step 3: Execute
    const execution = await commandApi.execute({
      command,
      sessionId: 'my-session'
    })

    // Step 4: Handle result
    if (execution.data.returnCode === 0) {
      console.log('Success:', execution.data.output)
    } else {
      console.error('Error:', execution.data.error)
    }
  } catch (error) {
    console.error('Operation failed:', error)
  }
}
```

## Requirements

This API service layer implements the following requirements:

- **Requirement 1.2**: Command translation API integration
- **Requirement 1.3**: Command execution API integration
- **Requirement 6.9**: Error handling and user feedback

## Related Files

- `src/stores/chat.ts` - Uses command API in chat store
- `web-ui/backend/api/command.py` - Backend API implementation
- `web-ui/backend/models/command.py` - Backend data models
