/**
 * OSE Platform - Portal Principal
 * Main entry point
 */

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// Import shared library
import { vuetify, pinia, useAuthStore } from '@ose/shared'

// Create Vue app
const app = createApp(App)

// Use plugins
app.use(pinia)
app.use(vuetify)
app.use(router)

// Initialize auth store
const authStore = useAuthStore()
authStore.initialize()

// Mount app
app.mount('#app')
