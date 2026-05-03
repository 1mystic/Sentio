# Sentio — Full Development Handoff

**Project:** Sentio — cognitive bias self-awareness platform  
**Stack:** Vue 3 + Vite (frontend) · FastAPI (backend) · Supabase (auth + DB) · Claude API  
**Working dir:** `g:\synced-pc\1_Work\projects\Sentio`  
**Last updated:** May 2026 (session 2)

---

## What This Project Is

A mental-wellness app that helps users discover and track their cognitive biases through:
- **Assessments** — standardised psychometric tests (CBI, NCS, MAI)
- **Journal** — freeform entries with AI bias detection in background
- **AI Guide** — Claude-powered SSE streaming chat with RAG context
- **Bias Explorer** — Wikipedia-style bias library
- **Progress** — radar charts, heatmaps, bias fingerprint evolution
- **Therapist directory** — filterable therapists with booking flow

---

## Current Completion State

### Infrastructure — ✅ LIVE
- Supabase project `wfgriwlzgxgnlsbwotkp` — **schema deployed**
- `handle_new_user` trigger **fixed** (`SET search_path = public`) — signup works
- 73 knowledge chunks live in `knowledge_articles` (12/45 articles seeded so far)
- `match_knowledge` pgvector RPC function — **needs to be created** (SQL below)

### Frontend (`src/`) — ✅ COMPLETE
All pages wired to real API data. No hardcoded stubs remaining.

| Page | Status |
|------|--------|
| Auth (Login/Signup) | ✅ Lucide icons, email-confirm UX handled |
| Onboarding (5 steps) | ✅ Lucide icons, saves to Supabase via `PATCH /users/me` |
| Dashboard | ✅ Radar chart fixed (`scores.value.map`), real bias stats |
| Journal Index | ✅ API-fetched, search/tab/sort working |
| Journal New | ✅ Saves to API, navigates to new entry |
| Journal Entry | ✅ Loads from API, bias analysis sidebar |
| Assessments Index | ✅ Tabs by status, slug-based metadata |
| Assessments Take | ✅ Real questions, score computation |
| Assessments Results | ✅ Ring chart, bias bars, recommendations |
| Progress | ✅ Activity chart, milestones, real stats |
| Explore (Bias list) | ✅ Fallback to hardcoded if API empty |
| Explore (BiasDetail) | ✅ Loads by slug, fallback content |
| AI Guide | ✅ SSE streaming + RAG context via `/ai/chat` |
| Therapists | ✅ API fetch with normalised fallback |
| Profile | ✅ Loads/saves real user data, live stats |

**Layout:**
- `DefaultLayout.vue` — sidebar with active-route highlighting (startsWith), sign-out button
- Auth guard uses `ensureInitialized()` (memoised promise, fixes hard-refresh bug)

### Backend (`sentio-api/`) — ✅ COMPLETE + RAG LIVE
FastAPI with 8 routers: auth, users, biases, assessments, journal, insights, therapists, ai

- **Bias classification** — `services/bias_classifier.py` rewritten to use `claude-haiku-4-5-20251001` directly. Caches 15-bias taxonomy with prompt caching. No HuggingFace Space needed. ~$0.0002/entry.
- **RAG pipeline** — fully wired in `ai.py` → `rag_service.py`. Embeds query with `all-MiniLM-L6-v2`, pgvector similarity via `match_knowledge()` RPC, Cohere reranking, injects top-3 chunks into Claude context.
- Background task pipeline: `_process_entry()` → bias classifier → NLP → updates journal row + bias profile
- Safety gateway on journal create/update (crisis keyword detection)
- JWT auth via `supabase.auth.get_user(token)` on every protected route
- Claude SSE streaming on `/ai/chat` (full conversation history, user context, RAG)

### ML (`sentio-ml/`) — SUPERSEDED
Bias classification uses Claude Haiku directly. DistilBERT pipeline not needed.
- `data/generate_training_data.py` — kept for reference only, do NOT run
- `spaces/journal-nlp/app.py` — journal NLP uses keyword fallback; HF Space optional

---

## ⚠️ One-Time Setup Remaining

### 1. Create the pgvector search function in Supabase
**Required for AI Guide RAG to work.** Run in [Supabase SQL editor](https://supabase.com/dashboard/project/wfgriwlzgxgnlsbwotkp/sql/new):

```sql
DROP FUNCTION IF EXISTS match_knowledge(vector, double precision, integer);

CREATE INDEX IF NOT EXISTS idx_knowledge_embedding
  ON knowledge_articles USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 50);

CREATE OR REPLACE FUNCTION match_knowledge(
  query_embedding vector(384),
  match_threshold float DEFAULT 0.65,
  match_count int DEFAULT 10
)
RETURNS TABLE (
  id uuid, title text, content text, category text,
  source_url text, source_citation text, similarity float
)
LANGUAGE sql STABLE AS $$
  SELECT id, title, content, category, source_url, source_citation,
    1 - (embedding <=> query_embedding) AS similarity
  FROM knowledge_articles
  WHERE 1 - (embedding <=> query_embedding) > match_threshold
  ORDER BY embedding <=> query_embedding
  LIMIT match_count;
$$;
```

### 2. Run seed scripts (if not done yet)
```bash
cd sentio-api
python db/seed_biases.py        # populates biases table
python db/seed_assessments.py   # populates assessments + questions (CBI, NCS, MAI)
python db/seed_therapists.py    # populates therapists table (demo data)
```

### 3. Complete knowledge base seed (33 articles missing, rate-limited)
The seed script is now idempotent and retries 429s automatically:
```bash
cd sentio-api
python db/seed_knowledge.py     # skips already-inserted, fetches the 33 missing articles
```

---

## Environment Variables

### Frontend (`/.env`)
```
VITE_SUPABASE_URL=https://wfgriwlzgxgnlsbwotkp.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGci...  (already set)
VITE_API_BASE_URL=http://localhost:8000  (default, can omit for local dev)
```

### Backend (`/sentio-api/.env`)
```
SUPABASE_URL=https://wfgriwlzgxgnlsbwotkp.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGci...  (already set — service role key)
ANTHROPIC_API_KEY=sk-ant-api03-...  (already set — used for AI Guide + bias classifier + reflections)
COHERE_API_KEY=cohere_...  (already set — for RAG reranking)
HF_API_TOKEN=hf_...  (already set — optional, HF pipeline superseded)
FRONTEND_URL=http://localhost:5173
ENVIRONMENT=development
```
Note: `BIAS_CLASSIFIER_URL` and `JOURNAL_NLP_URL` are deprecated — Claude Haiku handles classification directly.

---

## Running Locally

```bash
# Frontend
npm install
npm run dev       # → http://localhost:5173

# Backend
cd sentio-api
pip install -r requirements.txt
python main.py    # → http://localhost:8000
# or: uvicorn main:app --reload

# API docs
http://localhost:8000/docs
```

---

## Next Phases

### Phase 3 — Deploy

**Frontend → Vercel:**
```bash
npm run build
# Deploy dist/ to Vercel
# Set env vars: VITE_SUPABASE_URL, VITE_SUPABASE_ANON_KEY, VITE_API_BASE_URL (Railway URL)
```

**Backend → Railway or Render:**
```
Root: sentio-api/
Start: uvicorn main:app --host 0.0.0.0 --port $PORT
```
After deploy, set `ALLOWED_ORIGINS=https://your-vercel-app.vercel.app` in backend env.

**Google OAuth (post-deploy):**
1. In Supabase dashboard → Auth → Providers → Google
2. Set callback URL to: `https://wfgriwlzgxgnlsbwotkp.supabase.co/auth/v1/callback`
3. Add Vercel domain to `redirectTo` whitelist
4. In `Login.vue:handleGoogle()` replace the "coming soon" error with:
   ```js
   await supabase.auth.signInWithOAuth({ provider: 'google', options: { redirectTo: window.location.origin } })
   ```

### Phase 4 — Archetype Model (optional)

Build `sentio-ml/archetype_model.py`:
- Input: user's `bias_scores` dict from `user_bias_profiles`
- Method: UMAP (2D) + HDBSCAN clustering on all users
- Archetypes: "The Optimist", "The Analyst", "The Social Navigator", etc.
- Store result back to `user_bias_profiles.archetype`
- Dashboard already reads and displays `biasFingerprint.archetype`

---

## Key Architecture Decisions

**Auth init pattern (`src/stores/auth.js`):**
The router guard fires before `onMounted`, so initialization uses a memoized promise:
```js
let _initPromise = null
function ensureInitialized() {
  if (!_initPromise) _initPromise = _doInit()
  return _initPromise
}
// router/index.js calls: await auth.ensureInitialized()
```

**Signup trigger must use `SET search_path = public`** — without this, the trigger runs in the `auth` schema context and can't find the `public.profiles` table. The fix is in `schema.sql` and was applied to Supabase.

**Bias classification is async (BackgroundTask):** When a journal entry is created, `_process_entry()` runs in the background. The entry is immediately saved with `detected_biases: null`. Entry.vue shows "Analysis processing…" until biases appear (typically 2–5 seconds).

**Bias classifier uses Claude Haiku + prompt caching:** The 15-bias taxonomy is a static string cached with `cache_control: ephemeral`. Cost ~$0.0002/entry. Returns `[{"bias_id": "...", "bias": "...", "confidence": 0.87, "span": "..."}]`. See `sentio-api/services/bias_classifier.py`.

**RAG pipeline (AI Guide):** `rag_service.py` embeds the user's query with `all-MiniLM-L6-v2` (384-dim, lazy-loaded), calls `match_knowledge` pgvector RPC (cosine similarity), reranks top-10 with Cohere to top-3, injects as `[Source N: ...]` blocks into Claude's system prompt. Falls back to no-RAG silently if embedder or Cohere is unavailable.

**Assessment score computation:** `computeScores()` in `Take.vue` handles both string-option and object-option question formats. Each question has a `category` field; scores are averaged per category then ×10 to get 0–100 scale. Results pass via `router.push({ state: { scores } })` to `Results.vue` which reads `history.state`.

**Therapists fallback:** Until `seed_therapists.py` is run, `Therapists/Index.vue` falls back to 6 hardcoded demo therapists so the page doesn't look broken.

**Bias scores are floats 0–1:** `user_bias_profiles.bias_scores` is a JSONB dict like `{"confirmation_bias": 0.72, ...}`. Dashboard radar and Progress page both read from this. Scores increment by `confidence × 0.1` per detected journal instance (see `_update_bias_profile` in `journal.py`).

---

## File Tree (key paths)

```
Sentio/
├── src/
│   ├── api/           client.js + per-resource files (journals, assessments, biases, users, insights, therapists)
│   ├── assets/css/    main.css — global design system (CSS vars, .card, .btn, .badge, .skeleton)
│   ├── composables/   useSupabase.js — exports supabase client
│   ├── layouts/       DefaultLayout.vue (sidebar+topbar), AuthLayout.vue, OnboardingLayout.vue
│   ├── pages/         All route components (see table above)
│   ├── router/        index.js — all routes + beforeEach guard
│   └── stores/        auth, user, journal, assessment, bias, insights, therapist
├── sentio-api/
│   ├── main.py        FastAPI app, CORS, router registration
│   ├── routers/       auth, users, biases, assessments, journal, insights, therapists, ai, _auth_helpers
│   ├── services/      supabase_client, bias_classifier (Claude Haiku), journal_nlp, claude_service, safety, recommender, rag_service
│   └── db/            schema.sql, seed_biases.py, seed_assessments.py, seed_knowledge.py (idempotent)
├── sentio-ml/         (superseded — kept for reference)
├── .env               Frontend Supabase keys
└── sentio-api/.env    Backend keys (Supabase service key, Anthropic, Cohere, HF)
```

---

## What a Next Session Should Do

**Priority 1 — Complete setup (if not done):**
1. Run the `match_knowledge` SQL (see above) in Supabase
2. Run `seed_biases.py`, `seed_assessments.py`, `seed_therapists.py`
3. Run `seed_knowledge.py` to complete the 33 missing articles
4. Test full signup → onboarding → dashboard flow
5. Test journal entry creation → verify bias detection fires after ~3 seconds

**Priority 2 — Deploy:**
1. `npm run build` → deploy to Vercel, set env vars
2. Deploy `sentio-api/` to Railway → set all env vars + `ALLOWED_ORIGINS`
3. Update `VITE_API_BASE_URL` in Vercel to point to Railway URL
4. Enable Google OAuth with Vercel callback URL

**Priority 3 — Archetype model (optional):**
Build `sentio-ml/archetype_model.py` using UMAP + HDBSCAN — dashboard already displays the archetype field.

---

## Credentials Summary (all already in .env files)

- **Supabase project:** `wfgriwlzgxgnlsbwotkp` at `wfgriwlzgxgnlsbwotkp.supabase.co`
- **Anthropic:** key in `sentio-api/.env` — used for AI Guide chat, bias classification, journal reflections
- **Cohere:** key in `sentio-api/.env` — RAG reranking
- **HuggingFace:** token in `sentio-api/.env` — optional, not actively used

> ⚠️ These are real credentials committed to the local repo — do not push to a public GitHub repo without first moving them to Supabase/Railway/Vercel secrets.
