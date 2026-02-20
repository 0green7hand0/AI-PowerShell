<template>
  <div class="logs-view">
    <div class="logs-header">
      <h1 class="logs-title">系统日志</h1>
      <div class="logs-actions">
        <el-button :icon="Refresh" :loading="logsStore.isLoading" @click="handleRefresh">
          刷新
        </el-button>
        <el-button :icon="Delete" @click="handleClearLogs"> 清空日志 </el-button>
        <el-button
          :icon="Filter"
          :type="showAnalytics ? 'primary' : 'default'"
          @click="handleToggleAnalytics"
        >
          {{ showAnalytics ? '隐藏分析' : '显示分析' }}
        </el-button>
      </div>
    </div>

    <!-- System Status -->
    <div class="logs-status">
      <SystemStatus />
    </div>

    <!-- Log Analytics -->
    <transition name="fade">
      <div v-if="showAnalytics" class="logs-analytics">
        <LogAnalytics :logs="logsStore.logs" />
      </div>
    </transition>

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

      <LogList v-else :logs="logsStore.filteredLogs" :auto-scroll="logsStore.autoScroll" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useLogsStore } from '../stores/logs'
import { Refresh, Delete, Filter } from '@element-plus/icons-vue'
import { ElMessageBox } from 'element-plus'
import SystemStatus from '../components/SystemStatus.vue'
import LogFilter from '../components/LogFilter.vue'
import LogList from '../components/LogList.vue'
import LogAnalytics from '../components/LogAnalytics.vue'
import LoadingSpinner from '../components/LoadingSpinner.vue'

const logsStore = useLogsStore()
const showAnalytics = ref(true)

/**
 * Handle refresh logs
 */
const handleRefresh = async () => {
  await logsStore.refreshLogs()
}

/**
 * Handle clear logs
 */
const handleClearLogs = async () => {
  try {
    await ElMessageBox.confirm('确定要清空所有日志吗？此操作不可恢复。', '确认清空', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    logsStore.clearLogs()
  } catch {
    // User cancelled
  }
}

/**
 * Handle toggle analytics view
 */
const handleToggleAnalytics = () => {
  showAnalytics.value = !showAnalytics.value
}

/**
 * Initialize on mount
 */
onMounted(async () => {
  // Fetch initial logs
  await logsStore.fetchLogs({ limit: 1000 })

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
  // Clear status check interval
  if ((window as any).__logsStatusCheckInterval) {
    clearInterval((window as any).__logsStatusCheckInterval)
    delete (window as any).__logsStatusCheckInterval
  }
})
</script>

<style scoped>
.logs-view {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  gap: var(--space-4);
  padding: var(--space-6);
  overflow: auto;
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

.logs-analytics {
  margin-bottom: var(--space-4);
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



.fade-enter-active,
.fade-leave-active {
  transition: opacity var(--duration-normal) var(--ease-in-out);
}

.fade-enter-from,
.fade-leave-to {
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
