<!--
  HistoryDetailDialog Component
  
  Displays detailed information for a history item including
  full command, output, security info, and action buttons.
  
  Requirements: 3.3
-->

<template>
  <el-dialog
    v-model="visible"
    title="历史记录详情"
    width="800px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <div v-if="item" class="history-detail">
      <!-- Status Banner -->
      <div class="history-detail__banner" :class="bannerClass">
        <el-icon :size="24">
          <component :is="statusIcon" />
        </el-icon>
        <span class="history-detail__banner-text">
          {{ item.success ? '执行成功' : '执行失败' }}
        </span>
      </div>

      <!-- User Input Section -->
      <div class="history-detail__section">
        <h3 class="history-detail__section-title">
          <el-icon><ChatDotRound /></el-icon>
          用户输入
        </h3>
        <div class="history-detail__content">
          {{ item.userInput }}
        </div>
      </div>

      <!-- Command Section -->
      <div class="history-detail__section">
        <h3 class="history-detail__section-title">
          <el-icon><Document /></el-icon>
          PowerShell 命令
        </h3>
        <div class="history-detail__code-block">
          <div class="history-detail__code-header">
            <span>PowerShell</span>
            <el-button
              size="small"
              :icon="CopyDocument"
              @click="copyCommand"
            >
              复制
            </el-button>
          </div>
          <pre><code>{{ item.command }}</code></pre>
        </div>
      </div>

      <!-- Output Section -->
      <div v-if="item.output" class="history-detail__section">
        <h3 class="history-detail__section-title">
          <el-icon><Monitor /></el-icon>
          输出结果
        </h3>
        <div class="history-detail__code-block">
          <div class="history-detail__code-header">
            <span>Output</span>
            <el-button
              size="small"
              :icon="CopyDocument"
              @click="copyOutput"
            >
              复制
            </el-button>
          </div>
          <pre><code>{{ item.output }}</code></pre>
        </div>
      </div>

      <!-- Error Section -->
      <div v-if="item.error" class="history-detail__section">
        <h3 class="history-detail__section-title history-detail__section-title--error">
          <el-icon><WarningFilled /></el-icon>
          错误信息
        </h3>
        <div class="history-detail__code-block history-detail__code-block--error">
          <pre><code>{{ item.error }}</code></pre>
        </div>
      </div>

      <!-- Metadata Section -->
      <div class="history-detail__section">
        <h3 class="history-detail__section-title">
          <el-icon><InfoFilled /></el-icon>
          执行信息
        </h3>
        <div class="history-detail__metadata">
          <div class="history-detail__metadata-item">
            <span class="history-detail__metadata-label">执行时间:</span>
            <span class="history-detail__metadata-value">
              {{ formatTimestamp(item.timestamp) }}
            </span>
          </div>
          <div class="history-detail__metadata-item">
            <span class="history-detail__metadata-label">耗时:</span>
            <span class="history-detail__metadata-value">
              {{ formatDuration(item.executionTime) }}
            </span>
          </div>
          <div class="history-detail__metadata-item">
            <span class="history-detail__metadata-label">状态:</span>
            <el-tag :type="item.success ? 'success' : 'danger'">
              {{ item.success ? '成功' : '失败' }}
            </el-tag>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer Actions -->
    <template #footer>
      <div class="history-detail__footer">
        <el-button @click="handleClose">关闭</el-button>
        <el-button
          type="primary"
          :icon="Refresh"
          @click="handleReExecute"
        >
          重新执行
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  SuccessFilled,
  CircleCloseFilled,
  ChatDotRound,
  Document,
  Monitor,
  WarningFilled,
  InfoFilled,
  CopyDocument,
  Refresh
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { HistoryItem } from '../stores/history'
import { formatTimestamp, formatDuration } from '../utils/format'
import { copyToClipboard } from '../utils/clipboard'

// ============================================================================
// Props & Emits
// ============================================================================

interface Props {
  modelValue: boolean
  item: HistoryItem | null
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'reExecute', item: HistoryItem): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// ============================================================================
// Computed
// ============================================================================

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const statusIcon = computed(() => {
  return props.item?.success ? SuccessFilled : CircleCloseFilled
})

const bannerClass = computed(() => {
  return props.item?.success
    ? 'history-detail__banner--success'
    : 'history-detail__banner--error'
})

// ============================================================================
// Methods
// ============================================================================

const handleClose = () => {
  visible.value = false
}

const copyCommand = async () => {
  if (props.item?.command) {
    const success = await copyToClipboard(props.item.command)
    if (success) {
      ElMessage.success('命令已复制到剪贴板')
    }
  }
}

const copyOutput = async () => {
  if (props.item?.output) {
    const success = await copyToClipboard(props.item.output)
    if (success) {
      ElMessage.success('输出已复制到剪贴板')
    }
  }
}

const handleReExecute = async () => {
  if (!props.item) return

  try {
    await ElMessageBox.confirm(
      '确定要重新执行此命令吗？',
      '确认',
      {
        confirmButtonText: '执行',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    emit('reExecute', props.item)
    handleClose()
  } catch {
    // User cancelled
  }
}
</script>

<style scoped>
.history-detail {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.history-detail__banner {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  border-radius: 8px;
  font-weight: 500;
}

.history-detail__banner--success {
  background-color: var(--el-color-success-light-9);
  color: var(--el-color-success);
}

.history-detail__banner--error {
  background-color: var(--el-color-danger-light-9);
  color: var(--el-color-danger);
}

.history-detail__banner-text {
  font-size: 1.125rem;
}

.history-detail__section {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.history-detail__section-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.history-detail__section-title--error {
  color: var(--el-color-danger);
}

.history-detail__content {
  padding: 1rem;
  background-color: var(--el-fill-color-light);
  border-radius: 6px;
  font-size: 0.875rem;
  line-height: 1.6;
  color: var(--el-text-color-primary);
}

.history-detail__code-block {
  border: 1px solid var(--el-border-color);
  border-radius: 6px;
  overflow: hidden;
}

.history-detail__code-block--error {
  border-color: var(--el-color-danger-light-5);
  background-color: var(--el-color-danger-light-9);
}

.history-detail__code-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 1rem;
  background-color: var(--el-fill-color);
  border-bottom: 1px solid var(--el-border-color);
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--el-text-color-secondary);
}

.history-detail__code-block pre {
  margin: 0;
  padding: 1rem;
  background-color: var(--el-fill-color-light);
  overflow-x: auto;
}

.history-detail__code-block code {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 0.875rem;
  line-height: 1.6;
  color: var(--el-text-color-primary);
  white-space: pre-wrap;
  word-break: break-all;
}

.history-detail__metadata {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 1rem;
  background-color: var(--el-fill-color-light);
  border-radius: 6px;
}

.history-detail__metadata-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.history-detail__metadata-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--el-text-color-secondary);
  min-width: 80px;
}

.history-detail__metadata-value {
  font-size: 0.875rem;
  color: var(--el-text-color-primary);
}

.history-detail__footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

/* Responsive */
@media (max-width: 768px) {
  .history-detail__code-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
}
</style>
