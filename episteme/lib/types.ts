// lib/types.ts

export type DepthLevel = 'SURFACE' | 'CONCEPTUAL' | 'ANALYTICAL' | 'SYNTHESIS'
export type Domain = 'ml' | 'statistics' | 'economics' | 'cs' | 'general'
export type MessageRole = 'user' | 'assistant'

export interface Message {
  id: string
  session_id: string
  role: MessageRole
  content: string
  turn_number: number
  created_at: string
}

export interface Session {
  id: string
  domain: Domain
  created_at: string
  updated_at: string
  turns_count: number
  is_complete: boolean
  session_state?: {
    lastState?: string
    semanticAccuracy?: number
    consecutiveScaffolds?: number
    misconception?: string | null
  } | null
}

export interface Concept {
  id: string
  session_id: string
  name: string
  depth_reached: DepthLevel
  clarity_score: number
  created_at: string
}

export interface InsightCard {
  id: string
  session_id: string
  concept: string
  insight: string
  gaps: string[]
  clarity_score: number
  created_at: string
  next_starter?: string | null
}

export interface ClassifyResponse {
  depth: DepthLevel
  confidence: number
  keywords: string[]
}

export interface ChatRequest {
  sessionId: string
  message: string
  turnNumber: number
  domain: Domain
  conversationHistory: { role: MessageRole; content: string }[]
  conceptsCovered: string[]
}

export interface InsightRequest {
  sessionId: string
  domain: Domain
  conversationHistory: { role: MessageRole; content: string }[]
  mainConcept: string
}

export interface ChatState {
  messages: Message[]
  isStreaming: boolean
  currentStreamContent: string
  sessionId: string | null
  domain: Domain | null
  clarityScore: number
  depthLevel: DepthLevel | null
  conceptsCovered: string[]
  isComplete: boolean
  insightCard: InsightCard | null
}

export interface SidePanelState {
  concepts: Concept[]
  clarityHistory: number[]
  depthHistory: DepthLevel[]
}

export type SocraticState = 'PROBE' | 'DEEPEN' | 'SCAFFOLD' | 'RECTIFY' | 'REDIRECT' | 'CONSOLIDATE' | 'COMPLETE'

export interface LearnerProfile {
  id: string
  session_id: string
  strength_areas: string[]
  urgent_gaps: string[]
  next_session_starter: string
  learning_trajectory: 'accelerating' | 'plateauing' | 'regressing'
  recommended_depth: DepthLevel
  metacognitive_note?: string
  created_at: string
}

export interface SessionFingerprint {
  id: string
  session_id: string
  dominant_reasoning_style: string
  state_frequencies: Record<SocraticState, number>
  avg_bkt_delta: number
  avg_quality_score: number
  bloom_distribution: Record<DepthLevel, number>
  strong_concepts: string[]
  weak_concepts: string[]
  active_misconceptions: string[]
  next_session_question?: string
  recommended_depth: string
  metacognitive_note?: string
  total_turns: number
  breakthrough_turn?: number
  independent_reasoning_streak: number
  updated_at: string
  created_at: string
}

export interface Notification {
  id: string
  session_id: string
  type: 'daily_reflect' | 'weekly_digest' | 'streak_alert' | 'gap_reminder'
  title: string
  body: string
  action_url?: string
  is_read: boolean
  metadata: Record<string, unknown>
  created_at: string
}
