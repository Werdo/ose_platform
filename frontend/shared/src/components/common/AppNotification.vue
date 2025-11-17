<template>
  <v-snackbar
    v-model="show"
    :color="color"
    :timeout="timeout"
    :location="location"
    :vertical="vertical"
    elevation="6"
  >
    <div class="d-flex align-center">
      <v-icon v-if="icon" :icon="icon" class="mr-3" />
      <div class="flex-grow-1">
        <div v-if="title" class="font-weight-bold mb-1">{{ title }}</div>
        <div>{{ message }}</div>
      </div>
    </div>

    <template #actions>
      <v-btn
        v-if="action"
        variant="text"
        @click="handleAction"
      >
        {{ action.label }}
      </v-btn>
      <v-btn
        icon="mdi-close"
        variant="text"
        @click="show = false"
      />
    </template>
  </v-snackbar>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

interface Action {
  label: string
  callback: () => void
}

const props = withDefaults(
  defineProps<{
    modelValue?: boolean
    type?: 'success' | 'error' | 'warning' | 'info'
    title?: string
    message: string
    timeout?: number
    location?: 'top' | 'bottom' | 'left' | 'right' | 'center'
    vertical?: boolean
    action?: Action
  }>(),
  {
    modelValue: false,
    type: 'info',
    timeout: 5000,
    location: 'top',
    vertical: false,
  }
)

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
}>()

const show = ref(props.modelValue)

watch(
  () => props.modelValue,
  (newValue) => {
    show.value = newValue
  }
)

watch(show, (newValue) => {
  emit('update:modelValue', newValue)
})

const color = computed(() => {
  switch (props.type) {
    case 'success':
      return 'success'
    case 'error':
      return 'error'
    case 'warning':
      return 'warning'
    case 'info':
      return 'info'
    default:
      return 'info'
  }
})

const icon = computed(() => {
  switch (props.type) {
    case 'success':
      return 'mdi-check-circle'
    case 'error':
      return 'mdi-alert-circle'
    case 'warning':
      return 'mdi-alert'
    case 'info':
      return 'mdi-information'
    default:
      return undefined
  }
})

function handleAction() {
  if (props.action?.callback) {
    props.action.callback()
  }
  show.value = false
}
</script>

<script lang="ts">
export default {
  name: 'AppNotification',
}
</script>
