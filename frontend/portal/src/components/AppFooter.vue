<template>
  <v-footer app class="bg-grey-lighten-3 px-4 py-2">
    <v-row align="center" justify="space-between" no-gutters>
      <v-col cols="auto">
        <span class="text-caption text-medium-emphasis">
          © 2025 Oversun Energy. All rights reserved.
        </span>
      </v-col>

      <v-col cols="auto">
        <span class="text-caption text-medium-emphasis mr-4">
          API: <v-chip size="x-small" :color="apiStatus.color">{{ apiStatus.text }}</v-chip>
        </span>
        <span class="text-caption text-medium-emphasis">
          v{{ appVersion }}
        </span>
      </v-col>
    </v-row>
  </v-footer>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { apiService } from '@ose/shared'

const appVersion = ref(import.meta.env.VITE_APP_VERSION || '1.0.0')
const apiConnected = ref(true)

// Computed
const apiStatus = computed(() => {
  return apiConnected.value
    ? { text: 'Connected', color: 'success' }
    : { text: 'Disconnected', color: 'error' }
})

// Check API connection
async function checkApiConnection() {
  try {
    await apiService.get('/health')
    apiConnected.value = true
  } catch {
    apiConnected.value = false
  }
}

onMounted(() => {
  checkApiConnection()
  // Check API connection every 30 seconds
  setInterval(checkApiConnection, 30000)
})
</script>

<script lang="ts">
export default {
  name: 'AppFooter',
}
</script>
