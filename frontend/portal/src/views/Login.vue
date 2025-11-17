<template>
  <v-container fluid class="fill-height login-container">
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="6" lg="4">
        <v-card elevation="8" class="login-card">
          <!-- Header -->
          <v-card-title class="text-center pa-6">
            <div class="w-100">
              <v-icon size="64" color="primary" class="mb-4">mdi-solar-panel</v-icon>
              <h1 class="text-h4 font-weight-bold">OSE Platform</h1>
              <p class="text-subtitle-1 text-medium-emphasis mt-2">
                Sistema de Gestión Integral
              </p>
            </div>
          </v-card-title>

          <v-divider />

          <!-- Login Form -->
          <v-card-text class="pa-6">
            <v-form ref="formRef" v-model="formValid" @submit.prevent="handleLogin">
              <v-text-field
                v-model="email"
                label="Email"
                type="email"
                prepend-inner-icon="mdi-email"
                :rules="emailRules"
                :disabled="isLoading"
                variant="outlined"
                class="mb-3"
                @keyup.enter="handleLogin"
              />

              <v-text-field
                v-model="password"
                label="Password"
                :type="showPassword ? 'text' : 'password'"
                prepend-inner-icon="mdi-lock"
                :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
                :rules="passwordRules"
                :disabled="isLoading"
                variant="outlined"
                class="mb-3"
                @click:append-inner="showPassword = !showPassword"
                @keyup.enter="handleLogin"
              />

              <v-checkbox
                v-model="rememberMe"
                label="Remember me"
                :disabled="isLoading"
                color="primary"
                class="mt-0"
              />

              <v-alert v-if="error" type="error" variant="tonal" class="mb-4">
                {{ error }}
              </v-alert>

              <v-btn
                type="submit"
                color="primary"
                size="large"
                block
                :loading="isLoading"
                :disabled="!formValid || isLoading"
              >
                <v-icon left>mdi-login</v-icon>
                Sign In
              </v-btn>
            </v-form>

            <div class="text-center mt-6">
              <v-btn variant="text" size="small" @click="showForgotPassword = true">
                Forgot password?
              </v-btn>
            </div>
          </v-card-text>

          <!-- Footer -->
          <v-divider />
          <v-card-actions class="pa-4 justify-center">
            <span class="text-caption text-medium-emphasis">
              © 2025 Oversun Energy - v{{ appVersion }}
            </span>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <!-- Forgot Password Dialog -->
    <v-dialog v-model="showForgotPassword" max-width="500">
      <v-card>
        <v-card-title>Reset Password</v-card-title>
        <v-card-text>
          <v-text-field
            v-model="resetEmail"
            label="Email"
            type="email"
            prepend-inner-icon="mdi-email"
            variant="outlined"
            hint="Enter your email address to receive password reset instructions"
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="showForgotPassword = false">Cancel</v-btn>
          <v-btn color="primary" @click="handlePasswordReset">Send Reset Link</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Background decoration -->
    <div class="login-background" />
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuth, useNotification, required, email as emailValidator } from '@ose/shared'

const router = useRouter()
const route = useRoute()
const { login, isLoading, error: authError } = useAuth()
const { showSuccess, showError } = useNotification()

// Form data
const formRef = ref()
const formValid = ref(false)
const email = ref('')
const password = ref('')
const showPassword = ref(false)
const rememberMe = ref(false)

// Forgot password
const showForgotPassword = ref(false)
const resetEmail = ref('')

// App version
const appVersion = ref(import.meta.env.VITE_APP_VERSION || '1.0.0')

// Computed
const error = computed(() => authError.value)

// Validation rules
const emailRules = [required('Email is required'), emailValidator('Please enter a valid email')]

const passwordRules = [required('Password is required')]

// Methods
async function handleLogin() {
  if (!formValid.value) return

  try {
    await login({
      email: email.value,
      password: password.value,
    })

    showSuccess('Login successful!', 'Welcome back')

    // Redirect to intended page or dashboard
    const redirect = (route.query.redirect as string) || '/'
    router.push(redirect)
  } catch (err: any) {
    showError(err.message || 'Login failed', 'Authentication Error')
  }
}

async function handlePasswordReset() {
  if (!resetEmail.value) {
    showError('Please enter your email address', 'Validation Error')
    return
  }

  try {
    // TODO: Implement password reset
    showSuccess(
      'Password reset instructions sent to your email',
      'Reset Link Sent'
    )
    showForgotPassword.value = false
    resetEmail.value = ''
  } catch (err: any) {
    showError(err.message || 'Failed to send reset email', 'Error')
  }
}
</script>

<script lang="ts">
export default {
  name: 'Login',
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  position: relative;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  position: relative;
  z-index: 1;
}

.login-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  opacity: 0.1;
  background-image:
    radial-gradient(circle at 20% 50%, rgba(255, 255, 255, 0.2) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(255, 255, 255, 0.2) 0%, transparent 50%);
}

.w-100 {
  width: 100%;
}
</style>
