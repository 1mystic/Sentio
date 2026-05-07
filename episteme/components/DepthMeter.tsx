'use client'

import { motion } from 'framer-motion'
import type { DepthLevel } from '@/lib/types'

const DEPTH_LEVELS: DepthLevel[] = ['SURFACE', 'CONCEPTUAL', 'ANALYTICAL', 'SYNTHESIS']
const DEPTH_LABELS: Record<DepthLevel, string> = {
  SURFACE: 'Surface',
  CONCEPTUAL: 'Concept',
  ANALYTICAL: 'Analytic',
  SYNTHESIS: 'Synthesis',
}
const DEPTH_INDEX: Record<DepthLevel, number> = {
  SURFACE: 0, CONCEPTUAL: 1, ANALYTICAL: 2, SYNTHESIS: 3,
}

interface DepthMeterProps {
  depth: DepthLevel | null
  previousDepth: DepthLevel | null
}

export function DepthMeter({ depth, previousDepth }: DepthMeterProps) {
  const currentIdx = depth ? DEPTH_INDEX[depth] : -1
  const upgraded = depth && previousDepth && DEPTH_INDEX[depth] > DEPTH_INDEX[previousDepth]

  return (
    <div>
      <p
        style={{
          fontFamily: 'Plus Jakarta Sans, sans-serif',
          fontSize: '11px',
          fontWeight: 500,
          color: 'var(--text-dim)',
          marginBottom: '10px',
        }}
      >
        Bloom Depth
      </p>
      <div style={{ display: 'flex', gap: '4px', position: 'relative' }}>
        {upgraded && (
          <motion.div
            initial={{ opacity: 0.8, scaleX: 0 }}
            animate={{ opacity: 0, scaleX: 1 }}
            transition={{ duration: 0.5, ease: 'easeOut' }}
            style={{
              position: 'absolute',
              inset: 0,
              background: 'rgba(255,176,0,0.2)',
              transformOrigin: 'left',
              pointerEvents: 'none',
              borderRadius: '8px',
              zIndex: 1,
            }}
          />
        )}
        {DEPTH_LEVELS.map((level, i) => {
          const active = i <= currentIdx
          return (
            <div
              key={level}
              style={{
                flex: 1,
                height: '28px',
                background: active ? 'rgba(255,176,0,0.80)' : 'rgba(255,255,255,0.04)',
                border: `1.5px solid ${active ? 'rgba(255,176,0,0.9)' : 'rgba(255,255,255,0.10)'}`,
                borderRadius: '8px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                position: 'relative',
                transition: 'background 0.3s, border-color 0.3s',
              }}
            >
              <span
                style={{
                  fontFamily: 'Plus Jakarta Sans, sans-serif',
                  fontSize: '9px',
                  fontWeight: active ? 700 : 500,
                  color: active ? '#09090e' : 'var(--text-dim)',
                  userSelect: 'none',
                }}
              >
                {DEPTH_LABELS[level]}
              </span>
            </div>
          )
        })}
      </div>
    </div>
  )
}
