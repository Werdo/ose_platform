/**
 * useAuth Composable
 * Provides authentication utilities and shortcuts
 */

import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth.store'
import type { LoginCredentials } from '@/types'

export function useAuth() {
  const authStore = useAuthStore()

  // Computed properties
  const isAuthenticated = computed(() => authStore.isAuthenticated)
  const user = computed(() => authStore.user)
  const userRole = computed(() => authStore.userRole)
  const userName = computed(() => authStore.userName)
  const userEmail = computed(() => authStore.userEmail)
  const isLoading = computed(() => authStore.isLoading)
  const error = computed(() => authStore.error)

  // Methods
  async function login(credentials: LoginCredentials) {
    await authStore.login(credentials)
  }

  async function logout() {
    await authStore.logout()
  }

  async function refreshUser() {
    await authStore.refreshUser()
  }

  async function changePassword(currentPassword: string, newPassword: string) {
    await authStore.changePassword(currentPassword, newPassword)
  }

  function hasRole(role: string): boolean {
    return authStore.user?.role === role
  }

  function hasAnyRole(roles: string[]): boolean {
    return roles.includes(authStore.user?.role || '')
  }

  function clearError() {
    authStore.clearError()
  }

  return {
    // State
    isAuthenticated,
    user,
    userRole,
    userName,
    userEmail,
    isLoading,
    error,

    // Methods
    login,
    logout,
    refreshUser,
    changePassword,
    hasRole,
    hasAnyRole,
    clearError,
  }
}
