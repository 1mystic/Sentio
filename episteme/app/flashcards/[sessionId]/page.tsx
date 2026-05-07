'use client'

import { useState, useEffect, useCallback } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'

interface FlashCard {
  id: string
  concept: string
  insight: string
  clarity: number
  type: 'insight' | 'gap'
}

type Rating = 'got_it' | 'needs_review' | 'no_idea'

const font = 'Plus Jakarta Sans, sans-serif'

export default function FlashcardsPage() {
  const params = useParams()
  const sessionId = params.sessionId as string
  const [cards, setCards] = useState<FlashCard[]>([])
  const [current, setCurrent] = useState(0)
  const [flipped, setFlipped] = useState(false)
  const [ratings, setRatings] = useState<Record<string, Rating>>({})
  const [loading, setLoading] = useState(true)
  const [done, setDone] = useState(false)

  useEffect(() => {
    async function load() {
      const [insightRes] = await Promise.all([
        fetch(`/api/insights?sessionId=${sessionId}`),
        fetch(`/api/session?id=${sessionId}`),
      ])
      const insightData = await insightRes.json() as { insights?: Array<{ id: string; concept: string; insight: string; clarity_score: number; gaps: string[] }> }

      const result: FlashCard[] = []

      if (insightData.insights) {
        for (const insight of insightData.insights) {
          result.push({ id: insight.id, concept: insight.concept, insight: insight.insight, clarity: insight.clarity_score, type: 'insight' })
          for (const gap of (insight.gaps || [])) {
            result.push({ id: `gap-${insight.id}-${gap}`, concept: gap, insight: 'This is an identified gap — a concept you encountered but haven\'t fully internalized yet.', clarity: 0, type: 'gap' })
          }
        }
      }

      setCards(result)
      setLoading(false)
    }
    load().catch(() => setLoading(false))
  }, [sessionId])

  const handleRating = useCallback(async (rating: Rating) => {
    const card = cards[current]
    if (!card) return

    setRatings(prev => ({ ...prev, [card.id]: rating }))

    fetch('/api/mastery', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sessionId, concept: card.concept, rating }),
    }).catch(console.error)

    if (current < cards.length - 1) {
      setFlipped(false)
      setTimeout(() => setCurrent(c => c + 1), 150)
    } else {
      setDone(true)
    }
  }, [cards, current, sessionId])

  useEffect(() => {
    function handleKey(e: KeyboardEvent) {
      if (e.key === ' ' || e.key === 'Enter') { e.preventDefault(); setFlipped(f => !f) }
      if (e.key === 'ArrowLeft' && current > 0) { setFlipped(false); setTimeout(() => setCurrent(c => c - 1), 150) }
      if (e.key === 'ArrowRight' && current < cards.length - 1) { setFlipped(false); setTimeout(() => setCurrent(c => c + 1), 150) }
      if (e.key === '1') handleRating('got_it')
      if (e.key === '2') handleRating('needs_review')
      if (e.key === '3') handleRating('no_idea')
    }
    window.addEventListener('keydown', handleKey)
    return () => window.removeEventListener('keydown', handleKey)
  }, [current, cards.length, handleRating])

  if (loading) return (
    <div style={{ background: '#09090e', height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <span style={{ fontFamily: font, fontSize: '13px', color: '#FFB000' }}>Loading flashcards...</span>
    </div>
  )

  if (cards.length === 0) return (
    <div style={{ background: '#09090e', height: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '20px' }}>
      <span style={{ fontFamily: font, fontSize: '14px', color: 'rgba(255,255,255,0.4)' }}>No flashcards — complete a session first</span>
      <Link href={`/session/${sessionId}`} style={{ fontFamily: font, fontSize: '13px', fontWeight: 600, color: '#FFB000', textDecoration: 'none', border: '1px solid rgba(255,176,0,0.3)', borderRadius: '9999px', padding: '8px 20px' }}>← Back to Session</Link>
    </div>
  )

  const card = cards[current]

  if (done) return (
    <div style={{ background: '#09090e', height: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '24px' }}>
      <div style={{ fontFamily: font, fontSize: '20px', fontWeight: 700, color: '#FFB000' }}>Session Complete</div>
      <div style={{ display: 'flex', gap: '20px', fontFamily: font, fontSize: '13px' }}>
        <span style={{ color: '#4ade80' }}>Got It: {Object.values(ratings).filter(r => r === 'got_it').length}</span>
        <span style={{ color: '#FFB000' }}>Review: {Object.values(ratings).filter(r => r === 'needs_review').length}</span>
        <span style={{ color: '#f87171' }}>No Idea: {Object.values(ratings).filter(r => r === 'no_idea').length}</span>
      </div>
      <div style={{ display: 'flex', gap: '12px' }}>
        <Link href={`/knowledge-graph/${sessionId}`} style={{ fontFamily: font, fontSize: '13px', fontWeight: 600, color: '#09090e', background: '#FFB000', textDecoration: 'none', borderRadius: '9999px', padding: '10px 20px' }}>View Graph →</Link>
        <Link href={`/session/${sessionId}`} style={{ fontFamily: font, fontSize: '13px', fontWeight: 600, color: 'rgba(255,255,255,0.5)', textDecoration: 'none', border: '1px solid rgba(255,255,255,0.12)', borderRadius: '9999px', padding: '10px 20px' }}>← Session</Link>
      </div>
    </div>
  )

  const isGap = card?.type === 'gap'

  return (
    <div style={{ background: '#09090e', height: '100vh', display: 'flex', flexDirection: 'column', overflow: 'hidden', fontFamily: font }}>
      {/* Header */}
      <div style={{
        padding: '12px 24px',
        borderBottom: '1px solid rgba(255,255,255,0.07)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        background: 'rgba(9,9,14,0.92)',
        backdropFilter: 'blur(12px)',
      }}>
        <Link href={`/session/${sessionId}`} style={{ fontFamily: font, fontSize: '13px', fontWeight: 600, color: '#FFB000', textDecoration: 'none' }}>← Back</Link>
        <span style={{ fontFamily: font, fontSize: '12px', color: 'rgba(255,255,255,0.3)' }}>
          Flashcards · {current + 1}/{cards.length}
        </span>
        <span style={{
          fontFamily: font,
          fontSize: '11px',
          fontWeight: 600,
          color: isGap ? '#f87171' : '#FFB000',
          background: isGap ? 'rgba(248,113,113,0.08)' : 'rgba(255,176,0,0.08)',
          border: `1px solid ${isGap ? 'rgba(248,113,113,0.25)' : 'rgba(255,176,0,0.25)'}`,
          borderRadius: '9999px',
          padding: '3px 10px',
        }}>
          {isGap ? 'Gap' : 'Insight'}
        </span>
      </div>

      {/* Card area */}
      <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '32px 24px' }}>
        <div
          onClick={() => setFlipped(f => !f)}
          style={{
            width: '100%',
            maxWidth: '580px',
            minHeight: '280px',
            border: `1.5px solid ${isGap ? 'rgba(248,113,113,0.25)' : 'rgba(255,176,0,0.30)'}`,
            borderRadius: '20px',
            padding: '40px 44px',
            cursor: 'pointer',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'rgba(255,255,255,0.025)',
            backdropFilter: 'blur(16px)',
            WebkitBackdropFilter: 'blur(16px)',
            transition: 'border-color 0.2s, box-shadow 0.2s',
            position: 'relative',
            boxShadow: isGap ? '0 8px 32px rgba(248,113,113,0.06)' : '0 8px 32px rgba(255,176,0,0.06)',
          }}
        >
          {!flipped ? (
            <>
              <p style={{ fontFamily: font, fontSize: '22px', fontWeight: 700, color: '#ede8f5', textAlign: 'center', lineHeight: 1.45 }}>
                {card?.concept}
              </p>
              <span style={{ position: 'absolute', bottom: '16px', fontFamily: font, fontSize: '11px', color: 'rgba(255,255,255,0.25)' }}>
                tap to flip
              </span>
            </>
          ) : (
            <>
              <p style={{ fontFamily: font, fontSize: '14px', color: 'rgba(255,255,255,0.65)', textAlign: 'center', lineHeight: 1.75, marginBottom: card?.clarity ? '20px' : '0' }}>
                {card?.insight}
              </p>
              {card?.clarity > 0 && (
                <div style={{
                  fontFamily: font,
                  fontSize: '11px',
                  fontWeight: 600,
                  color: '#FFB000',
                  background: 'rgba(255,176,0,0.08)',
                  border: '1px solid rgba(255,176,0,0.2)',
                  borderRadius: '9999px',
                  padding: '4px 12px',
                }}>
                  Clarity: {card.clarity}/100
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* Rating buttons (only when flipped) */}
      {flipped && (
        <div style={{ padding: '0 24px 36px', display: 'flex', gap: '12px', justifyContent: 'center' }}>
          {[
            { rating: 'got_it' as Rating, label: 'Got It', color: '#4ade80', bg: 'rgba(74,222,128,0.08)', border: 'rgba(74,222,128,0.25)' },
            { rating: 'needs_review' as Rating, label: 'Needs Review', color: '#FFB000', bg: 'rgba(255,176,0,0.08)', border: 'rgba(255,176,0,0.25)' },
            { rating: 'no_idea' as Rating, label: 'No Idea', color: '#f87171', bg: 'rgba(248,113,113,0.08)', border: 'rgba(248,113,113,0.25)' },
          ].map(({ rating, label, color, bg, border }) => (
            <button
              key={rating}
              onClick={() => handleRating(rating)}
              style={{
                fontFamily: font,
                fontSize: '13px',
                fontWeight: 600,
                color,
                background: bg,
                border: `1px solid ${border}`,
                borderRadius: '9999px',
                padding: '10px 22px',
                cursor: 'pointer',
                transition: 'opacity 0.15s',
              }}
            >
              {label}
            </button>
          ))}
        </div>
      )}

      {/* Progress bar */}
      <div style={{ height: '2px', background: 'rgba(255,255,255,0.04)', flexShrink: 0 }}>
        <div style={{ height: '100%', width: `${((current + 1) / cards.length) * 100}%`, background: '#FFB000', transition: 'width 0.3s', borderRadius: '1px' }} />
      </div>
    </div>
  )
}
