import { ref } from 'vue'
import type { ToastOptions } from '../components/Toast.vue'

interface ToastInstance {
  addToast: (options: ToastOptions) => number
  removeToast: (id: number) => void
}

const toastInstance = ref<ToastInstance | null>(null)

export function useToast() {
  const setToastInstance = (instance: ToastInstance) => {
    toastInstance.value = instance
  }

  const success = (message: string, duration?: number) => {
    if (!toastInstance.value) {
      console.warn('Toast instance not initialized')
      return
    }
    return toastInstance.value.addToast({
      type: 'success',
      message,
      duration
    })
  }

  const error = (message: string, duration?: number) => {
    if (!toastInstance.value) {
      console.warn('Toast instance not initialized')
      return
    }
    return toastInstance.value.addToast({
      type: 'error',
      message,
      duration
    })
  }

  const warning = (message: string, duration?: number) => {
    if (!toastInstance.value) {
      console.warn('Toast instance not initialized')
      return
    }
    return toastInstance.value.addToast({
      type: 'warning',
      message,
      duration
    })
  }

  const info = (message: string, duration?: number) => {
    if (!toastInstance.value) {
      console.warn('Toast instance not initialized')
      return
    }
    return toastInstance.value.addToast({
      type: 'info',
      message,
      duration
    })
  }

  const remove = (id: number) => {
    if (!toastInstance.value) {
      console.warn('Toast instance not initialized')
      return
    }
    toastInstance.value.removeToast(id)
  }

  return {
    setToastInstance,
    success,
    error,
    warning,
    info,
    remove
  }
}
