import { defineStore } from 'pinia'
import { ref } from 'vue'
import { supabase } from '@/composables/useSupabase.js'

export const useBiasStore = defineStore('bias', () => {
  const allBiases = ref([])
  const isLoading = ref(false)

  async function fetchBiases() {
    isLoading.value = true
    const { data, error } = await supabase.from('biases').select('*').order('name')
    if (!error) allBiases.value = data || []
    isLoading.value = false
  }

  function getBiasBySlug(slug) {
    return allBiases.value.find(b => b.slug === slug)
  }

  function getBiasesByCategory(category) {
    return allBiases.value.filter(b => b.category === category)
  }

  return { allBiases, isLoading, fetchBiases, getBiasBySlug, getBiasesByCategory }
})
