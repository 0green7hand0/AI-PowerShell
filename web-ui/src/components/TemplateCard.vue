<template>
  <div 
    class="template-card"
    :class="{ 'template-card--hover': !disabled }"
    @click="handleCardClick"
  >
    <!-- Header -->
    <div class="template-card__header">
      <div class="template-card__icon">
        <i :class="getCategoryIcon(template.category)"></i>
      </div>
      <div class="template-card__title-section">
        <h3 class="template-card__title">{{ template.name }}</h3>
        <span class="template-card__category">{{ getCategoryLabel(template.category) }}</span>
      </div>
    </div>

    <!-- Description -->
    <p class="template-card__description">{{ template.description }}</p>

    <!-- Metadata -->
    <div class="template-card__metadata">
      <div class="template-card__meta-item">
        <i class="el-icon-document"></i>
        <span>{{ template.parameters.length }} 个参数</span>
      </div>
      <div v-if="template.keywords.length > 0" class="template-card__meta-item">
        <i class="el-icon-price-tag"></i>
        <span>{{ template.keywords.slice(0, 2).join(', ') }}</span>
      </div>
    </div>

    <!-- Keywords (Tags) -->
    <div v-if="template.keywords.length > 0" class="template-card__keywords">
      <el-tag
        v-for="keyword in template.keywords.slice(0, 3)"
        :key="keyword"
        size="small"
        type="info"
        effect="plain"
      >
        {{ keyword }}
      </el-tag>
      <el-tag
        v-if="template.keywords.length > 3"
        size="small"
        type="info"
        effect="plain"
      >
        +{{ template.keywords.length - 3 }}
      </el-tag>
    </div>

    <!-- Actions -->
    <div class="template-card__actions">
      <el-button
        type="primary"
        size="small"
        @click.stop="handleUse"
        :disabled="disabled"
      >
        <i class="el-icon-video-play"></i>
        使用
      </el-button>
      <el-button
        size="small"
        @click.stop="handleEdit"
        :disabled="disabled"
      >
        <i class="el-icon-edit"></i>
        编辑
      </el-button>
      <el-button
        size="small"
        type="danger"
        plain
        @click.stop="handleDelete"
        :disabled="disabled"
      >
        <i class="el-icon-delete"></i>
        删除
      </el-button>
    </div>

    <!-- Updated timestamp -->
    <div class="template-card__footer">
      <span class="template-card__timestamp">
        更新于 {{ formatDate(template.updatedAt) }}
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ElButton, ElTag } from 'element-plus'
import type { Template } from '../api/template'

// ============================================================================
// Props & Emits
// ============================================================================

interface Props {
  template: Template
  disabled?: boolean
}

interface Emits {
  (e: 'use', template: Template): void
  (e: 'edit', template: Template): void
  (e: 'delete', template: Template): void
  (e: 'click', template: Template): void
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false
})

const emit = defineEmits<Emits>()

// ============================================================================
// Methods
// ============================================================================

/**
 * Get icon class for category
 */
const getCategoryIcon = (category: string): string => {
  const iconMap: Record<string, string> = {
    automation: 'el-icon-setting',
    file_management: 'el-icon-folder',
    system_monitoring: 'el-icon-monitor',
    network: 'el-icon-connection',
    database: 'el-icon-coin',
    security: 'el-icon-lock',
    backup: 'el-icon-download',
    deployment: 'el-icon-upload',
    default: 'el-icon-document'
  }
  return iconMap[category] || iconMap.default
}

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
 * Format date to readable string
 */
const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return '刚刚'
  if (diffMins < 60) return `${diffMins} 分钟前`
  if (diffHours < 24) return `${diffHours} 小时前`
  if (diffDays < 7) return `${diffDays} 天前`

  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

/**
 * Handle card click
 */
const handleCardClick = (): void => {
  if (!props.disabled) {
    emit('click', props.template)
  }
}

/**
 * Handle use button click
 */
const handleUse = (): void => {
  emit('use', props.template)
}

/**
 * Handle edit button click
 */
const handleEdit = (): void => {
  emit('edit', props.template)
}

/**
 * Handle delete button click
 */
const handleDelete = (): void => {
  emit('delete', props.template)
}
</script>

<style scoped>
.template-card {
  background-color: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  transition: all var(--duration-normal) var(--ease-in-out);
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  height: 100%;
}

.template-card--hover:hover {
  border-color: var(--color-primary);
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.template-card__header {
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
}

.template-card__icon {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  background-color: var(--color-primary-light);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.template-card__icon i {
  font-size: 20px;
  color: var(--color-primary);
}

.template-card__title-section {
  flex: 1;
  min-width: 0;
}

.template-card__title {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--color-text-primary);
  margin: 0 0 var(--space-1) 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.template-card__category {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
}

.template-card__description {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  line-height: var(--leading-relaxed);
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  flex: 1;
}

.template-card__metadata {
  display: flex;
  gap: var(--space-4);
  flex-wrap: wrap;
}

.template-card__meta-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
}

.template-card__meta-item i {
  font-size: 14px;
}

.template-card__keywords {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
}

.template-card__actions {
  display: flex;
  gap: var(--space-2);
  padding-top: var(--space-2);
  border-top: 1px solid var(--color-border);
}

.template-card__actions .el-button {
  flex: 1;
}

.template-card__footer {
  display: flex;
  justify-content: flex-end;
  padding-top: var(--space-2);
  border-top: 1px solid var(--color-border);
}

.template-card__timestamp {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
}

/* Responsive */
@media (max-width: 768px) {
  .template-card {
    padding: var(--space-4);
  }

  .template-card__actions {
    flex-direction: column;
  }

  .template-card__actions .el-button {
    width: 100%;
  }
}
</style>
