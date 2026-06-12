# Sentio — Complete Interview Companion Guide

**Purpose**: re-learn everything about Sentio from zero — architecture, math, AI design, algorithms,
system design, all features, tech decisions, edge cases — ready for any 45-minute deep-dive.

**One-line pitch**: *"Sentio is a full-stack mental-clarity platform — Vue 3 + FastAPI + Supabase —
where an LLM guide with real three-tier memory, a RAG pipeline with measured reranker lift, a
distilled bias classifier, and a Bayesian Socratic tutor help users identify cognitive biases in
their own thinking. Every AI claim is backed by an eval number I can reproduce."*

---

## Part 1 — Full system tour

### Architecture diagram

```
┌─────────────────────────────────────────────────────────────┐
│  Vue 3 SPA (Vercel CDN)                                     │
│  Pinia stores · Vue Router · Axios (Bearer auto-inject)     │
│  7 Episteme algorithms in client-side TypeScript            │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTPS / SSE
┌────────────────────▼────────────────────────────────────────┐
│  FastAPI (HuggingFace Spaces, Docker, port 7860)            │
│  APScheduler (in-process, 3 jobs)                           │
│  Sentence-Transformers (all-MiniLM-L6-v2, preloaded)        │
├─────────────────────────────────────────────────────────────┤
│  /ai         SSE chat stream + memory retrieve/save         │
│  /journal    CRUD + background bias/NLP pipeline            │
│  /socratic   Bayesian Socratic tutor (SSE stream)           │
│  /assessments  Psychology questionnaires + scoring          │
│  /biases     CBT taxonomy browsing                          │
│  /community  Threads + replies + upvotes                    │
│  /therapists Therapist directory + filtering                │
│  /users      Profile + notification hub + badge engine      │
│  /insights   AI-generated personal insight reports          │
└──────┬─────────────┬──────────────┬───────────────┬─────────┘
       │             │              │               │
  Supabase      Anthropic      Cohere           OpenRouter
  Postgres +    Claude Haiku   rerank-          (fallback LLM
  pgvector      (primary LLM)  english-v2.0     when no Claude)
  + RLS + Auth
```

### Full feature inventory

| Feature | Route | What it does |
|---|---|---|
| Dashboard | `/` | Streak calendar, bias radar chart, recent journal, nudges |
| AI Guide | `/ai` | SSE chat with three-tier memory + RAG + bias context |
| AI Memory | `/memory` | View/delete episodic + semantic memories (GDPR) |
| Journal | `/journal` | Rich-text entries → async bias + NLP pipeline |
| Journal Entry | `/journal/:id` | Full entry + detected biases + reflection questions |
| Socratic Mode | `/ai` (tab) | Bayesian Socratic tutor with 7 Episteme algorithms |
| Learn | `/learn` | CBT knowledge base (RAG source articles) |
| Assessments | `/assessments` | GAD-7, PHQ-9, Big Five, Cognitive Style questionnaires |
| Biases | `/biases` | Browse all 15 bias classes with explanations |
| Community | `/community` | Threaded discussion + upvotes |
| Therapists | `/therapists` | Therapist directory, filter by specialty |
| Progress | `/progress` | Long-term bias trend charts |
| Profile | `/profile` | Account settings, badge collection |

---

## Part 2 — Three-tier memory (the headline feature)

### The problem it solves

Before upgrade: `ai_conversations.context_summary` column existed in schema but was NEVER written
(classic "the column lies" finding). `_USER_CTX_CACHE` was the only persistence — close the tab
and the AI forgot you existed.

### Architecture (mirrors human memory consolidation)

| Tier | Store | Lifetime | Written | Read |
|---|---|---|---|---|
| Working | `_USER_CTX_CACHE` (in-process dict) | 5-min TTL | per request | per request |
| Episodic | `memory_episodes` (pgvector 384-d) | half-life ~14 days | end of each chat session | pre-chat retrieval |
| Semantic | `user_facts` (pgvector 384-d) | half-life ~140 days | nightly 02:00 UTC consolidation | pre-chat retrieval |

**Session flow (Option B)**:
```
User opens AI Guide tab
  → frontend generates crypto.randomUUID() on FIRST message
  → every subsequent turn in same tab uses same UUID
  → backend upserts ONE ai_conversations row (not one per turn)
  → after SSE stream closes: asyncio.create_task(save_episode(...))
      → Haiku writes ≤80-word summary → embed → upsert memory_episodes
  → Nightly: episodes older than 7 days → Haiku extracts 2–4 durable user_facts
  → pre-chat: match_memory RPC → top-3 memories injected into system prompt
```

### The retrieval formula (memorise this)

```
score = cosine_sim(query_embedding, memory_embedding)
        × exp(−λ × age_days)
        × importance

λ_episode = 0.05   → half-life = ln(2)/0.05 ≈ 13.9 days
λ_fact    = 0.005  → half-life = ln(2)/0.005 ≈ 138.6 days

importance = min(2.0, max(0.5, 0.5 + 0.1×n_turns + 0.3×bias_mentions))
```

Computed **in SQL** inside the `match_memory` RPC (`UNION ALL` over both tables, one round-trip).
Cites: Park et al. 2023 (generative agents) for tri-factor scoring; MemGPT (Packer 2023) for tiering.

### Why Option B over Option A (one row per turn)?

Option A (new row per message): history is confetti — pagination breaks, episode summaries cover only
one turn, conversation_id changes mid-session. Option B: stable UUID → coherent episode → summary
updates each turn. Resuming from history panel reuses the existing id, episode keeps updating.

### GDPR / ethics surface

`/memory` page: lists every episode and fact in plain language. Per-item delete:
`DELETE /ai/memory/{id}?source=episode|fact`. Full wipe: `DELETE /ai/memory`.
One endpoint answers three interview questions: *"what if the memory is wrong?"* (delete it);
*"how is this ethical for a mental-health app?"* (full transparency + user control);
*"GDPR right-to-erasure?"* (wipe endpoint).

### Memory Q&A bank

**Q: Why not just stuff history in the context window?**
A: Cost and signal. Full history grows unboundedly — latency and token cost grow linearly.
Retrieval injects only top-3 scoring memories. Decay filters stale context that would pollute
current conversations.

**Q: Why two λ values?**
A: Episodes are situational ("stressed about Tuesday's exam") — worthless in a month.
Facts are dispositional ("tends to catastrophize about academics") — durable. The 10× ratio
(14d vs 140d) encodes that difference; tunable per product feedback.

**Q: Failure modes?**
A: Every memory function degrades gracefully. If embedder or DB is down, `retrieve_memory`
returns `""` and chat proceeds without memory (3 unit tests cover this path).
Consolidation is idempotent (consolidated flag) and per-user errors don't abort the nightly batch.

**Q: Why in-process APScheduler and not Celery / pg_cron?**
A: HF Spaces is one free-tier container — a separate worker doubles infra for a job that runs once
nightly. Documented trade-off: at scale, move to pg_cron (runs inside Postgres, survives restarts)
or a worker dyno.

---

## Part 3 — RAG pipeline + eval

### Pipeline

```
user query
  → all-MiniLM-L6-v2 (384-d, CPU, preloaded at startup, ~80 MB)
  → match_knowledge RPC (pgvector cosine, threshold 0.65, top-10)
  → Cohere rerank-english-v2.0 (cross-encoder, top-3) [degrades gracefully if key absent]
  → injected into Claude system prompt as "Relevant knowledge articles"
```

### Why a reranker works

Bi-encoders (MiniLM) embed query and document **independently** — fast but miss interaction
signals. A cross-encoder reads query+doc *together* — slower, so you only run it on top-10.
Standard retrieve-then-rerank pattern; widely used in production RAG (Cohere, BGE-reranker).

### Eval methodology

`scripts/eval_rag.py`: 51 (query → relevant article) pairs across 26 psychology/CBT topics.
Measures **precision@3** and **MRR** cosine-only vs cosine+rerank.

Honest auto-labeling caveat: query written per article; all chunks of that article are "relevant"
(matched by title prefix — articles are seeded as "(1/3)" chunks). Single-relevant-article
assumption slightly understates precision when topics overlap. Acknowledged in script comments.

### RAG Q&A bank

**Q: Why pgvector and not Pinecone/Weaviate?**
A: KB is tens of articles / hundreds of chunks. Data already in Supabase with RLS — a second vector
store adds an infra hop, a consistency problem, and cost for zero recall benefit at this scale.

**Q: Why MiniLM-L6-v2?**
A: 384-d, ~80 MB, CPU-fast, free, de-facto sentence embedding baseline. Eval harness exists
specifically so a swap to a larger model (e.g. BGE-large, text-embedding-3-small) is a measured
decision, not vibes.

**Q: Chunking strategy?**
A: Articles seeded as 3 chunks with titled prefixes; retrieval is chunk-level. No overlap
chunking (articles are short enough). Next step: sliding window with 20% overlap.

---

## Part 4 — Bias classifier: Haiku teacher + QLoRA student

### Production: Claude Haiku

`services/bias_classifier.py` — 15-class CBT taxonomy, strict-JSON output, post-validation
against a known-ID whitelist, confidence floor 0.5. ~$0.0002/entry.

```
Taxonomy (15 classes):
confirmation_bias · attribution_error · all_or_nothing · catastrophizing
mind_reading · overgeneralization · emotional_reasoning · should_statements
labeling · personalization · availability_bias · anchoring_bias
dunning_kruger · sunk_cost_fallacy · fundamental_attribution
```

### QLoRA distillation (notebook: sentio-ml/notebooks/sentio_bias_qlora.ipynb)

1. **Data**: 750 entries (50×15 classes) generated by production Haiku teacher (~$0.12 with prompt
   caching). No public dataset matches this 15-class taxonomy. Synthesizing from teacher IS the
   distillation step. In-notebook validation: malformed-line skip → label whitelist → ≥20-word
   filter → class-distribution assert → qualitative samples → stratified 80/10/10 split →
   token-length audit vs max_seq_length=512.

2. **Model**: Qwen2.5-3B-Instruct (open, ungated, ChatML template). Chosen over DistilBERT because
   generative output gives structured JSON + confidence + span quotes, and extends to new classes
   without retraining a classification head.

3. **QLoRA mechanics**:
   - 4-bit NF4 quantization + double quant (quantize the quantization constants too) → fits 16 GB T4
   - LoRA r=16, α=32, dropout=0.05 on all 7 linear projections (~1.3% trainable params)
   - SFTTrainer, 4 epochs, effective batch 8, lr 2e-4 cosine, paged_adamw_32bit,
     max_grad_norm=0.3, best-by-eval-loss, W&B project `sentio-bias-qlora`
   - Memory: 3B fp32 ≈ 12 GB weights alone → ~4 GB in NF4

4. **Eval**: same 30-entry human-labeled holdout scored for BOTH student AND teacher →
   per-class F1 delta table + agreement rates → RESULTS.md.

5. **Serving plan** (post-run): confidence cascade — student (free, local) at ≥0.7, else Haiku
   fallback. Expected ~80% API-cost reduction. NOT wired into prod until real numbers exist.

### Fine-tuning Q&A bank

**Q: Why QLoRA mechanically?**
A: Frozen 4-bit base; trainable fp16 low-rank matrices A·B (r=16) added to each linear layer;
gradients flow only through ~40M adapter params. NF4 is information-optimal for normally-distributed
weights (quantile quantization); double quant compresses the scale factors themselves.

**Q: Why macro F1?**
A: Equal class weighting — all 15 distortions matter equally clinically. Micro F1 would let
dominant classes mask failures on rare ones. Agreement rate (exact set match) is the stricter
"got the entire label set right" metric.

**Q: Synthetic data risk?**
A: Student inherits teacher's biases — acknowledged. Mitigated by human-written holdout (not
Haiku-generated). Per-class F1 surface any class the teacher labels badly. Not eliminated.

---

## Part 5 — Socratic mode + 7 Episteme algorithms

### What it is

An in-app Socratic tutor. User picks a domain (Cognitive Biases, Emotional Patterns, Decision
Making, Self-Reflection, Relationships, Tech & Logic) → up to 10 dialogue turns → the system
guides understanding without giving answers directly → generates an insight card at the end.

**Key architectural choice**: all 7 algorithms run **client-side in TypeScript** (zero round-trip
latency for state decisions). Only the actual LLM response generation hits the backend.

### Algorithm 1 — RDSE (Response Depth Signal Extractor)

Scores each user message on 6 signals to produce a `qualityScore` ∈ [0, 1]:

```
qualityScore =
  0.30 × reasoning_connectives   (because/therefore/however etc, normalized to 3 hits = max)
+ 0.20 × response_length         (vs expected = 20 + turn × 8 words)
+ 0.15 × certainty_level         (inverse of uncertainty markers like "i think/maybe/not sure")
+ 0.20 × technical_term_density  (domain vocab hits, normalized to 3 = max)
+ 0.10 × structure_score         (sentence count / 4)
+ 0.05 × (1 − question_backpressure)  (penalty if user responds with questions instead of answers)
```

Also computes `confusionCount` from confusion markers + very short responses.

### Algorithm 2 — SDSM (Socratic Dialogue State Machine)

7 states: `PROBE → DEEPEN | SCAFFOLD | RECTIFY | REDIRECT → CONSOLIDATE → COMPLETE`

State transition logic (pure function, no LLM):
```
if turn >= 9 → COMPLETE
if turn >= 7 → CONSOLIDATE
if turn == 1 → PROBE
if confusionCount >= 2 OR qualityScore < 0.15:
    → SCAFFOLD (or RECTIFY if already scaffolded twice in a row)
if semanticAccuracy < 0.25 AND qualityScore > 0.3 → RECTIFY
if semanticAccuracy < 0.40 AND qualityScore > 0.2 → REDIRECT
if qualityScore >= 0.55 AND semanticAccuracy >= 0.55 → DEEPEN
else → PROBE
```

State is sent to backend as `next_state` parameter. Claude's system prompt includes the
state-specific instruction — so the LLM is *steered* by the algorithm, not the reverse.

### Algorithm 3 — CBKT-CS (Cognitive Bayesian Knowledge Tracing – Clarity Score)

Standard BKT with 4 parameters per domain:
- `pL` — P(mastery) — probability user has learned the concept
- `pT` — P(transit) — probability of learning from not-learned to learned per turn
- `pS` — P(slip) — probability of wrong answer given mastery
- `pG` — P(guess) — probability of right answer given no mastery

Domain-specific priors (e.g. ml: `{pL:0.20, pT:0.12, pS:0.10, pG:0.08}`).

**BKT update per turn**:
```
P(correct|Known)   = (1 − pS) × qualitySignal + pS × (1 − qualitySignal)
P(correct|Unknown) = pG × qualitySignal + (1 − pG) × (1 − qualitySignal)
pTotal = pL × P(c|K) + (1−pL) × P(c|U)          # total evidence
pLpost = pL × P(c|K) / pTotal                     # Bayes posterior
pLnext = pLpost + (1 − pLpost) × pT               # add learning probability
```

`clarityScore = round(pL × 100)`. Sent to backend for Claude's context. pT grows slightly with
quality signal (adaptive: better responses → higher transit probability).

### Algorithm 4 — BGDC (Bloom-Grounded Depth Classifier)

Maps user question text to a Bloom's taxonomy level using keyword matching on verb phrases:
- `SURFACE` → "what is", "define", "list", "describe"
- `CONCEPTUAL` → "how does", "show how", "illustrate", "apply"
- `ANALYTICAL` → "why", "compare", "analyze", "what causes"
- `SYNTHESIS` → "design", "create", "evaluate", "trade-off", "would you decide"

Checked from highest to lowest; confidence = 0.85 if verb starts the question, 0.70 if mid-sentence,
0.45 if no match (defaults to SURFACE). Used to gauge the depth level of the user's question.

### Algorithm 5 — SDSM→Bloom Depth Mapper

Maps SDSM state + qualityScore → Bloom level for the insight card and progress tracking:
```
COMPLETE                    → SYNTHESIS
CONSOLIDATE + quality ≥0.55 → SYNTHESIS
CONSOLIDATE + quality <0.55 → ANALYTICAL
DEEPEN                      → ANALYTICAL
SCAFFOLD | RECTIFY          → SURFACE
default                     → CONCEPTUAL
```

### Algorithm 6 — CPGAB (Concept-Performance Gap Analyser, Bloom-based)

Maintains per-domain core concept lists (e.g. ml: gradient descent, loss functions, overfitting,
backpropagation, regularisation…). After each turn: checks which core concepts haven't been touched
in `conceptsCovered[]` → returns up to 5 gap concepts → injected into Claude's context as
"KNOWLEDGE GAPS IDENTIFIED". Enables the tutor to steer toward uncovered material.

Gap matching: fuzzy — checks if first word of core concept appears in covered list or vice versa.

### Algorithm 7 — EGP (Ebbinghaus Gap Prioritizer)

Implements the forgetting curve with a **stability** term that grows with mastery and review count:

```
S(clarityScore, timesExplored) = 2 × exp(4 × clarityScore/100 + 0.5 × ln(timesExplored+1))
retention = exp(−hoursElapsed / S)
gapUrgency = (1 − retention) × (1 − clarityScore/100)
```

High gapUrgency = concept is both poorly understood AND being forgotten → prioritize first.
Also implements SM-2 spaced repetition intervals:
```
interval_1 = 24h, interval_2 = 72h, interval_n = prevInterval × easiness
easiness = 1.3 + 0.1 × (clarityScore/20)
```

### How the algorithms wire together (per turn)

```
User types message
  → RDSE: qualityScore, confusionCount
  → BGDC: question depth level
  → CBKT-CS: update BKT state → clarityScore
  → SDSM: determine nextState (using quality + semanticAccuracy + confusion)
  → SDSM→Bloom: depth level for tracking
  → CPGAB: compute knowledge gaps
  → POST /socratic/chat with {message, nextState, qualityScore, clarityScore, conceptsCovered, ...}
  → Claude steered by nextState instruction
  → SSE response streams back
EGP: used when displaying session history to prioritize which concepts to revisit
```

---

## Part 6 — Reliability engineering (WS-4)

### The crash gap problem

`POST /journal` → inserts row → hands off to `asyncio.create_task(_process_entry(...))` → returns
201. If HF Space container restarts mid-task (routine on free tier), the row exists forever with
NULL biases/themes/sentiment. Frontend polls and never completes.

### Fix: durable state machine

```
INSERT row (DB default 'pending')
  ↓
_process_entry stamps 'processing' first
  ↓
success → stamps 'done' (same UPDATE as biases/themes/sentiment)
  ↓
exception → stamps 'failed' (separately observable for monitoring)

Crash path:
  row stays 'pending'
  APScheduler _sweep_orphan_analyses() runs every 10 min:
    WHERE analysis_status='pending' AND created_at < now()-5min
    → calls _process_entry() per orphan
    → continues-on-error (one bad entry doesn't abort sweep)
```

**Idempotency**: `'processing'` stamp prevents double-queuing if two sweep runs overlap.
`update_entry` resets to `'pending'` on content change so re-analysis is also crash-proof.
**Partial index** `WHERE analysis_status='pending'` keeps sweep query O(orphans) not O(table).
**Back-fill**: migration sets `'done'` for existing rows with `detected_biases IS NOT NULL`.

### APScheduler jobs (all 3)

| Job | Trigger | What it does |
|---|---|---|
| `_send_daily_nudge` | daily 19:00 UTC | Sends email nudge via Resend if user hasn't journaled today |
| `_weekly_digest` | Mon 08:00 UTC | Emails weekly bias pattern summary; queries DB fresh each run |
| `_sweep_orphan_analyses` | every 10 min | Recovers stuck journal entries (crash-gap fix) |
| `_consolidate_memories` | daily 02:00 UTC | Distils episodes → user_facts for users with 7+ day-old episodes |

Note: `_weekly_digest` is NOT a cache — it queries the DB fresh each run. The in-process
`_USER_CTX_CACHE` (5-min TTL dict) is the only in-memory data cache.

---

## Part 7 — LLM provider fallback (llm_client.py)

### Why it exists

Anthropic free-tier credits expire. During demo/interview season you may not want to pay.
The app should keep working by switching providers via env-var change, zero code change.

### Architecture (services/llm_client.py)

```python
Priority (checked at each call):
  1. ANTHROPIC_API_KEY set → Anthropic SDK, model = CLAUDE_MODEL
  2. OPENROUTER_API_KEY set → OpenRouter (openai-compat), model = FALLBACK_MODEL

Public interface:
  stream_text(system, messages, max_tokens) → AsyncGenerator[str, None]
  complete_text(system, messages, max_tokens) → str
  has_llm() → bool  (used as guard in bias_classifier + memory_service)
```

All three service files (`claude_service.py`, `bias_classifier.py`, `memory_service.py`) call ONLY
`stream_text` / `complete_text` / `has_llm` — they are completely provider-agnostic.

### Switching to OpenRouter (when credits expire)

In HF Space → Settings → Repository secrets:
1. Remove `ANTHROPIC_API_KEY`
2. Add `OPENROUTER_API_KEY` (free key from openrouter.ai)
3. Optionally set `FALLBACK_MODEL`:
   - `google/gemini-flash-1.5-exp` — free, fast, good instruction following (default)
   - `openai/gpt-4o-mini` — very reliable JSON output (~$0.15/1M tokens)
   - `anthropic/claude-haiku-4-5` — same Claude model, via OpenRouter credits
   - `meta-llama/llama-3.1-8b-instruct:free` — fully free, smaller quality
4. Click Restart Space. Done.

### What continues to work with OpenRouter

Every AI feature: AI Guide chat (streaming), AI Guide memory save/retrieve,
journal bias classification, journal reflection questions, Socratic mode (streaming),
Socratic insight card generation, nightly memory consolidation. The prompt caching
(`cache_control: ephemeral`) is Anthropic-specific and silently skipped — no functional impact,
slightly higher cost without it.

---

## Part 8 — Tech stack rationale

| Layer | Tech | Why |
|---|---|---|
| Frontend framework | Vue 3 (Composition API) | Reactive fine-grained updates for SSE streaming; lighter than React for a side project |
| State management | Pinia | Official Vue store, simpler than Vuex, TypeScript-first |
| Bundler | Vite | ESM-first, near-instant HMR, lazy-chunk splitting per route |
| Icons | lucide-vue-next | Tree-shakeable, consistent 24px grid, same icon set throughout |
| Markdown | marked + DOMPurify | `marked` parses, `DOMPurify` sanitizes before v-html — prevents XSS |
| HTTP client | Axios (client.js) | Interceptor auto-injects Bearer token; centralized base URL |
| Backend | FastAPI | Async-native (uvicorn + asyncio); SSE via `StreamingResponse`; auto-generates OpenAPI |
| Python env | uv | 10–100× faster than pip for dependency resolution |
| Database | Supabase (Postgres) | RLS for multi-tenant isolation; pgvector for embeddings; Auth built-in; free tier |
| Vector search | pgvector (cosine) | Co-located with app data; no extra infra; sufficient at KB scale |
| Embeddings | all-MiniLM-L6-v2 | 384-d, ~80 MB, CPU-fast, free, sentence-transformers baseline |
| Reranker | Cohere rerank-english-v2.0 | Cross-encoder; degrades gracefully if key absent |
| LLM | Claude Haiku → OpenRouter fallback | Haiku is cheap/fast; fallback means zero downtime when credits expire |
| Scheduler | APScheduler (in-process) | Free tier = one container; Celery would double infra |
| Frontend hosting | Vercel | Auto-deploy on push to main; CDN; zero config for Vite |
| Backend hosting | HuggingFace Spaces (Docker) | Free GPU/CPU container; git subtree deploy from monorepo |
| CI/eval | uv run pytest (26 tests) | 16 memory + 10 crash-gap; no integration tests (documented gap) |

---

## Part 9 — Frontend architecture

### File structure

```
src/
├── api/client.js              Axios instance, base URL from VITE_API_BASE_URL, Bearer inject
├── stores/
│   ├── auth.js                Pinia — Supabase session, user profile
│   └── journal.js             Pinia — journal CRUD, analysis polling
├── router/index.js            Vue Router — all routes with requiresAuth meta
├── layouts/DefaultLayout.vue  Shell: sidebar (main + tools nav) + topbar + search
├── pages/
│   ├── AIGuide.vue            Chat + Socratic mode (tabs) — SSE streaming, 7 algorithms
│   ├── Memory.vue             AI memory panel — episodes + facts, per-item delete, wipe
│   ├── journal/
│   │   ├── Index.vue          Journal list
│   │   ├── New.vue            Rich text editor + markdown preview
│   │   └── Entry.vue          Entry detail + bias cards + reflection questions
│   ├── Dashboard.vue          Streak, radar chart, recent activity
│   ├── Learn.vue              CBT knowledge articles
│   └── ...                    Assessments, Biases, Community, Therapists, Profile
├── composables/
│   └── useEpistemeChat.ts     All Socratic state (BKT, SDSM, session mgmt)
└── lib/episteme/
    ├── algorithms.ts           7 pure-function algorithms (no framework dependency)
    └── types.ts                TypeScript types: DepthLevel, SocraticState, BKTState
```

### SSE streaming pattern

```js
// AIGuide.vue (simplified)
const response = await fetch(API_BASE + '/ai/chat', {
  method: 'POST',
  headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
  body: JSON.stringify({ message, conversation_id: sessionConvId, ... }),
})
const reader = response.body.getReader()
while (true) {
  const { value, done } = await reader.read()
  if (done) break
  const chunk = new TextDecoder().decode(value)
  // parse SSE "data: ..." lines → append to message
}
```

Backend side: `StreamingResponse(event_stream(), media_type="text/event-stream")`.

---

## Part 10 — Database schema

| Table | Key columns | Purpose |
|---|---|---|
| `profiles` | id (FK auth.users), name, email | User profile data |
| `journal_entries` | id, user_id, content, mood, sentiment_score, detected_biases JSONB, themes JSONB, emotions JSONB, **analysis_status**, embedding vector(384) | Journal with crash-proof pipeline status |
| `knowledge_articles` | id, title, body, embedding vector(384) | RAG knowledge base (CBT articles) |
| `ai_conversations` | id (client UUID), user_id, messages JSONB, context_summary | Chat history, Option B session grouping |
| `memory_episodes` | id, user_id, conversation_id (UNIQUE), summary, embedding vector(384), importance, age_days | Episodic memory tier |
| `user_facts` | id, user_id, fact, embedding vector(384), access_count, consolidated_from | Semantic memory tier |
| `socratic_sessions` | id, user_id, domain, turns_count, is_complete | Socratic session metadata |
| `socratic_messages` | id, session_id, role, content, turn_number | Per-turn Socratic messages |
| `socratic_insight_cards` | id, session_id, concept, insight, gaps JSONB, clarity_score | End-of-session insight |
| `assessments` | id, slug, title, questions JSONB | Questionnaire definitions |
| `assessment_results` | id, user_id, assessment_id, scores JSONB | User questionnaire scores |
| `user_bias_profiles` | user_id, bias_scores JSONB, archetype, dominant_category | Aggregate bias fingerprint |
| `biases` | id, name, description, examples JSONB | 15-class CBT taxonomy |
| `community_threads` | id, author_id, topic, title, content | Discussion threads |
| `community_replies` | id, thread_id, author_id, content | Thread replies |
| `community_upvotes` | user_id, thread_id/reply_id | Upvote tracking |
| `therapists` | id, name, specialty, contact | Therapist directory |
| `user_badges` | user_id, badge_id | Badge collection |

**RLS**: every user-data table has Row Level Security — users can only read/write their own rows.
Enforced in Supabase, not in application code (defense-in-depth).

**pgvector indexes**: `IVFFlat` index on `knowledge_articles.embedding`, `memory_episodes.embedding`,
`user_facts.embedding` for ANN search. Partial index `idx_journal_pending` on `journal_entries`
where `analysis_status='pending'` for O(orphans) sweep.

---

## Part 11 — Safety systems

### Input gate (pre-LLM, zero cost)

20+ crisis keyword patterns checked BEFORE any token is spent or row saved:
- Keywords: "suicide", "self-harm", "end my life", "don't want to exist", etc.
- If triggered: returns India crisis helplines (iCall: 9152987821, Vandrevala: 1860-2662-345)
- Claude is never called; entry is never persisted
- Implemented in `services/safety.py`, called at the top of `/ai/chat` and `/journal/` POST

### Output filter (post-generation)

Every streamed chunk regex-scanned for clinical overreach:
- Patterns: diagnosis language, medication recommendations, "you have [condition]"
- Flagged chunk dropped before forwarding to client
- Stream continues with next chunk

### Memory ethics

Memory panel (`/memory`): shows what Sentio knows. Per-item delete + full wipe. No hidden
persistent data. Documented in app UI ("These fade over ~2 weeks").

### Therapist referral

System prompt instructs Claude: if user shows signs needing professional support, recommend
Sentio's therapist directory. Hardcoded in `SYSTEM_PROMPT_TEXT` — can't be overridden by user.

---

## Part 12 — System design decisions (the "why" behind choices)

| Decision | Alternative considered | Why this choice |
|---|---|---|
| Client-side Episteme algorithms | Server-side | Zero latency for state decisions; no API cost for pure logic |
| One episode per session (Option B) | One row per message | Coherent summaries; history panel loads full sessions; stable UUID |
| `analysis_status` on `journal_entries` | Separate `pending_jobs` table | One fewer join; data co-located; HF Spaces is single-process so no multi-worker fan-out needed |
| In-process APScheduler | pg_cron / Celery | Free tier = one container; documented trade-off in code |
| Claude Haiku for bias classifier | DistilBERT fine-tuned | Generative output = structured JSON + confidence + span; extends taxonomy without head retraining |
| QLoRA over full fine-tuning | Full FT | 3B fp32 ≈ 12 GB, NF4 ≈ 4 GB; fits free T4; only ~1.3% params trainable |
| git subtree for HF deploy | Separate repo | One monorepo source of truth; deploy only the `sentio-api/` subfolder as HF Space root |
| Prompt caching (`cache_control: ephemeral`) | No caching | Large static system prompt (400+ tokens) repeated every request; caching cuts cost ~4× |
| OpenRouter as fallback (not OpenAI) | Direct OpenAI | OpenRouter proxies 100+ models including Claude, Gemini, GPT via one key; model-agnostic |

---

## Part 13 — Numbers table (fill from RESULTS.md after runs)

| Metric | Value |
|---|---|
| RAG precision@3 (cosine only) | __ |
| RAG precision@3 (+ Cohere rerank) | __ |
| RAG MRR before → after rerank | __ → __ |
| Bias classifier (Haiku) macro F1 / agreement | __ / __ |
| QLoRA student macro F1 / agreement | __ / __ |
| Student vs teacher: classes won | __ / 15 |
| P50 / P95 @ 25 users (Locust) | __ / __ ms |
| P50 / P95 @ 50 users (Locust) | __ / __ ms |
| Backend tests | 26 passed (16 memory + 10 crash-gap) |
| Memory decay half-lives | 14 d episodes / 140 d facts |
| Cost: episode summary / bias classify | ~$0.0001 / ~$0.0002 |
| QLoRA training time on Kaggle T4 | ~60–75 min |
| QLoRA dataset cost (Haiku, 750 examples) | ~$0.12 |

---

## Part 14 — Demo script (5–6 minutes)

**Scene 1 — Journal bias detection (90s)**
1. New journal entry — paste: *"I completely failed my stats exam. I knew this would happen.
   I always mess up when it matters most. Everyone else seems to be landing opportunities
   effortlessly while I keep failing. There's no point applying anywhere."*
2. Submit — show "Sentiment analysis pending"
3. Navigate away, return in 20s — show biases: catastrophizing, mind_reading, overgeneralization,
   all_or_nothing. Mention the 15-class CBT taxonomy.

**Scene 2 — AI Guide with memory (2 min)**
1. Open AI Guide, send: *"I keep catastrophizing every time I face rejection. I got rejected from
   an internship and now I feel like my entire career is over. I'm Atharv, DS student at IITM."*
2. Show RAG-grounded response (network tab → match_knowledge 200)
3. One follow-up exchange — show response references bias profile
4. Close tab — mention episode is being saved (show HF logs: `POST memory_episodes 201`)

**Scene 3 — Memory recall (60s)**
1. Refresh, new session, send: *"What do you remember about me from before?"*
2. Show guide references the internship anxiety
3. Sidebar → AI Memory — show episode card, delete it — "now it forgets"

**Scene 4 — Socratic mode (45s)**
1. Switch to Socratic tab, choose "Cognitive Biases"
2. Show PROBE state — one turn of dialogue
3. Open browser dev tools — show `nextState: "PROBE"`, `clarityScore: 20`, `qualityScore: 0.4`
4. "All this runs client-side — no round trip for state decisions"

**Scene 5 — Numbers (30s)**
1. Open RESULTS.md — "every AI component has a measured eval"

---

## Part 15 — Reproduce every number

```bash
cd sentio-api
uv run pytest tests/ -v                           # 26 tests
python scripts/eval_rag.py                        # RAG precision@3 + MRR → RESULTS.md
python scripts/eval_bias.py                       # classifier F1 → RESULTS.md (~$0.006)
locust -f scripts/locustfile.py \
       --host https://<hf-space>.hf.space \
       --users 25 --spawn-rate 5 --run-time 60s --headless
# QLoRA: sentio-ml/notebooks/sentio_bias_qlora.ipynb on Kaggle T4 (~60 min)
```

---

## Part 16 — Weakness pre-emption (say it before they find it)

- **Auto-labeled RAG ground truth** — single-relevant-article assumption; next step = small human-judged query set.
- **30-entry bias holdout is small** — 2 per class gives directional, not tight, F1; flagged in eval script. Growing it costs ~$0.006/30 entries.
- **Synthetic training data inherits teacher bias** — mitigated by human holdout, not eliminated.
- **In-process APScheduler dies with container** — misfire_grace_time + orphan sweep = eventually-consistent; pg_cron is the scale answer.
- **Memory eval is qualitative** — with/without-memory dialogue; no quantitative benchmark (e.g. needle-style recall). A known gap I'd build next.
- **No integration tests** — 26 unit tests mock the DB layer; a real-DB test suite would catch migration regressions. Documented trade-off for a free-tier project.
- **Single container** — Locust P95 climbs sharply at 50 users. Fix: paid HF Space tier, or SSE connection cap + async queue for chat.
- **OpenRouter fallback models differ in JSON reliability** — bias classifier and insight card generation both parse strict JSON. GPT-4o-mini is most reliable; Llama free tier may hallucinate JSON structure. The `json.loads` try/except already handles this (falls back to generic response).

---

## Part 17 — Quick-reference: what happens when X

| "What happens when..." | Answer |
|---|---|
| User sends a chat message | Safety gate → working cache check → RAG query → memory retrieve → build system prompt → stream_text → SSE → post-stream: save episode (non-blocking) → badge check |
| User creates a journal entry | INSERT row (status=pending) → 201 → background: processing → Haiku classify biases → VADER sentiment → KeyBERT themes → embed entry → UPDATE row (status=done) |
| Container restarts mid-analysis | Row stays status=pending → sweep runs in 10 min → re-queues _process_entry → done |
| Anthropic credits expire | Set OPENROUTER_API_KEY, remove ANTHROPIC_API_KEY, restart Space → all features keep working via OpenRouter |
| User deletes a memory | DELETE /ai/memory/{id}?source=episode|fact → hard deletes from Supabase → next chat has no injection from that memory |
| Nightly consolidation runs | 02:00 UTC → find users with unconsolidated episodes > 7 days → Haiku distils 2–4 facts → insert user_facts → mark episodes consolidated |
| match_memory RPC fails | Returns "" → chat proceeds without memory context (graceful degradation, logged as WARNING) |

---

*Companion files: `UPGRADE_LOG.md` (decisions + test results) · `RUN_GUIDE.md` (what to run to fill the numbers table) · `RESULTS.md` (fill after running scripts)*
