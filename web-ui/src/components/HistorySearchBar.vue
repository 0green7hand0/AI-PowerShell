<!--
  HistorySearchBar Component
  
  Provides search input with debounce and clear functionality.
  
  Requirements: 3.6
-->

<template>
  <div class="history-search-bar">
    <!-- Search Input -->
    <el-input
      v-model="searchInput"
      placeholder="搜索历史记录..."
      :prefix-icon="Search"
      clearable
      size="large"
      @input="handleInput"
      @clear="handleClear"
    >
      <template #append>
        <el-button :icon="Search" @click="handleSearch">
          搜索
        </el-button>
      </template>
    </el-input>

    <!-- Active Search Indicator -->
    <div v-if="modelValue" class="history-search-bar__active">
      <el-tag
        closable
        type="info"
        @close="handleClear"
      >
        搜索: {{ modelValue }}
      </el-tag>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { Search } from '@element-plus/icons-vue'

// ============================================================================
// Props & Emits
// ============================================================================

interface Props {
  modelValue: string
  debounce?: number
}

interface Emits {
  (e: 'update:modelValue', value: string): void
  (e: 'search', query: string): void
}

const props = withDefaults(defineProps<Props>(), {
  debounce: 500
})

const emit = defineEmits<Emits>()

// ============================================================================
// State
// ============================================================================

const searchInput = ref(props.modelValue)
let debounceTimer: ReturnType<typeof setTimeout> | null = null

// ============================================================================
// Watchers
// ============================================================================

watch(() => props.modelValue, (newValue) => {
  searchInput.value = newValue
})

// ============================================================================
// Methods
// ============================================================================

/**
 * Debounced search handler
 */
const debouncedSearch = (query: string) => {
  if (debounceTimer) {
    clearTimeout(debounceTimer)
  }

  debounceTimer = setTimeout(() => {
    emit('update:modelValue', query)
    emit('search', query)
  }, props.debounce)
}

/**
 * Handle input change with debounce
 */
const handleInput = (value: string) => {
  debouncedSearch(value)
}

/**
 * Handle immediate search (button click)
 */
const handleSearch = () => {
  if (debounceTimer) {
    clearTimeout(debounceTimer)
  }
  emit('update:modelValue', searchInput.value)
  emit('search', searchInput.value)
}

/**
 * Handle clear search
 */
const handleClear = () => {
  if (debounceTimer) {
    clearTimeout(debounceTimer)
  }
  searchInput.value = ''
  emit('update:modelValue', '')
  emit('search', '')
}
</script>

<style scoped>
.history-search-bar {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.history-search-bar__active {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

/* Responsive */
@media (max-width: 768px) {
  .history-search-bar :deep(.el-input-group__append) {
    padding: 0 0.75rem;
  }
}
</style>
