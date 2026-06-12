# Sentio — Upgrade Log

Owner: Atharv (DS undergrad, AI/ML internships 2026–27)
Master context: `g:\project-updates\UPGRADE_CONTEXT.md`

---

## Repo verification (2026-06-11)

Checked every file named in the master plan against the actual code. All facts confirmed, one correction:

| Fact | Status |
|---|---|
| Vue 3 frontend `src/`; FastAPI backend `sentio-api/` | ✅ |
| pgvector(384), all-MiniLM-L6-v2, Cohere rerank | ✅ |
| 5-min `_USER_CTX_CACHE` in `routers/ai.py` | ✅ |
| "weekly digest cache in scheduler.py" | **CORRECTED** — `_weekly_digest()` in `services/scheduler.py` is an APScheduler email job (Mon 08:00 UTC) that queries DB fresh each run. It is not a data cache. The only in-memory cache is `_USER_CTX_CACHE`. |
| NO real memory — `ai_conversations.context_summary` always NULL | ✅ — column existed in schema but was never written; `stream_response()` had no history param |
| Bias classifier = Claude Haiku API, 15-class taxonomy | ✅ — `services/bias_classifier.py` → `claude-haiku-4-5-20251001` |
| 7 Episteme algorithms client-side | ✅ — `src/lib/episteme/algorithms.ts`: RDSE, SDSM, CBKT-CS, BGDC, SDSM→Bloom mapper, CPGAB, EGP |
| APScheduler active | ✅ — daily nudge 19:00 UTC + weekly digest Mon 08:00 UTC |
| No tests, no evals, no load tests | ✅ — no `tests/` directory found |
| Crash gap: `_process_entry` background task, returns 201 | ✅ — `routers/journal.py:153` |

---

---

## WS-1 — Three-Tier Memory (SHIPPED 2026-06-11)

### Decision: Option B (session-grouped conversations)
Frontend generates a stable UUID per chat session (`crypto.randomUUID()`) and carries it
through every message turn. Backend upserts into one `ai_conversations` row per session.
One `memory_episodes` row per session (unique index on `conversation_id`).

### Architecture
```
Turn 0..N  →  ai_conversations row (upserted, Option B)
Turn end   →  memory_episodes row (one per session, summary regenerated each turn)
Nightly    →  user_facts rows (consolidated from episodes > 7 days old)
Pre-chat   →  match_memory RPC → inject into system prompt
```

### Retrieval formula
```
score = cosine_sim(query, memory) × exp(−λ × age_days) × importance
λ_episode = 0.05  → half-life 14 days
λ_fact    = 0.005 → half-life 140 days
importance = min(2.0, 0.5 + 0.1×turns + 0.3×bias_mentions)
```
Cites: MemGPT (Packer 2023); Park et al. generative-agents memory-stream (2023).

### Files created / changed
| File | Change |
|---|---|
| `sentio-api/db/migration_memory.sql` | NEW — `memory_episodes`, `user_facts`, `match_memory()` RPC, `increment_fact_access()` RPC, RLS policies |
| `sentio-api/services/memory_service.py` | NEW — `save_episode`, `retrieve_memory`, `consolidate_user_episodes`, `get_user_memory`, `delete_memory_item`, `wipe_user_memory` |
| `sentio-api/services/claude_service.py` | ADD `memory_context` param to `_build_system()` and `stream_response()` |
| `sentio-api/routers/ai.py` | REWRITE — conversation upsert (Option B), memory retrieval pre-chat, episode save post-chat (asyncio.create_task), new endpoints: `GET /ai/memory`, `DELETE /ai/memory/{id}`, `DELETE /ai/memory` |
| `sentio-api/services/scheduler.py` | ADD `_consolidate_memories()` nightly job at 02:00 UTC |
| `src/pages/AIGuide.vue` | ADD `sessionConvId` ref; `sendGuideMessage` generates UUID on first message; `loadConversation` sets `sessionConvId = conv.id`; passes `conversation_id` in fetch body |
| `sentio-api/tests/test_memory_service.py` | NEW — 16 unit tests (all pass) |

### New API endpoints
| Endpoint | Purpose |
|---|---|
| `GET /ai/memory` | Returns user's episodes + facts for the memory panel |
| `DELETE /ai/memory/{id}?source=episode\|fact` | Delete one memory item |
| `DELETE /ai/memory` | GDPR wipe — all episodes + facts |

### Test results
```
16 passed in 1.99s
```
Covers: `_importance()` heuristic (4 tests), decay formula math (3 tests),
`save_episode` degradation (3 tests), `retrieve_memory` degradation + format (3 tests),
`consolidate_user_episodes` early-exit (1 test), `get_user_memory` shape (1 test),
`delete_memory_item` source validation (1 test).

### Pending user action
**Run in Supabase SQL editor:**
```
sentio-api/db/migration_memory.sql
```
(Idempotent — safe to re-run.)

### Interview talking points
1. **Why three tiers?** Working = sub-second (in-memory cache); episodic = per-session continuity; semantic = persistent patterns across weeks. Each tier has different decay rate, matching human memory consolidation.
2. **Decay formula** — same tri-factor (recency × relevance × importance) as Park et al. 2023 generative agents; λ tuned so 14-day episodes and 140-day facts.
3. **Option B conversation grouping** — one `ai_conversations` row per session, client-generated UUID. Enables single episode per session (coherent summary), history panel loads complete sessions. No frontend UX change.
4. **GDPR** — `DELETE /ai/memory` wipes all tiers. User-visible panel shows what's remembered with individual delete.
5. **Cost** — Claude Haiku @ ~$0.0001 per episode summary; embedding via local all-MiniLM-L6-v2 (free). Consolidation runs nightly (once, not per turn).

---

## WS-3 — Eval Harness (SHIPPED 2026-06-11)

### Files created
| File | Purpose |
|---|---|
| `sentio-api/scripts/eval_rag.py` | RAG eval: 51 labeled (query, article) pairs; precision@3 + MRR before/after Cohere rerank; writes `scripts/rag_eval_results.json` + `RESULTS.md` |
| `sentio-api/scripts/eval_bias.py` | Bias classifier eval: 30 entries, 2 per class × 15 classes; per-class precision/recall/F1 + agreement rate; writes `scripts/bias_eval_results.json` + `RESULTS.md` |
| `RESULTS.md` | Template populated by scripts when run |

### RAG eval method
- Auto-labeling: query generated per article, ground truth = all chunks whose title starts with the article name (handles "(1/3)" suffix)
- BEFORE rerank: top-3 from pgvector cosine similarity directly (match_threshold=0.0)
- AFTER rerank: Cohere rerank on top-10, take top-3 (same model as prod: `rerank-english-v2.0`)
- 51 queries across 26 psychology/CBT topics

### Bias eval method
- 30 journal entry snippets, 2 per class × 15 classes (same taxonomy as `bias_classifier.py`)
- Ground truth: author-labeled expected bias class(es)
- Classifier: production `classify_biases()` (Claude Haiku API)
- Per-class: TP/FP/FN → precision/recall/F1; macro averages + agreement rate
- Cost: ~$0.006 total

### Pending user actions (WS-3)
```bash
# From sentio-api/ with .env loaded:
python scripts/eval_rag.py       # requires SUPABASE_URL, SUPABASE_SERVICE_KEY, COHERE_API_KEY
python scripts/eval_bias.py      # requires ANTHROPIC_API_KEY
# Results appear in RESULTS.md and scripts/*.json
```

---

## WS-4 — Crash-Gap Fix + Locust Load Test (SHIPPED 2026-06-11)

### The crash gap
`create_entry` inserts a `journal_entries` row (content only), then hands off to a
background task. If the server dies between those two steps, the entry exists forever
with NULL biases/themes/sentiment. Frontend polls and never sees the analysis.

### Fix
1. **SQL column** (`analysis_status TEXT DEFAULT 'pending'`): added to `journal_entries`.
   Back-fill: existing rows with `detected_biases IS NOT NULL` → `'done'`.
2. **`_process_entry`** stamps:
   - `'processing'` on entry (prevents the sweep from double-queuing mid-run entries)
   - `'done'` on success (same UPDATE as biases/themes/sentiment)
   - `'failed'` on exception (allows separate monitoring/alerting)
3. **`update_entry`** resets `analysis_status = 'pending'` in the update payload when
   content changes, so the sweep recovers if the re-trigger dies too.
4. **APScheduler `_sweep_orphan_analyses()`**: runs every 10 min; queries for entries
   with `analysis_status='pending'` AND `created_at < NOW() - 5 min`; calls
   `_process_entry` directly per entry; continues on per-entry errors.

### Files created / changed
| File | Change |
|---|---|
| `sentio-api/db/migration_analysis_status.sql` | NEW — idempotent ALTER + back-fill + partial index |
| `sentio-api/routers/journal.py` | `_process_entry` status transitions; `update_entry` resets status on content change |
| `sentio-api/services/scheduler.py` | NEW `_sweep_orphan_analyses()` async job; registered with `IntervalTrigger(minutes=10)` |
| `sentio-api/scripts/locustfile.py` | NEW — Locust P50/P95 load test at 25/50 users |
| `sentio-api/tests/test_crash_gap.py` | NEW — 10 unit tests (all pass) |

### Locust load test
```bash
cd sentio-api
export SENTIO_TOKEN="<supabase-jwt-for-test-user>"
locust -f scripts/locustfile.py \
       --host https://<your-hf-space>.hf.space \
       --users 25 --spawn-rate 5 --run-time 60s --headless \
       --html scripts/locust_report_25.html
# Repeat with --users 50
```
Covers: `POST /journal`, `GET /journal`, `GET /journal/themes`, `POST /ai/chat` (SSE stream).
P50/P95 printed to stdout via `@events.quitting.add_listener`.

### Test results
```
26 passed in 2.13s (10 crash-gap + 16 memory)
```

### Pending user actions (WS-4)
1. **Run SQL migration** in Supabase query editor:
   ```
   sentio-api/db/migration_analysis_status.sql
   ```
2. **Install locust** and run the load test:
   ```bash
   uv pip install locust
   export SENTIO_TOKEN="..."
   locust -f scripts/locustfile.py --host https://... --users 25 --spawn-rate 5 --run-time 60s --headless
   locust -f scripts/locustfile.py --host https://... --users 50 --spawn-rate 10 --run-time 60s --headless
   # Paste P50/P95 numbers into RESULTS.md
   ```

### Interview talking points
1. **The crash gap** — Background task fires after 201 response; if process dies mid-task,
   entry row exists but analysis never lands. Detected by monitoring NULL biases on old entries.
2. **Status column as durable checkpoint** — `analysis_status` persists through server
   restarts. Sweep can see exactly which entries need recovery, no guessing.
3. **Why not a separate job table?** — Adding one column to the existing table avoids a join
   and keeps the data co-located. A separate `pending_jobs` table would be better for
   multi-worker fan-out, but HF Spaces runs one process.
4. **Idempotency** — `_process_entry` sets `'processing'` first, so even if two sweep runs
   overlap (e.g., first one is slow), the second won't double-queue `'processing'` entries.
5. **Locust P50/P95** — standard SLO metrics. SSE stream tasks are weighted lower (1 vs 3)
   because each holds a connection for 3–10 s; otherwise the concurrency limit of the HF
   Space would artificially inflate latency.

---

## STATUS

- [x] **WS-1 Three-tier memory** — DONE (2026-06-11); 16 tests pass
- [x] **WS-2 QLoRA bias classifier** — notebook READY (2026-06-12); user runs on Kaggle GPU (see RUN_GUIDE.md §3)
- [x] **WS-3 Eval harness** — DONE (2026-06-11); scripts pass py_compile; user runs against live Supabase to fill RESULTS.md
- [x] **WS-4 Crash-gap fix + Locust** — DONE (2026-06-11); 26 tests pass
- [x] **Docs** — README updated (memory, analysis_status, migrations, uv); `RUN_GUIDE.md` created (2026-06-12)
- [x] **Memory panel UI** — `src/pages/Memory.vue` + `/memory` route + "AI Memory" sidebar link
  (Plan WS-1 requirement: user-visible "what Sentio remembers" with per-item delete + full wipe).
  **Vite build green; Memory chunk emitted (2026-06-12).**
- [x] **Companion guide** — `INTERVIEW_PREP.md` finalized (full from-scratch teach: architecture,
  memory formula, RAG eval method, QLoRA mechanics, crash-gap state machine, demo script,
  Q&A bank, weakness pre-emption, reproduce-commands). Numbers table fills from RESULTS.md.

---

## WS-2 — QLoRA Bias Classifier (NOTEBOOK SHIPPED 2026-06-12)

### File
`sentio-ml/notebooks/sentio_bias_qlora.ipynb` — 21 cells, validated JSON, self-contained for Kaggle.

### Design
- **No external dataset** — generates its own 750 examples (50 × 15 classes) via Claude Haiku
  with prompt caching (~$0.12). Deliberate: no public dataset matches the 15-class taxonomy,
  and this *is* the distillation step (teacher = production classifier).
- **Base model**: `Qwen/Qwen2.5-3B-Instruct` (open, ungated, ChatML template) — chosen over the
  old DistilBERT script because the generative student outputs structured JSON + can extend
  the taxonomy without retraining a classification head.
- **QLoRA**: 4-bit NF4 + double quant, fp16 compute (T4); LoRA r=16/α=32/dropout 0.05 on all
  7 linear projections (~1.3% trainable params).
- **Training**: SFTTrainer, 4 epochs, effective batch 8, lr 2e-4 cosine, paged_adamw_32bit,
  max_grad_norm 0.3, eval/save per epoch, best-by-eval-loss. W&B project `sentio-bias-qlora`.
- **Data lifecycle in-notebook**: generation → JSONL validation (malformed-line skip, label
  whitelist, ≥20-word filter, class-distribution assert) → qualitative samples → stratified
  80/10/10 split → token-length audit vs max_seq_length=512.
- **Eval**: (a) generated 10% test split (format sanity); (b) 30-entry human-labeled holdout
  (2 × 15 classes, written fresh — NOT from training data) scored for BOTH student and Claude
  Haiku teacher → per-class P/R/F1, macro F1, exact-match agreement, head-to-head delta table.
- **Artifacts**: adapter + model card (with results table) pushed to HF Hub
  `<user>/sentio-bias-qlora-qwen25-3b`; `eval_results.json` in /kaggle/working.

### Production integration plan (post-run)
Cascade in `bias_classifier.py`: student (HF Space, free) at confidence ≥ 0.7, else Claude
Haiku fallback. Expected ~80% API-cost reduction. **Implementation deferred until the run
produces real numbers** — no fake integration before metrics exist.

### Interview talking points
Embedded in the notebook's final cell: why QLoRA, why distillation, why Qwen over DistilBERT,
synthetic-data validation strategy, why macro F1 + agreement rate, cascade threshold reasoning.

## Pending user actions (all workstreams)

- **WS-1**: Run `sentio-api/db/migration_memory.sql` in Supabase query editor
- **WS-3**: Run `python scripts/eval_rag.py` and `python scripts/eval_bias.py` (from `sentio-api/`)
- **WS-2**: Run QLoRA notebook on Colab/Kaggle GPU (implementation pending)
- **WS-4**: Run `sentio-api/db/migration_analysis_status.sql` in Supabase; run Locust and paste P50/P95 into RESULTS.md

## Verification quick-reference
```
cd sentio-api
uv run pytest tests/ -v        # 26 tests
```
