/**
 * Error handling utilities
 *
 * Provides centralized error logging and handling functions
 */

/**
 * Log error to external service
 * @param error - The error object
 * @param context - Context information for the error
 */
export function logErrorToService(error: unknown, context: string): void {
  // This is a placeholder for error tracking service integration
  // In production, you would send this to Sentry, LogRocket, etc.
  const errorData = {
    message: (error as any)?.message || String(error),
    stack: (error as any)?.stack,
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

/**
 * Setup global error handlers
 */
export function setupGlobalErrorHandlers(): void {
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
}
