import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import MainLayout from '../layouts/MainLayout.vue'
import { useAuthStore } from '@/stores/auth'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginView.vue'),
    meta: { 
      title: '登录',
      requiresAuth: false,
      hideForAuth: true
    }
  },
  {
    path: '/',
    component: MainLayout,
    redirect: '/chat',
    children: [
      {
        path: '/chat',
        name: 'Chat',
        component: () => import('../views/ChatView.vue'),
        meta: { 
          title: '对话',
          requiresAuth: false
        }
      },
      {
        path: '/history',
        name: 'History',
        component: () => import('../views/HistoryView.vue'),
        meta: { 
          title: '历史记录',
          requiresAuth: false
        }
      },
      {
        path: '/templates',
        name: 'Templates',
        component: () => import('../views/TemplateView.vue'),
        meta: { 
          title: '模板管理',
          requiresAuth: false
        }
      },
      {
        path: '/logs',
        name: 'Logs',
        component: () => import('../views/LogsView.vue'),
        meta: { 
          title: '日志',
          requiresAuth: false
        }
      },
      {
        path: '/settings',
        name: 'Settings',
        component: () => import('../views/SettingsView.vue'),
        meta: { 
          title: '设置',
          requiresAuth: false
        }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    redirect: '/chat'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard
router.beforeEach(async (to, from, next) => {
  // Set page title
  if (to.meta.title) {
    document.title = `${to.meta.title} - AI PowerShell Assistant`
  } else {
    document.title = 'AI PowerShell Assistant'
  }

  // Check if authentication is enabled (from environment variable)
  const authEnabled = import.meta.env.VITE_AUTH_ENABLED === 'true'
  
  if (!authEnabled) {
    // Authentication is disabled, allow all routes
    next()
    return
  }

  const authStore = useAuthStore()
  
  // If route requires auth and user is not authenticated
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
    return
  }
  
  // If user is authenticated and trying to access login page
  if (to.meta.hideForAuth && authStore.isAuthenticated) {
    next({ name: 'Chat' })
    return
  }
  
  next()
})

// After navigation hook for analytics or logging
router.afterEach((to, from) => {
  // Log navigation for debugging
  if (import.meta.env.DEV) {
    console.log(`Navigated from ${from.path} to ${to.path}`)
  }
})

export default router
