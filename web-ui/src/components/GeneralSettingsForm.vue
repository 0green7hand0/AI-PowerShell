<!--
  GeneralSettingsForm Component
  
  Form for configuring general application settings including language,
  theme, log level, and auto-save.
  
  Requirements: 8.2, 8.3
-->

<template>
  <div class="general-settings-form">
    <el-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-width="140px"
      label-position="left"
      @submit.prevent
    >
      <!-- Language -->
      <el-form-item label="界面语言" prop="language">
        <el-select v-model="formData.language" placeholder="选择界面语言" @change="handleChange">
          <el-option label="简体中文" value="zh-CN">
            <div class="language-option">
              <span class="language-option__flag">🇨🇳</span>
              <span class="language-option__name">简体中文</span>
            </div>
          </el-option>
          <el-option label="繁体中文" value="zh-TW">
            <div class="language-option">
              <span class="language-option__flag">🇹🇼</span>
              <span class="language-option__name">繁体中文</span>
            </div>
          </el-option>
          <el-option label="English" value="en-US">
            <div class="language-option">
              <span class="language-option__flag">🇺🇸</span>
              <span class="language-option__name">English</span>
            </div>
          </el-option>
          <el-option label="日本語" value="ja-JP">
            <div class="language-option">
              <span class="language-option__flag">🇯🇵</span>
              <span class="language-option__name">日本語</span>
            </div>
          </el-option>
        </el-select>
        <template #extra>
          <span class="form-item-help"> 更改界面显示语言。需要刷新页面生效 </span>
        </template>
      </el-form-item>

      <!-- Theme -->
      <el-form-item label="主题" prop="theme">
        <el-radio-group v-model="formData.theme" @change="handleThemeChange">
          <el-radio-button label="light">
            <el-icon><Sunny /></el-icon>
            浅色
          </el-radio-button>
          <el-radio-button label="dark">
            <el-icon><Moon /></el-icon>
            深色
          </el-radio-button>
        </el-radio-group>
        <template #extra>
          <span class="form-item-help"> 选择界面主题。更改后立即生效 </span>
        </template>
      </el-form-item>

      <!-- Theme Preview -->
      <el-form-item label="主题预览">
        <div class="theme-preview">
          <div
            class="theme-preview__card"
            :class="{ 'theme-preview__card--active': formData.theme === 'light' }"
            @click="selectTheme('light')"
          >
            <div class="theme-preview__header theme-preview__header--light">
              <div class="theme-preview__dot" />
              <div class="theme-preview__dot" />
              <div class="theme-preview__dot" />
            </div>
            <div class="theme-preview__body theme-preview__body--light">
              <div class="theme-preview__line" />
              <div class="theme-preview__line" />
              <div class="theme-preview__line theme-preview__line--short" />
            </div>
            <div class="theme-preview__label">浅色主题</div>
          </div>

          <div
            class="theme-preview__card"
            :class="{ 'theme-preview__card--active': formData.theme === 'dark' }"
            @click="selectTheme('dark')"
          >
            <div class="theme-preview__header theme-preview__header--dark">
              <div class="theme-preview__dot" />
              <div class="theme-preview__dot" />
              <div class="theme-preview__dot" />
            </div>
            <div class="theme-preview__body theme-preview__body--dark">
              <div class="theme-preview__line" />
              <div class="theme-preview__line" />
              <div class="theme-preview__line theme-preview__line--short" />
            </div>
            <div class="theme-preview__label">深色主题</div>
          </div>
        </div>
      </el-form-item>

      <!-- Log Level -->
      <el-form-item label="日志级别" prop="logLevel">
        <el-select v-model="formData.logLevel" placeholder="选择日志级别" @change="handleChange">
          <el-option label="DEBUG - 调试" value="DEBUG">
            <div class="log-level-option">
              <el-tag type="info" size="small"> DEBUG </el-tag>
              <span class="log-level-option__desc">显示所有日志，包括调试信息</span>
            </div>
          </el-option>
          <el-option label="INFO - 信息" value="INFO">
            <div class="log-level-option">
              <el-tag type="success" size="small"> INFO </el-tag>
              <span class="log-level-option__desc">显示一般信息和更高级别的日志</span>
            </div>
          </el-option>
          <el-option label="WARNING - 警告" value="WARNING">
            <div class="log-level-option">
              <el-tag type="warning" size="small"> WARNING </el-tag>
              <span class="log-level-option__desc">只显示警告和错误日志</span>
            </div>
          </el-option>
          <el-option label="ERROR - 错误" value="ERROR">
            <div class="log-level-option">
              <el-tag type="danger" size="small"> ERROR </el-tag>
              <span class="log-level-option__desc">只显示错误日志</span>
            </div>
          </el-option>
        </el-select>
        <template #extra>
          <span class="form-item-help">
            控制日志的详细程度。开发时建议使用 DEBUG，生产环境建议使用 INFO 或 WARNING
          </span>
        </template>
      </el-form-item>

      <!-- Auto Save -->
      <el-form-item label="自动保存" prop="autoSave">
        <el-switch
          v-model="formData.autoSave"
          active-text="启用"
          inactive-text="禁用"
          @change="handleChange"
        />
        <template #extra>
          <span class="form-item-help"> 启用后，配置更改将自动保存，无需手动点击保存按钮 </span>
        </template>
      </el-form-item>

      <!-- Additional Settings Info -->
      <el-alert type="info" :closable="false" show-icon class="general-settings-form__info">
        <template #title> 其他设置 </template>
        <template #default>
          <ul class="info-list">
            <li>
              <strong>快捷键：</strong>
              <ul class="shortcut-list">
                <li><kbd>Ctrl</kbd> + <kbd>Enter</kbd> - 发送消息</li>
                <li><kbd>Ctrl</kbd> + <kbd>K</kbd> - 聚焦搜索</li>
                <li><kbd>Ctrl</kbd> + <kbd>,</kbd> - 打开设置</li>
                <li><kbd>Esc</kbd> - 关闭对话框</li>
              </ul>
            </li>
            <li><strong>数据存储：</strong> 所有数据存储在本地，不会上传到服务器</li>
            <li><strong>隐私保护：</strong> 命令历史和配置仅保存在您的设备上</li>
          </ul>
        </template>
      </el-alert>

      <!-- Performance Info -->
      <el-alert
        v-if="formData.logLevel === 'DEBUG'"
        type="warning"
        :closable="false"
        show-icon
        class="general-settings-form__warning"
      >
        <template #title> 性能提示 </template>
        <template #default>
          DEBUG 日志级别会记录大量信息，可能影响性能。建议仅在开发或调试时使用。
        </template>
      </el-alert>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { Sunny, Moon } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import type { GeneralConfig } from '../api/config'
import { ElMessage } from 'element-plus'

// ============================================================================
// Props & Emits
// ============================================================================

const props = defineProps<{
  modelValue: GeneralConfig
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: GeneralConfig): void
  (e: 'change'): void
}>()

// ============================================================================
// State
// ============================================================================

const formRef = ref<FormInstance>()
const formData = ref<GeneralConfig>({ ...props.modelValue })

// ============================================================================
// Validation Rules
// ============================================================================

const rules: FormRules = {
  language: [{ required: true, message: '请选择界面语言', trigger: 'change' }],
  theme: [{ required: true, message: '请选择主题', trigger: 'change' }],
  logLevel: [{ required: true, message: '请选择日志级别', trigger: 'change' }],
  autoSave: [{ required: true, message: '请设置自动保存', trigger: 'change' }]
}

// ============================================================================
// Methods
// ============================================================================

/**
 * Select theme from preview
 */
const selectTheme = (theme: 'light' | 'dark') => {
  formData.value.theme = theme
  handleThemeChange(theme)
}

/**
 * Handle theme change with immediate preview
 */
const handleThemeChange = (theme: 'light' | 'dark') => {
  // Apply theme immediately for preview
  document.documentElement.setAttribute('data-theme', theme)
  if (theme === 'dark') {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }

  handleChange()
  ElMessage.success(`已切换到${theme === 'light' ? '浅色' : '深色'}主题`)
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
.general-settings-form {
  max-width: 800px;
}

.form-item-help {
  font-size: 0.875rem;
  color: var(--el-text-color-secondary);
  line-height: 1.5;
}

.language-option {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.language-option__flag {
  font-size: 1.25rem;
}

.language-option__name {
  color: var(--el-text-color-primary);
}

.log-level-option {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.log-level-option__desc {
  font-size: 0.875rem;
  color: var(--el-text-color-secondary);
}

.theme-preview {
  display: flex;
  gap: 1.5rem;
}

.theme-preview__card {
  flex: 1;
  border: 2px solid var(--el-border-color);
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s;
}

.theme-preview__card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.theme-preview__card--active {
  border-color: var(--el-color-primary);
  box-shadow: 0 0 0 3px rgba(64, 158, 255, 0.2);
}

.theme-preview__header {
  height: 30px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0 0.75rem;
}

.theme-preview__header--light {
  background-color: #f5f5f5;
}

.theme-preview__header--dark {
  background-color: #2d2d2d;
}

.theme-preview__dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: rgba(0, 0, 0, 0.2);
}

.theme-preview__body {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.theme-preview__body--light {
  background-color: #ffffff;
}

.theme-preview__body--dark {
  background-color: #1a1a1a;
}

.theme-preview__line {
  height: 8px;
  border-radius: 4px;
  background-color: rgba(0, 0, 0, 0.1);
}

.theme-preview__body--dark .theme-preview__line {
  background-color: rgba(255, 255, 255, 0.1);
}

.theme-preview__line--short {
  width: 60%;
}

.theme-preview__label {
  padding: 0.5rem;
  text-align: center;
  font-size: 0.875rem;
  color: var(--el-text-color-secondary);
  background-color: var(--el-fill-color-light);
}

.general-settings-form__info {
  margin-top: 1.5rem;
}

.general-settings-form__warning {
  margin-top: 1rem;
}

.info-list {
  margin: 0.5rem 0 0 0;
  padding-left: 1.5rem;
  list-style: disc;
}

.info-list > li {
  margin: 0.75rem 0;
  color: var(--el-text-color-regular);
  line-height: 1.6;
}

.shortcut-list {
  margin: 0.5rem 0 0 0;
  padding-left: 1.5rem;
  list-style: circle;
}

.shortcut-list li {
  margin: 0.25rem 0;
  font-size: 0.875rem;
}

kbd {
  display: inline-block;
  padding: 0.125rem 0.375rem;
  font-size: 0.75rem;
  font-family: monospace;
  background-color: var(--el-fill-color);
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

/* Form Item Extra Styling */
.general-settings-form :deep(.el-form-item__extra) {
  margin-top: 0.5rem;
}

/* Responsive */
@media (max-width: 768px) {
  .general-settings-form :deep(.el-form-item) {
    flex-direction: column;
  }

  .general-settings-form :deep(.el-form-item__label) {
    text-align: left;
    margin-bottom: 0.5rem;
  }

  .theme-preview {
    flex-direction: column;
  }
}
</style>
