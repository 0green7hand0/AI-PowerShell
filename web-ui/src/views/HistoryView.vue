<!--
  HistoryView Component
  
  Main view for displaying and managing command history.
  Includes search, filtering, and pagination functionality.
  
  Requirements: 3.1, 3.7
-->

<template>
  <div class="history-view">
    <!-- Header -->
    <div class="history-view__header">
      <div class="history-view__title-section">
        <h1 class="history-view__title">
          <el-icon><Clock /></el-icon>
          历史记录
        </h1>
        <p class="history-view__subtitle">
          查看和管理您的命令执行历史
        </p>
      </div>

      <div class="history-view__actions">
        <el-button
          :icon="Refresh"
          @click="handleRefresh"
          :loading="historyStore.isLoading"
        >
          刷新
        </el-button>
      </div>
    </div>

    <!-- Search Bar -->
    <div class="history-view__search">
      <HistorySearchBar
        v-model="historyStore.searchQuery"
        @search="handleSearch"
      />
    </div>

    <!-- Statistics -->
    <div v-if="historyStore.total > 0" class="history-view__stats">
      <el-card shadow="never">
        <div class="history-view__stats-content">
          <div class="history-view__stat">
            <el-icon :size="24" color="var(--el-color-primary)">
              <Document />
            </el-icon>
            <div class="history-view__stat-info">
              <span class="history-view__stat-value">{{ historyStore.total }}</span>
              <span class="history-view__stat-label">总记录数</span>
            </div>
          </div>

          <el-divider direction="vertical" />

          <div class="history-view__stat">
            <el-icon :size="24" color="var(--el-color-success)">
              <SuccessFilled />
            </el-icon>
            <div class="history-view__stat-info">
              <span class="history-view__stat-value">{{ successCount }}</span>
              <span class="history-view__stat-label">成功执行</span>
            </div>
          </div>

          <el-divider direction="vertical" />

          <div class="history-view__stat">
            <el-icon :size="24" color="var(--el-color-danger)">
              <CircleCloseFilled />
            </el-icon>
            <div class="history-view__stat-info">
              <span class="history-view__stat-value">{{ failedCount }}</span>
              <span class="history-view__stat-label">执行失败</span>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- History List -->
    <div class="history-view__content">
      <HistoryList
        :items="historyStore.items"
        :grouped-items="historyStore.groupedItems"
        :is-loading="historyStore.isLoading"
        :has-more="historyStore.hasMore"
        @view="handleView"
        @re-execute="handleReExecute"
        @delete="handleDelete"
        @load-more="handleLoadMore"
      />
    </div>

    <!-- Detail Dialog -->
    <HistoryDetailDialog
      v-model="showDetailDialog"
      :item="historyStore.selectedItem"
      @re-execute="handleReExecute"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  Clock,
  Refresh,
  Document,
  SuccessFilled,
  CircleCloseFilled
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useHistoryStore } from '../stores/history'
import type { HistoryItem } from '../stores/history'
import HistorySearchBar from '../components/HistorySearchBar.vue'
import HistoryList from '../components/HistoryList.vue'
import HistoryDetailDialog from '../components/HistoryDetailDialog.vue'

// ============================================================================
// Store
// ============================================================================

const historyStore = useHistoryStore()

// ============================================================================
// State
// ============================================================================

const showDetailDialog = ref(false)

// ============================================================================
// Computed
// ============================================================================

/**
 * Count of successful executions
 */
const successCount = computed(() => {
  return historyStore.items.filter(item => item.success).length
})

/**
 * Count of failed executions
 */
const failedCount = computed(() => {
  return historyStore.items.filter(item => !item.success).length
})

// ============================================================================
// Methods
// ============================================================================

/**
 * Handle search query change
 */
const handleSearch = async (query: string) => {
  await historyStore.searchHistory(query)
}

/**
 * Handle refresh button click
 */
const handleRefresh = async () => {
  await historyStore.refresh()
}

/**
 * Handle view history item details
 */
const handleView = (item: HistoryItem) => {
  historyStore.selectItem(item)
  showDetailDialog.value = true
}

/**
 * Handle re-execute command
 */
const handleReExecute = async (item: HistoryItem) => {
  await historyStore.reExecute(item)
}

/**
 * Handle delete history item
 */
const handleDelete = async (id: string) => {
  await historyStore.deleteHistory(id)
}

/**
 * Handle load more items
 */
const handleLoadMore = async () => {
  await historyStore.loadMore()
}

// ============================================================================
// Lifecycle
// ============================================================================

onMounted(async () => {
  // Load initial history
  await historyStore.fetchHistory()
})
</script>

<style scoped>
.history-view {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.history-view__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.history-view__title-section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.history-view__title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 0;
  font-size: 2rem;
  font-weight: 700;
  color: var(--el-text-color-primary);
}

.history-view__subtitle {
  margin: 0;
  font-size: 1rem;
  color: var(--el-text-color-secondary);
}

.history-view__actions {
  display: flex;
  gap: 0.75rem;
}

.history-view__search {
  width: 100%;
}

.history-view__stats {
  width: 100%;
}

.history-view__stats-content {
  display: flex;
  justify-content: space-around;
  align-items: center;
  gap: 1rem;
  padding: 0.5rem;
}

.history-view__stat {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex: 1;
  min-width: 0;
}

.history-view__stat-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.history-view__stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--el-text-color-primary);
  line-height: 1;
}

.history-view__stat-label {
  font-size: 0.875rem;
  color: var(--el-text-color-secondary);
}

.history-view__content {
  width: 100%;
}

/* Responsive */
@media (max-width: 1024px) {
  .history-view {
    padding: 1.5rem;
  }
}

@media (max-width: 768px) {
  .history-view {
    padding: 1rem;
    gap: 1rem;
  }

  .history-view__header {
    flex-direction: column;
  }

  .history-view__title {
    font-size: 1.5rem;
  }

  .history-view__subtitle {
    font-size: 0.875rem;
  }

  .history-view__actions {
    width: 100%;
  }

  .history-view__stats-content {
    flex-direction: column;
    align-items: stretch;
    gap: 0.5rem;
  }

  .history-view__stats-content :deep(.el-divider--vertical) {
    display: none;
  }

  .history-view__stat {
    padding: 0.75rem;
    background-color: var(--el-fill-color-light);
    border-radius: 8px;
  }

  .history-view__stat-value {
    font-size: 1.25rem;
  }
}

@media (max-width: 480px) {
  .history-view {
    padding: 0.75rem;
    gap: 0.75rem;
  }

  .history-view__title {
    font-size: 1.25rem;
    gap: 0.5rem;
  }

  .history-view__title :deep(.el-icon) {
    font-size: 1.25rem;
  }

  .history-view__subtitle {
    font-size: 0.75rem;
  }

  .history-view__stat-value {
    font-size: 1.125rem;
  }

  .history-view__stat-label {
    font-size: 0.75rem;
  }
}
</style>
