import { defineStore } from 'pinia'
import { ref } from 'vue'
import { insightsApi } from '@/api/insights.js'

export const useInsightsStore = defineStore('insights', () => {
  const stored = JSON.parse(sessionStorage.getItem('insights_cache') || 'null')

  const biasFingerprint = ref(stored?.biasFingerprint || { bias_scores: {}, archetype: null, dominant_category: null })
  const weeklyInsights = ref(stored?.weeklyInsights || [])
  const recommendations = ref(stored?.recommendations || { next_bias: null, next_assessment: null })
  const loading = ref(false)
  const lastFetched = ref(stored?.lastFetched || null)

  function saveCache() {
    sessionStorage.setItem('insights_cache', JSON.stringify({
      biasFingerprint: biasFingerprint.value,
      weeklyInsights: weeklyInsights.value,
      recommendations: recommendations.value,
      lastFetched: lastFetched.value
    }))
  }

  const CACHE_TTL = 5 * 60 * 1000 // 5 minutes

  function isStale() {
    return !lastFetched.value || Date.now() - lastFetched.value > CACHE_TTL
  }

  async function fetchAll(force = false) {
    if (!force && !isStale()) return
    loading.value = true
    try {
      const [fp, weekly, recs] = await Promise.allSettled([
        insightsApi.biasFingerprint(),
        insightsApi.weekly(),
        insightsApi.recommendations(),
      ])
      if (fp.status === 'fulfilled') biasFingerprint.value = fp.value.data
      if (weekly.status === 'fulfilled') weeklyInsights.value = weekly.value.data
      if (recs.status === 'fulfilled') recommendations.value = recs.value.data
      lastFetched.value = Date.now()
      saveCache()
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
      saveCache()
    } catch {}
  }

  return { biasFingerprint, weeklyInsights, recommendations, loading, fetchAll, fetchBiasFingerprint }
})
