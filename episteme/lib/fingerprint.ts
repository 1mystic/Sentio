// lib/fingerprint.ts
import { createServerSupabaseClient } from './supabase-server'
import type { SocraticState, DepthLevel } from './types'

export async function updateSessionFingerprint(
  sessionId: string,
  turnData: {
    state: SocraticState
    depthLevel: DepthLevel
    qualityScore: number
    bktDelta: number
    misconception: string | null
    turnNumber: number
  }
): Promise<void> {
  const supabase = createServerSupabaseClient()

  const { data: existing } = await supabase
    .from('session_fingerprints')
    .select('*')
    .eq('session_id', sessionId)
    .single()

  const fp = existing || {
    session_id: sessionId,
    state_frequencies: { PROBE:0,DEEPEN:0,SCAFFOLD:0,RECTIFY:0,REDIRECT:0,CONSOLIDATE:0,COMPLETE:0 },
    bloom_distribution: { SURFACE:0,CONCEPTUAL:0,ANALYTICAL:0,SYNTHESIS:0 },
    avg_bkt_delta: 0,
    avg_quality_score: 0,
    total_turns: 0,
    active_misconceptions: [] as string[],
    independent_reasoning_streak: 0,
    dominant_reasoning_style: 'unknown',
    strong_concepts: [] as string[],
    weak_concepts: [] as string[],
  }

  const freqs = fp.state_frequencies as Record<string, number>
  freqs[turnData.state] = (freqs[turnData.state] || 0) + 1

  const bloom = fp.bloom_distribution as Record<string, number>
  bloom[turnData.depthLevel] = (bloom[turnData.depthLevel] || 0) + 1

  const n = fp.total_turns
  const avgQuality = (fp.avg_quality_score * n + turnData.qualityScore) / (n + 1)
  const avgDelta = (fp.avg_bkt_delta * n + turnData.bktDelta) / (n + 1)

  const misconceptions: string[] = fp.active_misconceptions || []
  if (turnData.misconception && !misconceptions.includes(turnData.misconception)) {
    misconceptions.push(turnData.misconception)
    if (misconceptions.length > 5) misconceptions.shift()
  }

  // Track independent reasoning streak: increment when quality > 0.7, reset otherwise
  const streak = turnData.qualityScore > 0.7
    ? (fp.independent_reasoning_streak || 0) + 1
    : 0

  await supabase
    .from('session_fingerprints')
    .upsert({
      ...fp,
      session_id: sessionId,
      state_frequencies: freqs,
      bloom_distribution: bloom,
      avg_quality_score: avgQuality,
      avg_bkt_delta: avgDelta,
      total_turns: n + 1,
      active_misconceptions: misconceptions,
      independent_reasoning_streak: streak,
      updated_at: new Date().toISOString(),
    }, { onConflict: 'session_id' })
}
