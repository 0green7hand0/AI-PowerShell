<!--
  HistoryList Component
  
  Displays history items grouped by date (Today, Yesterday, Earlier)
  with infinite scroll support.
  
  Requirements: 3.1, 3.2, 3.7
-->

<template>
  <div class="history-list">
    <!-- Loading State -->
    <div v-if="isLoading && items.length === 0" class="history-list__loading">
      <el-skeleton :rows="5" animated />
    </div>

    <!-- Empty State -->
    <div v-else-if="items.length === 0" class="history-list__empty">
      <el-empty description="暂无历史记录">
        <template #image>
          <el-icon :size="80" color="var(--el-text-color-secondary)">
            <FolderOpened />
          </el-icon>
        </template>
      </el-empty>
    </div>

    <!-- History Groups -->
    <div v-else class="history-list__groups">
      <div
        v-for="group in groupedItems"
        :key="group.label"
        class="history-list__group"
      >
        <!-- Group Header -->
        <div class="history-list__group-header">
          <h3 class="history-list__group-title">{{ group.label }}</h3>
          <span class="history-list__group-count">{{ group.items.length }} 条</span>
        </div>

        <!-- Group Items -->
        <div class="history-list__group-items">
          <HistoryCard
            v-for="item in group.items"
            :key="item.id"
            :item="item"
            @view="handleView"
            @re-execute="handleReExecute"
            @delete="handleDelete"
          />
        </div>
      </div>

      <!-- Load More -->
      <div v-if="hasMore" class="history-list__load-more">
        <el-button
          v-if="!isLoading"
          type="primary"
          plain
          :icon="ArrowDown"
          @click="handleLoadMore"
        >
          加载更多
        </el-button>
        <el-skeleton v-else :rows="3" animated />
      </div>

      <!-- End Message -->
      <div v-else-if="items.length > 0" class="history-list__end">
        <el-divider>
          <el-icon><Check /></el-icon>
          已加载全部记录
        </el-divider>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { FolderOpened, ArrowDown, Check } from '@element-plus/icons-vue'
import HistoryCard from './HistoryCard.vue'
import type { HistoryItem, GroupedHistory } from '../stores/history'

// ============================================================================
// Props & Emits
// ============================================================================

interface Props {
  items: HistoryItem[]
  groupedItems: GroupedHistory[]
  isLoading: boolean
  hasMore: boolean
}

interface Emits {
  (e: 'view', item: HistoryItem): void
  (e: 'reExecute', item: HistoryItem): void
  (e: 'delete', id: string): void
  (e: 'loadMore'): void
}

defineProps<Props>()
const emit = defineEmits<Emits>()

// ============================================================================
// Methods
// ============================================================================

const handleView = (item: HistoryItem) => {
  emit('view', item)
}

const handleReExecute = (item: HistoryItem) => {
  emit('reExecute', item)
}

const handleDelete = (id: string) => {
  emit('delete', id)
}

const handleLoadMore = () => {
  emit('loadMore')
}
</script>

<style scoped>
.history-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.history-list__loading {
  padding: 1rem;
}

.history-list__empty {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
  padding: 2rem;
}

.history-list__groups {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.history-list__group {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.history-list__group-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid var(--el-border-color);
}

.history-list__group-title {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.history-list__group-count {
  font-size: 0.875rem;
  color: var(--el-text-color-secondary);
  padding: 0.25rem 0.75rem;
  background-color: var(--el-fill-color-light);
  border-radius: 12px;
}

.history-list__group-items {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.history-list__load-more {
  display: flex;
  justify-content: center;
  padding: 1rem;
}

.history-list__end {
  padding: 1rem 0;
}

.history-list__end :deep(.el-divider__text) {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--el-text-color-secondary);
  font-size: 0.875rem;
}

/* Animations */
.history-list__group-items > * {
  animation: slideIn 0.3s ease-out;
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

/* Responsive */
@media (max-width: 768px) {
  .history-list__group-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
}
</style>
