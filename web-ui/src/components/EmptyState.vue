<template>
  <div class="empty-state" :class="sizeClass">
    <div class="empty-icon">
      <!-- No Data Icon -->
      <svg
        v-if="type === 'no-data'"
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
        <polyline points="14 2 14 8 20 8"></polyline>
        <line x1="12" y1="18" x2="12" y2="12"></line>
        <line x1="9" y1="15" x2="15" y2="15"></line>
      </svg>
      
      <!-- No Search Results Icon -->
      <svg
        v-else-if="type === 'no-results'"
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <circle cx="11" cy="11" r="8"></circle>
        <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        <line x1="8" y1="11" x2="14" y2="11"></line>
      </svg>
      
      <!-- Error Icon -->
      <svg
        v-else-if="type === 'error'"
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <circle cx="12" cy="12" r="10"></circle>
        <line x1="15" y1="9" x2="9" y2="15"></line>
        <line x1="9" y1="9" x2="15" y2="15"></line>
      </svg>
      
      <!-- Network Error Icon -->
      <svg
        v-else-if="type === 'network-error'"
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <path d="M5 12.55a11 11 0 0 1 14.08 0"></path>
        <path d="M1.42 9a16 16 0 0 1 21.16 0"></path>
        <path d="M8.53 16.11a6 6 0 0 1 6.95 0"></path>
        <line x1="12" y1="20" x2="12.01" y2="20"></line>
        <line x1="2" y1="2" x2="22" y2="22"></line>
      </svg>
      
      <!-- Permission Denied Icon -->
      <svg
        v-else-if="type === 'permission-denied'"
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
        <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
      </svg>
      
      <!-- Custom Icon Slot -->
      <slot v-else name="icon">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="8" x2="12" y2="12"></line>
          <line x1="12" y1="16" x2="12.01" y2="16"></line>
        </svg>
      </slot>
    </div>
    
    <div class="empty-content">
      <h3 class="empty-title">{{ title || defaultTitle }}</h3>
      <p class="empty-description">{{ description || defaultDescription }}</p>
    </div>
    
    <div v-if="$slots.actions || action" class="empty-actions">
      <slot name="actions">
        <button
          v-if="action"
          class="btn btn-primary"
          @click="handleAction"
        >
          {{ actionText || defaultActionText }}
        </button>
      </slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  type?: 'no-data' | 'no-results' | 'error' | 'network-error' | 'permission-denied' | 'custom'
  title?: string
  description?: string
  actionText?: string
  action?: () => void
  size?: 'small' | 'medium' | 'large'
}

const props = withDefaults(defineProps<Props>(), {
  type: 'no-data',
  size: 'medium'
})

const emit = defineEmits<{
  action: []
}>()

const sizeClass = computed(() => `size-${props.size}`)

const defaultTitle = computed(() => {
  switch (props.type) {
    case 'no-data':
      return '暂无数据'
    case 'no-results':
      return '未找到结果'
    case 'error':
      return '出错了'
    case 'network-error':
      return '网络连接失败'
    case 'permission-denied':
      return '权限不足'
    default:
      return '空空如也'
  }
})

const defaultDescription = computed(() => {
  switch (props.type) {
    case 'no-data':
      return '这里还没有任何内容，开始创建吧'
    case 'no-results':
      return '尝试使用不同的关键词或筛选条件'
    case 'error':
      return '发生了一些错误，请稍后重试'
    case 'network-error':
      return '请检查您的网络连接后重试'
    case 'permission-denied':
      return '您没有权限访问此内容'
    default:
      return ''
  }
})

const defaultActionText = computed(() => {
  switch (props.type) {
    case 'no-data':
      return '创建新项目'
    case 'no-results':
      return '清除筛选'
    case 'error':
    case 'network-error':
      return '重试'
    default:
      return '返回'
  }
})

const handleAction = () => {
  if (props.action) {
    props.action()
  } else {
    emit('action')
  }
}
</script>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: var(--space-8);
  color: var(--color-text-secondary);
}

.size-small {
  padding: var(--space-4);
}

.size-medium {
  padding: var(--space-8);
}

.size-large {
  padding: var(--space-12);
  min-height: 400px;
}

.empty-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: var(--space-6);
  color: var(--color-text-tertiary);
  opacity: 0.6;
}

.size-small .empty-icon svg {
  width: 48px;
  height: 48px;
}

.size-medium .empty-icon svg {
  width: 80px;
  height: 80px;
}

.size-large .empty-icon svg {
  width: 120px;
  height: 120px;
}

.empty-content {
  margin-bottom: var(--space-6);
  max-width: 400px;
}

.empty-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0 0 var(--space-3) 0;
}

.size-small .empty-title {
  font-size: 1rem;
}

.size-large .empty-title {
  font-size: 1.5rem;
}

.empty-description {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  margin: 0;
  line-height: 1.6;
}

.size-small .empty-description {
  font-size: 0.75rem;
}

.size-large .empty-description {
  font-size: 1rem;
}

.empty-actions {
  display: flex;
  gap: var(--space-3);
  flex-wrap: wrap;
  justify-content: center;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-6);
  border: none;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-in-out);
}

.btn-primary {
  background-color: var(--color-primary);
  color: white;
}

.btn-primary:hover {
  background-color: var(--color-primary-hover);
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

/* Animation */
.empty-icon {
  animation: fadeInUp 0.6s ease-out;
}

.empty-content {
  animation: fadeInUp 0.6s ease-out 0.1s both;
}

.empty-actions {
  animation: fadeInUp 0.6s ease-out 0.2s both;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Responsive */
@media (max-width: 768px) {
  .empty-state {
    padding: var(--space-6);
  }

  .size-large {
    min-height: 300px;
  }

  .empty-icon svg {
    width: 64px;
    height: 64px;
  }

  .empty-title {
    font-size: 1.125rem;
  }

  .empty-description {
    font-size: 0.8125rem;
  }
}
</style>
