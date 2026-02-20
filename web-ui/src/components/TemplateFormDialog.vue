<template>
  <el-dialog
    v-model="dialogVisible"
    :title="isEditMode ? '编辑模板' : '创建模板'"
    width="900px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-position="top"
      @submit.prevent="handleSubmit"
    >
      <!-- Basic Info -->
      <div class="form-section">
        <h4 class="form-section__title">基本信息</h4>

        <el-form-item label="模板名称" prop="name" required>
          <el-input v-model="formData.name" placeholder="例如：备份脚本" clearable />
        </el-form-item>

        <el-form-item label="描述" prop="description" required>
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="描述模板的功能和用途"
            clearable
          />
        </el-form-item>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="分类" prop="category" required>
              <el-select v-model="formData.category" placeholder="选择分类" style="width: 100%">
                <el-option
                  v-for="cat in categories"
                  :key="cat.value"
                  :label="cat.label"
                  :value="cat.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="关键词" prop="keywords">
              <el-select
                v-model="formData.keywords"
                multiple
                filterable
                allow-create
                placeholder="输入关键词后按回车"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
      </div>

      <!-- Script Content -->
      <div class="form-section">
        <h4 class="form-section__title">脚本内容</h4>
        <p class="form-section__help">
          使用 <code v-text="'{{参数名}}'" /> 作为参数占位符，例如：<code
            v-text="'{{sourcePath}}'"
          />
        </p>

        <el-form-item prop="scriptContent" required>
          <div class="code-editor-container">
            <div class="code-editor-toolbar">
              <span class="language-label">PowerShell</span>
              <div class="toolbar-actions">
                <el-button size="small" @click="insertSnippet('copy-item')" title="复制文件">
                  复制文件
                </el-button>
                <el-button size="small" @click="insertSnippet('get-service')" title="获取服务">
                  服务管理
                </el-button>
                <el-button size="small" @click="insertSnippet('new-item')" title="创建项目">
                  创建项目
                </el-button>
              </div>
            </div>
            <div class="code-editor-wrapper">
              <div class="line-numbers" ref="lineNumbersRef">
                <div v-for="i in lineCount" :key="i" class="line-number">{{ i }}</div>
              </div>
              <el-input
                v-model="formData.scriptContent"
                type="textarea"
                :rows="10"
                placeholder="# PowerShell 脚本内容&#10;Copy-Item -Path {{sourcePath}} -Destination {{targetPath}}"
                class="code-editor"
                @input="updateLineNumbers"
                @scroll="syncScroll"
              />
              <pre v-if="formData.scriptContent" class="code-highlight" ref="highlightRef">{{ formData.scriptContent }}</pre>
            </div>
          </div>
        </el-form-item>
      </div>

      <!-- Parameters -->
      <div class="form-section">
        <div class="form-section__header">
          <h4 class="form-section__title">参数定义</h4>
          <el-button type="primary" size="small" @click="handleAddParameter">
            <i class="el-icon-plus" />
            添加参数
          </el-button>
        </div>

        <div v-if="formData.parameters.length === 0" class="form-section__empty">
          <p>暂无参数，点击上方按钮添加参数</p>
        </div>

        <div v-else class="parameters-list">
          <div v-for="(param, index) in formData.parameters" :key="index" class="parameter-item">
            <div class="parameter-item__header">
              <span class="parameter-item__index">参数 {{ index + 1 }}</span>
              <el-button type="danger" size="small" text @click="handleRemoveParameter(index)">
                <i class="el-icon-delete" />
                删除
              </el-button>
            </div>

            <el-row :gutter="16">
              <el-col :span="8">
                <el-form-item
                  :prop="`parameters.${index}.name`"
                  :rules="[{ required: true, message: '请输入参数名称', trigger: 'blur' }]"
                  label="参数名称"
                >
                  <el-input v-model="param.name" placeholder="例如：sourcePath" />
                </el-form-item>
              </el-col>

              <el-col :span="8">
                <el-form-item
                  :prop="`parameters.${index}.type`"
                  :rules="[{ required: true, message: '请选择参数类型', trigger: 'change' }]"
                  label="参数类型"
                >
                  <el-select v-model="param.type" placeholder="选择类型" style="width: 100%">
                    <el-option label="字符串" value="string" />
                    <el-option label="数字" value="number" />
                    <el-option label="布尔值" value="boolean" />
                    <el-option label="选择项" value="select" />
                  </el-select>
                </el-form-item>
              </el-col>

              <el-col :span="8">
                <el-form-item label="是否必填">
                  <el-switch v-model="param.required" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="描述">
              <el-input v-model="param.description" placeholder="参数的说明文字" />
            </el-form-item>

            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item label="默认值">
                  <el-input
                    v-if="param.type === 'string'"
                    v-model="param.default"
                    placeholder="默认值（可选）"
                  />
                  <el-input-number
                    v-else-if="param.type === 'number'"
                    v-model="param.default"
                    placeholder="默认值（可选）"
                    style="width: 100%"
                  />
                  <el-switch v-else-if="param.type === 'boolean'" v-model="param.default" />
                  <el-select
                    v-else-if="param.type === 'select'"
                    v-model="param.default"
                    placeholder="选择默认值"
                    style="width: 100%"
                  >
                    <el-option v-for="opt in param.options" :key="opt" :label="opt" :value="opt" />
                  </el-select>
                </el-form-item>
              </el-col>

              <el-col v-if="param.type === 'select'" :span="12">
                <el-form-item label="选项列表">
                  <el-select
                    v-model="param.options"
                    multiple
                    filterable
                    allow-create
                    placeholder="输入选项后按回车"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
            </el-row>
          </div>
        </div>
      </div>
    </el-form>

    <!-- Actions -->
    <template #footer>
      <div class="form-dialog__footer">
        <el-button :disabled="isSaving" @click="handleCancel"> 取消 </el-button>
        <el-button type="primary" :loading="isSaving" :disabled="isSaving" @click="handleSubmit">
          <i v-if="!isSaving" class="el-icon-check" />
          {{ isSaving ? '保存中...' : isEditMode ? '保存修改' : '创建模板' }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, reactive, onMounted, nextTick } from 'vue'
import {
  ElDialog,
  ElForm,
  ElFormItem,
  ElInput,
  ElInputNumber,
  ElSelect,
  ElOption,
  ElSwitch,
  ElButton,
  ElRow,
  ElCol,
  type FormInstance,
  type FormRules
} from 'element-plus'
import hljs from 'highlight.js/lib/core'
import powershell from 'highlight.js/lib/languages/powershell'
import 'highlight.js/styles/github-dark.css'
import type { Template, TemplateParameter, CreateTemplateRequest } from '../api/template'

// Register PowerShell language
hljs.registerLanguage('powershell', powershell)

// ============================================================================
// Props & Emits
// ============================================================================

interface Props {
  visible: boolean
  template?: Template | null
  isSaving?: boolean
}

interface Emits {
  (e: 'update:visible', value: boolean): void
  (e: 'submit', data: CreateTemplateRequest): void
  (e: 'cancel'): void
}

const props = withDefaults(defineProps<Props>(), {
  template: null,
  isSaving: false
})

const emit = defineEmits<Emits>()

// ============================================================================
// State
// ============================================================================

const formRef = ref<FormInstance>()
const lineNumbersRef = ref<HTMLElement | null>(null)
const highlightRef = ref<HTMLElement | null>(null)

const formData = reactive<CreateTemplateRequest>({
  name: '',
  description: '',
  category: '',
  scriptContent: '',
  parameters: [],
  keywords: []
})

// Code editor computed properties
const lineCount = computed(() => {
  if (!formData.scriptContent) return 1
  return formData.scriptContent.split('\n').length
})

// Code snippets
const snippets = {
  'copy-item': `# 复制文件示例
Copy-Item -Path "{{sourcePath}}" -Destination "{{targetPath}}" -Force -Recurse
`,
  'get-service': `# 服务管理示例
# 获取服务状态
Get-Service -Name "{{serviceName}}"

# 启动服务
Start-Service -Name "{{serviceName}}"

# 停止服务
Stop-Service -Name "{{serviceName}}"
`,
  'new-item': `# 创建项目示例
# 创建目录
New-Item -Path "{{directoryPath}}" -ItemType Directory -Force

# 创建文件
New-Item -Path "{{filePath}}" -ItemType File -Value "{{fileContent}}"
`
}

// Update line numbers when content changes
const updateLineNumbers = () => {
  nextTick(() => {
    highlightCode()
  })
}

// Sync scroll between textarea and line numbers
const syncScroll = (event: Event) => {
  const textarea = event.target as HTMLElement
  if (lineNumbersRef.value && highlightRef.value) {
    lineNumbersRef.value.scrollTop = textarea.scrollTop
    highlightRef.value.scrollTop = textarea.scrollTop
  }
}

// Highlight code using highlight.js
const highlightCode = () => {
  if (highlightRef.value && formData.scriptContent) {
    const highlighted = hljs.highlight(formData.scriptContent, { language: 'powershell' }).value
    highlightRef.value.innerHTML = highlighted
  }
}

// Insert code snippet
const insertSnippet = (type: keyof typeof snippets) => {
  const snippet = snippets[type]
  formData.scriptContent += snippet
  nextTick(() => {
    updateLineNumbers()
  })
}

// Initialize code editor
onMounted(() => {
  nextTick(() => {
    updateLineNumbers()
  })
})

// Watch for script content changes
watch(
  () => formData.scriptContent,
  () => {
    nextTick(() => {
      highlightCode()
    })
  }
)

// Watch for template changes
watch(
  () => props.template,
  (newTemplate) => {
    if (newTemplate) {
      nextTick(() => {
        updateLineNumbers()
      })
    }
  }
)

const categories = [
  { label: '自动化', value: 'automation' },
  { label: '文件管理', value: 'file_management' },
  { label: '系统监控', value: 'system_monitoring' },
  { label: '网络', value: 'network' },
  { label: '数据库', value: 'database' },
  { label: '安全', value: 'security' },
  { label: '备份', value: 'backup' },
  { label: '部署', value: 'deployment' }
]

// ============================================================================
// Computed
// ============================================================================

const dialogVisible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})

const isEditMode = computed(() => !!props.template)

const formRules: FormRules = {
  name: [
    { required: true, message: '请输入模板名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入描述', trigger: 'blur' },
    { min: 10, max: 500, message: '长度在 10 到 500 个字符', trigger: 'blur' }
  ],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }],
  scriptContent: [
    { required: true, message: '请输入脚本内容', trigger: 'blur' },
    { min: 10, message: '脚本内容至少 10 个字符', trigger: 'blur' }
  ]
}

// ============================================================================
// Watchers
// ============================================================================

watch(
  () => props.visible,
  (newValue) => {
    if (newValue) {
      if (props.template) {
        // Edit mode: populate form with template data
        loadTemplateData(props.template)
      } else {
        // Create mode: reset form
        resetForm()
      }
    }
  }
)

// ============================================================================
// Methods
// ============================================================================

/**
 * Load template data into form
 */
const loadTemplateData = (template: Template): void => {
  formData.name = template.name
  formData.description = template.description
  formData.category = template.category
  formData.scriptContent = template.scriptContent
  formData.parameters = JSON.parse(JSON.stringify(template.parameters))
  formData.keywords = [...template.keywords]
}

/**
 * Reset form to initial state
 */
const resetForm = (): void => {
  formData.name = ''
  formData.description = ''
  formData.category = ''
  formData.scriptContent = ''
  formData.parameters = []
  formData.keywords = []

  formRef.value?.clearValidate()
}

/**
 * Add a new parameter
 */
const handleAddParameter = (): void => {
  formData.parameters.push({
    name: '',
    type: 'string',
    required: true,
    description: '',
    default: undefined,
    options: []
  })
}

/**
 * Remove a parameter
 */
const handleRemoveParameter = (index: number): void => {
  formData.parameters.splice(index, 1)
}

/**
 * Handle form submit
 */
const handleSubmit = async (): Promise<void> => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()

    // Clean up parameters (remove empty defaults and options)
    const cleanedData: CreateTemplateRequest = {
      ...formData,
      parameters: formData.parameters.map((param) => {
        const cleaned: TemplateParameter = {
          name: param.name,
          type: param.type,
          required: param.required
        }

        if (param.description) {
          cleaned.description = param.description
        }

        if (param.default !== undefined && param.default !== '') {
          cleaned.default = param.default
        }

        if (param.type === 'select' && param.options && param.options.length > 0) {
          cleaned.options = param.options
        }

        return cleaned
      })
    }

    emit('submit', cleanedData)
  } catch (error) {
    console.error('Form validation failed:', error)
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
  if (!props.isSaving) {
    handleCancel()
  }
}
</script>

<style scoped>
.form-section {
  margin-bottom: var(--space-6);
  padding-bottom: var(--space-6);
  border-bottom: 1px solid var(--color-border);
}

.form-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.form-section__title {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--color-text-primary);
  margin: 0 0 var(--space-4) 0;
}

.form-section__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
}

.form-section__help {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  margin: 0 0 var(--space-3) 0;
  line-height: var(--leading-relaxed);
}

.form-section__help code {
  background-color: var(--color-bg-tertiary);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
  font-family: var(--font-mono);
  font-size: var(--text-xs);
}

.form-section__empty {
  text-align: center;
  padding: var(--space-8);
  background-color: var(--color-bg-secondary);
  border: 1px dashed var(--color-border);
  border-radius: var(--radius-md);
}

.form-section__empty p {
  font-size: var(--text-sm);
  color: var(--color-text-tertiary);
  margin: 0;
}

.code-editor-container {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  overflow: hidden;
  background-color: #1e1e1e;
  width: 100%;
}

.code-editor-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-2) var(--space-3);
  background-color: #252526;
  border-bottom: 1px solid #3e3e42;
  width: 100%;
  box-sizing: border-box;
}

.code-editor-wrapper {
  position: relative;
  display: flex;
  min-height: 300px;
  max-height: 500px;
  height: 100%;
  width: 100%;
  box-sizing: border-box;
}

.language-label {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: #d4d4d4;
}

.toolbar-actions {
  display: flex;
  gap: var(--space-1);
  flex-wrap: wrap;
}

.toolbar-actions .el-button {
  background-color: #0e639c;
  border-color: #1177bb;
  color: white;
  font-size: var(--text-xs);
  padding: 4px 8px;
  min-width: auto;
}

.toolbar-actions .el-button:hover {
  background-color: #1177bb;
  border-color: #1177bb;
}

.code-editor-wrapper {
  position: relative;
  display: flex;
  min-height: 300px;
  max-height: 500px;
  height: 100%;
}

.line-numbers {
  flex-shrink: 0;
  width: 50px;
  padding: var(--space-2) 0;
  background-color: #1e1e1e;
  border-right: 1px solid #3e3e42;
  text-align: center;
  overflow: hidden;
  user-select: none;
  height: 100%;
}

.line-number {
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  line-height: 1.5;
  color: #858585;
  padding: 0 var(--space-2);
}

.code-editor {
  flex: 1;
  background-color: transparent;
  color: transparent;
  caret-color: #d4d4d4;
  resize: vertical;
  min-height: 300px;
  max-height: 500px;
  z-index: 2;
  height: 100%;
  margin: 0;
}

.code-editor :deep(.el-textarea) {
  height: 100%;
  margin: 0;
}

.code-editor :deep(textarea) {
  background-color: transparent !important;
  color: transparent !important;
  caret-color: #d4d4d4 !important;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace !important;
  font-size: var(--text-sm) !important;
  line-height: 1.5 !important;
  padding: var(--space-2) !important;
  border: none !important;
  resize: vertical;
  z-index: 2;
  position: relative;
  height: 100% !important;
  min-height: 300px !important;
  max-height: 500px !important;
  box-sizing: border-box !important;
}

.code-editor :deep(.el-textarea__inner) {
  height: 100% !important;
  min-height: 300px !important;
  max-height: 500px !important;
  box-sizing: border-box !important;
}

.code-editor :deep(textarea):focus {
  border: none !important;
  box-shadow: none !important;
}

.code-highlight {
  position: absolute;
  top: 0;
  left: 50px;
  right: 0;
  bottom: 0;
  margin: 0;
  padding: var(--space-2);
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: var(--text-sm);
  line-height: 1.5;
  white-space: pre-wrap;
  word-wrap: break-word;
  pointer-events: none;
  z-index: 1;
  overflow: hidden;
  box-sizing: border-box;
}

.code-highlight code {
  background: none;
  padding: 0;
  border-radius: 0;
}

/* Responsive */
@media (max-width: 768px) {
  .code-editor-toolbar {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-2);
  }
  
  .toolbar-actions {
    width: 100%;
    justify-content: space-between;
  }
  
  .toolbar-actions .el-button {
    flex: 1;
    text-align: center;
  }
  
  .line-numbers {
    width: 40px;
  }
  
  .code-highlight {
    left: 40px;
  }
}

/* Parameters List */
.parameters-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.parameter-item {
  background-color: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--space-4);
}

.parameter-item__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-3);
  padding-bottom: var(--space-2);
  border-bottom: 1px solid var(--color-border);
}

.parameter-item__index {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--color-text-primary);
}

/* Footer */
.form-dialog__footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
}

/* Responsive */
@media (max-width: 768px) {
  :deep(.el-dialog) {
    width: 95% !important;
  }

  .form-section__header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-3);
  }

  .form-section__header .el-button {
    width: 100%;
  }

  .form-dialog__footer {
    flex-direction: column-reverse;
  }

  .form-dialog__footer .el-button {
    width: 100%;
  }
}
</style>
