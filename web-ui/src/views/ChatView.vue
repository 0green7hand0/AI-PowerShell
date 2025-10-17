<template>
  <div class="chat-view">
    <!-- Message List Container -->
    <div ref="messageListContainer" class="message-list-container">
      <MessageList 
        :messages="chatStore.messages" 
        :is-loading="chatStore.isLoading"
        @load-more="handleLoadMore"
      />
    </div>

    <!-- Input Box Container -->
    <div class="input-container">
      <InputBox
        v-model="chatStore.currentInput"
        :loading="chatStore.isLoading"
        :disabled="chatStore.isExecuting"
        @submit="handleSendMessage"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue'
import { useChatStore } from '../stores/chat'
import MessageList from '../components/MessageList.vue'
import InputBox from '../components/InputBox.vue'

/**
 * ChatView - Main chat interface component
 * 
 * Provides a ChatGPT-like conversational interface for command translation
 * and execution.
 * 
 * Requirements: 2.1
 */

const chatStore = useChatStore()
const messageListContainer = ref<HTMLElement | null>(null)

/**
 * Scroll to bottom of message list
 * Requirements: 2.1
 */
const scrollToBottom = (smooth = true) => {
  nextTick(() => {
    if (messageListContainer.value) {
      messageListContainer.value.scrollTo({
        top: messageListContainer.value.scrollHeight,
        behavior: smooth ? 'smooth' : 'auto'
      })
    }
  })
}

/**
 * Handle sending a message
 */
const handleSendMessage = async (message: string) => {
  await chatStore.sendMessage(message)
  chatStore.currentInput = ''
  scrollToBottom()
}

/**
 * Handle loading more history messages
 */
const handleLoadMore = async () => {
  await chatStore.loadHistory(20)
}

/**
 * Watch for new messages and auto-scroll
 */
watch(
  () => chatStore.messages.length,
  () => {
    scrollToBottom()
  }
)

/**
 * Load initial history on mount
 */
onMounted(() => {
  // Optionally load recent history
  // chatStore.loadHistory(10)
  scrollToBottom(false)
})
</script>

<style scoped>
.chat-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: var(--color-bg-primary);
}

.message-list-container {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: var(--space-4);
  scroll-behavior: smooth;
}

/* Custom scrollbar */
.message-list-container::-webkit-scrollbar {
  width: 8px;
}

.message-list-container::-webkit-scrollbar-track {
  background: var(--color-bg-secondary);
  border-radius: var(--radius-full);
}

.message-list-container::-webkit-scrollbar-thumb {
  background: var(--color-border);
  border-radius: var(--radius-full);
}

.message-list-container::-webkit-scrollbar-thumb:hover {
  background: var(--color-border-hover);
}

.input-container {
  flex-shrink: 0;
  padding: var(--space-4);
  background-color: var(--color-bg-primary);
  border-top: 1px solid var(--color-border);
}

/* Responsive design */
@media (max-width: 768px) {
  .message-list-container {
    padding: var(--space-3);
  }

  .input-container {
    padding: var(--space-3);
  }

  .message-list-container::-webkit-scrollbar {
    width: 4px;
  }
}

@media (max-width: 480px) {
  .message-list-container {
    padding: var(--space-2);
  }

  .input-container {
    padding: var(--space-2);
  }
}
</style>
