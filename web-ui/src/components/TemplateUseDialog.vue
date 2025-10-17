<template>
  <el-dialog
    v-model="dialogVisible"
    :title="`使用模板：${template?.name || ''}`"
    width="800px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <div v-if="template" class="use-dialog">
      <!-- Template Info -->
      <div class="use-dialog__info">
        <h4 class="use-dialog__section-title">模板信息</h4>
        <p class="use-dialog__description">{{ template.description }}</p>
        <div class="use-dialog__meta">
          <el-tag type="info" size="small">{{ getCategoryLabel(template.category) }}</el-tag>
          <span class="use-dialog__param-count">{{ template.parameters.length }} 个参数</span>
        </div>
      </div>

      <!-- Parameters Form -->
      <div v-if="template.parameters.length > 0" class="use-dialog__form">
        <h4 class="use-dialog__section-title">参数配置</h4>
        <el-form
          ref="formRef"
          :model="formData"
          :rules="formRules"
          label-position="top"
          @submit.prevent="handleGenerate"
        >
          <el-form-item
            v-for="param in template.parameters"
            :key="param.name"
            :label="getParamLabel(param)"
            :prop="param.name"
            :required="param.required"
          >
            <!-- String Input -->
            <el-input
              v-if="param.type === 'string'"
              v-model="formData[param.name]"
              :placeholder="param.description || `请输入${param.name}`"
              clearable
            />

            <!-- Number Input -->
            <el-input-number
              v-else-if="param.type === 'number'"
              v-model="formData[param.name]"
              :placeholder="param.description || `请输入${param.name}`"
              style="width: 100%"
            />

            <!-- Boolean Switch -->
            <el-switch
              v-else-if="param.type === 'boolean'"
              v-model="formData[param.name]"
            />

            <!-- Select Dropdown -->
            <el-select
              v-else-if="param.type === 'select'"
              v-model="formData[param.name]"
              :placeholder="param.description || `请选择${param.name}`"
              clearable
              style="width: 100%"
            >
              <el-option
                v-for="option in param.options"
                :key="option"
                :label="option"
                :value="option"
              />
            </el-select>

            <!-- Description -->
            <template v-if="param.description" #help>
              <span class="use-dialog__param-help">{{ param.description }}</span>
            </template>
          </el-form-item>
        </el-form>
      </div>

      <!-- Script Preview -->
      <div v-if="generatedScript" class="use-dialog__preview">
        <h4 class="use-dialog__section-title">脚本预览</h4>
        <CodeBlock
          :code="generatedScript"
          language="powershell"
          :copyable="true"
        />
      </div>

      <!-- No Parameters Message -->
      <div v-else-if="template.parameters.length === 0" class="use-dialog__no-params">
        <p>此模板不需要参数，可以直接生成脚本。</p>
      </div>
    </div>

    <!-- Actions -->
    <template #footer>
      <div class="use-dialog__footer">
        <el-button @click="handleCancel" :disabled="isGenerating">
          取消
        </el-button>
        <el-button
          v-if="!generatedScript"
          type="primary"
          @click="handleGenerate"
          :loading="isGenerating"
          :disabled="isGenerating"
        >
          <i v-if="!isGenerating" class="el-icon-document"></i>
          {{ isGenerating ? '生成中...' : '生成脚本' }}
        </el-button>
        <template v-else>
          <el-button
            @click="handleReset"
            :disabled="isExecuting"
          >
            <i class="el-icon-refresh"></i>
            重新配置
          </el-button>
          <el-button
            type="success"
            @click="handleExecute"
            :loading="isExecuting"
            :disabled="isExecuting"
          >
            <i v-if="!isExecuting" class="el-icon-video-play"></i>
            {{ isExecuting ? '执行中...' : '执行脚本' }}
          </el-button>
        </template>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, reactive } from 'vue'
import { 
  ElDialog, 
  ElForm, 
  ElFormItem, 
  ElInput, 
  ElInputNumber,
  ElSwitch,
  ElSelect,
  ElOption,
  ElButton, 
  ElTag,
  type FormInstance,
  type FormRules
} from 'element-plus'
import CodeBlock from './CodeBlock.vue'
import type { Template, TemplateParameter } from '../api/template'

// ============================================================================
// Props & Emits
// ============================================================================

interface Props {
  visible: boolean
  template: Template | null
  isGenerating?: boolean
  isExecuting?: boolean
}

interface Emits {
  (e: 'update:visible', value: boolean): void
  (e: 'generate', params: Record<string, any>): void
  (e: 'execute', script: string): void
  (e: 'cancel'): void
}

const props = withDefaults(defineProps<Props>(), {
  isGenerating: false,
  isExecuting: false
})

const emit = defineEmits<Emits>()

// ============================================================================
// State
// ============================================================================

const formRef = ref<FormInstance>()
const formData = reactive<Record<string, any>>({})
const generatedScript = ref('')

// ============================================================================
// Computed
// ============================================================================

const dialogVisible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})

const formRules = computed<FormRules>(() => {
  if (!props.template) return {}

  const rules: FormRules = {}
  props.template.parameters.forEach(param => {
    if (param.required) {
      rules[param.name] = [
        {
          required: true,
          message: `请输入${param.name}`,
          trigger: param.type === 'boolean' ? 'change' : 'blur'
        }
      ]
    }
  })
  return rules
})

// ============================================================================
// Watchers
// ============================================================================

watch(() => props.visible, (newValue) => {
  if (newValue && props.template) {
    // Initialize form data with default values
    initializeFormData()
    generatedScript.value = ''
  }
})

watch(() => props.template, (newTemplate) => {
  if (newTemplate) {
    initializeFormData()
  }
})

// ============================================================================
// Methods
// ============================================================================

/**
 * Initialize form data with default values
 */
const initializeFormData = (): void => {
  if (!props.template) return

  // Clear existing data
  Object.keys(formData).forEach(key => {
    delete formData[key]
  })

  // Set default values
  props.template.parameters.forEach(param => {
    if (param.default !== undefined) {
      formData[param.name] = param.default
    } else if (param.type === 'boolean') {
      formData[param.name] = false
    } else {
      formData[param.name] = ''
    }
  })
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
 * Get parameter label with required indicator
 */
const getParamLabel = (param: TemplateParameter): string => {
  return param.required ? `${param.name} *` : param.name
}

/**
 * Handle generate button click
 */
const handleGenerate = async (): Promise<void> => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    emit('generate', { ...formData })
  } catch (error) {
    console.error('Form validation failed:', error)
  }
}

/**
 * Handle execute button click
 */
const handleExecute = (): void => {
  if (generatedScript.value) {
    emit('execute', generatedScript.value)
  }
}

/**
 * Handle reset button click
 */
const handleReset = (): void => {
  generatedScript.value = ''
  initializeFormData()
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
  if (!props.isGenerating && !props.isExecuting) {
    handleCancel()
  }
}

/**
 * Set generated script (called from parent)
 */
const setGeneratedScript = (script: string): void => {
  generatedScript.value = script
}

// Expose methods for parent component
defineExpose({
  setGeneratedScript
})
</script>

<style scoped>
.use-dialog {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
}

.use-dialog__section-title {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--color-text-primary);
  margin: 0 0 var(--space-4) 0;
}

/* Info Section */
.use-dialog__info {
  background-color: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--space-4);
}

.use-dialog__description {
  font-size: var(--text-base);
  color: var(--color-text-secondary);
  line-height: var(--leading-relaxed);
  margin: 0 0 var(--space-3) 0;
}

.use-dialog__meta {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.use-dialog__param-count {
  font-size: var(--text-sm);
  color: var(--color-text-tertiary);
}

/* Form Section */
.use-dialog__form {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--space-4);
}

.use-dialog__param-help {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
}

/* Preview Section */
.use-dialog__preview {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--space-4);
}

/* No Parameters */
.use-dialog__no-params {
  text-align: center;
  padding: var(--space-8);
  background-color: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
}

.use-dialog__no-params p {
  font-size: var(--text-base);
  color: var(--color-text-secondary);
  margin: 0;
}

/* Footer */
.use-dialog__footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
}

/* Responsive */
@media (max-width: 768px) {
  :deep(.el-dialog) {
    width: 95% !important;
  }

  .use-dialog__footer {
    flex-direction: column-reverse;
  }

  .use-dialog__footer .el-button {
    width: 100%;
  }
}
</style>
