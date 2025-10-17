<template>
  <div v-if="show" class="dialog-overlay" @click.self="handleCancel">
    <div class="dialog-container">
      <div class="dialog-header">
        <div class="dialog-icon" :class="`risk-${riskLevel}`">
          <svg v-if="riskLevel === 'high' || riskLevel === 'critical'" xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
            <line x1="12" y1="9" x2="12" y2="13"></line>
            <line x1="12" y1="17" x2="12.01" y2="17"></line>
          </svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="8" x2="12" y2="12"></line>
            <line x1="12" y1="16" x2="12.01" y2="16"></line>
          </svg>
        </div>
        <h2 class="dialog-title">{{ title }}</h2>
        <button class="close-btn" @click="handleCancel" aria-label="关闭">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>

      <div class="dialog-body">
        <div class="warning-message">
          <p>{{ message }}</p>
        </div>

        <div v-if="warnings && warnings.length > 0" class="warnings-list">
          <h3>安全警告：</h3>
          <ul>
            <li v-for="(warning, index) in warnings" :key="index">
              {{ warning }}
            </li>
          </ul>
        </div>

        <div class="command-preview">
          <h3>命令：</h3>
          <div class="command-code">
            <code>{{ command }}</code>
          </div>
        </div>

        <div v-if="requiresElevation" class="elevation-notice">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
            <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
          </svg>
          <span>此命令需要管理员权限</span>
        </div>

        <div v-if="requireConfirmation" class="confirmation-input">
          <label for="confirm-text">
            请输入 <strong>{{ confirmText }}</strong> 以确认执行：
          </label>
          <input
            id="confirm-text"
            v-model="userInput"
            type="text"
            class="confirm-input"
            :placeholder="`输入 ${confirmText}`"
            @keyup.enter="handleConfirm"
          />
        </div>
      </div>

      <div class="dialog-footer">
        <button class="btn btn-secondary" @click="handleCancel">
          取消
        </button>
        <button
          class="btn btn-danger"
          :disabled="requireConfirmation && userInput !== confirmText"
          @click="handleConfirm"
        >
          {{ confirmButtonText }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';

interface Props {
  show: boolean;
  command: string;
  riskLevel: 'safe' | 'low' | 'medium' | 'high' | 'critical';
  warnings?: string[];
  requiresElevation?: boolean;
  requireConfirmation?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  warnings: () => [],
  requiresElevation: false,
  requireConfirmation: false
});

const emit = defineEmits<{
  confirm: [];
  cancel: [];
}>();

const userInput = ref('');
const confirmText = 'EXECUTE';

const title = computed(() => {
  switch (props.riskLevel) {
    case 'critical':
      return '危险命令警告';
    case 'high':
      return '高风险命令警告';
    case 'medium':
      return '中等风险命令';
    default:
      return '命令确认';
  }
});

const message = computed(() => {
  switch (props.riskLevel) {
    case 'critical':
      return '您即将执行一个极度危险的命令，可能会造成严重的系统损坏或数据丢失。请仔细确认后再继续。';
    case 'high':
      return '您即将执行一个高风险命令，可能会对系统造成重大影响。请确保您了解此命令的作用。';
    case 'medium':
      return '此命令可能会对系统产生一定影响，请确认后再执行。';
    default:
      return '请确认是否执行此命令。';
  }
});

const confirmButtonText = computed(() => {
  switch (props.riskLevel) {
    case 'critical':
    case 'high':
      return '我了解风险，继续执行';
    default:
      return '确认执行';
  }
});

function handleConfirm() {
  if (props.requireConfirmation && userInput.value !== confirmText) {
    return;
  }
  userInput.value = '';
  emit('confirm');
}

function handleCancel() {
  userInput.value = '';
  emit('cancel');
}
</script>

<style scoped>
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 1rem;
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.dialog-container {
  background-color: var(--color-bg-primary);
  border-radius: var(--radius-xl);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.dialog-header {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-6);
  border-bottom: 1px solid var(--color-border);
}

.dialog-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  flex-shrink: 0;
}

.dialog-icon.risk-safe,
.dialog-icon.risk-low {
  background-color: rgba(16, 185, 129, 0.1);
  color: var(--color-success);
}

.dialog-icon.risk-medium {
  background-color: rgba(245, 158, 11, 0.1);
  color: var(--color-warning);
}

.dialog-icon.risk-high,
.dialog-icon.risk-critical {
  background-color: rgba(239, 68, 68, 0.1);
  color: var(--color-danger);
}

.dialog-title {
  flex: 1;
  font-size: var(--text-xl);
  font-weight: var(--font-bold);
  color: var(--color-text-primary);
  margin: 0;
}

.close-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  background-color: transparent;
  color: var(--color-text-secondary);
  border-radius: 6px;
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-in-out);
}

.close-btn:hover {
  background-color: var(--color-bg-tertiary);
  color: var(--color-text-primary);
}

.dialog-body {
  flex: 1;
  padding: var(--space-6);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}

.warning-message {
  padding: var(--space-4);
  background-color: rgba(239, 68, 68, 0.1);
  border-left: 4px solid var(--color-danger);
  border-radius: var(--radius-md);
}

.warning-message p {
  margin: 0;
  color: var(--color-text-primary);
  line-height: 1.6;
}

.warnings-list {
  padding: var(--space-4);
  background-color: var(--color-bg-secondary);
  border-radius: var(--radius-md);
}

.warnings-list h3 {
  margin: 0 0 var(--space-3) 0;
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--color-text-primary);
}

.warnings-list ul {
  margin: 0;
  padding-left: var(--space-5);
  list-style-type: disc;
}

.warnings-list li {
  margin-bottom: var(--space-2);
  color: var(--color-text-secondary);
  font-size: var(--text-sm);
}

.command-preview {
  padding: var(--space-4);
  background-color: var(--color-bg-secondary);
  border-radius: var(--radius-md);
}

.command-preview h3 {
  margin: 0 0 var(--space-3) 0;
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--color-text-primary);
}

.command-code {
  padding: var(--space-3);
  background-color: var(--color-bg-tertiary);
  border-radius: var(--radius-md);
  overflow-x: auto;
}

.command-code code {
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  color: var(--color-text-primary);
  white-space: pre-wrap;
  word-break: break-all;
}

.elevation-notice {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3);
  background-color: rgba(245, 158, 11, 0.1);
  border-radius: var(--radius-md);
  color: var(--color-warning);
  font-size: var(--text-sm);
}

.confirmation-input {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.confirmation-input label {
  font-size: var(--text-sm);
  color: var(--color-text-primary);
}

.confirmation-input strong {
  color: var(--color-danger);
  font-family: var(--font-mono);
}

.confirm-input {
  width: 100%;
  padding: var(--space-3) var(--space-4);
  background-color: var(--color-bg-secondary);
  border: 2px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: var(--text-base);
  font-family: var(--font-mono);
  color: var(--color-text-primary);
  transition: all var(--duration-fast) var(--ease-in-out);
}

.confirm-input:focus {
  outline: none;
  border-color: var(--color-danger);
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

.dialog-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: var(--space-3);
  padding: var(--space-6);
  border-top: 1px solid var(--color-border);
}

.btn {
  padding: var(--space-3) var(--space-6);
  border: none;
  border-radius: var(--radius-md);
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-in-out);
}

.btn-secondary {
  background-color: var(--color-bg-tertiary);
  color: var(--color-text-primary);
}

.btn-secondary:hover {
  background-color: var(--color-border-hover);
}

.btn-danger {
  background-color: var(--color-danger);
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background-color: #dc2626;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}

.btn-danger:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Responsive */
@media (max-width: 640px) {
  .dialog-container {
    max-width: 100%;
    max-height: 100vh;
    border-radius: 0;
  }

  .dialog-header,
  .dialog-body,
  .dialog-footer {
    padding: var(--space-4);
  }

  .dialog-icon {
    width: 40px;
    height: 40px;
  }

  .dialog-title {
    font-size: var(--text-lg);
  }
}
</style>
