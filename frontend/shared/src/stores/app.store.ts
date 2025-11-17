/**
 * App Store
 * Manages global application state (theme, sidebar, notifications, etc.)
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Notification } from '@/types'

export const useAppStore = defineStore('app', () => {
  // ============================================================================
  // State
  // ============================================================================

  const appTitle = ref('OSE Platform')
  const appVersion = ref('1.0.0')
  const theme = ref<'oseLight' | 'oseDark'>('oseLight')
  const sidebarOpen = ref(true)
  const sidebarMini = ref(false)
  const isLoading = ref(false)
  const notifications = ref<Notification[]>([])
  const pageTitle = ref('')
  const breadcrumbs = ref<{ text: string; to?: string; disabled?: boolean }[]>([])

  // ============================================================================
  // Getters
  // ============================================================================

  const isDarkTheme = computed(() => theme.value === 'oseDark')

  const hasNotifications = computed(() => notifications.value.length > 0)

  const notificationCount = computed(() => notifications.value.length)

  // ============================================================================
  // Actions
  // ============================================================================

  /**
   * Toggle theme
   */
  function toggleTheme() {
    theme.value = theme.value === 'oseLight' ? 'oseDark' : 'oseLight'
    localStorage.setItem('theme', theme.value)
  }

  /**
   * Set theme
   */
  function setTheme(newTheme: 'oseLight' | 'oseDark') {
    theme.value = newTheme
    localStorage.setItem('theme', newTheme)
  }

  /**
   * Initialize theme from localStorage
   */
  function initializeTheme() {
    const savedTheme = localStorage.getItem('theme') as 'oseLight' | 'oseDark' | null
    if (savedTheme) {
      theme.value = savedTheme
    }
  }

  /**
   * Toggle sidebar
   */
  function toggleSidebar() {
    sidebarOpen.value = !sidebarOpen.value
  }

  /**
   * Set sidebar state
   */
  function setSidebarOpen(open: boolean) {
    sidebarOpen.value = open
  }

  /**
   * Toggle sidebar mini
   */
  function toggleSidebarMini() {
    sidebarMini.value = !sidebarMini.value
  }

  /**
   * Set sidebar mini state
   */
  function setSidebarMini(mini: boolean) {
    sidebarMini.value = mini
  }

  /**
   * Show loading overlay
   */
  function showLoading() {
    isLoading.value = true
  }

  /**
   * Hide loading overlay
   */
  function hideLoading() {
    isLoading.value = false
  }

  /**
   * Add notification
   */
  function addNotification(notification: Omit<Notification, 'id'>) {
    const id = `notif_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    const newNotification: Notification = {
      id,
      ...notification,
    }

    notifications.value.push(newNotification)

    // Auto-remove after duration
    if (notification.duration) {
      setTimeout(() => {
        removeNotification(id)
      }, notification.duration)
    }

    return id
  }

  /**
   * Remove notification
   */
  function removeNotification(id: string) {
    const index = notifications.value.findIndex((n) => n.id === id)
    if (index !== -1) {
      notifications.value.splice(index, 1)
    }
  }

  /**
   * Clear all notifications
   */
  function clearNotifications() {
    notifications.value = []
  }

  /**
   * Show success notification
   */
  function showSuccess(message: string, title = 'Success', duration = 5000) {
    return addNotification({
      type: 'success',
      title,
      message,
      duration,
    })
  }

  /**
   * Show error notification
   */
  function showError(message: string, title = 'Error', duration = 7000) {
    return addNotification({
      type: 'error',
      title,
      message,
      duration,
    })
  }

  /**
   * Show warning notification
   */
  function showWarning(message: string, title = 'Warning', duration = 6000) {
    return addNotification({
      type: 'warning',
      title,
      message,
      duration,
    })
  }

  /**
   * Show info notification
   */
  function showInfo(message: string, title = 'Info', duration = 5000) {
    return addNotification({
      type: 'info',
      title,
      message,
      duration,
    })
  }

  /**
   * Set page title
   */
  function setPageTitle(title: string) {
    pageTitle.value = title
    document.title = `${title} - ${appTitle.value}`
  }

  /**
   * Set breadcrumbs
   */
  function setBreadcrumbs(items: { text: string; to?: string; disabled?: boolean }[]) {
    breadcrumbs.value = items
  }

  // ============================================================================
  // Return store
  // ============================================================================

  return {
    // State
    appTitle,
    appVersion,
    theme,
    sidebarOpen,
    sidebarMini,
    isLoading,
    notifications,
    pageTitle,
    breadcrumbs,

    // Getters
    isDarkTheme,
    hasNotifications,
    notificationCount,

    // Actions
    toggleTheme,
    setTheme,
    initializeTheme,
    toggleSidebar,
    setSidebarOpen,
    toggleSidebarMini,
    setSidebarMini,
    showLoading,
    hideLoading,
    addNotification,
    removeNotification,
    clearNotifications,
    showSuccess,
    showError,
    showWarning,
    showInfo,
    setPageTitle,
    setBreadcrumbs,
  }
})
