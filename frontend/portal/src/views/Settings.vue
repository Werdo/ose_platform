<template>
  <div>
    <!-- Page header -->
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 font-weight-bold mb-2">Settings</h1>
        <p class="text-subtitle-1 text-medium-emphasis">
          Configure your application preferences
        </p>
      </v-col>
    </v-row>

    <v-divider class="my-6" />

    <v-row>
      <v-col cols="12" md="8">
        <!-- Appearance settings -->
        <v-card class="mb-4">
          <v-card-title>Appearance</v-card-title>
          <v-divider />
          <v-card-text>
            <v-row>
              <v-col cols="12">
                <div class="d-flex justify-space-between align-center mb-4">
                  <div>
                    <div class="font-weight-medium">Dark Mode</div>
                    <div class="text-caption text-medium-emphasis">
                      Enable dark theme across the application
                    </div>
                  </div>
                  <v-switch v-model="settings.darkMode" color="primary" @change="toggleTheme" />
                </div>

                <v-divider />

                <div class="d-flex justify-space-between align-center my-4">
                  <div>
                    <div class="font-weight-medium">Compact Sidebar</div>
                    <div class="text-caption text-medium-emphasis">
                      Minimize sidebar to show icons only
                    </div>
                  </div>
                  <v-switch v-model="settings.compactSidebar" color="primary" @change="toggleSidebarMini" />
                </div>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>

        <!-- Notification settings -->
        <v-card class="mb-4">
          <v-card-title>Notifications</v-card-title>
          <v-divider />
          <v-card-text>
            <div class="d-flex justify-space-between align-center mb-4">
              <div>
                <div class="font-weight-medium">Email Notifications</div>
                <div class="text-caption text-medium-emphasis">
                  Receive email updates for important events
                </div>
              </div>
              <v-switch v-model="settings.emailNotifications" color="primary" />
            </div>

            <v-divider />

            <div class="d-flex justify-space-between align-center my-4">
              <div>
                <div class="font-weight-medium">Desktop Notifications</div>
                <div class="text-caption text-medium-emphasis">
                  Show browser notifications
                </div>
              </div>
              <v-switch v-model="settings.desktopNotifications" color="primary" />
            </div>

            <v-divider />

            <div class="d-flex justify-space-between align-center mt-4">
              <div>
                <div class="font-weight-medium">Sound Alerts</div>
                <div class="text-caption text-medium-emphasis">
                  Play sound for notifications
                </div>
              </div>
              <v-switch v-model="settings.soundAlerts" color="primary" />
            </div>
          </v-card-text>
        </v-card>

        <!-- Language & Region -->
        <v-card>
          <v-card-title>Language & Region</v-card-title>
          <v-divider />
          <v-card-text>
            <v-row>
              <v-col cols="12" sm="6">
                <v-select
                  v-model="settings.language"
                  label="Language"
                  :items="languages"
                  variant="outlined"
                />
              </v-col>

              <v-col cols="12" sm="6">
                <v-select
                  v-model="settings.timezone"
                  label="Timezone"
                  :items="timezones"
                  variant="outlined"
                />
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Info sidebar -->
      <v-col cols="12" md="4">
        <v-card class="mb-4">
          <v-card-title>About</v-card-title>
          <v-divider />
          <v-list>
            <v-list-item>
              <v-list-item-title>Version</v-list-item-title>
              <v-list-item-subtitle>{{ appVersion }}</v-list-item-subtitle>
            </v-list-item>

            <v-list-item>
              <v-list-item-title>API URL</v-list-item-title>
              <v-list-item-subtitle class="text-caption">
                {{ apiUrl }}
              </v-list-item-subtitle>
            </v-list-item>

            <v-list-item>
              <v-list-item-title>Environment</v-list-item-title>
              <v-list-item-subtitle>{{ environment }}</v-list-item-subtitle>
            </v-list-item>
          </v-list>
        </v-card>

        <v-card>
          <v-card-title>Actions</v-card-title>
          <v-divider />
          <v-card-text>
            <v-btn color="primary" block class="mb-2" @click="saveSettings">
              <v-icon left>mdi-content-save</v-icon>
              Save Settings
            </v-btn>

            <v-btn variant="outlined" block @click="resetSettings">
              <v-icon left>mdi-restore</v-icon>
              Reset to Defaults
            </v-btn>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAppStore, useNotification } from '@ose/shared'

const appStore = useAppStore()
const { showSuccess } = useNotification()

// Settings
const settings = ref({
  darkMode: false,
  compactSidebar: false,
  emailNotifications: true,
  desktopNotifications: false,
  soundAlerts: true,
  language: 'es',
  timezone: 'Europe/Madrid',
})

// Options
const languages = [
  { title: 'Español', value: 'es' },
  { title: 'English', value: 'en' },
  { title: 'Français', value: 'fr' },
]

const timezones = [
  { title: 'Europe/Madrid (GMT+1)', value: 'Europe/Madrid' },
  { title: 'Europe/London (GMT)', value: 'Europe/London' },
  { title: 'America/New_York (GMT-5)', value: 'America/New_York' },
]

// App info
const appVersion = ref(import.meta.env.VITE_APP_VERSION || '1.0.0')
const apiUrl = ref(import.meta.env.VITE_API_URL || 'http://localhost:8001/api/v1')
const environment = ref(import.meta.env.MODE || 'development')

// Methods
function toggleTheme() {
  appStore.toggleTheme()
}

function toggleSidebarMini() {
  appStore.toggleSidebarMini()
}

function saveSettings() {
  // TODO: Save settings to backend
  localStorage.setItem('app_settings', JSON.stringify(settings.value))
  showSuccess('Settings saved successfully', 'Success')
}

function resetSettings() {
  settings.value = {
    darkMode: false,
    compactSidebar: false,
    emailNotifications: true,
    desktopNotifications: false,
    soundAlerts: true,
    language: 'es',
    timezone: 'Europe/Madrid',
  }
  showSuccess('Settings reset to defaults', 'Success')
}

function loadSettings() {
  const saved = localStorage.getItem('app_settings')
  if (saved) {
    settings.value = JSON.parse(saved)
  }

  // Sync with app store
  settings.value.darkMode = appStore.isDarkTheme
  settings.value.compactSidebar = appStore.sidebarMini
}

onMounted(() => {
  appStore.setPageTitle('Settings')
  loadSettings()
})
</script>

<script lang="ts">
export default {
  name: 'Settings',
}
</script>
