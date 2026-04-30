<template>
  <div class="template-editor">
    <!-- 编辑器标签页 -->
    <el-tabs v-model="activeTab" class="editor-tabs">
      <!-- 基本信息 -->
      <el-tab-pane label="基本信息" name="basic">
        <div class="editor-section">
          <el-form :model="formData" label-position="top">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="模板名称" required>
                  <el-input v-model="formData.name" placeholder="例如：文件备份脚本" clearable />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="分类" required>
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
            </el-row>

            <el-form-item label="描述" required>
              <el-input
                v-model="formData.description"
                type="textarea"
                :rows="3"
                placeholder="详细描述模板的功能和用途"
                clearable
              />
            </el-form-item>

            <el-form-item label="关键词">
              <el-tag
                v-for="(keyword, index) in formData.keywords"
                :key="index"
                closable
                class="keyword-tag"
                @close="removeKeyword(index)"
              >
                {{ keyword }}
              </el-tag>
              <el-input
                v-if="showKeywordInput"
                ref="keywordInputRef"
                v-model="newKeyword"
                size="small"
                class="keyword-input"
                @keyup.enter="addKeyword"
                @blur="addKeyword"
              />
              <el-button v-else size="small" @click="showKeywordInput = true">
                + 添加关键词
              </el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-tab-pane>

      <!-- 脚本编辑 -->
      <el-tab-pane label="脚本编辑" name="script">
        <div class="editor-section">
          <div class="editor-toolbar">
            <el-button-group>
              <el-button size="small" @click="insertPlaceholder">
                <el-icon><Plus /></el-icon>
                插入参数
              </el-button>
              <el-button size="small" @click="formatScript">
                <el-icon><Document /></el-icon>
                格式化
              </el-button>
              <el-button size="small" @click="validateScript">
                <el-icon><Check /></el-icon>
                验证
              </el-button>
            </el-button-group>

            <div class="editor-info">
              <span>行数: {{ scriptLines }}</span>
              <span>字符: {{ scriptChars }}</span>
            </div>
          </div>

          <div class="code-editor">
            <textarea
              ref="scriptEditorRef"
              v-model="formData.scriptContent"
              class="script-textarea"
              placeholder="# PowerShell 脚本内容&#10;# 使用 {{参数名}} 作为占位符&#10;&#10;Copy-Item -Path {{sourcePath}} -Destination {{targetPath}}"
              @input="onScriptChange"
            />
          </div>

          <div v-if="scriptErrors.length > 0" class="script-errors">
            <el-alert
              v-for="(error, index) in scriptErrors"
              :key="index"
              :title="error"
              type="error"
              :closable="false"
            />
          </div>
        </div>
      </el-tab-pane>

      <!-- 参数配置 -->
      <el-tab-pane label="参数配置" name="parameters">
        <div class="editor-section">
          <div class="parameters-header">
            <el-button type="primary" @click="addParameter">
              <el-icon><Plus /></el-icon>
              添加参数
            </el-button>
            <el-button @click="autoDetectParameters">
              <el-icon><MagicStick /></el-icon>
              自动检测参数
            </el-button>
          </div>

          <div v-if="formData.parameters.length === 0" class="empty-state">
            <el-empty description="暂无参数">
              <el-button type="primary" @click="addParameter"> 添加第一个参数 </el-button>
            </el-empty>
          </div>

          <div v-else class="parameters-list">
            <el-card
              v-for="(param, index) in formData.parameters"
              :key="index"
              class="parameter-card"
              shadow="hover"
            >
              <template #header>
                <div class="parameter-header">
                  <span class="parameter-title">
                    <el-tag size="small" type="info">{{ index + 1 }}</el-tag>
                    {{ param.name || '未命名参数' }}
                  </span>
                  <el-button type="danger" size="small" text @click="removeParameter(index)">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </div>
              </template>

              <el-form label-position="top">
                <el-row :gutter="16">
                  <el-col :span="8">
                    <el-form-item label="参数名称" required>
                      <el-input v-model="param.name" placeholder="例如：sourcePath" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="8">
                    <el-form-item label="类型" required>
                      <el-select v-model="param.type" style="width: 100%">
                        <el-option label="字符串" value="string" />
                        <el-option label="数字" value="number" />
                        <el-option label="布尔值" value="boolean" />
                        <el-option label="选择项" value="select" />
                      </el-select>
                    </el-form-item>
                  </el-col>
                  <el-col :span="8">
                    <el-form-item label="必填">
                      <el-switch v-model="param.required" />
                    </el-form-item>
                  </el-col>
                </el-row>

                <el-form-item label="描述">
                  <el-input v-model="param.description" placeholder="参数的说明" />
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
                        v-else-if="param.type === 'number' || param.type === 'integer'"
                        v-model="param.default"
                        style="width: 100%"
                        :min="param.type === 'integer' ? 0 : undefined"
                        :precision="param.type === 'integer' ? 0 : undefined"
                      />
                      <el-switch v-else-if="param.type === 'boolean'" v-model="param.default" />
                      <el-select
                        v-else-if="param.type === 'select'"
                        v-model="param.default"
                        style="width: 100%"
                      >
                        <el-option
                          v-for="opt in param.options"
                          :key="opt"
                          :label="opt"
                          :value="opt"
                        />
                      </el-select>
                    </el-form-item>
                  </el-col>
                  <el-col v-if="param.type === 'select'" :span="12">
                    <el-form-item label="选项">
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
              </el-form>
            </el-card>
          </div>
        </div>
      </el-tab-pane>

      <!-- 预览测试 -->
      <el-tab-pane label="预览测试" name="preview">
        <div class="editor-section">
          <div class="preview-container">
            <div class="preview-panel">
              <h4>模板信息</h4>
              <el-descriptions :column="2" border>
                <el-descriptions-item label="名称">
                  {{ formData.name || '-' }}
                </el-descriptions-item>
                <el-descriptions-item label="分类">
                  {{ getCategoryLabel(formData.category) }}
                </el-descriptions-item>
                <el-descriptions-item label="描述" :span="2">
                  {{ formData.description || '-' }}
                </el-descriptions-item>
                <el-descriptions-item label="关键词" :span="2">
                  <el-tag
                    v-for="(keyword, index) in formData.keywords"
                    :key="index"
                    size="small"
                    class="keyword-tag"
                  >
                    {{ keyword }}
                  </el-tag>
                  <span v-if="formData.keywords.length === 0">-</span>
                </el-descriptions-item>
                <el-descriptions-item label="参数数量">
                  {{ formData.parameters.length }}
                </el-descriptions-item>
                <el-descriptions-item label="脚本行数">
                  {{ scriptLines }}
                </el-descriptions-item>
              </el-descriptions>
            </div>

            <div class="preview-panel">
              <h4>参数列表</h4>
              <el-table :data="formData.parameters" border>
                <el-table-column prop="name" label="参数名" />
                <el-table-column prop="type" label="类型" width="100" />
                <el-table-column label="必填" width="80">
                  <template #default="{ row }">
                    <el-tag :type="row.required ? 'danger' : 'info'" size="small">
                      {{ row.required ? '是' : '否' }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="description" label="描述" />
              </el-table>
            </div>

            <div class="preview-panel">
              <h4>脚本预览</h4>
              <pre
                class="script-preview"
              ><code>{{ formData.scriptContent || '# 暂无脚本内容' }}</code></pre>
            </div>

            <div class="preview-actions">
              <el-button type="primary" @click="testTemplate">
                <el-icon><VideoPlay /></el-icon>
                测试模板
              </el-button>
            </div>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Delete, Document, Check, MagicStick, VideoPlay } from '@element-plus/icons-vue'
import type { TemplateParameter, CreateTemplateRequest } from '../api/template'

// Props
interface Props {
  modelValue: CreateTemplateRequest
}

const props = defineProps<Props>()

// Emits
interface Emits {
  (e: 'update:modelValue', value: CreateTemplateRequest): void
}

const emit = defineEmits<Emits>()

// State
const activeTab = ref('basic')
const formData = ref<CreateTemplateRequest>({ ...props.modelValue })
const scriptEditorRef = ref<HTMLTextAreaElement>()
const keywordInputRef = ref()
const showKeywordInput = ref(false)
const newKeyword = ref('')
const scriptErrors = ref<string[]>([])

// Categories
const categories = [
  { label: '自动化', value: 'automation' },
  { label: '文件管理', value: 'file_management' },
  { label: '系统监控', value: 'system_monitoring' },
  { label: '网络诊断', value: 'network_diagnostics' },
  { label: '进程管理', value: 'process_management' },
  { label: '日志分析', value: 'log_analysis' },
  { label: '定时任务', value: 'scheduled_tasks' }
]

// Computed
const scriptLines = computed(() => {
  return formData.value.scriptContent?.split('\n').length || 0
})

const scriptChars = computed(() => {
  return formData.value.scriptContent?.length || 0
})

// Watch
watch(
  () => props.modelValue,
  (newValue) => {
    formData.value = { ...newValue }
  },
  { deep: true }
)

watch(
  formData,
  (newValue) => {
    emit('update:modelValue', newValue)
  },
  { deep: true }
)

// Methods
const getCategoryLabel = (value: string) => {
  return categories.find((c) => c.value === value)?.label || value
}

const addKeyword = () => {
  if (newKeyword.value && !formData.value.keywords?.includes(newKeyword.value)) {
    if (!formData.value.keywords) {
      formData.value.keywords = []
    }
    formData.value.keywords.push(newKeyword.value)
    newKeyword.value = ''
  }
  showKeywordInput.value = false
}

const removeKeyword = (index: number) => {
  formData.value.keywords?.splice(index, 1)
}

const addParameter = () => {
  if (!formData.value.parameters) {
    formData.value.parameters = []
  }
  formData.value.parameters.push({
    name: '',
    type: 'string',
    required: true,
    description: '',
    default: undefined,
    options: []
  })
}

const removeParameter = (index: number) => {
  formData.value.parameters?.splice(index, 1)
}

const insertPlaceholder = () => {
  const textarea = scriptEditorRef.value
  if (!textarea) return

  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const text = formData.value.scriptContent || ''

  const placeholder = '{{参数名}}'
  formData.value.scriptContent = text.substring(0, start) + placeholder + text.substring(end)

  nextTick(() => {
    textarea.focus()
    textarea.setSelectionRange(start + 2, start + 2 + 3)
  })
}

const formatScript = () => {
  // 简单的格式化：移除多余空行
  if (formData.value.scriptContent) {
    formData.value.scriptContent = formData.value.scriptContent
      .split('\n')
      .map((line) => line.trimEnd())
      .join('\n')
      .replace(/\n{3,}/g, '\n\n')
    ElMessage.success('脚本已格式化')
  }
}

const validateScript = () => {
  scriptErrors.value = []

  if (!formData.value.scriptContent) {
    scriptErrors.value.push('脚本内容不能为空')
    return
  }

  // 检查参数占位符
  const placeholders = formData.value.scriptContent.match(/\{\{(\w+)\}\}/g) || []
  const paramNames = formData.value.parameters?.map((p) => p.name) || []

  placeholders.forEach((placeholder) => {
    const paramName = placeholder.replace(/\{\{|\}\}/g, '')
    if (!paramNames.includes(paramName)) {
      scriptErrors.value.push(`未定义的参数: ${paramName}`)
    }
  })

  if (scriptErrors.value.length === 0) {
    ElMessage.success('脚本验证通过')
  }
}

const autoDetectParameters = () => {
  if (!formData.value.scriptContent) {
    ElMessage.warning('请先输入脚本内容')
    return
  }

  const placeholders = formData.value.scriptContent.match(/\{\{(\w+)\}\}/g) || []
  const uniqueParams = [...new Set(placeholders.map((p) => p.replace(/\{\{|\}\}/g, '')))]

  const existingParams = formData.value.parameters?.map((p) => p.name) || []
  const newParams = uniqueParams.filter((p) => !existingParams.includes(p))

  if (newParams.length === 0) {
    ElMessage.info('未检测到新参数')
    return
  }

  newParams.forEach((paramName) => {
    formData.value.parameters?.push({
      name: paramName,
      type: 'string',
      required: true,
      description: `自动检测的参数: ${paramName}`,
      default: undefined
    })
  })

  ElMessage.success(`已添加 ${newParams.length} 个参数`)
  activeTab.value = 'parameters'
}

const onScriptChange = () => {
  scriptErrors.value = []
}

const testTemplate = () => {
  validateScript()
  if (scriptErrors.value.length === 0) {
    ElMessage.success('模板测试通过！')
  } else {
    ElMessage.error('模板存在错误，请修复后再试')
  }
}
</script>

<style scoped>
.template-editor {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.editor-tabs {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.editor-tabs :deep(.el-tabs__content) {
  flex: 1;
  overflow-y: auto;
}

.editor-section {
  padding: 20px;
}

.editor-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding: 12px;
  background: var(--el-fill-color-light);
  border-radius: 4px;
}

.editor-info {
  display: flex;
  gap: 16px;
  font-size: 14px;
  color: var(--el-text-color-secondary);
}

.code-editor {
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
  overflow: hidden;
}

.script-textarea {
  width: 100%;
  min-height: 400px;
  padding: 16px;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.6;
  border: none;
  outline: none;
  resize: vertical;
  background: var(--el-bg-color);
  color: var(--el-text-color-primary);
}

.script-errors {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.keyword-tag {
  margin-right: 8px;
  margin-bottom: 8px;
}

.keyword-input {
  width: 120px;
  margin-right: 8px;
}

.parameters-header {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.empty-state {
  padding: 60px 20px;
  text-align: center;
}

.parameters-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.parameter-card {
  transition: all 0.3s;
}

.parameter-card:hover {
  transform: translateY(-2px);
}

.parameter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.parameter-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.preview-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.preview-panel h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.script-preview {
  background: var(--el-fill-color-light);
  padding: 16px;
  border-radius: 4px;
  overflow-x: auto;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.6;
  margin: 0;
}

.script-preview code {
  color: var(--el-text-color-primary);
}

.preview-actions {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}
</style>
