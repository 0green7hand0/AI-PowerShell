/**
 * Template Store
 * 
 * Manages PowerShell script template state and provides actions for
 * fetching, creating, updating, deleting, and generating scripts.
 * 
 * Requirements: 4.1-4.9
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { 
  templateApi, 
  type Template, 
  type CreateTemplateRequest,
  type UpdateTemplateRequest,
  type GenerateScriptRequest
} from '../api/template'
import { ElMessage } from 'element-plus'

// ============================================================================
// Type Definitions
// ============================================================================

/**
 * Grouped templates by category
 */
export interface GroupedTemplates {
  category: string
  templates: Template[]
}

// ============================================================================
// Store Definition
// ============================================================================

export const useTemplateStore = defineStore('template', () => {
  // ============================================================================
  // State
  // ============================================================================

  const templates = ref<Template[]>([])
  const selectedTemplate = ref<Template | null>(null)
  const isLoading = ref(false)
  const searchQuery = ref('')
  const selectedCategory = ref<string>('all')
  const generatedScript = ref<string>('')

  // ============================================================================
  // Computed
  // ============================================================================

  /**
   * Get unique categories from templates
   */
  const categories = computed<string[]>(() => {
    if (!templates.value || templates.value.length === 0) {
      return ['all']
    }
    const uniqueCategories = new Set(templates.value.map(t => t.category))
    return ['all', ...Array.from(uniqueCategories).sort()]
  })

  /**
   * Filter templates by search query and category
   */
  const filteredTemplates = computed<Template[]>(() => {
    if (!templates.value || templates.value.length === 0) {
      return []
    }
    
    let result = templates.value

    // Filter by category
    if (selectedCategory.value !== 'all') {
      result = result.filter(t => t.category === selectedCategory.value)
    }

    // Filter by search query
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase()
      result = result.filter(t => 
        t.name.toLowerCase().includes(query) ||
        t.description.toLowerCase().includes(query) ||
        t.keywords.some(k => k.toLowerCase().includes(query))
      )
    }

    return result
  })

  /**
   * Group filtered templates by category
   */
  const groupedTemplates = computed<GroupedTemplates[]>(() => {
    if (!filteredTemplates.value || filteredTemplates.value.length === 0) {
      return []
    }
    
    const groups: { [key: string]: Template[] } = {}

    filteredTemplates.value.forEach(template => {
      if (!groups[template.category]) {
        groups[template.category] = []
      }
      groups[template.category].push(template)
    })

    return Object.entries(groups)
      .map(([category, templates]) => ({
        category,
        templates: templates.sort((a, b) => a.name.localeCompare(b.name))
      }))
      .sort((a, b) => a.category.localeCompare(b.category))
  })

  /**
   * Get total count of filtered templates
   */
  const totalCount = computed(() => filteredTemplates.value.length)

  // ============================================================================
  // Actions
  // ============================================================================

  /**
   * Fetch templates from the backend
   * 
   * @param params - Optional query parameters
   * 
   * Requirements: 4.1
   */
  const fetchTemplates = async (params?: { category?: string; search?: string }): Promise<void> => {
    isLoading.value = true

    try {
      const response = await templateApi.getTemplates(params)

      if (response.success) {
        templates.value = response.data.items
        ElMessage.success(`已加载 ${response.data.items.length} 个模板`)
      }
    } catch (error: any) {
      console.error('Failed to fetch templates:', error)
      ElMessage.error('加载模板失败')
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Create a new template
   * 
   * @param data - Template creation data
   * 
   * Requirements: 4.7, 4.8
   */
  const createTemplate = async (data: CreateTemplateRequest): Promise<Template | null> => {
    isLoading.value = true

    try {
      const response = await templateApi.createTemplate(data)

      if (response.success) {
        templates.value.push(response.data)
        ElMessage.success('模板创建成功')
        return response.data
      }
      return null
    } catch (error: any) {
      console.error('Failed to create template:', error)
      ElMessage.error('创建模板失败')
      return null
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Update an existing template
   * 
   * @param id - Template ID
   * @param data - Template update data
   * 
   * Requirements: 4.7, 4.8
   */
  const updateTemplate = async (id: string, data: UpdateTemplateRequest): Promise<Template | null> => {
    isLoading.value = true

    try {
      const response = await templateApi.updateTemplate(id, data)

      if (response.success) {
        // Update template in local state
        const index = templates.value.findIndex(t => t.id === id)
        if (index !== -1) {
          templates.value[index] = response.data
        }

        // Update selected template if it's the one being updated
        if (selectedTemplate.value?.id === id) {
          selectedTemplate.value = response.data
        }

        ElMessage.success('模板更新成功')
        return response.data
      }
      return null
    } catch (error: any) {
      console.error('Failed to update template:', error)
      ElMessage.error('更新模板失败')
      return null
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Delete a template
   * 
   * @param id - Template ID
   * 
   * Requirements: 4.9
   */
  const deleteTemplate = async (id: string): Promise<boolean> => {
    isLoading.value = true

    try {
      const response = await templateApi.deleteTemplate(id)

      if (response.success) {
        // Remove template from local state
        templates.value = templates.value.filter(t => t.id !== id)

        // Clear selection if deleted template was selected
        if (selectedTemplate.value?.id === id) {
          selectedTemplate.value = null
        }

        ElMessage.success('模板已删除')
        return true
      }
      return false
    } catch (error: any) {
      console.error('Failed to delete template:', error)
      ElMessage.error('删除模板失败')
      return false
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Generate script from template with provided parameters
   * 
   * @param id - Template ID
   * @param parameters - Parameters for script generation
   * 
   * Requirements: 4.4, 4.5, 4.6
   */
  const generateScript = async (id: string, parameters: Record<string, any>): Promise<string | null> => {
    isLoading.value = true

    try {
      const response = await templateApi.generateScript(id, { parameters })

      if (response.success) {
        generatedScript.value = response.data.script
        ElMessage.success('脚本生成成功')
        return response.data.script
      }
      return null
    } catch (error: any) {
      console.error('Failed to generate script:', error)
      ElMessage.error('生成脚本失败')
      return null
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Select a template for viewing/editing
   * 
   * @param template - Template to select
   */
  const selectTemplate = (template: Template | null): void => {
    selectedTemplate.value = template
  }

  /**
   * Set search query and filter templates
   * 
   * @param query - Search query
   */
  const setSearchQuery = (query: string): void => {
    searchQuery.value = query
  }

  /**
   * Set selected category filter
   * 
   * @param category - Category to filter by ('all' for no filter)
   * 
   * Requirements: 4.2
   */
  const setCategory = (category: string): void => {
    selectedCategory.value = category
  }

  /**
   * Clear all filters and reset to initial state
   */
  const clearFilters = (): void => {
    searchQuery.value = ''
    selectedCategory.value = 'all'
  }

  /**
   * Refresh templates (reload from backend)
   */
  const refresh = async (): Promise<void> => {
    await fetchTemplates()
  }

  /**
   * Get template by ID
   * 
   * @param id - Template ID
   * @returns Template or null if not found
   */
  const getTemplateById = (id: string): Template | null => {
    return templates.value.find(t => t.id === id) || null
  }

  // ============================================================================
  // Return
  // ============================================================================

  return {
    // State
    templates,
    selectedTemplate,
    isLoading,
    searchQuery,
    selectedCategory,
    generatedScript,

    // Computed
    categories,
    filteredTemplates,
    groupedTemplates,
    totalCount,

    // Actions
    fetchTemplates,
    createTemplate,
    updateTemplate,
    deleteTemplate,
    generateScript,
    selectTemplate,
    setSearchQuery,
    setCategory,
    clearFilters,
    refresh,
    getTemplateById
  }
})
