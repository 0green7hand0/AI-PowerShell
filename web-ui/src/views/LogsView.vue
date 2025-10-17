<template>
  <div class="logs-view">
    <div class="logs-header">
      <h1 class="logs-title">系统日志</h1>
      <div class="logs-actions">
        <el-button
          :icon="Refresh"
          :loading="logsStore.isLoading"
          @click="handleRefresh"
        >
          刷新
        </el-button>
        <el-button
          :icon="logsStore.isConnected ? Link : Connection"
          :type="logsStore.isConnected ? 'success' : 'default'"
          :loading="isConnecting"
          @click="handleToggleWebSocket"
        >
          {{ logsStore.isConnected ? '实时连接' : '连接实时日志' }}
        </el-button>
        <el-button
          :icon="Delete"
          @click="handleClearLogs"
        >
          清空日志
        </el-button>
      </div>
    </div>

    <!-- System Status -->
    <div class="logs-status">
      <SystemStatus />
    </div>

    <!-- Log Filter -->
    <div class="logs-filter">
      <LogFilter />
    </div>

    <!-- Log List -->
    <div class="logs-content">
      <el-card v-if="logsStore.isLoading && logsStore.logs.length === 0" class="loading-card">
        <div class="loading-state">
          <LoadingSpinner />
          <p>加载日志中...</p>
        </div>
      </el-card>

      <LogList
        v-else
        :logs="logsStore.filteredLogs"
        :auto-scroll="logsStore.autoScroll"
      />
    </div>

    <!-- Connection Status Indicator -->
    <transition name="slide-up">
      <div v-if="showConnectionStatus" class="connection-status" :class="connectionStatusClass">
        <el-icon><component :is="connectionStatusIcon" /></el-icon>
        <span>{{ connectionStatusText }}</span>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useLogsStore } from '../stores/logs'
import { Refresh, Delete, Link, Connection } from '@element-plus/icons-vue'
import { SuccessFilled, WarningFilled } from '@element-plus/icons-vue'
import { ElMessageBox } from 'element-plus'
import SystemStatus from '../components/SystemStatus.vue'
import LogFilter from '../components/LogFilter.vue'
import LogList from '../components/LogList.vue'
import LoadingSpinner from '../components/LoadingSpinner.vue'

const logsStore = useLogsStore()
const isConnecting = ref(false)
const showConnectionStatus = ref(false)
const connectionStatusTimeout = ref<ReturnType<typeof setTimeout> | null>(null)

/**
 * Connection status computed properties
 */
const connectionStatusClass = computed(() => {
  return logsStore.isConnected ? 'status-connected' : 'status-disconnected'
})

const connectionStatusIcon = computed(() => {
  return logsStore.isConnected ? SuccessFilled : WarningFilled
})

const connectionStatusText = computed(() => {
  return logsStore.isConnected ? '实时日志已连接' : '实时日志已断开'
})

/**
 * Show connection status notification
 */
const showConnectionNotification = () => {
  showConnectionStatus.value = true
  
  if (connectionStatusTimeout.value) {
    clearTimeout(connectionStatusTimeout.value)
  }
  
  connectionStatusTimeout.value = setTimeout(() => {
    showConnectionStatus.value = false
  }, 3000)
}

/**
 * Handle refresh logs
 */
const handleRefresh = async () => {
  await logsStore.refreshLogs()
}

/**
 * Handle toggle WebSocket connection
 */
const handleToggleWebSocket = async () => {
  if (logsStore.isConnected) {
    logsStore.disconnectWebSocket()
    showConnectionNotification()
  } else {
    isConnecting.value = true
    try {
      await logsStore.connectWebSocket()
      showConnectionNotification()
    } finally {
      isConnecting.value = false
    }
  }
}

/**
 * Handle clear logs
 */
const handleClearLogs = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空所有日志吗？此操作不可恢复。',
      '确认清空',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    logsStore.clearLogs()
  } catch {
    // User cancelled
  }
}

/**
 * Initialize on mount
 */
onMounted(async () => {
  // Fetch initial logs
  await logsStore.fetchLogs({ limit: 100 })
  
  // Check system status
  await logsStore.checkSystemStatus()
  
  // Setup periodic status check (every 30 seconds)
  const statusCheckInterval = setInterval(() => {
    logsStore.checkSystemStatus()
  }, 30000)
  
  // Store interval ID for cleanup
  ;(window as any).__logsStatusCheckInterval = statusCheckInterval
})

/**
 * Cleanup on unmount
 */
onUnmounted(() => {
  // Disconnect WebSocket if connected
  if (logsStore.isConnected) {
    logsStore.disconnectWebSocket()
  }
  
  // Clear status check interval
  if ((window as any).__logsStatusCheckInterval) {
    clearInterval((window as any).__logsStatusCheckInterval)
    delete (window as any).__logsStatusCheckInterval
  }
  
  // Clear connection status timeout
  if (connectionStatusTimeout.value) {
    clearTimeout(connectionStatusTimeout.value)
  }
})
</script>

<style scoped>
.logs-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: var(--space-4);
  padding: var(--space-6);
  overflow: hidden;
}

.logs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--space-4);
}

.logs-title {
  font-size: var(--text-3xl);
  font-weight: var(--font-bold);
  color: var(--color-text-primary);
  margin: 0;
}

.logs-actions {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
}

.logs-status {
  flex-shrink: 0;
}

.logs-filter {
  flex-shrink: 0;
}

.logs-content {
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

.loading-card {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-4);
}

.loading-state p {
  font-size: var(--text-base);
  color: var(--color-text-secondary);
  margin: 0;
}

.connection-status {
  position: fixed;
  bottom: var(--space-6);
  right: var(--space-6);
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  z-index: 1000;
}

.status-connected {
  background-color: var(--color-success);
  color: white;
}

.status-disconnected {
  background-color: var(--color-warning);
  color: white;
}

/* Animations */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: all var(--duration-normal) var(--ease-in-out);
}

.slide-up-enter-from {
  transform: translateY(100%);
  opacity: 0;
}

.slide-up-leave-to {
  transform: translateY(100%);
  opacity: 0;
}

/* Responsive */
@media (max-width: 768px) {
  .logs-view {
    padding: var(--space-4);
  }

  .logs-header {
    flex-direction: column;
    align-items: stretch;
  }

  .logs-title {
    font-size: var(--text-2xl);
  }

  .logs-actions {
    width: 100%;
  }

  .logs-actions .el-button {
    flex: 1;
  }

  .connection-status {
    bottom: var(--space-4);
    right: var(--space-4);
    left: var(--space-4);
    justify-content: center;
  }
}
</style>
