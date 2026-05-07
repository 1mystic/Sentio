'use client'

// app/session/[sessionId]/page.tsx

import { useState, useCallback, useRef, useEffect } from 'react'
import { useParams } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import Link from 'next/link'
import { useSession } from '@/hooks/useSession'
import { useClarity } from '@/hooks/useClarity'
import { useAuth } from '@/hooks/useAuth'
import { ChatPanel } from '@/components/ChatPanel'
import { SidePanel } from '@/components/SidePanel'
import { NotificationBell } from '@/components/NotificationBell'
import { QuickCapture } from '@/components/QuickCapture'
import { FocusTimer } from '@/components/FocusTimer'
import { ArrowLeft } from 'lucide-react'
import type { DepthLevel, InsightCard as InsightCardType, Domain } from '@/lib/types'

const DOMAIN_LABELS: Record<string, string> = {
  ml: 'Machine Learning',
  statistics: 'Statistics',
  economics: 'Economics',
  cs: 'Computer Science',
  general: 'General',
}

const STATE_LABELS: Record<string, string> = {
  PROBE:       'Probing',
  DEEPEN:      'Deepening',
  REDIRECT:    'Redirecting',
  SCAFFOLD:    'Scaffolding',
  RECTIFY:     'Rectifying',
  CONSOLIDATE: 'Consolidating',
  COMPLETE:    'Complete',
}

const DEFAULT_SIDEBAR_WIDTH = 380
const MIN_SIDEBAR_WIDTH = 280
const MAX_SIDEBAR_WIDTH = 560

export default function SessionPage() {
  const params = useParams()
  const sessionId = params.sessionId as string

  const { session, messages: savedMessages, concepts: savedConcepts, fingerprint, learnerProfile, insightCard: savedInsightCard, isLoading, error } = useSession(sessionId)
  const { score: clarityScore, history: clarityHistory, updateScore, trend } = useClarity(0)
  const { user } = useAuth()

  // Seed sidebar state from saved session data (populated after useSession loads)
  const [depthLevel, setDepthLevel] = useState<DepthLevel | null>(null)
  const [prevDepthLevel, setPrevDepthLevel] = useState<DepthLevel | null>(null)
  const [nextState, setNextState] = useState<string | null>(null)
  const [insightCard, setInsightCard] = useState<InsightCardType | null>(null)
  const [conceptsCovered, setConceptsCovered] = useState<string[]>([])
  const [gaps, setGaps] = useState<string[]>([])
  const [misconception, setMisconception] = useState<string | null>(null)

  // Once session data loads, seed sidebar state from saved records
  useEffect(() => {
    if (savedConcepts.length > 0) {
      const last = savedConcepts[savedConcepts.length - 1]
      setDepthLevel(last.depth_reached as DepthLevel)
      setConceptsCovered(savedConcepts.map((c) => c.name))
      updateScore(last.clarity_score)
    } else {
      // Fallback 1: lastClarityScore stored directly in session_state (added in recent fix)
      // Fallback 2: derive from semanticAccuracy (older sessions that predate the fix)
      const ss = session?.session_state as {
        lastClarityScore?: number
        semanticAccuracy?: number
      } | null
      if (ss?.lastClarityScore) {
        updateScore(ss.lastClarityScore)
      } else if (ss?.semanticAccuracy != null) {
        // semanticAccuracy is 0–1; map to a 0–100 clarity estimate
        updateScore(Math.round(ss.semanticAccuracy * 100))
      }
    }
    const ss = session?.session_state as { lastState?: string } | null
    if (ss?.lastState) setNextState(ss.lastState)
    // Seed gaps from insight card (primary) or learner profile urgent_gaps (fallback)
    if (savedInsightCard?.gaps?.length) {
      setGaps(savedInsightCard.gaps)
    } else if (learnerProfile?.urgent_gaps?.length) {
      setGaps(learnerProfile.urgent_gaps)
    }
    // Seed insight card so sidebar shows "Clarity at close" on session resume
    if (savedInsightCard) {
      setInsightCard(savedInsightCard)
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [savedConcepts, session, learnerProfile, savedInsightCard])
  const [showSidePanel, setShowSidePanel] = useState(false)
  const [sidebarWidth, setSidebarWidth] = useState(() =>
    typeof window !== 'undefined' ? Math.max(Math.round(window.innerWidth * 0.30), MIN_SIDEBAR_WIDTH) : DEFAULT_SIDEBAR_WIDTH
  )

  const isDragging = useRef(false)
  const dragStartX = useRef(0)
  const dragStartWidth = useRef(DEFAULT_SIDEBAR_WIDTH)

  const handleDragStart = useCallback((e: React.MouseEvent) => {
    isDragging.current = true
    dragStartX.current = e.clientX
    dragStartWidth.current = sidebarWidth
    document.body.style.cursor = 'col-resize'
    document.body.style.userSelect = 'none'
  }, [sidebarWidth])

  useEffect(() => {
    const onMove = (e: MouseEvent) => {
      if (!isDragging.current) return
      const delta = e.clientX - dragStartX.current
      const next = Math.max(MIN_SIDEBAR_WIDTH, Math.min(MAX_SIDEBAR_WIDTH, dragStartWidth.current + delta))
      setSidebarWidth(next)
    }
    const onUp = () => {
      if (!isDragging.current) return
      isDragging.current = false
      document.body.style.cursor = ''
      document.body.style.userSelect = ''
    }
    document.addEventListener('mousemove', onMove)
    document.addEventListener('mouseup', onUp)
    return () => {
      document.removeEventListener('mousemove', onMove)
      document.removeEventListener('mouseup', onUp)
    }
  }, [])

  const handleClarityUpdate = useCallback((score: number) => updateScore(score), [updateScore])

  const handleDepthUpdate = useCallback((depth: DepthLevel) => {
    setDepthLevel((prev) => {
      setPrevDepthLevel(prev)
      return depth
    })
  }, [])

  const handleInsightGenerated = useCallback((card: InsightCardType) => {
    setInsightCard(card)
  }, [])

  const handleConceptsUpdate = useCallback((concepts: string[]) => {
    setConceptsCovered(concepts)
  }, [])

  const handleNextStateUpdate = useCallback((state: string) => {
    setNextState(state)
  }, [])

  const handleGapsUpdate = useCallback((g: string[]) => {
    setGaps(g)
  }, [])

  const handleMisconceptionUpdate = useCallback((m: string | null) => {
    setMisconception(m)
  }, [])

  if (isLoading) {
    return (
      <div
        className="min-h-screen flex flex-col items-center justify-center gap-4"
        style={{ background: 'var(--bg)' }}
      >
        <motion.div
          animate={{ scale: [0.8, 1.2, 0.8], opacity: [0.6, 1, 0.6] }}
          transition={{ duration: 1.4, repeat: Infinity, ease: 'easeInOut' }}
          style={{ width: '8px', height: '8px', background: 'var(--amber)', borderRadius: '50%' }}
        />
        <p style={{ fontSize: '12px', color: 'var(--text-dim)', fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
          Loading session...
        </p>
      </div>
    )
  }

  if (error || !session) {
    return (
      <div
        className="min-h-screen flex flex-col items-center justify-center gap-5"
        style={{ background: 'var(--bg)' }}
      >
        <p style={{ fontSize: '18px', fontWeight: 600, color: 'var(--text)', fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
          {error ?? 'Session not found.'}
        </p>
        <Link
          href="/"
          className="transition-opacity hover:opacity-70"
          style={{ fontSize: '13px', fontWeight: 600, color: 'var(--amber)', fontFamily: 'Plus Jakarta Sans, sans-serif', textDecoration: 'none' }}
        >
          <span className="flex items-center gap-1.5"><ArrowLeft size={14} /> Return to home</span>
        </Link>
      </div>
    )
  }

  return (
    <div
      className="h-screen flex flex-col overflow-hidden"
      style={{ background: 'var(--bg)' }}
    >
      {/* ── Top status bar ───────────────────────────────────────────────────── */}
      <div
        className="flex items-center justify-between px-5 flex-shrink-0"
        style={{
          height: '52px',
          borderBottom: '1px solid var(--border)',
          background: 'rgba(9,9,14,0.92)',
          backdropFilter: 'blur(20px)',
          WebkitBackdropFilter: 'blur(20px)',
        }}
      >
        {/* Left: brand + domain */}
        <div className="flex items-center gap-3">
          <Link
            href="/"
            className="transition-opacity hover:opacity-80"
            style={{ fontSize: '17px', fontWeight: 800, color: 'var(--amber)', fontFamily: 'Plus Jakarta Sans, sans-serif', textDecoration: 'none', letterSpacing: '-0.02em' }}
          >
            Episteme
          </Link>
          <span style={{ color: 'var(--outline-variant)', fontSize: '16px', fontWeight: 300 }}>/</span>
          <span
            style={{ fontSize: '13px', color: 'var(--text-dim)', fontFamily: 'Plus Jakarta Sans, sans-serif', fontWeight: 500 }}
          >
            {DOMAIN_LABELS[session.domain] ?? session.domain}
          </span>
          <Link
            href={`/knowledge-graph/${sessionId}`}
            target="_blank"
            className="transition-opacity hover:opacity-70 hidden sm:block"
            style={{ fontSize: '12px', color: 'rgba(255,176,0,0.5)', textDecoration: 'none', fontFamily: 'Plus Jakarta Sans, sans-serif', fontWeight: 500 }}
          >
            Map ↗
          </Link>
        </div>

        {/* Right: SDSM state chip + clarity score + mobile toggle */}
        <div className="flex items-center gap-3">
          <AnimatePresence mode="wait">
            {nextState && (
              <motion.div
                key={nextState}
                initial={{ opacity: 0, y: -4 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 4 }}
                transition={{ duration: 0.25 }}
                className="hidden sm:flex items-center gap-2 px-3 py-1.5"
                style={{
                  border: '1px solid rgba(255,176,0,0.20)',
                  background: 'var(--primary-soft)',
                  borderRadius: '9999px',
                }}
              >
                <span
                  className="inline-block animate-pulse"
                  style={{ width: '6px', height: '6px', borderRadius: '50%', background: 'var(--amber)' }}
                />
                <span
                  style={{ fontSize: '12px', fontWeight: 600, color: 'var(--amber)', fontFamily: 'Plus Jakarta Sans, sans-serif' }}
                >
                  {STATE_LABELS[nextState] ?? nextState}
                </span>
              </motion.div>
            )}
          </AnimatePresence>

          <NotificationBell sessionId={sessionId} />
          <FocusTimer sessionId={sessionId} />

          {clarityScore > 0 && (
            <div className="flex items-center gap-1 px-2.5 py-1" style={{ background: 'var(--primary-container)', borderRadius: '9999px' }}>
              <span
                style={{ fontSize: '14px', fontWeight: 700, color: 'var(--amber)', fontFamily: 'Plus Jakarta Sans, sans-serif', letterSpacing: '-0.02em' }}
              >
                {clarityScore}
              </span>
              <span style={{ fontSize: '11px', color: 'var(--text-dim)', fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
                /100
              </span>
            </div>
          )}

          <button
            className="md:hidden px-3 py-1.5 transition-colors"
            style={{
              fontSize: '12px',
              fontWeight: 600,
              color: 'var(--text-muted)',
              border: '1px solid var(--border)',
              borderRadius: '9999px',
              background: showSidePanel ? 'var(--primary-soft)' : 'transparent',
              fontFamily: 'Plus Jakarta Sans, sans-serif',
            }}
            onClick={() => setShowSidePanel((p) => !p)}
          >
            {showSidePanel ? 'Hide' : 'Stats'}
          </button>

          {/* User avatar */}
          {user && (
            <Link
              href="/dashboard"
              title={user.email ?? 'Dashboard'}
              className="flex items-center justify-center transition-all duration-150 flex-shrink-0"
              style={{
                width: '32px',
                height: '32px',
                borderRadius: '50%',
                background: 'rgba(255,176,0,0.12)',
                border: '1px solid rgba(255,176,0,0.3)',
                fontSize: '13px',
                fontWeight: 700,
                color: 'var(--amber)',
                textDecoration: 'none',
                fontFamily: 'Plus Jakarta Sans, sans-serif',
              }}
              onMouseEnter={(e) => { e.currentTarget.style.background = 'rgba(255,176,0,0.20)' }}
              onMouseLeave={(e) => { e.currentTarget.style.background = 'rgba(255,176,0,0.12)' }}
            >
              {(user.email ?? 'U').charAt(0).toUpperCase()}
            </Link>
          )}
        </div>
      </div>

      {/* ── Main layout ──────────────────────────────────────────────────────── */}
      <div className="flex flex-1 overflow-hidden">

        {/* Desktop sidebar — resizable */}
        <div
          className="hidden md:flex flex-shrink-0 flex-col"
          style={{ width: `${sidebarWidth}px`, borderRight: '1px solid var(--border)' }}
        >
          <SidePanel
            clarityScore={clarityScore}
            clarityHistory={clarityHistory}
            clarityTrend={trend}
            depthLevel={depthLevel}
            previousDepthLevel={prevDepthLevel}
            nextState={nextState}
            conceptsCovered={conceptsCovered}
            gaps={gaps}
            misconception={misconception}
            domain={session.domain as Domain}
            insightCard={insightCard}
            sessionId={sessionId}
          />
        </div>

        {/* Drag handle */}
        <div
          className="hidden md:flex flex-shrink-0 items-center justify-center cursor-col-resize group"
          style={{ width: '6px', background: 'transparent', position: 'relative' }}
          onMouseDown={handleDragStart}
        >
          <div
            className="transition-all duration-150"
            style={{
              width: '3px',
              height: '40px',
              background: 'var(--outline-variant)',
              borderRadius: '2px',
            }}
          />
          <div
            className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity"
            style={{ background: 'var(--primary-soft)' }}
          />
        </div>

        {/* Mobile side panel overlay */}
        <AnimatePresence>
          {showSidePanel && (
            <motion.div
              initial={{ x: -300 }}
              animate={{ x: 0 }}
              exit={{ x: -300 }}
              transition={{ duration: 0.25, ease: [0.22, 1, 0.36, 1] }}
              className="md:hidden fixed inset-y-0 left-0 z-30 flex flex-col"
              style={{
                width: '280px',
                background: 'var(--bg-surface)',
                borderRight: '1px solid var(--border)',
                top: '52px',
              }}
            >
              <SidePanel
                clarityScore={clarityScore}
                clarityHistory={clarityHistory}
                clarityTrend={trend}
                depthLevel={depthLevel}
                previousDepthLevel={prevDepthLevel}
                nextState={nextState}
                conceptsCovered={conceptsCovered}
                gaps={gaps}
                domain={session.domain as Domain}
                insightCard={insightCard}
                sessionId={sessionId}
              />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Chat panel — seeded with saved messages so returning users see history */}
        <div className="flex-1 flex flex-col overflow-hidden min-w-0">
          {session.is_complete && learnerProfile?.next_session_starter && (
            <div style={{
              padding: '12px 20px',
              background: 'rgba(255,176,0,0.05)',
              borderBottom: '1px solid rgba(255,176,0,0.12)',
              display: 'flex',
              alignItems: 'flex-start',
              gap: '12px',
              flexShrink: 0,
            }}>
              <span style={{ fontFamily: 'Plus Jakarta Sans, sans-serif', fontSize: '11px', fontWeight: 700, color: 'var(--amber)', flexShrink: 0, paddingTop: '2px' }}>
                Next session
              </span>
              <p style={{ fontSize: '13px', color: 'var(--text-muted)', lineHeight: 1.5, margin: 0, fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
                {learnerProfile.next_session_starter}
              </p>
            </div>
          )}
          <ChatPanel
            sessionId={sessionId}
            domain={session.domain as Domain}
            initial={{
              messages: savedMessages,
              concepts: savedConcepts,
              nextState: session.session_state?.lastState ?? null,
              lastClarityScore: (session.session_state as { lastClarityScore?: number } | null)?.lastClarityScore,
            }}
            onClarityUpdate={handleClarityUpdate}
            onDepthUpdate={handleDepthUpdate}
            onInsightGenerated={handleInsightGenerated}
            onConceptsUpdate={handleConceptsUpdate}
            onNextStateUpdate={handleNextStateUpdate}
            onGapsUpdate={handleGapsUpdate}
            onMisconceptionUpdate={handleMisconceptionUpdate}
          />
        </div>
      </div>

      {/* Insight card is now a full page — ChatPanel navigates to /insights/[id] after generation */}
      <QuickCapture sessionId={sessionId} />
    </div>
  )
}
