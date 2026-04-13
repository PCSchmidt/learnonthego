/**
 * Authentication Service - Handles user authentication flows
 * Integrates with backend JWT authentication system
 */

import AsyncStorage from '@react-native-async-storage/async-storage';
import apiClient, { ApiResponse, STORAGE_KEYS } from './api';

// User Types
export interface User {
  id: number;
  email: string;
  full_name: string;
  subscription_tier: 'free' | 'premium' | 'enterprise';
  created_at: string;
  last_login_at?: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  confirmPassword: string;
  full_name?: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token?: string;
  token_type: string;
  user: User;
}

// Authentication Service Class
class AuthService {
  // Register new user
  async register(data: RegisterData): Promise<ApiResponse<AuthResponse>> {
    const response = await apiClient.post<AuthResponse>('/api/auth/register', {
      email: data.email,
      password: data.password,
      confirm_password: data.confirmPassword,
      full_name: data.full_name || 'User',
    });

    if (response.success && response.data) {
      // Store authentication data
      await this.storeAuthData(response.data);
    }

    return response;
  }

  // Login existing user
  async login(credentials: LoginCredentials): Promise<ApiResponse<AuthResponse>> {
    const response = await apiClient.post<AuthResponse>('/api/auth/login', credentials);

    if (response.success && response.data) {
      // Store authentication data
      await this.storeAuthData(response.data);
    }

    return response;
  }

  // Get current user profile
  async getCurrentUser(): Promise<ApiResponse<User>> {
    return apiClient.get<User>('/api/auth/me');
  }

  // Refresh authentication token
  async refreshToken(): Promise<ApiResponse<AuthResponse>> {
    const refreshToken = await AsyncStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN);
    
    if (!refreshToken) {
      return {
        success: false,
        error: 'No refresh token available',
      };
    }

    const response = await apiClient.post<AuthResponse>('/api/auth/refresh', {
      refresh_token: refreshToken,
    });

    if (response.success && response.data) {
      await this.storeAuthData(response.data);
    }

    return response;
  }

  // Logout user
  async logout(): Promise<ApiResponse<{ message: string }>> {
    const response = await apiClient.post<{ message: string }>('/api/auth/logout');
    
    // Clear local storage regardless of API response
    await apiClient.removeAuthToken();
    
    return response;
  }

  // Check if user is authenticated
  async isAuthenticated(): Promise<boolean> {
    try {
      const token = await AsyncStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
      
      if (!token) {
        return false;
      }

      // Verify token with backend
      const response = await this.getCurrentUser();
      return response.success;
    } catch (error) {
      return false;
    }
  }

  // Get stored user data
  async getStoredUser(): Promise<User | null> {
    try {
      const userData = await AsyncStorage.getItem(STORAGE_KEYS.USER_DATA);
      return userData ? JSON.parse(userData) : null;
    } catch (error) {
      console.error('Error retrieving stored user:', error);
      return null;
    }
  }

  // Store authentication data securely
  private async storeAuthData(authData: AuthResponse): Promise<void> {
    try {
      await Promise.all([
        apiClient.storeAuthToken(authData.access_token),
        AsyncStorage.setItem(STORAGE_KEYS.USER_DATA, JSON.stringify(authData.user)),
        authData.refresh_token
          ? AsyncStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, authData.refresh_token)
          : Promise.resolve(),
      ]);
    } catch (error) {
      console.error('Error storing auth data:', error);
    }
  }

  // Request password reset
  async requestPasswordReset(email: string): Promise<ApiResponse<{ message: string }>> {
    return apiClient.post<{ message: string }>('/api/auth/password-reset-request', {
      email,
    });
  }
}

// Export singleton instance
export const authService = new AuthService();
export default authService;
