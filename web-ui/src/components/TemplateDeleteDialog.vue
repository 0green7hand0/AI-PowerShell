<template>
  <el-dialog
    v-model="dialogVisible"
    title="删除模板"
    width="500px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <!-- Warning Icon -->
    <div class="delete-dialog__icon">
      <i class="el-icon-warning"></i>
    </div>

    <!-- Warning Message -->
    <div class="delete-dialog__content">
      <h3 class="delete-dialog__title">确认删除模板？</h3>
      <p class="delete-dialog__message">
        您即将删除模板 <strong>{{ template?.name }}</strong>。
        此操作无法撤销，请谨慎操作。
      </p>

      <!-- Template Info -->
      <div v-if="template" class="delete-dialog__info">
        <div class="delete-dialog__info-item">
          <span class="delete-dialog__info-label">模板名称：</span>
          <span class="delete-dialog__info-value">{{ template.name }}</span>
        </div>
        <div class="delete-dialog__info-item">
          <span class="delete-dialog__info-label">分类：</span>
          <span class="delete-dialog__info-value">{{ getCategoryLabel(template.category) }}</span>
        </div>
        <div class="delete-dialog__info-item">
          <span class="delete-dialog__info-label">参数数量：</span>
          <span class="delete-dialog__info-value">{{ template.parameters.length }} 个</span>
        </div>
      </div>

      <!-- Confirmation Input -->
      <div class="delete-dialog__confirmation">
        <p class="delete-dialog__confirmation-label">
          请输入模板名称 <code>{{ template?.name }}</code> 以确认删除：
        </p>
        <el-input
          v-model="confirmationInput"
          placeholder="输入模板名称"
          clearable
          @keyup.enter="handleConfirm"
        />
        <p v-if="showError" class="delete-dialog__error">
          模板名称不匹配，请重新输入
        </p>
      </div>
    </div>

    <!-- Actions -->
    <template #footer>
      <div class="delete-dialog__footer">
        <el-button @click="handleCancel" :disabled="isDeleting">
          取消
        </el-button>
        <el-button
          type="danger"
          @click="handleConfirm"
          :disabled="!isConfirmationValid || isDeleting"
          :loading="isDeleting"
        >
          <i v-if="!isDeleting" class="el-icon-delete"></i>
          {{ isDeleting ? '删除中...' : '确认删除' }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElDialog, ElInput, ElButton } from 'element-plus'
import type { Template } from '../api/template'

// ============================================================================
// Props & Emits
// ============================================================================

interface Props {
  visible: boolean
  template: Template | null
  isDeleting?: boolean
}

interface Emits {
  (e: 'update:visible', value: boolean): void
  (e: 'confirm', template: Template): void
  (e: 'cancel'): void
}

const props = withDefaults(defineProps<Props>(), {
  isDeleting: false
})

const emit = defineEmits<Emits>()

// ============================================================================
// State
// ============================================================================

const confirmationInput = ref('')
const showError = ref(false)

// ============================================================================
// Computed
// ============================================================================

const dialogVisible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})

const isConfirmationValid = computed(() => {
  return confirmationInput.value === props.template?.name
})

// ============================================================================
// Watchers
// ============================================================================

watch(() => props.visible, (newValue) => {
  if (newValue) {
    // Reset state when dialog opens
    confirmationInput.value = ''
    showError.value = false
  }
})

watch(confirmationInput, () => {
  // Hide error when user types
  if (showError.value) {
    showError.value = false
  }
})

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
 * Handle confirm button click
 */
const handleConfirm = (): void => {
  if (!isConfirmationValid.value) {
    showError.value = true
    return
  }

  if (props.template) {
    emit('confirm', props.template)
  }
}

/**
 * Handle cancel button click
 */
const handleCancel = (): void => {
  emit('cancel')
  emit('update:visible', false)
}

/**
 * Handle dialog close
 */
const handleClose = (): void => {
  if (!props.isDeleting) {
    handleCancel()
  }
}
</script>

<style scoped>
.delete-dialog__icon {
  display: flex;
  justify-content: center;
  margin-bottom: var(--space-4);
}

.delete-dialog__icon i {
  font-size: 64px;
  color: var(--color-danger);
}

.delete-dialog__content {
  text-align: center;
}

.delete-dialog__title {
  font-size: var(--text-xl);
  font-weight: var(--font-semibold);
  color: var(--color-text-primary);
  margin: 0 0 var(--space-3) 0;
}

.delete-dialog__message {
  font-size: var(--text-base);
  color: var(--color-text-secondary);
  line-height: var(--leading-relaxed);
  margin: 0 0 var(--space-6) 0;
}

.delete-dialog__message strong {
  color: var(--color-text-primary);
  font-weight: var(--font-semibold);
}

.delete-dialog__info {
  background-color: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--space-4);
  margin-bottom: var(--space-6);
  text-align: left;
}

.delete-dialog__info-item {
  display: flex;
  justify-content: space-between;
  padding: var(--space-2) 0;
}

.delete-dialog__info-item:not(:last-child) {
  border-bottom: 1px solid var(--color-border);
}

.delete-dialog__info-label {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
}

.delete-dialog__info-value {
  font-size: var(--text-sm);
  color: var(--color-text-primary);
  font-weight: var(--font-medium);
}

.delete-dialog__confirmation {
  text-align: left;
}

.delete-dialog__confirmation-label {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  margin: 0 0 var(--space-3) 0;
}

.delete-dialog__confirmation-label code {
  background-color: var(--color-bg-tertiary);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
  font-family: var(--font-mono);
  color: var(--color-text-primary);
  font-weight: var(--font-semibold);
}

.delete-dialog__error {
  font-size: var(--text-sm);
  color: var(--color-danger);
  margin: var(--space-2) 0 0 0;
}

.delete-dialog__footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
}

/* Responsive */
@media (max-width: 768px) {
  :deep(.el-dialog) {
    width: 90% !important;
  }

  .delete-dialog__icon i {
    font-size: 48px;
  }

  .delete-dialog__footer {
    flex-direction: column-reverse;
  }

  .delete-dialog__footer .el-button {
    width: 100%;
  }
}
</style>
