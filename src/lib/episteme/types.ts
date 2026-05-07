/** Ported from Episteme (CBC Hackathon 2026). TypeScript types — no framework dependencies. */

export type DepthLevel = 'SURFACE' | 'CONCEPTUAL' | 'ANALYTICAL' | 'SYNTHESIS'
export type Domain = 'ml' | 'statistics' | 'economics' | 'cs' | 'general'
export type MessageRole = 'user' | 'assistant'
export type SocraticState = 'PROBE' | 'DEEPEN' | 'SCAFFOLD' | 'RECTIFY' | 'REDIRECT' | 'CONSOLIDATE' | 'COMPLETE'

export interface BKTState {
  pL: number
  pT: number
  pS: number
  pG: number
}

export interface SocraticMessage {
  id: string
  role: MessageRole
  content: string
  turnNumber: number
  state?: SocraticState
  clarityScore?: number
  isStreaming?: boolean
}

export interface SocraticSession {
  id: string
  domain: string
  turns_count: number
  is_complete: boolean
  created_at: string
}

export interface InsightCard {
  id?: string
  session_id?: string
  concept: string
  insight: string
  gaps: string[]
  clarity_score: number
  next_question: string
  created_at?: string
}

// Sentio-specific extensions
export type ChatMode = 'guide' | 'socratic'

export interface SentioSessionContext {
  mode: ChatMode
  userBiasProfile?: Record<string, number>
  recentJournalThemes?: string[]
  ragContext?: string
}
