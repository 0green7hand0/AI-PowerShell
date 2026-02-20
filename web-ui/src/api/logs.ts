/**
 * Logs API Service
 *
 * Provides methods for fetching system logs
 *
 * Requirements: 1.4, 5.1, 5.2, 5.4
 */

import apiClient from './client'

// ============================================================================
// Type Definitions
// ============================================================================

/**
 * Log level types
 */
export type LogLevel = 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL'

/**
 * Log entry structure
 */
export interface LogEntry {
  timestamp: string
  level: LogLevel
  message: string
  source: string
}

/**
 * Request parameters for fetching logs
 */
export interface GetLogsParams {
  level?: LogLevel | ''
  limit?: number
  since?: string
}

/**
 * Response from get logs API
 */
export interface GetLogsResponse {
  success: boolean
  data: {
    logs: LogEntry[]
    total: number
  }
}

// ============================================================================
// API Methods
// ============================================================================

/**
 * Logs API service
 *
 * Provides methods for log retrieval
 */
export const logsApi = {
  /**
   * Get system logs with optional filtering
   *
   * @param params - Query parameters for filtering logs
   * @returns Promise resolving to logs response
   * @throws Error if request fails
   *
   * @example
   * ```typescript
   * const result = await logsApi.getLogs({
   *   level: 'ERROR',
   *   limit: 100
   * })
   * console.log(result.data.logs)
   * ```
   */
  getLogs: async (params?: GetLogsParams): Promise<GetLogsResponse> => {
    try {
      const queryParams = new URLSearchParams()

      if (params?.level) {
        queryParams.append('level', params.level)
      }
      if (params?.limit) {
        queryParams.append('limit', params.limit.toString())
      }
      if (params?.since) {
        queryParams.append('since', params.since)
      }

      const url = `/logs${queryParams.toString() ? '?' + queryParams.toString() : ''}`
      const response = (await apiClient.get(url)) as GetLogsResponse
      return response
    } catch (error) {
      throw error
    }
  }
}

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Get color class for log level
 *
 * @param level - Log level
 * @returns CSS class name for the log level
 */
export const getLogLevelColor = (level: LogLevel): string => {
  const colorMap: Record<LogLevel, string> = {
    DEBUG: 'info',
    INFO: 'success',
    WARNING: 'warning',
    ERROR: 'danger',
    CRITICAL: 'danger'
  }
  return colorMap[level] || 'info'
}

/**
 * Get icon for log level
 *
 * @param level - Log level
 * @returns Icon name for the log level
 */
export const getLogLevelIcon = (level: LogLevel): string => {
  const iconMap: Record<LogLevel, string> = {
    DEBUG: 'bug',
    INFO: 'info-circle',
    WARNING: 'exclamation-triangle',
    ERROR: 'times-circle',
    CRITICAL: 'exclamation-circle'
  }
  return iconMap[level] || 'info-circle'
}

/**
 * Format timestamp for display
 *
 * @param timestamp - ISO timestamp string
 * @returns Formatted time string
 */
export const formatLogTimestamp = (timestamp: string): string => {
  try {
    let date: Date
    
    // Handle different timestamp formats
    if (timestamp.includes(',')) {
      // Format: 2026-02-19 14:54:58,733 (with comma for milliseconds)
      const parts = timestamp.split(',')
      if (parts.length === 2) {
        date = new Date(parts[0].trim() + '.' + parts[1].trim().substring(0, 3))
      } else {
        date = new Date(timestamp)
      }
    } else if (timestamp.includes('T')) {
      // ISO format: 2026-02-19T14:54:58.733Z
      date = new Date(timestamp)
    } else if (timestamp.includes(' ')) {
      // Format: 2026-02-19 14:54:58
      date = new Date(timestamp)
    } else {
      date = new Date(timestamp)
    }
    
    if (isNaN(date.getTime())) {
      return timestamp
    }
    
    return date.toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    })
  } catch {
    return timestamp
  }
}
