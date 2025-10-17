/**
 * Config API Service
 * 
 * Provides methods for managing system configuration including
 * AI settings, security settings, execution settings, and general settings.
 * 
 * Requirements: 1.4, 8.1-8.7
 */

import apiClient from './client'

// ============================================================================
// Type Definitions
// ============================================================================

/**
 * AI Engine Configuration
 */
export interface AIConfig {
  provider: string
  modelName: string
  temperature: number
  maxTokens: number
  apiKey?: string
}

/**
 * Security Engine Configuration
 */
export interface SecurityConfig {
  whitelistMode: boolean
  requireConfirmation: boolean
  dangerousPatterns: string[]
  allowedCommands?: string[]
}

/**
 * Execution Engine Configuration
 */
export interface ExecutionConfig {
  timeout: number
  shellType: string
  encoding: string
  workingDirectory?: string
}

/**
 * General Application Configuration
 */
export interface GeneralConfig {
  language: string
  theme: 'light' | 'dark'
  logLevel: string
  autoSave: boolean
}

/**
 * Complete application configuration
 */
export interface AppConfig {
  ai: AIConfig
  security: SecurityConfig
  execution: ExecutionConfig
  general: GeneralConfig
}

/**
 * Response from get config API
 */
export interface GetConfigResponse {
  success: boolean
  data: AppConfig
}

/**
 * Request for updating config
 */
export interface UpdateConfigRequest {
  ai?: Partial<AIConfig>
  security?: Partial<SecurityConfig>
  execution?: Partial<ExecutionConfig>
  general?: Partial<GeneralConfig>
}

/**
 * Response from update config API
 */
export interface UpdateConfigResponse {
  success: boolean
  data: AppConfig
  message?: string
}

// ============================================================================
// API Methods
// ============================================================================

/**
 * Config API service
 * 
 * Provides methods for configuration management
 */
export const configApi = {
  /**
   * Get current application configuration
   * 
   * @returns Promise resolving to config response
   * @throws Error if request fails
   * 
   * Requirements: 8.1
   * 
   * @example
   * ```typescript
   * const result = await configApi.getConfig()
   * console.log(result.data.ai.modelName)
   * ```
   */
  getConfig: async (): Promise<GetConfigResponse> => {
    try {
      const response = await apiClient.get('/config') as GetConfigResponse
      return response
    } catch (error) {
      // Error is already handled by axios interceptor
      throw error
    }
  },

  /**
   * Update application configuration
   * 
   * @param config - Partial configuration to update
   * @returns Promise resolving to updated config response
   * @throws Error if request fails or validation fails
   * 
   * Requirements: 8.2, 8.3, 8.4
   * 
   * @example
   * ```typescript
   * const result = await configApi.updateConfig({
   *   ai: {
   *     temperature: 0.7,
   *     maxTokens: 2000
   *   }
   * })
   * console.log(result.data)
   * ```
   */
  updateConfig: async (config: UpdateConfigRequest): Promise<UpdateConfigResponse> => {
    try {
      const response = await apiClient.put('/config', config) as UpdateConfigResponse
      return response
    } catch (error) {
      throw error
    }
  },

  /**
   * Reset configuration to default values
   * 
   * @returns Promise resolving to default config response
   * @throws Error if request fails
   * 
   * Requirements: 8.6
   * 
   * @example
   * ```typescript
   * const result = await configApi.resetConfig()
   * console.log('Config reset to defaults')
   * ```
   */
  resetConfig: async (): Promise<UpdateConfigResponse> => {
    try {
      const response = await apiClient.post('/config/reset') as UpdateConfigResponse
      return response
    } catch (error) {
      throw error
    }
  }
}
