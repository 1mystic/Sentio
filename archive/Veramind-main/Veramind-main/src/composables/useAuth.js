import { ref, computed, readonly } from 'vue'
import { supabase } from '../integrations/supabase/client'

const user = ref(null)
const session = ref(null)
const loading = ref(true)

/**
 * Authentication composable
 * Provides reactive user state and auth methods
 */
export const useAuth = () => {
  // Initialize auth state
  const initAuth = async () => {
    try {
      const { data: { session: currentSession } } = await supabase.auth.getSession()
      session.value = currentSession
      user.value = currentSession?.user ?? null

      // Listen for auth changes
      supabase.auth.onAuthStateChange((_event, newSession) => {
        session.value = newSession
        user.value = newSession?.user ?? null
      })
    } catch (error) {
      console.error('Error initializing auth:', error)
    } finally {
      loading.value = false
    }
  }

  // Sign up with email and password
  const signUp = async (email, password, fullName) => {
    try {
      loading.value = true
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: {
            full_name: fullName
          }
        }
      })

      if (error) throw error

      // Create user profile
      if (data.user) {
        const { error: profileError } = await supabase
          .from('profiles')
          .insert({
            user_id: data.user.id,
            email: email,
            full_name: fullName
          })

        if (profileError) {
          console.error('Error creating profile:', profileError)
        }
      }

      return { data, error: null }
    } catch (error) {
      return { data: null, error }
    } finally {
      loading.value = false
    }
  }

  // Sign in with email and password
  const signIn = async (email, password) => {
    try {
      loading.value = true
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password
      })

      if (error) throw error

      session.value = data.session
      user.value = data.user

      return { data, error: null }
    } catch (error) {
      return { data: null, error }
    } finally {
      loading.value = false
    }
  }

  // Sign out
  const signOut = async () => {
    try {
      loading.value = true
      const { error } = await supabase.auth.signOut()
      if (error) throw error

      session.value = null
      user.value = null

      return { error: null }
    } catch (error) {
      return { error }
    } finally {
      loading.value = false
    }
  }

  // Reset password
  const resetPassword = async (email) => {
    try {
      const { data, error } = await supabase.auth.resetPasswordForEmail(email, {
        redirectTo: `${window.location.origin}/reset-password`
      })

      if (error) throw error
      return { data, error: null }
    } catch (error) {
      return { data: null, error }
    }
  }

  // Check if user is authenticated
  const isAuthenticated = computed(() => !!user.value)

  // Initialize on import (client-side only)
  if (typeof window !== 'undefined') {
    initAuth()
  }

  return {
    user: readonly(user),
    session: readonly(session),
    loading: readonly(loading),
    isAuthenticated,
    signUp,
    signIn,
    signOut,
    resetPassword,
    initAuth
  }
}

