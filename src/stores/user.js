import { defineStore } from 'pinia'
import { ref } from 'vue'
import { supabase } from '@/composables/useSupabase.js'

export const useUserStore = defineStore('user', () => {
  const profile = ref(null)
  const biasProfile = ref(null)
  const archetype = ref(null)

  async function fetchProfile(userId) {
    const { data } = await supabase.from('profiles').select('*').eq('id', userId).single()
    profile.value = data
  }

  async function fetchBiasProfile(userId) {
    const { data } = await supabase.from('user_bias_profiles').select('*').eq('user_id', userId).single()
    biasProfile.value = data
  }

  async function updateProfile(userId, updates) {
    const { data, error } = await supabase.from('profiles').update(updates).eq('id', userId).select().single()
    if (!error) profile.value = data
    return { data, error }
  }

  return { profile, biasProfile, archetype, fetchProfile, fetchBiasProfile, updateProfile }
})
