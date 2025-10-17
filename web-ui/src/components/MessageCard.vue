<template>
  <div :class="['message-card', `message-${message.type}`]">
    <!-- User Message -->
    <div v-if="message.type === 'user'" class="user-message">
      <div class="message-content">
        <div class="message-text">{{ message.content }}</div>
        <div class="message-timestamp">{{ formatTime(message.timestamp) }}</div>
      </div>
      <div class="message-avatar user-avatar">
        <el-icon><User /></el-icon>
      </div>
    </div>

    <!-- Assistant Message -->
    <div v-else-if="message.type === 'assistant'" class="assistant-message">
      <div class="message-avatar assistant-avatar">
        <el-icon><Cpu /></el-icon>
      </div>
      <div class="message-content">
        <div v-if="message.content" class="message-text">{{ message.content }}</div>
        
        <!-- Command Card -->
        <CommandCard
          v-if="message.command"
          :command="message.command.command"
          :confidence="message.command.confidence"
          :explanation="message.command.explanation"
          :security="message.command.security"
          @execute="handleExecute"
          @copy="handleCopy"
          @edit="handleEdit"
        />

        <!-- Execution Result -->
        <div v-if="message.result" class="result-card">
          <div class="result-header">
            <el-icon :class="message.result.success ? 'success-icon' : 'error-icon'">
              <component :is="message.result.success ? 'CircleCheck' : 'CircleClose'" />
            </el-icon>
            <span class="result-title">
              {{ message.result.success ? '执行成功' : '执行失败' }}
            </span>
            <span class="result-time">{{ message.result.executionTime.toFixed(3) }}s</span>
          </div>
          
          <CodeBlock
            v-if="message.result.output"
            :code="message.result.output"
            language="powershell"
            :copyable="true"
          />
          
          <div v-if="message.result.error" class="error-output">
            <el-icon class="error-icon"><Warning /></el-icon>
            <pre>{{ message.result.error }}</pre>
          </div>
        </div>

        <div class="message-timestamp">{{ formatTime(message.timestamp) }}</div>
      </div>
    </div>

    <!-- System Message -->
    <div v-else class="system-message">
      <div class="system-content">
        <el-icon><InfoFilled /></el-icon>
        <span>{{ message.content }}</span>
      </div>
      <div class="message-timestamp">{{ formatTime(message.timestamp) }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { User, Cpu, CircleCheck, CircleClose, Warning, InfoFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { Message } from '../stores/chat'
import { useChatStore } from '../stores/chat'
import CommandCard from './CommandCard.vue'
import CodeBlock from './CodeBlock.vue'

/**
 * MessageCard - Individual message display component
 * 
 * Renders different styles for user messages, AI responses, and system messages.
 * Includes timestamp display.
 * 
 * Requirements: 2.1
 */

interface Props {
  message: Message
}

const props = defineProps<Props>()
const chatStore = useChatStore()

/**
 * Format timestamp to readable time
 */
const formatTime = (date: Date): string => {
  const now = new Date()
  const diff = now.getTime() - new Date(date).getTime()
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)

  if (days > 0) {
    return `${days}天前`
  } else if (hours > 0) {
    return `${hours}小时前`
  } else if (minutes > 0) {
    return `${minutes}分钟前`
  } else if (seconds > 10) {
    return `${seconds}秒前`
  } else {
    return '刚刚'
  }
}

/**
 * Handle command execution
 */
const handleExecute = (command: string) => {
  chatStore.executeCommand(command, props.message.id)
}

/**
 * Handle command copy
 */
const handleCopy = (command: string) => {
  navigator.clipboard.writeText(command)
  ElMessage.success('已复制到剪贴板')
}

/**
 * Handle command edit
 */
const handleEdit = (command: string) => {
  chatStore.currentInput = command
  ElMessage.info('命令已填充到输入框')
}
</script>

<style scoped>
.message-card {
  width: 100%;
  margin-bottom: var(--space-2);
}

/* User Message */
.user-message {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
}

.user-message .message-content {
  max-width: 70%;
  background-color: var(--color-primary);
  color: white;
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-lg);
  border-bottom-right-radius: var(--radius-sm);
}

.user-message .message-text {
  font-size: var(--text-base);
  line-height: var(--leading-normal);
  word-wrap: break-word;
}

.user-avatar {
  background-color: var(--color-primary);
  color: white;
}

/* Assistant Message */
.assistant-message {
  display: flex;
  gap: var(--space-3);
  align-items: flex-start;
}

.assistant-message .message-content {
  flex: 1;
  max-width: 80%;
}

.assistant-message .message-text {
  font-size: var(--text-base);
  line-height: var(--leading-normal);
  color: var(--color-text-primary);
  margin-bottom: var(--space-3);
  padding: var(--space-3) var(--space-4);
  background-color: var(--color-bg-secondary);
  border-radius: var(--radius-lg);
  border-bottom-left-radius: var(--radius-sm);
}

.assistant-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

/* Message Avatar */
.message-avatar {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

/* System Message */
.system-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) 0;
}

.system-content {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  background-color: var(--color-bg-tertiary);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
}

/* Timestamp */
.message-timestamp {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
  margin-top: var(--space-2);
  opacity: 0.7;
}

.user-message .message-timestamp {
  text-align: right;
  color: rgba(255, 255, 255, 0.8);
}

/* Result Card */
.result-card {
  margin-top: var(--space-3);
  padding: var(--space-4);
  background-color: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
}

.result-header {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-3);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
}

.success-icon {
  color: var(--color-success);
}

.error-icon {
  color: var(--color-danger);
}

.result-title {
  flex: 1;
  color: var(--color-text-primary);
}

.result-time {
  color: var(--color-text-secondary);
  font-size: var(--text-xs);
}

.error-output {
  display: flex;
  gap: var(--space-2);
  padding: var(--space-3);
  background-color: rgba(239, 68, 68, 0.1);
  border-left: 3px solid var(--color-danger);
  border-radius: var(--radius-md);
  margin-top: var(--space-3);
}

.error-output pre {
  flex: 1;
  margin: 0;
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  color: var(--color-danger);
  white-space: pre-wrap;
  word-wrap: break-word;
}

/* Responsive */
@media (max-width: 768px) {
  .user-message .message-content,
  .assistant-message .message-content {
    max-width: 90%;
  }

  .message-avatar {
    width: 32px;
    height: 32px;
    font-size: 16px;
  }

  .user-message .message-content,
  .assistant-message .message-text {
    padding: var(--space-2) var(--space-3);
  }

  .result-card {
    padding: var(--space-3);
  }
}

@media (max-width: 480px) {
  .user-message .message-content,
  .assistant-message .message-content {
    max-width: 95%;
    font-size: var(--text-sm);
  }

  .message-avatar {
    width: 28px;
    height: 28px;
    font-size: 14px;
  }

  .user-message,
  .assistant-message {
    gap: var(--space-2);
  }

  .result-card {
    padding: var(--space-2);
  }

  .result-header {
    font-size: var(--text-xs);
  }
}
</style>
