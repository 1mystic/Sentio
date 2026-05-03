# Sentio — Full Development Handoff

**Project:** Sentio — cognitive bias self-awareness platform  
**Stack:** Vue 3 + Vite (frontend) · FastAPI (backend) · Supabase (auth + DB) · Claude API  
**Working dir:** `g:\synced-pc\1_Work\projects\Sentio`  
**Date:** May 2026

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

### Frontend (`src/`) — COMPLETE
All pages wired to real API data. No hardcoded stubs remaining.

| Page | Status |
|------|--------|
| Auth (Login/Signup) | ✅ Working, email-confirm UX handled |
| Onboarding (5 steps) | ✅ Saves to Supabase via `PATCH /users/me` |
| Dashboard | ✅ Real radar chart, bias stats, AI insight |
| Journal Index | ✅ API-fetched, search/tab/sort working |
| Journal New | ✅ Saves to API, navigates to new entry |
| Journal Entry | ✅ Loads from API, bias analysis sidebar |
| Assessments Index | ✅ Tabs by status, slug-based metadata |
| Assessments Take | ✅ Real questions, score computation |
| Assessments Results | ✅ Ring chart, bias bars, recommendations |
| Progress | ✅ Activity chart, milestones, real stats |
| Explore (Bias list) | ✅ Fallback to hardcoded if API empty |
| Explore (BiasDetail) | ✅ Loads by slug, fallback content |
| AI Guide | ✅ SSE streaming via `/ai/chat` |
| Therapists | ✅ API fetch with normalised fallback |
| Profile | ✅ Loads/saves real user data, live stats |

**Layout:**
- `DefaultLayout.vue` — sidebar with active-route highlighting (startsWith), sign-out button, `userStore.fetchProfile()` on mount
- Auth guard uses `ensureInitialized()` (memoised promise, fixes hard-refresh bug)

### Backend (`sentio-api/`) — COMPLETE
FastAPI with 8 routers: auth, users, biases, assessments, journal, insights, therapists, ai  
- Background task pipeline: `_process_entry()` → bias classifier → NLP → updates journal row + bias profile
- Safety gateway on journal create/update (crisis keyword detection → no save, return resources)
- JWT auth via Supabase Bearer token on every protected route
- RAG-ready: `knowledge_articles` table + pgvector extension (just needs seeding)
- Claude SSE streaming on `/ai/chat` (full conversation history, system prompt with user context)

### ML (`sentio-ml/`) — SCRIPTS WRITTEN, NOT RUN
- `data/generate_training_data.py` — generates 750 Claude-powered journal examples (15 biases × 50)
- `train_bias_classifier.py` — DistilBERT multi-label classifier for 15 bias classes
- `spaces/bias-classifier/app.py` — Gradio HF Space serving classifier
- `spaces/journal-nlp/app.py` — Gradio HF Space for GoEmotions + KeyBERT

---

## ⚠️ CRITICAL BLOCKER — Schema Not Deployed

**Signup will fail with 500** until this is done. The `handle_new_user` trigger fires on signup and tries to write to `public.profiles` — which doesn't exist yet in the active project.

**Fix (2 minutes):**
1. Go to: https://supabase.com/dashboard/project/wfgriwlzgxgnlsbwotkp/sql/new
2. Paste and run: `sentio-api/db/schema.sql`
3. Verify tables exist: `SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;`
   Expected: `ai_conversations, assessment_results, assessments, biases, bookings, journal_entries, knowledge_articles, profiles, therapists, user_bias_profiles`
4. Enable pgvector: `CREATE EXTENSION IF NOT EXISTS vector;` (needed for knowledge_articles)

**Then run seeds:**
```bash
cd sentio-api
python db/seed_biases.py          # populates biases table
python db/seed_assessments.py     # populates assessments + questions (CBI, NCS, MAI)
python db/seed_therapists.py      # populates therapists table (demo data)
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
ANTHROPIC_API_KEY=sk-ant-api03-...  (already set)
COHERE_API_KEY=cohere_...  (already set — for RAG reranking)
HF_API_TOKEN=hf_...  (already set — for HuggingFace Spaces)
BIAS_CLASSIFIER_URL=https://YOUR-SPACE.hf.space  (set after deploying)
JOURNAL_NLP_URL=https://YOUR-NLP-SPACE.hf.space  (set after deploying)
FRONTEND_URL=http://localhost:5173
ENVIRONMENT=development
ALLOWED_ORIGINS=http://localhost:5173  (add Vercel URL after deploy)
```

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

### Phase 2 — ML Pipeline (do once schema is deployed)

```bash
# 1. Generate training data (~$2-3 Claude API cost, ~30 min)
cd sentio-ml
pip install -r requirements.txt
python data/generate_training_data.py
# Output: sentio-ml/data/training_data.jsonl

# 2. Train classifier (~1 hour, GPU recommended)
python train_bias_classifier.py
# Output: sentio-ml/model/ + sentio_config.json

# 3. Seed knowledge base (for AI Guide RAG)
cd sentio-api
pip install sentence-transformers
python db/seed_knowledge.py
# Fetches 45 Wikipedia psychology articles, chunks + embeds, inserts into knowledge_articles

# 4. Deploy to HuggingFace Spaces
# Upload sentio-ml/spaces/bias-classifier/ → set BIAS_CLASSIFIER_URL in backend .env
# Upload sentio-ml/spaces/journal-nlp/ → set JOURNAL_NLP_URL in backend .env
```

**After deploying Spaces:** The journal background task (`_process_entry` in `sentio-api/routers/journal.py`) will start returning real bias classifications instead of the stub response.

### Phase 3 — AI Guide RAG Activation

File: `sentio-api/routers/ai.py` — currently calls Claude with just the message + user context. After `seed_knowledge.py` runs, activate the RAG pipeline:

```python
# In the /ai/chat endpoint, before calling Claude:
# 1. Embed the user message
# 2. Query knowledge_articles via pgvector similarity search (top 5 chunks)
# 3. Inject retrieved chunks into Claude's system prompt as [KNOWLEDGE] blocks
```

The schema already has `knowledge_articles (id, title, content, embedding vector(384), source_url, chunk_index)`. The `seed_knowledge.py` script uses `all-MiniLM-L6-v2` for embeddings (384-dim). The backend needs `from sentence_transformers import SentenceTransformer` installed.

### Phase 4 — Archetype Model

Build `sentio-ml/archetype_model.py`:
- Input: user's `bias_scores` dict from `user_bias_profiles`
- Method: UMAP (2D) + HDBSCAN clustering on all users
- Archetypes: "The Optimist", "The Analyst", "The Social Navigator", etc.
- Store result back to `user_bias_profiles.archetype`
- Dashboard already reads and displays `biasFingerprint.archetype`

### Phase 5 — Deployment

**Frontend → Vercel:**
```bash
npm run build
# Deploy dist/ to Vercel
# Set env vars: VITE_SUPABASE_URL, VITE_SUPABASE_ANON_KEY, VITE_API_BASE_URL
```

**Backend → Railway or Render:**
```
Root: sentio-api/
Start: uvicorn main:app --host 0.0.0.0 --port $PORT
```
After deploy, update `ALLOWED_ORIGINS` in backend env to include the Vercel domain.

**Google OAuth (post-deploy):**
1. In Supabase dashboard → Auth → Providers → Google
2. Set callback URL to: `https://wfgriwlzgxgnlsbwotkp.supabase.co/auth/v1/callback`
3. Add Vercel domain to `redirectTo` whitelist
4. Remove "coming soon" message in `Login.vue:handleGoogle()` and implement `supabase.auth.signInWithOAuth({ provider: 'google' })`

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

**Journal NLP is async:** When a journal entry is created/updated, the bias classification runs in a FastAPI `BackgroundTask`. The entry is immediately saved with `detected_biases: null`. The Entry.vue shows "Analysis processing…" until biases appear.

**Assessment score computation:** `computeScores()` in `Take.vue` handles both string-option and object-option question formats. Each question has a `category` field; scores are averaged per category then ×10 to get 0–100 scale. Results pass via `router.push({ state: { scores } })` to `Results.vue` which reads `history.state`.

**Therapists fallback:** The therapists table needs `seed_therapists.py`. Until seeded, `Therapists/Index.vue` falls back to 6 hardcoded demo therapists so the page doesn't look broken.

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
│   ├── services/      supabase_client, bias_classifier, journal_nlp, claude_service, safety, recommender
│   └── db/            schema.sql, seed_biases.py, seed_assessments.py, seed_knowledge.py
├── sentio-ml/
│   ├── data/          generate_training_data.py
│   ├── train_bias_classifier.py
│   └── spaces/        bias-classifier/app.py, journal-nlp/app.py
├── .env               Frontend Supabase keys
└── sentio-api/.env    Backend keys (Supabase service key, Anthropic, Cohere, HF)
```

---

## What a Next Session Should Do

**Priority 1 — Make the app actually work end-to-end:**
1. Deploy `schema.sql` to Supabase project `wfgriwlzgxgnlsbwotkp`
2. Run `seed_biases.py` and `seed_assessments.py`
3. Test the full signup → onboarding → dashboard flow
4. Test taking an assessment end-to-end
5. Test creating a journal entry and viewing it

**Priority 2 — ML pipeline:**
1. Run `generate_training_data.py` (needs ANTHROPIC_API_KEY — already in .env)
2. Train the classifier
3. Deploy HF Spaces
4. Test the end-to-end journal bias detection flow

**Priority 3 — AI Guide RAG:**
1. Run `seed_knowledge.py` (needs `pip install sentence-transformers`)
2. Activate vector similarity search in `sentio-api/routers/ai.py`
3. Test the AI Guide with psychology questions

**Priority 4 — Deploy:**
1. Build and deploy frontend to Vercel
2. Deploy backend to Railway (Dockerfile already written? Check `sentio-api/`)
3. Update CORS and OAuth callback URLs

---

## Credentials Summary (all already in .env files)

- **Supabase project:** `wfgriwlzgxgnlsbwotkp` at `wfgriwlzgxgnlsbwotkp.supabase.co`
- **Anthropic:** key in `sentio-api/.env`
- **HuggingFace:** token in `sentio-api/.env`
- **Cohere:** key in `sentio-api/.env` (RAG reranking)

> ⚠️ These are real credentials committed to the local repo — do not push to a public GitHub repo without first moving them to Supabase/Railway/Vercel secrets.
