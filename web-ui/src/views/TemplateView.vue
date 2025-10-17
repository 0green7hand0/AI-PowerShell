<!--
  TemplateView Component
  
  Main view for displaying and managing PowerShell script templates.
  Includes template list, creation, editing, and usage functionality.
  
  Requirements: 4.1, 4.2
-->

<template>
  <div class="template-view">
    <!-- Header -->
    <div class="template-view__header">
      <div class="template-view__title-section">
        <h1 class="template-view__title">
          <el-icon><Document /></el-icon>
          模板管理
        </h1>
        <p class="template-view__subtitle">
          管理和使用 PowerShell 脚本模板
        </p>
      </div>

      <div class="template-view__actions">
        <el-button
          :icon="Refresh"
          @click="handleRefresh"
          :loading="templateStore.isLoading"
        >
          刷新
        </el-button>
        <el-button
          type="primary"
          :icon="Plus"
          @click="handleCreate"
        >
          创建模板
        </el-button>
      </div>
    </div>

    <!-- Search and Filter Bar -->
    <div class="template-view__toolbar">
      <el-input
        v-model="templateStore.searchQuery"
        placeholder="搜索模板名称、描述或关键词..."
        :prefix-icon="Search"
        clearable
        @input="handleSearchInput"
        class="template-view__search"
      />

      <el-select
        v-model="templateStore.selectedCategory"
        placeholder="选择分类"
        clearable
        @change="handleCategoryChange"
        class="template-view__category-filter"
      >
        <el-option
          v-for="category in templateStore.categories"
          :key="category"
          :label="getCategoryLabel(category)"
          :value="category"
        />
      </el-select>
    </div>

    <!-- Statistics -->
    <div v-if="templateStore.totalCount > 0" class="template-view__stats">
      <el-card shadow="never">
        <div class="template-view__stats-content">
          <div class="template-view__stat">
            <el-icon :size="24" color="var(--el-color-primary)">
              <Document />
            </el-icon>
            <div class="template-view__stat-info">
              <span class="template-view__stat-value">{{ templateStore.totalCount }}</span>
              <span class="template-view__stat-label">模板总数</span>
            </div>
          </div>

          <el-divider direction="vertical" />

          <div class="template-view__stat">
            <el-icon :size="24" color="var(--el-color-success)">
              <FolderOpened />
            </el-icon>
            <div class="template-view__stat-info">
              <span class="template-view__stat-value">{{ templateStore.categories.length - 1 }}</span>
              <span class="template-view__stat-label">分类数量</span>
            </div>
          </div>

          <el-divider direction="vertical" />

          <div class="template-view__stat">
            <el-icon :size="24" color="var(--el-color-warning)">
              <Filter />
            </el-icon>
            <div class="template-view__stat-info">
              <span class="template-view__stat-value">{{ templateStore.filteredTemplates.length }}</span>
              <span class="template-view__stat-label">筛选结果</span>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Template List -->
    <div class="template-view__content">
      <TemplateList
        :templates="templateStore.filteredTemplates"
        :grouped-templates="templateStore.groupedTemplates"
        :is-loading="templateStore.isLoading"
        @use="handleUse"
        @edit="handleEdit"
        @delete="handleDeleteConfirm"
        @click="handleTemplateClick"
        @create="handleCreate"
      />
    </div>

    <!-- Use Template Dialog -->
    <TemplateUseDialog
      v-model:visible="showUseDialog"
      :template="selectedTemplate"
      :is-generating="isGenerating"
      :is-executing="isExecuting"
      @generate="handleGenerate"
      @execute="handleExecute"
      @cancel="handleUseCancel"
      ref="useDialogRef"
    />

    <!-- Create/Edit Template Dialog -->
    <TemplateFormDialog
      v-model:visible="showFormDialog"
      :template="editingTemplate"
      :is-saving="isSaving"
      @submit="handleFormSubmit"
      @cancel="handleFormCancel"
    />

    <!-- Delete Confirmation Dialog -->
    <TemplateDeleteDialog
      v-model:visible="showDeleteDialog"
      :template="deletingTemplate"
      :is-deleting="isDeleting"
      @confirm="handleDeleteConfirmed"
      @cancel="handleDeleteCancel"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import {
  Document,
  Refresh,
  Plus,
  Search,
  FolderOpened,
  Filter
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useTemplateStore } from '../stores/template'
import { useChatStore } from '../stores/chat'
import { useRouter } from 'vue-router'
import type { Template, CreateTemplateRequest } from '../api/template'
import TemplateList from '../components/TemplateList.vue'
import TemplateUseDialog from '../components/TemplateUseDialog.vue'
import TemplateFormDialog from '../components/TemplateFormDialog.vue'
import TemplateDeleteDialog from '../components/TemplateDeleteDialog.vue'

// ============================================================================
// Store & Router
// ============================================================================

const templateStore = useTemplateStore()
const chatStore = useChatStore()
const router = useRouter()

// ============================================================================
// State
// ============================================================================

const showUseDialog = ref(false)
const showFormDialog = ref(false)
const showDeleteDialog = ref(false)
const selectedTemplate = ref<Template | null>(null)
const editingTemplate = ref<Template | null>(null)
const deletingTemplate = ref<Template | null>(null)
const isGenerating = ref(false)
const isExecuting = ref(false)
const isSaving = ref(false)
const isDeleting = ref(false)
const useDialogRef = ref<InstanceType<typeof TemplateUseDialog>>()

// ============================================================================
// Methods
// ============================================================================

/**
 * Get display label for category
 */
const getCategoryLabel = (category: string): string => {
  if (category === 'all') return '全部分类'
  
  const labelMap: Record<string, string> = {
    automation: '自动化',
    file_management: '文件管理',
    system_monitoring: '系统监控',
    network: '网络',
    database: '数据库',
    security: '安全',
    backup: '备份',
    deployment: '部署'
  }
  return labelMap[category] || category
}

/**
 * Handle search input with debounce
 */
let searchTimeout: NodeJS.Timeout
const handleSearchInput = (value: string) => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    templateStore.setSearchQuery(value)
  }, 300)
}

/**
 * Handle category filter change
 */
const handleCategoryChange = (value: string) => {
  templateStore.setCategory(value || 'all')
}

/**
 * Handle refresh button click
 */
const handleRefresh = async () => {
  await templateStore.refresh()
}

/**
 * Handle create template button click
 */
const handleCreate = () => {
  editingTemplate.value = null
  showFormDialog.value = true
}

/**
 * Handle use template
 */
const handleUse = (template: Template) => {
  selectedTemplate.value = template
  showUseDialog.value = true
}

/**
 * Handle edit template
 */
const handleEdit = (template: Template) => {
  editingTemplate.value = template
  showFormDialog.value = true
}

/**
 * Handle delete template (show confirmation)
 */
const handleDeleteConfirm = (template: Template) => {
  deletingTemplate.value = template
  showDeleteDialog.value = true
}

/**
 * Handle template card click
 */
const handleTemplateClick = (template: Template) => {
  // Could show a preview or details
  templateStore.selectTemplate(template)
}

/**
 * Handle generate script from template
 */
const handleGenerate = async (params: Record<string, any>) => {
  if (!selectedTemplate.value) return

  isGenerating.value = true
  try {
    const script = await templateStore.generateScript(selectedTemplate.value.id, params)
    if (script && useDialogRef.value) {
      useDialogRef.value.setGeneratedScript(script)
    }
  } finally {
    isGenerating.value = false
  }
}

/**
 * Handle execute generated script
 */
const handleExecute = async (script: string) => {
  isExecuting.value = true
  try {
    // Add script to chat and navigate to chat view
    await chatStore.sendMessage(`执行以下脚本：\n${script}`)
    
    // Close dialog and navigate to chat
    showUseDialog.value = false
    router.push('/chat')
    
    ElMessage.success('脚本已发送到聊天界面执行')
  } catch (error) {
    console.error('Failed to execute script:', error)
  } finally {
    isExecuting.value = false
  }
}

/**
 * Handle use dialog cancel
 */
const handleUseCancel = () => {
  selectedTemplate.value = null
}

/**
 * Handle form submit (create or update)
 */
const handleFormSubmit = async (data: CreateTemplateRequest) => {
  isSaving.value = true
  try {
    if (editingTemplate.value) {
      // Update existing template
      const result = await templateStore.updateTemplate(editingTemplate.value.id, data)
      if (result) {
        showFormDialog.value = false
        editingTemplate.value = null
      }
    } else {
      // Create new template
      const result = await templateStore.createTemplate(data)
      if (result) {
        showFormDialog.value = false
      }
    }
  } finally {
    isSaving.value = false
  }
}

/**
 * Handle form cancel
 */
const handleFormCancel = () => {
  editingTemplate.value = null
}

/**
 * Handle delete confirmed
 */
const handleDeleteConfirmed = async (template: Template) => {
  isDeleting.value = true
  try {
    const success = await templateStore.deleteTemplate(template.id)
    if (success) {
      showDeleteDialog.value = false
      deletingTemplate.value = null
    }
  } finally {
    isDeleting.value = false
  }
}

/**
 * Handle delete cancel
 */
const handleDeleteCancel = () => {
  deletingTemplate.value = null
}

// ============================================================================
// Lifecycle
// ============================================================================

onMounted(async () => {
  // Load templates on mount
  await templateStore.fetchTemplates()
})
</script>

<style scoped>
.template-view {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.template-view__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.template-view__title-section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.template-view__title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 0;
  font-size: 2rem;
  font-weight: 700;
  color: var(--el-text-color-primary);
}

.template-view__subtitle {
  margin: 0;
  font-size: 1rem;
  color: var(--el-text-color-secondary);
}

.template-view__actions {
  display: flex;
  gap: 0.75rem;
}

.template-view__toolbar {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.template-view__search {
  flex: 1;
  max-width: 500px;
}

.template-view__category-filter {
  width: 200px;
}

.template-view__stats {
  width: 100%;
}

.template-view__stats-content {
  display: flex;
  justify-content: space-around;
  align-items: center;
  gap: 1rem;
  padding: 0.5rem;
}

.template-view__stat {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex: 1;
  min-width: 0;
}

.template-view__stat-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.template-view__stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--el-text-color-primary);
  line-height: 1;
}

.template-view__stat-label {
  font-size: 0.875rem;
  color: var(--el-text-color-secondary);
}

.template-view__content {
  width: 100%;
}

/* Responsive */
@media (max-width: 1024px) {
  .template-view {
    padding: 1.5rem;
  }

  .template-view__toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .template-view__search {
    max-width: none;
  }

  .template-view__category-filter {
    width: 100%;
  }
}

@media (max-width: 768px) {
  .template-view {
    padding: 1rem;
    gap: 1rem;
  }

  .template-view__header {
    flex-direction: column;
  }

  .template-view__title {
    font-size: 1.5rem;
  }

  .template-view__subtitle {
    font-size: 0.875rem;
  }

  .template-view__actions {
    width: 100%;
    flex-direction: column;
  }

  .template-view__actions .el-button {
    width: 100%;
  }

  .template-view__stats-content {
    flex-direction: column;
    align-items: stretch;
    gap: 0.5rem;
  }

  .template-view__stats-content :deep(.el-divider--vertical) {
    display: none;
  }

  .template-view__stat {
    padding: 0.75rem;
    background-color: var(--el-fill-color-light);
    border-radius: 8px;
  }

  .template-view__stat-value {
    font-size: 1.25rem;
  }
}

@media (max-width: 480px) {
  .template-view {
    padding: 0.75rem;
    gap: 0.75rem;
  }

  .template-view__title {
    font-size: 1.25rem;
    gap: 0.5rem;
  }

  .template-view__title :deep(.el-icon) {
    font-size: 1.25rem;
  }

  .template-view__subtitle {
    font-size: 0.75rem;
  }

  .template-view__stat-value {
    font-size: 1.125rem;
  }

  .template-view__stat-label {
    font-size: 0.75rem;
  }
}
</style>
