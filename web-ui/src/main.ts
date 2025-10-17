import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './style.css'
import './styles/highlight-themes.css'
import App from './App.vue'
import router from './router'
import { measurePerformance, observeLCP, observeFID, observeCLS, preconnect } from './utils/performance'

// Preconnect to API server for faster requests
if (import.meta.env.VITE_API_BASE_URL) {
  preconnect(import.meta.env.VITE_API_BASE_URL)
}

const app = createApp(App)
const pinia = createPinia()

// Global error handler
app.config.errorHandler = (err, instance, info) => {
  console.error('Global error:', err)
  console.error('Error info:', info)
  console.error('Component instance:', instance)
  
  // Log error to external service in production
  if (import.meta.env.PROD) {
    // TODO: Send to error tracking service (e.g., Sentry)
    logErrorToService(err, info)
  }
}

// Global warning handler (development only)
if (import.meta.env.DEV) {
  app.config.warnHandler = (msg, instance, trace) => {
    console.warn('Vue warning:', msg)
    console.warn('Trace:', trace)
  }
}

// Handle unhandled promise rejections
window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled promise rejection:', event.reason)
  
  if (import.meta.env.PROD) {
    logErrorToService(event.reason, 'unhandledrejection')
  }
  
  // Prevent default browser error handling
  event.preventDefault()
})

// Handle global errors
window.addEventListener('error', (event) => {
  console.error('Global error event:', event.error)
  
  if (import.meta.env.PROD) {
    logErrorToService(event.error, 'error')
  }
})

// Error logging function
function logErrorToService(error: any, context: string) {
  // This is a placeholder for error tracking service integration
  // In production, you would send this to Sentry, LogRocket, etc.
  const errorData = {
    message: error?.message || String(error),
    stack: error?.stack,
    context,
    timestamp: new Date().toISOString(),
    userAgent: navigator.userAgent,
    url: window.location.href
  }
  
  console.log('Error logged:', errorData)
  
  // Example: Send to backend API
  // fetch('/api/logs/error', {
  //   method: 'POST',
  //   headers: { 'Content-Type': 'application/json' },
  //   body: JSON.stringify(errorData)
  // }).catch(console.error)
}

app.use(pinia)
app.use(router)
app.use(ElementPlus)

app.mount('#app')

// Measure performance metrics after app is mounted
if (import.meta.env.PROD || import.meta.env.VITE_ENABLE_ANALYTICS === 'true') {
  // Measure initial performance
  setTimeout(() => {
    const metrics = measurePerformance()
    console.log('Initial Performance Metrics:', metrics)
  }, 0)

  // Observe Core Web Vitals
  observeLCP((value) => {
    console.log('LCP:', value)
  })

  observeFID((value) => {
    console.log('FID:', value)
  })

  observeCLS((value) => {
    console.log('CLS:', value)
  })
}
