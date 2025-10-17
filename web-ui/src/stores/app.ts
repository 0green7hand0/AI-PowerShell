/**
 * App Store
 * 
 * Manages global application state including theme, sidebar,
 * configuration, and system status.
 * 
 * Requirements: 8.1, 8.4, 8.6
 */

import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { configApi, type AppConfig } from '../api/config'
import { ElMessage } from 'element-plus'

// ============================================================================
// Type Definitions
// ============================================================================

/**
 * System status for different engines
 */
export interface SystemStatus {
  ai: 'online' | 'offline' | 'error'
  security: 'online' | 'offline' | 'error'
  execution: 'online' | 'offline' | 'error'
  lastCheck: Date | null
}

/**
 * Theme type
 */
export type Theme = 'light' | 'dark'

// ============================================================================
// Store Definition
// ============================================================================

export const useAppStore = defineStore('app', () => {
  // ============================================================================
  // State
  // ============================================================================

  const theme = ref<Theme>('light')
  const sidebarCollapsed = ref(false)
  const config = ref<AppConfig | null>(null)
  const systemStatus = ref<SystemStatus>({
    ai: 'offline',
    security: 'offline',
    execution: 'offline',
    lastCheck: null
  })
  const isLoadingConfig = ref(false)
  const isSavingConfig = ref(false)

  // ============================================================================
  // Computed
  // ============================================================================

  /**
   * Check if all systems are online
   */
  const allSystemsOnline = computed(() => {
    return (
      systemStatus.value.ai === 'online' &&
      systemStatus.value.security === 'online' &&
      systemStatus.value.execution === 'online'
    )
  })

  /**
   * Check if any system has an error
   */
  const hasSystemError = computed(() => {
    return (
      systemStatus.value.ai === 'error' ||
      systemStatus.value.security === 'error' ||
      systemStatus.value.execution === 'error'
    )
  })

  /**
   * Get current language from config
   */
  const language = computed(() => {
    return config.value?.general?.language || 'zh-CN'
  })

  // ============================================================================
  // Actions
  // ============================================================================

  /**
   * Toggle theme between light and dark
   * 
   * Requirements: 6.2
   */
  const toggleTheme = (): void => {
    theme.value = theme.value === 'light' ? 'dark' : 'light'
    applyTheme(theme.value)
    saveThemeToStorage(theme.value)
  }

  /**
   * Set theme explicitly
   * 
   * @param newTheme - Theme to set
   */
  const setTheme = (newTheme: Theme): void => {
    theme.value = newTheme
    applyTheme(newTheme)
    saveThemeToStorage(newTheme)
  }

  /**
   * Apply theme to document
   * 
   * @param themeValue - Theme to apply
   */
  const applyTheme = (themeValue: Theme): void => {
    document.documentElement.setAttribute('data-theme', themeValue)
    
    // Update Element Plus theme
    if (themeValue === 'dark') {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }

  /**
   * Save theme to localStorage
   * 
   * @param themeValue - Theme to save
   */
  const saveThemeToStorage = (themeValue: Theme): void => {
    localStorage.setItem('theme', themeValue)
  }

  /**
   * Load theme from localStorage
   */
  const loadThemeFromStorage = (): void => {
    const savedTheme = localStorage.getItem('theme') as Theme | null
    if (savedTheme && (savedTheme === 'light' || savedTheme === 'dark')) {
      theme.value = savedTheme
      applyTheme(savedTheme)
    } else {
      // Check system preference
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      theme.value = prefersDark ? 'dark' : 'light'
      applyTheme(theme.value)
    }
  }

  /**
   * Toggle sidebar collapsed state
   */
  const toggleSidebar = (): void => {
    sidebarCollapsed.value = !sidebarCollapsed.value
    saveSidebarStateToStorage(sidebarCollapsed.value)
  }

  /**
   * Set sidebar collapsed state
   * 
   * @param collapsed - Whether sidebar should be collapsed
   */
  const setSidebarCollapsed = (collapsed: boolean): void => {
    sidebarCollapsed.value = collapsed
    saveSidebarStateToStorage(collapsed)
  }

  /**
   * Save sidebar state to localStorage
   * 
   * @param collapsed - Sidebar collapsed state
   */
  const saveSidebarStateToStorage = (collapsed: boolean): void => {
    localStorage.setItem('sidebarCollapsed', String(collapsed))
  }

  /**
   * Load sidebar state from localStorage
   */
  const loadSidebarStateFromStorage = (): void => {
    const savedState = localStorage.getItem('sidebarCollapsed')
    if (savedState !== null) {
      sidebarCollapsed.value = savedState === 'true'
    }
  }

  /**
   * Load configuration from backend
   * 
   * Requirements: 8.1
   */
  const loadConfig = async (): Promise<void> => {
    isLoadingConfig.value = true

    try {
      const response = await configApi.getConfig()

      if (response.success) {
        config.value = response.data

        // Sync theme with config
        if (response.data.general?.theme) {
          setTheme(response.data.general.theme)
        }

        console.log('Configuration loaded successfully')
      }
    } catch (error: any) {
      console.error('Failed to load config:', error)
      ElMessage.error('加载配置失败')
    } finally {
      isLoadingConfig.value = false
    }
  }

  /**
   * Update configuration
   * 
   * @param updates - Partial configuration updates
   * 
   * Requirements: 8.4
   */
  const updateConfig = async (updates: Partial<AppConfig>): Promise<boolean> => {
    isSavingConfig.value = true

    try {
      const response = await configApi.updateConfig(updates)

      if (response.success) {
        config.value = response.data

        // Sync theme if it was updated
        if (updates.general?.theme) {
          setTheme(updates.general.theme)
        }

        ElMessage.success('配置已保存')
        return true
      }

      return false
    } catch (error: any) {
      console.error('Failed to update config:', error)
      ElMessage.error('保存配置失败')
      return false
    } finally {
      isSavingConfig.value = false
    }
  }

  /**
   * Reset configuration to defaults
   * 
   * Requirements: 8.6
   */
  const resetConfig = async (): Promise<boolean> => {
    isSavingConfig.value = true

    try {
      const response = await configApi.resetConfig()

      if (response.success) {
        config.value = response.data

        // Sync theme with reset config
        if (response.data.general?.theme) {
          setTheme(response.data.general.theme)
        }

        ElMessage.success('配置已重置为默认值')
        return true
      }

      return false
    } catch (error: any) {
      console.error('Failed to reset config:', error)
      ElMessage.error('重置配置失败')
      return false
    } finally {
      isSavingConfig.value = false
    }
  }

  /**
   * Check system status
   * 
   * Requirements: 5.6
   */
  const checkSystemStatus = async (): Promise<void> => {
    try {
      // In a real implementation, this would call a health check endpoint
      // For now, we'll simulate it based on config loading
      if (config.value) {
        systemStatus.value = {
          ai: 'online',
          security: 'online',
          execution: 'online',
          lastCheck: new Date()
        }
      } else {
        systemStatus.value = {
          ai: 'offline',
          security: 'offline',
          execution: 'offline',
          lastCheck: new Date()
        }
      }
    } catch (error: any) {
      console.error('Failed to check system status:', error)
      systemStatus.value = {
        ai: 'error',
        security: 'error',
        execution: 'error',
        lastCheck: new Date()
      }
    }
  }

  /**
   * Initialize app store
   * 
   * Loads theme, sidebar state, and configuration
   */
  const initialize = async (): Promise<void> => {
    loadThemeFromStorage()
    loadSidebarStateFromStorage()
    await loadConfig()
    await checkSystemStatus()
  }

  // ============================================================================
  // Watchers
  // ============================================================================

  // Watch config changes and sync theme
  watch(
    () => config.value?.general?.theme,
    (newTheme) => {
      if (newTheme && newTheme !== theme.value) {
        setTheme(newTheme)
      }
    }
  )

  // ============================================================================
  // Return
  // ============================================================================

  return {
    // State
    theme,
    sidebarCollapsed,
    config,
    systemStatus,
    isLoadingConfig,
    isSavingConfig,

    // Computed
    allSystemsOnline,
    hasSystemError,
    language,

    // Actions
    toggleTheme,
    setTheme,
    toggleSidebar,
    setSidebarCollapsed,
    loadConfig,
    updateConfig,
    resetConfig,
    checkSystemStatus,
    initialize
  }
})
