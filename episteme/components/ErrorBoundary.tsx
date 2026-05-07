'use client'

// components/ErrorBoundary.tsx

import { Component, type ReactNode } from 'react'

interface Props {
  children: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, info: { componentStack: string }) {
    console.error('ErrorBoundary caught:', error, info)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex flex-col items-center justify-center gap-5" style={{ background: 'var(--bg, #f8f9ff)' }}>
          <div style={{ position: 'fixed', top: 0, left: 0, right: 0, height: '2px', background: '#f87171' }} />

          <p style={{ fontSize: '22px', fontWeight: 700, color: 'var(--text)', fontFamily: 'Plus Jakarta Sans, sans-serif', fontStyle: 'italic' }}>
            Something broke.
          </p>

          {process.env.NODE_ENV === 'development' && this.state.error && (
            <p className="px-4 text-center" style={{ fontSize: '13px', color: '#f87171', maxWidth: '480px', fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
              {this.state.error.message}
            </p>
          )}

          {process.env.NODE_ENV !== 'development' && (
            <p style={{ fontSize: '13px', color: 'var(--text-dim)', fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
              An unexpected error occurred.
            </p>
          )}

          <button
            onClick={() => window.location.reload()}
            style={{
              fontSize: '13px',
              fontWeight: 600,
              color: 'var(--primary)',
              border: '1px solid rgba(103,75,181,0.3)',
              borderRadius: '9999px',
              padding: '8px 20px',
              background: 'var(--primary-soft)',
              cursor: 'pointer',
              fontFamily: 'Plus Jakarta Sans, sans-serif',
            }}
          >
            Try refreshing
          </button>
        </div>
      )
    }

    return this.props.children
  }
}
