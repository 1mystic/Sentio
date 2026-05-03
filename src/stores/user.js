import { defineStore } from 'pinia'
import { ref } from 'vue'
import { usersApi } from '@/api/users.js'
import { useAuthStore } from '@/stores/auth.js'

export const useUserStore = defineStore('user', () => {
  const profile = ref(null)
  const loading = ref(false)
  const saving = ref(false)
  const error = ref(null)

  async function fetchProfile() {
    loading.value = true
    error.value = null
    try {
      const { data } = await usersApi.me()
      profile.value = data
      return data
    } catch (err) {
      // Profile may not exist yet (new user) — use auth data
      const auth = useAuthStore()
      profile.value = {
        display_name: auth.user?.user_metadata?.full_name || 'User',
        email: auth.user?.email || '',
      }
      return profile.value
    } finally {
      loading.value = false
    }
  }

  async function saveProfile(updates) {
    saving.value = true
    error.value = null
    try {
      const { data } = await usersApi.updateMe(updates)
      profile.value = { ...profile.value, ...data }
      return { data, error: null }
    } catch (err) {
      error.value = err.message
      return { data: null, error: err.message }
    } finally {
      saving.value = false
    }
  }

  async function savePreferences(prefs) {
    try {
      await usersApi.preferences(prefs)
      if (profile.value) {
        profile.value.preferences = { ...(profile.value.preferences || {}), ...prefs }
      }
    } catch (err) {
      console.warn('Save preferences error:', err.message)
    }
  }

  return { profile, loading, saving, error, fetchProfile, saveProfile, savePreferences }
})
