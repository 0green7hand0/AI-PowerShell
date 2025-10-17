# ChatStore Quick Reference

## Import

```typescript
import { useChatStore } from '@/stores/chat'
```

## Initialize

```typescript
const chatStore = useChatStore()
```

## State

| Property | Type | Description |
|----------|------|-------------|
| `messages` | `Message[]` | Array of chat messages |
| `currentInput` | `string` | Current input text |
| `isLoading` | `boolean` | Translation loading state |
| `isExecuting` | `boolean` | Execution loading state |
| `sessionId` | `string` | Unique session identifier |

## Actions

### sendMessage(input: string)
Translate natural language to PowerShell command.

```typescript
await chatStore.sendMessage('显示CPU使用率最高的5个进程')
```

**What it does:**
1. Validates input
2. Adds user message
3. Calls translation API
4. Adds assistant response with command
5. Shows success/error notification

### executeCommand(command: string, messageId?: string)
Execute a PowerShell command.

```typescript
await chatStore.executeCommand('Get-Process | Select-Object -First 5')
```

**What it does:**
1. Validates command
2. Shows "executing" status
3. Calls execution API
4. Updates message with result
5. Shows success/error notification

### loadHistory(limit?: number)
Load chat history from backend.

```typescript
await chatStore.loadHistory(20) // Load last 20 items
```

**What it does:**
1. Fetches history from API
2. Converts to messages
3. Prepends to current messages
4. Shows success/error notification

### clearChat()
Clear all messages and start new session.

```typescript
chatStore.clearChat()
```

**What it does:**
1. Clears all messages
2. Generates new session ID
3. Resets current input
4. Shows confirmation

### addMessage(message)
Add a message manually (helper function).

```typescript
chatStore.addMessage({
  type: 'user',
  content: 'Hello'
})
```

## Message Interface

```typescript
interface Message {
  id: string                    // Auto-generated
  type: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date               // Auto-generated
  command?: {
    command: string
    confidence: number
    explanation: string
    security: {
      level: 'safe' | 'low' | 'medium' | 'high' | 'critical'
      warnings: string[]
      requiresConfirmation: boolean
    }
  }
  result?: {
    output: string
    error: string | null
    executionTime: number
    success: boolean
  }
}
```

## Common Patterns

### Basic Chat Component

```vue
<script setup lang="ts">
import { useChatStore } from '@/stores/chat'
import { ref, computed } from 'vue'

const chatStore = useChatStore()
const input = ref('')

const messages = computed(() => chatStore.messages)
const isLoading = computed(() => chatStore.isLoading)

const send = async () => {
  await chatStore.sendMessage(input.value)
  input.value = ''
}
</script>

<template>
  <div>
    <div v-for="msg in messages" :key="msg.id">
      {{ msg.content }}
    </div>
    <input v-model="input" @keyup.enter="send" />
    <button @click="send" :disabled="isLoading">Send</button>
  </div>
</template>
```

### Execute Command from Message

```typescript
const executeFromMessage = async (message: Message) => {
  if (message.command) {
    await chatStore.executeCommand(
      message.command.command,
      message.id
    )
  }
}
```

### Filter Messages

```typescript
// Get only user messages
const userMessages = chatStore.messages.filter(m => m.type === 'user')

// Get messages with commands
const commandMessages = chatStore.messages.filter(m => m.command)

// Get successful executions
const successfulExecutions = chatStore.messages.filter(
  m => m.result?.success === true
)
```

### Watch for Changes

```typescript
import { watch } from 'vue'

watch(
  () => chatStore.messages,
  (newMessages) => {
    console.log('Messages updated:', newMessages.length)
  },
  { deep: true }
)
```

## Error Handling

All actions handle errors internally and show user notifications. You can add additional error handling:

```typescript
try {
  await chatStore.sendMessage(input)
} catch (error) {
  // Additional error handling if needed
  console.error('Error:', error)
}
```

## Requirements Coverage

- ✅ **Req 2.5**: Translation API integration
- ✅ **Req 2.6**: Loading state management
- ✅ **Req 2.14**: Execution status messages

## Tips

1. **Always check loading states** before allowing user actions
2. **Use computed properties** for reactive state access
3. **Handle empty input** - the store validates but UI should too
4. **Session management** - session ID is auto-generated and persists
5. **History loading** - call on component mount for better UX
6. **Clear chat** - useful for starting fresh conversations

## Example: Complete Chat Flow

```typescript
// 1. Load history on mount
onMounted(async () => {
  await chatStore.loadHistory(20)
})

// 2. Send message
const handleSend = async (input: string) => {
  await chatStore.sendMessage(input)
  
  // 3. Get the last message with command
  const lastMsg = chatStore.messages[chatStore.messages.length - 1]
  
  // 4. Optionally auto-execute if safe
  if (lastMsg.command?.security.level === 'safe') {
    await chatStore.executeCommand(lastMsg.command.command, lastMsg.id)
  }
}

// 5. Clear when done
const handleClear = () => {
  chatStore.clearChat()
}
```

## Troubleshooting

**Messages not updating?**
- Make sure you're using computed properties or reactive refs
- Check that the store is properly initialized

**API calls failing?**
- Check backend is running
- Verify API base URL in `.env`
- Check browser console for errors

**Loading states stuck?**
- Errors are caught in finally blocks
- Check for network issues
- Verify API responses

## Related Files

- Implementation: `src/stores/chat.ts`
- Tests: `src/stores/__tests__/chat.spec.ts`
- Examples: `src/stores/examples/chat-store-usage.ts`
- Documentation: `src/stores/CHAT_STORE_IMPLEMENTATION.md`
