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
│  APScheduler (in-process, 4 jobs)                           │
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

### Journal NLP pipeline (services/journal_nlp.py)

Three signals extracted from every journal entry after bias classification:

```
analyze_journal(text)
  ├─ If JOURNAL_NLP_URL env var set:
  │    → POST to external HF Space NLP endpoint (themes + sentiment + emotions)
  │    → Falls back to local if endpoint times out (25s) or errors
  └─ Local fallback (always available, zero API cost):
       ├─ Sentiment: VADER SentimentIntensityAnalyzer
       │    → compound score ∈ [-1.0, +1.0] (lexicon + rule-based, no model)
       │    → e.g. "I failed completely" → -0.7, "I feel grateful" → +0.8
       ├─ Themes: keyword mapping dict (20 categories)
       │    → "deadline/project/work" → "work-stress", "study/learn" → "learning", etc.
       │    → returns up to 5 matched themes
       └─ Emotions: simple keyword heuristic
            → frustrated/angry → anger, sad/hurt → sadness, happy/grateful → joy,
              worried/anxious → fear, else → neutral
```

**Why VADER and not a transformer?** VADER is a validated, rule-based lexicon specifically
designed for social media / conversational text (Hutto & Gilbert 2014). It runs in microseconds
with zero API cost, no model loading, and no cold-start. For short journal entries (200–500 words)
it is comparable to small sentiment transformers on valence classification. The HF NLP endpoint
(if configured) replaces it with a proper transformer pipeline — VADER is the cost-free fallback.

**VADER compound score**: sum of normalized lexicon valence scores, adjusted for punctuation
emphasis (!!!), capitalization (GREAT vs great), and negation (not great). Clamped to [-1, 1].

### APScheduler jobs (all 4)

| Job | Trigger | LLM? | What it does |
|---|---|---|---|
| `_send_daily_nudge` | daily 19:00 UTC | No | DB query + Resend email if user hasn't journaled today |
| `_weekly_digest` | Mon 08:00 UTC | No | DB query + Resend email with weekly bias summary |
| `_sweep_orphan_analyses` | every 10 min | Only if orphans exist | One DB query; re-queues stuck entries only if `pending` + `created_at < now()-5min` |
| `_consolidate_memories` | daily 02:00 UTC | Yes (once/user/week) | Distils episodes → user_facts for users with 7+ day-old episodes |

**Credit safety**: `_sweep_orphan_analyses` runs 144×/day but is just one Supabase HTTP GET
— zero LLM cost in normal operation. `_consolidate_memories` costs ~$0.0001 per active user
per night (one `complete_text` call), only when they have qualifying old episodes.
`_weekly_digest` and `_send_daily_nudge` are pure DB + email — no LLM calls, no model inference.

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
| Sentiment | VADER (vaderSentiment) | Lexicon + rule-based, microsecond latency, zero API cost; falls back from external NLP endpoint |
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
| User creates a journal entry | INSERT row (status=pending) → 201 → background: _process_entry: (1) Haiku classify_biases → detected_biases JSONB, (2) journal_nlp.analyze_journal() → VADER sentiment [-1,1] + keyword themes + emotion heuristic, (3) embed entry with MiniLM → UPDATE row status=done |
| Container restarts mid-analysis | Row stays status=pending → sweep runs in 10 min → re-queues _process_entry → done |
| Anthropic credits expire | Set OPENROUTER_API_KEY, remove ANTHROPIC_API_KEY, restart Space → all features keep working via OpenRouter |
| User deletes a memory | DELETE /ai/memory/{id}?source=episode|fact → hard deletes from Supabase → next chat has no injection from that memory |
| Nightly consolidation runs | 02:00 UTC → find users with unconsolidated episodes > 7 days → Haiku distils 2–4 facts → insert user_facts → mark episodes consolidated |
| match_memory RPC fails | Returns "" → chat proceeds without memory context (graceful degradation, logged as WARNING) |

| User requests reflection questions | POST /journal/{id}/reflections → fetch content + detected_biases → Haiku generates exactly 3 open-ended questions grounded in bias context → returned to client on demand (NOT at save time) |
| User submits an assessment | POST /assessments/{id}/submit → insert assessment_results → update user_bias_profiles (Likert → normalized 0–1, blended 60%/40% with journal scores) → background: send email + award badges |
| User upvotes a thread | Check community_upvotes for existing row → if exists: delete + decrement_thread_upvote RPC → if not: insert + increment_thread_upvote RPC (idempotent toggle) |
| User requests weekly insights | GET /insights/weekly → check in-process weekly cache (key=user_id+year+week) → if miss: aggregate last 7 journal entries → Anthropic generates 3 JSON insights → cache and return |
| Daily nudge job runs | 19:00 UTC → for each profile with notifications.daily=true: check if journaled today → if not: get email from auth.admin → compute streak → send_daily_reminder via Resend |
| User connects to therapist | POST /therapists/{id}/book → verify therapist.verified → insert bookings row (status=pending) → background: send booking confirmation email |

---

## Part 18 — Badge engine

### 12 badges, when awarded

`services/badge_engine.py` — `check_and_award_badges(user_id, supabase)` is called after:
- Journal entry save (in `_process_entry`)
- Assessment submit (in `assessments.py` background task)
- Community thread or reply create (in `community.py`)

| Badge ID | Name | Trigger |
|---|---|---|
| `first_journal` | First Reflection | ≥1 journal entry |
| `streak_7` | Week of Clarity | 7-day consecutive journaling streak |
| `streak_30` | Month of Mindfulness | 30-day consecutive streak |
| `bias_3` | Pattern Spotter | 3 unique bias IDs across all entries |
| `bias_10` | Bias Hunter | 10 unique bias IDs |
| `no_bias` | Clean Slate | 5 entries where `detected_biases` is empty |
| `assessment_1` | Self-Examiner | ≥1 assessment completed |
| `assessment_all` | Full Spectrum | All available assessments completed (count from DB) |
| `ai_convo` | Deep Thinker | ≥1 AI Guide conversation saved |
| `community_first` | Contributor | ≥1 thread or reply created |
| `community_10` | Voice of Reason | ≥10 combined threads + replies |
| `archetype_set` | Self-Aware | `user_bias_profiles.archetype` is non-null |

### Streak algorithm

```python
def _compute_streak(entries):
    days = sorted({date(e['created_at'][:10]) for e in entries}, reverse=True)
    streak = 1
    for i in range(1, len(days)):
        if days[i-1] - days[i] == timedelta(days=1):
            streak += 1
        else:
            break
    return streak
```

Note: streak counts distinct calendar days (two entries on the same day = 1 day). Streaks reset on any gap > 1 day.

### Idempotency

`user_badges` has `(user_id, badge_id)` unique constraint. `award()` checks the already-awarded set loaded at function start — no re-insert if badge already exists. Community badge check is wrapped in try/except (tables may not exist in older deployments).

---

## Part 19 — Cognitive archetypes + bias profile aggregation

### Archetype map (12 types)

`_ARCHETYPE_MAP` in `routers/journal.py`:

| Dominant bias | Archetype name |
|---|---|
| confirmation_bias | The Conviction Keeper |
| anchoring_bias | The Anchor |
| availability_bias | The Storyteller |
| overconfidence | The Visionary |
| social_conformity | The Harmonizer |
| attribution_error | The Judge |
| sunk_cost_fallacy | The Investor |
| dunning_kruger | The Explorer |
| status_quo_bias | The Traditionalist |
| halo_effect | The Idealist |
| bandwagon_effect | The Follower |
| recency_bias | The Moment-Chaser |

Any unmapped bias → `'The Thinker'`

### Blend archetype (top-2 within 0.05)

```python
def _compute_archetype(bias_scores):
    sorted_biases = sorted(bias_scores.items(), key=lambda x: x[1], reverse=True)
    top1_bias, top1_score = sorted_biases[0]
    top2_bias, top2_score = sorted_biases[1]
    if (top1_score - top2_score) < 0.05 and arch1 != arch2:
        return f"{arch1} with {arch2} tendencies"   # blend archetype
    return arch1
```

E.g. "The Conviction Keeper with The Explorer tendencies" — surfaced in weekly digest email + bias fingerprint page.

### Bias profile aggregation — two update paths

**Path 1: Journal detection** (`_update_bias_profile` in `routers/journal.py`):
```python
delta = confidence × 0.1          # e.g. 0.87 confidence → +0.087
new_score = min(1.0, old + delta)  # capped at 1.0
```
Called per-entry, incremental. A single journal entry cannot swing the profile dramatically.

**Path 2: Assessment submission** (`routers/assessments.py`):
```python
# Likert 1–5 → 0–1
new_score = (average_raw_score - 1) / 4

# Blend with existing journal score
merged[bias_id] = old_score * 0.6 + new_score * 0.4   # 60% journal, 40% assessment
```
Assessment provides structured aggregate view; journal provides real-time signal. The 60/40 blend weights longitudinal journal data more heavily.

### bias_scores JSON structure

```json
{
  "confirmation_bias": 0.342,
  "catastrophizing": 0.180,
  "attribution_error": 0.091
}
```

Keys are `snake_case` bias IDs matching `_BIAS_TAXONOMY`. Scores accumulate over time; archived in `user_bias_profiles`. The bias fingerprint page renders a radar chart over all scores.

---

## Part 20 — Assessment system

### 4 assessment types

| Assessment | Validated tool? | What it measures |
|---|---|---|
| GAD-7 | Yes (clinical) | Generalized anxiety (7 items, 0–3 Likert) |
| PHQ-9 | Yes (clinical) | Depression severity (9 items, 0–3 Likert) |
| Big Five | Yes (OCEAN) | Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism |
| Cognitive Style | Sentio custom | Bias-linked thinking patterns |

Field `assessments.validated_tool` (boolean) displayed in UI to signal clinical grounding.

### Assessment data model

```json
assessments.questions = [
  {
    "id": "q1",
    "text": "Feeling nervous, anxious or on edge",
    "type": "likert",
    "scale": [0, 1, 2, 3],
    "labels": ["Not at all", "Several days", "More than half", "Nearly every day"],
    "bias_signal": "catastrophizing"   ← maps to bias_scores key
  },
  ...
]
```

### Scoring pipeline (frontend → backend)

1. Frontend presents questions, collects `raw_scores: {"q1": 2, "q2": 1, ...}`
2. Frontend computes `computed_scores` (domain totals) and `bias_implications`
3. `POST /assessments/{id}/submit` body: `{raw_scores, computed_scores, bias_implications}`
4. Backend normalizes: `(avg_raw - min_scale) / (max_scale - min_scale)`
5. Backend blends into `user_bias_profiles.bias_scores`
6. Background: assessment complete email + badge check

### Most-recent-result deduplication

`GET /assessments/user/results` returns the **most recent result per assessment** (not all-time history). History view: `GET /assessments/{id}/history` shows all past submissions for trend tracking.

---

## Part 21 — Email system

### Provider: Resend

```python
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
FROM_EMAIL = os.getenv("RESEND_FROM_EMAIL", "noreply@sentio.app")
```

**Free tier**: 3,000 emails/month, 100/day. If `RESEND_API_KEY` is absent → `send_email` logs stub and returns `True` (no crash, no email). All email calls are non-blocking (FastAPI `BackgroundTasks`).

### 4 email templates

| Function | Trigger | Content |
|---|---|---|
| `send_daily_reminder` | APScheduler 19:00 UTC | "Time to reflect" + streak count + journal CTA |
| `send_weekly_digest` | APScheduler Mon 08:00 UTC | Entry count + top themes + emotional tone + archetype block |
| `send_assessment_complete` | After assessment submit | Assessment title + overall score + archetype |
| `send_booking_notification` | After therapist booking | Therapist name + "request submitted" |

All use `_base_template(content)` — Sentio purple gradient header, consistent brand footer with "manage preferences" link.

### Notification preferences (user-controlled)

`profiles.preferences` is a JSONB column:
```json
{
  "notifications": {
    "daily": true,
    "weekly": true
  }
}
```

Scheduler checks `prefs.get("notifications", {}).get("daily", True)` — defaults to `True` if pref not set (opt-out model). User can toggle in `/profile` page.

---

## Part 22 — Community features

### Data model

```
community_topics       (id, slug, title, thread_count)
  └── community_threads  (id, topic_id, author_id, title, body, upvotes, reply_count, is_pinned, is_locked)
       └── community_replies  (id, thread_id, author_id, body, parent_reply_id, upvotes)
community_upvotes      (user_id, target_type ["thread"|"reply"], target_id)
```

### Threading (nested replies)

Replies have `parent_reply_id` for one level of nesting (direct reply to a specific reply). Frontend renders the tree; backend stores flat with parent pointer.

### Upvote toggle (idempotent)

```python
# POST /community/threads/{id}/upvote
existing = check community_upvotes WHERE user_id + target_type + target_id
if existing:
    delete upvote + decrement_thread_upvote RPC
    return {"action": "removed"}
else:
    insert upvote + increment_thread_upvote RPC
    return {"action": "added"}
```

Counter is stored on the thread/reply row (denormalized for fast listing). `community_upvotes` table prevents duplicates.

### Thread management

- `is_pinned`: admin/mod feature — pinned threads sort first in topic listing
- `is_locked`: prevents new replies (enforced in `add_reply` endpoint with 403)
- Thread deletion: author-only (403 if `thread.author_id != user_id`)
- Reply deletion: author-only (same check)

### Safety in community

Every thread/reply body passes `safety.check_input()` before insert. Crisis keywords → `422 Unprocessable Entity` with crisis resources (same response as AI chat gate).

### Author display names

Community endpoints deliberately **don't** use PostgREST embedded joins for author profiles (avoids schema-cache issues after FK migrations). Instead: batch-resolve author IDs → separate `profiles` query → merge into response dict.

---

## Part 23 — Therapist directory + recommender

### Therapist filtering

`GET /therapists` supports 5 optional query params:
- `language` — filter by language string in `therapists.languages[]`
- `specialization` — filter by keyword in `therapists.specializations[]`
- `format` — online / in-person / both (substring match)
- `lat` + `lng` + `radius_km` — geolocation: invokes `get_nearest_therapists` Supabase RPC (haversine formula), falls back to full list if RPC not installed

Only `verified=true` therapists are returned. Sentio does **not** intermediate the clinical relationship — the booking button records intent; actual scheduling happens on the therapist's external platform.

### Booking flow

1. `POST /therapists/{id}/book` body: `{message, requested_at}`
2. Verify therapist exists + is verified
3. Insert `bookings` row (status=`pending`)
4. Background: `send_booking_notification` email to user
5. Returns `{status: "request_submitted", booking_id}`

### Recommender (`services/recommender.py`)

**`recommend_bias_to_explore`**:
```
CATEGORY_ADJACENCY = {
  "memory": ["belief", "decision"],
  "social": ["self", "belief"],
  "decision": ["memory", "reasoning"],
  "self": ["social", "belief"],
  "belief": ["reasoning", "social"],
  "reasoning": ["decision", "belief"],
}

New user → first bias alphabetically
Returning user → find top-scoring bias → its category → adjacent category → first bias in that category
```

**`recommend_assessment`**: query assessments NOT IN (completed_assessment_ids) → return first uncompleted. Used on Dashboard to show personalized "next step" cards.

---

## Part 24 — Weekly insights (`/insights/weekly`)

### What it does

`GET /insights/weekly` → Claude generates 3 personalized data-driven insights from the last 7 journal entries:
- Entry count
- Top 5 themes (Counter)
- Top 3 detected biases (Counter)
- Average sentiment score
- Socratic session count

Claude returns JSON: `[{"type": "bias", "text": "...", "icon": "brain"}, ...]`. Icon must be a valid lucide-vue-next icon name.

### In-process weekly cache

```python
_WEEKLY_INSIGHT_CACHE: dict[str, list] = {}
cache_key = f"{user_id}_{current_year}_{current_week}"
```

Prevents regenerating insights multiple times in the same calendar week for the same user. Cache is in-process (lost on container restart) — that's acceptable; insights regenerate on next request.

### ⚠️ Known gap: still uses direct Anthropic client

`routers/insights.py` imports `anthropic` directly (`import anthropic`) instead of going through `llm_client.py`. This means:
- Weekly insights **will break** when Anthropic credits expire and you switch to OpenRouter
- **Fix needed**: replace direct `client.messages.create()` with `await complete_text(...)` from `llm_client`
- All other LLM features (AI Guide, bias classifier, memory, Socratic, reflections) correctly use `llm_client.py`

---

## Part 25 — Auth flow + env vars

### Supabase Auth flow

1. Frontend: Supabase JS client → `supabase.auth.signInWithPassword()` or OAuth
2. Returns: JWT access token (stored in Pinia `auth.js` store)
3. Axios interceptor: `Authorization: Bearer <token>` on every request
4. Backend `_auth_helpers.py`: `get_user_id(authorization)` → calls `supabase.auth.get_user(jwt)` → returns `user.id`; raises 401 if invalid
5. RLS: Supabase enforces `auth.uid() = user_id` on every user-data table — even if app code has a bug, DB won't return other users' rows

```python
# _auth_helpers.py
def get_user_id(authorization: str | None) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing auth token")
    token = authorization.split(" ")[1]
    user = get_supabase().auth.get_user(token)
    if not user or not user.user:
        raise HTTPException(401, "Invalid token")
    return user.user.id

def get_user(authorization) -> dict:
    # same but returns full user object (for email access)
```

### Required env vars (backend — HF Space secrets)

| Variable | Required | Purpose |
|---|---|---|
| `SUPABASE_URL` | Yes | Supabase project URL |
| `SUPABASE_SERVICE_KEY` | Yes | Service-role key (bypasses RLS for admin ops) |
| `ANTHROPIC_API_KEY` | One of these | Primary LLM provider |
| `OPENROUTER_API_KEY` | One of these | Fallback LLM provider |
| `COHERE_API_KEY` | Optional | Reranker (degrades gracefully if absent) |
| `RESEND_API_KEY` | Optional | Email delivery (stub/log-only if absent) |
| `RESEND_FROM_EMAIL` | Optional | Sender address (default: noreply@sentio.app) |
| `APP_URL` | Optional | Base URL for email links (default: https://sentio.app) |
| `JOURNAL_NLP_URL` | Optional | External HF NLP endpoint (local VADER fallback if absent) |
| `CLAUDE_MODEL` | Optional | Override Anthropic model (default: claude-haiku-4-5-20251001) |
| `FALLBACK_MODEL` | Optional | Override OpenRouter model (default: google/gemini-flash-1.5-exp) |

### Required env vars (frontend — Vercel)

| Variable | Purpose |
|---|---|
| `VITE_SUPABASE_URL` | Supabase project URL |
| `VITE_SUPABASE_ANON_KEY` | Anon key (client-safe, RLS enforced) |
| `VITE_API_BASE_URL` | FastAPI backend URL (e.g. https://your-space.hf.space) |

**Security note**: frontend uses `ANON_KEY` (public, RLS-restricted). Backend uses `SERVICE_KEY` (never exposed to client — bypasses RLS for admin operations like `auth.admin.get_user_by_id`).

---

## Part 26 — Reflection questions (on-demand, not at save time)

`POST /journal/{entry_id}/reflections` — user explicitly clicks "Get Reflection Questions":

1. Fetch entry `content` + `detected_biases` from DB
2. Call `generate_journal_reflections(content, biases)` in `claude_service.py`
3. Prompt: "Generate exactly 3 follow-up reflection questions... grounded in the specific content... do not label the person"
4. Parse response: split by newline, take first 3 non-empty lines
5. Fallback questions if LLM fails — bias-aware (different Q if `confirmation_bias` detected)

**Why on-demand?** Reflection requires user attention — generating them at save time would be wasted compute for entries never revisited. Also avoids adding a 4th API call to the already-busy `_process_entry` background task.

---

## Part 27 — Supabase RPCs inventory

All database-side functions invoked via `supabase.rpc(...)`:

| RPC | Called from | What it does |
|---|---|---|
| `match_knowledge` | `rag_service.py` | pgvector cosine search on `knowledge_articles`, threshold 0.65, top-10 |
| `match_memory` | `memory_service.py` | Decay-weighted UNION of `memory_episodes` + `user_facts`, top-k |
| `increment_fact_access` | `memory_service.py` | Bumps `user_facts.access_count` for retrieved facts |
| `get_nearest_therapists` | `routers/therapists.py` | Haversine distance sort within radius_km |
| `increment_thread_reply_count` | `routers/community.py` | +1 on `community_threads.reply_count` |
| `increment_topic_thread_count` | `routers/community.py` | +1 on `community_topics.thread_count` |
| `increment_thread_upvote` | `routers/community.py` | +1 on `community_threads.upvotes` |
| `decrement_thread_upvote` | `routers/community.py` | −1 on `community_threads.upvotes` |
| `increment_reply_upvote` | `routers/community.py` | +1 on `community_replies.upvotes` |
| `decrement_reply_upvote` | `routers/community.py` | −1 on `community_replies.upvotes` |

**Why RPCs for counters?** Atomic increment/decrement at DB level — no race condition from concurrent reads + updates in application code. PostgREST `.update({upvotes: upvotes+1})` requires a read-modify-write cycle.

---

## Part 28 — Git subtree deploy (monorepo → HF Space)

### Why monorepo + subtree

Single source of truth: `sentio-repo/` contains both `src/` (Vue frontend) and `sentio-api/` (FastAPI backend). HF Spaces expects a repo root with the `Dockerfile` — so only `sentio-api/` subfolder is pushed as the Space root.

### Deploy commands

```bash
# From sentio-repo/ — push only sentio-api/ subfolder to HF Space main branch
git subtree split --prefix=sentio-api --branch hf-deploy
git push hf-space hf-deploy:main --force
git branch -D hf-deploy

# Frontend (Vercel auto-deploys on git push to main — no manual step)
git push origin main
```

### Dockerfile (in sentio-api/)

Builds a Docker image: installs `uv`, copies app, runs `uv sync`, starts `uvicorn main:app --host 0.0.0.0 --port 7860`. Port 7860 is HF Spaces standard.

### Cold-start behavior

`sentence_transformers` model (all-MiniLM-L6-v2, ~80 MB) is preloaded at startup via `_get_embedder()` called from `main.py` lifespan. APScheduler also starts in the lifespan hook. First request after cold start is slow (~15s for model load); subsequent requests are fast.

---

*Companion files: `UPGRADE_LOG.md` (decisions + test results) · `RUN_GUIDE.md` (what to run to fill the numbers table) · `RESULTS.md` (fill after running scripts)*
