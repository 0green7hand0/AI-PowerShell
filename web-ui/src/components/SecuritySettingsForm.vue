<!--
  SecuritySettingsForm Component
  
  Form for configuring security settings including whitelist mode,
  confirmation requirements, and dangerous patterns.
  
  Requirements: 8.2, 8.3
-->

<template>
  <div class="security-settings-form">
    <el-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-width="180px"
      label-position="left"
      @submit.prevent
    >
      <!-- Sandbox Mode -->
      <el-form-item label="沙箱模式" prop="sandboxEnabled">
        <el-select
          v-model="sandboxMode"
          placeholder="选择沙箱模式"
          @change="handleSandboxModeChange"
        >
          <el-option label="禁用" value="disabled">
            <div class="sandbox-option">
              <span class="sandbox-option__name">禁用</span>
              <span class="sandbox-option__desc">不使用沙箱，所有命令直接执行</span>
            </div>
          </el-option>
          <el-option label="仅高危命令（推荐）" value="highRiskOnly">
            <div class="sandbox-option">
              <span class="sandbox-option__name">仅高危命令（推荐）</span>
              <span class="sandbox-option__desc">高危命令在沙箱中执行，普通命令直接执行</span>
            </div>
          </el-option>
          <el-option label="所有命令" value="all">
            <div class="sandbox-option">
              <span class="sandbox-option__name">所有命令</span>
              <span class="sandbox-option__desc">所有命令都在沙箱中执行，最安全但较慢</span>
            </div>
          </el-option>
        </el-select>
        <template #extra>
          <span class="form-item-help"> 
            沙箱模式使用 Docker 容器隔离执行命令，提供额外的安全保护。需要安装 Docker
          </span>
        </template>
      </el-form-item>

      <!-- Whitelist Mode -->
      <el-form-item label="白名单模式" prop="whitelistMode">
        <el-switch
          v-model="formData.whitelistMode"
          active-text="启用"
          inactive-text="禁用"
          @change="handleChange"
        />
        <template #extra>
          <span class="form-item-help"> 启用后，只有白名单中的命令才能执行。更安全但限制更多 </span>
        </template>
      </el-form-item>

      <!-- Require Confirmation -->
      <el-form-item label="需要确认" prop="requireConfirmation">
        <el-switch
          v-model="formData.requireConfirmation"
          active-text="启用"
          inactive-text="禁用"
          @change="handleChange"
        />
        <template #extra>
          <span class="form-item-help"> 执行高风险命令前需要用户确认 </span>
        </template>
      </el-form-item>

      <!-- Allowed Commands (shown when whitelist mode is enabled) -->
      <el-form-item v-if="formData.whitelistMode" label="允许的命令" prop="allowedCommands">
        <el-select
          v-model="formData.allowedCommands"
          multiple
          filterable
          allow-create
          default-first-option
          placeholder="输入命令名称并按回车添加"
          class="full-width"
          @change="handleChange"
        >
          <el-option v-for="cmd in commonCommands" :key="cmd" :label="cmd" :value="cmd" />
        </el-select>
        <template #extra>
          <span class="form-item-help"> 白名单模式下允许执行的命令列表。可以输入自定义命令 </span>
        </template>
      </el-form-item>

      <!-- Dangerous Patterns -->
      <el-form-item label="危险模式" prop="dangerousPatterns">
        <div class="patterns-container">
          <el-tag
            v-for="(pattern, index) in formData.dangerousPatterns"
            :key="index"
            closable
            type="danger"
            class="pattern-tag"
            @close="handleRemovePattern(index)"
          >
            {{ pattern }}
          </el-tag>
          <el-input
            v-model="newPattern"
            placeholder="输入危险模式并按回车添加"
            class="pattern-input"
            size="small"
            @keyup.enter="handleAddPattern"
          >
            <template #append>
              <el-button :icon="Plus" @click="handleAddPattern" />
            </template>
          </el-input>
        </div>
        <template #extra>
          <span class="form-item-help"> 包含这些模式的命令将被标记为高风险。支持正则表达式 </span>
        </template>
      </el-form-item>

      <!-- Common Dangerous Patterns -->
      <el-form-item label="常见危险模式">
        <div class="common-patterns">
          <el-tag
            v-for="pattern in commonDangerousPatterns"
            :key="pattern"
            type="info"
            class="common-pattern-tag"
            @click="handleAddCommonPattern(pattern)"
          >
            <el-icon><Plus /></el-icon>
            {{ pattern }}
          </el-tag>
        </div>
        <template #extra>
          <span class="form-item-help"> 点击添加常见的危险模式到列表中 </span>
        </template>
      </el-form-item>

      <!-- Security Level Info -->
      <el-alert
        :type="getSecurityLevelType()"
        :closable="false"
        show-icon
        class="security-settings-form__info"
      >
        <template #title> 当前安全级别：{{ getSecurityLevelText() }} </template>
        <template #default>
          <div class="security-level-description">
            {{ getSecurityLevelDescription() }}
          </div>
        </template>
      </el-alert>

      <!-- Warning for Disabled Security -->
      <el-alert
        v-if="!formData.sandboxEnabled && !formData.whitelistMode && !formData.requireConfirmation"
        type="warning"
        :closable="false"
        show-icon
        class="security-settings-form__warning"
      >
        <template #title> 安全警告 </template>
        <template #default>
          您已禁用所有安全保护措施。这可能导致危险命令被执行而无需确认。建议至少启用"沙箱模式"或"需要确认"选项。
        </template>
      </el-alert>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import type { SecurityConfig } from '../api/config'
import { ElMessage } from 'element-plus'

// ============================================================================
// Props & Emits
// ============================================================================

const props = defineProps<{
  modelValue: SecurityConfig
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: SecurityConfig): void
  (e: 'change'): void
}>()

// ============================================================================
// State
// ============================================================================

const formRef = ref<FormInstance>()
const formData = ref<SecurityConfig>({
  sandboxEnabled: false,
  sandboxForHighRiskOnly: true,
  whitelistMode: false,
  requireConfirmation: true,
  dangerousPatterns: [],
  ...props.modelValue
})
const newPattern = ref('')

// Common commands for whitelist
const commonCommands = [
  'Get-Process',
  'Get-Service',
  'Get-Date',
  'Get-Location',
  'Get-ChildItem',
  'Get-Content',
  'Get-EventLog',
  'Get-NetAdapter',
  'Get-Disk',
  'Get-Volume',
  'Test-Connection',
  'Test-Path'
]

// Common dangerous patterns
const commonDangerousPatterns = [
  'Remove-Item.*-Recurse',
  'Remove-Item.*-Force',
  'Format-Volume',
  'Clear-Disk',
  'Stop-Computer',
  'Restart-Computer',
  'Invoke-Expression',
  'Invoke-Command',
  'Set-ExecutionPolicy',
  'New-Object.*Net.WebClient'
]

// ============================================================================
// Validation Rules
// ============================================================================

const rules: FormRules = {
  whitelistMode: [{ required: true, message: '请设置白名单模式', trigger: 'change' }],
  requireConfirmation: [{ required: true, message: '请设置确认要求', trigger: 'change' }],
  dangerousPatterns: [
    {
      type: 'array',
      message: '危险模式必须是数组',
      trigger: 'change'
    }
  ],
  allowedCommands: [
    {
      type: 'array',
      message: '允许的命令必须是数组',
      trigger: 'change'
    }
  ]
}

// ============================================================================
// Computed
// ============================================================================

/**
 * Sandbox mode selection
 */
const sandboxMode = computed({
  get: () => {
    if (!formData.value.sandboxEnabled) return 'disabled'
    if (formData.value.sandboxForHighRiskOnly) return 'highRiskOnly'
    return 'all'
  },
  set: (value: string) => {
    switch (value) {
      case 'disabled':
        formData.value.sandboxEnabled = false
        formData.value.sandboxForHighRiskOnly = true
        break
      case 'highRiskOnly':
        formData.value.sandboxEnabled = true
        formData.value.sandboxForHighRiskOnly = true
        break
      case 'all':
        formData.value.sandboxEnabled = true
        formData.value.sandboxForHighRiskOnly = false
        break
    }
  }
})

/**
 * Calculate security level based on settings
 */
const securityLevel = computed(() => {
  if (formData.value.sandboxEnabled && formData.value.whitelistMode) {
    return 'highest'
  }
  if (formData.value.sandboxEnabled) {
    return 'high'
  }
  if (formData.value.whitelistMode) {
    return 'high'
  } else if (formData.value.requireConfirmation && formData.value.dangerousPatterns.length > 5) {
    return 'medium'
  } else if (formData.value.requireConfirmation) {
    return 'low'
  } else {
    return 'none'
  }
})

// ============================================================================
// Methods
// ============================================================================

/**
 * Get security level alert type
 */
const getSecurityLevelType = (): 'success' | 'warning' | 'info' | 'error' => {
  switch (securityLevel.value) {
    case 'highest':
      return 'success'
    case 'high':
      return 'success'
    case 'medium':
      return 'info'
    case 'low':
      return 'warning'
    case 'none':
      return 'error'
    default:
      return 'info'
  }
}

/**
 * Get security level text
 */
const getSecurityLevelText = (): string => {
  switch (securityLevel.value) {
    case 'highest':
      return '最高（沙箱+白名单）'
    case 'high':
      return '高（推荐）'
    case 'medium':
      return '中等'
    case 'low':
      return '低'
    case 'none':
      return '无保护'
    default:
      return '未知'
  }
}

/**
 * Get security level description
 */
const getSecurityLevelDescription = (): string => {
  switch (securityLevel.value) {
    case 'highest':
      return '沙箱模式和白名单模式均已启用，命令将在隔离容器中执行且只能执行白名单中的命令。这是最安全的配置。'
    case 'high':
      return '沙箱模式或白名单模式已启用，提供强大的安全保护。'
    case 'medium':
      return '需要确认高风险命令，并配置了较多危险模式。提供良好的安全保护。'
    case 'low':
      return '需要确认高风险命令，但危险模式配置较少。建议添加更多危险模式。'
    case 'none':
      return '未启用任何安全保护。所有命令都可以直接执行，存在安全风险。'
    default:
      return ''
  }
}

/**
 * Handle add dangerous pattern
 */
const handleAddPattern = () => {
  const pattern = newPattern.value.trim()

  if (!pattern) {
    return
  }

  if (formData.value.dangerousPatterns.includes(pattern)) {
    ElMessage.warning('该模式已存在')
    return
  }

  // Validate regex pattern
  try {
    new RegExp(pattern)
  } catch (error) {
    ElMessage.error('无效的正则表达式')
    return
  }

  formData.value.dangerousPatterns.push(pattern)
  newPattern.value = ''
  handleChange()
}

/**
 * Handle remove dangerous pattern
 */
const handleRemovePattern = (index: number) => {
  formData.value.dangerousPatterns.splice(index, 1)
  handleChange()
}

/**
 * Handle add common pattern
 */
const handleAddCommonPattern = (pattern: string) => {
  if (formData.value.dangerousPatterns.includes(pattern)) {
    ElMessage.warning('该模式已存在')
    return
  }

  formData.value.dangerousPatterns.push(pattern)
  handleChange()
  ElMessage.success('已添加危险模式')
}

/**
 * Handle sandbox mode change
 */
const handleSandboxModeChange = (value: string) => {
  sandboxMode.value = value
  handleChange()
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
.security-settings-form {
  max-width: 800px;
}

.full-width {
  width: 100%;
}

.form-item-help {
  font-size: 0.875rem;
  color: var(--el-text-color-secondary);
  line-height: 1.5;
}

.sandbox-option {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.sandbox-option__name {
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.sandbox-option__desc {
  font-size: 0.75rem;
  color: var(--el-text-color-secondary);
}

.patterns-container {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  align-items: flex-start;
}

.pattern-tag {
  cursor: default;
}

.pattern-input {
  flex: 1;
  min-width: 250px;
}

.common-patterns {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.common-pattern-tag {
  cursor: pointer;
  transition: all 0.2s;
}

.common-pattern-tag:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.common-pattern-tag .el-icon {
  margin-right: 0.25rem;
}

.security-settings-form__info {
  margin-top: 1.5rem;
}

.security-settings-form__warning {
  margin-top: 1rem;
}

.security-level-description {
  margin-top: 0.5rem;
  color: var(--el-text-color-regular);
  line-height: 1.6;
}

/* Form Item Extra Styling */
.security-settings-form :deep(.el-form-item__extra) {
  margin-top: 0.5rem;
}

/* Responsive */
@media (max-width: 768px) {
  .security-settings-form :deep(.el-form-item) {
    flex-direction: column;
  }

  .security-settings-form :deep(.el-form-item__label) {
    text-align: left;
    margin-bottom: 0.5rem;
  }

  .pattern-input {
    min-width: 100%;
  }
}
</style>
