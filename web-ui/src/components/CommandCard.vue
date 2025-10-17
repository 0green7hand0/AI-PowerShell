<template>
  <div class="command-card">
    <!-- Header -->
    <div class="command-header">
      <div class="header-left">
        <el-icon class="command-icon"><Monitor /></el-icon>
        <span class="command-title">生成的命令</span>
      </div>
      <SecurityBadge :level="security.level" size="small" />
    </div>

    <!-- Command Code Block -->
    <div class="command-body">
      <CodeBlock
        :code="command"
        language="powershell"
        :copyable="false"
      />
    </div>

    <!-- Confidence Bar -->
    <div class="confidence-section">
      <div class="confidence-label">
        <span>置信度</span>
        <span class="confidence-value">{{ (confidence * 100).toFixed(0) }}%</span>
      </div>
      <el-progress
        :percentage="confidence * 100"
        :color="confidenceColor"
        :show-text="false"
        :stroke-width="6"
      />
    </div>

    <!-- Explanation -->
    <div v-if="explanation" class="explanation-section">
      <el-icon class="info-icon"><InfoFilled /></el-icon>
      <p class="explanation-text">{{ explanation }}</p>
    </div>

    <!-- Security Warnings -->
    <div v-if="security.warnings.length > 0" class="warnings-section">
      <div class="warning-header">
        <el-icon class="warning-icon"><Warning /></el-icon>
        <span>安全警告</span>
      </div>
      <ul class="warning-list">
        <li v-for="(warning, index) in security.warnings" :key="index">
          {{ warning }}
        </li>
      </ul>
    </div>

    <!-- Action Buttons -->
    <div class="action-buttons">
      <el-button
        size="small"
        @click="handleCopy"
      >
        <el-icon><DocumentCopy /></el-icon>
        复制
      </el-button>
      
      <el-button
        size="small"
        @click="handleEdit"
      >
        <el-icon><Edit /></el-icon>
        编辑
      </el-button>
      
      <el-button
        type="primary"
        size="small"
        @click="handleExecute"
        :loading="isExecuting"
      >
        <el-icon><CaretRight /></el-icon>
        执行
      </el-button>
    </div>

    <!-- Security Confirmation Dialog -->
    <SecurityConfirmDialog
      :show="showConfirmDialog"
      :command="command"
      :risk-level="security.level"
      :warnings="security.warnings"
      :requires-elevation="security.requiresElevation"
      :require-confirmation="security.level === 'high' || security.level === 'critical'"
      @confirm="confirmExecute"
      @cancel="showConfirmDialog = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { 
  Monitor, 
  DocumentCopy, 
  Edit, 
  CaretRight, 
  InfoFilled, 
  Warning 
} from '@element-plus/icons-vue'
import type { SecurityInfo } from '../api/command'
import SecurityBadge from './SecurityBadge.vue'
import CodeBlock from './CodeBlock.vue'
import SecurityConfirmDialog from './SecurityConfirmDialog.vue'

/**
 * CommandCard - Command display and action component
 * 
 * Displays generated PowerShell command with syntax highlighting,
 * confidence score, security badge, and action buttons.
 * 
 * Requirements: 2.8, 2.9, 2.10, 2.11, 2.12
 */

interface Props {
  command: string
  confidence: number
  explanation?: string
  security: SecurityInfo
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'execute', command: string): void
  (e: 'copy', command: string): void
  (e: 'edit', command: string): void
}>()

const showConfirmDialog = ref(false)
const isExecuting = ref(false)

/**
 * Get confidence bar color based on confidence level
 * Requirements: 2.9
 */
const confidenceColor = computed(() => {
  if (props.confidence >= 0.8) return '#10b981' // Green
  if (props.confidence >= 0.6) return '#f59e0b' // Amber
  return '#ef4444' // Red
})

/**
 * Handle copy button click
 * Requirements: 2.12
 */
const handleCopy = () => {
  emit('copy', props.command)
}

/**
 * Handle edit button click
 * Requirements: 2.12
 */
const handleEdit = () => {
  emit('edit', props.command)
}

/**
 * Handle execute button click
 * Requirements: 2.12, 2.13
 */
const handleExecute = () => {
  // Show confirmation dialog for high-risk commands
  if (props.security.requiresConfirmation || 
      props.security.level === 'high' || 
      props.security.level === 'critical') {
    showConfirmDialog.value = true
  } else {
    confirmExecute()
  }
}

/**
 * Confirm and execute command
 */
const confirmExecute = () => {
  showConfirmDialog.value = false
  isExecuting.value = true
  emit('execute', props.command)
  
  // Reset executing state after a delay
  setTimeout(() => {
    isExecuting.value = false
  }, 1000)
}
</script>

<style scoped>
.command-card {
  background-color: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  margin: var(--space-3) 0;
}

/* Header */
.command-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-3) var(--space-4);
  background-color: var(--color-bg-tertiary);
  border-bottom: 1px solid var(--color-border);
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.command-icon {
  color: var(--color-primary);
  font-size: 18px;
}

.command-title {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--color-text-primary);
}

/* Body */
.command-body {
  padding: var(--space-3);
}

/* Confidence Section */
.confidence-section {
  padding: var(--space-3) var(--space-4);
  border-top: 1px solid var(--color-border);
}

.confidence-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-2);
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
}

.confidence-value {
  font-weight: var(--font-semibold);
  color: var(--color-text-primary);
}

/* Explanation Section */
.explanation-section {
  display: flex;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  background-color: rgba(59, 130, 246, 0.05);
  border-top: 1px solid var(--color-border);
}

.info-icon {
  flex-shrink: 0;
  color: var(--color-info);
  margin-top: 2px;
}

.explanation-text {
  flex: 1;
  margin: 0;
  font-size: var(--text-sm);
  line-height: var(--leading-normal);
  color: var(--color-text-secondary);
}

/* Warnings Section */
.warnings-section {
  padding: var(--space-3) var(--space-4);
  background-color: rgba(245, 158, 11, 0.05);
  border-top: 1px solid var(--color-border);
}

.warning-header {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-2);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--color-warning);
}

.warning-icon {
  font-size: 16px;
}

.warning-list {
  margin: 0;
  padding-left: var(--space-5);
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
}

.warning-list li {
  margin-bottom: var(--space-1);
}

/* Action Buttons */
.action-buttons {
  display: flex;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  border-top: 1px solid var(--color-border);
  background-color: var(--color-bg-primary);
}

/* Responsive */
@media (max-width: 768px) {
  .command-header,
  .confidence-section,
  .explanation-section,
  .warnings-section,
  .action-buttons {
    padding: var(--space-2) var(--space-3);
  }

  .command-body {
    padding: var(--space-2);
  }

  .action-buttons {
    flex-wrap: wrap;
    gap: var(--space-2);
  }

  .action-buttons .el-button {
    flex: 1;
    min-width: 80px;
  }

  .command-title {
    font-size: var(--text-xs);
  }

  .confidence-label,
  .explanation-text,
  .warning-list {
    font-size: var(--text-xs);
  }
}

@media (max-width: 480px) {
  .command-header,
  .confidence-section,
  .explanation-section,
  .warnings-section,
  .action-buttons {
    padding: var(--space-2);
  }

  .action-buttons {
    flex-direction: column;
  }

  .action-buttons .el-button {
    width: 100%;
  }
}
</style>
