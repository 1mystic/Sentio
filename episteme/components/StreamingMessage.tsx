'use client'

// components/StreamingMessage.tsx

import { useEffect, useRef, useState, useCallback } from 'react'
import { motion } from 'framer-motion'
import { Play, Pause, Square } from 'lucide-react'

interface StreamingMessageProps {
  role: 'user' | 'assistant'
  content: string
  isStreaming: boolean
  turnNumber: number
}

// Module-level singleton — only one message plays at a time across all instances
const ttsState = {
  activeId: null as string | null,
  listeners: new Set<(id: string | null) => void>(),
  set(id: string | null) {
    this.activeId = id
    this.listeners.forEach((fn) => fn(id))
  },
}

function stripMarkdown(text: string): string {
  return text
    .replace(/\*\*(.+?)\*\*/g, '$1')
    .replace(/\*(.+?)\*/g, '$1')
    .replace(/`{1,3}([^`]+)`{1,3}/g, '$1')
    .replace(/#{1,6}\s+/g, '')
    .replace(/^>\s+/gm, '')
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
    .replace(/[-_]{3,}/g, '')
    .replace(/\n{2,}/g, '. ')
    .trim()
}

const hasSpeech = typeof window !== 'undefined' && 'speechSynthesis' in window

export function StreamingMessage({ role, content, isStreaming, turnNumber }: StreamingMessageProps) {
  const msgId = useRef(`t${turnNumber}-${role}`).current
  const [playState, setPlayState] = useState<'idle' | 'playing' | 'paused'>('idle')
  const wasStreamingRef = useRef(false)
  // keep a stable ref to latest content so auto-play closure is never stale
  const contentRef = useRef(content)
  useEffect(() => { contentRef.current = content }, [content])

  // Subscribe to global TTS state changes so siblings reset when another plays
  useEffect(() => {
    if (role !== 'assistant') return
    const handler = (id: string | null) => {
      if (id !== msgId) setPlayState('idle')
    }
    ttsState.listeners.add(handler)
    return () => { ttsState.listeners.delete(handler) }
  }, [role, msgId])

  // Cancel and clean up if this component unmounts while speaking
  useEffect(() => {
    return () => {
      if (hasSpeech && ttsState.activeId === msgId) {
        window.speechSynthesis.cancel()
        ttsState.set(null)
      }
    }
  }, [msgId])

  const speak = useCallback((text: string) => {
    if (!hasSpeech) return
    window.speechSynthesis.cancel()

    const utterance = new SpeechSynthesisUtterance(stripMarkdown(text))
    utterance.rate = 1.0
    utterance.pitch = 1.0
    utterance.volume = 1.0

    utterance.onstart = () => {
      setPlayState('playing')
      ttsState.set(msgId)
    }
    utterance.onend = () => {
      setPlayState('idle')
      ttsState.set(null)
    }
    utterance.onerror = () => {
      setPlayState('idle')
      ttsState.set(null)
    }

    window.speechSynthesis.speak(utterance)
  }, [msgId])

  // Auto-play when streaming finishes
  useEffect(() => {
    if (role !== 'assistant') return
    if (wasStreamingRef.current && !isStreaming && contentRef.current) {
      speak(contentRef.current)
    }
    wasStreamingRef.current = isStreaming
    // intentionally only isStreaming as dep — speak is stable, content via ref
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isStreaming])

  const handlePlayPause = useCallback(() => {
    if (!hasSpeech) return
    if (playState === 'idle') {
      speak(contentRef.current)
    } else if (playState === 'playing') {
      window.speechSynthesis.pause()
      setPlayState('paused')
    } else {
      window.speechSynthesis.resume()
      setPlayState('playing')
    }
  }, [playState, speak])

  const handleStop = useCallback(() => {
    if (!hasSpeech) return
    window.speechSynthesis.cancel()
    setPlayState('idle')
    ttsState.set(null)
  }, [])

  if (role === 'user') {
    return (
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.25 }}
        className="flex justify-end"
      >
        <div
          className="max-w-[80%] px-5 py-3"
          style={{
            fontSize: '15px',
            background: 'rgba(255,176,0,0.06)',
            border: '1px solid rgba(255,176,0,0.14)',
            color: 'var(--text)',
            lineHeight: 1.65,
            borderRadius: '20px 20px 4px 20px',
            fontFamily: 'Plus Jakarta Sans, sans-serif',
          }}
        >
          {content}
        </div>
      </motion.div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className="flex gap-3"
    >
      {/* AI avatar */}
      <div
        style={{
          width: '32px', height: '32px', borderRadius: '50%',
          background: 'rgba(255,176,0,0.10)',
          border: '1px solid rgba(255,176,0,0.22)',
          color: 'var(--amber)',
          fontSize: '13px',
          fontWeight: 700,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: 0,
          marginTop: '4px',
          fontFamily: 'Plus Jakarta Sans, sans-serif',
        }}
      >
        E
      </div>

      <div className="flex flex-col flex-1 min-w-0">
        <div
          className="relative"
          style={{
            background: 'rgba(255,255,255,0.03)',
            backdropFilter: 'blur(12px)',
            WebkitBackdropFilter: 'blur(12px)',
            border: '1px solid rgba(255,255,255,0.07)',
            borderRadius: '4px 20px 20px 20px',
            padding: '14px 18px',
          }}
        >
          <span
            style={{ fontSize: '10px', color: 'var(--text-dim)', fontFamily: 'Plus Jakarta Sans, sans-serif', position: 'absolute', top: '-18px', left: '0' }}
          >
            Turn {turnNumber}
          </span>
          <p
            style={{ fontSize: '15px', color: 'var(--text)', lineHeight: 1.8, fontFamily: 'Plus Jakarta Sans, sans-serif', margin: 0 }}
          >
            {content}
            {isStreaming && <span className="streaming-cursor" />}
          </p>
        </div>

        {/* TTS controls */}
        {!isStreaming && hasSpeech && (
          <div className="flex items-center gap-2 mt-2 ml-1">
            <button
              onClick={handlePlayPause}
              title={playState === 'playing' ? 'Pause narration' : playState === 'paused' ? 'Resume narration' : 'Play narration'}
              className="flex items-center justify-center transition-all duration-150"
              style={{
                width: '22px',
                height: '22px',
                borderRadius: '50%',
                color: playState !== 'idle' ? 'var(--amber)' : 'var(--text-dim)',
                border: `1px solid ${playState !== 'idle' ? 'rgba(255,176,0,0.35)' : 'var(--border)'}`,
                background: playState !== 'idle' ? 'rgba(255,176,0,0.06)' : 'transparent',
              }}
              onMouseEnter={(e) => { e.currentTarget.style.color = 'var(--amber)'; e.currentTarget.style.borderColor = 'rgba(255,176,0,0.35)' }}
              onMouseLeave={(e) => {
                if (playState === 'idle') {
                  e.currentTarget.style.color = 'var(--text-dim)'
                  e.currentTarget.style.borderColor = 'var(--border)'
                }
              }}
            >
              {playState === 'playing' ? <Pause size={10} strokeWidth={2} /> : <Play size={10} strokeWidth={2} />}
            </button>

            {playState !== 'idle' && (
              <button
                onClick={handleStop}
                title="Stop narration"
                className="flex items-center justify-center transition-all duration-150"
                style={{
                  width: '22px',
                  height: '22px',
                  borderRadius: '50%',
                  color: 'var(--text-dim)',
                  border: '1px solid var(--border)',
                  background: 'transparent',
                }}
                onMouseEnter={(e) => { e.currentTarget.style.color = '#f87171'; e.currentTarget.style.borderColor = 'rgba(248,113,113,0.3)' }}
                onMouseLeave={(e) => { e.currentTarget.style.color = 'var(--text-dim)'; e.currentTarget.style.borderColor = 'var(--border)' }}
              >
                <Square size={9} strokeWidth={2} />
              </button>
            )}
          </div>
        )}
      </div>
    </motion.div>
  )
}
