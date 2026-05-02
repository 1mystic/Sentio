import { defineStore } from 'pinia'
import { ref } from 'vue'
import { supabase } from '@/composables/useSupabase.js'

export const useJournalStore = defineStore('journal', () => {
  const entries = ref([])
  const currentEntry = ref(null)
  const isLoading = ref(false)

  async function fetchEntries(userId) {
    isLoading.value = true
    const { data } = await supabase
      .from('journal_entries')
      .select('*')
      .eq('user_id', userId)
      .order('created_at', { ascending: false })
    entries.value = data || []
    isLoading.value = false
  }

  async function createEntry(entryData) {
    const { data, error } = await supabase.from('journal_entries').insert(entryData).select().single()
    if (!error) entries.value.unshift(data)
    return { data, error }
  }

  async function fetchEntry(id) {
    const { data } = await supabase.from('journal_entries').select('*').eq('id', id).single()
    currentEntry.value = data
    return data
  }

  return { entries, currentEntry, isLoading, fetchEntries, createEntry, fetchEntry }
})
