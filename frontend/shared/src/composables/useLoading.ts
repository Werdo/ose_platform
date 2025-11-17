/**
 * useLoading Composable
 * Provides loading state management
 */

import { ref } from 'vue'

export function useLoading(initialState = false) {
  const isLoading = ref(initialState)

  function startLoading() {
    isLoading.value = true
  }

  function stopLoading() {
    isLoading.value = false
  }

  function toggleLoading() {
    isLoading.value = !isLoading.value
  }

  /**
   * Wrap an async function with loading state
   */
  async function withLoading<T>(fn: () => Promise<T>): Promise<T> {
    startLoading()
    try {
      return await fn()
    } finally {
      stopLoading()
    }
  }

  return {
    isLoading,
    startLoading,
    stopLoading,
    toggleLoading,
    withLoading,
  }
}
