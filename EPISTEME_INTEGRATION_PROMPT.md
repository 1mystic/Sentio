# Claude Code Prompt: Integrate Episteme Socratic Engine into Sentio

## Context for the Agent

You are working on **Sentio** — a Vue 3 + Vite + FastAPI cognitive bias self-awareness platform. You need to integrate the Socratic dialogue engine from **Episteme** — a separate Next.js project — into Sentio's chat interface (`/ai-guide` page).

The two projects live in different directories. Sentio is Vue 3. Episteme is Next.js/TypeScript. You cannot copy Vue or Next.js components directly. Your job is to port the *logic* (framework-agnostic TypeScript) and rewrite the *UI* in Vue 3.

---

## Step 1: Understand What to Take from Episteme

First, navigate to the Episteme project directory and read these files IN THIS ORDER. Do not skip any.

```
READ (in order):
1. episteme/lib/types.ts              — all TypeScript interfaces and enums
2. episteme/lib/algorithms.ts         — the 7 deterministic algorithms (PURE FUNCTIONS)
3. episteme/lib/prompts.ts            — Socratic system prompts per state
4. episteme/lib/scoring.ts            — if exists, scoring helpers
5. episteme/app/api/chat/route.ts     — the SSE streaming pipeline (12-step sequence)
6. episteme/app/api/classify/route.ts — BGDC depth classification
7. episteme/app/api/insights/route.ts — insight card generation
8. episteme/app/api/session/route.ts  — session creation
9. episteme/components/ChatPanel.tsx  — understand the UI structure only (don't copy JSX)
10. episteme/components/SidePanel.tsx — understand what data is displayed in the side panel
11. episteme/hooks/useChat.ts         — understand SSE consumption pattern
```

After reading, produce a summary of:
- Every function signature in `algorithms.ts` with its inputs and outputs
- The exact 12-step per-turn pipeline from `chat/route.ts`
- The 7 SDSM states and their transition conditions
- What the side panel displays (clarity score, depth level, knowledge map, etc.)

Do not proceed until you have read and summarised all of the above.

---

## Step 2: Understand What Sentio Already Has

Navigate to the Sentio project directory and read:

```
READ:
1. sentio/pages/ai-guide.vue              — current AI Guide page
2. sentio/components/ai/ChatInterface.vue — current chat component
3. sentio/components/ai/MessageBubble.vue — current message component
4. sentio/services/ai.js (or equivalent) — current API call pattern
5. sentio/stores/useAIStore.js (or equiv) — current AI state store
6. sentio/assets/css/main.css             — design system tokens (teal/amber palette)
```

Identify:
- How the current AI Guide calls the backend (fetch/axios, endpoint path)
- How streaming is currently handled (if at all)
- What Pinia store structure exists for AI state

---

## Step 3: Create the Shared Algorithm Library

Create this file in Sentio's project:

**`sentio/src/lib/episteme/algorithms.ts`**

Port ALL 7 algorithms from `episteme/lib/algorithms.ts` verbatim. These are pure TypeScript functions with zero framework dependencies — they port directly. 

Rules:
- Do NOT change any algorithm logic
- Do fix any Next.js-specific imports (there should be none in algorithms.ts — it's pure TS)
- Export every function individually AND as a named group
- Add JSDoc comment at top: `/** Ported from Episteme (CBC Hackathon 2026). Pure algorithmic functions — no framework dependencies. */`

Also create:

**`sentio/src/lib/episteme/types.ts`**
Port from `episteme/lib/types.ts`. Add these Sentio-specific additions at the bottom:

```typescript
// Sentio-specific extensions
export type ChatMode = 'guide' | 'socratic'

export interface SentioSessionContext {
  mode: ChatMode
  userBiasProfile?: Record<string, number>  // from Sentio's bias fingerprint
  recentJournalThemes?: string[]             // from Sentio's journal analysis
  ragContext?: string                         // only used in 'guide' mode
}
```

**`sentio/src/lib/episteme/prompts.ts`**
Port from `episteme/lib/prompts.ts`. Then add a Sentio-specific prompt wrapper:

```typescript
export function buildSentioSocraticPrompt(
  state: DialogueState,
  domain: string,
  userBiasProfile: Record<string, number>,
  journalThemes: string[]
): string {
  const basePrompt = buildPromptForState(state, domain)  // existing Episteme function
  
  const biasContext = Object.keys(userBiasProfile).length > 0
    ? `\n\nUser context from Sentio: This user's cognitive bias profile shows elevated scores in: ${
        Object.entries(userBiasProfile)
          .filter(([_, score]) => score > 60)
          .map(([bias]) => bias)
          .join(', ')
      }. Their journal themes include: ${journalThemes.join(', ')}. 
      Where relevant, connect the Socratic dialogue to these patterns — not prescriptively, but as a lens.`
    : ''
  
  return basePrompt + biasContext
}
```

---

## Step 4: Create the Sentio FastAPI Backend Routes

Create these new routes in `sentio-api/routers/socratic.py`:

```python
# sentio-api/routers/socratic.py
# Socratic dialogue engine — ported from Episteme (CBC Hackathon 2026)
# Implements the 7-algorithm pipeline as FastAPI SSE endpoints

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json, asyncio
from typing import Optional, List
from ..services.claude_service import stream_socratic_response
from ..services.supabase_client import supabase
from ..utils.validators import safety_check

router = APIRouter(prefix="/socratic", tags=["socratic"])


# ── Request / Response schemas ────────────────────────────────────────────────

class CreateSessionRequest(BaseModel):
    domain: str = "general"  # ml|statistics|psychology|general
    user_id: str

class ChatRequest(BaseModel):
    session_id: str
    message: str
    turn_number: int
    domain: str
    conversation_history: List[dict]
    concepts_covered: List[str] = []
    user_id: str

class InsightRequest(BaseModel):
    session_id: str
    concept: str
    domain: str

class ClassifyRequest(BaseModel):
    question: str
    session_id: str


# ── Algorithm stubs (implement in TypeScript on frontend, call results here) ──
# The 7 algorithms run CLIENT-SIDE in the Vue composable for low latency.
# The backend receives the algorithm outputs and uses them to build the Claude prompt.

class AlgorithmOutputs(BaseModel):
    quality_score: float          # RDSE output [0-1]
    confusion_count: int          # RDSE output [0-3]
    depth_level: str              # BGDC output: SURFACE|CONCEPTUAL|ANALYTICAL|SYNTHESIS
    next_state: str               # SDSM output: PROBE|DEEPEN|SCAFFOLD|RECTIFY|CONSOLIDATE|COMPLETE
    semantic_accuracy: float      # SUV output [0-1]
    misconception: Optional[str]  # SUV output
    bkt_pl: float                 # CBKT-CS: P(knows)
    clarity_score: int            # CBKT-CS: [0-100]


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/session")
async def create_session(req: CreateSessionRequest):
    result = supabase.table("socratic_sessions").insert({
        "domain": req.domain,
        "user_id": req.user_id,
        "turns_count": 0,
        "is_complete": False,
    }).execute()
    return {"session": result.data[0]}


@router.post("/classify")
async def classify_question(req: ClassifyRequest):
    """BGDC: classify cognitive depth of a question via Claude zero-shot."""
    from ..services.claude_service import classify_depth
    depth, confidence = await classify_depth(req.question)
    return {"depth": depth, "confidence": confidence}


@router.post("/chat")
async def socratic_chat(req: ChatRequest, algo: AlgorithmOutputs):
    """
    Core Socratic pipeline. Receives pre-computed algorithm outputs from client,
    builds enriched prompt, streams Claude response via SSE.
    """
    # Safety check
    safety = safety_check(req.message)
    if safety.action == "REDIRECT":
        return {"error": "crisis_detected", "resources": safety.message}

    # Fetch user context from Sentio (bias profile + journal themes)
    user_profile = supabase.table("user_bias_profiles")\
        .select("bias_scores")\
        .eq("user_id", req.user_id)\
        .maybe_single().execute()
    
    journal_themes = supabase.table("journal_entries")\
        .select("themes")\
        .eq("user_id", req.user_id)\
        .order("created_at", desc=True)\
        .limit(5).execute()
    
    bias_scores = user_profile.data.get("bias_scores", {}) if user_profile.data else {}
    themes = [t for entry in (journal_themes.data or []) for t in (entry.get("themes") or [])]

    async def event_stream():
        async for chunk in stream_socratic_response(
            message=req.message,
            conversation_history=req.conversation_history,
            domain=req.domain,
            next_state=algo.next_state,
            quality_score=algo.quality_score,
            misconception=algo.misconception,
            clarity_score=algo.clarity_score,
            bias_scores=bias_scores,
            journal_themes=themes,
        ):
            yield f"data: {json.dumps(chunk)}\n\n"
        
        # After stream: update DB
        supabase.table("socratic_sessions")\
            .update({"turns_count": req.turn_number + 1})\
            .eq("id", req.session_id).execute()
        
        supabase.table("socratic_messages").insert({
            "session_id": req.session_id,
            "role": "user",
            "content": req.message,
            "turn_number": req.turn_number,
        }).execute()

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.post("/insights")
async def generate_insight(req: InsightRequest):
    """Generate session insight card after ≥4 turns."""
    messages = supabase.table("socratic_messages")\
        .select("*")\
        .eq("session_id", req.session_id)\
        .order("turn_number").execute()
    
    if len([m for m in messages.data if m["role"] == "user"]) < 4:
        raise HTTPException(400, "Need at least 4 user turns for insight generation")
    
    from ..services.claude_service import generate_insight_card
    insight = await generate_insight_card(
        messages=messages.data,
        concept=req.concept,
        domain=req.domain,
    )
    
    supabase.table("socratic_insight_cards").insert({
        "session_id": req.session_id,
        **insight,
    }).execute()
    
    return {"insight_card": insight}
```

Also add to `sentio-api/services/claude_service.py`:

```python
async def stream_socratic_response(
    message: str,
    conversation_history: list,
    domain: str,
    next_state: str,
    quality_score: float,
    misconception: str | None,
    clarity_score: int,
    bias_scores: dict,
    journal_themes: list,
):
    """
    Builds the Episteme-style enriched system prompt and streams Claude response.
    next_state determines the Socratic strategy (PROBE/DEEPEN/SCAFFOLD/RECTIFY/etc.)
    """
    
    STATE_INSTRUCTIONS = {
        "PROBE": "Begin with 'Before I respond — what do you already think?' Do NOT answer the question. Probe their prior understanding.",
        "DEEPEN": "They have some understanding. Push deeper. Ask them to explain WHY, not just WHAT. Connect to implications.",
        "SCAFFOLD": "They're confused. Provide a foothold — a simpler analogy or a related concept they DO understand. Don't answer directly.",
        "RECTIFY": f"There is a misconception: '{misconception}'. Address it without saying 'you're wrong'. Guide them to discover the error.",
        "REDIRECT": "They've drifted off-topic. Gently redirect to the core concept without dismissing their tangent.",
        "CONSOLIDATE": "They've shown strong understanding. Help them synthesise. Ask them to connect this concept to something else they know.",
        "COMPLETE": "The session has reached natural completion. Acknowledge what they now understand. Reveal any remaining gap briefly.",
    }
    
    high_bias = [k for k, v in bias_scores.items() if v > 60] if bias_scores else []
    
    system = f"""You are Sentio's Socratic Guide — combining cognitive bias education with Socratic dialogue.

CURRENT DIALOGUE STATE: {next_state}
YOUR INSTRUCTION: {STATE_INSTRUCTIONS.get(next_state, STATE_INSTRUCTIONS['PROBE'])}

USER'S COGNITIVE CONTEXT (from Sentio):
- Clarity score this session: {clarity_score}/100
- Quality of last response: {quality_score:.2f}/1.0
- Domain: {domain}
- Notable cognitive biases in their profile: {', '.join(high_bias) if high_bias else 'not yet established'}
- Recent journal themes: {', '.join(journal_themes[:5]) if journal_themes else 'none yet'}

ABSOLUTE RULES:
1. NEVER directly answer the question until state is COMPLETE
2. NEVER say 'you're wrong' or 'that's incorrect' — guide them to discover errors
3. NEVER diagnose. NEVER provide clinical advice. NEVER mention their biases prescriptively.
4. Keep responses under 120 words. One focused probe at a time.
5. End every PROBE/DEEPEN response with exactly one question.
6. If the topic connects naturally to one of their known cognitive biases, you MAY note the connection — gently, once, not as a label."""

    async with anthropic.messages.stream(
        model="claude-sonnet-4-20250514",
        max_tokens=300,
        system=system,
        messages=conversation_history + [{"role": "user", "content": message}],
    ) as stream:
        async for text in stream.text_stream:
            yield {"text": text}
        
        final = await stream.get_final_message()
        yield {
            "done": True,
            "clarity_score": clarity_score,
            "next_state": next_state,
            "can_generate_insight": False,  # client computes from turn count
            "input_tokens": final.usage.input_tokens,
            "output_tokens": final.usage.output_tokens,
        }
```

---

## Step 5: Add Supabase Tables for Socratic Sessions

Run this in Supabase SQL editor:

```sql
-- Socratic sessions (Episteme sessions, now within Sentio)
CREATE TABLE socratic_sessions (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id       UUID REFERENCES profiles(id) ON DELETE CASCADE,
  domain        TEXT NOT NULL DEFAULT 'general',
  turns_count   INT DEFAULT 0,
  is_complete   BOOLEAN DEFAULT FALSE,
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- Socratic messages
CREATE TABLE socratic_messages (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id    UUID REFERENCES socratic_sessions(id) ON DELETE CASCADE,
  role          TEXT CHECK (role IN ('user', 'assistant')),
  content       TEXT NOT NULL,
  turn_number   INT NOT NULL,
  algo_state    TEXT,           -- which SDSM state produced this response
  clarity_score INT,            -- BKT clarity at this turn
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- Socratic insight cards
CREATE TABLE socratic_insight_cards (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id    UUID REFERENCES socratic_sessions(id) ON DELETE CASCADE,
  concept       TEXT NOT NULL,
  insight       TEXT NOT NULL,
  gaps          TEXT[] DEFAULT '{}',
  clarity_score INT DEFAULT 0,
  next_question TEXT,
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- Socratic concept mastery (BKT state per concept per session)
CREATE TABLE socratic_concepts (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id    UUID REFERENCES socratic_sessions(id) ON DELETE CASCADE,
  user_id       UUID REFERENCES profiles(id),
  name          TEXT NOT NULL,
  depth_reached TEXT CHECK (depth_reached IN ('SURFACE','CONCEPTUAL','ANALYTICAL','SYNTHESIS')),
  clarity_score INT DEFAULT 0,
  bkt_pl        FLOAT DEFAULT 0.20,
  created_at    TIMESTAMPTZ DEFAULT NOW()
);
```

---

## Step 6: Create the Vue Composable — `useEpistemeChat.ts`

This is the most important file. Create it at:

**`sentio/src/composables/useEpistemeChat.ts`**

This composable ports the logic from Episteme's `hooks/useChat.ts` and `hooks/useClarity.ts` into Vue 3.

```typescript
// sentio/src/composables/useEpistemeChat.ts
// Ports Episteme's Socratic engine hooks into Vue 3 reactive composable

import { ref, computed } from 'vue'
import {
  extractDepthSignals,      // RDSE
  determineNextState,       // SDSM
  updateBKT,                // CBKT-CS
  buildDepthClassification, // BGDC (keyword portion — LLM portion handled by API)
  prioritiseGaps,           // EGP
  // Import remaining algorithms from lib/episteme/algorithms.ts
} from '@/lib/episteme/algorithms'
import type { 
  DialogueState, 
  Message, 
  AlgorithmOutputs,
  ChatMode,
} from '@/lib/episteme/types'
import { useUserStore } from '@/stores/useUserStore'
import { useJournalStore } from '@/stores/useJournalStore'

export function useEpistemeChat() {
  const userStore = useUserStore()
  const journalStore = useJournalStore()

  // ── State ──────────────────────────────────────────────────────────────────
  const messages = ref<Message[]>([])
  const isStreaming = ref(false)
  const currentState = ref<DialogueState>('PROBE')
  const clarityScore = ref(0)
  const turnNumber = ref(0)
  const sessionId = ref<string | null>(null)
  const domain = ref('general')
  const conceptsCovered = ref<string[]>([])
  const canGenerateInsight = ref(false)
  const currentStreamedText = ref('')
  const algoOutputs = ref<AlgorithmOutputs | null>(null)

  // BKT state
  const bktState = ref({ pL: 0.20, pT: 0.12, pS: 0.10, pG: 0.08 })

  // ── Computed ───────────────────────────────────────────────────────────────
  const depthLabel = computed(() => {
    const score = clarityScore.value
    if (score < 25) return 'Surface'
    if (score < 50) return 'Conceptual'
    if (score < 75) return 'Analytical'
    return 'Synthesis'
  })

  const stateLabel = computed(() => ({
    PROBE: 'Exploring your understanding',
    DEEPEN: 'Pushing deeper',
    SCAFFOLD: 'Building a foothold',
    RECTIFY: 'Correcting a misconception',
    REDIRECT: 'Refocusing',
    CONSOLIDATE: 'Synthesising',
    COMPLETE: 'Session complete',
  }[currentState.value] ?? 'Thinking'))

  // ── Actions ────────────────────────────────────────────────────────────────
  async function startSession(selectedDomain: string = 'general') {
    domain.value = selectedDomain
    messages.value = []
    turnNumber.value = 0
    clarityScore.value = 0
    currentState.value = 'PROBE'
    bktState.value = { pL: 0.20, pT: 0.12, pS: 0.10, pG: 0.08 }

    const res = await fetch('/api/socratic/session', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        domain: selectedDomain,
        user_id: userStore.profile?.id,
      }),
    })
    const data = await res.json()
    sessionId.value = data.session.id
  }

  async function sendMessage(userText: string) {
    if (!sessionId.value || isStreaming.value) return

    // 1. Add user message to UI immediately
    messages.value.push({ role: 'user', content: userText, turnNumber: turnNumber.value })

    // 2. Run client-side algorithms (RDSE → SDSM → CBKT-CS)
    const depthSignals = extractDepthSignals(userText, turnNumber.value)
    const nextState = determineNextState({
      turnNumber: turnNumber.value,
      qualityScore: depthSignals.qualityScore,
      confusionCount: depthSignals.confusionCount,
      currentState: currentState.value,
      clarityScore: clarityScore.value,
      consecutiveScaffolds: countConsecutiveScaffolds(),
    })
    const newBKT = updateBKT(bktState.value, depthSignals.qualityScore)
    const newClarity = Math.round(newBKT.pL * 100)

    // Update local state
    currentState.value = nextState
    bktState.value = newBKT
    clarityScore.value = newClarity
    algoOutputs.value = {
      quality_score: depthSignals.qualityScore,
      confusion_count: depthSignals.confusionCount,
      depth_level: depthSignals.depthLevel,
      next_state: nextState,
      semantic_accuracy: 1.0,  // SUV runs server-side for the first version
      misconception: null,
      bkt_pl: newBKT.pL,
      clarity_score: newClarity,
    }

    // 3. Start streaming response
    isStreaming.value = true
    currentStreamedText.value = ''

    // Add empty assistant message as streaming placeholder
    messages.value.push({ role: 'assistant', content: '', turnNumber: turnNumber.value, isStreaming: true })
    const assistantMsgIndex = messages.value.length - 1

    try {
      const response = await fetch('/api/socratic/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId.value,
          message: userText,
          turn_number: turnNumber.value,
          domain: domain.value,
          conversation_history: messages.value
            .filter(m => !m.isStreaming)
            .map(m => ({ role: m.role, content: m.content })),
          concepts_covered: conceptsCovered.value,
          user_id: userStore.profile?.id,
          // Algorithm outputs passed to backend
          quality_score: algoOutputs.value.quality_score,
          confusion_count: algoOutputs.value.confusion_count,
          depth_level: algoOutputs.value.depth_level,
          next_state: algoOutputs.value.next_state,
          semantic_accuracy: algoOutputs.value.semantic_accuracy,
          misconception: algoOutputs.value.misconception,
          bkt_pl: algoOutputs.value.bkt_pl,
          clarity_score: algoOutputs.value.clarity_score,
        }),
      })

      // 4. Parse SSE stream
      const reader = response.body!.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() ?? ''

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          const payload = JSON.parse(line.slice(6))

          if (payload.text) {
            currentStreamedText.value += payload.text
            messages.value[assistantMsgIndex].content = currentStreamedText.value
          }

          if (payload.done) {
            messages.value[assistantMsgIndex].isStreaming = false
            clarityScore.value = payload.clarity_score
            canGenerateInsight.value = turnNumber.value >= 3
          }
        }
      }
    } finally {
      isStreaming.value = false
      turnNumber.value++
    }
  }

  async function generateInsight(concept: string) {
    if (!sessionId.value || turnNumber.value < 4) return null

    const res = await fetch('/api/socratic/insights', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId.value,
        concept,
        domain: domain.value,
      }),
    })
    return (await res.json()).insight_card
  }

  function countConsecutiveScaffolds(): number {
    let count = 0
    for (let i = messages.value.length - 1; i >= 0; i--) {
      const msg = messages.value[i] as any
      if (msg.role === 'assistant' && msg.algoState === 'SCAFFOLD') count++
      else if (msg.role === 'assistant') break
    }
    return count
  }

  return {
    // State
    messages, isStreaming, currentState, clarityScore,
    turnNumber, sessionId, domain, canGenerateInsight,
    algoOutputs,
    // Computed
    depthLabel, stateLabel,
    // Actions
    startSession, sendMessage, generateInsight,
  }
}
```

---

## Step 7: Build the Dual-Mode AI Guide Page

Now replace `sentio/pages/ai-guide.vue` with a dual-mode interface:

**`sentio/pages/ai-guide.vue`**

Requirements:
- Two modes, toggled with a pill switcher at the top:
  - **Guide mode** (existing): RAG-powered Q&A about cognitive biases. Uses existing `useAIStore` and RAG endpoint. 
  - **Socratic mode** (new): Episteme engine. Uses `useEpistemeChat`. 
- Mode switcher: pill toggle — "Ask anything" | "Socratic session"
- In Socratic mode, show a domain selector BEFORE the first message: "What are you exploring?" with options: General thinking · Cognitive biases · Decision-making · Statistics · ML concepts
- Crisis intercept banner always visible (both modes)
- Disclaimer always visible (both modes)

**Socratic mode layout (two-column on desktop, single column on mobile):**

Left column (70%): Chat area
- Message bubbles (user right, assistant left — same style as Guide mode)  
- For assistant messages: show a subtle state badge (e.g. "Probing your understanding")
- Input bar at bottom with send button
- Streaming: assistant message streams in character by character

Right column (30%): Live Cognitive Panel
- **Clarity meter**: vertical progress bar, 0-100, teal fill, label "Clarity" + score
- **Current state**: pill badge showing SDSM state with label (e.g. "Deepening")  
- **Depth level**: current Bloom's level (Surface / Conceptual / Analytical / Synthesis)
- **Turn count**: "Turn 3 of session"
- **"Generate insight" button**: appears when `canGenerateInsight === true` (after turn 4)
- **Insight card**: when generated, expands inline — concept, what was understood, gaps, next question

Use Sentio's design system throughout (teal/amber palette, DM Sans + Instrument Serif, CSS variables). Do NOT import any Episteme styling.

On mobile: right panel collapses into a thin strip at the top of the chat area showing just the clarity score and current state badge.

---

## Step 8: Wire the Router and Register the Backend Route

In `sentio-api/main.py`:
```python
from routers.socratic import router as socratic_router
app.include_router(socratic_router, prefix="/api")
```

In `sentio/src/router/index.js` — the `/ai-guide` route should already exist. Verify it uses `DefaultLayout`.

---

## Step 9: Final Verification Checklist

Before finishing, verify each item:

```
ALGORITHMS:
[ ] algorithms.ts ported — run: npx tsc --noEmit in sentio/src/lib/episteme/
[ ] All 7 functions exported and callable
[ ] extractDepthSignals('because the model is overfitting', 2) returns an object with qualityScore, confusionCount, depthLevel
[ ] determineNextState({turnNumber: 1, qualityScore: 0.1, ...}) returns 'SCAFFOLD'
[ ] updateBKT({pL: 0.2, pT: 0.12, pS: 0.10, pG: 0.08}, 0.7) returns updated pL > 0.2

BACKEND:
[ ] POST /api/socratic/session returns {session: {id, domain, turns_count}}
[ ] POST /api/socratic/chat streams SSE with {text} and final {done, clarity_score, next_state}
[ ] POST /api/socratic/insights returns {insight_card} after ≥4 turns
[ ] Safety check fires on crisis keywords — returns crisis resources, does NOT call Claude

FRONTEND:
[ ] Mode toggle switches between Guide and Socratic cleanly
[ ] Socratic mode: domain selector shown before first message
[ ] Messages stream character by character in Socratic mode
[ ] Right panel updates clarity score after each turn
[ ] State badge changes correctly as turns progress
[ ] "Generate insight" button appears after turn 4
[ ] Insight card renders inline with concept, insight text, gaps, next question
[ ] Crisis banner always visible
[ ] Disclaimer always visible
[ ] Sentio design system used throughout (no Episteme dark terminal aesthetic)
[ ] Mobile: right panel collapses to top strip

DATABASE:
[ ] socratic_sessions, socratic_messages, socratic_insight_cards, socratic_concepts tables created
[ ] Row Level Security: users can only read/write their own rows
```

---

## What NOT to Port

Do NOT port these from Episteme — they either don't apply or conflict with Sentio:
- `app/page.tsx` — Episteme's landing page (Sentio has its own)
- `app/session/[sessionId]/page.tsx` — full Next.js page (rewritten in Vue)
- `components/SessionReplay.tsx` — skip for now (V2 feature)
- `components/ExportPanel.tsx` — skip for now (Sentio has its own export)
- `app/api/export/route.ts` — skip for now
- `app/api/agent/reflect/route.ts` — skip for V1, add as Phase 2 feature
- Any Episteme database migrations — Sentio has its own Supabase project
- Any Episteme `.env` values — Sentio uses its own API keys
- Episteme's Tailwind config or global CSS — Sentio uses its own design system

---

## Summary: What Gets Created

```
NEW FILES IN SENTIO:
  sentio/src/lib/episteme/
    ├── algorithms.ts       ← ported verbatim from Episteme
    ├── types.ts            ← ported + Sentio extensions
    └── prompts.ts          ← ported + Sentio bias context wrapper

  sentio/src/composables/
    └── useEpistemeChat.ts  ← Vue 3 port of Episteme's useChat + useClarity hooks

  sentio-api/routers/
    └── socratic.py         ← new FastAPI router (session, chat SSE, insights, classify)

MODIFIED FILES IN SENTIO:
  sentio/pages/ai-guide.vue           ← dual-mode: Guide + Socratic
  sentio-api/main.py                  ← register socratic router
  sentio-api/services/claude_service.py  ← add stream_socratic_response()

NEW SUPABASE TABLES:
  socratic_sessions
  socratic_messages
  socratic_insight_cards
  socratic_concepts
```
