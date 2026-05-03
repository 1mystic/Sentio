import { defineStore } from 'pinia'
import { ref } from 'vue'
import { therapistsApi } from '@/api/therapists.js'

export const useTherapistStore = defineStore('therapist', () => {
  const therapists = ref([])
  const currentTherapist = ref(null)
  const loading = ref(false)
  const error = ref(null)

  async function fetchList(filters = {}) {
    loading.value = true
    error.value = null
    try {
      const { data } = await therapistsApi.list(filters)
      therapists.value = data
    } catch (err) {
      error.value = err.message
    } finally {
      loading.value = false
    }
  }

  async function fetchOne(id) {
    loading.value = true
    try {
      const { data } = await therapistsApi.get(id)
      currentTherapist.value = data
      return data
    } catch (err) {
      error.value = err.message
      return null
    } finally {
      loading.value = false
    }
  }

  async function requestBooking(therapistId, message) {
    try {
      const { data } = await therapistsApi.book(therapistId, { message })
      return { data, error: null }
    } catch (err) {
      return { data: null, error: err.message }
    }
  }

  return { therapists, currentTherapist, loading, error, fetchList, fetchOne, requestBooking }
})
