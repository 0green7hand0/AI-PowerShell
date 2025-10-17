<template>
  <div class="log-filter">
    <div class="filter-row">
      <!-- Search Input -->
      <div class="filter-search">
        <el-input
          v-model="searchInput"
          placeholder="搜索日志..."
          :prefix-icon="Search"
          clearable
          @input="handleSearchInput"
          @clear="handleClearSearch"
        />
      </div>

      <!-- Level Filter -->
      <div class="filter-level">
        <el-select
          v-model="selectedLevel"
          placeholder="日志级别"
          @change="handleLevelChange"
        >
          <el-option label="全部" value="ALL">
            <span class="level-option">
              <span class="level-badge level-all">全部</span>
              <span class="level-count">{{ logsStore.logCounts.ALL }}</span>
            </span>
          </el-option>
          <el-option label="DEBUG" value="DEBUG">
            <span class="level-option">
              <span class="level-badge level-debug">DEBUG</span>
              <span class="level-count">{{ logsStore.logCounts.DEBUG }}</span>
            </span>
          </el-option>
          <el-option label="INFO" value="INFO">
            <span class="level-option">
              <span class="level-badge level-info">INFO</span>
              <span class="level-count">{{ logsStore.logCounts.INFO }}</span>
            </span>
          </el-option>
          <el-option label="WARNING" value="WARNING">
            <span class="level-option">
              <span class="level-badge level-warning">WARNING</span>
              <span class="level-count">{{ logsStore.logCounts.WARNING }}</span>
            </span>
          </el-option>
          <el-option label="ERROR" value="ERROR">
            <span class="level-option">
              <span class="level-badge level-error">ERROR</span>
              <span class="level-count">{{ logsStore.logCounts.ERROR }}</span>
            </span>
          </el-option>
          <el-option label="CRITICAL" value="CRITICAL">
            <span class="level-option">
              <span class="level-badge level-critical">CRITICAL</span>
              <span class="level-count">{{ logsStore.logCounts.CRITICAL }}</span>
            </span>
          </el-option>
        </el-select>
      </div>

      <!-- Clear Filters Button -->
      <el-button
        v-if="hasActiveFilters"
        :icon="Close"
        @click="handleClearFilters"
      >
        清除过滤
      </el-button>

      <!-- Auto Scroll Toggle -->
      <el-tooltip content="自动滚动到底部" placement="top">
        <el-button
          :icon="logsStore.autoScroll ? Bottom : Top"
          :type="logsStore.autoScroll ? 'primary' : 'default'"
          @click="handleToggleAutoScroll"
        />
      </el-tooltip>
    </div>

    <!-- Active Filters Display -->
    <div v-if="hasActiveFilters" class="active-filters">
      <span class="filter-label">当前过滤:</span>
      <el-tag
        v-if="selectedLevel !== 'ALL'"
        closable
        @close="handleLevelChange('ALL')"
      >
        级别: {{ selectedLevel }}
      </el-tag>
      <el-tag
        v-if="searchInput"
        closable
        @close="handleClearSearch"
      >
        搜索: {{ searchInput }}
      </el-tag>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useLogsStore } from '../stores/logs'
import { Search, Close, Bottom, Top } from '@element-plus/icons-vue'
import type { LogLevel } from '../api/logs'

const logsStore = useLogsStore()

// Local state for inputs
const searchInput = ref(logsStore.searchQuery)
const selectedLevel = ref<LogLevel | 'ALL'>(logsStore.filterLevel)

// Debounce timer for search
let searchDebounceTimer: ReturnType<typeof setTimeout> | null = null

/**
 * Check if there are active filters
 */
const hasActiveFilters = computed(() => {
  return selectedLevel.value !== 'ALL' || searchInput.value.trim() !== ''
})

/**
 * Handle search input with debounce
 */
const handleSearchInput = (value: string) => {
  if (searchDebounceTimer) {
    clearTimeout(searchDebounceTimer)
  }

  searchDebounceTimer = setTimeout(() => {
    logsStore.setSearchQuery(value)
  }, 300)
}

/**
 * Handle clear search
 */
const handleClearSearch = () => {
  searchInput.value = ''
  logsStore.setSearchQuery('')
}

/**
 * Handle level filter change
 */
const handleLevelChange = (level: LogLevel | 'ALL') => {
  selectedLevel.value = level
  logsStore.setFilterLevel(level)
}

/**
 * Handle clear all filters
 */
const handleClearFilters = () => {
  searchInput.value = ''
  selectedLevel.value = 'ALL'
  logsStore.clearFilters()
}

/**
 * Handle toggle auto scroll
 */
const handleToggleAutoScroll = () => {
  logsStore.toggleAutoScroll()
}
</script>

<style scoped>
.log-filter {
  background-color: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
}

.filter-row {
  display: flex;
  gap: var(--space-3);
  align-items: center;
  flex-wrap: wrap;
}

.filter-search {
  flex: 1;
  min-width: 200px;
}

.filter-level {
  min-width: 150px;
}

.level-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.level-badge {
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
}

.level-all {
  background-color: var(--color-bg-tertiary);
  color: var(--color-text-primary);
}

.level-debug {
  background-color: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.level-info {
  background-color: rgba(16, 185, 129, 0.1);
  color: var(--color-success);
}

.level-warning {
  background-color: rgba(245, 158, 11, 0.1);
  color: var(--color-warning);
}

.level-error {
  background-color: rgba(239, 68, 68, 0.1);
  color: var(--color-danger);
}

.level-critical {
  background-color: rgba(220, 38, 38, 0.1);
  color: #dc2626;
}

.level-count {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
  margin-left: var(--space-2);
}

.active-filters {
  display: flex;
  gap: var(--space-2);
  align-items: center;
  margin-top: var(--space-3);
  padding-top: var(--space-3);
  border-top: 1px solid var(--color-border);
}

.filter-label {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  font-weight: var(--font-medium);
}

/* Responsive */
@media (max-width: 768px) {
  .filter-row {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-search,
  .filter-level {
    width: 100%;
    min-width: auto;
  }
}
</style>
