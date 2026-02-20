<template>
  <div class="template-management">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">
          <el-icon><Document /></el-icon>
          模板管理中心
        </h1>
        <p class="page-subtitle">创建、编辑和管理 PowerShell 脚本模板</p>
      </div>
      <div class="header-actions">
        <el-button :icon="Refresh" :loading="loading" @click="refreshTemplates"> 刷新 </el-button>
        <el-button type="primary" :icon="Plus" @click="createTemplate"> 新建模板 </el-button>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <el-card class="filter-card" shadow="never">
      <el-row :gutter="16">
        <el-col :span="12">
          <el-input
            v-model="searchQuery"
            placeholder="搜索模板名称、描述或关键词..."
            :prefix-icon="Search"
            clearable
            @input="handleSearch"
          />
        </el-col>
        <el-col :span="6">
          <el-select
            v-model="selectedCategory"
            placeholder="选择分类"
            clearable
            style="width: 100%"
            @change="handleCategoryChange"
          >
            <el-option label="全部分类" value="" />
            <el-option
              v-for="cat in categories"
              :key="cat.value"
              :label="cat.label"
              :value="cat.value"
            />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-select v-model="viewMode" placeholder="视图模式" style="width: 100%">
            <el-option label="卡片视图" value="card" />
            <el-option label="列表视图" value="list" />
            <el-option label="表格视图" value="table" />
          </el-select>
        </el-col>
      </el-row>
    </el-card>

    <!-- 统计信息 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <el-icon :size="32" color="#409EFF">
              <Document />
            </el-icon>
            <div class="stat-info">
              <div class="stat-value">
                {{ totalTemplates }}
              </div>
              <div class="stat-label">模板总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <el-icon :size="32" color="#67C23A">
              <FolderOpened />
            </el-icon>
            <div class="stat-info">
              <div class="stat-value">
                {{ categories.length }}
              </div>
              <div class="stat-label">分类数量</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <el-icon :size="32" color="#E6A23C">
              <Filter />
            </el-icon>
            <div class="stat-info">
              <div class="stat-value">
                {{ filteredTemplates.length }}
              </div>
              <div class="stat-label">筛选结果</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <el-icon :size="32" color="#F56C6C">
              <Star />
            </el-icon>
            <div class="stat-info">
              <div class="stat-value">
                {{ customTemplates }}
              </div>
              <div class="stat-label">自定义模板</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 模板列表 -->
    <el-card class="templates-card" shadow="never">
      <!-- 卡片视图 -->
      <div v-if="viewMode === 'card'" class="card-view">
        <el-empty v-if="filteredTemplates.length === 0" description="暂无模板">
          <el-button type="primary" @click="createTemplate"> 创建第一个模板 </el-button>
        </el-empty>

        <div v-else class="template-grid">
          <el-card
            v-for="template in filteredTemplates"
            :key="template.id"
            class="template-card"
            shadow="hover"
            @click="viewTemplate(template)"
          >
            <template #header>
              <div class="template-card-header">
                <span class="template-name">{{ template.name }}</span>
                <el-tag size="small">
                  {{ getCategoryLabel(template.category) }}
                </el-tag>
              </div>
            </template>

            <div class="template-card-body">
              <p class="template-description">
                {{ template.description }}
              </p>

              <div class="template-meta">
                <el-tag
                  v-for="keyword in template.keywords.slice(0, 3)"
                  :key="keyword"
                  size="small"
                  type="info"
                  class="keyword-tag"
                >
                  {{ keyword }}
                </el-tag>
                <span v-if="template.keywords.length > 3" class="more-keywords">
                  +{{ template.keywords.length - 3 }}
                </span>
              </div>

              <div class="template-stats">
                <span
                  ><el-icon><Setting /></el-icon> {{ template.parameters.length }} 参数</span
                >
                <span
                  ><el-icon><Clock /></el-icon> {{ formatDate(template.updatedAt) }}</span
                >
              </div>
            </div>

            <template #footer>
              <div class="template-actions">
                <el-button size="small" @click.stop="useTemplate(template)">
                  <el-icon><VideoPlay /></el-icon>
                  使用
                </el-button>
                <el-button size="small" @click.stop="editTemplate(template)">
                  <el-icon><Edit /></el-icon>
                  编辑
                </el-button>
                <el-button size="small" type="danger" @click.stop="deleteTemplate(template)">
                  <el-icon><Delete /></el-icon>
                  删除
                </el-button>
              </div>
            </template>
          </el-card>
        </div>
      </div>

      <!-- 列表视图 -->
      <div v-else-if="viewMode === 'list'" class="list-view">
        <el-empty v-if="filteredTemplates.length === 0" description="暂无模板" />

        <div v-else class="template-list">
          <div
            v-for="template in filteredTemplates"
            :key="template.id"
            class="template-list-item"
            @click="viewTemplate(template)"
          >
            <div class="list-item-main">
              <div class="list-item-header">
                <h4 class="list-item-title">
                  {{ template.name }}
                </h4>
                <el-tag size="small">
                  {{ getCategoryLabel(template.category) }}
                </el-tag>
              </div>
              <p class="list-item-description">
                {{ template.description }}
              </p>
              <div class="list-item-meta">
                <el-tag
                  v-for="keyword in template.keywords.slice(0, 5)"
                  :key="keyword"
                  size="small"
                  type="info"
                >
                  {{ keyword }}
                </el-tag>
              </div>
            </div>
            <div class="list-item-actions">
              <el-button size="small" @click.stop="useTemplate(template)"> 使用 </el-button>
              <el-button size="small" @click.stop="editTemplate(template)"> 编辑 </el-button>
              <el-button size="small" type="danger" @click.stop="deleteTemplate(template)">
                删除
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 表格视图 -->
      <div v-else-if="viewMode === 'table'" class="table-view">
        <el-table :data="filteredTemplates" stripe style="width: 100%" @row-click="viewTemplate">
          <el-table-column prop="name" label="名称" width="200" />
          <el-table-column prop="description" label="描述" show-overflow-tooltip />
          <el-table-column prop="category" label="分类" width="120">
            <template #default="{ row }">
              <el-tag size="small">
                {{ getCategoryLabel(row.category) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="参数" width="80" align="center">
            <template #default="{ row }">
              {{ row.parameters.length }}
            </template>
          </el-table-column>
          <el-table-column prop="updatedAt" label="更新时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.updatedAt) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="240" fixed="right">
            <template #default="{ row }">
              <el-button size="small" @click.stop="useTemplate(row)"> 使用 </el-button>
              <el-button size="small" @click.stop="editTemplate(row)"> 编辑 </el-button>
              <el-button size="small" type="danger" @click.stop="deleteTemplate(row)">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>

    <!-- 编辑对话框 -->
    <el-dialog
      v-model="showEditorDialog"
      :title="editorMode === 'create' ? '创建模板' : '编辑模板'"
      width="90%"
      :close-on-click-modal="false"
      @close="handleEditorClose"
    >
      <TemplateEditor v-model="currentTemplate" />

      <template #footer>
        <el-button @click="showEditorDialog = false"> 取消 </el-button>
        <el-button type="primary" :loading="saving" @click="saveTemplate">
          {{ saving ? '保存中...' : '保存' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 使用模板对话框 -->
    <TemplateUseDialog
      v-model:visible="showUseDialog"
      :template="selectedTemplate"
      @generate="handleGenerate"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Document,
  Refresh,
  Plus,
  Search,
  FolderOpened,
  Filter,
  Star,
  Setting,
  Clock,
  VideoPlay,
  Edit,
  Delete
} from '@element-plus/icons-vue'
import { templateApi, type Template, type CreateTemplateRequest } from '../api/template'
import TemplateEditor from '../components/TemplateEditor.vue'
import TemplateUseDialog from '../components/TemplateUseDialog.vue'

// State
const loading = ref(false)
const saving = ref(false)
const templates = ref<Template[]>([])
const searchQuery = ref('')
const selectedCategory = ref('')
const viewMode = ref<'card' | 'list' | 'table'>('card')
const showEditorDialog = ref(false)
const showUseDialog = ref(false)
const editorMode = ref<'create' | 'edit'>('create')
const currentTemplate = ref<CreateTemplateRequest>({
  name: '',
  description: '',
  category: '',
  scriptContent: '',
  parameters: [],
  keywords: []
})
const selectedTemplate = ref<Template | null>(null)

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
const filteredTemplates = computed(() => {
  let result = templates.value

  // 按分类筛选
  if (selectedCategory.value) {
    result = result.filter((t) => t.category === selectedCategory.value)
  }

  // 按搜索词筛选
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(
      (t) =>
        t.name.toLowerCase().includes(query) ||
        t.description.toLowerCase().includes(query) ||
        t.keywords.some((k) => k.toLowerCase().includes(query))
    )
  }

  return result
})

const totalTemplates = computed(() => templates.value.length)
const customTemplates = computed(
  () => templates.value.filter((t) => t.category === 'custom').length
)

// Methods
const getCategoryLabel = (value: string) => {
  return categories.find((c) => c.value === value)?.label || value
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

const refreshTemplates = async () => {
  loading.value = true
  try {
    const response = await templateApi.getTemplates()
    templates.value = response.data.items
    ElMessage.success('刷新成功')
  } catch (error) {
    ElMessage.error('刷新失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  // 搜索已通过 computed 自动处理
}

const handleCategoryChange = () => {
  // 筛选已通过 computed 自动处理
}

const createTemplate = () => {
  editorMode.value = 'create'
  currentTemplate.value = {
    name: '',
    description: '',
    category: '',
    scriptContent: '',
    parameters: [],
    keywords: []
  }
  showEditorDialog.value = true
}

const viewTemplate = (template: Template) => {
  // 可以显示详情对话框或跳转到详情页
  console.log('View template:', template)
}

const editTemplate = (template: Template) => {
  editorMode.value = 'edit'
  currentTemplate.value = {
    name: template.name,
    description: template.description,
    category: template.category,
    scriptContent: template.scriptContent,
    parameters: JSON.parse(JSON.stringify(template.parameters)),
    keywords: [...template.keywords]
  }
  selectedTemplate.value = template
  showEditorDialog.value = true
}

const useTemplate = (template: Template) => {
  selectedTemplate.value = template
  showUseDialog.value = true
}

const deleteTemplate = async (template: Template) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除模板 "${template.name}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await templateApi.deleteTemplate(template.id)
    ElMessage.success('删除成功')
    await refreshTemplates()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
      console.error(error)
    }
  }
}

const saveTemplate = async () => {
  // 验证
  if (!currentTemplate.value.name) {
    ElMessage.warning('请输入模板名称')
    return
  }
  if (!currentTemplate.value.description) {
    ElMessage.warning('请输入模板描述')
    return
  }
  if (!currentTemplate.value.category) {
    ElMessage.warning('请选择模板分类')
    return
  }
  if (!currentTemplate.value.scriptContent) {
    ElMessage.warning('请输入脚本内容')
    return
  }

  saving.value = true
  try {
    if (editorMode.value === 'create') {
      await templateApi.createTemplate(currentTemplate.value)
      ElMessage.success('创建成功')
    } else {
      if (selectedTemplate.value) {
        await templateApi.updateTemplate(selectedTemplate.value.id, currentTemplate.value)
        ElMessage.success('更新成功')
      }
    }

    showEditorDialog.value = false
    await refreshTemplates()
  } catch (error) {
    ElMessage.error(editorMode.value === 'create' ? '创建失败' : '更新失败')
    console.error(error)
  } finally {
    saving.value = false
  }
}

const handleEditorClose = () => {
  currentTemplate.value = {
    name: '',
    description: '',
    category: '',
    scriptContent: '',
    parameters: [],
    keywords: []
  }
  selectedTemplate.value = null
}

const handleGenerate = async (params: Record<string, any>) => {
  if (!selectedTemplate.value) return

  try {
    const response = await templateApi.generateScript(selectedTemplate.value.id, {
      parameters: params
    })
    ElMessage.success('脚本生成成功')
    console.log('Generated script:', response.data.script)
  } catch (error) {
    ElMessage.error('生成失败')
    console.error(error)
  }
}

// Lifecycle
onMounted(() => {
  refreshTemplates()
})
</script>

<style scoped>
.template-management {
  padding: 24px;
  max-width: 1600px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.header-content {
  flex: 1;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 700;
  color: var(--el-text-color-primary);
}

.page-subtitle {
  margin: 0;
  font-size: 14px;
  color: var(--el-text-color-secondary);
}

.header-actions {
  display: flex;
  gap: 12px;
}

.filter-card {
  margin-bottom: 24px;
}

.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  cursor: pointer;
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-4px);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: var(--el-text-color-primary);
  line-height: 1;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: var(--el-text-color-secondary);
}

.templates-card {
  min-height: 400px;
}

/* 卡片视图 */
.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.template-card {
  cursor: pointer;
  transition: all 0.3s;
}

.template-card:hover {
  transform: translateY(-4px);
}

.template-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.template-name {
  font-weight: 600;
  font-size: 16px;
}

.template-card-body {
  min-height: 180px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.template-description {
  flex: 1;
  margin: 0;
  font-size: 14px;
  color: var(--el-text-color-secondary);
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.template-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.keyword-tag {
  font-size: 12px;
}

.more-keywords {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.template-stats {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.template-stats span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.template-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

/* 列表视图 */
.template-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.template-list-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border: 1px solid var(--el-border-color);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.template-list-item:hover {
  background: var(--el-fill-color-light);
  border-color: var(--el-color-primary);
}

.list-item-main {
  flex: 1;
}

.list-item-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.list-item-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.list-item-description {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: var(--el-text-color-secondary);
}

.list-item-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.list-item-actions {
  display: flex;
  gap: 8px;
}

/* 响应式 */
@media (max-width: 768px) {
  .template-management {
    padding: 16px;
  }

  .page-header {
    flex-direction: column;
    gap: 16px;
  }

  .header-actions {
    width: 100%;
  }

  .header-actions .el-button {
    flex: 1;
  }

  .template-grid {
    grid-template-columns: 1fr;
  }

  .template-list-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .list-item-actions {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>
