/**
 * ChatStore Usage Examples
 * 
 * This file demonstrates how to use the ChatStore in Vue components
 */

import { useChatStore } from '../chat'

// Example 1: Basic Usage in a Component
export function exampleBasicUsage() {
  const chatStore = useChatStore()

  // Access state
  console.log('Messages:', chatStore.messages)
  console.log('Loading:', chatStore.isLoading)
  console.log('Session ID:', chatStore.sessionId)

  // Send a message
  const handleSendMessage = async (input: string) => {
    await chatStore.sendMessage(input)
  }

  // Execute a command
  const handleExecuteCommand = async (command: string) => {
    await chatStore.executeCommand(command)
  }

  return {
    messages: chatStore.messages,
    isLoading: chatStore.isLoading,
    handleSendMessage,
    handleExecuteCommand
  }
}

// Example 2: Complete Chat Flow
export async function exampleChatFlow() {
  const chatStore = useChatStore()

  // 1. Send a message to translate
  console.log('Step 1: Sending message...')
  await chatStore.sendMessage('显示CPU使用率最高的5个进程')

  // 2. Get the translated command from the last message
  const lastMessage = chatStore.messages[chatStore.messages.length - 1]
  if (lastMessage.command) {
    console.log('Step 2: Command translated:', lastMessage.command.command)

    // 3. Execute the command
    console.log('Step 3: Executing command...')
    await chatStore.executeCommand(lastMessage.command.command, lastMessage.id)

    // 4. Check the result
    const updatedMessage = chatStore.messages.find(m => m.id === lastMessage.id)
    if (updatedMessage?.result) {
      console.log('Step 4: Execution result:', updatedMessage.result)
    }
  }
}

// Example 3: Load History on Component Mount
export async function exampleLoadHistory() {
  const chatStore = useChatStore()

  // Load last 20 history items
  await chatStore.loadHistory(20)

  console.log('History loaded:', chatStore.messages.length, 'messages')
}

// Example 4: Clear Chat
export function exampleClearChat() {
  const chatStore = useChatStore()

  // Clear all messages and start fresh
  chatStore.clearChat()

  console.log('Chat cleared. New session ID:', chatStore.sessionId)
}

// Example 5: Vue Component Setup
export function exampleVueComponent() {
  return `
<script setup lang="ts">
import { useChatStore } from '@/stores/chat'
import { ref, computed } from 'vue'

const chatStore = useChatStore()
const inputText = ref('')

// Computed properties
const messages = computed(() => chatStore.messages)
const isLoading = computed(() => chatStore.isLoading)
const isExecuting = computed(() => chatStore.isExecuting)

// Methods
const handleSend = async () => {
  if (!inputText.value.trim()) return
  
  await chatStore.sendMessage(inputText.value)
  inputText.value = ''
}

const handleExecute = async (command: string, messageId?: string) => {
  await chatStore.executeCommand(command, messageId)
}

const handleClear = () => {
  chatStore.clearChat()
}

// Load history on mount
onMounted(async () => {
  await chatStore.loadHistory(20)
})
</script>

<template>
  <div class="chat-container">
    <!-- Message List -->
    <div class="messages">
      <div
        v-for="message in messages"
        :key="message.id"
        :class="['message', message.type]"
      >
        <div class="content">{{ message.content }}</div>
        
        <!-- Command Card -->
        <div v-if="message.command" class="command-card">
          <pre>{{ message.command.command }}</pre>
          <div class="confidence">
            Confidence: {{ (message.command.confidence * 100).toFixed(0) }}%
          </div>
          <button @click="handleExecute(message.command.command, message.id)">
            Execute
          </button>
        </div>

        <!-- Result Card -->
        <div v-if="message.result" class="result-card">
          <div :class="['status', message.result.success ? 'success' : 'error']">
            {{ message.result.success ? '✓ Success' : '✗ Failed' }}
          </div>
          <pre v-if="message.result.output">{{ message.result.output }}</pre>
          <pre v-if="message.result.error" class="error">{{ message.result.error }}</pre>
          <div class="time">
            Execution time: {{ message.result.executionTime.toFixed(3) }}s
          </div>
        </div>
      </div>
    </div>

    <!-- Input Box -->
    <div class="input-container">
      <textarea
        v-model="inputText"
        placeholder="输入中文描述..."
        :disabled="isLoading || isExecuting"
        @keydown.enter.exact.prevent="handleSend"
      />
      <button
        @click="handleSend"
        :disabled="isLoading || isExecuting || !inputText.trim()"
      >
        {{ isLoading ? '翻译中...' : '发送' }}
      </button>
      <button @click="handleClear">清空</button>
    </div>
  </div>
</template>
  `
}

// Example 6: Error Handling
export async function exampleErrorHandling() {
  const chatStore = useChatStore()

  try {
    // This will handle errors internally and show user feedback
    await chatStore.sendMessage('invalid input that might fail')
  } catch (error) {
    // Errors are already handled in the store
    // But you can add additional error handling here if needed
    console.error('Additional error handling:', error)
  }
}

// Example 7: Watching State Changes
export function exampleWatchState() {
  return `
<script setup lang="ts">
import { useChatStore } from '@/stores/chat'
import { watch } from 'vue'

const chatStore = useChatStore()

// Watch for new messages
watch(
  () => chatStore.messages,
  (newMessages, oldMessages) => {
    if (newMessages.length > oldMessages.length) {
      console.log('New message added!')
      // Scroll to bottom, play sound, etc.
    }
  },
  { deep: true }
)

// Watch loading state
watch(
  () => chatStore.isLoading,
  (isLoading) => {
    if (isLoading) {
      console.log('Loading started...')
    } else {
      console.log('Loading finished!')
    }
  }
)
</script>
  `
}

// Example 8: Advanced Usage with Message Filtering
export function exampleMessageFiltering() {
  const chatStore = useChatStore()

  // Get only user messages
  const userMessages = chatStore.messages.filter(m => m.type === 'user')

  // Get only messages with commands
  const commandMessages = chatStore.messages.filter(m => m.command !== undefined)

  // Get only successful executions
  const successfulExecutions = chatStore.messages.filter(
    m => m.result?.success === true
  )

  // Get messages from last hour
  const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000)
  const recentMessages = chatStore.messages.filter(
    m => m.timestamp > oneHourAgo
  )

  return {
    userMessages,
    commandMessages,
    successfulExecutions,
    recentMessages
  }
}

// Example 9: Batch Operations
export async function exampleBatchOperations() {
  const chatStore = useChatStore()

  const commands = [
    '显示当前时间',
    '列出所有进程',
    '显示系统信息'
  ]

  // Send multiple messages sequentially
  for (const command of commands) {
    await chatStore.sendMessage(command)
    // Wait a bit between messages
    await new Promise(resolve => setTimeout(resolve, 1000))
  }
}

// Example 10: Integration with Other Stores
export function exampleStoreIntegration() {
  return `
<script setup lang="ts">
import { useChatStore } from '@/stores/chat'
import { useHistoryStore } from '@/stores/history'
import { useAppStore } from '@/stores/app'

const chatStore = useChatStore()
const historyStore = useHistoryStore()
const appStore = useAppStore()

// Execute command and update history
const executeAndSaveToHistory = async (command: string) => {
  await chatStore.executeCommand(command)
  
  // Refresh history store
  await historyStore.fetchHistory()
}

// Use app theme in chat
const isDarkMode = computed(() => appStore.theme === 'dark')
</script>
  `
}
