/**
 * Template API Service
 * 
 * Provides methods for managing PowerShell script templates including
 * fetching, creating, updating, deleting, and generating scripts.
 * 
 * Requirements: 1.4, 4.1-4.9
 */

import apiClient from './client'

// ============================================================================
// Type Definitions
// ============================================================================

/**
 * Template parameter definition
 */
export interface TemplateParameter {
  name: string
  type: 'string' | 'number' | 'boolean' | 'select'
  required: boolean
  default?: any
  options?: string[]
  description?: string
}

/**
 * Template representing a PowerShell script template
 */
export interface Template {
  id: string
  name: string
  description: string
  category: string
  scriptContent: string
  parameters: TemplateParameter[]
  keywords: string[]
  createdAt: string
  updatedAt: string
}

/**
 * Query parameters for fetching templates
 */
export interface TemplateQueryParams {
  category?: string
  search?: string
}

/**
 * Request body for creating a template
 */
export interface CreateTemplateRequest {
  name: string
  description: string
  category: string
  scriptContent: string
  parameters: TemplateParameter[]
  keywords?: string[]
}

/**
 * Request body for updating a template
 */
export interface UpdateTemplateRequest {
  name?: string
  description?: string
  category?: string
  scriptContent?: string
  parameters?: TemplateParameter[]
  keywords?: string[]
}

/**
 * Request body for generating script from template
 */
export interface GenerateScriptRequest {
  parameters: Record<string, any>
}

/**
 * Response from template list API
 */
export interface TemplateListResponse {
  success: boolean
  data: {
    items: Template[]
    total: number
  }
}

/**
 * Response from template detail API
 */
export interface TemplateDetailResponse {
  success: boolean
  data: Template
}

/**
 * Response from create/update template API
 */
export interface TemplateResponse {
  success: boolean
  data: Template
  message?: string
}

/**
 * Response from delete template API
 */
export interface DeleteTemplateResponse {
  success: boolean
  message?: string
}

/**
 * Response from generate script API
 */
export interface GenerateScriptResponse {
  success: boolean
  data: {
    script: string
    parameters: Record<string, any>
  }
}

// ============================================================================
// API Methods
// ============================================================================

/**
 * Template API service
 * 
 * Provides methods for template management
 */
export const templateApi = {
  /**
   * Get template list with optional filtering
   * 
   * @param params - Query parameters (category, search)
   * @returns Promise resolving to template list response
   * @throws Error if request fails
   * 
   * Requirements: 4.1, 4.2
   * 
   * @example
   * ```typescript
   * const result = await templateApi.getTemplates({
   *   category: 'automation',
   *   search: 'backup'
   * })
   * console.log(result.data.items)
   * ```
   */
  getTemplates: async (params?: TemplateQueryParams): Promise<TemplateListResponse> => {
    try {
      const response = await apiClient.get('/templates', { params }) as TemplateListResponse
      return response
    } catch (error) {
      throw error
    }
  },

  /**
   * Get detailed information for a specific template
   * 
   * @param id - Template ID
   * @returns Promise resolving to template detail response
   * @throws Error if request fails or template not found
   * 
   * Requirements: 4.3
   * 
   * @example
   * ```typescript
   * const result = await templateApi.getTemplateDetail('tmpl_123')
   * console.log(result.data.scriptContent)
   * ```
   */
  getTemplateDetail: async (id: string): Promise<TemplateDetailResponse> => {
    try {
      const response = await apiClient.get(`/templates/${id}`) as TemplateDetailResponse
      return response
    } catch (error) {
      throw error
    }
  },

  /**
   * Create a new template
   * 
   * @param data - Template creation data
   * @returns Promise resolving to created template response
   * @throws Error if request fails or validation fails
   * 
   * Requirements: 4.7, 4.8
   * 
   * @example
   * ```typescript
   * const result = await templateApi.createTemplate({
   *   name: 'Backup Script',
   *   description: 'Backup files to target location',
   *   category: 'automation',
   *   scriptContent: 'Copy-Item -Path {{sourcePath}} -Destination {{targetPath}}',
   *   parameters: [
   *     { name: 'sourcePath', type: 'string', required: true },
   *     { name: 'targetPath', type: 'string', required: true }
   *   ]
   * })
   * ```
   */
  createTemplate: async (data: CreateTemplateRequest): Promise<TemplateResponse> => {
    try {
      const response = await apiClient.post('/templates', data) as TemplateResponse
      return response
    } catch (error) {
      throw error
    }
  },

  /**
   * Update an existing template
   * 
   * @param id - Template ID
   * @param data - Template update data
   * @returns Promise resolving to updated template response
   * @throws Error if request fails or template not found
   * 
   * Requirements: 4.7, 4.8
   * 
   * @example
   * ```typescript
   * const result = await templateApi.updateTemplate('tmpl_123', {
   *   description: 'Updated description'
   * })
   * ```
   */
  updateTemplate: async (id: string, data: UpdateTemplateRequest): Promise<TemplateResponse> => {
    try {
      const response = await apiClient.put(`/templates/${id}`, data) as TemplateResponse
      return response
    } catch (error) {
      throw error
    }
  },

  /**
   * Delete a template
   * 
   * @param id - Template ID
   * @returns Promise resolving to delete response
   * @throws Error if request fails or template not found
   * 
   * Requirements: 4.9
   * 
   * @example
   * ```typescript
   * await templateApi.deleteTemplate('tmpl_123')
   * ```
   */
  deleteTemplate: async (id: string): Promise<DeleteTemplateResponse> => {
    try {
      const response = await apiClient.delete(`/templates/${id}`) as DeleteTemplateResponse
      return response
    } catch (error) {
      throw error
    }
  },

  /**
   * Generate script from template with provided parameters
   * 
   * @param id - Template ID
   * @param data - Parameters for script generation
   * @returns Promise resolving to generated script response
   * @throws Error if request fails or validation fails
   * 
   * Requirements: 4.4, 4.5, 4.6
   * 
   * @example
   * ```typescript
   * const result = await templateApi.generateScript('tmpl_123', {
   *   parameters: {
   *     sourcePath: 'C:\\Data',
   *     targetPath: 'D:\\Backup'
   *   }
   * })
   * console.log(result.data.script)
   * ```
   */
  generateScript: async (id: string, data: GenerateScriptRequest): Promise<GenerateScriptResponse> => {
    try {
      const response = await apiClient.post(`/templates/${id}/generate`, data) as GenerateScriptResponse
      return response
    } catch (error) {
      throw error
    }
  }
}
