<template>
  <div class="system-status">
    <div class="status-header">
      <h3 class="status-title">系统状态</h3>
      <el-button
        :icon="Refresh"
        :loading="isRefreshing"
        size="small"
        @click="handleRefresh"
      >
        刷新
      </el-button>
    </div>

    <div class="status-grid">
      <!-- AI Engine Status -->
      <div class="status-item">
        <div class="status-icon" :class="`status-${logsStore.systemStatus.ai}`">
          <el-icon><cpu-icon /></el-icon>
        </div>
        <div class="status-info">
          <div class="status-name">AI 引擎</div>
          <div class="status-value" :class="`text-${logsStore.systemStatus.ai}`">
            {{ getStatusText(logsStore.systemStatus.ai) }}
          </div>
        </div>
      </div>

      <!-- Security Engine Status -->
      <div class="status-item">
        <div class="status-icon" :class="`status-${logsStore.systemStatus.security}`">
          <el-icon><lock-icon /></el-icon>
        </div>
        <div class="status-info">
          <div class="status-name">安全引擎</div>
          <div class="status-value" :class="`text-${logsStore.systemStatus.security}`">
            {{ getStatusText(logsStore.systemStatus.security) }}
          </div>
        </div>
      </div>

      <!-- Execution Engine Status -->
      <div class="status-item">
        <div class="status-icon" :class="`status-${logsStore.systemStatus.execution}`">
          <el-icon><play-icon /></el-icon>
        </div>
        <div class="status-info">
          <div class="status-name">执行引擎</div>
          <div class="status-value" :class="`text-${logsStore.systemStatus.execution}`">
            {{ getStatusText(logsStore.systemStatus.execution) }}
          </div>
        </div>
      </div>
    </div>

    <div v-if="logsStore.systemStatus.lastCheck" class="status-footer">
      <span class="last-check">
        最后检查: {{ formatLastCheck(logsStore.systemStatus.lastCheck) }}
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, h } from 'vue'
import { useLogsStore } from '../stores/logs'
import { Refresh, Cpu, Lock, VideoPlay } from '@element-plus/icons-vue'

// Use Element Plus icons
const CpuIcon = Cpu
const LockIcon = Lock
const PlayIcon = VideoPlay

const logsStore = useLogsStore()
const isRefreshing = ref(false)

/**
 * Get display text for status
 */
const getStatusText = (status: 'online' | 'offline' | 'error'): string => {
  const textMap = {
    online: '在线',
    offline: '离线',
    error: '错误'
  }
  return textMap[status] || '未知'
}

/**
 * Format last check timestamp
 */
const formatLastCheck = (date: Date): string => {
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const seconds = Math.floor(diff / 1000)

  if (seconds < 60) {
    return `${seconds} 秒前`
  } else if (seconds < 3600) {
    return `${Math.floor(seconds / 60)} 分钟前`
  } else {
    return date.toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit'
    })
  }
}

/**
 * Handle refresh button click
 */
const handleRefresh = async () => {
  isRefreshing.value = true
  try {
    await logsStore.checkSystemStatus()
  } finally {
    isRefreshing.value = false
  }
}
</script>

<style scoped>
.system-status {
  background-color: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
}

.status-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
}

.status-title {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--color-text-primary);
  margin: 0;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: var(--space-4);
  margin-bottom: var(--space-4);
}

.status-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3);
  background-color: var(--color-bg-secondary);
  border-radius: var(--radius-md);
  transition: all var(--duration-fast) var(--ease-in-out);
}

.status-item:hover {
  background-color: var(--color-bg-tertiary);
}

.status-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);
  font-size: 20px;
  transition: all var(--duration-fast) var(--ease-in-out);
}

.status-icon.status-online {
  background-color: rgba(16, 185, 129, 0.1);
  color: var(--color-success);
}

.status-icon.status-offline {
  background-color: rgba(107, 114, 128, 0.1);
  color: var(--color-text-tertiary);
}

.status-icon.status-error {
  background-color: rgba(239, 68, 68, 0.1);
  color: var(--color-danger);
}

.status-info {
  flex: 1;
  min-width: 0;
}

.status-name {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  margin-bottom: 2px;
}

.status-value {
  font-size: var(--text-base);
  font-weight: var(--font-medium);
}

.text-online {
  color: var(--color-success);
}

.text-offline {
  color: var(--color-text-tertiary);
}

.text-error {
  color: var(--color-danger);
}

.status-footer {
  padding-top: var(--space-3);
  border-top: 1px solid var(--color-border);
  text-align: center;
}

.last-check {
  font-size: var(--text-sm);
  color: var(--color-text-tertiary);
}

/* Responsive */
@media (max-width: 768px) {
  .status-grid {
    grid-template-columns: 1fr;
  }
}
</style>
