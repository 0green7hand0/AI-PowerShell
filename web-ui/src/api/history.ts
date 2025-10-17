/**
 * History API Service
 * 
 * Provides methods for managing command history including
 * fetching, searching, and deleting history records.
 * 
 * Requirements: 1.4, 3.1-3.7
 */

import apiClient from './client'

// ============================================================================
// Type Definitions
// ============================================================================

/**
 * History item representing a command execution record
 */
export interface HistoryItem {
  id: string
  userInput: string
  command: string
  success: boolean
  output?: string | null
  error?: string | null
  executionTime: number
  timestamp: string
}

/**
 * Query parameters for fetching history
 */
export interface HistoryQueryParams {
  page?: number
  limit?: number
  search?: string
}

/**
 * Response from history list API
 */
export interface HistoryListResponse {
  success: boolean
  data: {
    items: HistoryItem[]
    total: number
    page: number
    limit: number
  }
}

/**
 * Response from history detail API
 */
export interface HistoryDetailResponse {
  success: boolean
  data: HistoryItem
}

/**
 * Response from delete history API
 */
export interface DeleteHistoryResponse {
  success: boolean
  message?: string
}

// ============================================================================
// API Methods
// ============================================================================

/**
 * History API service
 * 
 * Provides methods for history management
 */
export const historyApi = {
  /**
   * Get history list with pagination and search
   * 
   * @param params - Query parameters (page, limit, search)
   * @returns Promise resolving to history list response
   * @throws Error if request fails
   * 
   * Requirements: 3.1, 3.6, 3.7
   * 
   * @example
   * ```typescript
   * const result = await historyApi.getHistory({
   *   page: 1,
   *   limit: 20,
   *   search: 'process'
   * })
   * console.log(result.data.items)
   * ```
   */
  getHistory: async (params?: HistoryQueryParams): Promise<HistoryListResponse> => {
    try {
      const response = await apiClient.get('/history', { params }) as HistoryListResponse
      return response
    } catch (error) {
      // Error is already handled by axios interceptor
      throw error
    }
  },

  /**
   * Get detailed information for a specific history item
   * 
   * @param id - History item ID
   * @returns Promise resolving to history detail response
   * @throws Error if request fails or item not found
   * 
   * Requirements: 3.3
   * 
   * @example
   * ```typescript
   * const result = await historyApi.getHistoryDetail('hist_123')
   * console.log(result.data.output)
   * ```
   */
  getHistoryDetail: async (id: string): Promise<HistoryDetailResponse> => {
    try {
      const response = await apiClient.get(`/history/${id}`) as HistoryDetailResponse
      return response
    } catch (error) {
      throw error
    }
  },

  /**
   * Delete a history item
   * 
   * @param id - History item ID
   * @returns Promise resolving to delete response
   * @throws Error if request fails or item not found
   * 
   * Requirements: 3.4, 3.5
   * 
   * @example
   * ```typescript
   * await historyApi.deleteHistory('hist_123')
   * ```
   */
  deleteHistory: async (id: string): Promise<DeleteHistoryResponse> => {
    try {
      const response = await apiClient.delete(`/history/${id}`) as DeleteHistoryResponse
      return response
    } catch (error) {
      throw error
    }
  }
}
