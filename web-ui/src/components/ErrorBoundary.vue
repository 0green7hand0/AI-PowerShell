<template>
  <div v-if="error" class="error-boundary">
    <div class="error-content">
      <div class="error-icon">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="64"
          height="64"
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
      </div>
      
      <h2 class="error-title">出错了</h2>
      
      <p class="error-message">{{ errorMessage }}</p>
      
      <div v-if="showDetails && errorDetails" class="error-details">
        <details>
          <summary>错误详情</summary>
          <pre>{{ errorDetails }}</pre>
        </details>
      </div>
      
      <div class="error-actions">
        <button class="btn btn-primary" @click="handleReset">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <polyline points="1 4 1 10 7 10"></polyline>
            <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"></path>
          </svg>
          重试
        </button>
        
        <button class="btn btn-secondary" @click="handleGoHome">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
            <polyline points="9 22 9 12 15 12 15 22"></polyline>
          </svg>
          返回首页
        </button>
      </div>
    </div>
  </div>
  
  <slot v-else />
</template>

<script setup lang="ts">
import { ref, onErrorCaptured } from 'vue'
import { useRouter } from 'vue-router'

interface Props {
  showDetails?: boolean
  fallbackMessage?: string
}

const props = withDefaults(defineProps<Props>(), {
  showDetails: import.meta.env.DEV,
  fallbackMessage: '应用程序遇到了一个错误，请重试或返回首页。'
})

const emit = defineEmits<{
  error: [error: Error]
  reset: []
}>()

const router = useRouter()

const error = ref<Error | null>(null)
const errorMessage = ref('')
const errorDetails = ref('')

onErrorCaptured((err: Error) => {
  error.value = err
  errorMessage.value = err.message || props.fallbackMessage
  errorDetails.value = err.stack || ''
  
  // Log error to console in development
  if (import.meta.env.DEV) {
    console.error('ErrorBoundary caught error:', err)
  }
  
  // Emit error event for parent components
  emit('error', err)
  
  // Prevent error from propagating
  return false
})

const handleReset = () => {
  error.value = null
  errorMessage.value = ''
  errorDetails.value = ''
  emit('reset')
}

const handleGoHome = () => {
  error.value = null
  errorMessage.value = ''
  errorDetails.value = ''
  router.push('/chat')
}

// Expose reset method for external use
defineExpose({
  reset: handleReset
})
</script>

<style scoped>
.error-boundary {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  padding: var(--space-8);
  background-color: var(--color-bg-secondary);
}

.error-content {
  max-width: 600px;
  text-align: center;
}

.error-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: var(--space-6);
  color: var(--color-danger);
  animation: shake 0.5s ease-in-out;
}

.error-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0 0 var(--space-4) 0;
}

.error-message {
  font-size: 1rem;
  color: var(--color-text-secondary);
  margin: 0 0 var(--space-6) 0;
  line-height: 1.6;
}

.error-details {
  margin-bottom: var(--space-6);
  text-align: left;
}

.error-details details {
  background-color: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: var(--space-4);
}

.error-details summary {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text-primary);
  cursor: pointer;
  user-select: none;
}

.error-details summary:hover {
  color: var(--color-primary);
}

.error-details pre {
  margin-top: var(--space-3);
  padding: var(--space-3);
  background-color: var(--color-bg-tertiary);
  border-radius: 4px;
  font-size: 0.75rem;
  color: var(--color-text-secondary);
  overflow-x: auto;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.error-actions {
  display: flex;
  gap: var(--space-3);
  justify-content: center;
  flex-wrap: wrap;
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

.btn-secondary {
  background-color: var(--color-bg-tertiary);
  color: var(--color-text-primary);
}

.btn-secondary:hover {
  background-color: var(--color-border);
  transform: translateY(-1px);
}

@keyframes shake {
  0%, 100% {
    transform: translateX(0);
  }
  10%, 30%, 50%, 70%, 90% {
    transform: translateX(-5px);
  }
  20%, 40%, 60%, 80% {
    transform: translateX(5px);
  }
}

/* Responsive */
@media (max-width: 768px) {
  .error-boundary {
    padding: var(--space-4);
    min-height: 300px;
  }

  .error-title {
    font-size: 1.25rem;
  }

  .error-message {
    font-size: 0.875rem;
  }

  .error-actions {
    flex-direction: column;
  }

  .btn {
    width: 100%;
    justify-content: center;
  }
}
</style>
