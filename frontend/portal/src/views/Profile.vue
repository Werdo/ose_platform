<template>
  <div>
    <!-- Page header -->
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 font-weight-bold mb-2">My Profile</h1>
        <p class="text-subtitle-1 text-medium-emphasis">
          Manage your account information and settings
        </p>
      </v-col>
    </v-row>

    <v-divider class="my-6" />

    <v-row>
      <!-- Profile card -->
      <v-col cols="12" md="4">
        <v-card>
          <v-card-text class="text-center pa-6">
            <v-avatar color="primary" size="120" class="mb-4">
              <v-icon size="64">mdi-account</v-icon>
            </v-avatar>

            <h2 class="text-h5 font-weight-bold mb-2">{{ user?.name || 'User' }}</h2>
            <p class="text-body-2 text-medium-emphasis mb-2">{{ user?.email }}</p>
            <v-chip :color="getRoleColor(user?.role)" size="small" class="mb-4">
              {{ formatRole(user?.role) }}
            </v-chip>

            <v-divider class="my-4" />

            <v-list>
              <v-list-item prepend-icon="mdi-shield-account">
                <v-list-item-title>Role</v-list-item-title>
                <v-list-item-subtitle>{{ formatRole(user?.role) }}</v-list-item-subtitle>
              </v-list-item>

              <v-list-item prepend-icon="mdi-calendar">
                <v-list-item-title>Member Since</v-list-item-title>
                <v-list-item-subtitle>{{ formatDate(user?.created_at) }}</v-list-item-subtitle>
              </v-list-item>

              <v-list-item prepend-icon="mdi-clock">
                <v-list-item-title>Last Updated</v-list-item-title>
                <v-list-item-subtitle>{{ formatDate(user?.updated_at) }}</v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Profile information -->
      <v-col cols="12" md="8">
        <v-card class="mb-4">
          <v-card-title>Personal Information</v-card-title>
          <v-divider />
          <v-card-text>
            <v-form ref="formRef">
              <v-row>
                <v-col cols="12" sm="6">
                  <v-text-field
                    v-model="profileForm.name"
                    label="Full Name"
                    prepend-inner-icon="mdi-account"
                    variant="outlined"
                    :disabled="!editMode"
                  />
                </v-col>

                <v-col cols="12" sm="6">
                  <v-text-field
                    v-model="profileForm.email"
                    label="Email"
                    type="email"
                    prepend-inner-icon="mdi-email"
                    variant="outlined"
                    :disabled="!editMode"
                  />
                </v-col>

                <v-col cols="12" sm="6">
                  <v-text-field
                    v-model="profileForm.phone"
                    label="Phone"
                    prepend-inner-icon="mdi-phone"
                    variant="outlined"
                    :disabled="!editMode"
                  />
                </v-col>

                <v-col cols="12" sm="6">
                  <v-text-field
                    v-model="profileForm.department"
                    label="Department"
                    prepend-inner-icon="mdi-office-building"
                    variant="outlined"
                    :disabled="!editMode"
                  />
                </v-col>
              </v-row>
            </v-form>
          </v-card-text>
          <v-card-actions class="px-6 pb-4">
            <v-btn
              v-if="!editMode"
              color="primary"
              prepend-icon="mdi-pencil"
              @click="editMode = true"
            >
              Edit Profile
            </v-btn>
            <template v-else>
              <v-btn variant="text" @click="cancelEdit">Cancel</v-btn>
              <v-btn color="primary" @click="saveProfile">Save Changes</v-btn>
            </template>
          </v-card-actions>
        </v-card>

        <!-- Change password -->
        <v-card>
          <v-card-title>Change Password</v-card-title>
          <v-divider />
          <v-card-text>
            <v-form ref="passwordFormRef">
              <v-text-field
                v-model="passwordForm.current"
                label="Current Password"
                type="password"
                prepend-inner-icon="mdi-lock"
                variant="outlined"
                class="mb-3"
              />

              <v-text-field
                v-model="passwordForm.new"
                label="New Password"
                type="password"
                prepend-inner-icon="mdi-lock"
                variant="outlined"
                class="mb-3"
              />

              <v-text-field
                v-model="passwordForm.confirm"
                label="Confirm New Password"
                type="password"
                prepend-inner-icon="mdi-lock"
                variant="outlined"
              />
            </v-form>
          </v-card-text>
          <v-card-actions class="px-6 pb-4">
            <v-btn color="primary" @click="changePassword">Update Password</v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useAuth, useAppStore, useNotification, formatDate } from '@ose/shared'

const appStore = useAppStore()
const { user } = useAuth()
const { showSuccess, showError } = useNotification()

// Forms
const formRef = ref()
const passwordFormRef = ref()
const editMode = ref(false)

const profileForm = ref({
  name: '',
  email: '',
  phone: '',
  department: '',
})

const passwordForm = ref({
  current: '',
  new: '',
  confirm: '',
})

// Computed
const userValue = computed(() => user.value)

// Methods
function formatRole(role: string | undefined): string {
  if (!role) return 'N/A'
  return role.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())
}

function getRoleColor(role: string | undefined): string {
  const colors: Record<string, string> = {
    admin: 'error',
    supervisor: 'warning',
    operator: 'primary',
    quality_inspector: 'info',
    technician: 'success',
  }
  return colors[role || ''] || 'grey'
}

function initializeForm() {
  if (userValue.value) {
    profileForm.value = {
      name: userValue.value.name || '',
      email: userValue.value.email || '',
      phone: '',
      department: '',
    }
  }
}

function cancelEdit() {
  editMode.value = false
  initializeForm()
}

async function saveProfile() {
  try {
    // TODO: Implement profile update API call
    showSuccess('Profile updated successfully', 'Success')
    editMode.value = false
  } catch (err: any) {
    showError(err.message || 'Failed to update profile', 'Error')
  }
}

async function changePassword() {
  if (!passwordForm.value.current || !passwordForm.value.new || !passwordForm.value.confirm) {
    showError('Please fill in all password fields', 'Validation Error')
    return
  }

  if (passwordForm.value.new !== passwordForm.value.confirm) {
    showError('New passwords do not match', 'Validation Error')
    return
  }

  try {
    // TODO: Implement password change API call
    showSuccess('Password changed successfully', 'Success')
    passwordForm.value = { current: '', new: '', confirm: '' }
  } catch (err: any) {
    showError(err.message || 'Failed to change password', 'Error')
  }
}

onMounted(() => {
  appStore.setPageTitle('My Profile')
  initializeForm()
})
</script>

<script lang="ts">
export default {
  name: 'Profile',
}
</script>
