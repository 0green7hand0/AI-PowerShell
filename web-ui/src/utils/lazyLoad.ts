/**
 * Lazy load utility for components with loading and error states
 */
import { defineAsyncComponent, Component } from 'vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import ErrorBoundary from '@/components/ErrorBoundary.vue'

interface LazyLoadOptions {
  delay?: number
  timeout?: number
  loadingComponent?: Component
  errorComponent?: Component
}

/**
 * Create a lazy-loaded component with loading and error handling
 */
export function lazyLoadComponent(
  loader: () => Promise<any>,
  options: LazyLoadOptions = {}
) {
  const {
    delay = 200,
    timeout = 30000,
    loadingComponent = LoadingSpinner,
    errorComponent = ErrorBoundary
  } = options

  return defineAsyncComponent({
    loader,
    loadingComponent,
    errorComponent,
    delay,
    timeout,
    suspensible: false
  })
}

/**
 * Preload a component for better performance
 */
export function preloadComponent(loader: () => Promise<any>) {
  return loader()
}

/**
 * Preload multiple components
 */
export function preloadComponents(loaders: Array<() => Promise<any>>) {
  return Promise.all(loaders.map(loader => loader()))
}

/**
 * Create a lazy-loaded route component
 */
export function lazyLoadRoute(importFn: () => Promise<any>) {
  return () => importFn()
}
