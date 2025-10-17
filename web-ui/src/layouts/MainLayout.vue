<template>
  <div class="main-layout" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
    <!-- Mobile Overlay -->
    <transition name="overlay-fade">
      <div 
        v-if="!sidebarCollapsed && isMobile" 
        class="mobile-overlay"
        @click="toggleSidebar"
      ></div>
    </transition>

    <!-- Sidebar -->
    <Sidebar 
      :collapsed="sidebarCollapsed"
      :is-mobile="isMobile"
      @toggle="toggleSidebar"
    />

    <!-- Main Content Area -->
    <main ref="mainContentRef" class="main-content">
      <!-- Top Bar -->
      <div class="top-bar">
        <button 
          class="sidebar-toggle-btn"
          @click="toggleSidebar"
          :aria-label="sidebarCollapsed ? '展开侧边栏' : '收起侧边栏'"
        >
          <svg 
            xmlns="http://www.w3.org/2000/svg" 
            width="20" 
            height="20" 
            viewBox="0 0 24 24" 
            fill="none" 
            stroke="currentColor" 
            stroke-width="2" 
            stroke-linecap="round" 
            stroke-linejoin="round"
          >
            <line x1="3" y1="12" x2="21" y2="12"></line>
            <line x1="3" y1="6" x2="21" y2="6"></line>
            <line x1="3" y1="18" x2="21" y2="18"></line>
          </svg>
        </button>

        <div class="top-bar-title">
          <h1>{{ pageTitle }}</h1>
        </div>

        <div class="top-bar-actions">
          <!-- Theme Toggle -->
          <ThemeToggle />
        </div>
      </div>

      <!-- Page Content -->
      <div class="page-content">
        <router-view v-slot="{ Component }">
          <transition name="page-fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </main>

    <!-- Bottom Navigation (Mobile Only) -->
    <BottomNav v-if="isMobile" />
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAppStore } from '../stores/app'
import { useSwipe } from '../composables/useSwipe'
import Sidebar from '../components/Sidebar.vue'
import ThemeToggle from '../components/ThemeToggle.vue'
import BottomNav from '../components/BottomNav.vue'

const route = useRoute()
const appStore = useAppStore()

const isMobile = ref(false)
const mainContentRef = ref<HTMLElement | null>(null)
const isKeyboardVisible = ref(false)

const sidebarCollapsed = computed(() => appStore.sidebarCollapsed)

const pageTitle = computed(() => {
  return (route.meta.title as string) || 'AI PowerShell Assistant'
})

// Setup swipe gesture for mobile
const { direction } = useSwipe(mainContentRef, {
  threshold: 80,
  timeout: 300
})

// Watch for swipe gestures
watch(direction, (newDirection) => {
  if (!isMobile.value) return

  if (newDirection === 'right' && sidebarCollapsed.value) {
    // Swipe right to open sidebar
    appStore.toggleSidebar()
  } else if (newDirection === 'left' && !sidebarCollapsed.value) {
    // Swipe left to close sidebar
    appStore.toggleSidebar()
  }
})

const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
  // Auto-collapse sidebar on mobile
  if (isMobile.value && !sidebarCollapsed.value) {
    appStore.toggleSidebar()
  }
}

const toggleSidebar = () => {
  appStore.toggleSidebar()
}

// Detect virtual keyboard visibility
const handleFocusIn = () => {
  if (isMobile.value) {
    isKeyboardVisible.value = true
    document.body.classList.add('keyboard-visible')
  }
}

const handleFocusOut = () => {
  if (isMobile.value) {
    isKeyboardVisible.value = false
    document.body.classList.remove('keyboard-visible')
  }
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
  
  // Listen for input focus events
  document.addEventListener('focusin', handleFocusIn)
  document.addEventListener('focusout', handleFocusOut)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
  document.removeEventListener('focusin', handleFocusIn)
  document.removeEventListener('focusout', handleFocusOut)
})
</script>

<style scoped>
.main-layout {
  display: flex;
  width: 100%;
  height: 100vh;
  overflow: hidden;
  background-color: var(--color-bg-secondary);
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: margin-left var(--duration-normal) var(--ease-in-out);
}

.top-bar {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-4) var(--space-6);
  background-color: var(--color-bg-primary);
  border-bottom: 1px solid var(--color-border);
  height: 64px;
  flex-shrink: 0;
}

.sidebar-toggle-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border: none;
  background-color: transparent;
  color: var(--color-text-secondary);
  border-radius: 8px;
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-in-out);
}

.sidebar-toggle-btn:hover {
  background-color: var(--color-bg-tertiary);
  color: var(--color-text-primary);
}

.top-bar-title {
  flex: 1;
}

.top-bar-title h1 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.top-bar-actions {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.page-content {
  flex: 1;
  overflow: auto;
  padding: var(--space-6);
}

/* Page transition animations */
.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity var(--duration-normal) var(--ease-in-out),
              transform var(--duration-normal) var(--ease-in-out);
}

.page-fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.page-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* Mobile Overlay */
.mobile-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 999;
  backdrop-filter: blur(2px);
}

.overlay-fade-enter-active,
.overlay-fade-leave-active {
  transition: opacity var(--duration-normal) var(--ease-in-out);
}

.overlay-fade-enter-from,
.overlay-fade-leave-to {
  opacity: 0;
}

/* Responsive Design */
@media (max-width: 768px) {
  .page-content {
    padding: var(--space-3);
    padding-bottom: calc(64px + var(--space-3)); /* Account for bottom nav */
  }

  .top-bar {
    padding: var(--space-3) var(--space-4);
    height: 56px;
  }

  .top-bar-title h1 {
    font-size: 1rem;
  }

  .sidebar-toggle-btn {
    width: 36px;
    height: 36px;
  }
}

@media (max-width: 480px) {
  .page-content {
    padding: var(--space-2);
    padding-bottom: calc(64px + var(--space-2)); /* Account for bottom nav */
  }

  .top-bar {
    padding: var(--space-2) var(--space-3);
    height: 52px;
    gap: var(--space-2);
  }

  .top-bar-title h1 {
    font-size: 0.875rem;
  }
}
</style>
