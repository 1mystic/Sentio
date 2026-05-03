import { defineStore } from 'pinia'
import { ref } from 'vue'
import { insightsApi } from '@/api/insights.js'

export const useInsightsStore = defineStore('insights', () => {
  const biasFingerprint = ref({ bias_scores: {}, archetype: null, dominant_category: null })
  const weeklyInsights = ref([])
  const recommendations = ref({ next_bias: null, next_assessment: null })
  const loading = ref(false)
  const lastFetched = ref(null)

  const CACHE_TTL = 5 * 60 * 1000 // 5 minutes

  function isStale() {
    return !lastFetched.value || Date.now() - lastFetched.value > CACHE_TTL
  }

  async function fetchAll(force = false) {
    if (!force && !isStale()) return
    loading.value = true
    try {
      const [fp, weekly, recs] = await Promise.all([
        insightsApi.biasFingerprint(),
        insightsApi.weekly(),
        insightsApi.recommendations(),
      ])
      biasFingerprint.value = fp.data
      weeklyInsights.value = weekly.data
      recommendations.value = recs.data
      lastFetched.value = Date.now()
    } catch (err) {
      console.warn('Insights fetch error:', err.message)
    } finally {
      loading.value = false
    }
  }

  async function fetchBiasFingerprint() {
    try {
      const { data } = await insightsApi.biasFingerprint()
      biasFingerprint.value = data
    } catch {}
  }

  return { biasFingerprint, weeklyInsights, recommendations, loading, fetchAll, fetchBiasFingerprint }
})
