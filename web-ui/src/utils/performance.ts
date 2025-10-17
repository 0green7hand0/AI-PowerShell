/**
 * Performance monitoring utilities
 */

interface PerformanceMetrics {
  fcp?: number // First Contentful Paint
  lcp?: number // Largest Contentful Paint
  fid?: number // First Input Delay
  cls?: number // Cumulative Layout Shift
  ttfb?: number // Time to First Byte
}

/**
 * Measure and log performance metrics
 */
export function measurePerformance(): PerformanceMetrics {
  const metrics: PerformanceMetrics = {}

  if ('performance' in window) {
    // Get navigation timing
    const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming
    if (navigation) {
      metrics.ttfb = navigation.responseStart - navigation.requestStart
    }

    // Get paint timing
    const paintEntries = performance.getEntriesByType('paint')
    paintEntries.forEach((entry) => {
      if (entry.name === 'first-contentful-paint') {
        metrics.fcp = entry.startTime
      }
    })

    // Log metrics in development
    if (import.meta.env.DEV) {
      console.log('Performance Metrics:', metrics)
    }
  }

  return metrics
}

/**
 * Observe Largest Contentful Paint
 */
export function observeLCP(callback: (value: number) => void): void {
  if ('PerformanceObserver' in window) {
    try {
      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntries()
        const lastEntry = entries[entries.length - 1]
        callback(lastEntry.startTime)
      })
      observer.observe({ entryTypes: ['largest-contentful-paint'] })
    } catch (e) {
      console.warn('LCP observation not supported')
    }
  }
}

/**
 * Observe First Input Delay
 */
export function observeFID(callback: (value: number) => void): void {
  if ('PerformanceObserver' in window) {
    try {
      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntries()
        entries.forEach((entry: any) => {
          callback(entry.processingStart - entry.startTime)
        })
      })
      observer.observe({ entryTypes: ['first-input'] })
    } catch (e) {
      console.warn('FID observation not supported')
    }
  }
}

/**
 * Observe Cumulative Layout Shift
 */
export function observeCLS(callback: (value: number) => void): void {
  if ('PerformanceObserver' in window) {
    try {
      let clsValue = 0
      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntries()
        entries.forEach((entry: any) => {
          if (!entry.hadRecentInput) {
            clsValue += entry.value
            callback(clsValue)
          }
        })
      })
      observer.observe({ entryTypes: ['layout-shift'] })
    } catch (e) {
      console.warn('CLS observation not supported')
    }
  }
}

/**
 * Debounce function for performance
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: ReturnType<typeof setTimeout> | null = null

  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      timeout = null
      func(...args)
    }

    if (timeout) {
      clearTimeout(timeout)
    }
    timeout = setTimeout(later, wait)
  }
}

/**
 * Throttle function for performance
 */
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean = false

  return function executedFunction(...args: Parameters<T>) {
    if (!inThrottle) {
      func(...args)
      inThrottle = true
      setTimeout(() => {
        inThrottle = false
      }, limit)
    }
  }
}

/**
 * Request idle callback wrapper
 */
export function runWhenIdle(callback: () => void, timeout = 2000): void {
  if ('requestIdleCallback' in window) {
    requestIdleCallback(callback, { timeout })
  } else {
    setTimeout(callback, timeout)
  }
}

/**
 * Prefetch resource
 */
export function prefetchResource(url: string, as: string = 'fetch'): void {
  const link = document.createElement('link')
  link.rel = 'prefetch'
  link.as = as
  link.href = url
  document.head.appendChild(link)
}

/**
 * Preconnect to origin
 */
export function preconnect(url: string): void {
  const link = document.createElement('link')
  link.rel = 'preconnect'
  link.href = url
  document.head.appendChild(link)
}

/**
 * Monitor long tasks
 */
export function monitorLongTasks(callback: (duration: number) => void): void {
  if ('PerformanceObserver' in window) {
    try {
      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntries()
        entries.forEach((entry) => {
          callback(entry.duration)
        })
      })
      observer.observe({ entryTypes: ['longtask'] })
    } catch (e) {
      console.warn('Long task monitoring not supported')
    }
  }
}
