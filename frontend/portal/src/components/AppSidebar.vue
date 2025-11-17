<template>
  <v-navigation-drawer v-model="drawerOpen" :rail="sidebarMini" permanent>
    <!-- Logo / Header -->
    <v-list-item
      :prepend-icon="sidebarMini ? 'mdi-solar-panel' : undefined"
      :title="sidebarMini ? undefined : 'OSE Platform'"
      :subtitle="sidebarMini ? undefined : 'v' + appVersion"
      class="px-2"
    >
      <template v-if="!sidebarMini" #prepend>
        <v-icon color="primary" size="32">mdi-solar-panel</v-icon>
      </template>

      <template v-if="!sidebarMini" #append>
        <v-btn icon size="small" @click="toggleMini">
          <v-icon>mdi-chevron-left</v-icon>
        </v-btn>
      </template>
    </v-list-item>

    <v-divider />

    <!-- Main navigation -->
    <v-list density="compact" nav>
      <v-list-item
        v-for="item in mainMenuItems"
        :key="item.title"
        :prepend-icon="item.icon"
        :title="item.title"
        :value="item.title"
        :to="item.to"
        :active="isActiveRoute(item.to)"
      />
    </v-list>

    <v-divider class="my-2" />

    <!-- Applications -->
    <v-list-subheader v-if="!sidebarMini">APPLICATIONS</v-list-subheader>

    <v-list density="compact" nav>
      <v-list-item
        v-for="app in applications"
        :key="app.title"
        :prepend-icon="app.icon"
        :title="app.title"
        :value="app.title"
        :to="app.to"
      />
    </v-list>

    <!-- Mini toggle button when rail is active -->
    <template #append>
      <div v-if="sidebarMini" class="pa-2 text-center">
        <v-btn icon size="small" @click="toggleMini">
          <v-icon>mdi-chevron-right</v-icon>
        </v-btn>
      </div>
    </template>
  </v-navigation-drawer>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAppStore } from '@ose/shared'

const route = useRoute()
const appStore = useAppStore()

// Computed
const drawerOpen = computed({
  get: () => appStore.sidebarOpen,
  set: (value) => appStore.setSidebarOpen(value),
})

const sidebarMini = computed(() => appStore.sidebarMini)
const appVersion = computed(() => appStore.appVersion)

// Menu items
const mainMenuItems = [
  {
    title: 'Dashboard',
    icon: 'mdi-view-dashboard',
    to: '/',
  },
  {
    title: 'Profile',
    icon: 'mdi-account',
    to: '/profile',
  },
  {
    title: 'Settings',
    icon: 'mdi-cog',
    to: '/settings',
  },
]

// Applications
const applications = [
  {
    title: 'Notificación Series',
    icon: 'mdi-email-multiple',
    to: '/app1',
  },
  {
    title: 'Importación Datos',
    icon: 'mdi-file-import',
    to: '/app2',
  },
  {
    title: 'RMA & Tickets',
    icon: 'mdi-ticket',
    to: '/app3',
  },
  {
    title: 'Import Transform',
    icon: 'mdi-transform',
    to: '/app4',
  },
  {
    title: 'Factura Ticket',
    icon: 'mdi-receipt',
    to: '/app5',
  },
  {
    title: 'Picking Palets',
    icon: 'mdi-package-variant',
    to: '/app6',
  },
]

// Methods
function toggleMini() {
  appStore.toggleSidebarMini()
}

function isActiveRoute(to: string): boolean {
  return route.path === to
}
</script>

<script lang="ts">
export default {
  name: 'AppSidebar',
}
</script>
