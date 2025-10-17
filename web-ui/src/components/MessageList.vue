<template>
  <div class="message-list">
    <!-- Load More Button (for scrolling to load history) -->
    <div v-if="messages.length > 0" class="load-more-container">
      <el-button 
        text 
        size="small" 
        @click="$emit('load-more')"
        :loading="isLoading"
      >
        加载更多历史消息
      </el-button>
    </div>

    <!-- Empty State -->
    <div v-if="messages.length === 0 && !isLoading" class="empty-state">
      <div class="empty-icon">💬</div>
      <h3>开始对话</h3>
      <p>输入中文描述，AI 将帮您生成 PowerShell 命令</p>
    </div>

    <!-- Messages -->
    <TransitionGroup name="slide-in" tag="div" class="messages-container">
      <MessageCard
        v-for="message in messages"
        :key="message.id"
        :message="message"
        class="message-item"
      />
    </TransitionGroup>

    <!-- Loading Indicator -->
    <div v-if="isLoading" class="loading-message">
      <div class="loading-avatar">
        <LoadingSpinner size="small" />
      </div>
      <div class="loading-content">
        <div class="loading-text">AI 正在思考...</div>
        <div class="loading-dots">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Message } from '../stores/chat'
import MessageCard from './MessageCard.vue'
import LoadingSpinner from './LoadingSpinner.vue'

/**
 * MessageList - Displays chat messages with animations
 * 
 * Renders user messages and AI responses with different styles.
 * Supports auto-scrolling and loading more history.
 * 
 * Requirements: 2.1, 2.17
 */

interface Props {
  messages: Message[]
  isLoading?: boolean
}

defineProps<Props>()

defineEmits<{
  (e: 'load-more'): void
}>()
</script>

<style scoped>
.message-list {
  width: 100%;
  max-width: 900px;
  margin: 0 auto;
}

.load-more-container {
  text-align: center;
  padding: var(--space-4) 0;
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-16) var(--space-4);
  text-align: center;
  color: var(--color-text-secondary);
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: var(--space-4);
  opacity: 0.5;
}

.empty-state h3 {
  font-size: var(--text-xl);
  font-weight: var(--font-semibold);
  color: var(--color-text-primary);
  margin-bottom: var(--space-2);
}

.empty-state p {
  font-size: var(--text-base);
  color: var(--color-text-secondary);
}

/* Messages Container */
.messages-container {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.message-item {
  width: 100%;
}

/* Loading Message */
.loading-message {
  display: flex;
  gap: var(--space-3);
  padding: var(--space-4);
  margin-top: var(--space-4);
}

.loading-avatar {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--color-primary-light);
  border-radius: var(--radius-full);
}

.loading-content {
  flex: 1;
}

.loading-text {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  margin-bottom: var(--space-2);
}

.loading-dots {
  display: flex;
  gap: var(--space-1);
}

.loading-dots span {
  width: 8px;
  height: 8px;
  background-color: var(--color-primary);
  border-radius: var(--radius-full);
  animation: pulse 1.4s ease-in-out infinite;
}

.loading-dots span:nth-child(2) {
  animation-delay: 0.2s;
}

.loading-dots span:nth-child(3) {
  animation-delay: 0.4s;
}

/* Animations */
@keyframes pulse {
  0%, 100% {
    opacity: 0.3;
    transform: scale(0.8);
  }
  50% {
    opacity: 1;
    transform: scale(1);
  }
}

/* Slide-in animation for messages */
.slide-in-enter-active {
  animation: slideIn var(--duration-normal) var(--ease-out);
}

.slide-in-leave-active {
  animation: slideOut var(--duration-fast) var(--ease-in);
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideOut {
  from {
    opacity: 1;
    transform: translateY(0);
  }
  to {
    opacity: 0;
    transform: translateY(-10px);
  }
}

/* Responsive */
@media (max-width: 768px) {
  .message-list {
    max-width: 100%;
  }

  .empty-state {
    padding: var(--space-8) var(--space-4);
  }
}
</style>
