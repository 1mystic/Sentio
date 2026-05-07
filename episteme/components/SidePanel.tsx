'use client'

// components/SidePanel.tsx

import { motion, AnimatePresence } from 'framer-motion'
import { DepthMeter } from '@/components/DepthMeter'
import { ClarityScore } from '@/components/ClarityScore'
import { KnowledgeMap } from '@/components/KnowledgeMap'
import type { DepthLevel, InsightCard, Domain } from '@/lib/types'

const STATE_LABELS: Record<string, string> = {
  PROBE:       'Probing',
  DEEPEN:      'Deepening',
  REDIRECT:    'Redirecting',
  SCAFFOLD:    'Scaffolding',
  RECTIFY:     'Rectifying',
  CONSOLIDATE: 'Consolidating',
  COMPLETE:    'Complete',
}

const STATE_DESCRIPTIONS: Record<string, string> = {
  PROBE:       'Mapping your prior knowledge',
  DEEPEN:      'Pushing to the next cognitive level',
  REDIRECT:    'Steering back to the core concept',
  SCAFFOLD:    'Building a minimal foothold',
  RECTIFY:     'Addressing a specific misconception',
  CONSOLIDATE: 'Crystallising what you have built',
  COMPLETE:    'Session has reached natural completion',
}

interface SidePanelProps {
  clarityScore: number
  clarityHistory: number[]
  clarityTrend: 'up' | 'down' | 'stable'
  depthLevel: DepthLevel | null
  previousDepthLevel: DepthLevel | null
  nextState: string | null
  conceptsCovered: string[]
  gaps: string[]
  misconception?: string | null
  domain: Domain
  insightCard: InsightCard | null
  sessionId?: string
}

function SectionDivider() {
  return (
    <div style={{ height: '1px', background: 'var(--border, rgba(0,0,0,0.08))', margin: '0' }} />
  )
}

export function SidePanel({
  clarityScore,
  clarityHistory,
  clarityTrend,
  depthLevel,
  previousDepthLevel,
  nextState,
  conceptsCovered,
  gaps,
  misconception,
  domain,
  insightCard,
  sessionId,
}: SidePanelProps) {
  return (
    <div className="flex flex-col h-full overflow-y-auto" style={{ background: 'var(--bg-surface)' }}>

      {/* ── SDSM State block ──────────────────────────────── */}
      <AnimatePresence mode="wait">
        {nextState ? (
          <motion.div
            key={nextState}
            initial={{ opacity: 0, y: -6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="flex-shrink-0 px-5 pt-5 pb-4"
            style={{ background: 'rgba(255,176,0,0.04)' }}
          >
            <div className="flex items-center gap-2 mb-1.5">
              <span
                className="inline-block animate-pulse flex-shrink-0"
                style={{ width: '7px', height: '7px', borderRadius: '50%', background: 'var(--amber)' }}
              />
              <span
                style={{ fontSize: '12px', fontWeight: 600, color: 'var(--amber)', fontFamily: 'Plus Jakarta Sans, sans-serif' }}
              >
                {STATE_LABELS[nextState] ?? nextState}
              </span>
            </div>
            <p
              style={{ fontSize: '12px', color: 'var(--text-muted)', lineHeight: 1.5, paddingLeft: '15px', fontFamily: 'Plus Jakarta Sans, sans-serif' }}
            >
              {STATE_DESCRIPTIONS[nextState] ?? ''}
            </p>
          </motion.div>
        ) : (
          <motion.div
            key="idle"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex-shrink-0 px-5 pt-5 pb-4"
          >
            <div className="flex items-center gap-2">
              <span
                style={{ width: '7px', height: '7px', borderRadius: '50%', border: '1px solid rgba(255,176,0,0.25)', display: 'inline-block' }}
              />
              <span
                style={{ fontSize: '12px', color: 'var(--text-dim)', fontFamily: 'Plus Jakarta Sans, sans-serif' }}
              >
                Waiting to begin
              </span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <SectionDivider />

      {/* ── Clarity score ─────────────────────────────────── */}
      <div className="px-5 py-5 flex-shrink-0">
        <ClarityScore score={clarityScore} history={clarityHistory} trend={clarityTrend} />
      </div>

      <SectionDivider />

      {/* ── Depth meter ───────────────────────────────────── */}
      <div className="px-5 py-5 flex-shrink-0">
        <DepthMeter depth={depthLevel} previousDepth={previousDepthLevel} />
      </div>

      <SectionDivider />

      {/* ── Session stats strip ───────────────────────────── */}
      <div className="flex-shrink-0 px-5 py-4 grid grid-cols-2 gap-4">
        <div>
          <p style={{ fontSize: '11px', color: 'var(--text-dim)', marginBottom: '4px', fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
            Domain
          </p>
          <p style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-muted)', fontFamily: 'Plus Jakarta Sans, sans-serif', textTransform: 'capitalize' }}>
            {domain}
          </p>
        </div>
        <div>
          <p style={{ fontSize: '11px', color: 'var(--text-dim)', marginBottom: '4px', fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
            Concepts
          </p>
          <p style={{ fontSize: '13px', fontWeight: 700, color: conceptsCovered.length > 0 ? 'var(--amber)' : 'var(--text-dim)', fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
            {conceptsCovered.length}
          </p>
        </div>
        {insightCard && (
          <div className="col-span-2">
            <p style={{ fontSize: '11px', color: 'var(--text-dim)', marginBottom: '4px', fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
              Clarity at close
            </p>
            <p style={{ fontSize: '13px', fontWeight: 700, color: 'var(--amber)', fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
              {insightCard.clarity_score}/100
            </p>
          </div>
        )}
      </div>

      <SectionDivider />

      {/* ── Knowledge map ─────────────────────────────────── */}
      <div className="px-5 py-5 flex-1">
        <KnowledgeMap concepts={conceptsCovered} gaps={gaps} domain={domain} />
      </div>

      {sessionId && (
        <div style={{ padding: '12px 16px', borderTop: '1px solid var(--border)' }}>
          <a
            href={`/knowledge-graph/${sessionId}`}
            target="_blank"
            rel="noopener noreferrer"
            style={{
              display: 'block',
              fontFamily: 'Plus Jakarta Sans, sans-serif',
              fontSize: '12px',
              fontWeight: 600,
              color: 'var(--amber)',
              textDecoration: 'none',
              textAlign: 'center',
              padding: '8px',
              background: 'rgba(255,176,0,0.06)',
              border: '1px solid rgba(255,176,0,0.2)',
              borderRadius: '8px',
            }}
            onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.background = 'rgba(255,176,0,0.10)' }}
            onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.background = 'rgba(255,176,0,0.06)' }}
          >
            View Knowledge Map ↗
          </a>
        </div>
      )}
    </div>
  )
}
