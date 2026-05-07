'use client'

import { useState } from 'react'

interface QuickCaptureProps {
  sessionId: string
  onSaved?: (question: string) => void
}

export function QuickCapture({ sessionId, onSaved }: QuickCaptureProps) {
  const [open, setOpen] = useState(false)
  const [text, setText] = useState('')
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)

  async function handleSave() {
    if (!text.trim()) return
    setSaving(true)

    await fetch('/api/follow-up', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sessionId, question: text.trim() }),
    })

    setSaving(false)
    setSaved(true)
    onSaved?.(text.trim())
    setText('')
    setTimeout(() => { setSaved(false); setOpen(false) }, 1200)
  }

  return (
    <>
      {/* FAB button */}
      <button
        onClick={() => setOpen(p => !p)}
        style={{
          position: 'fixed',
          bottom: '90px',
          left: '24px',
          width: '44px',
          height: '44px',
          background: 'var(--primary)',
          border: 'none',
          cursor: 'pointer',
          fontFamily: 'Plus Jakarta Sans, sans-serif',
          fontSize: '18px',
          color: '#09090e',
          fontWeight: 700,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 40,
          boxShadow: '0 4px 20px rgba(255,176,0,0.30)',
          borderRadius: '9999px',
        }}
        title="Capture a follow-up question"
      >
        +?
      </button>

      {/* Modal */}
      {open && (
        <div style={{
          position: 'fixed',
          bottom: '146px',
          left: '24px',
          width: '300px',
          background: 'rgba(15,15,24,0.96)',
          backdropFilter: 'blur(20px)',
          WebkitBackdropFilter: 'blur(20px)',
          border: '1px solid rgba(255,176,0,0.20)',
          borderRadius: '16px',
          padding: '16px',
          zIndex: 41,
          boxShadow: '0 8px 32px rgba(0,0,0,0.5)',
        }}>
          <div style={{
            fontFamily: 'Plus Jakarta Sans, sans-serif',
            fontSize: '12px',
            fontWeight: 600,
            color: 'var(--text-muted)',
            marginBottom: '10px',
          }}>
            Capture thought
          </div>
          <textarea
            value={text}
            onChange={e => setText(e.target.value)}
            placeholder="What's your follow-up question?"
            autoFocus
            rows={3}
            style={{
              width: '100%',
              background: 'var(--surface-container)',
              border: '1.5px solid var(--outline-variant)',
              borderRadius: '10px',
              color: 'var(--text)',
              fontFamily: 'Plus Jakarta Sans, sans-serif',
              fontSize: '13px',
              padding: '10px 12px',
              outline: 'none',
              resize: 'none',
              boxSizing: 'border-box',
              lineHeight: 1.5,
              transition: 'border-color 0.2s',
            }}
            onFocus={(e) => { e.target.style.borderColor = 'rgba(255,176,0,0.45)' }}
            onBlur={(e) => { e.target.style.borderColor = 'var(--outline-variant)' }}
            onKeyDown={e => { if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) handleSave() }}
          />
          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '10px', alignItems: 'center' }}>
            <span style={{ fontFamily: 'Plus Jakarta Sans, sans-serif', fontSize: '11px', color: 'var(--text-dim)' }}>⌘↵ to save</span>
            <button
              onClick={handleSave}
              disabled={!text.trim() || saving}
              style={{
                fontFamily: 'Plus Jakarta Sans, sans-serif',
                fontSize: '12px',
                fontWeight: 600,
                color: saved ? 'white' : 'white',
                background: saved ? '#4ade80' : text.trim() ? 'var(--primary)' : 'var(--outline-variant)',
                border: 'none',
                borderRadius: '9999px',
                padding: '6px 16px',
                cursor: text.trim() && !saving ? 'pointer' : 'not-allowed',
                transition: 'background 0.2s',
              }}
            >
              {saved ? 'Saved ✓' : saving ? '...' : 'Save'}
            </button>
          </div>
        </div>
      )}
    </>
  )
}
