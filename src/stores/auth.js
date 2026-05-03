import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { supabase } from '@/composables/useSupabase.js'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const isLoading = ref(false)
  const session = ref(null)
  const initialized = ref(false)

  const isAuthenticated = computed(() => !!user.value)

  let _initPromise = null
  let _authSubscription = null

  // Call this anywhere — safe to call multiple times, resolves once
  function ensureInitialized() {
    if (!_initPromise) _initPromise = _doInit()
    return _initPromise
  }

  async function _doInit() {
    const { data: { session: s } } = await supabase.auth.getSession()
    session.value = s
    user.value = s?.user ?? null
    initialized.value = true

    // Unsubscribe any previous listener before registering a new one
    _authSubscription?.unsubscribe()
    const { data } = supabase.auth.onAuthStateChange((_event, s) => {
      session.value = s
      user.value = s?.user ?? null
    })
    _authSubscription = data.subscription
  }

  async function signUp(email, password, metadata = {}) {
    isLoading.value = true
    try {
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: { data: metadata }
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

  return {
    user, session, isLoading, isAuthenticated, initialized,
    ensureInitialized, signUp, signIn, signOut
  }
})
