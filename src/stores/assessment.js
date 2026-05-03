import { defineStore } from 'pinia'
import { ref } from 'vue'
import { assessmentsApi } from '@/api/assessments.js'

export const useAssessmentStore = defineStore('assessment', () => {
  const assessments = ref([])
  const currentAssessment = ref(null)
  const results = ref([])
  const loading = ref(false)
  const submitting = ref(false)
  const error = ref(null)

  async function fetchList() {
    loading.value = true
    error.value = null
    try {
      const { data } = await assessmentsApi.list()
      assessments.value = data
    } catch (err) {
      error.value = err.message
    } finally {
      loading.value = false
    }
  }

  async function fetchOne(id) {
    loading.value = true
    try {
      const { data } = await assessmentsApi.get(id)
      currentAssessment.value = data
      return data
    } catch (err) {
      error.value = err.message
      return null
    } finally {
      loading.value = false
    }
  }

  async function submit(id, payload) {
    submitting.value = true
    error.value = null
    try {
      const { data } = await assessmentsApi.submit(id, payload)
      return { data, error: null }
    } catch (err) {
      error.value = err.message
      return { data: null, error: err.message }
    } finally {
      submitting.value = false
    }
  }

  async function fetchHistory(id) {
    try {
      const { data } = await assessmentsApi.history(id)
      results.value = data
      return data
    } catch {
      return []
    }
  }

  return {
    assessments, currentAssessment, results, loading, submitting, error,
    fetchList, fetchOne, submit, fetchHistory,
  }
})
