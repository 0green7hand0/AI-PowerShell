/**
 * Authentication API service
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  expires_in: number;
  token_type: string;
}

export interface RefreshRequest {
  refresh_token: string;
}

export interface RefreshResponse {
  access_token: string;
  expires_in: number;
  token_type: string;
}

export interface VerifyResponse {
  username: string;
  role: string;
}

/**
 * Login with username and password
 */
export async function login(credentials: LoginRequest): Promise<LoginResponse> {
  const response = await axios.post(`${API_BASE_URL}/api/auth/login`, credentials);
  return response.data.data;
}

/**
 * Refresh access token using refresh token
 */
export async function refreshToken(refreshToken: string): Promise<RefreshResponse> {
  const response = await axios.post(`${API_BASE_URL}/api/auth/refresh`, {
    refresh_token: refreshToken
  });
  return response.data.data;
}

/**
 * Logout (client-side token removal)
 */
export async function logout(): Promise<void> {
  const token = localStorage.getItem('access_token');
  if (token) {
    try {
      await axios.post(`${API_BASE_URL}/api/auth/logout`, {}, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
    } catch (error) {
      // Ignore errors on logout
      console.error('Logout error:', error);
    }
  }
}

/**
 * Verify current token
 */
export async function verifyToken(): Promise<VerifyResponse> {
  const token = localStorage.getItem('access_token');
  if (!token) {
    throw new Error('No token found');
  }
  
  const response = await axios.get(`${API_BASE_URL}/api/auth/verify`, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });
  return response.data.data;
}
