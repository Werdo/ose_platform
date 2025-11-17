/**
 * useNotification Composable
 * Provides easy-to-use notification methods
 */

import { useAppStore } from '@/stores/app.store'

export function useNotification() {
  const appStore = useAppStore()

  function showSuccess(message: string, title = 'Success') {
    return appStore.showSuccess(message, title)
  }

  function showError(message: string, title = 'Error') {
    return appStore.showError(message, title)
  }

  function showWarning(message: string, title = 'Warning') {
    return appStore.showWarning(message, title)
  }

  function showInfo(message: string, title = 'Info') {
    return appStore.showInfo(message, title)
  }

  /**
   * Show API error notification
   */
  function showApiError(error: any, defaultMessage = 'An error occurred') {
    const message = error?.response?.data?.detail || error?.message || defaultMessage
    return showError(message, 'API Error')
  }

  /**
   * Show validation error notification
   */
  function showValidationError(errors: string | string[]) {
    const message = Array.isArray(errors) ? errors.join(', ') : errors
    return showError(message, 'Validation Error')
  }

  return {
    showSuccess,
    showError,
    showWarning,
    showInfo,
    showApiError,
    showValidationError,
  }
}
