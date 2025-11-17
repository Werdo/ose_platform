/**
 * Authentication Store
 * Manages authentication state, user data, and auth operations
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import authService from '@/services/auth.service'
import type { User, LoginCredentials } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  // ============================================================================
  // State
  // ============================================================================

  const user = ref<User | null>(null)
  const accessToken = ref<string | null>(null)
  const refreshToken = ref<string | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // ============================================================================
  // Getters
  // ============================================================================

  const isAuthenticated = computed(() => !!accessToken.value && !!user.value)

  const userRole = computed(() => user.value?.role || null)

  const userName = computed(() => user.value?.name || '')

  const userEmail = computed(() => user.value?.email || '')

  const hasRole = computed(() => (role: string) => {
    return user.value?.role === role
  })

  const hasAnyRole = computed(() => (roles: string[]) => {
    return roles.includes(user.value?.role || '')
  })

  // ============================================================================
  // Actions
  // ============================================================================

  /**
   * Initialize store from localStorage
   */
  function initialize() {
    const storedAccessToken = authService.getAccessToken()
    const storedRefreshToken = authService.getRefreshToken()
    const storedUser = authService.getStoredUser()

    if (storedAccessToken && storedRefreshToken && storedUser) {
      accessToken.value = storedAccessToken
      refreshToken.value = storedRefreshToken
      user.value = storedUser
    }
  }

  /**
   * Login user
   */
  async function login(credentials: LoginCredentials): Promise<void> {
    isLoading.value = true
    error.value = null

    try {
      const response = await authService.login(credentials)

      accessToken.value = response.tokens.access_token
      refreshToken.value = response.tokens.refresh_token
      user.value = response.user

      console.log('✅ Login successful:', user.value)
    } catch (err: any) {
      error.value = err.message || 'Login failed'
      console.error('❌ Login error:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Logout user
   */
  async function logout(): Promise<void> {
    isLoading.value = true
    error.value = null

    try {
      await authService.logout()
    } catch (err: any) {
      console.error('❌ Logout error:', err)
    } finally {
      // Clear state
      accessToken.value = null
      refreshToken.value = null
      user.value = null
      isLoading.value = false

      console.log('✅ Logout successful')
    }
  }

  /**
   * Refresh current user data
   */
  async function refreshUser(): Promise<void> {
    if (!isAuthenticated.value) return

    isLoading.value = true
    error.value = null

    try {
      const updatedUser = await authService.getCurrentUser()
      user.value = updatedUser
      localStorage.setItem('user', JSON.stringify(updatedUser))

      console.log('✅ User data refreshed')
    } catch (err: any) {
      error.value = err.message || 'Failed to refresh user data'
      console.error('❌ Refresh user error:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Refresh access token
   */
  async function refreshAccessToken(): Promise<void> {
    try {
      const newAccessToken = await authService.refreshToken()
      accessToken.value = newAccessToken

      console.log('✅ Access token refreshed')
    } catch (err: any) {
      console.error('❌ Refresh token error:', err)
      // If refresh fails, logout user
      await logout()
      throw err
    }
  }

  /**
   * Request password reset
   */
  async function requestPasswordReset(email: string): Promise<void> {
    isLoading.value = true
    error.value = null

    try {
      await authService.requestPasswordReset(email)
      console.log('✅ Password reset requested')
    } catch (err: any) {
      error.value = err.message || 'Password reset request failed'
      console.error('❌ Password reset request error:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Confirm password reset
   */
  async function confirmPasswordReset(token: string, newPassword: string): Promise<void> {
    isLoading.value = true
    error.value = null

    try {
      await authService.confirmPasswordReset(token, newPassword)
      console.log('✅ Password reset confirmed')
    } catch (err: any) {
      error.value = err.message || 'Password reset failed'
      console.error('❌ Password reset error:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Change password
   */
  async function changePassword(currentPassword: string, newPassword: string): Promise<void> {
    isLoading.value = true
    error.value = null

    try {
      await authService.changePassword(currentPassword, newPassword)
      console.log('✅ Password changed')
    } catch (err: any) {
      error.value = err.message || 'Password change failed'
      console.error('❌ Password change error:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Clear error
   */
  function clearError() {
    error.value = null
  }

  // ============================================================================
  // Listen to logout events
  // ============================================================================

  if (typeof window !== 'undefined') {
    window.addEventListener('auth:logout', () => {
      accessToken.value = null
      refreshToken.value = null
      user.value = null
    })
  }

  // ============================================================================
  // Return store
  // ============================================================================

  return {
    // State
    user,
    accessToken,
    refreshToken,
    isLoading,
    error,

    // Getters
    isAuthenticated,
    userRole,
    userName,
    userEmail,
    hasRole,
    hasAnyRole,

    // Actions
    initialize,
    login,
    logout,
    refreshUser,
    refreshAccessToken,
    requestPasswordReset,
    confirmPasswordReset,
    changePassword,
    clearError,
  }
})
