<template>
  <v-app-bar elevation="1" color="white">
    <!-- Menu toggle button -->
    <v-app-bar-nav-icon @click="toggleSidebar" />

    <!-- Title -->
    <v-toolbar-title class="font-weight-bold">
      {{ pageTitle || 'OSE Platform' }}
    </v-toolbar-title>

    <v-spacer />

    <!-- Theme toggle -->
    <v-btn icon @click="toggleTheme">
      <v-icon>{{ isDarkTheme ? 'mdi-weather-sunny' : 'mdi-weather-night' }}</v-icon>
    </v-btn>

    <!-- Notifications -->
    <v-btn icon>
      <v-badge v-if="notificationCount > 0" :content="notificationCount" color="error">
        <v-icon>mdi-bell</v-icon>
      </v-badge>
      <v-icon v-else>mdi-bell</v-icon>
    </v-btn>

    <!-- User menu -->
    <v-menu>
      <template #activator="{ props }">
        <v-btn icon v-bind="props">
          <v-avatar color="primary" size="36">
            <v-icon>mdi-account</v-icon>
          </v-avatar>
        </v-btn>
      </template>

      <v-list>
        <v-list-item prepend-icon="mdi-account-circle" :title="userName" :subtitle="userEmail" />

        <v-divider />

        <v-list-item prepend-icon="mdi-account" title="Profile" @click="goToProfile" />

        <v-list-item prepend-icon="mdi-cog" title="Settings" @click="goToSettings" />

        <v-divider />

        <v-list-item
          prepend-icon="mdi-logout"
          title="Logout"
          @click="handleLogout"
        />
      </v-list>
    </v-menu>
  </v-app-bar>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth, useAppStore, useNotification } from '@ose/shared'

const router = useRouter()
const appStore = useAppStore()
const { logout, userName, userEmail } = useAuth()
const { showSuccess } = useNotification()

// Computed
const pageTitle = computed(() => appStore.pageTitle)
const isDarkTheme = computed(() => appStore.isDarkTheme)
const notificationCount = computed(() => appStore.notificationCount)

// Methods
function toggleSidebar() {
  appStore.toggleSidebar()
}

function toggleTheme() {
  appStore.toggleTheme()
}

function goToProfile() {
  router.push({ name: 'Profile' })
}

function goToSettings() {
  router.push({ name: 'Settings' })
}

async function handleLogout() {
  try {
    await logout()
    showSuccess('Logged out successfully', 'Goodbye')
    router.push({ name: 'Login' })
  } catch (err) {
    console.error('Logout error:', err)
  }
}
</script>

<script lang="ts">
export default {
  name: 'AppHeader',
}
</script>
