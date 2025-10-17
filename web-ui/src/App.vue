<template>
  <ErrorBoundary>
    <router-view />
    <Toast ref="toastRef" />
  </ErrorBoundary>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useAppStore } from './stores/app'
import { useToast } from './composables/useToast'
import ErrorBoundary from './components/ErrorBoundary.vue'
import Toast from './components/Toast.vue'

const appStore = useAppStore()
const { setToastInstance } = useToast()
const toastRef = ref()

onMounted(() => {
  // Initialize app
  appStore.initialize()
  
  // Initialize toast
  if (toastRef.value) {
    setToastInstance(toastRef.value)
  }
})
</script>

<style scoped>
/* App-level styles */
</style>
