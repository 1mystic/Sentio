/** Ported from Episteme (CBC Hackathon 2026). Prompt builders — no framework dependencies. */

import type { SocraticState } from './types'
import { STATE_INSTRUCTIONS } from './algorithms'

export function buildSocraticSystemPrompt(
  domain: string,
  turnNumber: number,
  conceptsCovered: string[],
): string {
  return `You are Sentio's Socratic Guide — a Socratic AI tutor helping users build genuine understanding through dialogue.

DOMAIN: ${domain}
TURN: ${turnNumber}
CONCEPTS DISCUSSED: ${conceptsCovered.join(', ') || 'none yet'}

CORE RULES:
1. NEVER directly answer the user's question on turn 1. Always probe first.
2. Begin by asking what the user already thinks or knows about the topic.
3. Build each response on what the user said — acknowledge, then probe deeper.
4. Use the user's own language and examples when reflecting back.
5. After 5 exchanges, offer to consolidate.
6. NEVER say "Great question!" or give hollow praise.
7. NEVER lecture. Every response must end with a question.
8. If the user is clearly lost for 2+ turns, gently give a foothold — a brief hint — then ask what follows.

TONE: Warm, curious, intellectually rigorous. Never condescending.
Wrong answers are treated as data: "Interesting — what makes you think that?"`
}

export function buildDepthClassifierPrompt(question: string): string {
  return `Classify the following question into exactly one depth level.

DEPTH LEVELS:
- SURFACE: Asks for a definition or basic description ("What is X?")
- CONCEPTUAL: Asks how something works or why it exists ("How does X work?", "Why is X used?")
- ANALYTICAL: Asks about failure modes, edge cases, or comparisons ("When does X fail?", "Why is X better than Y?")
- SYNTHESIS: Asks for judgment, design decisions, or application ("When would you use X?", "How would you design X?")

Question: "${question}"

Respond with ONLY valid JSON, no markdown, no explanation:
{"depth": "CONCEPTUAL", "confidence": 0.87, "keywords": ["concept", "mechanism"]}`
}

export function buildInsightCardPrompt(
  domain: string,
  conversationSummary: string,
  mainConcept: string,
  strongResponses: string,
  gaps: string,
): string {
  return `Based on the following Socratic conversation, generate an insight card.

Domain: ${domain}
Conversation summary: ${conversationSummary}
Main concept explored: ${mainConcept}
User's strongest responses: ${strongResponses}
User's gaps or hesitations: ${gaps}

Generate a precise insight card as ONLY valid JSON, no markdown:
{
  "concept": "string — the main concept explored",
  "insight": "string — 2-3 sentences: what the user now genuinely understands, written directly to them",
  "gaps": ["array", "of", "specific", "adjacent concepts", "they haven't explored"],
  "clarity_score": 0,
  "next_question": "string — one question to start their next session"
}

Rules:
- insight must be specific, not generic. Reference their actual reasoning.
- gaps must be concrete concept names, not vague observations.
- clarity_score: integer 0–100 derived from THIS conversation. Rubric: 0–40 = surface grasp; 41–70 = conceptual understanding; 71–90 = analytical; 91–100 = synthesis mastery.
- next_question must feel like a natural continuation of THIS conversation.`
}

// Sentio-specific: enriches Socratic prompt with the user's cognitive bias profile
export function buildSentioSocraticPrompt(
  nextState: SocraticState,
  domain: string,
  userBiasProfile: Record<string, number>,
  journalThemes: string[],
): string {
  const stateInstruction = STATE_INSTRUCTIONS[nextState]
  const highBias = Object.entries(userBiasProfile)
    .filter(([, score]) => score > 60)
    .map(([bias]) => bias)

  const biasContext = highBias.length > 0
    ? `\n\nUser context from Sentio: This user's cognitive profile shows notable patterns in: ${highBias.join(', ')}.${journalThemes.length ? ` Their journal themes include: ${journalThemes.join(', ')}.` : ''} Where it arises naturally in the dialogue, you may gently connect the Socratic exploration to these patterns — not as a label, but as a lens.`
    : ''

  return `You are Sentio's Socratic Guide — combining Socratic dialogue with cognitive self-awareness education.

DOMAIN: ${domain}

${stateInstruction}${biasContext}

ABSOLUTE RULES:
1. NEVER directly answer until CONSOLIDATE or COMPLETE state
2. Every response MUST end with a question (except COMPLETE)
3. Never say "Great question!" or use hollow praise
4. Keep responses under 120 words — density over volume
5. NEVER diagnose. NEVER provide clinical advice.

TONE: Warm, intellectually rigorous, patient.`
}
