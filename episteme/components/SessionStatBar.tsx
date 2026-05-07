'use client'

import { useEffect, useRef, useState } from 'react'
import type { DepthLevel } from '@/lib/types'

interface SessionStatBarProps {
  domain: string
  turnNumber: number
  maxTurns?: number
  nextState: string | null
  clarityScore: number
  independentStreak?: number
}

const DEPTH_SHORT: Record<string, string> = {
  SURFACE: 'SURF', CONCEPTUAL: 'CONC', ANALYTICAL: 'ANAL', SYNTHESIS: 'SYNT',
}

export function SessionStatBar({ domain, turnNumber, maxTurns = 9, nextState, clarityScore, independentStreak = 0 }: SessionStatBarProps) {
  return (
    <div style={{
      width: '100%',
      display: 'flex',
      alignItems: 'center',
      padding: '0 16px',
      height: '28px',
      background: 'rgba(255,176,0,0.03)',
      borderBottom: '1px solid rgba(255,176,0,0.1)',
      gap: '0',
      overflow: 'hidden',
    }}>
      {[
        { label: 'Domain', value: domain.toUpperCase() },
        { label: 'Turn', value: `${turnNumber}/${maxTurns}` },
        { label: 'State', value: nextState || '—' },
        { label: 'Clarity', value: clarityScore > 0 ? `${clarityScore}%` : '—' },
        { label: 'Streak', value: `${independentStreak}` },
      ].map((item, i) => (
        <div key={item.label} style={{ display: 'flex', alignItems: 'center' }}>
          {i > 0 && (
            <div style={{ width: '1px', height: '14px', background: 'rgba(255,176,0,0.2)', margin: '0 10px' }} />
          )}
          <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
            <span style={{
              fontFamily: 'Rubik, sans-serif',
              fontSize: '8px',
              color: '#8a7560',
              letterSpacing: '0.04em',
            }}>
              {item.label}
            </span>
            <span style={{
              fontFamily: 'Rubik, sans-serif',
              fontSize: '9px',
              color: '#9f8e78',
              letterSpacing: '0.08em',
            }}>
              {item.value}
            </span>
          </div>
        </div>
      ))}
    </div>
  )
}
