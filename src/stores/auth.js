import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { supabase } from '@/composables/useSupabase.js'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const isLoading = ref(false)
  const session = ref(null)

  const isAuthenticated = computed(() => !!user.value)

  async function initialize() {
    // DEV MODE: mock user so all pages are accessible without real auth
    user.value = { id: 'dev-user', email: 'dev@sentio.app', user_metadata: { full_name: 'Dev User' } }
  }

  async function signUp(email, password, displayName) {
    isLoading.value = true
    try {
      const { data, error } = await supabase.auth.signUp({
        email, password,
        options: { data: { display_name: displayName } }
      })
      if (error) throw error
      return { data, error: null }
    } catch (error) {
      return { data: null, error }
    } finally {
      isLoading.value = false
    }
  }

  async function signIn(email, password) {
    isLoading.value = true
    try {
      const { data, error } = await supabase.auth.signInWithPassword({ email, password })
      if (error) throw error
      return { data, error: null }
    } catch (error) {
      return { data: null, error }
    } finally {
      isLoading.value = false
    }
  }

  async function signOut() {
    await supabase.auth.signOut()
    user.value = null
    session.value = null
  }

  return { user, session, isLoading, isAuthenticated, initialize, signUp, signIn, signOut }
})
