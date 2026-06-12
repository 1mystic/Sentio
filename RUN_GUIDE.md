# Sentio — Run Guide (post-upgrade user actions)

Everything you must run yourself, in order. Each step is independent unless noted.
Companion docs: `UPGRADE_LOG.md` (decisions + talking points) · `RESULTS.md` (metrics land here).

---

## 1. SQL migrations (Supabase SQL Editor) — ~2 min

Run both, in this order. Both are **idempotent** (safe to re-run).

| # | File | What it adds |
|---|------|--------------|
| 1 | `sentio-api/db/migration_memory.sql` | `memory_episodes` + `user_facts` tables, `match_memory()` + `increment_fact_access()` RPCs, RLS policies |
| 2 | `sentio-api/db/migration_analysis_status.sql` | `journal_entries.analysis_status` column + back-fill + partial index |

Verify:
```sql
SELECT table_name FROM information_schema.tables
WHERE table_name IN ('memory_episodes','user_facts');
SELECT column_name FROM information_schema.columns
WHERE table_name='journal_entries' AND column_name='analysis_status';
```

---

## 2. Eval harness (WS-3) — local, ~5 min, ~$0.006

From `sentio-api/` with `.env` loaded (needs `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `COHERE_API_KEY`, `ANTHROPIC_API_KEY`):

```bash
cd sentio-api
uv venv && .venv\Scripts\activate
uv pip install -r requirements.txt
python scripts/eval_rag.py        # RAG precision@3 + MRR, before/after Cohere rerank
python scripts/eval_bias.py       # 30-entry bias classifier eval (~$0.006 Claude credits)
```

Results auto-append to `RESULTS.md` + write `scripts/rag_eval_results.json` and `scripts/bias_eval_results.json`.

---

## 3. QLoRA notebook (WS-2) — Kaggle, ~60–75 min total, ~$0.20

**No external dataset needed** — the notebook generates its own training data via Claude Haiku (the production teacher model). This is by design: it's teacher-student distillation, and no public dataset matches Sentio's exact 15-class taxonomy.

1. Go to [kaggle.com/code](https://www.kaggle.com/code) → **New Notebook** → File → Import Notebook → upload `sentio-ml/notebooks/sentio_bias_qlora.ipynb`
2. Settings (right panel):
   - **Accelerator**: GPU T4 x2 (or P100)
   - **Internet**: ON
3. Add-ons → Secrets → add three secrets:
   - `ANTHROPIC_API_KEY` (required — data generation + teacher eval, ~$0.20)
   - `HF_TOKEN` (HuggingFace write token — for pushing the adapter; [create here](https://huggingface.co/settings/tokens))
   - `WANDB_API_KEY` (from [wandb.ai/authorize](https://wandb.ai/authorize); or set the value to `off` to skip tracking)
4. **Run All**. Phases: data gen ~15–20 min → training ~35–45 min → eval ~10 min.
5. When done, download `/kaggle/working/eval_results.json` and paste the student-vs-teacher table into `RESULTS.md` under a `## WS-2` heading.
6. The adapter is pushed to `https://huggingface.co/<your-username>/sentio-bias-qlora-qwen25-3b` automatically.

If the T4 runs out of memory during training: in the training cell set `per_device_train_batch_size=1` and `gradient_accumulation_steps=8`.

---

## 4. Locust load test (WS-4) — local, ~5 min

Needs a Supabase JWT for a dedicated test account (sign up a throwaway user in the app, grab the `access_token` from browser devtools → Local Storage → supabase auth key).

```bash
cd sentio-api
uv pip install locust
set SENTIO_TOKEN=<jwt>                      # PowerShell: $env:SENTIO_TOKEN="<jwt>"

locust -f scripts/locustfile.py --host https://mozoj4-sentio-backend.hf.space ^
       --users 25 --spawn-rate 5 --run-time 60s --headless --html scripts/locust_report_25.html

locust -f scripts/locustfile.py --host https://mozoj4-sentio-backend.hf.space ^
       --users 50 --spawn-rate 10 --run-time 60s --headless --html scripts/locust_report_50.html
```

P50/P95 per endpoint print to stdout at the end — paste both runs into `RESULTS.md` under `## WS-4 Load Test`.

> Note: HF Spaces free tier is a single container — expect P95 to climb sharply at 50 users on `/ai/chat` (SSE holds connections). That's a legitimate finding, not a failure; it's the talking point for "when would you move off free tier."

---

## 5. Backend tests (verify nothing broke) — local, ~10 s

```bash
cd sentio-api
uv run pytest tests/ -v        # expect: 26 passed (16 memory + 10 crash-gap)
```

---

## 6. Deploy

```bash
# Backend → HF Spaces (after migrations are applied!)
git add -A && git commit -m "feat: three-tier memory, eval harness, crash-gap fix, QLoRA notebook"
git subtree split --prefix=sentio-api --branch hf-deploy
git push hf-space hf-deploy:main --force
git branch -D hf-deploy

# Frontend → Vercel (auto on push)
git push origin main
```

**Order matters**: run the SQL migrations (step 1) *before* deploying the backend — the new code queries `analysis_status` and the memory tables on startup paths.

---

## Quick status checklist

- [ ] Step 1 — both SQL migrations applied
- [ ] Step 2 — `RESULTS.md` has RAG + bias eval numbers
- [ ] Step 3 — Kaggle notebook run; adapter on HF Hub; WS-2 numbers in `RESULTS.md`
- [ ] Step 4 — Locust P50/P95 at 25 + 50 users in `RESULTS.md`
- [ ] Step 5 — 26 tests pass locally
- [ ] Step 6 — deployed
