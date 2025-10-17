/**
 * CSRF protection API service
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

let csrfToken: string | null = null;

/**
 * Get CSRF token from server
 */
export async function getCsrfToken(): Promise<string> {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/csrf/token`);
    csrfToken = response.data.data.csrf_token;
    return csrfToken;
  } catch (error) {
    console.error('Failed to get CSRF token:', error);
    throw error;
  }
}

/**
 * Get current CSRF token (from cache or fetch new one)
 */
export async function getToken(): Promise<string> {
  if (!csrfToken) {
    await getCsrfToken();
  }
  return csrfToken!;
}

/**
 * Clear cached CSRF token
 */
export function clearToken(): void {
  csrfToken = null;
}

/**
 * Verify CSRF token (for testing)
 */
export async function verifyToken(token: string): Promise<boolean> {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/csrf/verify`, {
      csrf_token: token
    });
    return response.data.data.valid;
  } catch (error) {
    console.error('Failed to verify CSRF token:', error);
    return false;
  }
}
