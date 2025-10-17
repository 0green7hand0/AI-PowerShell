/**
 * Logs Store
 * 
 * Manages system logs state, fetching, filtering, and WebSocket connection
 * 
 * Requirements: 5.1, 5.4
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { logsApi, LogEntry, LogLevel, LogsWebSocketManager } from '../api/logs'
import { ElMessage } from 'element-plus'

/**
 * System status for different engines
 */
export interface SystemStatus {
  ai: 'online' | 'offline' | 'error'
  security: 'online' | 'offline' | 'error'
  execution: 'online' | 'offline' | 'error'
  lastCheck: Date | null
}

export const useLogsStore = defineStore('logs', () => {
  // ============================================================================
  // State
  // ============================================================================

  const logs = ref<LogEntry[]>([])
  const isLoading = ref(false)
  const isConnected = ref(false)
  const filterLevel = ref<LogLevel | 'ALL'>('ALL')
  const searchQuery = ref('')
  const autoScroll = ref(true)
  const systemStatus = ref<SystemStatus>({
    ai: 'offline',
    security: 'offline',
    execution: 'offline',
    lastCheck: null
  })

  // WebSocket manager instance
  let wsManager: LogsWebSocketManager | null = null

  // ============================================================================
  // Computed
  // ============================================================================

  /**
   * Filtered logs based on level and search query
   */
  const filteredLogs = computed(() => {
    let result = logs.value

    // Filter by level
    if (filterLevel.value !== 'ALL') {
      result = result.filter(log => log.level === filterLevel.value)
    }

    // Filter by search query
    if (searchQuery.value.trim()) {
      const query = searchQuery.value.toLowerCase()
      result = result.filter(log => 
        log.message.toLowerCase().includes(query) ||
        log.source.toLowerCase().includes(query)
      )
    }

    return result
  })

  /**
   * Count of logs by level
   */
  const logCounts = computed(() => {
    const counts = {
      DEBUG: 0,
      INFO: 0,
      WARNING: 0,
      ERROR: 0,
      CRITICAL: 0,
      ALL: logs.value.length
    }

    logs.value.forEach(log => {
      counts[log.level]++
    })

    return counts
  })

  // ============================================================================
  // Actions
  // ============================================================================

  /**
   * Fetch logs from the API
   * Requirements: 5.1
   * 
   * @param params - Optional query parameters
   */
  const fetchLogs = async (params?: { level?: LogLevel; limit?: number }): Promise<void> => {
    isLoading.value = true

    try {
      const response = await logsApi.getLogs({
        level: params?.level || '',
        limit: params?.limit || 100
      })

      if (response.success) {
        logs.value = response.data.logs
      } else {
        throw new Error('Failed to fetch logs')
      }
    } catch (error: any) {
      console.error('Failed to fetch logs:', error)
      ElMessage.error('获取日志失败')
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Filter logs by level
   * Requirements: 5.4
   * 
   * @param level - Log level to filter by
   */
  const setFilterLevel = (level: LogLevel | 'ALL'): void => {
    filterLevel.value = level

    // Update WebSocket subscription if connected
    if (wsManager?.isConnected()) {
      wsManager.updateSubscription(level)
    }
  }

  /**
   * Set search query for filtering logs
   * Requirements: 5.4
   * 
   * @param query - Search query string
   */
  const setSearchQuery = (query: string): void => {
    searchQuery.value = query
  }

  /**
   * Clear all filters
   */
  const clearFilters = (): void => {
    filterLevel.value = 'ALL'
    searchQuery.value = ''
  }

  /**
   * Add a new log entry (from WebSocket or manual)
   * 
   * @param log - Log entry to add
   */
  const addLog = (log: LogEntry): void => {
    logs.value.unshift(log)

    // Keep only last 1000 logs to prevent memory issues
    if (logs.value.length > 1000) {
      logs.value = logs.value.slice(0, 1000)
    }
  }

  /**
   * Clear all logs
   */
  const clearLogs = (): void => {
    logs.value = []
    ElMessage.info('日志已清空')
  }

  /**
   * Connect to WebSocket for real-time logs
   * Requirements: 5.2
   */
  const connectWebSocket = async (): Promise<void> => {
    if (wsManager?.isConnected()) {
      console.log('WebSocket already connected')
      return
    }

    try {
      wsManager = new LogsWebSocketManager()

      await wsManager.connect({
        level: filterLevel.value,
        onConnect: () => {
          isConnected.value = true
          ElMessage.success('已连接到实时日志流')
        },
        onDisconnect: () => {
          isConnected.value = false
          ElMessage.warning('实时日志流已断开')
        },
        onLog: (log: LogEntry) => {
          addLog(log)
        },
        onError: (error: Error) => {
          console.error('WebSocket error:', error)
          ElMessage.error('实时日志连接失败')
        }
      })
    } catch (error: any) {
      console.error('Failed to connect WebSocket:', error)
      ElMessage.error('无法连接到实时日志流')
    }
  }

  /**
   * Disconnect from WebSocket
   */
  const disconnectWebSocket = (): void => {
    if (wsManager) {
      wsManager.disconnect()
      wsManager = null
      isConnected.value = false
    }
  }

  /**
   * Toggle auto-scroll behavior
   */
  const toggleAutoScroll = (): void => {
    autoScroll.value = !autoScroll.value
  }

  /**
   * Check system status
   * Requirements: 5.6
   */
  const checkSystemStatus = async (): Promise<void> => {
    try {
      // Call health check endpoint
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api'}/health`)
      const data = await response.json()

      if (data.success && data.components) {
        // Update status based on health check
        // Map 'operational' and 'degraded' to 'online', only 'offline' to 'offline'
        const mapStatus = (status: string) => {
          if (status === 'operational' || status === 'degraded') return 'online'
          if (status === 'offline') return 'offline'
          return 'error'
        }
        
        systemStatus.value = {
          ai: mapStatus(data.components.ai),
          security: mapStatus(data.components.security),
          execution: mapStatus(data.components.execution),
          lastCheck: new Date()
        }
      } else {
        // Set all to offline if health check fails
        systemStatus.value = {
          ai: 'offline',
          security: 'offline',
          execution: 'offline',
          lastCheck: new Date()
        }
      }
    } catch (error) {
      console.error('Failed to check system status:', error)
      
      // Set all to error state
      systemStatus.value = {
        ai: 'error',
        security: 'error',
        execution: 'error',
        lastCheck: new Date()
      }
    }
  }

  /**
   * Refresh logs (fetch latest)
   */
  const refreshLogs = async (): Promise<void> => {
    await fetchLogs({ limit: 100 })
    ElMessage.success('日志已刷新')
  }

  // ============================================================================
  // Return
  // ============================================================================

  return {
    // State
    logs,
    isLoading,
    isConnected,
    filterLevel,
    searchQuery,
    autoScroll,
    systemStatus,

    // Computed
    filteredLogs,
    logCounts,

    // Actions
    fetchLogs,
    setFilterLevel,
    setSearchQuery,
    clearFilters,
    addLog,
    clearLogs,
    connectWebSocket,
    disconnectWebSocket,
    toggleAutoScroll,
    checkSystemStatus,
    refreshLogs
  }
})
