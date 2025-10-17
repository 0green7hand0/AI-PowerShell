<!--
  HistoryCard Component
  
  Displays a single history item with user input, command, status,
  timestamp, and action buttons.
  
  Requirements: 3.2, 3.3, 3.4
-->

<template>
  <div class="history-card" :class="{ 'history-card--failed': !item.success }">
    <!-- Status Icon -->
    <div class="history-card__status">
      <el-icon :size="20" :color="statusColor">
        <component :is="statusIcon" />
      </el-icon>
    </div>

    <!-- Content -->
    <div class="history-card__content">
      <!-- User Input -->
      <div class="history-card__input">
        <span class="history-card__label">输入:</span>
        <span class="history-card__text">{{ item.userInput }}</span>
      </div>

      <!-- Command -->
      <div class="history-card__command">
        <code>{{ item.command }}</code>
      </div>

      <!-- Metadata -->
      <div class="history-card__meta">
        <span class="history-card__time">
          <el-icon><Clock /></el-icon>
          {{ formatTimestamp(item.timestamp) }}
        </span>
        <span class="history-card__duration">
          <el-icon><Timer /></el-icon>
          {{ formatDuration(item.executionTime) }}
        </span>
        <span v-if="!item.success" class="history-card__error-badge">
          <el-icon><WarningFilled /></el-icon>
          执行失败
        </span>
      </div>
    </div>

    <!-- Actions -->
    <div class="history-card__actions">
      <el-tooltip content="查看详情" placement="top">
        <el-button
          size="small"
          :icon="View"
          circle
          @click="handleView"
        />
      </el-tooltip>

      <el-tooltip content="重新执行" placement="top">
        <el-button
          size="small"
          :icon="Refresh"
          circle
          @click="handleReExecute"
        />
      </el-tooltip>

      <el-tooltip content="删除" placement="top">
        <el-button
          size="small"
          :icon="Delete"
          circle
          type="danger"
          @click="handleDelete"
        />
      </el-tooltip>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { 
  SuccessFilled, 
  CircleCloseFilled, 
  Clock, 
  Timer, 
  WarningFilled,
  View,
  Refresh,
  Delete
} from '@element-plus/icons-vue'
import { ElMessageBox } from 'element-plus'
import type { HistoryItem } from '../stores/history'
import { formatTimestamp, formatDuration } from '../utils/format'

// ============================================================================
// Props & Emits
// ============================================================================

interface Props {
  item: HistoryItem
}

interface Emits {
  (e: 'view', item: HistoryItem): void
  (e: 'reExecute', item: HistoryItem): void
  (e: 'delete', id: string): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// ============================================================================
// Computed
// ============================================================================

const statusIcon = computed(() => {
  return props.item.success ? SuccessFilled : CircleCloseFilled
})

const statusColor = computed(() => {
  return props.item.success ? '#67c23a' : '#f56c6c'
})

// ============================================================================
// Methods
// ============================================================================

const handleView = () => {
  emit('view', props.item)
}

const handleReExecute = async () => {
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
  } catch {
    // User cancelled
  }
}

const handleDelete = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要删除此历史记录吗？此操作不可恢复。',
      '确认删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    emit('delete', props.item.id)
  } catch {
    // User cancelled
  }
}
</script>

<style scoped>
.history-card {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  background-color: var(--el-bg-color);
  border: 1px solid var(--el-border-color);
  border-radius: 8px;
  transition: all 0.3s ease;
}

.history-card:hover {
  border-color: var(--el-color-primary);
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.history-card--failed {
  border-left: 3px solid var(--el-color-danger);
}

.history-card__status {
  flex-shrink: 0;
  display: flex;
  align-items: flex-start;
  padding-top: 0.25rem;
}

.history-card__content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.history-card__input {
  display: flex;
  gap: 0.5rem;
  align-items: baseline;
}

.history-card__label {
  font-size: 0.875rem;
  color: var(--el-text-color-secondary);
  font-weight: 500;
  flex-shrink: 0;
}

.history-card__text {
  font-size: 0.875rem;
  color: var(--el-text-color-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.history-card__command {
  padding: 0.5rem;
  background-color: var(--el-fill-color-light);
  border-radius: 4px;
  overflow-x: auto;
}

.history-card__command code {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 0.875rem;
  color: var(--el-text-color-primary);
  white-space: pre-wrap;
  word-break: break-all;
}

.history-card__meta {
  display: flex;
  gap: 1rem;
  align-items: center;
  font-size: 0.75rem;
  color: var(--el-text-color-secondary);
}

.history-card__time,
.history-card__duration,
.history-card__error-badge {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.history-card__error-badge {
  color: var(--el-color-danger);
  font-weight: 500;
}

.history-card__actions {
  flex-shrink: 0;
  display: flex;
  gap: 0.5rem;
  align-items: flex-start;
}

/* Responsive */
@media (max-width: 768px) {
  .history-card {
    flex-direction: column;
  }

  .history-card__actions {
    justify-content: flex-end;
  }

  .history-card__meta {
    flex-wrap: wrap;
  }
}
</style>
