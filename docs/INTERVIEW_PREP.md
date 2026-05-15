# Sentio — Comprehensive Interview Preparation Guide

> **Purpose:** Deep technical reference for one-on-one interviews with domain experts.
> Covers every layer of the system: product, architecture, ML, NLP, algorithms, and engineering decisions.

---

## 1. Project Summary (60-second pitch)

**Sentio** is a full-stack cognitive-bias self-awareness platform. Users write daily journal entries; the system uses a multi-layer AI pipeline to detect cognitive biases in their writing, track bias patterns over time, assign a personalised cognitive archetype, and guide users toward greater self-awareness through a Socratic AI dialogue engine.

Key differentiators:
- **Dual-mode AI:** a *Guide* mode (direct explanations via RAG) and a *Socratic* mode (Episteme engine with 7 client-side algorithms that model the user's knowledge state)
- **Real NLP pipeline:** VADER sentiment + Claude Haiku bias classification (15-class taxonomy)
- **Longitudinal profiling:** bias scores accumulate across journal entries → archetype emerges over time
- **Safety-first:** two-layer content safety gate (crisis detection + clinical overreach prevention on every streamed token)

---

## 2. Tech Stack

| Layer | Technology | Why chosen |
|---|---|---|
| Frontend | Vue 3 + Vite + Pinia + Vue Router 4 | Composition API enables clean reactive composables; Vite gives sub-second HMR |
| Backend | FastAPI + Python 3.11 + Pydantic v2 | Async-first; automatic OpenAPI docs; Pydantic v2 is 5-17× faster than v1 for validation |
| Database | Supabase (PostgreSQL + pgvector + RLS + Auth) | Managed Postgres with built-in auth, realtime, and vector extension for RAG |
| Primary AI | Anthropic Claude (Haiku for classification/insights, Sonnet for Socratic) | Best instruction-following for structured JSON output; prompt caching cuts costs |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` | 384-dim, 80 MB, fast on CPU; cosine similarity well-calibrated for semantic search |
| Reranking | Cohere Rerank v2 | Cross-encoder quality at API latency; graceful fallback to cosine top-k |
| Sentiment | VADER (vaderSentiment 3.3.2) | Rule-based; no GPU needed; performs on par with fine-tuned models for social/journal text |
| Scheduling | APScheduler | In-process cron jobs for background analytics without a separate worker queue |
| Deployment | HuggingFace Spaces (Docker, port 7860) + Vercel | HF Spaces is free for CPU workloads; Vercel gives edge-cached SPA delivery |

---

## 3. Architecture Overview

```
Browser (Vue 3 SPA)
    │
    │  HTTPS / SSE
    ▼
FastAPI (HuggingFace Spaces, port 7860)
    ├── /auth          → Supabase Auth proxy
    ├── /journal       → CRUD + background NLP task
    ├── /socratic      → Episteme SSE engine
    ├── /ai            → Guide mode (RAG + Claude)
    ├── /insights      → Fingerprint, weekly synthesis
    ├── /assessments   → Psychometric tools
    ├── /therapists    → Booking + email notification
    └── /community     → Threads & replies
         │
         ├── Supabase PostgreSQL
         │     ├── journal_entries (pgvector column: embedding)
         │     ├── user_bias_profiles (JSONB: bias_scores)
         │     ├── knowledge_articles (pgvector column: embedding)
         │     └── socratic_sessions / messages / insight_cards
         │
         ├── Anthropic API (Claude Haiku / Sonnet)
         ├── Cohere API (rerank-english-v2.0)
         └── Resend API (transactional email)
```

**Request lifecycle for a journal entry:**
1. POST `/journal/` → safety gate → insert raw entry → return immediately (201)
2. `BackgroundTasks.add_task(_process_entry)` fires async:
   - `classify_biases(content)` → Claude Haiku → JSON bias list
   - `analyze_journal(content)` → VADER sentiment + keyword themes
   - PATCH entry with results
   - `_update_bias_profile()` → upsert `user_bias_profiles`
   - `check_and_award_badges()` → badge engine

Frontend polls `/journal/{id}` every 3s until `detected_biases != null`.

---

## 4. Directory Structure

```
Sentio/
├── src/                          # Vue 3 frontend
│   ├── pages/
│   │   ├── journal/
│   │   │   ├── Index.vue         # List + CRUD (ellipsis menu, delete modal)
│   │   │   ├── New.vue           # Real-time bias analysis while typing
│   │   │   └── Entry.vue         # Entry detail + polling for async analysis
│   │   ├── Dashboard.vue         # Radar chart, archetype, stats
│   │   └── AIGuide.vue           # Dual-mode AI (Guide / Socratic)
│   ├── composables/
│   │   └── useEpistemeChat.ts    # 7-algorithm Socratic engine (TypeScript)
│   ├── lib/episteme/
│   │   ├── algorithms.ts         # RDSE, SDSM, BKT, SDSM, BGDC, CPGAB, EGP, SM-2
│   │   └── types.ts
│   ├── stores/                   # Pinia stores
│   └── api/                      # Axios wrappers per router
│
├── sentio-api/                   # FastAPI backend
│   ├── main.py                   # App factory, CORS, lifespan (pre-warm embedder)
│   ├── routers/
│   │   ├── journal.py            # CRUD + background NLP task
│   │   ├── socratic.py           # SSE stream + session management
│   │   ├── insights.py           # Fingerprint, weekly Claude synthesis
│   │   ├── therapists.py         # Booking + Resend email
│   │   └── _auth_helpers.py      # JWT decode, get_user_id, get_user
│   ├── services/
│   │   ├── bias_classifier.py    # Claude Haiku 15-class taxonomy
│   │   ├── journal_nlp.py        # VADER + keyword themes
│   │   ├── rag_service.py        # Embed → pgvector → Cohere rerank
│   │   ├── safety.py             # Crisis + clinical overreach filters
│   │   ├── badge_engine.py       # Gamification logic
│   │   ├── scheduler.py          # APScheduler background jobs
│   │   └── email_service.py      # Resend transactional templates
│   └── db/
│       └── migration_rls_policies.sql
│
└── docs/
    ├── CONTEXT.md
    ├── PROGRESS.md
    └── INTERVIEW_PREP.md         # ← this file
```

---

## 5. Database Schema (key tables)

### `journal_entries`
| Column | Type | Notes |
|---|---|---|
| id | uuid PK | |
| user_id | uuid FK | RLS: `user_id = auth.uid()` |
| content | text | Raw markdown |
| prompt_used | text | Optional writing prompt |
| detected_biases | jsonb | Array of `{bias_id, confidence, span}` — populated async |
| sentiment_score | float4 | VADER compound `[-1, +1]` |
| themes | jsonb | String array from keyword extractor |
| created_at | timestamptz | |

### `user_bias_profiles`
| Column | Type | Notes |
|---|---|---|
| user_id | uuid UNIQUE | One row per user |
| bias_scores | jsonb | `{bias_id: float}` — cumulative, updated on every entry |
| archetype | text | `_compute_archetype()` result |
| dominant_category | text | |

### `knowledge_articles`
| Column | Type | Notes |
|---|---|---|
| embedding | vector(384) | MiniLM-L6-v2 output |
| content | text | Chunked psychology knowledge |
| source_citation | text | APA-style citation |

RLS policies enforce `user_id = auth.uid()` at the Postgres level — even a compromised API key cannot read other users' data.

---
*— End of Part 1 (Architecture & Stack) —*

---

## 6. NLP Pipeline — Deep Dive

### 6.1 Sentiment Analysis: VADER

**What it is:** VADER (Valence Aware Dictionary and sEntiment Reasoner) is a **rule-based** lexicon and grammar model specifically tuned for social-media and short-form text. It does NOT use neural networks.

**How it works:**
1. Every word in the lexicon has a **valence score** in `[-4, +4]` (e.g., *great* = +3.1, *terrible* = -2.9)
2. Five grammatical heuristics modify raw scores:
   - **Punctuation:** `!!!` amplifies by +0.292 per `!` (capped)
   - **Capitalisation:** ALL CAPS boosts intensity by 0.733
   - **Degree modifiers:** *extremely* multiplies by 1.3; *barely* multiplies by 0.5
   - **Contrastive conjunctions:** "but" shifts weight toward the clause after it (0.5/0.5 → 0.25/0.75)
   - **Negation:** preceding negative words (`not`, `never`) flip sign and reduce intensity

**Compound score formula:**
$$C = \frac{x}{\sqrt{x^2 + \alpha}}$$
where $x = \sum_{i} v_i$ (sum of valence scores with heuristic adjustments) and $\alpha = 15$ (normalisation constant).

Output range: $C \in [-1, +1]$.

**Thresholds used in Sentio:**
| Compound range | Label shown |
|---|---|
| $C \geq 0.2$ | Positive tone |
| $-0.2 < C < 0.2$ | Neutral tone |
| $C \leq -0.2$ | Challenging tone |

**Why VADER over a fine-tuned transformer?**
- No GPU required → runs on HF free CPU tier
- Zero inference latency (pure Python dictionary lookup)
- Outperforms LSTM models on social/diary text in original benchmarks (F1 ~0.96 vs ~0.85)
- Production-proven; no training data needed for new domains

**Validation:** VADER was validated on 4,200 tweets by Hutto & Gilbert (2014). On the NLTK movie review corpus it achieves Pearson r = 0.872 against human raters.

### 6.2 Theme Extraction

A **keyword trie lookup** maps surface-form words to 12 canonical themes (work-stress, relationships, finances, etc.). The result is a string array stored in `themes` column. Intentionally lightweight — it is the fallback when the remote HF NLP microservice is unavailable.

**Production upgrade path:** The `analyze_journal()` function first tries `JOURNAL_NLP_URL` (a separate HF Space running a fine-tuned DistilBERT for zero-shot topic classification). If that endpoint is unreachable (timeout > 25s), it falls back to the keyword extractor. This graceful-degradation pattern ensures the journal save never blocks.

---

## 7. Bias Classifier — Deep Dive

### 7.1 Design Decision: LLM-as-Classifier vs Fine-tuned Model

**Alternative considered:** Fine-tune a BERT/RoBERTa model on a labelled cognitive bias dataset.

**Why LLM was chosen:**
- No labelled training set exists for all 15 bias classes in journal text
- Claude Haiku achieves near-expert accuracy via few-shot prompt engineering
- Cost: ~$0.0002 per entry at typical journal lengths (< 500 words)
- Zero infrastructure: no GPU, no model weights to host, no retraining pipeline
- **Prompt caching** (system prompt marked `cache_control: ephemeral`) means the 700-token taxonomy is cached server-side, cutting per-request input tokens by ~60%

### 7.2 The 15-Class Taxonomy

| ID | Bias Name | Key Signal |
|---|---|---|
| `confirmation_bias` | Confirmation Bias | Seeking confirming evidence only |
| `attribution_error` | Attribution Error | Others = character flaws; self = circumstances |
| `all_or_nothing` | All-or-Nothing | No middle ground; absolute language |
| `catastrophizing` | Catastrophizing | Worst-case assumed |
| `mind_reading` | Mind Reading | Assuming others' thoughts without evidence |
| `overgeneralization` | Overgeneralization | "always", "never", "everyone" |
| `emotional_reasoning` | Emotional Reasoning | Feelings treated as facts |
| `should_statements` | Should Statements | Rigid "must"/"should" rules |
| `labeling` | Labeling | Reducing person to single trait |
| `personalization` | Personalization | Excessive self-blame for external events |
| `availability_bias` | Availability Heuristic | Overweighting recent/vivid events |
| `anchoring_bias` | Anchoring Bias | Over-relying on first information |
| `dunning_kruger` | Dunning-Kruger | Overestimating competence |
| `sunk_cost_fallacy` | Sunk Cost Fallacy | Past investment drives future decisions |
| `fundamental_attribution` | Fundamental Attribution | Underweighting situational factors |

### 7.3 Prompt Engineering Strategy

**System prompt structure:**
1. Role definition: "cognitive bias detection system"
2. Full 15-class taxonomy (cached)
3. Rules: confidence threshold ≥ 0.5, max 3 biases, direct quote span required
4. Output schema enforcement: JSON array with strict field names

**Output schema:**
```json
[{"bias_id": "string", "bias": "string", "confidence": 0.5-1.0, "span": "quote"}]
```

**Parsing robustness:** The code strips markdown fences (` ```json `) before `json.loads()`, normalises `bias_id`/`bias` field aliases, and validates against the known ID set. Unknown IDs are silently discarded.

### 7.4 Incremental Bias Scoring

Each detected bias updates the user's cumulative profile using:

$$s_{\text{new}}(b) = \min\left(1.0,\ s_{\text{old}}(b) + \delta\right)$$

where $\delta = \text{confidence} \times 0.1$

For example, a bias detected with confidence 0.82 contributes $\delta = 0.082$. After 12 detections at similar confidence the score saturates at 1.0.

**Rationale:** A multiplicative or Bayesian update was considered but the additive approach is:
- Interpretable to non-technical users
- Easy to audit
- Naturally saturates (no score can exceed 1.0)

### 7.5 Archetype Computation

```python
def _compute_archetype(bias_scores: dict) -> str | None:
    sorted_biases = sorted(bias_scores.items(), key=lambda x: x[1], reverse=True)
    top1_bias, top1_score = sorted_biases[0]
    top2_bias, top2_score = sorted_biases[1]
    # Blend if top-2 scores within 5%
    if (top1_score - top2_score) < 0.05 and arch1 != arch2:
        return f"{arch1} with {arch2} tendencies"
    return arch1
```

**The 5% blending threshold** was chosen because scores below 0.05 apart are statistically indistinguishable given the 0.1-per-detection delta; forcing a single archetype would be misleading.

---

## 8. RAG Pipeline — Deep Dive

### 8.1 Architecture: Embed → Retrieve → Rerank → Generate

```
User query
    │
    ▼ encode() → 384-dim float32 vector
MiniLM-L6-v2
    │
    ▼ cosine similarity search, threshold=0.65
Supabase pgvector (match_knowledge RPC)
    │ returns top-10 chunks
    ▼
Cohere rerank-english-v2.0
    │ cross-encoder scoring, returns top-3
    ▼
Context string injected into Claude prompt
    │
    ▼ streamed response
SSE → browser
```

### 8.2 Embedding Model: all-MiniLM-L6-v2

**Architecture:** 6-layer MiniLM (distilled from BERT-base), 22M parameters, output dimension 384.

**Training:** Trained with **contrastive loss** on 1B sentence pairs from diverse web corpora. The objective is:

$$\mathcal{L} = -\log \frac{e^{\text{sim}(h_i, h_i^+)/\tau}}{\sum_{j} e^{\text{sim}(h_i, h_j)/\tau}}$$

where $h_i$ is the anchor embedding, $h_i^+$ is a positive (semantically similar) pair, and $\tau$ is a temperature parameter.

**Why this model over OpenAI `text-embedding-ada-002`?**
- Runs locally — zero per-call cost, zero latency from API roundtrip
- 384-dim vs 1536-dim → pgvector index 4× smaller, similarity search 4× faster
- MTEB benchmark: MiniLM-L6-v2 scores 56.3 vs ada-002's 60.9 — a 8% quality gap that is acceptable for domain-specific psychology knowledge

**pgvector indexing:** An HNSW index (`m=16, ef_construction=64`) is used for approximate nearest-neighbour search at O(log n) instead of exact O(n) brute force.

### 8.3 Cosine Similarity Threshold

$$\text{sim}(\mathbf{a}, \mathbf{b}) = \frac{\mathbf{a} \cdot \mathbf{b}}{\|\mathbf{a}\| \|\mathbf{b}\|}$$

Threshold = **0.65** chosen empirically:
- Below 0.65: retrieved chunks frequently off-topic
- Above 0.75: recall drops, returning empty results for valid queries
- 0.65 balances precision (no noise injected into Claude prompt) vs recall

### 8.4 Cohere Reranking

The initial pgvector retrieval is a **bi-encoder** (both query and document encoded independently). Cohere's `rerank-english-v2.0` is a **cross-encoder** — it reads query and document jointly, capturing interactions missed by independent encodings.

**Why two-stage?**
- Cross-encoders are O(n) inference per document — too slow for full-corpus search
- Two-stage (bi-encoder top-k → cross-encoder rerank) gives near-cross-encoder quality at bi-encoder speed
- Cohere rerank is stateless API — no model to host

**Graceful degradation:** If `COHERE_API_KEY` is absent or reranking fails, the system falls back to cosine top-3 (already sorted by pgvector). The user never sees an error.

---
*— End of Part 2 (NLP & ML Deep Dive) —*

---

## 9. Episteme Socratic Engine — Deep Dive

The Socratic mode uses **7 algorithms** running **client-side in TypeScript** to model user knowledge state and drive the conversation strategy. The algorithm outputs are sent to the backend with every message so Claude receives them as context.

### 9.1 Why Client-Side Algorithms?

Running stateful knowledge-modeling on the client means:
- **Zero latency** for algorithm computation (no extra API round-trip)
- Backend remains stateless — any server can handle any request
- User's cognitive state survives page refresh via sessionStorage
- Algorithms can update reactively on every keystroke (real-time UI feedback)

### 9.2 RDSE — Response Depth Signal Extractor

**Purpose:** Extract a `qualityScore ∈ [0,1]` from the user's free-text response.

**Method:** Heuristic scoring of lexical signals:
- Word count normalized: `min(wordCount / 50, 1.0) × 0.3`
- Presence of reasoning words (*because*, *therefore*, *however*): +0.25
- Absence of vague filler (*I think*, *maybe*, *kind of*): +0.15
- Question marks (metacognitive curiosity): +0.10
- Domain-specific vocabulary hit: +0.20

$$q = \min\left(1.0, \sum_i w_i \cdot f_i(\text{text})\right)$$

`confusionCount` is incremented when phrases like *"I don't understand"* or *"can you explain"* are present.

### 9.3 SDSM — Socratic Dialogue State Machine

**States:** `PROBE → DEEPEN → SCAFFOLD → RECTIFY → REDIRECT → CONSOLIDATE → COMPLETE`

**Transition rules (simplified):**

| Condition | Next State |
|---|---|
| turn=0 | PROBE |
| quality ≥ 0.7 AND turns ≥ 2 | DEEPEN |
| quality < 0.4 OR confusionCount > 0 | SCAFFOLD |
| consecutiveScaffolds ≥ 3 | RECTIFY |
| turns ≥ 8 AND quality ≥ 0.6 | CONSOLIDATE |
| CONSOLIDATE reached | COMPLETE |

The state is passed to Claude as `next_state` in the request body, and Claude's system prompt contains instructions for each state's behaviour (probing questions, scaffolding hints, misconception correction, etc.).

### 9.4 CBKT-CS — Client-side Bayesian Knowledge Tracing

**Purpose:** Model the probability that the user has *learned* a concept, updating after every response.

**BKT is a Hidden Markov Model** with 4 parameters:
- $P(L_0)$ — prior probability of knowing the concept (initialised per domain)
- $P(T)$ — probability of transitioning to "known" after one opportunity
- $P(S)$ — probability of a "slip" (knows it but answers wrong)  
- $P(G)$ — probability of a "guess" (doesn't know but answers correctly)

**Update equations:**

$$P(L_t | \text{correct}) = \frac{P(L_{t-1})(1 - P(S))}{P(L_{t-1})(1-P(S)) + (1-P(L_{t-1}))P(G)}$$

$$P(L_t | \text{incorrect}) = \frac{P(L_{t-1})P(S)}{P(L_{t-1})P(S) + (1-P(L_{t-1}))(1-P(G))}$$

**After observing:** $P(L_t) = P(L_t | \text{obs}) + (1 - P(L_t | \text{obs})) \cdot P(T)$

In Sentio's implementation, `qualityScore` acts as a soft proxy for correctness: `quality ≥ 0.7` triggers the "correct" update path, `quality < 0.4` triggers the "incorrect" path.

**`clarityScore`** (shown in the UI) is derived:
$$\text{clarityScore} = \lfloor P(L_t) \times 100 \rfloor$$

**Initial priors per domain:**
```typescript
const DOMAIN_BKT_PRIORS = {
  general:    { pL: 0.20, pT: 0.12, pS: 0.10, pG: 0.08 },
  psychology: { pL: 0.15, pT: 0.10, pS: 0.12, pG: 0.06 },
  // ...
}
```
Lower priors for specialised domains reflect that users are less likely to have prior knowledge.

### 9.5 BGDC — Bias-Guided Dialogue Controller

Reads the user's `bias_scores` from the backend (fetched before the SSE stream starts) and injects them into Claude's context:

```python
bias_scores = profile.data[0].get("bias_scores") or {}
# Passed to stream_socratic_response() as context
```

If a user has a high `confirmation_bias` score, Claude is instructed to present counter-evidence and ask "what would change your mind?" This personalises the Socratic questioning to the user's known cognitive patterns.

### 9.6 SM-2 — Spaced Repetition Algorithm (for Insight Cards)

When a session completes and an Insight Card is generated, the concept is scheduled for review using the **SM-2 algorithm** (SuperMemo 2):

$$I_n = \begin{cases} 1 & n = 1 \\ 6 & n = 2 \\ I_{n-1} \times EF & n > 2 \end{cases}$$

**Ease Factor update:**
$$EF_{n+1} = EF_n + (0.1 - (5-q)(0.08 + (5-q) \times 0.02))$$

where $q \in [0,5]$ is derived from `clarityScore` and $EF \geq 1.3$ is enforced.

This drives the "Review" notification system — users are reminded to revisit concepts at optimal intervals for long-term retention.

---

## 10. Safety System — Deep Dive

### 10.1 Two-Layer Architecture

```
User input → check_input() → [REDIRECT if crisis] → AI call
                                                         │
                                                         ▼ streamed tokens
                                                check_output(chunk) → [DROP chunk if clinical overreach]
                                                         │
                                                         ▼
                                                    SSE to browser
```

**Layer 1 — Crisis Detection (Input):**
Keyword scan against 18 crisis phrases (suicide, self-harm, etc.). On match: save the entry is **blocked**, user receives Indian crisis helpline numbers (iCall, Vandrevala Foundation). This prevents the platform from being used as a substitute for mental health emergency services.

**Layer 2 — Clinical Overreach Prevention (Output):**
Every streamed token chunk passes through `check_output()` before being forwarded to the client. Seven regex patterns block clinical language:
```python
CLINICAL_OVERREACH_PATTERNS = [
    r'\bdiagnos\w*\b',        # diagnose, diagnosis, diagnosed
    r'\bdisorder\b',
    r'\billness\b',
    r'\bmedication\b',
    r'\bprescri\w*\b',        # prescribe, prescription
    r'\btherapist says\b',
    r'\byou have\s+\w+\s+(disorder|condition|syndrome)\b',
]
```

**Why regex over another LLM call?** Zero latency — every SSE chunk passes through in microseconds. An LLM guard call would add 200-500ms delay per chunk, making streaming feel broken.

### 10.2 Security — Row Level Security (RLS)

All user-scoped tables have Postgres RLS enabled:
```sql
CREATE POLICY "users_own_journal" ON journal_entries
  FOR ALL USING (user_id = auth.uid());
```

**Why this matters:** Even if an attacker obtains a valid `service_key`, the `auth.uid()` check runs server-side in Postgres. The backend passes the user's JWT via Supabase client initialisation, so Postgres enforces the policy. A bug in the API layer cannot return another user's journal entries.

### 10.3 Auth Flow

1. Frontend authenticates via Supabase Auth (email/password or OAuth)
2. Supabase issues a signed JWT containing `sub` (user UUID)
3. Frontend sends `Authorization: Bearer <jwt>` on every API request
4. Backend `get_user_id()` decodes the JWT:
   ```python
   result = supabase.auth.get_user(token)  # validates signature server-side
   return result.user.id
   ```
5. The user UUID is used in every DB query — no trust in client-provided IDs

---

## 11. Streaming — SSE Implementation

### 11.1 Why SSE over WebSockets?

| | SSE | WebSocket |
|---|---|---|
| Direction | Server → Client only | Bidirectional |
| Reconnect | Automatic (browser built-in) | Manual |
| HTTP/2 multiplexing | Yes | No |
| Overhead | Low (text frames) | Higher (binary framing) |
| Use case | LLM token streaming | Chat, gaming |

For one-way token streaming from Claude, SSE is the correct choice. WebSockets would add complexity with no benefit.

### 11.2 SSE Protocol in Sentio

```
data: {"text": "I"}\n\n
data: {"text": " noticed"}\n\n
data: {"text": " that"}\n\n
data: {"done": true, "clarity_score": 42, "next_state": "DEEPEN", "can_generate_insight": false}\n\n
```

The frontend parses this with a `ReadableStream` reader:
```typescript
const reader = res.body!.getReader()
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
    if (payload.text) message.content += payload.text
    if (payload.done) { /* update state machine */ }
  }
}
```

The `buffer` pattern handles **partial line splits** — a chunk boundary may arrive in the middle of a JSON line, so we accumulate until we see `\n`.

---

## 12. Performance & Production Engineering

### 12.1 Embedder Pre-warming

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _get_embedder)  # pre-warm in thread
    yield
```

`SentenceTransformer` model load takes ~7s (downloading weights on cold start). Pre-warming in a thread executor prevents the first `/ai/chat` request from blocking the event loop.

### 12.2 Weekly Insights Caching

```python
_WEEKLY_INSIGHT_CACHE: dict[str, list] = {}
cache_key = f"{user_id}_{current_year}_{current_week}"
if cache_key in _WEEKLY_INSIGHT_CACHE:
    return _WEEKLY_INSIGHT_CACHE[cache_key]
```

Claude synthesis costs ~$0.001 per call. Without caching, every dashboard load would call the API. The cache is keyed by `(user_id, ISO week)` — same insights for the entire week, regenerated each Monday. **Trade-off:** A new journal entry written mid-week won't update insights until next week. This is acceptable for the weekly insights feature.

### 12.3 Background Task Pattern

FastAPI's `BackgroundTasks` runs the NLP pipeline **after** the HTTP response is sent. This keeps the journal save latency < 200ms (just a Supabase insert), while Claude bias classification (which takes 2-4s) runs asynchronously.

**Risk:** If the server crashes between the response and the background task completion, the entry is saved but unanalysed. Mitigation: the frontend polls until `detected_biases != null` (max 24s), and the field's `null` state is a valid UI state showing "Analysis pending."

### 12.4 Deployment Architecture

```
GitHub (main branch) ──────────────────► Vercel
                                         (SPA, edge-cached)
                                         VITE_API_BASE_URL=https://mozoj4-sentio-backend.hf.space

GitHub (sentio-api/ subtree) ──────────► HuggingFace Spaces
  git subtree push --prefix sentio-api    (Docker, Python 3.11, port 7860)
  hf-space main                           uvicorn main:app --host 0.0.0.0 --port 7860
```

**Why subtree over submodule?** `git subtree` copies the directory history into the target repo — HF Spaces sees a clean standalone repo. Submodules require the target to clone recursively, which HF Spaces doesn't support.

---

## 13. Common Interview Questions & Answers

**Q: How do you prevent the bias classifier from hallucinating bias names?**
A: The parser validates every returned `bias_id` against a Python `set` of the 15 known IDs. Any ID not in the set is silently discarded before writing to the database. The confidence threshold (≥ 0.5) further filters low-certainty detections.

**Q: What happens if Claude is down?**
A: The bias classifier returns `[]` (empty list). The journal entry is saved with `detected_biases = []` (not `null`). The frontend treats `[]` as "no biases found" rather than "analysis pending" — a distinction maintained by the `null` vs `[]` sentinel pattern.

**Q: How would you scale this to 100,000 users?**
A: 1) Move background tasks to a real queue (Celery + Redis) to survive server restarts. 2) Add a Redis cache for bias fingerprints (currently in-memory). 3) Shard the `knowledge_articles` pgvector table by category. 4) Use Anthropic's Batch API for bias classification (50% cost reduction, async delivery within 24h).

**Q: Why not use OpenAI instead of Anthropic?**
A: Claude has better instruction-following for structured JSON output and stricter safety defaults — important for a mental wellness platform. Claude Haiku is also ~3× cheaper than GPT-3.5-turbo at equivalent quality for classification tasks.

**Q: How does the radar chart handle new users with no data?**
A: It shows a `FALLBACK_RADAR` with placeholder labels and uniform 0.3 scores. Once real data exists, the chart uses proportional scaling: each score is divided by the maximum score and multiplied by 0.85 (capped at 85% of chart radius). This ensures the radar is always visually meaningful regardless of absolute score magnitude.

**Q: What is your biggest technical risk in production?**
A: The HuggingFace free tier has a ~30s cold start if the Space has been idle. The first request after a cold start will hit the 7s model pre-warm AND the HF container spin-up, for a combined ~37s latency. Mitigation: a cron ping (`/health`) every 5 minutes keeps the Space warm. Long-term: move to HF Pro tier ($9/mo) which eliminates cold starts.

---

*— End of INTERVIEW_PREP.md — Built for Sentio v0.1.0, May 2026 —*
