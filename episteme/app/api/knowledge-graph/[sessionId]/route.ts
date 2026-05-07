import { createServerSupabaseClient } from '@/lib/supabase-server'
import { NextResponse } from 'next/server'

interface GraphNode {
  id: string
  label: string
  type: 'explored' | 'gap' | 'prerequisite'
  clarity: number
  centrality: number
  bktPL: number
}

interface GraphEdge {
  source: string
  target: string
  strength: number
}

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ sessionId: string }> }
): Promise<Response> {
  const { sessionId } = await params

  const supabase = createServerSupabaseClient()

  const [
    { data: session },
    { data: messages },
    { data: concepts },
    { data: fingerprint },
    { data: insightCard },
    { data: learnerProfile },
  ] = await Promise.all([
    supabase.from('sessions').select('*').eq('id', sessionId).single(),
    supabase.from('messages').select('role, content, turn_number').eq('session_id', sessionId).order('turn_number'),
    supabase.from('concepts').select('*').eq('session_id', sessionId),
    supabase.from('session_fingerprints').select('*').eq('session_id', sessionId).single(),
    supabase.from('insight_cards').select('*').eq('session_id', sessionId).single(),
    supabase.from('learner_profiles').select('*').eq('session_id', sessionId).single(),
  ])

  if (!session) {
    return NextResponse.json({ error: 'Session not found' }, { status: 404 })
  }

  // Build graph nodes from explored concepts
  const conceptList = (concepts || []) as Array<{
    id: string; name: string; depth_reached: string; clarity_score: number; bkt_pL: number
  }>

  const maxClarity = Math.max(...conceptList.map(c => c.clarity_score), 1)

  const exploredNodes: GraphNode[] = conceptList.map((c, i) => ({
    id: c.id,
    label: c.name.slice(0, 20),
    type: 'explored',
    clarity: c.clarity_score,
    centrality: (conceptList.length - i) / conceptList.length,
    bktPL: c.bkt_pL || 0.3,
  }))

  // Gap nodes from insight card
  const gapNodes: GraphNode[] = ((insightCard?.gaps as string[]) || []).map((gap, i) => ({
    id: `gap-${i}`,
    label: gap.slice(0, 20),
    type: 'gap',
    clarity: 0,
    centrality: 0.3,
    bktPL: 0.1,
  }))

  const nodes: GraphNode[] = [...exploredNodes, ...gapNodes]

  // Edges: connect explored nodes in sequence, connect last explored to gap nodes
  const edges: GraphEdge[] = []
  for (let i = 0; i < exploredNodes.length - 1; i++) {
    edges.push({ source: exploredNodes[i].id, target: exploredNodes[i + 1].id, strength: 0.8 })
  }
  if (exploredNodes.length > 0) {
    const lastExplored = exploredNodes[exploredNodes.length - 1]
    gapNodes.forEach(gap => {
      edges.push({ source: lastExplored.id, target: gap.id, strength: 0.4 })
    })
  }

  // Bloom distribution with percentages
  const bloomRaw = (fingerprint?.bloom_distribution as Record<string, number>) || {}
  const bloomTotal = Object.values(bloomRaw).reduce((a, b) => a + b, 0) || 1
  const bloomData = Object.entries(bloomRaw).map(([level, count]) => ({
    level,
    count,
    pct: Math.round((count / bloomTotal) * 100),
  }))

  // EGP gap schedule
  const clarityScore = (insightCard?.clarity_score as number) || 50
  const updatedAt = session.updated_at as string
  const hoursElapsed = (Date.now() - new Date(updatedAt).getTime()) / 3600000
  const S = 2 * Math.exp(4 * (clarityScore / 100) + 0.5 * Math.log(2))

  const gapSchedule = ((insightCard?.gaps as string[]) || []).map((concept, i) => {
    const urgency = Math.exp(-hoursElapsed / (S * (1 + i * 0.5)))
    return {
      concept,
      urgency: Math.round(urgency * 100),
      reviewInHours: Math.round(S * (1 + i * 0.5) * (1 - urgency) * 10),
    }
  })

  return NextResponse.json({
    session,
    nodes,
    edges,
    fingerprint: fingerprint || null,
    insightCard: insightCard || null,
    learnerProfile: learnerProfile || null,
    bloomData,
    gapSchedule,
    messageCount: (messages || []).length,
  })
}
