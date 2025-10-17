/**
 * Command API Service
 * 
 * Provides methods for translating natural language to PowerShell commands
 * and executing PowerShell commands.
 * 
 * Requirements: 1.2, 1.3
 */

import apiClient from './client'

// ============================================================================
// Type Definitions
// ============================================================================

/**
 * Security level for commands
 */
export type SecurityLevel = 'safe' | 'low' | 'medium' | 'high' | 'critical'

/**
 * Context for command translation
 */
export interface CommandContext {
  sessionId: string
  history?: Array<{
    input: string
    command: string
    timestamp: string
  }>
}

/**
 * Security information for a command
 */
export interface SecurityInfo {
  level: SecurityLevel
  warnings: string[]
  requiresConfirmation: boolean
  requiresElevation?: boolean
}

/**
 * Request payload for translating natural language to PowerShell
 */
export interface TranslateRequest {
  input: string
  context?: CommandContext
}

/**
 * Response from translate API
 */
export interface TranslateResponse {
  success: boolean
  data: {
    command: string
    confidence: number
    explanation: string
    security: SecurityInfo
  }
}

/**
 * Request payload for executing a PowerShell command
 */
export interface ExecuteRequest {
  command: string
  sessionId: string
  timeout?: number
}

/**
 * Response from execute API
 */
export interface ExecuteResponse {
  success: boolean
  data: {
    output: string | null
    error: string | null
    executionTime: number
    returnCode: number
  }
}

// ============================================================================
// API Methods
// ============================================================================

/**
 * Command API service
 * 
 * Provides methods for command translation and execution
 */
export const commandApi = {
  /**
   * Translate natural language to PowerShell command
   * 
   * @param data - Translation request data
   * @returns Promise resolving to translation response
   * @throws Error if translation fails
   * 
   * @example
   * ```typescript
   * const result = await commandApi.translate({
   *   input: '显示CPU使用率最高的5个进程',
   *   context: {
   *     sessionId: 'session-123'
   *   }
   * })
   * console.log(result.data.command)
   * ```
   */
  translate: async (data: TranslateRequest): Promise<TranslateResponse> => {
    try {
      // apiClient.post returns the unwrapped data (response.data)
      const response = await apiClient.post('/command/translate', data) as TranslateResponse
      return response
    } catch (error) {
      // Error is already handled by axios interceptor
      throw error
    }
  },

  /**
   * Execute a PowerShell command
   * 
   * @param data - Execution request data
   * @returns Promise resolving to execution response
   * @throws Error if execution fails
   * 
   * @example
   * ```typescript
   * const result = await commandApi.execute({
   *   command: 'Get-Process | Select-Object -First 5',
   *   sessionId: 'session-123',
   *   timeout: 30
   * })
   * console.log(result.data.output)
   * ```
   */
  execute: async (data: ExecuteRequest): Promise<ExecuteResponse> => {
    try {
      // apiClient.post returns the unwrapped data (response.data)
      const response = await apiClient.post('/command/execute', data) as ExecuteResponse
      return response
    } catch (error) {
      // Error is already handled by axios interceptor
      throw error
    }
  }
}

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Check if a command requires confirmation based on security level
 * 
 * @param security - Security information
 * @returns true if confirmation is required
 */
export const requiresConfirmation = (security: SecurityInfo): boolean => {
  return security.requiresConfirmation || 
         security.level === 'high' || 
         security.level === 'critical'
}

/**
 * Get color class for security level
 * 
 * @param level - Security level
 * @returns CSS class name for the security level
 */
export const getSecurityLevelColor = (level: SecurityLevel): string => {
  const colorMap: Record<SecurityLevel, string> = {
    safe: 'success',
    low: 'info',
    medium: 'warning',
    high: 'danger',
    critical: 'danger'
  }
  return colorMap[level] || 'info'
}

/**
 * Get display text for security level
 * 
 * @param level - Security level
 * @returns Display text for the security level
 */
export const getSecurityLevelText = (level: SecurityLevel): string => {
  const textMap: Record<SecurityLevel, string> = {
    safe: '安全',
    low: '低风险',
    medium: '中风险',
    high: '高风险',
    critical: '严重风险'
  }
  return textMap[level] || '未知'
}
