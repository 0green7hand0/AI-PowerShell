/**
 * Authentication store
 */
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import * as authApi from '@/api/auth';

export const useAuthStore = defineStore('auth', () => {
  // State
  const accessToken = ref<string | null>(localStorage.getItem('access_token'));
  const refreshToken = ref<string | null>(localStorage.getItem('refresh_token'));
  const username = ref<string | null>(localStorage.getItem('username'));
  const role = ref<string | null>(localStorage.getItem('role'));
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  // Getters
  const isAuthenticated = computed(() => !!accessToken.value);
  const isAdmin = computed(() => role.value === 'admin');

  // Actions
  async function login(credentials: authApi.LoginRequest) {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await authApi.login(credentials);
      
      // Store tokens
      accessToken.value = response.access_token;
      refreshToken.value = response.refresh_token;
      username.value = credentials.username;
      
      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('refresh_token', response.refresh_token);
      localStorage.setItem('username', credentials.username);
      
      // Verify token to get user role
      await verify();
      
      return true;
    } catch (err: any) {
      error.value = err.response?.data?.error?.message || 'Login failed';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function refresh() {
    if (!refreshToken.value) {
      throw new Error('No refresh token available');
    }

    try {
      const response = await authApi.refreshToken(refreshToken.value);
      
      accessToken.value = response.access_token;
      localStorage.setItem('access_token', response.access_token);
      
      return true;
    } catch (err: any) {
      // If refresh fails, logout
      await logout();
      throw err;
    }
  }

  async function logout() {
    try {
      await authApi.logout();
    } catch (err) {
      // Ignore errors on logout
      console.error('Logout error:', err);
    } finally {
      // Clear state
      accessToken.value = null;
      refreshToken.value = null;
      username.value = null;
      role.value = null;
      
      // Clear localStorage
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('username');
      localStorage.removeItem('role');
    }
  }

  async function verify() {
    try {
      const response = await authApi.verifyToken();
      username.value = response.username;
      role.value = response.role;
      
      localStorage.setItem('username', response.username);
      localStorage.setItem('role', response.role);
      
      return true;
    } catch (err) {
      // If verification fails, logout
      await logout();
      throw err;
    }
  }

  // Initialize auth state on store creation
  async function initialize() {
    if (accessToken.value) {
      try {
        await verify();
      } catch (err) {
        // Token is invalid, clear it
        await logout();
      }
    }
  }

  return {
    // State
    accessToken,
    refreshToken,
    username,
    role,
    isLoading,
    error,
    
    // Getters
    isAuthenticated,
    isAdmin,
    
    // Actions
    login,
    refresh,
    logout,
    verify,
    initialize
  };
});
