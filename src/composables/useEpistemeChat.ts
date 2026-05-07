// useEpistemeChat.ts — Vue 3 composable for the Episteme Socratic engine
// Ports Episteme's client-side hook pattern into Vue 3 reactive state

import { ref, computed } from 'vue'
import {
  extractDepthSignals,
  determineNextState,
  updateBKT,
  bktToScore,
  sdsmToDepthLevel,
  DOMAIN_BKT_PRIORS,
} from '@/lib/episteme/algorithms'
import type { SocraticState, SocraticMessage, InsightCard, BKTState } from '@/lib/episteme/types'
import { useAuthStore } from '@/stores/auth.js'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export function useEpistemeChat() {
  const auth = useAuthStore()

  // ── Core state ─────────────────────────────────────────────────────────────
  const messages = ref<SocraticMessage[]>([])
  const isStreaming = ref(false)
  const sessionId = ref<string | null>(null)
  const domain = ref('general')
  const turnNumber = ref(0)
  const currentState = ref<SocraticState>('PROBE')
  const clarityScore = ref(0)
  const depthLevel = ref('SURFACE')
  const conceptsCovered = ref<string[]>([])
  const consecutiveScaffolds = ref(0)
  const bktState = ref<BKTState>({ pL: 0.20, pT: 0.12, pS: 0.10, pG: 0.08 })
  const canGenerateInsight = ref(false)
  const insightCard = ref<InsightCard | null>(null)
  const insightLoading = ref(false)
  const sessionConcept = ref('')

  // ── Computed ───────────────────────────────────────────────────────────────
  const stateLabel = computed<string>(() => ({
    PROBE: 'Probing',
    DEEPEN: 'Deepening',
    SCAFFOLD: 'Scaffolding',
    RECTIFY: 'Correcting',
    REDIRECT: 'Redirecting',
    CONSOLIDATE: 'Consolidating',
    COMPLETE: 'Complete',
  }[currentState.value] ?? 'Thinking'))

  const stateDescription = computed<string>(() => ({
    PROBE: 'Exploring your understanding',
    DEEPEN: 'Pushing toward deeper reasoning',
    SCAFFOLD: 'Building a conceptual foothold',
    RECTIFY: 'Gently correcting a misconception',
    REDIRECT: 'Refocusing the discussion',
    CONSOLIDATE: 'Synthesising what you\'ve learned',
    COMPLETE: 'Session complete',
  }[currentState.value] ?? ''))

  const depthLabel = computed<string>(() => ({
    SURFACE: 'Surface',
    CONCEPTUAL: 'Conceptual',
    ANALYTICAL: 'Analytical',
    SYNTHESIS: 'Synthesis',
  }[depthLevel.value] ?? 'Surface'))

  // ── Actions ────────────────────────────────────────────────────────────────
  async function startSession(selectedDomain: string) {
    domain.value = selectedDomain
    messages.value = []
    turnNumber.value = 0
    clarityScore.value = 0
    currentState.value = 'PROBE'
    consecutiveScaffolds.value = 0
    insightCard.value = null
    canGenerateInsight.value = false
    sessionConcept.value = ''
    bktState.value = DOMAIN_BKT_PRIORS[selectedDomain] ?? DOMAIN_BKT_PRIORS.general

    const token = auth.session?.access_token
    const res = await fetch(`${API_BASE}/socratic/session`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({ domain: selectedDomain }),
    })

    if (!res.ok) throw new Error(`Failed to create session: ${res.status}`)
    const data = await res.json()
    sessionId.value = data.session.id
  }

  async function sendMessage(userText: string) {
    if (!sessionId.value || isStreaming.value || !userText.trim()) return

    // Track the first message as the session concept
    if (!sessionConcept.value) sessionConcept.value = userText.slice(0, 80)

    // Push user message immediately
    messages.value.push({
      id: `user-${Date.now()}`,
      role: 'user',
      content: userText,
      turnNumber: turnNumber.value,
    })

    // Run RDSE (client-side)
    const { qualityScore, confusionCount } = extractDepthSignals(
      userText, domain.value, turnNumber.value,
    )

    // Run SDSM (client-side)
    const nextState = determineNextState(
      turnNumber.value,
      qualityScore,
      0.5, // semantic accuracy placeholder — SUV runs server-side
      confusionCount,
      consecutiveScaffolds.value,
    )

    // Update consecutive scaffolds counter
    if (nextState === 'SCAFFOLD') {
      consecutiveScaffolds.value++
    } else {
      consecutiveScaffolds.value = 0
    }

    // Run CBKT-CS (client-side)
    const newBKT = updateBKT(bktState.value, qualityScore)
    const newClarity = bktToScore(newBKT)
    const newDepthLevel = sdsmToDepthLevel(nextState, qualityScore)

    bktState.value = newBKT
    currentState.value = nextState
    clarityScore.value = newClarity
    depthLevel.value = newDepthLevel

    // Add streaming placeholder for assistant
    const assistantId = `ai-${Date.now()}`
    messages.value.push({
      id: assistantId,
      role: 'assistant',
      content: '',
      turnNumber: turnNumber.value,
      state: nextState,
      clarityScore: newClarity,
      isStreaming: true,
    })
    const aiMsgIdx = messages.value.length - 1

    isStreaming.value = true

    try {
      const token = auth.session?.access_token
      const conversationHistory = messages.value
        .filter((m) => !m.isStreaming)
        .map((m) => ({ role: m.role, content: m.content }))

      const res = await fetch(`${API_BASE}/socratic/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          session_id: sessionId.value,
          message: userText,
          turn_number: turnNumber.value,
          domain: domain.value,
          conversation_history: conversationHistory,
          concepts_covered: conceptsCovered.value,
          // Algorithm outputs
          quality_score: qualityScore,
          confusion_count: confusionCount,
          depth_level: newDepthLevel,
          next_state: nextState,
          semantic_accuracy: 0.5,
          bkt_pl: newBKT.pL,
          clarity_score: newClarity,
        }),
      })

      if (!res.ok) {
        const body = await res.json().catch(() => ({}))
        messages.value[aiMsgIdx].content = body.error || 'Something went wrong. Please try again.'
        messages.value[aiMsgIdx].isStreaming = false
        return
      }

      // Parse SSE
      const reader = res.body!.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() ?? ''

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          const raw = line.slice(6).trim()
          try {
            const payload = JSON.parse(raw)
            if (payload.text) {
              messages.value[aiMsgIdx].content += payload.text
            }
            if (payload.done) {
              messages.value[aiMsgIdx].isStreaming = false
              if (payload.clarity_score !== undefined) clarityScore.value = payload.clarity_score
              if (payload.next_state) currentState.value = payload.next_state as SocraticState
            }
          } catch { /* partial line */ }
        }
      }
    } catch (err) {
      messages.value[aiMsgIdx].content = 'Connection interrupted. Please try again.'
      messages.value[aiMsgIdx].isStreaming = false
    } finally {
      messages.value[aiMsgIdx].isStreaming = false
      isStreaming.value = false
      turnNumber.value++
      canGenerateInsight.value = turnNumber.value >= 4
    }
  }

  async function generateInsight() {
    if (!sessionId.value || insightLoading.value) return
    insightLoading.value = true
    try {
      const token = auth.session?.access_token
      const res = await fetch(`${API_BASE}/socratic/insights`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          session_id: sessionId.value,
          concept: sessionConcept.value,
          domain: domain.value,
          conversation_history: messages.value.map((m) => ({ role: m.role, content: m.content })),
        }),
      })
      if (res.ok) {
        const data = await res.json()
        insightCard.value = data.insight_card
      }
    } finally {
      insightLoading.value = false
    }
  }

  function loadSession(data: { session: any; messages: any[]; insight_card: any | null }) {
    const s = data.session
    sessionId.value = s.id
    domain.value = s.domain
    turnNumber.value = s.turns_count ?? 0

    messages.value = data.messages.map((m: any) => ({
      id: m.id,
      role: m.role as 'user' | 'assistant',
      content: m.content,
      turnNumber: m.turn_number,
      state: (m.algo_state ?? undefined) as SocraticState | undefined,
      clarityScore: m.clarity_score ?? undefined,
      isStreaming: false,
    }))

    if (data.insight_card) {
      insightCard.value = {
        concept: data.insight_card.concept,
        insight: data.insight_card.insight,
        gaps: data.insight_card.gaps || [],
        clarity_score: data.insight_card.clarity_score,
        next_question: data.insight_card.next_question || '',
      }
      canGenerateInsight.value = false
    } else {
      insightCard.value = null
      canGenerateInsight.value = turnNumber.value >= 4
    }

    const firstUser = messages.value.find(m => m.role === 'user')
    if (firstUser) sessionConcept.value = firstUser.content.slice(0, 80)

    const lastAI = [...messages.value].reverse().find(m => m.role === 'assistant')
    if (lastAI?.clarityScore != null) clarityScore.value = lastAI.clarityScore
    if (lastAI?.state) currentState.value = lastAI.state as SocraticState

    bktState.value = DOMAIN_BKT_PRIORS[domain.value] ?? DOMAIN_BKT_PRIORS.general
  }

  function reset() {
    messages.value = []
    sessionId.value = null
    turnNumber.value = 0
    clarityScore.value = 0
    currentState.value = 'PROBE'
    consecutiveScaffolds.value = 0
    canGenerateInsight.value = false
    insightCard.value = null
    sessionConcept.value = ''
    bktState.value = { pL: 0.20, pT: 0.12, pS: 0.10, pG: 0.08 }
  }

  return {
    messages,
    isStreaming,
    sessionId,
    domain,
    turnNumber,
    currentState,
    clarityScore,
    depthLevel,
    conceptsCovered,
    canGenerateInsight,
    insightCard,
    insightLoading,
    sessionConcept,
    stateLabel,
    stateDescription,
    depthLabel,
    startSession,
    sendMessage,
    generateInsight,
    loadSession,
    reset,
  }
}
