'use client'

// hooks/useSession.ts

import { useState, useEffect, useCallback } from 'react'
import type { Session, Message, Concept, InsightCard, LearnerProfile, SessionFingerprint } from '@/lib/types'

interface UseSessionResult {
  session: Session | null
  messages: Message[]
  concepts: Concept[]
  fingerprint: SessionFingerprint | null
  learnerProfile: LearnerProfile | null
  insightCard: InsightCard | null
  isLoading: boolean
  error: string | null
  refetch: () => void
}

export function useSession(sessionId: string): UseSessionResult {
  const [session, setSession] = useState<Session | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [concepts, setConcepts] = useState<Concept[]>([])
  const [fingerprint, setFingerprint] = useState<SessionFingerprint | null>(null)
  const [learnerProfile, setLearnerProfile] = useState<LearnerProfile | null>(null)
  const [insightCard, setInsightCard] = useState<InsightCard | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchSession = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const res = await fetch(`/api/session?id=${sessionId}`)
      if (res.status === 404) {
        setError('Session not found')
        return
      }
      if (!res.ok) {
        setError('Failed to load session')
        return
      }
      const data = await res.json() as {
        session: Session
        messages: Message[]
        concepts: Concept[]
        fingerprint: SessionFingerprint | null
        learnerProfile: LearnerProfile | null
        insightCard: InsightCard | null
      }
      setSession(data.session)
      setMessages(data.messages)
      setConcepts(data.concepts)
      setFingerprint(data.fingerprint ?? null)
      setLearnerProfile(data.learnerProfile ?? null)
      setInsightCard(data.insightCard ?? null)
    } catch {
      setError('Failed to load session')
    } finally {
      setIsLoading(false)
    }
  }, [sessionId])

  useEffect(() => {
    fetchSession()
  }, [fetchSession])

  return { session, messages, concepts, fingerprint, learnerProfile, insightCard, isLoading, error, refetch: fetchSession }
}
