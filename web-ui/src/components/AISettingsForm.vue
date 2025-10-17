<!--
  AISettingsForm Component
  
  Form for configuring AI engine settings including provider,
  model name, temperature, and max tokens.
  
  Requirements: 8.2, 8.3
-->

<template>
  <div class="ai-settings-form">
    <el-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-width="140px"
      label-position="left"
      @submit.prevent
    >
      <!-- Provider -->
      <el-form-item label="AI 提供商" prop="provider">
        <el-select
          v-model="formData.provider"
          placeholder="选择 AI 提供商"
          @change="handleChange"
        >
          <el-option label="本地模型 (Local)" value="local" />
          <el-option label="Ollama" value="ollama" />
          <el-option label="OpenAI" value="openai" />
          <el-option label="Azure OpenAI" value="azure" />
          <el-option label="Claude" value="claude" />
          <el-option label="Google Gemini" value="gemini" />
        </el-select>
        <template #extra>
          <span class="form-item-help">
            选择用于命令翻译的 AI 服务提供商
          </span>
        </template>
      </el-form-item>

      <!-- Model Name -->
      <el-form-item label="模型名称" prop="modelName">
        <el-input
          v-model="formData.modelName"
          placeholder="例如: gpt-4, gpt-3.5-turbo"
          @input="handleChange"
        />
        <template #extra>
          <span class="form-item-help">
            使用的具体模型名称，不同提供商支持的模型不同
          </span>
        </template>
      </el-form-item>

      <!-- Temperature -->
      <el-form-item label="温度 (Temperature)" prop="temperature">
        <div class="slider-container">
          <el-slider
            v-model="formData.temperature"
            :min="0"
            :max="2"
            :step="0.1"
            :show-tooltip="true"
            :format-tooltip="formatTemperatureTooltip"
            @change="handleChange"
          />
          <el-input-number
            v-model="formData.temperature"
            :min="0"
            :max="2"
            :step="0.1"
            :precision="1"
            controls-position="right"
            class="slider-input"
            @change="handleChange"
          />
        </div>
        <template #extra>
          <span class="form-item-help">
            控制输出的随机性。较低的值（0.0-0.5）使输出更确定，较高的值（0.5-2.0）使输出更有创造性
          </span>
        </template>
      </el-form-item>

      <!-- Max Tokens -->
      <el-form-item label="最大令牌数" prop="maxTokens">
        <div class="slider-container">
          <el-slider
            v-model="formData.maxTokens"
            :min="100"
            :max="8000"
            :step="100"
            :show-tooltip="true"
            :format-tooltip="formatTokensTooltip"
            @change="handleChange"
          />
          <el-input-number
            v-model="formData.maxTokens"
            :min="100"
            :max="8000"
            :step="100"
            controls-position="right"
            class="slider-input"
            @change="handleChange"
          />
        </div>
        <template #extra>
          <span class="form-item-help">
            生成响应的最大令牌数。较大的值允许更长的响应，但会增加成本
          </span>
        </template>
      </el-form-item>

      <!-- API Key (Optional) -->
      <el-form-item label="API 密钥" prop="apiKey">
        <el-input
          v-model="formData.apiKey"
          type="password"
          placeholder="可选：输入 API 密钥"
          show-password
          @input="handleChange"
        />
        <template #extra>
          <span class="form-item-help">
            可选。如果未设置，将使用环境变量中的密钥
          </span>
        </template>
      </el-form-item>

      <!-- Info Card -->
      <el-alert
        type="info"
        :closable="false"
        show-icon
        class="ai-settings-form__info"
      >
        <template #title>
          推荐配置
        </template>
        <template #default>
          <ul class="ai-settings-form__recommendations">
            <li><strong>快速响应：</strong> gpt-3.5-turbo, Temperature: 0.3, Max Tokens: 1000</li>
            <li><strong>平衡模式：</strong> gpt-4, Temperature: 0.5, Max Tokens: 2000</li>
            <li><strong>创造性：</strong> gpt-4, Temperature: 0.8, Max Tokens: 3000</li>
            <li><strong>本地部署：</strong> Ollama + llama2, Temperature: 0.5, Max Tokens: 2000</li>
          </ul>
        </template>
      </el-alert>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import type { AIConfig } from '../api/config'

// ============================================================================
// Props & Emits
// ============================================================================

const props = defineProps<{
  modelValue: AIConfig
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: AIConfig): void
  (e: 'change'): void
}>()

// ============================================================================
// State
// ============================================================================

const formRef = ref<FormInstance>()
const formData = ref<AIConfig>({ ...props.modelValue })

// ============================================================================
// Validation Rules
// ============================================================================

const rules: FormRules = {
  provider: [
    { required: true, message: '请选择 AI 提供商', trigger: 'change' }
  ],
  modelName: [
    { required: true, message: '请输入模型名称', trigger: 'blur' },
    { min: 2, max: 100, message: '模型名称长度应在 2-100 个字符之间', trigger: 'blur' }
  ],
  temperature: [
    { required: true, message: '请设置温度值', trigger: 'change' },
    { type: 'number', min: 0, max: 2, message: '温度值应在 0-2 之间', trigger: 'change' }
  ],
  maxTokens: [
    { required: true, message: '请设置最大令牌数', trigger: 'change' },
    { type: 'number', min: 100, max: 8000, message: '最大令牌数应在 100-8000 之间', trigger: 'change' }
  ],
  apiKey: [
    { min: 0, max: 500, message: 'API 密钥长度不能超过 500 个字符', trigger: 'blur' }
  ]
}

// ============================================================================
// Methods
// ============================================================================

/**
 * Format temperature tooltip
 */
const formatTemperatureTooltip = (value: number): string => {
  if (value < 0.3) return `${value} (非常确定)`
  if (value < 0.7) return `${value} (平衡)`
  if (value < 1.2) return `${value} (创造性)`
  return `${value} (非常创造性)`
}

/**
 * Format tokens tooltip
 */
const formatTokensTooltip = (value: number): string => {
  return `${value} tokens (~${Math.round(value * 0.75)} 字)`
}

/**
 * Handle form change
 */
const handleChange = () => {
  emit('update:modelValue', formData.value)
  emit('change')
}

/**
 * Validate form
 */
const validate = async (): Promise<boolean> => {
  if (!formRef.value) return false
  
  try {
    await formRef.value.validate()
    return true
  } catch (error) {
    return false
  }
}

// ============================================================================
// Watchers
// ============================================================================

watch(
  () => props.modelValue,
  (newValue) => {
    formData.value = { ...newValue }
  },
  { deep: true }
)

// ============================================================================
// Expose
// ============================================================================

defineExpose({
  validate
})
</script>

<style scoped>
.ai-settings-form {
  max-width: 800px;
}

.slider-container {
  display: flex;
  align-items: center;
  gap: 1rem;
  width: 100%;
}

.slider-container :deep(.el-slider) {
  flex: 1;
}

.slider-input {
  width: 120px;
  flex-shrink: 0;
}

.form-item-help {
  font-size: 0.875rem;
  color: var(--el-text-color-secondary);
  line-height: 1.5;
}

.ai-settings-form__info {
  margin-top: 1.5rem;
}

.ai-settings-form__recommendations {
  margin: 0.5rem 0 0 0;
  padding-left: 1.5rem;
  list-style: disc;
}

.ai-settings-form__recommendations li {
  margin: 0.5rem 0;
  color: var(--el-text-color-regular);
  line-height: 1.6;
}

.ai-settings-form__recommendations strong {
  color: var(--el-text-color-primary);
}

/* Form Item Extra Styling */
.ai-settings-form :deep(.el-form-item__extra) {
  margin-top: 0.5rem;
}

/* Responsive */
@media (max-width: 768px) {
  .ai-settings-form :deep(.el-form-item) {
    flex-direction: column;
  }

  .ai-settings-form :deep(.el-form-item__label) {
    text-align: left;
    margin-bottom: 0.5rem;
  }

  .slider-container {
    flex-direction: column;
    align-items: stretch;
  }

  .slider-input {
    width: 100%;
  }
}
</style>
