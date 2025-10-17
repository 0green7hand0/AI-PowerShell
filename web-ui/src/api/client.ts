/**
 * Axios API Client
 * 
 * Configured axios instance with interceptors for:
 * - Request preprocessing (auth, headers)
 * - Response handling (data extraction, error handling)
 * - Error notification (user-friendly messages)
 * 
 * Requirements: 1.2, 1.3, 6.9
 */

import axios, { AxiosError, AxiosRequestConfig, AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'

// ============================================================================
// Configuration
// ============================================================================

/**
 * API base URL from environment or default to /api
 */
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

/**
 * Default request timeout (30 seconds)
 */
const DEFAULT_TIMEOUT = 30000

/**
 * Create axios instance with default configuration
 */
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: DEFAULT_TIMEOUT,
  headers: {
    'Content-Type': 'application/json'
  }
})

// ============================================================================
// Request Interceptor
// ============================================================================

/**
 * Request interceptor
 * 
 * Adds authentication tokens and other headers before sending requests
 */
apiClient.interceptors.request.use(
  (config) => {
    // Add authentication token if available
    const token = localStorage.getItem('auth_token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }

    // Add request timestamp for debugging
    if (import.meta.env?.DEV) {
      console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`, config.data)
    }

    return config
  },
  (error: AxiosError) => {
    console.error('[API Request Error]', error)
    return Promise.reject(error)
  }
)

// ============================================================================
// Response Interceptor
// ============================================================================

/**
 * Response interceptor
 * 
 * Handles successful responses and errors
 */
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    // Log response in development mode
    if (import.meta.env?.DEV) {
      console.log(`[API Response] ${response.config.method?.toUpperCase()} ${response.config.url}`, response.data)
    }

    // Return the data directly (unwrap response)
    return response.data
  },
  (error: AxiosError<ApiErrorResponse>) => {
    // Handle different error scenarios
    handleApiError(error)
    return Promise.reject(error)
  }
)

// ============================================================================
// Error Handling
// ============================================================================

/**
 * API error response structure
 */
interface ApiErrorResponse {
  success: false
  error: {
    message: string
    code: number
    details?: any
  }
}

/**
 * Handle API errors and show user-friendly messages
 * 
 * @param error - Axios error object
 */
const handleApiError = (error: AxiosError<ApiErrorResponse>) => {
  let message = '请求失败'

  if (error.response) {
    // Server responded with error status
    const { status, data } = error.response

    // Extract error message from response
    message = data?.error?.message || error.message || '服务器错误'

    // Handle specific status codes
    switch (status) {
      case 400:
        message = data?.error?.message || '请求参数错误'
        break
      case 401:
        message = '未授权，请登录'
        // Optionally redirect to login
        // router.push('/login')
        break
      case 403:
        message = '没有权限访问'
        break
      case 404:
        message = '请求的资源不存在'
        break
      case 500:
        message = data?.error?.message || '服务器内部错误'
        break
      case 503:
        message = '服务暂时不可用'
        break
      default:
        message = data?.error?.message || `请求失败 (${status})`
    }

    // Log error details in development
    if (import.meta.env?.DEV) {
      console.error('[API Error Response]', {
        status,
        url: error.config?.url,
        method: error.config?.method,
        data: error.config?.data,
        response: data
      })
    }
  } else if (error.request) {
    // Request was made but no response received
    message = '网络错误，请检查网络连接'
    console.error('[API Network Error]', error.request)
  } else {
    // Error in request configuration
    message = error.message || '请求配置错误'
    console.error('[API Config Error]', error.message)
  }

  // Show error message to user
  ElMessage.error(message)
}

// ============================================================================
// Export
// ============================================================================

export default apiClient

/**
 * Export error handler for custom error handling
 */
export { handleApiError }
