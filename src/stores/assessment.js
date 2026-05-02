import { defineStore } from 'pinia'
import { ref } from 'vue'
import { supabase } from '@/composables/useSupabase.js'

export const useAssessmentStore = defineStore('assessment', () => {
  const available = ref([])
  const results = ref([])
  const isLoading = ref(false)

  async function fetchAssessments() {
    isLoading.value = true
    const { data } = await supabase.from('assessments').select('*').order('title')
    available.value = data || []
    isLoading.value = false
  }

  async function fetchResults(userId) {
    const { data } = await supabase
      .from('assessment_results')
      .select('*, assessments(title, slug)')
      .eq('user_id', userId)
      .order('completed_at', { ascending: false })
    results.value = data || []
  }

  async function submitAssessment(assessmentId, userId, rawScores, computedScores) {
    const { data, error } = await supabase.from('assessment_results').insert({
      assessment_id: assessmentId,
      user_id: userId,
      raw_scores: rawScores,
      computed_scores: computedScores
    }).select().single()
    if (!error) results.value.unshift(data)
    return { data, error }
  }

  return { available, results, isLoading, fetchAssessments, fetchResults, submitAssessment }
})
