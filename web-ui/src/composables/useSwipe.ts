import { ref, onMounted, onUnmounted, Ref } from 'vue'

/**
 * Swipe direction
 */
export type SwipeDirection = 'left' | 'right' | 'up' | 'down' | 'none'

/**
 * Swipe options
 */
export interface SwipeOptions {
  threshold?: number // Minimum distance to trigger swipe (px)
  timeout?: number // Maximum time for swipe (ms)
  passive?: boolean // Use passive event listeners
}

/**
 * Swipe composable for touch gesture support
 * 
 * Provides swipe detection for mobile devices
 * Requirements: 6.4
 */
export function useSwipe(
  target: Ref<HTMLElement | null>,
  options: SwipeOptions = {}
) {
  const {
    threshold = 50,
    timeout = 500,
    passive = true
  } = options

  const isSwiping = ref(false)
  const direction = ref<SwipeDirection>('none')
  const lengthX = ref(0)
  const lengthY = ref(0)

  let startX = 0
  let startY = 0
  let startTime = 0

  /**
   * Handle touch start
   */
  const onTouchStart = (e: TouchEvent) => {
    const touch = e.touches[0]
    startX = touch.clientX
    startY = touch.clientY
    startTime = Date.now()
    isSwiping.value = true
    direction.value = 'none'
    lengthX.value = 0
    lengthY.value = 0
  }

  /**
   * Handle touch move
   */
  const onTouchMove = (e: TouchEvent) => {
    if (!isSwiping.value) return

    const touch = e.touches[0]
    lengthX.value = touch.clientX - startX
    lengthY.value = touch.clientY - startY
  }

  /**
   * Handle touch end
   */
  const onTouchEnd = () => {
    if (!isSwiping.value) return

    const duration = Date.now() - startTime
    const absX = Math.abs(lengthX.value)
    const absY = Math.abs(lengthY.value)

    // Check if swipe is valid
    if (duration <= timeout && (absX >= threshold || absY >= threshold)) {
      // Determine direction
      if (absX > absY) {
        direction.value = lengthX.value > 0 ? 'right' : 'left'
      } else {
        direction.value = lengthY.value > 0 ? 'down' : 'up'
      }
    }

    isSwiping.value = false
  }

  /**
   * Setup event listeners
   */
  const setup = () => {
    const el = target.value
    if (!el) return

    el.addEventListener('touchstart', onTouchStart, { passive })
    el.addEventListener('touchmove', onTouchMove, { passive })
    el.addEventListener('touchend', onTouchEnd, { passive })
  }

  /**
   * Cleanup event listeners
   */
  const cleanup = () => {
    const el = target.value
    if (!el) return

    el.removeEventListener('touchstart', onTouchStart)
    el.removeEventListener('touchmove', onTouchMove)
    el.removeEventListener('touchend', onTouchEnd)
  }

  onMounted(setup)
  onUnmounted(cleanup)

  return {
    isSwiping,
    direction,
    lengthX,
    lengthY
  }
}
