<template>
  <div class="input-box">
    <div class="input-wrapper">
      <!-- Textarea -->
      <el-input
        v-model="inputValue"
        type="textarea"
        :placeholder="placeholder"
        :maxlength="maxLength"
        :disabled="disabled"
        :autosize="{ minRows: 1, maxRows: 6 }"
        resize="none"
        class="input-textarea"
        @keydown="handleKeyDown"
      />

      <!-- Character Count -->
      <div v-if="showCount" class="char-count">
        {{ inputValue.length }}{{ maxLength ? ` / ${maxLength}` : '' }}
      </div>
    </div>

    <!-- Action Bar -->
    <div class="action-bar">
      <div class="action-left">
        <el-tooltip content="快捷键：Enter 发送，Shift+Enter 换行" placement="top">
          <el-icon class="hint-icon"><QuestionFilled /></el-icon>
        </el-tooltip>
      </div>

      <div class="action-right">
        <el-button
          v-if="inputValue.length > 0"
          text
          size="small"
          @click="handleClear"
        >
          清空
        </el-button>

        <el-button
          type="primary"
          size="default"
          :disabled="!canSubmit"
          :loading="loading"
          @click="handleSubmit"
          class="send-button"
        >
          <el-icon v-if="!loading"><Promotion /></el-icon>
          {{ loading ? '发送中...' : '发送' }}
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { QuestionFilled, Promotion } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { isValidCommandInput, sanitizeInput } from '@/utils/validation'

/**
 * InputBox - Multi-line input component for chat
 * 
 * Supports multi-line text input with character count,
 * keyboard shortcuts (Enter to send, Shift+Enter for newline),
 * and loading state.
 * 
 * Requirements: 2.2, 2.3, 2.4, 7.2
 */

interface Props {
  modelValue?: string
  placeholder?: string
  maxLength?: number
  loading?: boolean
  disabled?: boolean
  showCount?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  placeholder: '输入中文描述，AI 将帮您生成 PowerShell 命令...',
  maxLength: 2000,
  loading: false,
  disabled: false,
  showCount: true
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'submit', value: string): void
}>()

const inputValue = ref(props.modelValue)

/**
 * Check if can submit
 */
const canSubmit = computed(() => {
  return inputValue.value.trim().length > 0 && !props.loading && !props.disabled
})

/**
 * Handle keyboard shortcuts
 * Requirements: 2.4
 */
const handleKeyDown = (event: KeyboardEvent) => {
  // Enter without Shift: Submit
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    if (canSubmit.value) {
      handleSubmit()
    }
  }
  // Shift+Enter: New line (default behavior, no need to handle)
}

/**
 * Handle submit with validation
 * Requirements: 7.2
 */
const handleSubmit = () => {
  if (!canSubmit.value) return
  
  const trimmedValue = inputValue.value.trim()
  
  // Validate input
  const validation = isValidCommandInput(trimmedValue)
  if (!validation.valid) {
    ElMessage.error(validation.reason || '输入包含无效内容')
    return
  }
  
  // Sanitize input
  const sanitizedValue = sanitizeInput(trimmedValue)
  
  emit('submit', sanitizedValue)
  inputValue.value = ''
}

/**
 * Handle clear
 */
const handleClear = () => {
  inputValue.value = ''
  emit('update:modelValue', '')
}

/**
 * Watch for external changes to modelValue
 */
watch(() => props.modelValue, (newValue) => {
  inputValue.value = newValue
})

/**
 * Emit updates to parent
 */
watch(inputValue, (newValue) => {
  emit('update:modelValue', newValue)
})
</script>

<style scoped>
.input-box {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  background-color: var(--color-bg-primary);
}

.input-wrapper {
  position: relative;
}

.input-textarea {
  width: 100%;
}

.input-textarea :deep(.el-textarea__inner) {
  padding: var(--space-3) var(--space-4);
  padding-right: 60px; /* Space for char count */
  font-size: var(--text-base);
  line-height: var(--leading-normal);
  border-radius: var(--radius-lg);
  border: 2px solid var(--color-border);
  background-color: var(--color-bg-secondary);
  color: var(--color-text-primary);
  transition: all var(--duration-fast) var(--ease-in-out);
}

.input-textarea :deep(.el-textarea__inner):focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-light);
}

.input-textarea :deep(.el-textarea__inner):disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Character Count */
.char-count {
  position: absolute;
  right: var(--space-3);
  bottom: var(--space-2);
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
  pointer-events: none;
}

/* Action Bar */
.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.action-left {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.hint-icon {
  color: var(--color-text-tertiary);
  font-size: 16px;
  cursor: help;
  transition: color var(--duration-fast) var(--ease-in-out);
}

.hint-icon:hover {
  color: var(--color-text-secondary);
}

.action-right {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.send-button {
  min-width: 100px;
}

/* Responsive */
@media (max-width: 768px) {
  .input-textarea :deep(.el-textarea__inner) {
    padding: var(--space-2) var(--space-3);
    padding-right: 50px;
    font-size: var(--text-sm);
  }

  .char-count {
    right: var(--space-2);
    bottom: var(--space-1);
    font-size: 0.625rem;
  }

  .action-bar {
    flex-wrap: wrap;
    gap: var(--space-2);
  }

  .action-left {
    order: 2;
    width: 100%;
  }

  .action-right {
    order: 1;
    width: 100%;
  }

  .send-button {
    width: 100%;
    min-width: auto;
  }

  .hint-text {
    font-size: var(--text-xs);
  }
}

@media (max-width: 480px) {
  .input-textarea :deep(.el-textarea__inner) {
    padding: var(--space-2);
    padding-right: 45px;
    font-size: var(--text-sm);
    min-height: 80px;
  }

  .send-button {
    padding: var(--space-3) var(--space-4);
    font-size: var(--text-base);
    height: 44px; /* Touch-friendly size */
  }
}
</style>
