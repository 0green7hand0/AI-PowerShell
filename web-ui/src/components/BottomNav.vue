<template>
  <nav class="bottom-nav">
    <router-link
      v-for="item in navItems"
      :key="item.id"
      :to="item.route"
      class="bottom-nav__item"
      :class="{ active: isActive(item.route) }"
    >
      <div class="bottom-nav__icon" v-html="item.icon"></div>
      <span class="bottom-nav__label">{{ item.label }}</span>
    </router-link>
  </nav>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

/**
 * BottomNav - Mobile bottom navigation bar
 * 
 * Provides quick access to main sections on mobile devices
 * Requirements: 6.4
 */

interface NavItem {
  id: string
  label: string
  icon: string
  route: string
}

const route = useRoute()

const navItems = computed<NavItem[]>(() => [
  {
    id: 'chat',
    label: '对话',
    icon: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
    </svg>`,
    route: '/chat'
  },
  {
    id: 'history',
    label: '历史',
    icon: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <polyline points="1 4 1 10 7 10"></polyline>
      <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"></path>
    </svg>`,
    route: '/history'
  },
  {
    id: 'templates',
    label: '模板',
    icon: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
      <polyline points="14 2 14 8 20 8"></polyline>
    </svg>`,
    route: '/templates'
  },
  {
    id: 'logs',
    label: '日志',
    icon: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
      <polyline points="14 2 14 8 20 8"></polyline>
      <line x1="16" y1="13" x2="8" y2="13"></line>
      <line x1="16" y1="17" x2="8" y2="17"></line>
    </svg>`,
    route: '/logs'
  },
  {
    id: 'settings',
    label: '设置',
    icon: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <circle cx="12" cy="12" r="3"></circle>
      <path d="M12 1v6m0 6v6m5.2-13.2l-4.2 4.2m0 6l4.2 4.2M23 12h-6m-6 0H1m18.2-5.2l-4.2 4.2m0 6l4.2 4.2"></path>
    </svg>`,
    route: '/settings'
  }
])

const isActive = (routePath: string) => {
  return route.path === routePath
}
</script>

<style scoped>
.bottom-nav {
  display: none;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 64px;
  background-color: var(--color-bg-primary);
  border-top: 1px solid var(--color-border);
  z-index: 100;
  padding: 0 var(--space-2);
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.05);
}

.bottom-nav__item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-1);
  color: var(--color-text-secondary);
  text-decoration: none;
  transition: all var(--duration-fast) var(--ease-in-out);
  border-radius: var(--radius-md);
  padding: var(--space-1);
  min-width: 0;
}

.bottom-nav__item:active {
  transform: scale(0.95);
  background-color: var(--color-bg-tertiary);
}

.bottom-nav__item.active {
  color: var(--color-primary);
}

.bottom-nav__icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
}

.bottom-nav__icon :deep(svg) {
  width: 24px;
  height: 24px;
}

.bottom-nav__label {
  font-size: 0.625rem;
  font-weight: var(--font-medium);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}

/* Show on mobile */
@media (max-width: 768px) {
  .bottom-nav {
    display: flex;
  }
}

/* Adjust for very small screens */
@media (max-width: 360px) {
  .bottom-nav {
    height: 56px;
  }

  .bottom-nav__icon {
    width: 20px;
    height: 20px;
  }

  .bottom-nav__icon :deep(svg) {
    width: 20px;
    height: 20px;
  }

  .bottom-nav__label {
    font-size: 0.5625rem;
  }
}
</style>
