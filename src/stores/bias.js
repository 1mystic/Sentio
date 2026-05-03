import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { biasesApi } from '@/api/biases.js'

export const useBiasStore = defineStore('bias', () => {
  const biases = ref([])
  const currentBias = ref(null)
  const loading = ref(false)
  const error = ref(null)

  const byCategory = computed(() => {
    return biases.value.reduce((acc, b) => {
      if (!acc[b.category]) acc[b.category] = []
      acc[b.category].push(b)
      return acc
    }, {})
  })

  async function fetchAll(params = {}) {
    loading.value = true
    error.value = null
    try {
      const { data } = await biasesApi.list(params)
      biases.value = data
    } catch (err) {
      error.value = err.message
    } finally {
      loading.value = false
    }
  }

  async function fetchBySlug(slug) {
    loading.value = true
    error.value = null
    try {
      const { data } = await biasesApi.getBySlug(slug)
      currentBias.value = data
      return data
    } catch (err) {
      error.value = err.message
      return null
    } finally {
      loading.value = false
    }
  }

  return { biases, currentBias, loading, error, byCategory, fetchAll, fetchBySlug }
})
