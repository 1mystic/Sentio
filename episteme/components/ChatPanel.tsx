'use client'

// components/ChatPanel.tsx

import { useEffect, useRef, useState, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import { useChat, type InitialChatState } from '@/hooks/useChat'
import { StreamingMessage } from '@/components/StreamingMessage'
import { CognitiveLiveView } from '@/components/CognitiveLiveView'
import { AlgorithmStatePanel } from '@/components/AlgorithmStatePanel'
import { Button } from '@/components/ui/button'
import { ArrowRight, Sparkles } from 'lucide-react'
import type { Domain, DepthLevel, InsightCard } from '@/lib/types'

interface ChatPanelProps {
  sessionId: string
  domain: Domain
  initial?: InitialChatState
  onClarityUpdate: (score: number) => void
  onDepthUpdate: (depth: DepthLevel) => void
  onInsightGenerated: (card: InsightCard) => void
  onConceptsUpdate: (concepts: string[]) => void
  onNextStateUpdate: (state: string) => void
  onGapsUpdate?: (gaps: string[]) => void
  onMisconceptionUpdate?: (m: string | null) => void
}


export function ChatPanel({
  sessionId,
  domain,
  initial,
  onClarityUpdate,
  onDepthUpdate,
  onInsightGenerated,
  onConceptsUpdate,
  onNextStateUpdate,
  onGapsUpdate,
  onMisconceptionUpdate,
}: ChatPanelProps) {
  const router = useRouter()
  const {
    messages,
    isStreaming,
    clarityScore,
    depthLevel,
    nextState,
    conceptsCovered,
    gaps,
    misconception,
    insightCard,
    insightId,
    sendMessage,
    generateInsight,
    canGenerateInsight,
    error,
  } = useChat(sessionId, domain, initial)

  const [input, setInput] = useState('')
  const [insightLoading, setInsightLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const isFirstRender = useRef(true)

  useEffect(() => { onClarityUpdate(clarityScore) }, [clarityScore, onClarityUpdate])
  useEffect(() => { if (depthLevel) onDepthUpdate(depthLevel) }, [depthLevel, onDepthUpdate])
  useEffect(() => { if (nextState) onNextStateUpdate(nextState) }, [nextState, onNextStateUpdate])
  useEffect(() => { onConceptsUpdate(conceptsCovered) }, [conceptsCovered, onConceptsUpdate])
  useEffect(() => { onGapsUpdate?.(gaps) }, [gaps, onGapsUpdate])
  useEffect(() => { onMisconceptionUpdate?.(misconception) }, [misconception, onMisconceptionUpdate])
  useEffect(() => { if (insightCard) onInsightGenerated(insightCard) }, [insightCard, onInsightGenerated])

  useEffect(() => {
    // Jump instantly to bottom on initial load (historical messages); smooth for new messages
    const behavior = isFirstRender.current ? 'instant' : 'smooth'
    isFirstRender.current = false
    messagesEndRef.current?.scrollIntoView({ behavior })
  }, [messages])

  const handleSend = useCallback(async () => {
    const trimmed = input.trim()
    if (!trimmed || isStreaming) return
    setInput('')
    if (textareaRef.current) textareaRef.current.style.height = 'auto'
    await sendMessage(trimmed)
  }, [input, isStreaming, sendMessage])

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault()
        handleSend()
      }
    },
    [handleSend]
  )

  const handleTextareaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value)
    e.target.style.height = 'auto'
    e.target.style.height = `${Math.min(e.target.scrollHeight, 140)}px`
  }

  const handleGenerateInsight = async () => {
    setInsightLoading(true)
    await generateInsight()
    setInsightLoading(false)
    // insightId is set in useChat after generation — navigate to the full insight page
  }

  // Navigate to insight page once insightId is known
  useEffect(() => {
    if (insightId) router.push(`/insights/${insightId}`)
  }, [insightId, router])

  const userTurns = messages.filter((m) => m.role === 'user').length

  return (
    <div className="flex flex-col h-full" style={{ background: 'var(--bg)' }}>
      {/* Chat header — turn counter + streaming state only (domain shown in top bar) */}
      <div
        className="flex items-center justify-end px-5 flex-shrink-0"
        style={{ height: '40px', borderBottom: '1px solid var(--border)' }}
      >
        <div className="flex items-center gap-3">
          <AnimatePresence mode="wait">
            {isStreaming && (
              <motion.div
                key="streaming"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex items-center gap-2"
              >
                <motion.span
                  animate={{ opacity: [1, 0.3, 1] }}
                  transition={{ duration: 1.2, repeat: Infinity }}
                  style={{ width: '6px', height: '6px', borderRadius: '50%', background: 'var(--amber)', display: 'inline-block' }}
                />
                <span style={{ fontSize: '12px', color: 'var(--text-dim)', fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
                  thinking...
                </span>
              </motion.div>
            )}
          </AnimatePresence>
          {userTurns > 0 && (
            <span className="tabular-nums" style={{ fontSize: '11px', color: 'var(--text-dim)', fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
              Turn {userTurns}
            </span>
          )}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-5 py-8 flex flex-col gap-8">
        {messages.length === 0 && (
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="flex flex-col items-center justify-center h-full text-center gap-5"
          >
            <div
              style={{
                width: '48px', height: '48px', borderRadius: '50%',
                background: 'rgba(255,176,0,0.10)',
                border: '1px solid rgba(255,176,0,0.25)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                boxShadow: '0 4px 20px rgba(255,176,0,0.15)',
              }}
            >
              <span style={{ fontSize: '22px', color: 'var(--amber)' }}>E</span>
            </div>
            <p
              style={{ fontSize: '20px', color: 'var(--text)', fontWeight: 700, maxWidth: '400px', lineHeight: 1.4, fontFamily: 'Plus Jakarta Sans, sans-serif' }}
            >
              Ask anything. I won&apos;t answer it — not directly.
            </p>
            <p style={{ fontSize: '14px', color: 'var(--text-dim)', fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
              I&apos;ll ask you what you already think. We&apos;ll build from there.
            </p>
          </motion.div>
        )}

        {messages.map((msg) => (
          <StreamingMessage
            key={msg.id}
            role={msg.role}
            content={msg.content}
            isStreaming={msg.isStreaming}
            turnNumber={msg.turnNumber}
          />
        ))}

        {error && (
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="font-grotesk text-center"
            style={{ fontSize: '12px', color: '#f87171', letterSpacing: '0.04em' }}
          >
            {error}
          </motion.p>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Insight generation CTA */}
      <AnimatePresence>
        {canGenerateInsight && !insightCard && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 8 }}
            className="px-5 py-2 flex-shrink-0"
          >
            <button
              onClick={handleGenerateInsight}
              disabled={insightLoading || isStreaming}
              className="w-full py-3 text-center transition-all duration-200 disabled:opacity-40 disabled:cursor-not-allowed"
              style={{
                fontSize: '13px',
                fontWeight: 600,
                color: 'var(--amber)',
                background: 'rgba(255,176,0,0.06)',
                border: '1px solid rgba(255,176,0,0.2)',
                borderRadius: '12px',
                fontFamily: 'Plus Jakarta Sans, sans-serif',
              }}
              onMouseEnter={(e) => { (e.currentTarget).style.background = 'rgba(255,176,0,0.10)' }}
              onMouseLeave={(e) => { (e.currentTarget).style.background = 'rgba(255,176,0,0.06)' }}
            >
              <span className="flex items-center justify-center gap-2">
                <Sparkles size={13} />
                {insightLoading ? 'Analyzing session...' : 'Generate insight card'}
              </span>
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Session complete banner */}
      {insightCard && (
        <div
          className="px-5 py-4 flex-shrink-0 flex items-center justify-between"
          style={{ borderTop: '1px solid var(--border)', background: 'rgba(255,176,0,0.03)' }}
        >
          <p style={{ fontSize: '13px', color: 'var(--text-muted)', fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
            Session complete.
          </p>
          <Button variant="outline" size="sm" onClick={() => (window.location.href = '/')} className="flex items-center gap-1.5">
            Start new session <ArrowRight size={12} />
          </Button>
        </div>
      )}

      {/* Input area */}
      {!insightCard && (
        <div
          className="flex-shrink-0"
          style={{ borderTop: '1px solid var(--border)', background: 'var(--bg)' }}
        >
          {/* Live cognitive signals */}
          <CognitiveLiveView
            draftResponse={input}
            domain={domain}
            turnNumber={userTurns + 1}
          />

          <div className="px-4 py-4">
            <div
              className="flex items-center gap-3"
              style={{
                background: 'rgba(255,255,255,0.04)',
                backdropFilter: 'blur(16px)',
                WebkitBackdropFilter: 'blur(16px)',
                border: '1.5px solid rgba(255,255,255,0.10)',
                borderRadius: '9999px',
                padding: '10px 10px 10px 20px',
                transition: 'border-color 0.2s, box-shadow 0.2s',
              }}
              onFocusCapture={(e) => {
                const el = e.currentTarget as HTMLElement
                el.style.borderColor = 'rgba(255,176,0,0.45)'
                el.style.boxShadow = '0 0 0 3px rgba(255,176,0,0.08)'
              }}
              onBlurCapture={(e) => {
                const el = e.currentTarget as HTMLElement
                el.style.borderColor = 'rgba(255,255,255,0.10)'
                el.style.boxShadow = 'none'
              }}
            >
              <textarea
                ref={textareaRef}
                value={input}
                onChange={handleTextareaChange}
                onKeyDown={handleKeyDown}
                disabled={isStreaming}
                placeholder="What do you want to understand today?"
                rows={1}
                className="flex-1 resize-none bg-transparent outline-none disabled:opacity-50"
                style={{
                  fontSize: '15px',
                  color: 'var(--text)',
                  lineHeight: 1.6,
                  maxHeight: '140px',
                  overflowY: 'auto',
                  caretColor: 'var(--amber)',
                  fontFamily: 'Plus Jakarta Sans, sans-serif',
                }}
              />
              <button
                onClick={handleSend}
                disabled={isStreaming || !input.trim()}
                className="flex-shrink-0 flex items-center justify-center transition-all duration-200 active:scale-95 disabled:opacity-30 disabled:cursor-not-allowed"
                style={{
                  color: '#09090e',
                  background: input.trim() ? 'var(--amber)' : 'rgba(255,176,0,0.25)',
                  width: '40px',
                  height: '40px',
                  borderRadius: '9999px',
                  boxShadow: input.trim() ? '0 4px 12px rgba(255,176,0,0.3)' : 'none',
                  transition: 'box-shadow 0.2s, background 0.2s',
                  flexShrink: 0,
                }}
              >
                <ArrowRight size={16} strokeWidth={2.5} />
              </button>
            </div>
          </div>
        </div>
      )}

      <AlgorithmStatePanel
        depthLevel={depthLevel}
        nextState={nextState}
        clarityScore={clarityScore}
        misconception={misconception ?? null}
      />
    </div>
  )
}
