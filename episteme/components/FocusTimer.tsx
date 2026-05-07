'use client'

import { useState, useEffect, useRef } from 'react'

const POMODORO_SECONDS = 25 * 60

interface FocusTimerProps {
  sessionId: string
}

export function FocusTimer({ sessionId }: FocusTimerProps) {
  const [elapsed, setElapsed] = useState(0)
  const [running, setRunning] = useState(false)
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)

  useEffect(() => {
    if (running) {
      intervalRef.current = setInterval(() => setElapsed(e => e + 1), 1000)
    } else {
      if (intervalRef.current) clearInterval(intervalRef.current)
    }
    return () => { if (intervalRef.current) clearInterval(intervalRef.current) }
  }, [running])

  // Auto-start on mount
  useEffect(() => { setRunning(true) }, [])

  const minutes = Math.floor(elapsed / 60)
  const seconds = elapsed % 60
  const pomodoroDone = elapsed >= POMODORO_SECONDS
  const pomodoroCount = Math.floor(elapsed / POMODORO_SECONDS)

  const display = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`

  return (
    <div
      onClick={() => setRunning(p => !p)}
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '5px',
        cursor: 'pointer',
        padding: '4px 10px',
        border: '1px solid',
        borderColor: pomodoroDone ? 'rgba(74,222,128,0.4)' : 'var(--border)',
        borderRadius: '9999px',
        background: running ? 'var(--primary-soft)' : 'transparent',
      }}
      title={running ? 'Click to pause' : 'Click to resume'}
    >
      <span style={{
        fontFamily: 'Plus Jakarta Sans, sans-serif',
        fontSize: '11px',
        fontWeight: 500,
        color: 'var(--text-dim)',
      }}>
        Focus
      </span>
      <span style={{
        fontFamily: 'Plus Jakarta Sans, sans-serif',
        fontSize: '11px',
        fontWeight: 600,
        color: pomodoroDone ? '#4ade80' : 'var(--primary)',
        fontVariantNumeric: 'tabular-nums',
      } as React.CSSProperties}>
        {display}
      </span>
      {pomodoroCount > 0 && (
        <span style={{ fontSize: '8px', color: '#4ade80' }}>
          {'◆'.repeat(Math.min(pomodoroCount, 4))}
        </span>
      )}
    </div>
  )
}
