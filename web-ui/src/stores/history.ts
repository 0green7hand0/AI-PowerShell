/**
 * History Store
 * 
 * Manages command history state and provides actions for
 * fetching, searching, deleting, and re-executing history items.
 * 
 * Requirements: 3.1, 3.4, 3.5, 3.6
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { historyApi, type HistoryItem as APIHistoryItem } from '../api/history'
import { commandApi } from '../api/command'
import { ElMessage } from 'element-plus'

// ============================================================================
// Type Definitions
// ============================================================================

/**
 * History item with parsed timestamp
 */
export interface HistoryItem {
  id: string
  userInput: string
  command: string
  success: boolean
  output?: string | null
  error?: string | null
  executionTime: number
  timestamp: Date
}

/**
 * Grouped history items by date
 */
export interface GroupedHistory {
  label: string
  items: HistoryItem[]
}

// ============================================================================
// Store Definition
// ============================================================================

export const useHistoryStore = defineStore('history', () => {
  // ============================================================================
  // State
  // ============================================================================

  const items = ref<HistoryItem[]>([])
  const total = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(20)
  const searchQuery = ref('')
  const isLoading = ref(false)
  const selectedItem = ref<HistoryItem | null>(null)

  // ============================================================================
  // Computed
  // ============================================================================

  /**
   * Group history items by date (Today, Yesterday, Earlier)
   */
  const groupedItems = computed<GroupedHistory[]>(() => {
    const now = new Date()
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    const yesterday = new Date(today)
    yesterday.setDate(yesterday.getDate() - 1)

    const groups: { [key: string]: HistoryItem[] } = {
      today: [],
      yesterday: [],
      earlier: []
    }

    items.value.forEach(item => {
      const itemDate = new Date(item.timestamp)
      const itemDay = new Date(itemDate.getFullYear(), itemDate.getMonth(), itemDate.getDate())

      if (itemDay.getTime() === today.getTime()) {
        groups.today.push(item)
      } else if (itemDay.getTime() === yesterday.getTime()) {
        groups.yesterday.push(item)
      } else {
        groups.earlier.push(item)
      }
    })

    const result: GroupedHistory[] = []
    if (groups.today.length > 0) {
      result.push({ label: '今天', items: groups.today })
    }
    if (groups.yesterday.length > 0) {
      result.push({ label: '昨天', items: groups.yesterday })
    }
    if (groups.earlier.length > 0) {
      result.push({ label: '更早', items: groups.earlier })
    }

    return result
  })

  /**
   * Check if there are more pages to load
   */
  const hasMore = computed(() => {
    return items.value.length < total.value
  })

  // ============================================================================
  // Actions
  // ============================================================================

  /**
   * Fetch history from the backend
   * 
   * @param page - Page number (default: current page)
   * @param append - Whether to append to existing items (for infinite scroll)
   * 
   * Requirements: 3.1, 3.7
   */
  const fetchHistory = async (page?: number, append: boolean = false): Promise<void> => {
    isLoading.value = true

    try {
      const pageToFetch = page || currentPage.value

      const response = await historyApi.getHistory({
        page: pageToFetch,
        limit: pageSize.value,
        search: searchQuery.value || undefined
      })

      if (response.success) {
        // Convert API items to store items (parse timestamp)
        const newItems: HistoryItem[] = response.data.items.map(item => ({
          ...item,
          timestamp: new Date(item.timestamp)
        }))

        if (append) {
          items.value = [...items.value, ...newItems]
        } else {
          items.value = newItems
        }

        total.value = response.data.total
        currentPage.value = response.data.page

        if (!append) {
          ElMessage.success(`已加载 ${newItems.length} 条历史记录`)
        }
      }
    } catch (error: any) {
      console.error('Failed to fetch history:', error)
      ElMessage.error('加载历史记录失败')
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Search history with a query string
   * 
   * @param query - Search query
   * 
   * Requirements: 3.6
   */
  const searchHistory = async (query: string): Promise<void> => {
    searchQuery.value = query
    currentPage.value = 1
    await fetchHistory(1, false)
  }

  /**
   * Delete a history item
   * 
   * @param id - History item ID
   * 
   * Requirements: 3.4, 3.5
   */
  const deleteHistory = async (id: string): Promise<void> => {
    try {
      const response = await historyApi.deleteHistory(id)

      if (response.success) {
        // Remove item from local state
        items.value = items.value.filter(item => item.id !== id)
        total.value -= 1

        ElMessage.success('历史记录已删除')

        // If selected item was deleted, clear selection
        if (selectedItem.value?.id === id) {
          selectedItem.value = null
        }
      }
    } catch (error: any) {
      console.error('Failed to delete history:', error)
      ElMessage.error('删除历史记录失败')
    }
  }

  /**
   * Re-execute a command from history
   * 
   * @param item - History item to re-execute
   * 
   * Requirements: 3.5
   */
  const reExecute = async (item: HistoryItem): Promise<void> => {
    try {
      ElMessage.info('正在重新执行命令...')

      const response = await commandApi.execute({
        command: item.command,
        sessionId: crypto.randomUUID(),
        timeout: 30
      })

      if (response.success) {
        const success = response.data.returnCode === 0 && !response.data.error

        if (success) {
          ElMessage.success('命令执行成功')
        } else {
          ElMessage.warning('命令执行完成，但有错误')
        }

        // Refresh history to show the new execution
        await fetchHistory(1, false)
      }
    } catch (error: any) {
      console.error('Failed to re-execute command:', error)
      ElMessage.error('命令执行失败')
    }
  }

  /**
   * Load more history items (for infinite scroll)
   * 
   * Requirements: 3.7
   */
  const loadMore = async (): Promise<void> => {
    if (!hasMore.value || isLoading.value) {
      return
    }

    const nextPage = currentPage.value + 1
    await fetchHistory(nextPage, true)
  }

  /**
   * Select a history item for viewing details
   * 
   * @param item - History item to select
   */
  const selectItem = (item: HistoryItem | null): void => {
    selectedItem.value = item
  }

  /**
   * Clear all filters and reset to initial state
   */
  const clearFilters = (): void => {
    searchQuery.value = ''
    currentPage.value = 1
    fetchHistory(1, false)
  }

  /**
   * Refresh history (reload current page)
   */
  const refresh = async (): Promise<void> => {
    await fetchHistory(currentPage.value, false)
  }

  // ============================================================================
  // Return
  // ============================================================================

  return {
    // State
    items,
    total,
    currentPage,
    pageSize,
    searchQuery,
    isLoading,
    selectedItem,

    // Computed
    groupedItems,
    hasMore,

    // Actions
    fetchHistory,
    searchHistory,
    deleteHistory,
    reExecute,
    loadMore,
    selectItem,
    clearFilters,
    refresh
  }
})
