'use client'

import { useState, useEffect, useRef } from 'react'
import type { Notification } from '@/lib/types'

interface NotificationBellProps {
  sessionId: string
}

export function NotificationBell({ sessionId }: NotificationBellProps) {
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [open, setOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  const unreadCount = notifications.filter(n => !n.is_read).length

  useEffect(() => {
    fetch(`/api/notifications?sessionId=${sessionId}&unread=false`)
      .then(r => r.json())
      .then((d: { notifications: Notification[] }) => setNotifications(d.notifications))
      .catch(() => {})
  }, [sessionId])

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClick)
    return () => document.removeEventListener('mousedown', handleClick)
  }, [])

  async function handleOpen() {
    setOpen(prev => !prev)
    if (!open && unreadCount > 0) {
      await fetch('/api/notifications', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sessionId }),
      })
      setNotifications(prev => prev.map(n => ({ ...n, is_read: true })))
    }
  }

  function formatTime(iso: string) {
    const h = Math.round((Date.now() - new Date(iso).getTime()) / 3600000)
    if (h < 1) return 'just now'
    if (h < 24) return `${h}h ago`
    return `${Math.round(h / 24)}d ago`
  }

  return (
    <div ref={dropdownRef} style={{ position: 'relative' }}>
      <button
        onClick={handleOpen}
        style={{
          fontFamily: 'Plus Jakarta Sans, sans-serif',
          fontSize: '12px',
          fontWeight: 600,
          color: unreadCount > 0 ? 'var(--amber)' : 'var(--text-dim)',
          background: open ? 'rgba(255,176,0,0.08)' : 'transparent',
          border: '1px solid',
          borderColor: unreadCount > 0 ? 'rgba(255,176,0,0.3)' : 'var(--border)',
          padding: '4px 10px',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          gap: '5px',
          borderRadius: '9999px',
        }}
      >
        Alerts
        {unreadCount > 0 && (
          <span style={{
            background: 'var(--amber)',
            color: '#09090e',
            fontFamily: 'Plus Jakarta Sans, sans-serif',
            fontSize: '9px',
            fontWeight: 700,
            padding: '1px 5px',
            borderRadius: '9999px',
            minWidth: '16px',
            textAlign: 'center',
          }}>
            {unreadCount}
          </span>
        )}
      </button>

      {open && (
        <div style={{
          position: 'absolute',
          right: 0,
          top: 'calc(100% + 8px)',
          width: '320px',
          background: 'rgba(15,15,24,0.96)',
          backdropFilter: 'blur(20px)',
          WebkitBackdropFilter: 'blur(20px)',
          border: '1px solid rgba(255,176,0,0.20)',
          borderRadius: '16px',
          zIndex: 50,
          maxHeight: '400px',
          overflowY: 'auto',
          boxShadow: '0 8px 32px rgba(0,0,0,0.4)',
        }}>
          <div style={{
            padding: '10px 16px',
            borderBottom: '1px solid var(--border)',
            fontFamily: 'Plus Jakarta Sans, sans-serif',
            fontSize: '12px',
            fontWeight: 600,
            color: 'var(--amber)',
          }}>
            Alerts — {notifications.length} total
          </div>
          {notifications.length === 0 ? (
            <div style={{ padding: '20px 16px', fontFamily: 'Plus Jakarta Sans, sans-serif', fontSize: '13px', color: 'var(--text-dim)' }}>
              No alerts yet
            </div>
          ) : (
            notifications.map(n => (
              <div
                key={n.id}
                style={{
                  padding: '12px 16px',
                  borderLeft: '3px solid',
                  borderLeftColor: n.is_read ? 'var(--outline-variant)' : 'var(--primary)',
                  borderBottom: '1px solid var(--border)',
                  background: n.is_read ? 'transparent' : 'var(--primary-soft)',
                }}
              >
                <div style={{ fontFamily: 'Plus Jakarta Sans, sans-serif', fontSize: '13px', fontWeight: 600, color: 'var(--text)', marginBottom: '4px' }}>
                  {n.title}
                </div>
                <div style={{ fontSize: '12px', color: 'var(--text-muted)', lineHeight: 1.5, marginBottom: '6px', fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
                  {n.body}
                </div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <span style={{ fontFamily: 'Plus Jakarta Sans, sans-serif', fontSize: '11px', color: 'var(--text-dim)' }}>
                    {formatTime(n.created_at)}
                  </span>
                  {n.action_url && (
                    <a
                      href={n.action_url}
                      style={{ fontFamily: 'Plus Jakarta Sans, sans-serif', fontSize: '12px', fontWeight: 600, color: 'var(--primary)', textDecoration: 'none' }}
                    >
                      Resume →
                    </a>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  )
}
