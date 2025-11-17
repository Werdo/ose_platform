<template>
  <v-container fluid class="fill-height">
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="6" class="text-center">
        <v-icon size="120" color="grey-lighten-1" class="mb-6">
          mdi-cloud-off-outline
        </v-icon>

        <h1 class="text-h2 font-weight-bold mb-4">404</h1>
        <h2 class="text-h5 text-medium-emphasis mb-6">
          Oops! Page Not Found
        </h2>

        <p class="text-body-1 text-medium-emphasis mb-8">
          The page you are looking for might have been removed, had its name changed,
          or is temporarily unavailable.
        </p>

        <div class="d-flex justify-center gap-4">
          <v-btn
            color="primary"
            size="large"
            prepend-icon="mdi-home"
            @click="goHome"
          >
            Go to Dashboard
          </v-btn>

          <v-btn
            variant="outlined"
            size="large"
            prepend-icon="mdi-arrow-left"
            @click="goBack"
          >
            Go Back
          </v-btn>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

function goHome() {
  router.push({ name: 'Dashboard' })
}

function goBack() {
  router.back()
}
</script>

<script lang="ts">
export default {
  name: 'NotFound',
}
</script>

<style scoped>
.gap-4 {
  gap: 1rem;
}
</style>
