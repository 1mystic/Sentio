'use client'

import { useEffect, useState, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { extractDepthSignals, REASONING_CONNECTIVES, CONFUSION_MARKERS } from '@/lib/algorithms'
import type { Domain } from '@/lib/types'

interface Signals {
  reasoning: number
  depth: number
  clarity: number
}

function Bar({
  label,
  value,
  color,
  description,
}: {
  label: string
  value: number
  color: string
  description: string
}) {
  const pct = Math.round(value * 100)
  return (
    <div className="flex items-center gap-3">
      <div className="flex-shrink-0 w-20 text-right">
        <span
          className="font-grotesk font-medium"
          style={{ fontSize: '10px', color: 'var(--text-dim, #9f8e78)', letterSpacing: '0.04em' }}
          title={description}
        >
          {label}
        </span>
      </div>

      <div
        className="flex-1 relative overflow-hidden"
        style={{ height: '3px', background: 'var(--border, rgba(0,0,0,0.08))', borderRadius: '2px' }}
      >
        <motion.div
          style={{ height: '100%', background: color, originX: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.18, ease: 'easeOut' }}
        />
      </div>

      <span
        className="font-grotesk flex-shrink-0 w-9 text-right tabular-nums"
        style={{ fontSize: '10px', color, opacity: pct > 0 ? 0.85 : 0.3 }}
      >
        {pct}%
      </span>
    </div>
  )
}

export function CognitiveLiveView({
  draftResponse,
  domain,
  turnNumber,
}: {
  draftResponse: string
  domain: Domain
  turnNumber: number
}) {
  const [signals, setSignals] = useState<Signals>({ reasoning: 0, depth: 0, clarity: 0 })
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  useEffect(() => {
    if (draftResponse.length < 8) {
      setSignals({ reasoning: 0, depth: 0, clarity: 0 })
      return
    }

    if (debounceRef.current) clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(() => {
      const text = draftResponse.toLowerCase()
      const words = text.split(/\s+/).filter(Boolean)

      // Analytical question patterns (in addition to connectives)
      const QUESTION_ANALYTICAL = [
        'how does', 'how do', 'how is', 'how are', 'how can', 'how did',
        'why does', 'why do', 'why is', 'why are', 'why did', 'why was',
        'what causes', 'what makes', 'what determines', 'what happens',
        'explain', 'difference between', 'relationship between',
        'compare', 'contrast', 'in what way', 'what would happen',
        'what is the effect', 'how would', 'what if',
      ]
      const connectiveHits = REASONING_CONNECTIVES.filter((c) => text.includes(c)).length
      const analyticalHits = QUESTION_ANALYTICAL.filter((p) => text.includes(p)).length
      const totalHits = connectiveHits + analyticalHits * 0.6
      const reasoning = Math.min(totalHits / Math.max(words.length / 8, 1.2), 1)

      // Depth: calibrated for user questions (shorter expected length)
      const expectedWords = Math.max(10 + turnNumber * 3, 12)
      const lengthScore = Math.min(words.length / expectedWords, 1)
      const { qualityScore, confusionCount } = extractDepthSignals(draftResponse, domain, turnNumber)
      const depth = Math.min(0.45 * qualityScore + 0.55 * lengthScore, 1)

      const confusionHits = CONFUSION_MARKERS.filter((m) => text.includes(m)).length
      const clarity = Math.max(0, 1 - confusionCount / 3 - confusionHits * 0.25)

      setSignals({ reasoning, depth, clarity })
    }, 120)

    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current)
    }
  }, [draftResponse, domain, turnNumber])

  const visible = draftResponse.length >= 8

  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
          transition={{ duration: 0.2, ease: 'easeOut' }}
          className="overflow-hidden"
          style={{ borderTop: '1px solid var(--border, rgba(0,0,0,0.08))', background: 'rgba(103,75,181,0.03)' }}
        >
          <div className="px-5 py-3 flex flex-col gap-2">
            <p
              className="font-grotesk font-medium mb-1"
              style={{ fontSize: '10px', color: 'var(--text-dim)', letterSpacing: '0.08em' }}
            >
              Cognitive signals
            </p>
            <Bar
              label="Analysis"
              value={signals.reasoning}
              color="var(--primary, #674bb5)"
              description="Analytical depth — how, why, explanatory reasoning in your question"
            />
            <Bar
              label="Depth"
              value={signals.depth}
              color="#4ade80"
              description="Specificity and length — detailed questions score higher"
            />
            <Bar
              label="Clarity"
              value={signals.clarity}
              color="#60a5fa"
              description="Absence of confusion signals — high means your question is clear"
            />
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
