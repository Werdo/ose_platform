<template>
  <v-layout>
    <!-- Sidebar -->
    <AppSidebar />

    <!-- Main content area -->
    <v-main>
      <!-- Header -->
      <AppHeader />

      <!-- Content -->
      <v-container fluid class="pa-6">
        <router-view />
      </v-container>

      <!-- Footer -->
      <AppFooter />
    </v-main>

    <!-- Global loading overlay -->
    <AppLoading :model-value="isLoading" text="Loading..." />

    <!-- Global notifications -->
    <AppNotification
      v-for="notification in notifications"
      :key="notification.id"
      :model-value="true"
      :type="notification.type"
      :title="notification.title"
      :message="notification.message"
      :timeout="notification.duration"
      @update:model-value="removeNotification(notification.id)"
    />
  </v-layout>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAppStore, AppLoading, AppNotification } from '@ose/shared'
import AppHeader from '@/components/AppHeader.vue'
import AppSidebar from '@/components/AppSidebar.vue'
import AppFooter from '@/components/AppFooter.vue'

const appStore = useAppStore()

// Computed
const isLoading = computed(() => appStore.isLoading)
const notifications = computed(() => appStore.notifications)

// Methods
function removeNotification(id: string) {
  appStore.removeNotification(id)
}
</script>

<script lang="ts">
export default {
  name: 'Layout',
}
</script>

<style scoped>
:deep(.v-main__wrap) {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}
</style>
