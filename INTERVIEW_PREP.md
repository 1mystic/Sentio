# Sentio — Interview Companion Guide

**Purpose**: teach Sentio from scratch so you can defend every layer in a 45-minute technical
deep-dive. Read top-to-bottom once, then drill the Q&A bank. Numbers marked `→ RESULTS.md` are
filled in after you complete `RUN_GUIDE.md`.

**One-line pitch**: *"Sentio is a full-stack mental-clarity platform — Vue 3 + FastAPI + Supabase —
where an LLM guide with real three-tier memory, a RAG pipeline with measured reranker lift, and a
distilled bias classifier help users identify cognitive biases in their own thinking. Every AI
claim in it is backed by an eval number I can reproduce."*

---

## Part 1 — The 60-second system tour

```
Vue 3 SPA (Vercel)
 ├─ 7 Socratic algorithms in client-side TypeScript (zero round-trip latency)
 └─ axios → FastAPI (HF Spaces Docker, port 7860)
      ├─ /ai/chat ............ SSE stream, Claude Haiku, 3 context layers injected
      ├─ /ai/memory .......... view/delete what Sentio remembers (GDPR surface)
      ├─ /journal ............ CRUD + background bias/NLP pipeline + crash-proof status
      ├─ /socratic, /assessments, /biases, /community, /therapists ...
      └─ Supabase (Postgres + pgvector + RLS + Auth)
           ├─ knowledge_articles (RAG KB, vector(384))
           ├─ memory_episodes / user_facts (memory tiers)
           └─ journal_entries (analysis_status state machine)
```

Five AI subsystems, each with a verifiable story:

| Subsystem | What it is | Evidence |
|---|---|---|
| Three-tier memory | episodic + semantic + working, decay-weighted retrieval | 16 unit tests; formula below |
| RAG pipeline | MiniLM embed → pgvector → Cohere rerank → top-3 | precision@3 + MRR before/after rerank → RESULTS.md |
| Bias classifier | Claude Haiku, 15-class, prompt-cached | 30-entry human-labeled per-class F1 → RESULTS.md |
| QLoRA student | Qwen2.5-3B distilled from Haiku | head-to-head F1 vs teacher → RESULTS.md |
| Crash-proof jobs | analysis_status state machine + orphan sweep | 10 unit tests; Locust P50/P95 → RESULTS.md |

---

## Part 2 — Three-tier memory (the headline feature)

### The problem
Before the upgrade, Sentio had only *caches* (a 5-min user-context dict). Close the tab and the AI
forgot you existed. `ai_conversations.context_summary` existed in the schema but was never written
— a classic "the column lies" finding from code exploration.

### The architecture (mirrors human memory consolidation)

| Tier | Store | Lifetime | Written | Read |
|---|---|---|---|---|
| Working | `_USER_CTX_CACHE` in-process dict | 5 min TTL | per request | per request |
| Episodic | `memory_episodes` (pgvector 384) | half-life ~14 days | end of each chat session | pre-chat retrieval |
| Semantic | `user_facts` (pgvector 384) | half-life ~140 days | nightly consolidation 02:00 UTC | pre-chat retrieval |

**Flow**: each chat turn ends → `asyncio.create_task(save_episode(...))` (non-blocking, SSE stream
closes immediately) → Claude Haiku writes a ≤80-word session summary → embedded with the same
all-MiniLM-L6-v2 used by RAG (no new model) → upserted as ONE row per session (unique index on
`conversation_id`). Nightly, episodes older than 7 days are consolidated: Haiku distills 2–4 durable
facts ("user is preparing for exams and shows recurring catastrophizing about results") into
`user_facts`, and the raw episodes are marked `consolidated`.

### The retrieval formula (memorize this)

```
score = cosine_sim(query, memory) × exp(−λ × age_days) × importance

λ_episode = 0.05   → half-life ≈ 14 days   (ln2/0.05 ≈ 13.9)
λ_fact    = 0.005  → half-life ≈ 140 days
importance = min(2.0, max(0.5, 0.5 + 0.1×turns + 0.3×bias_mentions))
```

This is the tri-factor scoring from **Park et al. 2023 (generative agents)** — recency × relevance
× importance — with the tiering idea from **MemGPT (Packer 2023)**. Computed **in SQL** inside the
`match_memory` RPC (a `UNION ALL` over both tables, ordered by score, `LIMIT k`) — one round trip,
no Python post-processing.

### Option B conversation grouping (a real bug fix)
The frontend used to reset the conversation id on *every* message, so each turn created a new
`ai_conversations` row — history was confetti. Fix: frontend generates `crypto.randomUUID()` on
the first message of a session, carries it through every turn; backend upserts one row per session
(insert accepts the client UUID). Resuming an old conversation from the history panel reuses its id,
so the episode summary keeps updating coherently.

### The ethics/GDPR surface (interviewers love this)
`/memory` page in the app ("AI Memory" in the sidebar): lists every fact and episode in plain
language, per-item delete, and a "Delete All Memory" wipe → `GET /ai/memory`,
`DELETE /ai/memory/{id}?source=episode|fact`, `DELETE /ai/memory`. One answer covers three
questions: *what if the memory is wrong?* (user deletes it), *how is this ethical for a mental-health
adjacent app?* (full transparency + control), *GDPR right-to-erasure?* (the wipe endpoint).

### Memory Q&A
- **Why not just stuff history into the context window?** Cost and signal. Full history grows
  unboundedly (Haiku is cheap but not free, and latency grows); retrieval injects only the top-3
  scoring memories. Decay ensures stale context doesn't pollute current conversations.
- **Why two λ values?** Episodes are situational ("stressed about Tuesday's exam") — worthless in a
  month. Facts are dispositional ("tends to catastrophize about academics") — durable. Different
  decay rates encode that difference; the 10× ratio (14d vs 140d) was a design choice, tunable per
  product feedback.
- **Failure modes?** Every memory function degrades gracefully — if the embedder or DB is down,
  `retrieve_memory` returns `""` and chat proceeds without memory (3 unit tests cover this).
  Consolidation is idempotent (consolidated flag) and per-user errors don't abort the batch.
- **Why in-process APScheduler and not Celery/pg_cron?** One free-tier container on HF Spaces;
  a separate worker doubles infra for a job that runs once nightly. Documented trade-off in the
  scheduler module: at scale, move to pg_cron or a worker dyno.

---

## Part 3 — RAG pipeline + its eval

### Pipeline
```
query → all-MiniLM-L6-v2 (384-d, pre-warmed at startup)
      → match_knowledge RPC (pgvector cosine, threshold 0.65, top-10)
      → Cohere rerank-english-v2.0 (cross-encoder, top-3)   [optional: degrades gracefully]
      → injected into Claude system prompt
```

### Why a reranker, and how do you KNOW it helps?
Bi-encoders (MiniLM) embed query and document independently — fast, but they miss interaction
signals. A cross-encoder reads query+document *together* — slower, so you only run it on the
top-10 shortlist. That's the standard retrieve-then-rerank pattern.

The proof is `scripts/eval_rag.py`: 51 labeled (query → relevant article) pairs across 26
psychology topics; measures **precision@3** and **MRR** with cosine-only vs cosine+rerank.
The delta is the reranker's earned keep → RESULTS.md. Honest methodology note: ground-truth
labels are auto-derived (query written per article; all chunks of that article are "relevant",
matched by title prefix since the seeder splits articles into "(1/3)" chunks) — scalable but
assumes one relevant article per query, which slightly understates precision when topics overlap.

### RAG Q&A
- **Why pgvector and not Pinecone/FAISS?** KB is small (tens of articles, hundreds of chunks);
  the data already lives in Supabase with RLS. A second vector store adds an infra hop and a
  consistency problem for zero recall benefit at this scale.
- **Why MiniLM-L6-v2?** 384-d, ~80 MB, CPU-fast, free, and the de-facto baseline sentence
  embedder. The eval harness exists precisely so a swap to a larger embedder is a measurable
  decision, not vibes.
- **Chunking?** Articles seeded in ~3 chunks with titled prefixes; retrieval is chunk-level.

---

## Part 4 — Bias classifier: API teacher + QLoRA student

### Production today: Claude Haiku
`services/bias_classifier.py` — Haiku with a 15-class CBT-grounded taxonomy (confirmation_bias,
catastrophizing, mind_reading, …) in a **prompt-cached** system block (`cache_control: ephemeral`),
strict-JSON output, post-validation against a known-ID whitelist, confidence floor 0.5.
~$0.0002/entry. Eval: `scripts/eval_bias.py`, 30 human-labeled entries (2×15 classes), per-class
precision/recall/F1 + macro + exact-match agreement → RESULTS.md.

### The fine-tuning answer (kills "so you're a prompt engineer?")
`sentio-ml/notebooks/sentio_bias_qlora.ipynb` — full teacher→student distillation on a free
Kaggle T4:

1. **Data**: 750 entries (50×15 classes) *generated and labeled by the production teacher*
   (Haiku, prompt-cached, ~$0.12). No public dataset matches this taxonomy — and synthesizing
   from the teacher IS the distillation step. In-notebook validation: malformed-line skip,
   label whitelist, ≥20-word filter, class-distribution assert, qualitative samples,
   stratified 80/10/10 split, token-length audit.
2. **Model**: Qwen2.5-3B-Instruct, 4-bit NF4 + double quant (fits 16 GB T4), LoRA r=16 α=32
   dropout 0.05 on all 7 linear projections (~1.3% trainable). SFTTrainer, 4 epochs, eff. batch 8,
   lr 2e-4 cosine, paged_adamw_32bit, max_grad_norm 0.3, best-by-eval-loss. W&B-tracked.
3. **Eval**: the SAME 30-entry human holdout scored for BOTH student and teacher → per-class
   F1 delta table + agreement rates → RESULTS.md. The generated 10% test split is reported but
   explicitly flagged as same-distribution sanity only.
4. **Serving plan**: confidence cascade — student (free, local) at ≥0.7, else Haiku fallback
   (~$0.0002). Expected ~80% API-cost cut. *Deliberately not wired into prod until the run
   produces real numbers* — that restraint is itself a talking point.

### Fine-tuning Q&A
- **Why QLoRA, mechanically?** Frozen 4-bit base; trainable fp16 low-rank matrices A·B (r=16)
  added to each linear layer; gradients flow only through ~40M adapter params. NF4 quantile
  quantization is information-optimal for normally-distributed weights; double quant compresses
  the quantization constants themselves. Memory: 3B fp32 ≈ 12 GB weights alone vs ~4 GB in NF4.
- **Why a generative 3B and not DistilBERT with a classification head?** (The repo has the old
  DistilBERT script — know it exists!) Generative output gives structured JSON with confidence
  AND span quotes, and extends to new classes without retraining a head. The trade-off is
  inference cost (3B > 66M), mitigated by the cascade.
- **Synthetic-data risk?** The student inherits the teacher's biases — acknowledged. That's why
  the holdout is human-written, not Haiku-generated, and why per-class F1 (not just macro) is
  reported: a class the teacher labels badly will show up.
- **Why macro F1?** Equal class weighting — all 15 distortions matter equally clinically; micro
  would let dominant classes mask failures on rare ones. Agreement rate (exact set match) is the
  stricter "got the whole label set right" metric.

---

## Part 5 — Reliability engineering (WS-4)

### The crash gap, honestly told
`POST /journal` inserted the row, queued `_process_entry` (bias + NLP) as a FastAPI background
task, and returned 201. If the container died (HF Spaces restarts are routine) the entry stayed
unanalyzed **forever** — frontend polls saw nothing, no retry existed.

### The fix: a durable state machine + sweeper
```
INSERT (DB default) ─→ pending ─→ processing ─→ done
                          │            └────────→ failed   (classifier error)
                          └── server crash? row stays 'pending'
                              └─ APScheduler sweep (every 10 min):
                                 pending AND created_at < now()−5min → re-run _process_entry
```
- Status column on `journal_entries` itself (not a separate job table): one fewer join, data
  co-located, and HF Spaces is single-process so multi-worker fan-out isn't needed — *yet*.
  Partial index `WHERE analysis_status='pending'` keeps the sweep query O(orphans).
- `processing` stamp prevents double-queuing if two sweeps overlap; `failed` is separately
  observable; editing entry content resets it to `pending` so re-analysis is also crash-proof.
- Migration back-fills `done` for rows that already have `detected_biases` — no false orphans.
- 10 unit tests: status transitions, failure stamping, secondary-exception swallowing, sweep
  filtering, continue-on-error, no-orphan no-op.

### Load test
`scripts/locustfile.py` — realistic mix (journal create/list/themes + SSE chat consumed to
completion), SSE weighted low because each stream holds a connection 3–10 s. P50/P95 at 25 and
50 users → RESULTS.md. Expected honest finding: P95 climbs sharply at 50 users on the single
free-tier container — and "what would you do about it" (paid container, SSE connection caps,
queue the chat) is the discussion you *want* to have.

### Safety (know this cold — it's a mental-health-adjacent app)
- **Input gate** runs BEFORE any token is spent or row saved: 20 crisis-keyword patterns →
  returns India crisis helplines (iCall, Vandrevala), Claude never called, entry not persisted.
- **Output filter**: every streamed chunk regex-scanned for clinical overreach
  (diagnosis/medication phrasing) and dropped before forwarding.
- Memory panel + wipe endpoint complete the responsible-AI story.

---

## Part 6 — Numbers table (fill from RESULTS.md after runs)

| Metric | Value |
|---|---|
| RAG precision@3 (cosine only) | __ |
| RAG precision@3 (+ Cohere rerank) | __ |
| RAG MRR before → after | __ → __ |
| Bias classifier (Haiku) macro F1 / agreement | __ / __ |
| QLoRA student macro F1 / agreement | __ / __ |
| Student vs teacher: classes won | __ / 15 |
| P50 / P95 @ 25 users | __ / __ ms |
| P50 / P95 @ 50 users | __ / __ ms |
| Backend tests | 26 passed (16 memory + 10 crash-gap) |
| Memory decay half-lives | 14 d episodes / 140 d facts |
| Cost: episode summary / bias classify | ~$0.0001 / ~$0.0002 |

---

## Part 7 — Demo script (5 minutes)

1. **Chat with memory**: open AI Guide, mention something specific ("I keep panicking about my
   stats exam"), finish the session. New session next day → guide references it. Show the
   network tab: `conversation_id` constant across turns (Option B).
2. **Memory panel**: sidebar → AI Memory. Show the episode summary, delete it, show the guide
   no longer knows. *That's the ethics demo.*
3. **Journal pipeline**: write an entry with an obvious distortion ("I always ruin everything").
   Show detected biases appear async; mention `analysis_status` flips pending→done underneath.
4. **Evals**: open RESULTS.md — "every AI component has a number, here's how each was measured,
   here's the script that reproduces it."
5. **If asked about scale**: Locust report HTML + the honest single-container finding.

## Part 8 — Reproduce every number

```bash
cd sentio-api
uv run pytest tests/ -v                  # 26 tests
python scripts/eval_rag.py               # RAG metrics → RESULTS.md
python scripts/eval_bias.py              # classifier F1 → RESULTS.md  (~$0.006)
locust -f scripts/locustfile.py --host <hf-space> --users 25 --spawn-rate 5 \
       --run-time 60s --headless         # P50/P95
# QLoRA: sentio-ml/notebooks/sentio_bias_qlora.ipynb on Kaggle T4 (RUN_GUIDE.md §3)
```

## Part 9 — Weakness pre-emption (say it before they find it)

- **Auto-labeled RAG ground truth** — scalable but single-relevant-article assumption; next step
  is a small human-judged query set.
- **30-entry bias holdout is small** — 2 per class gives directional, not tight, per-class F1;
  flagged in the eval script itself. Growing it is cheap and planned.
- **Synthetic training data inherits teacher bias** — mitigated by human holdout, not eliminated.
- **In-process scheduler dies with the container** — misfire_grace_time + the orphan sweep make
  jobs eventually-consistent; pg_cron is the scale answer.
- **Memory eval is qualitative** (a with/without-memory dialogue) — a quantitative memory benchmark
  (e.g., needle-style recall over sessions) is a known gap I'd build next.

---
*Maintained alongside `UPGRADE_LOG.md` (decisions log) and `RUN_GUIDE.md` (what to run).*
