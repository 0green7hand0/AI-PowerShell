<!--
  ExecutionSettingsForm Component
  
  Form for configuring execution engine settings including timeout,
  shell type, encoding, and working directory.
  
  Requirements: 8.2, 8.3
-->

<template>
  <div class="execution-settings-form">
    <el-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-width="160px"
      label-position="left"
      @submit.prevent
    >
      <!-- Timeout -->
      <el-form-item label="超时时间 (秒)" prop="timeout">
        <div class="slider-container">
          <el-slider
            v-model="formData.timeout"
            :min="5"
            :max="300"
            :step="5"
            :show-tooltip="true"
            :format-tooltip="formatTimeoutTooltip"
            @change="handleChange"
          />
          <el-input-number
            v-model="formData.timeout"
            :min="5"
            :max="300"
            :step="5"
            controls-position="right"
            class="slider-input"
            @change="handleChange"
          />
        </div>
        <template #extra>
          <span class="form-item-help">
            命令执行的最大等待时间。超时后命令将被终止
          </span>
        </template>
      </el-form-item>

      <!-- Shell Type -->
      <el-form-item label="Shell 类型" prop="shellType">
        <el-select
          v-model="formData.shellType"
          placeholder="选择 Shell 类型"
          @change="handleChange"
        >
          <el-option label="PowerShell" value="powershell">
            <div class="shell-option">
              <span class="shell-option__name">PowerShell</span>
              <span class="shell-option__desc">Windows PowerShell 5.1</span>
            </div>
          </el-option>
          <el-option label="PowerShell Core" value="pwsh">
            <div class="shell-option">
              <span class="shell-option__name">PowerShell Core</span>
              <span class="shell-option__desc">跨平台 PowerShell 7+</span>
            </div>
          </el-option>
          <el-option label="CMD" value="cmd">
            <div class="shell-option">
              <span class="shell-option__name">CMD</span>
              <span class="shell-option__desc">Windows 命令提示符</span>
            </div>
          </el-option>
          <el-option label="Bash" value="bash">
            <div class="shell-option">
              <span class="shell-option__name">Bash</span>
              <span class="shell-option__desc">Linux/macOS Shell</span>
            </div>
          </el-option>
        </el-select>
        <template #extra>
          <span class="form-item-help">
            用于执行命令的 Shell 环境。建议使用 PowerShell 或 PowerShell Core
          </span>
        </template>
      </el-form-item>

      <!-- Encoding -->
      <el-form-item label="字符编码" prop="encoding">
        <el-select
          v-model="formData.encoding"
          placeholder="选择字符编码"
          @change="handleChange"
        >
          <el-option label="UTF-8" value="utf-8" />
          <el-option label="UTF-16" value="utf-16" />
          <el-option label="GBK (简体中文)" value="gbk" />
          <el-option label="GB2312 (简体中文)" value="gb2312" />
          <el-option label="Big5 (繁体中文)" value="big5" />
          <el-option label="ASCII" value="ascii" />
          <el-option label="ISO-8859-1" value="iso-8859-1" />
        </el-select>
        <template #extra>
          <span class="form-item-help">
            命令输出的字符编码。中文 Windows 系统建议使用 GBK
          </span>
        </template>
      </el-form-item>

      <!-- Working Directory -->
      <el-form-item label="工作目录" prop="workingDirectory">
        <el-input
          v-model="formData.workingDirectory"
          placeholder="例如: C:\Users\YourName\Documents"
          @input="handleChange"
        >
          <template #prepend>
            <el-icon><Folder /></el-icon>
          </template>
        </el-input>
        <template #extra>
          <span class="form-item-help">
            可选。命令执行的默认工作目录。留空则使用当前目录
          </span>
        </template>
      </el-form-item>

      <!-- Platform Detection -->
      <el-alert
        type="info"
        :closable="false"
        show-icon
        class="execution-settings-form__info"
      >
        <template #title>
          系统信息
        </template>
        <template #default>
          <div class="system-info">
            <div class="system-info__item">
              <span class="system-info__label">操作系统：</span>
              <span class="system-info__value">{{ detectedPlatform }}</span>
            </div>
            <div class="system-info__item">
              <span class="system-info__label">推荐 Shell：</span>
              <span class="system-info__value">{{ recommendedShell }}</span>
            </div>
            <div class="system-info__item">
              <span class="system-info__label">推荐编码：</span>
              <span class="system-info__value">{{ recommendedEncoding }}</span>
            </div>
          </div>
          <el-button
            type="primary"
            size="small"
            @click="applyRecommended"
            class="apply-recommended-btn"
          >
            应用推荐配置
          </el-button>
        </template>
      </el-alert>

      <!-- Performance Tips -->
      <el-alert
        type="success"
        :closable="false"
        show-icon
        class="execution-settings-form__tips"
      >
        <template #title>
          性能建议
        </template>
        <template #default>
          <ul class="tips-list">
            <li>对于快速命令，使用较短的超时时间（10-30秒）</li>
            <li>对于长时间运行的脚本，增加超时时间（60-300秒）</li>
            <li>PowerShell Core (pwsh) 通常比 PowerShell 5.1 更快</li>
            <li>正确的字符编码可以避免中文乱码问题</li>
          </ul>
        </template>
      </el-alert>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Folder } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import type { ExecutionConfig } from '../api/config'
import { ElMessage } from 'element-plus'

// ============================================================================
// Props & Emits
// ============================================================================

const props = defineProps<{
  modelValue: ExecutionConfig
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: ExecutionConfig): void
  (e: 'change'): void
}>()

// ============================================================================
// State
// ============================================================================

const formRef = ref<FormInstance>()
const formData = ref<ExecutionConfig>({ ...props.modelValue })

// ============================================================================
// Validation Rules
// ============================================================================

const rules: FormRules = {
  timeout: [
    { required: true, message: '请设置超时时间', trigger: 'change' },
    { type: 'number', min: 5, max: 300, message: '超时时间应在 5-300 秒之间', trigger: 'change' }
  ],
  shellType: [
    { required: true, message: '请选择 Shell 类型', trigger: 'change' }
  ],
  encoding: [
    { required: true, message: '请选择字符编码', trigger: 'change' }
  ],
  workingDirectory: [
    { max: 500, message: '工作目录路径不能超过 500 个字符', trigger: 'blur' }
  ]
}

// ============================================================================
// Computed
// ============================================================================

/**
 * Detect platform
 */
const detectedPlatform = computed(() => {
  const platform = navigator.platform.toLowerCase()
  if (platform.includes('win')) return 'Windows'
  if (platform.includes('mac')) return 'macOS'
  if (platform.includes('linux')) return 'Linux'
  return '未知'
})

/**
 * Get recommended shell based on platform
 */
const recommendedShell = computed(() => {
  const platform = detectedPlatform.value
  if (platform === 'Windows') return 'pwsh (PowerShell Core)'
  if (platform === 'macOS' || platform === 'Linux') return 'bash'
  return 'powershell'
})

/**
 * Get recommended encoding based on platform
 */
const recommendedEncoding = computed(() => {
  const platform = detectedPlatform.value
  const lang = navigator.language.toLowerCase()
  
  if (platform === 'Windows' && lang.includes('zh')) {
    return 'gbk'
  }
  return 'utf-8'
})

// ============================================================================
// Methods
// ============================================================================

/**
 * Format timeout tooltip
 */
const formatTimeoutTooltip = (value: number): string => {
  if (value < 30) return `${value}秒 (快速命令)`
  if (value < 60) return `${value}秒 (普通命令)`
  if (value < 120) return `${value}秒 (长时间命令)`
  return `${value}秒 (非常长的命令)`
}

/**
 * Apply recommended configuration
 */
const applyRecommended = () => {
  const platform = detectedPlatform.value
  
  if (platform === 'Windows') {
    formData.value.shellType = 'pwsh'
    formData.value.encoding = navigator.language.toLowerCase().includes('zh') ? 'gbk' : 'utf-8'
  } else if (platform === 'macOS' || platform === 'Linux') {
    formData.value.shellType = 'bash'
    formData.value.encoding = 'utf-8'
  }
  
  handleChange()
  ElMessage.success('已应用推荐配置')
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
.execution-settings-form {
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

.shell-option {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.shell-option__name {
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.shell-option__desc {
  font-size: 0.75rem;
  color: var(--el-text-color-secondary);
}

.execution-settings-form__info {
  margin-top: 1.5rem;
}

.execution-settings-form__tips {
  margin-top: 1rem;
}

.system-info {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin: 0.5rem 0 1rem 0;
}

.system-info__item {
  display: flex;
  gap: 0.5rem;
}

.system-info__label {
  font-weight: 500;
  color: var(--el-text-color-secondary);
  min-width: 100px;
}

.system-info__value {
  color: var(--el-text-color-primary);
}

.apply-recommended-btn {
  margin-top: 0.5rem;
}

.tips-list {
  margin: 0.5rem 0 0 0;
  padding-left: 1.5rem;
  list-style: disc;
}

.tips-list li {
  margin: 0.5rem 0;
  color: var(--el-text-color-regular);
  line-height: 1.6;
}

/* Form Item Extra Styling */
.execution-settings-form :deep(.el-form-item__extra) {
  margin-top: 0.5rem;
}

/* Responsive */
@media (max-width: 768px) {
  .execution-settings-form :deep(.el-form-item) {
    flex-direction: column;
  }

  .execution-settings-form :deep(.el-form-item__label) {
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

  .system-info__item {
    flex-direction: column;
    gap: 0.25rem;
  }

  .system-info__label {
    min-width: auto;
  }
}
</style>
