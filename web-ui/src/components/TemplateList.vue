<template>
  <div class="template-list">
    <!-- Loading State -->
    <div v-if="isLoading" class="template-list__loading">
      <LoadingSpinner size="large" />
      <p>加载模板中...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="templates.length === 0" class="template-list__empty">
      <div class="template-list__empty-icon">
        <i class="el-icon-document-copy"></i>
      </div>
      <h3>{{ emptyTitle }}</h3>
      <p>{{ emptyMessage }}</p>
      <el-button v-if="showCreateButton" type="primary" @click="handleCreate">
        <i class="el-icon-plus"></i>
        创建第一个模板
      </el-button>
    </div>

    <!-- Template Groups -->
    <div v-else class="template-list__content">
      <div
        v-for="group in groupedTemplates"
        :key="group.category"
        class="template-list__group"
      >
        <!-- Group Header -->
        <div class="template-list__group-header">
          <h3 class="template-list__group-title">
            {{ getCategoryLabel(group.category) }}
          </h3>
          <span class="template-list__group-count">
            {{ group.templates.length }} 个模板
          </span>
        </div>

        <!-- Template Grid -->
        <div class="template-list__grid">
          <TemplateCard
            v-for="template in group.templates"
            :key="template.id"
            :template="template"
            @use="handleUse"
            @edit="handleEdit"
            @delete="handleDelete"
            @click="handleClick"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ElButton } from 'element-plus'
import TemplateCard from './TemplateCard.vue'
import LoadingSpinner from './LoadingSpinner.vue'
import type { Template } from '../api/template'

// ============================================================================
// Props & Emits
// ============================================================================

interface GroupedTemplates {
  category: string
  templates: Template[]
}

interface Props {
  templates: Template[]
  groupedTemplates: GroupedTemplates[]
  isLoading?: boolean
  emptyTitle?: string
  emptyMessage?: string
  showCreateButton?: boolean
}

interface Emits {
  (e: 'use', template: Template): void
  (e: 'edit', template: Template): void
  (e: 'delete', template: Template): void
  (e: 'click', template: Template): void
  (e: 'create'): void
}

const props = withDefaults(defineProps<Props>(), {
  isLoading: false,
  emptyTitle: '暂无模板',
  emptyMessage: '还没有创建任何模板，点击下方按钮创建第一个模板',
  showCreateButton: true
})

const emit = defineEmits<Emits>()

// ============================================================================
// Methods
// ============================================================================

/**
 * Get display label for category
 */
const getCategoryLabel = (category: string): string => {
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
 * Handle template use
 */
const handleUse = (template: Template): void => {
  emit('use', template)
}

/**
 * Handle template edit
 */
const handleEdit = (template: Template): void => {
  emit('edit', template)
}

/**
 * Handle template delete
 */
const handleDelete = (template: Template): void => {
  emit('delete', template)
}

/**
 * Handle template click
 */
const handleClick = (template: Template): void => {
  emit('click', template)
}

/**
 * Handle create button click
 */
const handleCreate = (): void => {
  emit('create')
}
</script>

<style scoped>
.template-list {
  width: 100%;
  height: 100%;
}

/* Loading State */
.template-list__loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-16);
  gap: var(--space-4);
}

.template-list__loading p {
  font-size: var(--text-base);
  color: var(--color-text-secondary);
  margin: 0;
}

/* Empty State */
.template-list__empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-16);
  text-align: center;
}

.template-list__empty-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background-color: var(--color-bg-tertiary);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: var(--space-6);
}

.template-list__empty-icon i {
  font-size: 40px;
  color: var(--color-text-tertiary);
}

.template-list__empty h3 {
  font-size: var(--text-xl);
  font-weight: var(--font-semibold);
  color: var(--color-text-primary);
  margin: 0 0 var(--space-2) 0;
}

.template-list__empty p {
  font-size: var(--text-base);
  color: var(--color-text-secondary);
  margin: 0 0 var(--space-6) 0;
  max-width: 400px;
}

/* Content */
.template-list__content {
  display: flex;
  flex-direction: column;
  gap: var(--space-8);
}

/* Group */
.template-list__group {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.template-list__group-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: var(--space-3);
  border-bottom: 2px solid var(--color-border);
}

.template-list__group-title {
  font-size: var(--text-xl);
  font-weight: var(--font-semibold);
  color: var(--color-text-primary);
  margin: 0;
}

.template-list__group-count {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  background-color: var(--color-bg-tertiary);
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
}

/* Grid */
.template-list__grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: var(--space-6);
}

/* Responsive */
@media (max-width: 1200px) {
  .template-list__grid {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: var(--space-4);
  }
}

@media (max-width: 768px) {
  .template-list__grid {
    grid-template-columns: 1fr;
    gap: var(--space-3);
  }

  .template-list__content {
    gap: var(--space-4);
  }

  .template-list__group {
    gap: var(--space-3);
  }

  .template-list__group-title {
    font-size: var(--text-lg);
  }

  .template-list__empty {
    padding: var(--space-8);
  }

  .template-list__empty-icon {
    width: 60px;
    height: 60px;
  }

  .template-list__empty-icon i {
    font-size: 30px;
  }

  .template-list__empty h3 {
    font-size: var(--text-lg);
  }

  .template-list__empty p {
    font-size: var(--text-sm);
  }
}

@media (max-width: 480px) {
  .template-list__grid {
    gap: var(--space-2);
  }

  .template-list__content {
    gap: var(--space-3);
  }

  .template-list__group-title {
    font-size: var(--text-base);
  }

  .template-list__group-count {
    font-size: var(--text-xs);
  }

  .template-list__empty {
    padding: var(--space-6);
  }

  .template-list__empty-icon {
    width: 50px;
    height: 50px;
  }

  .template-list__empty-icon i {
    font-size: 24px;
  }
}
</style>
