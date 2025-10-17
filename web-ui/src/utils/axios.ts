/**
 * Axios configuration with interceptors
 */
import axios from 'axios';
import { useAuthStore } from '@/stores/auth';
import router from '@/router';
import * as csrfApi from '@/api/csrf';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request interceptor to add auth token and CSRF token
apiClient.interceptors.request.use(
  async (config) => {
    const authEnabled = import.meta.env.VITE_AUTH_ENABLED === 'true';
    const csrfEnabled = import.meta.env.VITE_CSRF_ENABLED !== 'false'; // Enabled by default
    
    // Add auth token if enabled
    if (authEnabled) {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    
    // Add CSRF token for non-GET requests if enabled
    if (csrfEnabled && config.method && !['get', 'head', 'options'].includes(config.method.toLowerCase())) {
      try {
        const csrfToken = await csrfApi.getToken();
        config.headers['X-CSRF-Token'] = csrfToken;
      } catch (error) {
        console.error('Failed to get CSRF token:', error);
      }
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token expiration and CSRF errors
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    const authEnabled = import.meta.env.VITE_AUTH_ENABLED === 'true';
    const csrfEnabled = import.meta.env.VITE_CSRF_ENABLED !== 'false';
    
    // Handle CSRF token errors (403)
    if (csrfEnabled && error.response?.status === 403 && !originalRequest._retryCSRF) {
      originalRequest._retryCSRF = true;
      
      try {
        // Clear and get new CSRF token
        csrfApi.clearToken();
        const csrfToken = await csrfApi.getCsrfToken();
        originalRequest.headers['X-CSRF-Token'] = csrfToken;
        
        return apiClient(originalRequest);
      } catch (csrfError) {
        console.error('Failed to refresh CSRF token:', csrfError);
        return Promise.reject(csrfError);
      }
    }
    
    // Handle auth token expiration (401)
    if (authEnabled && error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const authStore = useAuthStore();
        
        // Try to refresh the token
        await authStore.refresh();
        
        // Retry the original request with new token
        const token = localStorage.getItem('access_token');
        if (token) {
          originalRequest.headers.Authorization = `Bearer ${token}`;
        }
        
        return apiClient(originalRequest);
      } catch (refreshError) {
        // Refresh failed, redirect to login
        const authStore = useAuthStore();
        await authStore.logout();
        router.push({ name: 'Login' });
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

export default apiClient;
