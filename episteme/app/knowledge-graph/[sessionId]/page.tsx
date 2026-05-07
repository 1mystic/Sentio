'use client'

import { useState, useEffect, useCallback } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import { KnowledgeGraphD3 } from '@/components/KnowledgeGraphD3'

interface GraphData {
  session: { domain: string; turns_count: number; updated_at: string }
  nodes: Array<{ id: string; label: string; type: 'explored' | 'gap' | 'prerequisite'; clarity: number; centrality: number; bktPL: number }>
  edges: Array<{ source: string; target: string; strength: number }>
  fingerprint: {
    bloom_distribution: Record<string, number>
    state_frequencies: Record<string, number>
    avg_quality_score: number
    active_misconceptions: string[]
    next_session_question: string
    independent_reasoning_streak: number
    total_turns: number
  } | null
  insightCard: { concept: string; insight: string; gaps: string[]; clarity_score: number } | null
  learnerProfile: { next_session_starter: string; metacognitive_note: string; strength_areas: string[]; urgent_gaps: string[] } | null
  bloomData: Array<{ level: string; count: number; pct: number }>
  gapSchedule: Array<{ concept: string; urgency: number; reviewInHours: number }>
  messageCount: number
}

const BLOOM_COLORS: Record<string, string> = {
  SURFACE: 'rgba(255,176,0,0.3)',
  CONCEPTUAL: 'rgba(255,176,0,0.5)',
  ANALYTICAL: 'rgba(255,176,0,0.75)',
  SYNTHESIS: '#FFB000',
}

const STATE_LABELS: Record<string, string> = {
  PROBE: 'PROBE', DEEPEN: 'DEEPEN', SCAFFOLD: 'SCAFFOLD',
  RECTIFY: 'RECTIFY', REDIRECT: 'REDIRECT', CONSOLIDATE: 'CONSOL', COMPLETE: 'DONE',
}

const font = 'Plus Jakarta Sans, sans-serif'

export default function KnowledgeGraphPage() {
  const params = useParams()
  const sessionId = params.sessionId as string
  const [data, setData] = useState<GraphData | null>(null)
  const [loading, setLoading] = useState(true)
  const [selectedNode, setSelectedNode] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch(`/api/knowledge-graph/${sessionId}`)
      .then(r => r.json())
      .then((d: GraphData) => { setData(d); setLoading(false) })
      .catch(() => { setError('Failed to load graph data'); setLoading(false) })
  }, [sessionId])

  const handleNodeClick = useCallback((nodeId: string) => {
    setSelectedNode(prev => prev === nodeId ? null : nodeId)
  }, [])

  if (loading) {
    return (
      <div style={{ background: '#09090e', height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <span style={{ fontFamily: font, fontSize: '13px', color: '#FFB000' }}>Loading graph...</span>
      </div>
    )
  }

  if (error || !data) {
    return (
      <div style={{ background: '#09090e', height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <span style={{ fontFamily: font, fontSize: '13px', color: 'rgba(255,255,255,0.4)' }}>{error || 'No data'}</span>
      </div>
    )
  }

  const selectedNodeData = selectedNode ? data.nodes.find(n => n.id === selectedNode) : null
  const date = new Date(data.session.updated_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })

  return (
    <div style={{ background: '#09090e', height: '100vh', display: 'flex', flexDirection: 'column', overflow: 'hidden', fontFamily: font }}>
      {/* Header */}
      <div style={{
        borderBottom: '1px solid rgba(255,176,0,0.25)',
        padding: '10px 20px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexShrink: 0,
        background: 'rgba(9,9,14,0.92)',
        backdropFilter: 'blur(12px)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <Link href={`/session/${sessionId}`} style={{ fontFamily: font, fontSize: '12px', fontWeight: 600, color: '#FFB000', textDecoration: 'none' }}>
            ← Back
          </Link>
          <span style={{ color: 'rgba(255,255,255,0.12)', fontSize: '12px' }}>/</span>
          <span style={{ fontFamily: font, fontSize: '12px', color: 'rgba(255,255,255,0.35)' }}>
            Episteme · Knowledge Graph · {data.session.domain} · {date}
          </span>
        </div>
        <Link
          href={`/flashcards/${sessionId}`}
          style={{
            fontFamily: font,
            fontSize: '12px',
            fontWeight: 600,
            color: '#FFB000',
            border: '1px solid rgba(255,176,0,0.3)',
            borderRadius: '9999px',
            padding: '5px 14px',
            textDecoration: 'none',
          }}
        >
          Flashcards →
        </Link>
      </div>

      {/* Main layout */}
      <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
        {/* Graph panel */}
        <div style={{ flex: '0 0 60%', position: 'relative', borderRight: '1px solid rgba(255,176,0,0.20)' }}>
          <KnowledgeGraphD3
            nodes={data.nodes}
            edges={data.edges}
            onNodeClick={handleNodeClick}
          />
          {/* Node detail overlay */}
          {selectedNodeData && (
            <div style={{
              position: 'absolute', bottom: '16px', left: '16px', right: '16px',
              background: 'rgba(15,15,24,0.94)',
              backdropFilter: 'blur(16px)',
              border: '1px solid rgba(255,176,0,0.25)',
              borderRadius: '12px',
              padding: '12px 16px',
            }}>
              <div style={{ fontFamily: font, fontSize: '13px', fontWeight: 600, color: '#FFB000', marginBottom: '4px' }}>
                {selectedNodeData.label}
              </div>
              <div style={{ fontFamily: font, fontSize: '11px', color: 'rgba(255,255,255,0.45)' }}>
                Type: {selectedNodeData.type} · Clarity: {selectedNodeData.clarity}/100 · BKT P(L): {selectedNodeData.bktPL.toFixed(2)}
              </div>
            </div>
          )}
          {/* Legend */}
          <div style={{ position: 'absolute', top: '12px', left: '12px', display: 'flex', gap: '12px' }}>
            {[
              { color: 'rgba(255,176,0,0.6)', label: 'Explored', dash: false },
              { color: 'rgba(255,255,255,0.25)', label: 'Gap', dash: true },
            ].map(({ color, label, dash }) => (
              <div key={label} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: color, border: dash ? '1px dashed rgba(255,255,255,0.45)' : 'none' }} />
                <span style={{ fontFamily: font, fontSize: '11px', color: 'rgba(255,255,255,0.4)' }}>{label}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Report panel */}
        <div style={{ flex: '0 0 40%', overflowY: 'auto', padding: '20px 24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>

          {/* Session summary */}
          <section>
            <div style={{ fontFamily: font, fontSize: '11px', fontWeight: 600, color: '#FFB000', letterSpacing: '0.04em', marginBottom: '10px', borderBottom: '1px solid rgba(255,176,0,0.12)', paddingBottom: '6px' }}>
              Session Summary
            </div>
            {data.insightCard && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                <div style={{ fontFamily: font, fontSize: '14px', fontWeight: 600, color: '#ede8f5' }}>
                  {data.insightCard.concept}
                </div>
                <div style={{ fontFamily: font, fontSize: '12px', color: 'rgba(255,255,255,0.4)', display: 'flex', gap: '12px' }}>
                  <span>Clarity: {data.insightCard.clarity_score}/100</span>
                  <span>Turns: {data.session.turns_count}</span>
                  <span>Msgs: {data.messageCount}</span>
                </div>
              </div>
            )}
          </section>

          {/* Bloom distribution */}
          {data.bloomData.some(b => b.count > 0) && (
            <section>
              <div style={{ fontFamily: font, fontSize: '11px', fontWeight: 600, color: '#FFB000', letterSpacing: '0.04em', marginBottom: '10px', borderBottom: '1px solid rgba(255,176,0,0.12)', paddingBottom: '6px' }}>
                Bloom Distribution
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {data.bloomData.map(b => (
                  <div key={b.level} style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <div style={{ fontFamily: font, fontSize: '11px', color: 'rgba(255,255,255,0.4)', width: '80px' }}>{b.level}</div>
                    <div style={{ flex: 1, height: '5px', background: 'rgba(255,255,255,0.06)', borderRadius: '3px', overflow: 'hidden' }}>
                      <div style={{ height: '100%', width: `${b.pct}%`, background: BLOOM_COLORS[b.level] || '#FFB000', borderRadius: '3px', transition: 'width 0.5s' }} />
                    </div>
                    <div style={{ fontFamily: font, fontSize: '11px', color: 'rgba(255,255,255,0.35)', width: '32px', textAlign: 'right' }}>{b.pct}%</div>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* SDSM state frequency */}
          {data.fingerprint?.state_frequencies && (
            <section>
              <div style={{ fontFamily: font, fontSize: '11px', fontWeight: 600, color: '#FFB000', letterSpacing: '0.04em', marginBottom: '10px', borderBottom: '1px solid rgba(255,176,0,0.12)', paddingBottom: '6px' }}>
                State Usage
              </div>
              <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                {Object.entries(data.fingerprint.state_frequencies).filter(([, v]) => v > 0).map(([state, count]) => (
                  <div key={state} style={{ fontFamily: font, fontSize: '11px', fontWeight: 500, padding: '3px 10px', border: '1px solid rgba(255,176,0,0.18)', borderRadius: '9999px', color: 'rgba(255,255,255,0.5)' }}>
                    {STATE_LABELS[state] || state}: {count as number}
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Active misconceptions */}
          {(data.fingerprint?.active_misconceptions?.length ?? 0) > 0 && (
            <section>
              <div style={{ fontFamily: font, fontSize: '11px', fontWeight: 600, color: '#FFB000', letterSpacing: '0.04em', marginBottom: '10px', borderBottom: '1px solid rgba(255,176,0,0.12)', paddingBottom: '6px' }}>
                Misconceptions
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {data.fingerprint?.active_misconceptions?.map((m, i) => (
                  <div key={i} style={{ fontFamily: font, fontSize: '12px', color: 'rgba(255,255,255,0.55)', padding: '8px 12px', background: 'rgba(248,113,113,0.06)', border: '1px solid rgba(248,113,113,0.18)', borderRadius: '8px' }}>
                    {m}
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* EGP gap schedule */}
          {data.gapSchedule.length > 0 && (
            <section>
              <div style={{ fontFamily: font, fontSize: '11px', fontWeight: 600, color: '#FFB000', letterSpacing: '0.04em', marginBottom: '10px', borderBottom: '1px solid rgba(255,176,0,0.12)', paddingBottom: '6px' }}>
                Review Schedule
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                {data.gapSchedule.map((g, i) => (
                  <div key={i} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 12px', background: 'rgba(255,255,255,0.03)', borderRadius: '8px' }}>
                    <span style={{ fontFamily: font, fontSize: '12px', color: 'rgba(255,255,255,0.6)' }}>{g.concept.slice(0, 28)}</span>
                    <span style={{ fontFamily: font, fontSize: '11px', color: g.urgency < 50 ? '#FFB000' : 'rgba(255,255,255,0.3)' }}>
                      review in {g.reviewInHours}h
                    </span>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Metacognitive notes */}
          {data.learnerProfile?.metacognitive_note && (
            <section>
              <div style={{ fontFamily: font, fontSize: '11px', fontWeight: 600, color: '#FFB000', letterSpacing: '0.04em', marginBottom: '10px', borderBottom: '1px solid rgba(255,176,0,0.12)', paddingBottom: '6px' }}>
                Insights
              </div>
              <p style={{ fontFamily: font, fontSize: '13px', color: 'rgba(255,255,255,0.55)', lineHeight: 1.7, fontStyle: 'italic' }}>
                {data.learnerProfile.metacognitive_note}
              </p>
            </section>
          )}

          {/* Next session */}
          {(data.fingerprint?.next_session_question || data.learnerProfile?.next_session_starter) && (
            <section>
              <div style={{ fontFamily: font, fontSize: '11px', fontWeight: 600, color: '#FFB000', letterSpacing: '0.04em', marginBottom: '10px', borderBottom: '1px solid rgba(255,176,0,0.12)', paddingBottom: '6px' }}>
                Next Session
              </div>
              <p style={{ fontFamily: font, fontSize: '13px', color: '#ede8f5', lineHeight: 1.7, marginBottom: '16px', borderLeft: '2px solid rgba(255,176,0,0.4)', paddingLeft: '14px' }}>
                {data.fingerprint?.next_session_question || data.learnerProfile?.next_session_starter}
              </p>
              <Link
                href={`/?resume=${sessionId}`}
                style={{
                  display: 'inline-block',
                  fontFamily: font,
                  fontSize: '13px',
                  fontWeight: 700,
                  color: '#09090e',
                  background: '#FFB000',
                  padding: '10px 20px',
                  textDecoration: 'none',
                  borderRadius: '9999px',
                  boxShadow: '0 4px 16px rgba(255,176,0,0.3)',
                }}
              >
                Start New Session →
              </Link>
            </section>
          )}
        </div>
      </div>
    </div>
  )
}
