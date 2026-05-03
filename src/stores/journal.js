import { defineStore } from 'pinia'
import { ref } from 'vue'
import { journalsApi } from '@/api/journals.js'

export const useJournalStore = defineStore('journal', () => {
  const entries = ref([])
  const currentEntry = ref(null)
  const themes = ref([])
  const loading = ref(false)
  const saving = ref(false)
  const error = ref(null)

  async function fetchEntries(params = {}) {
    loading.value = true
    error.value = null
    try {
      const { data } = await journalsApi.list(params)
      entries.value = data
    } catch (err) {
      error.value = err.message
    } finally {
      loading.value = false
    }
  }

  async function fetchEntry(id) {
    loading.value = true
    try {
      const { data } = await journalsApi.get(id)
      currentEntry.value = data
      return data
    } catch (err) {
      error.value = err.message
      return null
    } finally {
      loading.value = false
    }
  }

  async function createEntry(entryData) {
    saving.value = true
    error.value = null
    try {
      const { data } = await journalsApi.create(entryData)
      entries.value.unshift(data)
      return { data, error: null }
    } catch (err) {
      error.value = err.message
      return { data: null, error: err.message }
    } finally {
      saving.value = false
    }
  }

  async function deleteEntry(id) {
    try {
      await journalsApi.delete(id)
      entries.value = entries.value.filter(e => e.id !== id)
      return true
    } catch {
      return false
    }
  }

  async function getReflections(id) {
    try {
      const { data } = await journalsApi.reflections(id)
      return data.questions || []
    } catch {
      return []
    }
  }

  async function fetchThemes() {
    try {
      const { data } = await journalsApi.themes()
      themes.value = data
    } catch {}
  }

  return {
    entries, currentEntry, themes, loading, saving, error,
    fetchEntries, fetchEntry, createEntry, deleteEntry, getReflections, fetchThemes,
  }
})
