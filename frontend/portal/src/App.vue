<template>
  <v-app>
    <router-view />
  </v-app>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useAppStore } from '@ose/shared'

const appStore = useAppStore()

onMounted(() => {
  // Initialize theme from localStorage
  appStore.initializeTheme()
})
</script>

<script lang="ts">
export default {
  name: 'App',
}
</script>

<style>
#app {
  font-family: 'Roboto', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
</style>
