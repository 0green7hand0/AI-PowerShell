/**
 * Logs API Service
 * 
 * Provides methods for fetching system logs and managing WebSocket connections
 * for real-time log streaming.
 * 
 * Requirements: 1.4, 5.1, 5.2, 5.4
 */

import apiClient from './client'
import { io, Socket } from 'socket.io-client'

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

/**
 * WebSocket subscription options
 */
export interface LogSubscriptionOptions {
  level?: LogLevel | 'ALL'
  onLog?: (log: LogEntry) => void
  onConnect?: () => void
  onDisconnect?: () => void
  onError?: (error: Error) => void
}

// ============================================================================
// API Methods
// ============================================================================

/**
 * Logs API service
 * 
 * Provides methods for log retrieval and real-time streaming
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
      const response = await apiClient.get(url) as GetLogsResponse
      return response
    } catch (error) {
      throw error
    }
  }
}

// ============================================================================
// WebSocket Connection Manager
// ============================================================================

/**
 * WebSocket connection manager for real-time log streaming
 */
export class LogsWebSocketManager {
  private socket: Socket | null = null
  private options: LogSubscriptionOptions = {}
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000

  /**
   * Connect to the logs WebSocket
   * 
   * @param options - Subscription options and callbacks
   * @returns Promise that resolves when connected
   */
  connect(options: LogSubscriptionOptions = {}): Promise<void> {
    return new Promise((resolve, reject) => {
      this.options = options

      // Get base URL from environment or default
      const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'
      
      // Create socket connection
      this.socket = io(baseUrl, {
        path: '/socket.io',
        transports: ['websocket', 'polling'],
        reconnection: true,
        reconnectionAttempts: this.maxReconnectAttempts,
        reconnectionDelay: this.reconnectDelay
      })

      // Handle connection
      this.socket.on('connect', () => {
        console.log('Connected to logs WebSocket')
        this.reconnectAttempts = 0
        
        // Subscribe to logs namespace
        this.socket?.emit('subscribe', {
          level: options.level || 'ALL'
        })
        
        if (options.onConnect) {
          options.onConnect()
        }
        
        resolve()
      })

      // Handle connection errors
      this.socket.on('connect_error', (error) => {
        console.error('WebSocket connection error:', error)
        this.reconnectAttempts++
        
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
          if (options.onError) {
            options.onError(new Error('Failed to connect after multiple attempts'))
          }
          reject(error)
        }
      })

      // Handle disconnection
      this.socket.on('disconnect', (reason) => {
        console.log('Disconnected from logs WebSocket:', reason)
        
        if (options.onDisconnect) {
          options.onDisconnect()
        }
      })

      // Handle log messages
      this.socket.on('log', (log: LogEntry) => {
        if (options.onLog) {
          options.onLog(log)
        }
      })

      // Handle subscription confirmation
      this.socket.on('subscribed', (data) => {
        console.log('Subscribed to logs:', data)
      })

      // Handle connection confirmation
      this.socket.on('connected', (data) => {
        console.log('WebSocket connected:', data)
      })
    })
  }

  /**
   * Disconnect from the logs WebSocket
   */
  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
    }
  }

  /**
   * Check if WebSocket is connected
   * 
   * @returns true if connected
   */
  isConnected(): boolean {
    return this.socket?.connected || false
  }

  /**
   * Update subscription filters
   * 
   * @param level - Log level to filter by
   */
  updateSubscription(level: LogLevel | 'ALL'): void {
    if (this.socket?.connected) {
      this.socket.emit('subscribe', { level })
    }
  }

  /**
   * Manually emit a log event (for testing)
   * 
   * @param log - Log entry to emit
   */
  emitLog(log: LogEntry): void {
    if (this.options.onLog) {
      this.options.onLog(log)
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
    const date = new Date(timestamp)
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
