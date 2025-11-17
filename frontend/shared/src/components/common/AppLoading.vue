<template>
  <v-overlay :model-value="modelValue" :persistent="persistent" class="app-loading">
    <v-progress-circular :size="size" :width="width" color="primary" indeterminate>
      <template v-if="text">
        <v-icon>mdi-loading</v-icon>
      </template>
    </v-progress-circular>
    <div v-if="text" class="loading-text mt-4">
      {{ text }}
    </div>
  </v-overlay>
</template>

<script setup lang="ts">
defineProps<{
  modelValue?: boolean
  text?: string
  size?: number
  width?: number
  persistent?: boolean
}>()
</script>

<script lang="ts">
export default {
  name: 'AppLoading',
}
</script>

<style scoped>
.app-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.loading-text {
  color: white;
  font-size: 1.1rem;
  font-weight: 500;
  text-align: center;
}
</style>
