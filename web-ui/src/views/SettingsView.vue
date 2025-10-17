<!--
  SettingsView Component
  
  Main view for managing application settings including AI, Security,
  Execution, and General configuration.
  
  Requirements: 8.1, 8.2
-->

<template>
  <div class="settings-view">
    <!-- Header -->
    <div class="settings-view__header">
      <div class="settings-view__title-section">
        <h1 class="settings-view__title">
          <el-icon><Setting /></el-icon>
          设置
        </h1>
        <p class="settings-view__subtitle">
          配置 AI PowerShell 助手的各项参数
        </p>
      </div>

      <div class="settings-view__actions">
        <el-button
          :icon="Refresh"
          @click="handleReset"
          :loading="appStore.isSavingConfig"
          :disabled="!hasChanges"
        >
          重置
        </el-button>
        <el-button
          type="primary"
          :icon="Check"
          @click="handleSave"
          :loading="appStore.isSavingConfig"
          :disabled="!hasChanges"
        >
          保存设置
        </el-button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="appStore.isLoadingConfig" class="settings-view__loading">
      <el-skeleton :rows="10" animated />
    </div>

    <!-- Settings Content -->
    <div v-else-if="localConfig" class="settings-view__content">
      <!-- Tabs -->
      <el-tabs v-model="activeTab" class="settings-view__tabs">
        <!-- AI Settings Tab -->
        <el-tab-pane label="AI 设置" name="ai">
          <template #label>
            <span class="settings-view__tab-label">
              <el-icon><Cpu /></el-icon>
              AI 设置
            </span>
          </template>
          <AISettingsForm
            v-model="localConfig.ai"
            @change="handleConfigChange"
          />
        </el-tab-pane>

        <!-- Security Settings Tab -->
        <el-tab-pane label="安全设置" name="security">
          <template #label>
            <span class="settings-view__tab-label">
              <el-icon><Lock /></el-icon>
              安全设置
            </span>
          </template>
          <SecuritySettingsForm
            v-model="localConfig.security"
            @change="handleConfigChange"
          />
        </el-tab-pane>

        <!-- Execution Settings Tab -->
        <el-tab-pane label="执行设置" name="execution">
          <template #label>
            <span class="settings-view__tab-label">
              <el-icon><Monitor /></el-icon>
              执行设置
            </span>
          </template>
          <ExecutionSettingsForm
            v-model="localConfig.execution"
            @change="handleConfigChange"
          />
        </el-tab-pane>

        <!-- General Settings Tab -->
        <el-tab-pane label="通用设置" name="general">
          <template #label>
            <span class="settings-view__tab-label">
              <el-icon><Tools /></el-icon>
              通用设置
            </span>
          </template>
          <GeneralSettingsForm
            v-model="localConfig.general"
            @change="handleConfigChange"
          />
        </el-tab-pane>
      </el-tabs>

      <!-- Unsaved Changes Warning -->
      <el-alert
        v-if="hasChanges"
        type="warning"
        :closable="false"
        show-icon
        class="settings-view__warning"
      >
        <template #title>
          您有未保存的更改
        </template>
        <template #default>
          请点击"保存设置"按钮保存您的更改，或点击"重置"按钮放弃更改。
        </template>
      </el-alert>
    </div>

    <!-- Error State -->
    <div v-else class="settings-view__error">
      <el-empty description="加载配置失败">
        <el-button type="primary" @click="handleReload">
          重新加载
        </el-button>
      </el-empty>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import {
  Setting,
  Refresh,
  Check,
  Cpu,
  Lock,
  Monitor,
  Tools
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAppStore } from '../stores/app'
import { useRouter, onBeforeRouteLeave } from 'vue-router'
import type { AppConfig } from '../api/config'
import AISettingsForm from '../components/AISettingsForm.vue'
import SecuritySettingsForm from '../components/SecuritySettingsForm.vue'
import ExecutionSettingsForm from '../components/ExecutionSettingsForm.vue'
import GeneralSettingsForm from '../components/GeneralSettingsForm.vue'

// ============================================================================
// Store & Router
// ============================================================================

const appStore = useAppStore()
const router = useRouter()

// ============================================================================
// State
// ============================================================================

const activeTab = ref('ai')
const localConfig = ref<AppConfig | null>(null)
const hasChanges = ref(false)

// ============================================================================
// Methods
// ============================================================================

/**
 * Initialize local config from store
 */
const initializeLocalConfig = () => {
  if (appStore.config) {
    localConfig.value = JSON.parse(JSON.stringify(appStore.config))
    hasChanges.value = false
  }
}

/**
 * Handle config change
 */
const handleConfigChange = () => {
  hasChanges.value = true
}

/**
 * Handle save settings
 */
const handleSave = async () => {
  if (!localConfig.value) return

  const success = await appStore.updateConfig(localConfig.value)
  
  if (success) {
    hasChanges.value = false
    ElMessage.success('设置已保存')
  }
}

/**
 * Handle reset settings
 */
const handleReset = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要重置所有设置为默认值吗？此操作不可撤销。',
      '重置设置',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const success = await appStore.resetConfig()
    
    if (success) {
      initializeLocalConfig()
      ElMessage.success('设置已重置为默认值')
    }
  } catch (error) {
    // User cancelled
  }
}

/**
 * Handle reload config
 */
const handleReload = async () => {
  await appStore.loadConfig()
  initializeLocalConfig()
}

/**
 * Check for unsaved changes before leaving
 */
const checkUnsavedChanges = async (): Promise<boolean> => {
  if (!hasChanges.value) {
    return true
  }

  try {
    await ElMessageBox.confirm(
      '您有未保存的更改，确定要离开吗？',
      '未保存的更改',
      {
        confirmButtonText: '离开',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    return true
  } catch (error) {
    return false
  }
}

// ============================================================================
// Watchers
// ============================================================================

// Watch store config changes
watch(
  () => appStore.config,
  (newConfig) => {
    if (newConfig && !hasChanges.value) {
      initializeLocalConfig()
    }
  },
  { deep: true }
)

// ============================================================================
// Route Guards
// ============================================================================

onBeforeRouteLeave(async (to, from, next) => {
  const canLeave = await checkUnsavedChanges()
  next(canLeave)
})

// ============================================================================
// Lifecycle
// ============================================================================

onMounted(async () => {
  // Load config if not already loaded
  if (!appStore.config) {
    await appStore.loadConfig()
  }
  
  initializeLocalConfig()
})

// Handle browser refresh/close
onBeforeUnmount(() => {
  if (hasChanges.value) {
    // Note: Modern browsers don't allow custom messages
    window.onbeforeunload = () => true
  }
})
</script>

<style scoped>
.settings-view {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.settings-view__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.settings-view__title-section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.settings-view__title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 0;
  font-size: 2rem;
  font-weight: 700;
  color: var(--el-text-color-primary);
}

.settings-view__subtitle {
  margin: 0;
  font-size: 1rem;
  color: var(--el-text-color-secondary);
}

.settings-view__actions {
  display: flex;
  gap: 0.75rem;
}

.settings-view__loading {
  padding: 2rem;
}

.settings-view__content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.settings-view__tabs {
  width: 100%;
}

.settings-view__tab-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.settings-view__warning {
  margin-top: 1rem;
}

.settings-view__error {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

/* Tab Pane Content Styling */
.settings-view__tabs :deep(.el-tab-pane) {
  padding: 1.5rem 0;
}

/* Responsive */
@media (max-width: 1024px) {
  .settings-view {
    padding: 1.5rem;
  }
}

@media (max-width: 768px) {
  .settings-view {
    padding: 1rem;
  }

  .settings-view__header {
    flex-direction: column;
  }

  .settings-view__title {
    font-size: 1.5rem;
  }

  .settings-view__actions {
    width: 100%;
    flex-direction: column;
  }

  .settings-view__actions .el-button {
    width: 100%;
  }

  .settings-view__tabs :deep(.el-tabs__nav-wrap) {
    overflow-x: auto;
  }

  .settings-view__tab-label {
    font-size: 0.875rem;
  }
}
</style>
