<!--
  ThemeToggle Component
  
  A button component for toggling between light and dark themes.
  Includes smooth animations and visual feedback.
  
  Requirements: 6.2
-->

<template>
  <button
    class="theme-toggle"
    :class="{ 'theme-toggle--dark': isDark }"
    @click="handleToggle"
    :aria-label="isDark ? '切换到浅色模式' : '切换到深色模式'"
    :title="isDark ? '切换到浅色模式' : '切换到深色模式'"
  >
    <transition name="icon-fade" mode="out-in">
      <svg
        v-if="isDark"
        key="moon"
        class="theme-toggle__icon"
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
      </svg>
      <svg
        v-else
        key="sun"
        class="theme-toggle__icon"
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <circle cx="12" cy="12" r="5"></circle>
        <line x1="12" y1="1" x2="12" y2="3"></line>
        <line x1="12" y1="21" x2="12" y2="23"></line>
        <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
        <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
        <line x1="1" y1="12" x2="3" y2="12"></line>
        <line x1="21" y1="12" x2="23" y2="12"></line>
        <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
        <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
      </svg>
    </transition>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAppStore } from '../stores/app'

// ============================================================================
// Store
// ============================================================================

const appStore = useAppStore()

// ============================================================================
// Computed
// ============================================================================

const isDark = computed(() => appStore.theme === 'dark')

// ============================================================================
// Methods
// ============================================================================

/**
 * Handle theme toggle with animation
 */
const handleToggle = (): void => {
  // Add ripple effect
  const button = document.querySelector('.theme-toggle') as HTMLElement
  if (button) {
    button.classList.add('theme-toggle--animating')
    setTimeout(() => {
      button.classList.remove('theme-toggle--animating')
    }, 300)
  }

  // Toggle theme
  appStore.toggleTheme()
}
</script>

<style scoped>
.theme-toggle {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
  padding: 0;
  background-color: var(--color-bg-tertiary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--duration-normal) var(--ease-in-out);
  overflow: hidden;
}

.theme-toggle:hover {
  background-color: var(--color-bg-hover);
  border-color: var(--color-border-hover);
  transform: scale(1.05);
}

.theme-toggle:active {
  transform: scale(0.95);
}

.theme-toggle:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

.theme-toggle--dark {
  background-color: var(--color-bg-tertiary);
}

.theme-toggle__icon {
  width: 1.25rem;
  height: 1.25rem;
  color: var(--color-text-primary);
  transition: transform var(--duration-normal) var(--ease-in-out);
}

.theme-toggle:hover .theme-toggle__icon {
  transform: rotate(15deg);
}

.theme-toggle--dark .theme-toggle__icon {
  color: #fbbf24; /* Amber color for moon */
}

/* Animation for theme toggle */
.theme-toggle--animating {
  animation: theme-pulse 0.3s ease-out;
}

@keyframes theme-pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
  }
}

/* Icon transition */
.icon-fade-enter-active,
.icon-fade-leave-active {
  transition: all var(--duration-fast) var(--ease-in-out);
}

.icon-fade-enter-from {
  opacity: 0;
  transform: rotate(-90deg) scale(0.8);
}

.icon-fade-leave-to {
  opacity: 0;
  transform: rotate(90deg) scale(0.8);
}

/* Ripple effect */
.theme-toggle::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  border-radius: 50%;
  background-color: var(--color-primary);
  opacity: 0;
  transform: translate(-50%, -50%);
  transition: width var(--duration-normal) var(--ease-out),
              height var(--duration-normal) var(--ease-out),
              opacity var(--duration-normal) var(--ease-out);
}

.theme-toggle--animating::before {
  width: 100%;
  height: 100%;
  opacity: 0.2;
}

/* Responsive */
@media (max-width: 768px) {
  .theme-toggle {
    width: 2.25rem;
    height: 2.25rem;
  }

  .theme-toggle__icon {
    width: 1.125rem;
    height: 1.125rem;
  }
}
</style>
