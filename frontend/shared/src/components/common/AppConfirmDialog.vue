<template>
  <v-dialog
    v-model="show"
    :max-width="maxWidth"
    persistent
  >
    <v-card>
      <v-card-title class="d-flex align-center">
        <v-icon v-if="icon" :icon="icon" :color="iconColor" class="mr-2" />
        {{ title }}
      </v-card-title>

      <v-card-text>
        {{ message }}
      </v-card-text>

      <v-card-actions>
        <v-spacer />
        <v-btn
          variant="text"
          @click="handleCancel"
          :disabled="loading"
        >
          {{ cancelText }}
        </v-btn>
        <v-btn
          :color="confirmColor"
          variant="elevated"
          @click="handleConfirm"
          :loading="loading"
        >
          {{ confirmText }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const props = withDefaults(
  defineProps<{
    modelValue?: boolean
    title?: string
    message: string
    confirmText?: string
    cancelText?: string
    confirmColor?: string
    icon?: string
    iconColor?: string
    maxWidth?: string | number
  }>(),
  {
    modelValue: false,
    title: 'Confirm',
    confirmText: 'Confirm',
    cancelText: 'Cancel',
    confirmColor: 'primary',
    maxWidth: 500,
  }
)

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'confirm'): void
  (e: 'cancel'): void
}>()

const show = ref(props.modelValue)
const loading = ref(false)

watch(
  () => props.modelValue,
  (newValue) => {
    show.value = newValue
  }
)

watch(show, (newValue) => {
  emit('update:modelValue', newValue)
})

function handleConfirm() {
  emit('confirm')
  show.value = false
}

function handleCancel() {
  emit('cancel')
  show.value = false
}
</script>

<script lang="ts">
export default {
  name: 'AppConfirmDialog',
}
</script>
