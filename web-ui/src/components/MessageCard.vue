<template>
  <div :class="['message-card', `message-${props.message.type}`]">
    <!-- User Message -->
    <div v-if="props.message.type === 'user'" class="user-message">
      <div class="message-content">
        <div class="message-text">
          {{ props.message.content }}
        </div>
        <div class="message-timestamp">
          {{ formatTime(props.message.timestamp) }}
        </div>
      </div>
      <div class="message-avatar user-avatar">
        <el-icon><User /></el-icon>
      </div>
    </div>
    
    <!-- Assistant Message -->
    <div v-else-if="props.message.type === 'assistant'" class="assistant-message">
      <div class="message-avatar assistant-avatar">
        <el-icon><Cpu /></el-icon>
      </div>
      <div class="message-content">
        <div v-if="props.message.content" class="message-text">
          <div class="message-text-content">
            {{ props.message.content }}
          </div>
          <el-button text size="small" class="copy-button" @click="handleCopyMessage">
            <el-icon><DocumentCopy /></el-icon>
          </el-button>
        </div>

        <!-- Command Card -->
        <CommandCard
          v-if="props.message.command"
          :key="props.message.command.command"
          :command="props.message.command.command"
          :confidence="props.message.command.confidence"
          :explanation="props.message.command.explanation"
          :security="props.message.command.security"
          @execute="handleExecute"
          @copy="handleCopy"
          @edit="handleEdit"
          @feedback="handleFeedback"
          @regenerate="handleRegenerate"
        />

        <!-- Execution Result -->
        <div v-if="props.message.result" class="result-card">
          <div class="result-header">
            <el-icon :class="props.message.result?.success ? 'success-icon' : 'error-icon'">
              {{ props.message.result?.success ? '✓' : '✗' }}
            </el-icon>
            <span class="result-title">
              {{ props.message.result?.success ? '执行成功' : '执行失败' }}
            </span>
            <el-tag v-if="props.message.result?.sandbox" type="info" size="small" class="sandbox-tag">
              <el-icon><Lock /></el-icon>
              沙箱执行
            </el-tag>
            <span class="result-time">{{ props.message.result?.executionTime.toFixed(3) }}s</span>
          </div>

          <CodeBlock
            v-if="props.message.result?.output"
            :code="props.message.result?.output"
            language="powershell"
            :copyable="true"
          />

          <div v-if="props.message.result?.error" class="error-output">
            <el-icon class="error-icon">
              <Warning />
            </el-icon>
            <pre>{{ props.message.result?.error }}</pre>
          </div>
        </div>

        <div class="message-timestamp">
          {{ formatTime(props.message.timestamp) }}
        </div>
      </div>
    </div>
    
    <!-- System Message -->
    <div v-else class="system-message">
      <div class="system-content">
        <el-icon><InfoFilled /></el-icon>
        <span>{{ props.message.content }}</span>
      </div>
      <div class="message-timestamp">
        {{ formatTime(props.message.timestamp) }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { User, Cpu, Warning, InfoFilled, DocumentCopy, Lock } from '@element-plus/icons-vue'
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

/**
 * Handle message content copy
 */
const handleCopyMessage = () => {
  if (props.message.content) {
    navigator.clipboard.writeText(props.message.content)
    ElMessage.success('已复制到剪贴板')
  }
}

/**
 * Handle user feedback
 */
const handleFeedback = (command: string, isCorrect: boolean) => {
  const feedbackText = isCorrect ? '感谢您的反馈！这个命令是正确的。' : '感谢您的反馈！我们会改进这个命令。'
  ElMessage.success(feedbackText)
  
  // Here you could also send the feedback to the backend for analysis
  console.log('Feedback received:', { command, isCorrect, messageId: props.message.id })
}

/**
 * Handle command regeneration
 */
const handleRegenerate = () => {
  chatStore.regenerateCommand(props.message.id)
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
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-2);
}

.message-text-content {
  flex: 1;
  word-wrap: break-word;
}

.copy-button {
  flex-shrink: 0;
  margin-top: 2px;
  opacity: 0.6;
  transition: opacity var(--duration-fast) var(--ease-in-out);
}

.copy-button:hover {
  opacity: 1;
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

.sandbox-tag {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-left: auto;
  margin-right: var(--space-2);
}

.sandbox-tag .el-icon {
  font-size: 12px;
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
