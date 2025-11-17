<template>
  <div>
    <!-- Page header -->
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 font-weight-bold mb-2">Dashboard</h1>
        <p class="text-subtitle-1 text-medium-emphasis">
          Welcome back, {{ userName }}! Here's an overview of the OSE Platform.
        </p>
      </v-col>
    </v-row>

    <v-divider class="my-6" />

    <!-- Stats cards -->
    <v-row>
      <v-col v-for="stat in stats" :key="stat.title" cols="12" sm="6" md="3">
        <v-card>
          <v-card-text>
            <div class="d-flex justify-space-between align-center">
              <div>
                <div class="text-overline text-medium-emphasis">{{ stat.title }}</div>
                <div class="text-h4 font-weight-bold">{{ stat.value }}</div>
                <div class="text-caption" :class="stat.changeColor">
                  <v-icon size="small">{{ stat.changeIcon }}</v-icon>
                  {{ stat.change }}
                </div>
              </div>
              <v-avatar :color="stat.color" size="56">
                <v-icon size="32">{{ stat.icon }}</v-icon>
              </v-avatar>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Quick access cards -->
    <v-row class="mt-6">
      <v-col cols="12">
        <h2 class="text-h5 font-weight-bold mb-4">Quick Access</h2>
      </v-col>

      <v-col v-for="app in applications" :key="app.title" cols="12" sm="6" md="4">
        <v-card hover @click="goToApp(app.route)" class="cursor-pointer">
          <v-card-text class="pa-6">
            <div class="d-flex align-center mb-4">
              <v-avatar :color="app.color" size="48" class="mr-4">
                <v-icon size="28" color="white">{{ app.icon }}</v-icon>
              </v-avatar>
              <div>
                <div class="text-h6 font-weight-bold">{{ app.title }}</div>
                <div class="text-caption text-medium-emphasis">{{ app.subtitle }}</div>
              </div>
            </div>
            <v-divider class="my-3" />
            <p class="text-body-2 text-medium-emphasis">
              {{ app.description }}
            </p>
          </v-card-text>

          <v-card-actions>
            <v-btn variant="text" color="primary" append-icon="mdi-arrow-right">
              Open
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <!-- Recent activity -->
    <v-row class="mt-6">
      <v-col cols="12" md="8">
        <v-card>
          <v-card-title class="d-flex justify-space-between align-center">
            <span>Recent Activity</span>
            <v-btn variant="text" size="small">View All</v-btn>
          </v-card-title>
          <v-divider />
          <v-card-text>
            <v-timeline side="end" density="compact">
              <v-timeline-item
                v-for="(activity, index) in recentActivities"
                :key="index"
                :dot-color="activity.color"
                size="small"
              >
                <div class="mb-4">
                  <div class="font-weight-bold">{{ activity.title }}</div>
                  <div class="text-caption text-medium-emphasis">{{ activity.time }}</div>
                  <div class="text-body-2 mt-1">{{ activity.description }}</div>
                </div>
              </v-timeline-item>
            </v-timeline>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="4">
        <v-card class="mb-4">
          <v-card-title>System Status</v-card-title>
          <v-divider />
          <v-list>
            <v-list-item
              v-for="system in systemStatus"
              :key="system.name"
              :prepend-icon="system.icon"
            >
              <v-list-item-title>{{ system.name }}</v-list-item-title>
              <template #append>
                <v-chip :color="system.status === 'online' ? 'success' : 'error'" size="small">
                  {{ system.status }}
                </v-chip>
              </template>
            </v-list-item>
          </v-list>
        </v-card>

        <v-card>
          <v-card-title>Quick Links</v-card-title>
          <v-divider />
          <v-list>
            <v-list-item
              v-for="link in quickLinks"
              :key="link.title"
              :prepend-icon="link.icon"
              :title="link.title"
              @click="router.push(link.to)"
            />
          </v-list>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth, useAppStore } from '@ose/shared'

const router = useRouter()
const appStore = useAppStore()
const { userName } = useAuth()

// Stats data
const stats = ref([
  {
    title: 'Total Devices',
    value: '12,584',
    change: '+12% from last month',
    changeIcon: 'mdi-trending-up',
    changeColor: 'text-success',
    icon: 'mdi-devices',
    color: 'primary',
  },
  {
    title: 'Active Tickets',
    value: '23',
    change: '-5% from last week',
    changeIcon: 'mdi-trending-down',
    changeColor: 'text-success',
    icon: 'mdi-ticket',
    color: 'warning',
  },
  {
    title: 'Production Orders',
    value: '8',
    change: '2 in progress',
    changeIcon: 'mdi-information',
    changeColor: 'text-info',
    icon: 'mdi-factory',
    color: 'info',
  },
  {
    title: 'RMA Cases',
    value: '5',
    change: '3 pending',
    changeIcon: 'mdi-clock-outline',
    changeColor: 'text-warning',
    icon: 'mdi-package-variant-closed',
    color: 'error',
  },
])

// Applications
const applications = ref([
  {
    title: 'Notificación Series',
    subtitle: 'App 1',
    description: 'Send device series notifications to customers via email',
    icon: 'mdi-email-multiple',
    color: 'blue',
    route: '/app1',
  },
  {
    title: 'Importación Datos',
    subtitle: 'App 2',
    description: 'Import device data from Excel/CSV files with validation',
    icon: 'mdi-file-import',
    color: 'green',
    route: '/app2',
  },
  {
    title: 'RMA & Tickets',
    subtitle: 'App 3',
    description: 'Manage customer support tickets and RMA cases',
    icon: 'mdi-ticket',
    color: 'orange',
    route: '/app3',
  },
  {
    title: 'Import Transform',
    subtitle: 'App 4',
    description: 'Advanced data transformation and mapping',
    icon: 'mdi-transform',
    color: 'purple',
    route: '/app4',
  },
  {
    title: 'Factura Ticket',
    subtitle: 'App 5',
    description: 'Generate invoices from support tickets',
    icon: 'mdi-receipt',
    color: 'teal',
    route: '/app5',
  },
  {
    title: 'Picking Palets',
    subtitle: 'App 6',
    description: 'Warehouse picking and pallet management',
    icon: 'mdi-package-variant',
    color: 'indigo',
    route: '/app6',
  },
])

// Recent activities
const recentActivities = ref([
  {
    title: 'New production order created',
    description: 'Order #PO-2025-001 for 500 units',
    time: '2 hours ago',
    color: 'primary',
  },
  {
    title: 'RMA case resolved',
    description: 'Case #RMA-2025-0023 closed successfully',
    time: '4 hours ago',
    color: 'success',
  },
  {
    title: 'Ticket assigned',
    description: 'Ticket #TKT-2025-0156 assigned to Juan Pérez',
    time: '6 hours ago',
    color: 'info',
  },
  {
    title: 'Data import completed',
    description: '1,250 devices imported successfully',
    time: '1 day ago',
    color: 'success',
  },
])

// System status
const systemStatus = ref([
  { name: 'API Backend', status: 'online', icon: 'mdi-server' },
  { name: 'Database', status: 'online', icon: 'mdi-database' },
  { name: 'Email Service', status: 'online', icon: 'mdi-email' },
])

// Quick links
const quickLinks = ref([
  { title: 'My Profile', icon: 'mdi-account', to: '/profile' },
  { title: 'Settings', icon: 'mdi-cog', to: '/settings' },
  { title: 'Documentation', icon: 'mdi-book-open-variant', to: '/docs' },
  { title: 'Support', icon: 'mdi-help-circle', to: '/support' },
])

// Methods
function goToApp(route: string) {
  router.push(route)
}

onMounted(() => {
  appStore.setPageTitle('Dashboard')
})
</script>

<script lang="ts">
export default {
  name: 'Dashboard',
}
</script>

<style scoped>
.cursor-pointer {
  cursor: pointer;
}
</style>
