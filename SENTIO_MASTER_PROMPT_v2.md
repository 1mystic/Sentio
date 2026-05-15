# SENTIO — CLAUDE CODE MASTER PROMPT v2
## Based on Actual README + Critical Audit (May 2026)
## Anti-Hallucination · Context-Preserving · Multi-AI Orchestrated

---

> **HOW TO USE THIS FILE**
> At the start of every Claude Code session, paste the relevant PHASE block.
> Claude Code MUST read `docs/CONTEXT.md` and `docs/PROGRESS.md` before
> touching any file. Update both at the end of every session. No exceptions.

---

## PRIME DIRECTIVE

You are a senior engineer fixing the Sentio cognitive-bias platform.
The project is a real, live, deployed full-stack app (sentio-go.vercel.app).
This is NOT a greenfield build — you are fixing and completing an existing system.

**Stack (confirmed from README):**
- Frontend: Vue 3 + Vite + Pinia + Vue Router 4 (JavaScript, not TypeScript — except episteme/lib/)
- Backend: FastAPI / Python 3.11 / Pydantic v2 / APScheduler → HuggingFace Spaces Docker port 7860
- Database: Supabase (PostgreSQL + pgvector + RLS + Auth)
- AI: Anthropic Claude (haiku default, sonnet optional) via async streaming SDK
- Embeddings: sentence-transformers all-MiniLM-L6-v2 (384-dim, pre-warmed at startup)
- Reranking: Cohere rerank-english-v2.0 (optional, graceful degradation)
- Auth: Supabase email/password + Google OAuth
- Deployment: Vercel (frontend) + HuggingFace Spaces Docker (backend)

**What actually exists (confirmed from audit):**
- ✅ Vue 3 frontend with Pinia stores, router guards, SSE streaming
- ✅ FastAPI backend with auth, CORS, lifespan pre-warming
- ✅ Supabase schema with RLS declared (but policies may not be written)
- ✅ RAG pipeline: embed → pgvector → optional Cohere rerank → injected into Claude prompt
- ✅ Bias classifier: Claude Haiku zero-shot with 15-class taxonomy + prompt caching
- ✅ Safety gate: crisis input check + output filter (completeness TBD)
- ✅ APScheduler background tasks for journal analysis
- ✅ `src/lib/episteme/algorithms.ts` EXISTS (7 algorithms in TypeScript)
- ⚠️ Episteme algorithms: file exists but integration into socratic.py is incomplete
- ❌ Journal NLP (sentiment/emotion): keyword fallback only, returns 0.0
- ❌ Archetype model: hardcoded if-else, not UMAP clustering
- ❌ RLS policies: declared in schema but explicit policies may not be written
- ❌ Safety output filter: claimed in README, implementation completeness unknown
- ❌ Therapist directory: demo data only, booking doesn't notify
- ❌ Insight PDF/clipboard export: claimed, not implemented
- ❌ No TypeScript in frontend (only in lib/episteme/)
- ❌ No tests, no CI/CD
- ❌ Sentiment score always 0.0 in DB

---

## ANTI-HALLUCINATION RULES (Non-negotiable, every session)

1. **READ BEFORE WRITE.** Read every file you will modify. Read functions you call.
   Never assume file contents — always `cat` or `view` them first.

2. **NO INVENTED STATUS.** If you haven't verified something works,
   write `[UNVERIFIED]` not `[DONE]`. Tested = ran the command, saw the output.

3. **NO NEW CLAIMS.** Do not add claims to README or docs that aren't implemented.
   Tighten claims. Never expand them.

4. **CONTEXT FILES ARE GROUND TRUTH.** If CONTEXT.md says a file exists with
   a certain schema, verify before extending it. The audit found discrepancies —
   always check reality, not docs.

5. **ONE TASK AT A TIME.** Complete → verify → document → commit → next task.
   Never batch 5 things without verifying each.

6. **WHEN UNSURE, STOP.** Write a clear question in PROGRESS.md under `## BLOCKED`.
   Do not guess at behavior of Supabase RLS, APScheduler, or SSE internals.

7. **REAL DATA ONLY.** Never write a metric (score, count, correlation) unless
   you computed it from real data in this session. Use `[NEEDS_REAL_DATA]`.

---

## CONTEXT FILES — MAINTAIN THESE ALWAYS

### `docs/CONTEXT.md` — Project Ground Truth

Update this file whenever any of the following change:
- A new route is added or modified
- The database schema changes
- A service is implemented (was stub → now real)
- An environment variable is added

```markdown
# Sentio Project Context
Last updated: [DATE] — Session [N]

## Deployment URLs
- Frontend: https://sentio-go.vercel.app
- Backend API: https://mozoj4-sentio-backend.hf.space/docs
- Supabase: [project ref]

## Tech Stack (verified)
[list with versions, updated only after verifying in requirements.txt / package.json]

## API Routes — Status
[route] [method] — [REAL/STUB/BROKEN/PARTIAL] — [last verified date]

## Services — Status
[service file] — [REAL/STUB/PARTIAL] — [what it actually does]

## Episteme Algorithm Integration Status
[RDSE/SDSM/CBKT-CS/BGDC/CPGAB/EGP/SM-2] — [CLIENT-SIDE-ONLY/WIRED-TO-BACKEND/STUB]

## RLS Policy Status
[table] — [RLS-ON/RLS-OFF] — [policies written: Y/N]

## Known Issues (open)
[issue] — [severity] — [discovered in session N]
```

### `docs/PROGRESS.md` — Session Log (append only)

```markdown
## Session [N] — [DATE]
### Goal
[one sentence]
### Done
- [task]: [what exactly was done] — REASON: [why this approach]
### Files changed
- [path]: [nature of change]
### Commands run & output
- `[command]`: [result / last few lines of output]
### Status of goal
[COMPLETE / PARTIAL / BLOCKED]
### Next session: start with
[single specific task]
### BLOCKED ON (if any)
[clear question]
---
```

---

## PHASE 0 — DEEP AUDIT (DO THIS FIRST, NO CODE CHANGES)

```
CLAUDE CODE INSTRUCTIONS — PHASE 0

Goal: Build accurate ground truth of what exists. No code changes.

Step 1: Map every file
  - Run: find . -type f -name "*.py" -o -name "*.vue" -o -name "*.ts" -o -name "*.js" | sort
  - Note any directory that looks structural but is empty (no files >10 lines)

Step 2: Verify episteme algorithms actually work
  - Read: src/lib/episteme/algorithms.ts in full
  - Read: src/lib/episteme/types.ts and prompts.ts
  - Read: src/pages/AIGuide.vue — does it import from lib/episteme/?
  - Read: sentio-api/routers/socratic.py — does it use any signals from frontend algorithms?
  - Determine: Are these algorithms (a) fully implemented in TS, (b) called from Vue,
    (c) their output signals sent with each API call to enrich Claude's prompt?
  - Mark each of 7 algorithms: [TS-IMPLEMENTED] / [TS-STUB] / [WIRED-TO-BACKEND] / [ISOLATED]

Step 3: Verify safety gate completeness
  - Read: sentio-api/services/safety.py in full
  - Verify: Does input check cover /journal create, /ai/chat, /socratic/chat?
  - Verify: Is the output filter (regex scan of streamed chunks) actually implemented
    in the SSE streaming path, or just mentioned in comments?
  - Mark each endpoint: [HAS-CRISIS-GATE] / [MISSING-CRISIS-GATE]
  - Mark output filter: [IMPLEMENTED] / [STUB] / [MISSING]

Step 4: Verify RLS
  - Read: sentio-api/db/migration_phase6.sql (if it exists)
  - Determine: Are explicit CREATE POLICY statements present for all user-scoped tables?
  - Tables that need RLS: journal_entries, user_bias_profiles, assessment_submissions,
    socratic_sessions, notifications, user_badges
  - Mark each: [RLS-POLICY-EXISTS] / [RLS-ENABLED-NO-POLICY] / [RLS-OFF]

Step 5: Verify journal NLP
  - Read: sentio-api/services/journal_nlp.py in full
  - Is sentiment_score actually computed, or always 0.0 / None?
  - Is there a real HF Space endpoint being called, or just a local keyword fallback?
  - Mark: [REAL-SENTIMENT] / [ALWAYS-ZERO] / [HF-ENDPOINT-EXISTS-BUT-UNREACHABLE]

Step 6: Verify insight synthesis
  - Read: sentio-api/routers/insights.py
  - Are weekly insights actually Claude-synthesized, or templated strings?
  - Mark: [CLAUDE-SYNTHESIZED] / [TEMPLATED]

Step 7: Verify therapist booking
  - Read: sentio-api/routers/therapists.py
  - Does POST /therapists/{id}/book send any notification (email/webhook)?
  - Is the directory real therapists or demo data?
  - Mark: [REAL-THERAPISTS] / [DEMO-DATA-ONLY]

Step 8: Check for hardcoded secrets
  - Run: grep -r "sk-ant\|supabase\.co\|eyJ" . --include="*.py" --include="*.vue" --include="*.js"
  - Any hits = CRITICAL SECURITY ISSUE, fix before anything else

Step 9: Check model names for accuracy
  - Run: grep -r "claude-" . --include="*.py" | grep -v ".pyc"
  - Verify all model strings exist at https://docs.anthropic.com/en/docs/about-claude/models
  - Note: claude-haiku-4-5-20251001 and claude-sonnet-4-6 — verify these are current
  - Flag any deprecated model strings

Write CONTEXT.md with all findings. Write PROGRESS.md Session 0.
DO NOT CHANGE ANY CODE IN PHASE 0.
```

---

## PHASE 1 — CRITICAL SECURITY & CORRECTNESS
### Fix what can break users or expose data

---

### P1-T1: Verify and Write RLS Policies

```
CLAUDE CODE INSTRUCTIONS — P1-T1

PREREQUISITE: Phase 0 audit complete. Check CONTEXT.md "## RLS Policy Status".
If all policies are confirmed written and tested, SKIP this task and note it.

CONTEXT: Read the existing migration SQL file before writing anything.
Read: sentio-api/db/migration_phase6.sql
Understand the exact table names and user_id column names used.

TASK: Write explicit RLS policies for all user-scoped tables.

For each table that lacks an explicit policy, write:

-- journal_entries
ALTER TABLE journal_entries ENABLE ROW LEVEL SECURITY;
CREATE POLICY "user_own_journal" ON journal_entries
  FOR ALL USING (auth.uid() = user_id);

-- user_bias_profiles
ALTER TABLE user_bias_profiles ENABLE ROW LEVEL SECURITY;
CREATE POLICY "user_own_bias_profile" ON user_bias_profiles
  FOR ALL USING (auth.uid() = user_id);

-- assessment_submissions
ALTER TABLE assessment_submissions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "user_own_assessments" ON assessment_submissions
  FOR ALL USING (auth.uid() = user_id);

-- socratic_sessions
ALTER TABLE socratic_sessions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "user_own_sessions" ON socratic_sessions
  FOR ALL USING (auth.uid() = user_id);

-- notifications
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
CREATE POLICY "user_own_notifications" ON notifications
  FOR ALL USING (auth.uid() = user_id);

-- user_badges
ALTER TABLE user_badges ENABLE ROW LEVEL SECURITY;
CREATE POLICY "user_own_badges" ON user_badges
  FOR ALL USING (auth.uid() = user_id);

Save to: sentio-api/db/migration_rls_policies.sql

VERIFY: Run these in Supabase SQL Editor.
Test: Log in as user A, try to fetch user B's journal entries via Supabase JS client.
Should return empty array (not user B's data).
Document test result in PROGRESS.md.

Update CONTEXT.md: change each table from [RLS-ENABLED-NO-POLICY] to [RLS-POLICY-EXISTS].
```

---

### P1-T2: Standardize Safety Gate Across All Endpoints

```
CLAUDE CODE INSTRUCTIONS — P1-T2

PREREQUISITE: Phase 0 audit showing which endpoints are missing the safety gate.
Read: sentio-api/services/safety.py FULLY before touching anything.

TASK: Every endpoint that accepts user-generated text must run safety.check_input().

Current state (from audit):
- /ai/chat: has crisis gate ✅
- /socratic/chat: has crisis gate ✅
- /journal (create): has crisis gate ✅
- /assessments, /biases: NO crisis gate (low risk, no free text — likely fine)
- /community (thread/reply creation): CHECK if it has gate — add if missing

For the output filter (regex scan of streamed chunks):
Read the actual SSE streaming code in claude_service.py.
If the output filter is just a comment or is called but the regex is incomplete:

Implement in sentio-api/services/safety.py:

CLINICAL_OVERREACH_PATTERNS = [
    r'\bdiagnos\w*\b',
    r'\bdisorder\b',
    r'\billness\b',
    r'\bmedication\b',
    r'\bprescri\w*\b',
    r'\btherapist says\b',
    r'\byou have\s+\w+\s+(disorder|condition|syndrome)\b',
]

def filter_clinical_overreach(chunk: str) -> tuple[str, bool]:
    """Returns (safe_chunk, was_filtered). Drops whole chunk if pattern matches."""
    for pattern in CLINICAL_OVERREACH_PATTERNS:
        if re.search(pattern, chunk, re.IGNORECASE):
            return "", True
    return chunk, False

Ensure this runs on EVERY chunk in both /ai/chat and /socratic/chat SSE paths.

VERIFY:
- Send a message to /ai/chat that would plausibly trigger "you have anxiety disorder"
- Confirm the chunk containing that phrase is dropped
- Confirm the stream continues (not killed)
Document the test in PROGRESS.md.
```

---

### P1-T3: Verify and Fix Model Names

```
CLAUDE CODE INSTRUCTIONS — P1-T3

PREREQUISITE: Phase 0 grep of all model strings.

TASK: Verify every Claude model string used in the codebase is current.

1. Fetch current model list: https://docs.anthropic.com/en/docs/about-claude/models
   (use web_search or browser — do not assume from memory)

2. For each model string found:
   - claude-haiku-4-5-20251001 → verify this is the correct identifier
   - claude-sonnet-4-6 → verify this is correct
   - Any others found in grep

3. If a model string is deprecated or incorrect:
   - Update sentio-api/services/claude_service.py
   - Update any hardcoded references
   - Update .env.example with the correct default

4. Update CONTEXT.md "## Tech Stack" with verified model names.

RULE: Do not change model names based on memory. Only change based on
verified current Anthropic documentation.
```

---

## PHASE 2 — EPISTEME ALGORITHM INTEGRATION
### The flagship feature — make it actually work end-to-end

---

### P2-T1: Audit What the Algorithms Actually Do

```
CLAUDE CODE INSTRUCTIONS — P2-T1

PREREQUISITE: Phase 0 audit of episteme status.

TASK: Read src/lib/episteme/algorithms.ts fully. For each of the 7 algorithms,
determine its current state with precision.

For each algorithm, answer:
1. Is the TypeScript implementation complete? (not just a class stub)
2. Does it export a function/class that can be called?
3. What does it return? (what data structure)
4. Is it imported anywhere in the Vue frontend?
5. If imported, is its output used to enrich the API payload to /socratic/chat?

Read: src/pages/AIGuide.vue or wherever Socratic chat is handled
Read: src/lib/episteme/types.ts for the data structures

Write in PROGRESS.md Session [N]:
Algorithm Audit Results:
- RDSE: [TS-COMPLETE/TS-STUB] | [IMPORTED-IN-VUE/NOT-IMPORTED] | [WIRED-TO-BACKEND/NOT-WIRED]
- SDSM: [same]
- CBKT-CS: [same]
- BGDC: [same]
- CPGAB: [same]
- EGP: [same]
- SM-2: [same]

Current backend usage: Does /socratic/chat receive any algorithm signals from frontend?
Read the request body schema in socratic.py → SocraticChatRequest
Does it have fields for clarity_score, dialogue_state, bloom_depth, etc.?

This is audit only. No code changes. But this determines all subsequent P2 tasks.
```

---

### P2-T2: Wire Algorithm Signals to Backend (if not already done)

```
CLAUDE CODE INSTRUCTIONS — P2-T2

PREREQUISITE: P2-T1 complete. Read its findings in PROGRESS.md.
If algorithms are already wired to backend, verify end-to-end and SKIP to P2-T3.

SCENARIO A: Algorithms are implemented in TS but not sent to backend.
SCENARIO B: Algorithms are stubs — need implementation first.
SCENARIO C: Fully working — just verify.

For SCENARIO A (most likely based on audit):

STEP 1 — Extend the API request payload:
In sentio-api/routers/socratic.py, extend SocraticChatRequest:

class AlgorithmSignals(BaseModel):
    clarity_score: float | None = None        # from CBKT-CS P(learned)
    dialogue_state: str | None = None          # from SDSM: PROBE/DEEPEN/etc.
    bloom_depth: str | None = None             # from BGDC: Remember/Apply/etc.
    reasoning_depth_score: float | None = None # from RDSE
    session_progress: float | None = None      # from EGP: 0.0-1.0
    knowledge_gaps: list[str] | None = None    # from CPGAB

class SocraticChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    algorithm_signals: AlgorithmSignals | None = None  # ADD THIS

STEP 2 — Use signals in Claude prompt:
In sentio-api/services/claude_service.py, in the Socratic system prompt builder:

If algorithm_signals is present, inject:
"""
Current session state (computed client-side):
- Dialogue phase: {signals.dialogue_state or 'PROBE'}
- Learner mastery: {signals.clarity_score:.0%} confidence
- Response depth: {signals.bloom_depth or 'Remember'}
- Session progress: {signals.session_progress:.0%}
- Concepts to address: {', '.join(signals.knowledge_gaps) if signals.knowledge_gaps else 'none identified'}

Adjust your question to match this state. If dialogue_state is CONSOLIDATE,
help the learner summarize what they've understood.
"""

STEP 3 — Send signals from frontend:
In the Vue component that handles /socratic/chat API call:
After each user message, run all 7 algorithms on the response.
Include their output in the request body as algorithm_signals.

VERIFY:
1. Type a message in Socratic mode
2. Check browser Network tab → payload to /socratic/chat
   Should show algorithm_signals with real computed values (not null)
3. Check the Claude prompt being constructed in backend logs
   Should show the injected signal block

Document: "Algorithms wired on [date]. Signals verified non-null for: [which ones]"

For SCENARIO B (algorithms are stubs):
→ See DELEGATION TASK A below (use Gemini/Qwen to implement specific algorithms)
```

---

### P2-T3: Socratic Insight Cards — Complete Export Feature

```
CLAUDE CODE INSTRUCTIONS — P2-T3

PREREQUISITE: Read the existing insight card generation code in claude_service.py.
Read the frontend component that displays insight cards.
Determine what "Markdown, PDF, clipboard" export currently does.

TASK: Complete the insight card export feature.

1. Markdown export:
   - If not implemented: add a "Copy Markdown" button
   - Content: session summary, clarity score, key concepts covered, SM-2 schedule
   - Copy to clipboard via navigator.clipboard.writeText()

2. Clipboard export:
   - Plain text version of the insight card
   - Same button pattern as Markdown but formatted for plain text

3. PDF export:
   - Use the browser's window.print() with print-specific CSS (simplest approach)
   - OR use jsPDF (npm package, no server needed)
   - Add @media print CSS to the insight card component
   - This is the hardest of the three — if time-constrained, label as v2

If all three already work: verify them, document that they work, done.
If Markdown and clipboard work but PDF doesn't: implement PDF via print CSS.

VERIFY: Complete a Socratic session → click each export button → confirm output.
Document what works in PROGRESS.md.
```

---

## PHASE 3 — JOURNAL NLP: MAKE SENTIMENT REAL

```
CLAUDE CODE INSTRUCTIONS — PHASE 3

PREREQUISITE: Phase 0 audit of journal_nlp.py confirmed sentiment is always 0.0.
Read: sentio-api/services/journal_nlp.py fully before any changes.

PROBLEM: journal_entries.sentiment column is always 0.0 or None.
All downstream visualizations (progress page sentiment trend) are broken.

APPROACH: Two-tier implementation.

TIER 1 — Local fallback (must work without any external API):
Use VADER (already in requirements? check — if not, add: pip install vaderSentiment)
VADER is rule-based, no ML runtime, runs on CPU, gives -1 to +1 score.

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
_vader = SentimentIntensityAnalyzer()

def compute_sentiment_local(text: str) -> float:
    """Returns compound score -1 (negative) to +1 (positive)"""
    scores = _vader.polarity_scores(text)
    return round(scores['compound'], 3)

TIER 2 — Optional HF endpoint (if configured):
If HF_NLP_ENDPOINT env var is set, POST text to that endpoint.
Expect response: {"sentiment": float, "emotions": [str], "themes": [str]}
If call fails or times out (>3s), fall back to VADER silently.

Integration:
In the APScheduler background task (_process_entry in journal.py):
After bias classification runs, compute sentiment and update the row:
await supabase.from_("journal_entries").update({
    "sentiment": compute_sentiment(entry_text),
    "themes": extract_themes(entry_text)  # keyword extraction
}).eq("id", entry_id)

VERIFY:
1. Save a journal entry with clearly positive text ("Today was wonderful, everything went great")
2. Save another with clearly negative text ("Everything is terrible, I failed completely")
3. Check DB: journal_entries → sentiment column
   Positive text should be > 0.3, negative should be < -0.3
4. Check Progress page: sentiment trend should now show real data

Document actual sentiment values from test in PROGRESS.md.
Add to requirements.txt: vaderSentiment>=3.3.2
```

---

## PHASE 4 — WEEKLY INSIGHTS: REAL CLAUDE SYNTHESIS

```
CLAUDE CODE INSTRUCTIONS — PHASE 4

PREREQUISITE: Read sentio-api/routers/insights.py fully.
Determine: are insights actually Claude-synthesized or just templated strings?

IF TEMPLATED (likely):

Current behavior: returns formatted strings like "You wrote N entries this week"
Target behavior: Claude synthesizes a real insight from actual user data.

STEP 1 — Gather real data for synthesis:
In the /insights/weekly endpoint, query:
- Last 7 days of journal entries: count, themes, detected biases, sentiment scores
- Assessment scores (if any in last 30 days)
- Socratic session count and average clarity score (if any)
- Top 3 recurring biases across the week

STEP 2 — Build a synthesis prompt:
synthesis_prompt = f"""
You are analyzing one week of cognitive clarity work for a user.
Based on the following data, write 3 specific, personalized insights.

This week's data:
- Journal entries: {entry_count} entries
- Average sentiment: {avg_sentiment:.2f} (range: -1 negative to +1 positive)
- Recurring themes: {', '.join(top_themes[:5])}
- Most detected biases: {', '.join(top_biases[:3])}
- Socratic sessions completed: {session_count}
- Average clarity score: {avg_clarity:.1%}

Write exactly 3 insights. Each insight must:
1. Reference a specific data point (not generic)
2. Name a pattern the user may not have noticed
3. End with one actionable question for the user to reflect on

Format: JSON array of {{"type": str, "text": str, "icon": str}}
Do not include clinical terms, diagnoses, or treatment recommendations.
"""

STEP 3 — Call Claude with this prompt (haiku for cost efficiency).
Parse the JSON response. Return it.

CACHE: Cache the result per user per week (key: user_id + ISO week number).
Do not call Claude again if cached result exists.

VERIFY:
1. Hit /insights/weekly as a user with 3+ journal entries
2. Response should contain insights that reference actual themes from those entries
3. Two different users should get different insights
Document sample insight text in PROGRESS.md (verify it's specific, not generic).
```

---

## PHASE 5 — ARCHETYPE MODEL: HONEST IMPLEMENTATION

```
CLAUDE CODE INSTRUCTIONS — PHASE 5

PREREQUISITE: Read the current archetype computation in badge_engine.py or wherever it lives.
Confirm: it's currently top-bias-renamed, not UMAP clustering.

DECISION POINT (read this carefully):

OPTION A — Keep rule-based but describe it accurately (RECOMMENDED for now):
  - The current approach is: find top-scoring bias → map to archetype name
  - This is legitimate and defensible — just describe it honestly
  - Update all docs: "Bias-based archetype mapping: your dominant bias pattern
    determines your archetype. Future: clustering-based archetypes in v2."
  - Add more nuance: if top 2 biases are close in score (<5 points difference),
    use the combination to determine a "blend" archetype
  - This takes 2 hours and is honest

OPTION B — Implement basic clustering (if time allows, 8-12 hours):
  - Requires: 50+ users with bias_scores data in the DB
  - If you have that data: use scikit-learn KMeans (not UMAP — simpler, more stable)
  - n_clusters = 5 (one per "archetype family")
  - Retrain weekly on all user bias_scores
  - This is real ML, defensible in an interview

For now: DO OPTION A immediately.
OPTION B: create a ticket in PROGRESS.md as "Future: v2 clustering archetypes".

For OPTION A:
1. Read the current _ARCHETYPE_MAP and _compute_archetype function
2. Add blend logic: if top_score - second_score < 5:
   archetype = f"{_ARCHETYPE_MAP[top1]} with {_ARCHETYPE_MAP[top2]} tendencies"
3. Update README: remove any claim of "UMAP clustering"
   Replace with: "Bias-pattern archetype mapping"
4. Update CONTEXT.md

VERIFY: Submit an assessment → check that archetype appears in profile.
Document in PROGRESS.md.
```

---

## PHASE 6 — THERAPIST DIRECTORY: HONEST & FUNCTIONAL

```
CLAUDE CODE INSTRUCTIONS — PHASE 6

PREREQUISITE: Read sentio-api/routers/therapists.py fully.
Determine: are therapists hardcoded or from DB?

CURRENT STATE (from audit): 20 hardcoded demo therapists, no real booking notification.

TASKS:

TASK A — Add honest labeling (30 minutes):
  In the therapist directory UI, add a banner:
  "This is a curated demo directory. Real therapist onboarding coming in v2.
   To be listed, email [contact address]."
  This is honest and takes 30 minutes.

TASK B — Make booking send an email (2 hours, if Resend is configured):
  Read sentio-api/services/email_service.py
  When POST /therapists/{id}/book is called:
  1. Record the booking request in a new DB table booking_requests
     {id, user_id, therapist_id, preferred_time, notes, created_at, status}
  2. Send confirmation email to the user via Resend:
     "Your request to connect with [therapist name] has been received.
      They will contact you at [user email] within 2 business days."
  3. If therapist has a real email in the DB, send notification there too.

Schema for booking_requests:
CREATE TABLE booking_requests (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES auth.users(id),
  therapist_id uuid,
  preferred_time text,
  notes text,
  created_at timestamptz DEFAULT now(),
  status text DEFAULT 'pending'
);
ALTER TABLE booking_requests ENABLE ROW LEVEL SECURITY;
CREATE POLICY "user_own_bookings" ON booking_requests
  FOR ALL USING (auth.uid() = user_id);

VERIFY: Submit a booking request → check DB for the row → verify email arrives.
```

---

## PHASE 7 — FRONTEND QUALITY
### TypeScript, error handling, testing

---

### P7-T1: Fix Event Listener Memory Leaks

```
CLAUDE CODE INSTRUCTIONS — P7-T1

Search for all addEventListener calls in the frontend:
grep -r "addEventListener" src/ --include="*.vue" --include="*.js" --include="*.ts"

For each one, verify there is a corresponding removeEventListener in onUnmounted().

Common pattern that's wrong:
onMounted(() => {
  document.addEventListener('keydown', handler)
})
// Missing: onUnmounted(() => document.removeEventListener('keydown', handler))

Fix all instances. This is especially important in:
- The journal editor (keyboard shortcuts: Ctrl+B, Ctrl+I, Tab)
- Any live bias detection listeners
- SSE EventSource cleanup (must call eventSource.close() on unmount)

VERIFY: Open a page, navigate away, open another. Check browser memory profiler
(DevTools → Memory → Record) — no growing listener count.
```

---

### P7-T2: Add Proper Error States to All Data-Fetching Components

```
CLAUDE CODE INSTRUCTIONS — P7-T2

PREREQUISITE: Read each page component that fetches API data.

For each data-fetching component, ensure it has:
1. Loading state (skeleton or spinner)
2. Error state with user-friendly message and retry button
3. Empty state with actionable prompt (not just blank)

The Sentio design system uses --plum, --lavender, --slate CSS tokens.
Error states should use a red-tinted card (match existing error styling in main.css).

Pattern to implement in each store action:
state.loading = true
state.error = null
try {
  const data = await api.get('/endpoint')
  state.data = data
} catch (e) {
  state.error = e.response?.data?.detail || 'Something went wrong. Try refreshing.'
} finally {
  state.loading = false
}

In the Vue component:
<div v-if="store.loading" class="skeleton-card" />
<div v-else-if="store.error" class="error-state">
  {{ store.error }}
  <button @click="store.fetch()">Try again</button>
</div>
<div v-else-if="!store.data?.length" class="empty-state">
  [actionable empty state message]
</div>
<div v-else>
  [normal content]
</div>

Priority pages: Dashboard, Journal Index, Progress, AIGuide, Assessments.
```

---

### P7-T3: Add Basic Test Coverage

```
CLAUDE CODE INSTRUCTIONS — P7-T3

BACKEND — Add pytest tests for the most critical paths:

File: sentio-api/tests/test_safety.py
- test that crisis keywords trigger 422 response
- test that safe messages pass through
- test that output filter drops clinical overreach chunks
- test that non-clinical chunks pass through unchanged

File: sentio-api/tests/test_bias_classifier.py
- test that classify_biases returns valid bias_ids from the 15-class taxonomy
- test that confidence scores are 0.0-1.0
- test empty input handling

File: sentio-api/tests/test_journal_nlp.py
- test that positive text returns sentiment > 0
- test that negative text returns sentiment < 0
- test that VADER fallback works without HF endpoint

Run: pytest sentio-api/tests/ -v
Target: all tests pass. Fix any failures before moving on.

FRONTEND — Add Vitest for one critical component:
File: src/tests/safety.test.js
- test that crisis detection in the frontend (if any) works

Setup: npm install -D vitest @vue/test-utils
Add to package.json scripts: "test": "vitest run"

VERIFY: pytest passes, vitest passes. Document in PROGRESS.md.
```

---

## PHASE 8 — PERFORMANCE & RATE LIMITING

```
CLAUDE CODE INSTRUCTIONS — PHASE 8

TASK A — Rate limiting on Claude API endpoints:

Install: pip install slowapi
Add to requirements.txt.

In sentio-api/main.py:
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

In /ai/chat: @limiter.limit("30/minute")
In /socratic/chat: @limiter.limit("20/minute")
In /journal (create): @limiter.limit("10/minute")

TASK B — Verify caching is working:

The README says _USER_CTX_CACHE has 5-min TTL in ai.py.
Verify: make 3 rapid /ai/chat calls → check logs → only 1 DB query for context.
If cache isn't working: debug the TTL logic.

TASK C — Add Cohere fallback verification:

Start the backend WITHOUT COHERE_API_KEY set.
Send a message to /ai/chat.
Verify: RAG still returns results (pgvector match without reranking).
Verify: No exception is raised.
Document: "Cohere degradation tested [date]: [works/fails]"
```

---

## PHASE 9 — DOCUMENTATION TRUTHFULNESS

```
CLAUDE CODE INSTRUCTIONS — PHASE 9

This phase is about making README.md and all docs match reality exactly.

STEP 1 — Audit every claim in README.md against CONTEXT.md (which now has verified state).

For each claimed feature, mark it as one of:
[IMPLEMENTED-VERIFIED] — works, tested, confirmed
[IMPLEMENTED-PARTIAL] — works but with limitations
[DEMO-ONLY] — works but with demo data
[PLANNED-V2] — not implemented, honest future work

STEP 2 — Update README.md sections:

Models & ML table: update to reflect actual state.
After this phase, this table must be 100% accurate.

Therapist Directory: add note "(demo directory — real onboarding in v2)"

Insight cards: if PDF not implemented, change to "(Markdown · clipboard — PDF in v2)"

STEP 3 — Update Architecture diagram if any routes changed.

STEP 4 — Add a "What's Real, What's Coming" section to README:
"""
## Implementation Status

### Fully implemented and live
- AI Guide with RAG context injection
- Socratic mode with [N of 7] algorithms wired
- Journal with live bias detection and sentiment analysis
- Cognitive assessments with bias profile blending
- Safety gate (input + output)
- Community forum

### Implemented with demo data
- Therapist directory (real therapists onboarding in v2)

### Planned for v2
- Archetype clustering (currently rule-based)
- PDF insight card export
- Fine-tuned bias classifier
"""

This section is honest and actually impressive — it shows engineering maturity.
```

---

## MULTI-AI DELEGATION TASKS

### WHAT CLAUDE CODE MANAGES vs. WHAT GETS DELEGATED

```
Claude Code manages:
- All files in the Sentio repo
- Integration of any delegated output
- CONTEXT.md and PROGRESS.md always
- Test execution and verification
- Final judgment on what gets merged

Delegated to other AIs:
- Complex TypeScript algorithm implementation (if stubs need filling) → Gemini/Qwen
- Training data generation for future fine-tuning → Gemini
- ML architecture research → Qwen / DeepSeek-R1
- Clinical text review → Gemini 1.5 Pro (long context)

RULE: Every delegated output is read fully by Claude Code before integration.
Never blindly paste. Every integration gets its own PROGRESS.md entry.
```

---

### DELEGATION A — FOR GEMINI 2.0 PRO
#### Fill any stub Socratic algorithms in TypeScript

```
PROMPT TO SEND TO GEMINI (only if Phase 0 audit shows algorithm stubs):

Context: I have a cognitive bias awareness app called Sentio. I have a file
src/lib/episteme/algorithms.ts containing 7 Socratic dialogue algorithms.
Some are stubs. I need you to implement the following [LIST WHICH ONES ARE STUBS
FROM YOUR PHASE 0 AUDIT].

The algorithms must be:
1. Pure TypeScript — no external dependencies
2. Self-contained — each is a class with clear input/output types
3. Stateful — they maintain session state across dialogue turns

[PASTE the types.ts file here so Gemini knows the types]
[PASTE the current stub implementations so Gemini continues them]

For each stub, implement:
- The full algorithm logic as described in the comments
- A reset() method to clear session state
- An update(userMessage: string, aiResponse: string) method that updates state
- A getSignals() method that returns the current computed values for backend injection

Output: complete TypeScript for the stubbed algorithms only. Do not rewrite
working algorithms. Use the exact same class names and interface.

WHAT CLAUDE CODE DOES WITH THIS:
1. Read the output carefully — does the logic match the algorithm description?
2. Replace the stub implementations in algorithms.ts
3. Run: npm run build → should compile without errors
4. Test in browser: complete a Socratic turn → check that algorithm state updates
5. Verify signals are non-null and reasonable
6. Document in PROGRESS.md: "Gemini-completed algorithms: [list]. Verified [date]."
```

---

### DELEGATION B — FOR QWEN2.5 / DEEPSEEK-R1
#### Research: Is Claude Haiku zero-shot for bias classification good enough?

```
PROMPT TO SEND TO QWEN OR DEEPSEEK:

I have a system that uses Claude Haiku to classify text into 15 cognitive bias
categories. The prompt is a zero-shot taxonomy classification. It costs ~$0.0002
per journal entry.

I want to know:
1. At what scale (daily active users) does this become expensive?
   Assume average user writes 3 journal entries/day, each 300 words.

2. What would a local alternative look like?
   I want a model that runs on CPU (my HF Space has no GPU) and classifies
   text into 15 classes. Suggest: the model, library, fine-tuning approach.

3. How many labeled examples do I need to fine-tune a DistilBERT-style model
   to match Claude Haiku's zero-shot performance on this task?

4. Given my 15-class taxonomy, generate 30 labeled training examples
   (text, bias_label) as JSONL. Each example should be 50-200 words of
   realistic journal entry text that exhibits the named bias.
   Use these class names: [paste the 15 bias names from README]

Output:
- Cost analysis (as a table)
- Architecture recommendation
- Training data estimate
- 30 JSONL examples

WHAT CLAUDE CODE DOES:
1. Save the 30 examples to data/training/bias_labels_seed.jsonl
2. Validate: each has {text, label} where label is one of the 15 valid classes
3. Document in CONTEXT.md under "## ML Models":
   "Seed training data: 30 examples generated by Qwen [date].
    Synthetic — not from real users. To be expanded with real user feedback."
4. Use this as the seed for future fine-tuning (Phase 10)
```

---

### DELEGATION C — FOR GEMINI 1.5 PRO (long context)
#### Generate synthetic bias training data at scale

```
PROMPT TO SEND TO GEMINI:

I need synthetic training data for a cognitive bias text classifier.
Generate 200 journal entry text examples, labeled with one of these 15 biases:

confirmation_bias, attribution_error, all_or_nothing, catastrophizing,
mind_reading, overgeneralization, emotional_reasoning, should_statements,
labeling, personalization, availability_bias, anchoring_bias, dunning_kruger,
sunk_cost_fallacy, fundamental_attribution

Requirements:
- 13-14 examples per class (balanced)
- Text: 80-250 words, realistic journal entry style, first person
- The bias must be naturally embedded in the text — not stated explicitly
- Diverse contexts: career, relationships, studies, health, money
- Indian cultural context where appropriate (India is the primary market)

Output: JSONL format, one object per line:
{"text": "...", "label": "confirmation_bias", "context": "career"}
No markdown fences. No preamble. Just the JSONL.

WHAT CLAUDE CODE DOES:
1. Save to data/training/bias_training_synthetic_v1.jsonl
2. Validate: wc -l (should be 200), check all labels are valid
3. Sample 20 random examples, read them for quality
4. Run a quick Claude Haiku classification on 10 examples:
   do Claude's predictions match the labels?
   If agreement > 70%, the data is high quality.
5. Document quality check in PROGRESS.md:
   "Synthetic data quality: [N]/10 matches Claude Haiku predictions.
    Assessment: [high/medium/low quality]. Use for fine-tuning: [Y/N]"
```

---

## FINE-TUNING PLAN (Phase 10 — When Data Ready)

```
WHEN TO START: Only after collecting at least 150 high-quality labeled examples
(mix of synthetic and real user-corrected labels). Minimum threshold: not before.

APPROACH: LoRA fine-tuning on a small open model (not Claude — not available for fine-tuning)

Recommended model: distilbert-base-uncased (67M params, fast, CPU-friendly)
Task: 15-class sequence classification
Library: HuggingFace transformers + PEFT

Why DistilBERT and not something larger:
- Must run on HF Spaces CPU container (2 vCPU, 16GB RAM)
- Inference must be <100ms per entry (background task, but still)
- 15-class classification doesn't need a large model
- DistilBERT fine-tuned on 200+ examples will likely match Claude Haiku zero-shot
  for this specific taxonomy

File: scripts/train_bias_classifier.py (already referenced in repo — complete it)

Steps:
1. from transformers import DistilBertForSequenceClassification, Trainer, TrainingArguments
2. label2id = {bias: i for i, bias in enumerate(BIAS_CLASSES)}
3. Tokenize data: max_length=256
4. Train: 3 epochs, lr=2e-5, batch_size=16
5. Evaluate: accuracy, per-class F1 (some biases are harder than others)
6. Save: model.save_pretrained("sentio-api/models/bias_classifier_v1/")
7. In bias_classifier.py: load local model first, fall back to Claude Haiku if unavailable

WHAT TO CLAIM AFTER THIS:
"Bias classifier: DistilBERT fine-tuned on [N] labeled examples
 (synthetic + user-corrected). Deployed locally in the FastAPI service.
 Claude Haiku used as fallback during model loading.
 Validation accuracy: [actual number]%"

WHAT NOT TO CLAIM:
- Do not say "trained on 750 examples" if you have 200
- Do not say "active learning feedback loop" until you implement the loop
- Report actual validation accuracy — do not round up
```

---

## SESSION PROTOCOL

### Start of every session:
```
1. cat docs/CONTEXT.md
2. tail -100 docs/PROGRESS.md
3. Note "Next session: start with" from last entry
4. cat [the specific files you'll modify today]
5. Then start work
```

### End of every session:
```
1. pytest sentio-api/tests/ -v  (if tests exist)
2. npm run build  (confirm frontend still compiles)
3. Update docs/CONTEXT.md for any changes
4. Write docs/PROGRESS.md entry
5. git add docs/ && git commit -m "docs: session [N] context + progress update"
6. git add [changed files] && git commit -m "[phase]-[task]: [what and why]"
```

### When blocked:
```
Write in PROGRESS.md:
## BLOCKED — [date]
File: [which file caused the block]
Expected: [what you thought was there]
Actual: [what you found]
Question: [specific question]
Options: [A vs B]
Recommendation: [which seems better]
STOP. Do not guess. Next session starts by resolving this block.
```

---

## QUICK REFERENCE: ISSUE → PHASE MAPPING

| Issue from Audit | Phase | Priority |
|---|---|---|
| RLS policies not written | P1-T1 | CRITICAL |
| Safety gate incomplete | P1-T2 | CRITICAL |
| Model names may be outdated | P1-T3 | HIGH |
| Episteme algorithms not wired | P2-T1/T2 | HIGH |
| Insight card PDF/clipboard | P2-T3 | MEDIUM |
| Sentiment always 0.0 | Phase 3 | HIGH |
| Weekly insights templated | Phase 4 | MEDIUM |
| Archetype not ML-based | Phase 5 | MEDIUM |
| Therapist booking silent | Phase 6 | MEDIUM |
| Event listener memory leaks | P7-T1 | HIGH |
| Error states missing | P7-T2 | MEDIUM |
| No tests | P7-T3 | MEDIUM |
| No rate limiting | Phase 8 | MEDIUM |
| README overclaims | Phase 9 | HIGH |

---

## WHAT THE README NOW CORRECTLY CLAIMS (good baseline)

These things are accurate in the current README. Do not break them.
Protect them when refactoring:
- Claude Haiku zero-shot bias classifier ✅
- sentence-transformers all-MiniLM-L6-v2 for embeddings ✅
- pgvector cosine similarity + optional Cohere rerank ✅
- APScheduler background tasks for journal analysis ✅
- SSE streaming for both guide and socratic chat ✅
- 5-min user context cache ✅
- Prompt caching for bias taxonomy ✅
- Crisis gate with India-specific helplines ✅
- Vue 3 + Pinia + Vue Router 4 ✅
- Supabase auth (email + Google OAuth) ✅

---

*This master prompt is calibrated to the actual README and critical audit findings
as of May 2026. Update CONTEXT.md as the project evolves — this file is a
starting point, not a perpetual source of truth.*
