<template>
  <Teleport to="body">
    <Transition name="overlay">
      <div v-if="visible" class="loading-overlay" @click="handleClick">
        <div class="loading-content" @click.stop>
          <LoadingSpinner :size="size" :text="text" />
          <button
            v-if="cancellable"
            class="cancel-button"
            @click="handleCancel"
          >
            取消
          </button>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import LoadingSpinner from './LoadingSpinner.vue'

interface Props {
  visible?: boolean
  text?: string
  size?: 'small' | 'medium' | 'large'
  cancellable?: boolean
  closeOnClick?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  visible: false,
  size: 'large',
  cancellable: false,
  closeOnClick: false
})

const emit = defineEmits<{
  cancel: []
  close: []
}>()

const handleClick = () => {
  if (props.closeOnClick) {
    emit('close')
  }
}

const handleCancel = () => {
  emit('cancel')
}
</script>

<style scoped>
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9998;
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-6);
  padding: var(--space-8);
  background-color: var(--color-bg-primary);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  min-width: 200px;
}

.cancel-button {
  padding: var(--space-2) var(--space-6);
  background-color: var(--color-bg-tertiary);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-in-out);
}

.cancel-button:hover {
  background-color: var(--color-border);
  border-color: var(--color-border-hover);
}

/* Overlay animations */
.overlay-enter-active,
.overlay-leave-active {
  transition: opacity var(--duration-normal) var(--ease-in-out);
}

.overlay-enter-active .loading-content,
.overlay-leave-active .loading-content {
  transition: transform var(--duration-normal) var(--ease-in-out);
}

.overlay-enter-from,
.overlay-leave-to {
  opacity: 0;
}

.overlay-enter-from .loading-content {
  transform: scale(0.9);
}

.overlay-leave-to .loading-content {
  transform: scale(0.9);
}
</style>
