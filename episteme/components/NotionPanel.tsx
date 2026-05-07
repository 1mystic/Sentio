'use client'

import { useState, useEffect } from 'react'

type PanelState = 'NOT_CONNECTED' | 'CONNECTED' | 'SYNCING' | 'ERROR'

interface NotionConnection {
  notion_page_url: string
  last_synced_at: string | null
  sync_count: number
  is_active: boolean
}

interface NotionPanelProps {
  sessionId: string
}

export function NotionPanel({ sessionId }: NotionPanelProps) {
  const [panelState, setPanelState] = useState<PanelState>('NOT_CONNECTED')
  const [connection, setConnection] = useState<NotionConnection | null>(null)
  const [token, setToken] = useState('')
  const [pageId, setPageId] = useState('')
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch(`/api/notion/connect?sessionId=${sessionId}`)
      .then(r => r.json())
      .then((d: { connection: NotionConnection | null }) => {
        if (d.connection?.is_active) {
          setConnection(d.connection)
          setPanelState('CONNECTED')
        }
      })
      .catch(() => {})
  }, [sessionId])

  async function handleConnect() {
    if (!token.trim() || !pageId.trim()) return
    setPanelState('SYNCING')
    setError(null)

    const res = await fetch('/api/notion/connect', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sessionId, notionToken: token.trim(), notionPageId: pageId.trim() }),
    })
    const data = await res.json() as { success?: boolean; error?: string; notionPageUrl?: string }

    if (data.success) {
      setConnection({ notion_page_url: data.notionPageUrl || '', last_synced_at: new Date().toISOString(), sync_count: 1, is_active: true })
      setPanelState('CONNECTED')
    } else {
      setError(data.error || 'Connection failed')
      setPanelState('ERROR')
    }
  }

  async function handleSync() {
    setPanelState('SYNCING')
    setError(null)

    const res = await fetch(`/api/notion/sync/${sessionId}`, { method: 'POST' })
    const data = await res.json() as { success?: boolean; error?: string }

    if (data.success) {
      setConnection(prev => prev ? { ...prev, last_synced_at: new Date().toISOString(), sync_count: prev.sync_count + 1 } : prev)
      setPanelState('CONNECTED')
    } else {
      setError(data.error || 'Sync failed')
      setPanelState('ERROR')
    }
  }

  const labelStyle: React.CSSProperties = {
    fontFamily: 'Rubik, sans-serif',
    fontSize: '11px',
    color: '#FFB000',
    letterSpacing: '0.04em',
    marginBottom: '12px',
    display: 'block',
  }

  const inputStyle: React.CSSProperties = {
    width: '100%',
    background: 'rgba(255,255,255,0.03)',
    border: '1px solid rgba(255,255,255,0.1)',
    color: '#EDE0CC',
    fontFamily: 'Rubik, sans-serif',
    fontSize: '10px',
    padding: '8px 10px',
    outline: 'none',
    boxSizing: 'border-box',
  }

  const borderColor = panelState === 'CONNECTED' ? 'rgba(255,176,0,0.5)' : 'rgba(255,255,255,0.1)'

  return (
    <div style={{ border: `1px solid ${borderColor}`, borderRadius: '8px', padding: '16px', background: 'rgba(255,255,255,0.01)' }}>
      <span style={labelStyle}>Notion {panelState === 'CONNECTED' && '· Connected'}</span>

      {panelState === 'NOT_CONNECTED' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <input
            style={inputStyle}
            placeholder="Notion integration token (secret_...)"
            value={token}
            onChange={e => setToken(e.target.value)}
          />
          <input
            style={inputStyle}
            placeholder="Page ID (from Notion page URL)"
            value={pageId}
            onChange={e => setPageId(e.target.value)}
          />
          <button
            onClick={handleConnect}
            disabled={!token || !pageId}
            style={{
              fontFamily: 'Rubik, sans-serif',
              fontSize: '10px',
              fontWeight: 700,
              letterSpacing: '0.04em',
              color: '#08090A',
              background: token && pageId ? '#FFB000' : 'rgba(255,176,0,0.3)',
              border: 'none',
              borderRadius: '6px',
              padding: '8px 16px',
              cursor: token && pageId ? 'pointer' : 'not-allowed',
              alignSelf: 'flex-start',
            }}
          >
            Connect →
          </button>
        </div>
      )}

      {panelState === 'CONNECTED' && connection && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#4ade80' }} />
            <span style={{ fontFamily: 'Rubik, sans-serif', fontSize: '9px', color: '#9f8e78' }}>
              {connection.last_synced_at
                ? `Last synced ${new Date(connection.last_synced_at).toLocaleDateString('en-IN')} · ${connection.sync_count} syncs`
                : 'Not yet synced'}
            </span>
          </div>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              onClick={handleSync}
              style={{
                fontFamily: 'Rubik, sans-serif',
                fontSize: '10px',
                fontWeight: 700,
                letterSpacing: '0.04em',
                color: '#08090A',
                background: '#FFB000',
                border: 'none',
                borderRadius: '6px',
                padding: '6px 14px',
                cursor: 'pointer',
              }}
            >
              Sync Now
            </button>
            {connection.notion_page_url && (
              <a
                href={connection.notion_page_url}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  fontFamily: 'Rubik, sans-serif',
                  fontSize: '10px',
                  letterSpacing: '0.04em',
                  color: '#FFB000',
                  border: '1px solid rgba(255,176,0,0.3)',
                  borderRadius: '6px',
                  padding: '6px 12px',
                  textDecoration: 'none',
                }}
              >
                Open in Notion ↗
              </a>
            )}
          </div>
        </div>
      )}

      {panelState === 'SYNCING' && (
        <div style={{ fontFamily: 'Rubik, sans-serif', fontSize: '9px', color: '#FFB000', letterSpacing: '0.04em' }}>
          Syncing...
        </div>
      )}

      {panelState === 'ERROR' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <div style={{ fontFamily: 'Rubik, sans-serif', fontSize: '9px', color: '#ff6b6b' }}>{error}</div>
          <button
            onClick={() => { setError(null); setPanelState('NOT_CONNECTED') }}
            style={{
              fontFamily: 'Rubik, sans-serif',
              fontSize: '9px',
              letterSpacing: '0.04em',
              color: '#9f8e78',
              background: 'transparent',
              border: '1px solid rgba(255,255,255,0.1)',
              borderRadius: '6px',
              padding: '4px 10px',
              cursor: 'pointer',
              alignSelf: 'flex-start',
            }}
          >
            Retry
          </button>
        </div>
      )}
    </div>
  )
}
