# API Service Layer - Quick Reference

## Import

```typescript
import { commandApi, requiresConfirmation, getSecurityLevelColor, getSecurityLevelText } from '@/api'
```

## Translate Command

```typescript
// Basic translation
const result = await commandApi.translate({
  input: '显示CPU使用率最高的5个进程'
})

// With context
const result = await commandApi.translate({
  input: '再显示一次',
  context: {
    sessionId: 'session-123',
    history: [...]
  }
})

// Access result
console.log(result.data.command)        // PowerShell command
console.log(result.data.confidence)     // 0.0 - 1.0
console.log(result.data.explanation)    // Explanation text
console.log(result.data.security.level) // 'safe' | 'low' | 'medium' | 'high' | 'critical'
```

## Execute Command

```typescript
const result = await commandApi.execute({
  command: 'Get-Process | Select-Object -First 5',
  sessionId: 'session-123',
  timeout: 30 // Optional, default 30 seconds
})

// Check result
if (result.data.returnCode === 0) {
  console.log('Success:', result.data.output)
} else {
  console.error('Error:', result.data.error)
}

console.log('Execution time:', result.data.executionTime, 'seconds')
```

## Security Helpers

```typescript
// Check if confirmation is needed
if (requiresConfirmation(security)) {
  await ElMessageBox.confirm('此命令存在风险', '确认执行')
}

// Get color class for badge
const color = getSecurityLevelColor('high') // Returns: 'danger'

// Get display text
const text = getSecurityLevelText('high') // Returns: '高风险'
```

## Error Handling

```typescript
try {
  const result = await commandApi.translate({ input: 'test' })
} catch (error) {
  // Error is already shown to user via ElMessage
  // Handle additional logic here
  console.error('Translation failed:', error)
}
```

## Complete Example

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

    // Step 2: Check security
    if (requiresConfirmation(security)) {
      await ElMessageBox.confirm(
        `此命令存在风险：${security.warnings.join(', ')}`,
        '确认执行',
        { type: 'warning' }
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

## Types

```typescript
// Request types
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

interface ExecuteRequest {
  command: string
  sessionId: string
  timeout?: number
}

// Response types
interface TranslateResponse {
  success: boolean
  data: {
    command: string
    confidence: number
    explanation: string
    security: SecurityInfo
  }
}

interface ExecuteResponse {
  success: boolean
  data: {
    output: string | null
    error: string | null
    executionTime: number
    returnCode: number
  }
}

// Security types
type SecurityLevel = 'safe' | 'low' | 'medium' | 'high' | 'critical'

interface SecurityInfo {
  level: SecurityLevel
  warnings: string[]
  requiresConfirmation: boolean
  requiresElevation?: boolean
}
```

## Configuration

```env
# .env.development
VITE_API_BASE_URL=http://localhost:5000/api

# .env.production
VITE_API_BASE_URL=/api
```

## Common Patterns

### In Pinia Store

```typescript
import { defineStore } from 'pinia'
import { commandApi } from '@/api'

export const useChatStore = defineStore('chat', () => {
  const sendMessage = async (input: string) => {
    const result = await commandApi.translate({ input })
    // Handle result...
  }

  return { sendMessage }
})
```

### In Vue Component

```typescript
<script setup lang="ts">
import { ref } from 'vue'
import { commandApi } from '@/api'

const input = ref('')
const result = ref(null)

const handleSubmit = async () => {
  result.value = await commandApi.translate({
    input: input.value
  })
}
</script>
```

### With Composable

```typescript
import { ref } from 'vue'
import { commandApi } from '@/api'

export function useCommand() {
  const loading = ref(false)
  const error = ref(null)

  const translate = async (input: string) => {
    loading.value = true
    error.value = null
    try {
      return await commandApi.translate({ input })
    } catch (e) {
      error.value = e
      throw e
    } finally {
      loading.value = false
    }
  }

  return { translate, loading, error }
}
```

## Tips

1. Always include `sessionId` for better context
2. Use `requiresConfirmation()` before executing high-risk commands
3. Handle errors gracefully - they're already shown to users
4. Set appropriate timeouts for long-running commands
5. Check `returnCode` to determine execution success
6. Use helper functions for consistent UI display

## See Also

- [Full Documentation](./README.md)
- [Backend API](../../backend/README.md)
- [Chat Store](../stores/chat.ts)
