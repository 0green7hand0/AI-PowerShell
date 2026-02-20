<template>
  <div class="chat-view">
    <!-- Message List Container -->
    <div ref="messageListContainer" class="message-list-container">
      <MessageList
        :messages="chatStore.messages"
        :is-loading="chatStore.isLoading"
        @load-more="handleLoadMore"
      />
      <!-- Scroll to bottom button -->
      <button
        v-if="showScrollButton"
        class="scroll-to-bottom-btn"
        aria-label="Scroll to bottom"
        @click="scrollToBottom(true)"
      >
        ↓
      </button>
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
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
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
const showScrollButton = ref(false)
const scrollThreshold = 200 // Pixels from bottom to show button

/**
 * Scroll to bottom of message list
 * Requirements: 2.1
 */
const scrollToBottom = (smooth = true) => {
  nextTick(() => {
    if (messageListContainer.value) {
      // Use a more efficient scrolling method
      const container = messageListContainer.value
      const scrollHeight = container.scrollHeight
      const clientHeight = container.clientHeight

      // Calculate the target scroll position
      const targetPosition = scrollHeight - clientHeight

      // Use scrollTop directly for better performance
      if (smooth) {
        // Implement smooth scrolling manually for better control
        const startPosition = container.scrollTop
        const distance = targetPosition - startPosition
        const duration = 300 // milliseconds
        let startTime: number | null = null

        const animation = (timestamp: number) => {
          if (!startTime) startTime = timestamp
          const progress = Math.min((timestamp - startTime) / duration, 1)
          // Easing function for smoother scroll
          const easeOutQuad = 1 - (1 - progress) * (1 - progress)
          container.scrollTop = startPosition + distance * easeOutQuad

          if (progress < 1) {
            requestAnimationFrame(animation)
          } else {
            // Reset scroll button visibility after scroll
            showScrollButton.value = false
          }
        }

        requestAnimationFrame(animation)
      } else {
        container.scrollTop = targetPosition
        showScrollButton.value = false
      }
    }
  })
}

/**
 * Handle scroll event to show/hide scroll to bottom button
 */
const handleScroll = () => {
  if (messageListContainer.value) {
    const { scrollTop, scrollHeight, clientHeight } = messageListContainer.value
    const distanceFromBottom = scrollHeight - scrollTop - clientHeight
    showScrollButton.value = distanceFromBottom > scrollThreshold
  }
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

  // Add scroll event listener
  if (messageListContainer.value) {
    messageListContainer.value.addEventListener('scroll', handleScroll)
  }
})

// Cleanup event listener when component is unmounted
onUnmounted(() => {
  if (messageListContainer.value) {
    messageListContainer.value.removeEventListener('scroll', handleScroll)
  }
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
  position: relative;
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

/* Scroll to bottom button */
.scroll-to-bottom-btn {
  position: absolute;
  bottom: var(--space-4);
  right: var(--space-4);
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: var(--color-primary);
  color: white;
  border: none;
  font-size: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  transition: all 0.2s ease;
  z-index: 10;
}

.scroll-to-bottom-btn:hover {
  background-color: var(--color-primary-hover);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.scroll-to-bottom-btn:active {
  transform: translateY(0);
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

  .scroll-to-bottom-btn {
    width: 36px;
    height: 36px;
    font-size: 18px;
    bottom: var(--space-3);
    right: var(--space-3);
  }
}

@media (max-width: 480px) {
  .message-list-container {
    padding: var(--space-2);
  }

  .input-container {
    padding: var(--space-2);
  }

  .scroll-to-bottom-btn {
    width: 32px;
    height: 32px;
    font-size: 16px;
    bottom: var(--space-2);
    right: var(--space-2);
  }
}
</style>
