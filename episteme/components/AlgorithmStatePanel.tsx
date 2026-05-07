'use client'

import { useState } from 'react'
import type { DepthLevel } from '@/lib/types'

interface AlgorithmStatePanelProps {
  qualityScore?: number
  depthLevel: DepthLevel | null
  nextState: string | null
  clarityScore: number
  semanticAccuracy?: number
  misconception: string | null
}

export function AlgorithmStatePanel({
  qualityScore = 0,
  depthLevel,
  nextState,
  clarityScore,
  semanticAccuracy = 0,
  misconception,
}: AlgorithmStatePanelProps) {
  const [open, setOpen] = useState(false)

  return (
    <div style={{ borderTop: '1px solid rgba(255,255,255,0.06)' }}>
      <button
        onClick={() => setOpen(p => !p)}
        style={{
          width: '100%',
          padding: '6px 16px',
          background: 'transparent',
          border: 'none',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          textAlign: 'left',
        }}
      >
        <span style={{ fontFamily: 'Rubik, sans-serif', fontSize: '8px', color: '#8a7560', letterSpacing: '0.03em' }}>
          Why is Episteme doing this?
        </span>
        <span style={{ fontFamily: 'Rubik, sans-serif', fontSize: '8px', color: 'rgba(255,176,0,0.4)', marginLeft: 'auto' }}>
          {open ? '▲' : '▼'}
        </span>
      </button>

      {open && (
        <div style={{
          padding: '8px 16px 12px',
          display: 'grid',
          gridTemplateColumns: '1fr 1fr 1fr',
          gap: '8px',
          background: 'rgba(255,176,0,0.02)',
          borderTop: '1px solid rgba(255,176,0,0.08)',
          borderRadius: '6px',
        }}>
          {[
            { label: 'Quality', value: qualityScore.toFixed(2) },
            { label: 'Depth', value: depthLevel || '—' },
            { label: 'State', value: nextState || '—' },
            { label: 'BKT P(L)', value: (clarityScore / 100).toFixed(2) },
            { label: 'Accuracy', value: semanticAccuracy.toFixed(2) },
            { label: 'Misconception', value: misconception ? 'Detected' : 'None' },
          ].map(item => (
            <div key={item.label}>
              <div style={{ fontFamily: 'Rubik, sans-serif', fontSize: '7px', color: '#8a7560', letterSpacing: '0.03em', marginBottom: '2px' }}>
                {item.label}
              </div>
              <div style={{
                fontFamily: 'Rubik, sans-serif',
                fontSize: '10px',
                color: item.label === 'Misconception' && misconception ? '#ff6b6b' : '#FFB000',
                letterSpacing: '0.06em',
              }}>
                {item.value}
              </div>
            </div>
          ))}

          {misconception && (
            <div style={{ gridColumn: '1 / -1', marginTop: '4px', padding: '6px 8px', background: 'rgba(255,80,80,0.06)', borderLeft: '2px solid rgba(255,80,80,0.3)' }}>
              <span style={{ fontFamily: 'Rubik, sans-serif', fontSize: '8px', color: '#ff6b6b' }}>{misconception}</span>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
