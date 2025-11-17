/**
 * Authentication Service
 * Handles login, logout, token refresh, and password reset
 */

import apiService from './api.service'
import type { LoginCredentials, AuthTokens, User } from '@/types'

class AuthService {
  /**
   * Login user
   */
  async login(credentials: LoginCredentials): Promise<{ tokens: AuthTokens; user: User }> {
    try {
      // Backend expects form data for OAuth2 password flow
      const formData = new URLSearchParams()
      formData.append('username', credentials.email)
      formData.append('password', credentials.password)

      const response = await apiService.post<{
        access_token: string
        refresh_token: string
        token_type: string
      }>('/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      })

      // Save tokens to localStorage
      localStorage.setItem('access_token', response.access_token)
      localStorage.setItem('refresh_token', response.refresh_token)

      // Fetch user data
      const user = await this.getCurrentUser()

      // Save user to localStorage
      localStorage.setItem('user', JSON.stringify(user))

      return {
        tokens: {
          access_token: response.access_token,
          refresh_token: response.refresh_token,
          token_type: response.token_type,
        },
        user,
      }
    } catch (error: any) {
      console.error('Login error:', error)
      throw new Error(error.response?.data?.detail || 'Login failed')
    }
  }

  /**
   * Logout user
   */
  async logout(): Promise<void> {
    try {
      // Call backend logout endpoint
      await apiService.post('/auth/logout')
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      // Clear local storage regardless of API call success
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')

      // Dispatch logout event
      window.dispatchEvent(new CustomEvent('auth:logout'))
    }
  }

  /**
   * Get current logged-in user
   */
  async getCurrentUser(): Promise<User> {
    try {
      const user = await apiService.get<User>('/auth/me')
      return user
    } catch (error: any) {
      console.error('Get current user error:', error)
      throw new Error(error.response?.data?.detail || 'Failed to get user data')
    }
  }

  /**
   * Refresh access token
   */
  async refreshToken(): Promise<string> {
    try {
      const refreshToken = localStorage.getItem('refresh_token')

      if (!refreshToken) {
        throw new Error('No refresh token available')
      }

      const response = await apiService.post<{ access_token: string }>('/auth/refresh', {
        refresh_token: refreshToken,
      })

      // Save new access token
      localStorage.setItem('access_token', response.access_token)

      return response.access_token
    } catch (error: any) {
      console.error('Refresh token error:', error)
      // Clear auth data on refresh failure
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
      throw new Error(error.response?.data?.detail || 'Token refresh failed')
    }
  }

  /**
   * Request password reset
   */
  async requestPasswordReset(email: string): Promise<void> {
    try {
      await apiService.post('/auth/password-reset', { email })
    } catch (error: any) {
      console.error('Password reset request error:', error)
      throw new Error(error.response?.data?.detail || 'Password reset request failed')
    }
  }

  /**
   * Confirm password reset with token
   */
  async confirmPasswordReset(token: string, newPassword: string): Promise<void> {
    try {
      await apiService.post('/auth/password-reset/confirm', {
        token,
        new_password: newPassword,
      })
    } catch (error: any) {
      console.error('Password reset confirmation error:', error)
      throw new Error(error.response?.data?.detail || 'Password reset failed')
    }
  }

  /**
   * Change password for logged-in user
   */
  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    try {
      await apiService.post('/auth/change-password', {
        current_password: currentPassword,
        new_password: newPassword,
      })
    } catch (error: any) {
      console.error('Change password error:', error)
      throw new Error(error.response?.data?.detail || 'Password change failed')
    }
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    const token = localStorage.getItem('access_token')
    return !!token
  }

  /**
   * Get stored access token
   */
  getAccessToken(): string | null {
    return localStorage.getItem('access_token')
  }

  /**
   * Get stored refresh token
   */
  getRefreshToken(): string | null {
    return localStorage.getItem('refresh_token')
  }

  /**
   * Get stored user data
   */
  getStoredUser(): User | null {
    const userStr = localStorage.getItem('user')
    if (!userStr) return null

    try {
      return JSON.parse(userStr) as User
    } catch {
      return null
    }
  }
}

// Export singleton instance
export default new AuthService()
