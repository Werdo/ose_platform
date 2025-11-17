/**
 * OSE Platform - Authentication Service
 */

import apiService from './api.service'
import type { LoginCredentials, AuthResponse, User } from '../types'

const authService = {
  /**
   * Login user with email or employee_id
   */
  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    const response = await apiService.post<any>('/api/v1/auth/login', credentials)

    // Backend returns: { user, tokens: { access_token, refresh_token, ... } }
    // Extract tokens from nested structure
    const tokens = response.tokens || response
    const user = response.user

    // Store tokens
    localStorage.setItem('access_token', tokens.access_token)
    localStorage.setItem('refresh_token', tokens.refresh_token)

    // Store user info if provided
    if (user) {
      localStorage.setItem('user', JSON.stringify(user))
    }

    // Return in expected format
    return {
      access_token: tokens.access_token,
      refresh_token: tokens.refresh_token,
      token_type: tokens.token_type || 'bearer',
      expires_in: tokens.expires_in || 3600,
      user
    }
  },

  /**
   * Logout current user
   */
  logout: async (): Promise<void> => {
    try {
      await apiService.post('/api/v1/auth/logout')
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      // Clear local storage
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
    }
  },

  /**
   * Get current user info
   */
  getCurrentUser: async (): Promise<User> => {
    return await apiService.get<User>('/api/v1/auth/me')
  },

  /**
   * Refresh access token
   */
  refreshToken: async (refreshToken: string): Promise<string> => {
    const response = await apiService.post<{ access_token: string }>('/api/v1/auth/refresh', {
      refresh_token: refreshToken,
    })

    localStorage.setItem('access_token', response.access_token)
    return response.access_token
  },

  /**
   * Check if user is authenticated
   */
  isAuthenticated: (): boolean => {
    const token = localStorage.getItem('access_token')
    const user = localStorage.getItem('user')
    return !!(token && user)
  },

  /**
   * Get stored user from localStorage
   */
  getStoredUser: (): User | null => {
    const userStr = localStorage.getItem('user')
    if (!userStr) return null

    try {
      return JSON.parse(userStr)
    } catch (error) {
      console.error('Error parsing stored user:', error)
      return null
    }
  },

  /**
   * Check if user has specific permission
   */
  hasPermission: (permission: string): boolean => {
    const user = authService.getStoredUser()
    if (!user) return false

    return user.permissions[permission as keyof typeof user.permissions] === true
  },

  /**
   * Check if user has admin role
   */
  isAdmin: (): boolean => {
    const user = authService.getStoredUser()
    return user?.role === 'admin' || false
  },
}

export default authService
