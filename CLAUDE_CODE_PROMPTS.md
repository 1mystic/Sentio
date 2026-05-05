# Sentio — Claude Code Prompts
## Ready-to-Use Prompts for Each Build Phase

Each prompt below is designed to be dropped directly into Claude Code with your project directory open.

---

## PROMPT 0A: Directory Audit & Cleanup

```
I have a Vue 3 + Vite project directory that is a messy combination of two previous projects called "Mindfluence" and "VeraMind". I'm rebuilding it as "Sentio" — a cognitive bias self-awareness platform.

First, audit the entire project directory and give me:
1. A complete file tree (2 levels deep)
2. For each file, classify as: KEEP, REMOVE, or REPURPOSE
   - KEEP: Working auth composables, Supabase client setup, useful Vue components, config files
   - REMOVE: Nuxt-specific files (nuxt.config.js unless used), dead routes, duplicate components, Mindfluence/VeraMind branding
   - REPURPOSE: Files that can be adapted for Sentio

Do NOT make any changes yet. Just give me the audit report.
```

---

## PROMPT 0B: Project Rename & Design System

```
I'm renaming this project from Mindfluence/VeraMind to "Sentio". Apply the following changes:

1. RENAME all occurrences of "Mindfluence", "MindFluence", "VeraMind", "Veramind" to "Sentio" in:
   - package.json (name field)
   - index.html (title)
   - README.md
   - All .vue files (text content, meta tags)
   - app.vue
   
2. REPLACE the existing CSS design system in assets/css/main.css with the Sentio Design System (I'll paste it below).

3. ADD Google Fonts import at the top of main.css:
   @import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300;1,9..40,400&display=swap');

4. INSTALL: lucide-vue-next (npm install lucide-vue-next)

5. VERIFY: npm run dev starts without errors after all changes.

[PASTE DESIGN_SYSTEM.md CSS section here when running this prompt]
```

---

## PROMPT 0C: Route Scaffold & Pinia Stores

```
Scaffold the complete Sentio application structure.

ROUTES to create (create stub .vue files for each):
/                          → pages/index.vue (landing page stub)
/onboarding                → pages/onboarding/index.vue
/onboarding/welcome        → pages/onboarding/welcome.vue
/onboarding/baseline       → pages/onboarding/baseline.vue
/onboarding/interests      → pages/onboarding/interests.vue
/onboarding/complete       → pages/onboarding/complete.vue
/dashboard                 → pages/dashboard.vue
/explore                   → pages/explore/index.vue
/explore/:slug             → pages/explore/[slug].vue
/assessments               → pages/assessments/index.vue
/assessments/:id           → pages/assessments/[id].vue
/assessments/:id/results   → pages/assessments/[id]/results.vue
/journal                   → pages/journal/index.vue
/journal/new               → pages/journal/new.vue
/journal/:id               → pages/journal/[id].vue
/therapists                → pages/therapists/index.vue
/therapists/:id            → pages/therapists/[id].vue
/ai-guide                  → pages/ai-guide.vue
/profile                   → pages/profile.vue

Each stub should:
- Use <script setup> composition API
- Have a simple <template> with the page name as an h1
- Import the Sentio default layout

LAYOUTS to create:
- layouts/DefaultLayout.vue (sidebar 240px + topbar 60px + main content)
- layouts/AuthLayout.vue (centered card, no sidebar)
- layouts/OnboardingLayout.vue (progress stepper at top)

PINIA STORES to create in stores/:
- useAuthStore.js (user, isAuthenticated, login, logout, signup)
- useUserStore.js (profile, biasProfile, archetype, updateProfile)
- useBiasStore.js (allBiases, userBiasScores, fetchBiases, getBiasBySlug)
- useJournalStore.js (entries, currentEntry, createEntry, fetchEntries)
- useAssessmentStore.js (available, results, submitAssessment)

ROUTER (update router/index.js or equivalent):
- Set up all routes with correct layout components
- Add navigation guard: redirect to /onboarding if !user.onboarding_completed
- Add auth guard: redirect to /login if !isAuthenticated (except /, /login, /signup)
```

---

## PROMPT 1A: FastAPI Backend Setup

```
Set up the Sentio FastAPI backend from scratch. Create a new directory called sentio-api/ in my project.

Structure to create:
sentio-api/
├── main.py
├── requirements.txt
├── .env.example
├── routers/
│   ├── __init__.py
│   ├── auth.py
│   ├── users.py
│   ├── assessments.py
│   ├── journal.py
│   ├── insights.py
│   ├── therapists.py
│   └── ai.py
├── models/
│   ├── __init__.py
│   ├── user.py
│   ├── bias.py
│   ├── journal.py
│   └── assessment.py
├── services/
│   ├── __init__.py
│   ├── supabase_client.py
│   ├── bias_classifier.py     (stub — calls HF Space)
│   ├── journal_nlp.py         (stub — calls HF Space)
│   ├── recommender.py         (stub)
│   ├── claude_service.py      (stub — calls Anthropic API)
│   └── safety.py              (content safety checker)
├── db/
│   ├── __init__.py
│   └── queries.py
└── utils/
    └── validators.py

requirements.txt should include:
fastapi, uvicorn[standard], supabase, anthropic, python-dotenv, httpx, pydantic, 
sentence-transformers, keybert, transformers, torch, cohere

Implement fully:
1. main.py with CORS, all routers registered, /health endpoint
2. services/safety.py with SafetyChecker class (crisis keyword detection)
3. All router files with correct endpoint signatures (stub implementations returning placeholder data)
4. supabase_client.py with client initialization

The safety checker must intercept ANY input containing crisis keywords before sending to AI.
Crisis keywords: ["suicide", "kill myself", "end my life", "self harm", "hurt myself", "don't want to live"]
Response: Return crisis resources (iCall India: 9152987821, Vandrevala: 1860-2662-345)
```

---

## PROMPT 1B: Supabase Schema Deployment

```
Deploy the Sentio database schema to Supabase.

Create a file: sentio-api/db/schema.sql with ALL the table definitions from the ARCHITECTURE.md database schema section.

Also create: sentio-api/db/seed_biases.py

The seed script should insert 30 cognitive biases into the biases table.
Use this exact list with accurate data:

Biases to seed (name, category, description, example):
Memory:
1. Availability Bias — overweighting recent/vivid events
2. Rosy Retrospection — remembering past as better than it was
3. Fading Affect Bias — emotional memories fade faster than factual
4. Misinformation Effect — post-event info corrupts memory
5. Source Confusion — misattributing source of a memory

Social:
6. Fundamental Attribution Error — underestimating situational factors in others' behavior
7. Halo Effect — one positive trait colors perception of everything
8. In-group Bias — favoring people similar to us
9. False Consensus Effect — overestimating how many agree with us
10. Spotlight Effect — overestimating how much others notice us

Decision-Making:
11. Anchoring Bias — over-relying on first piece of information
12. Sunk Cost Fallacy — continuing due to past investment
13. Status Quo Bias — preference for current state of affairs
14. Planning Fallacy — underestimating time/cost of tasks
15. Optimism Bias — overestimating positive outcomes for oneself

Self-Perception:
16. Dunning-Kruger Effect — overconfidence in areas of low competence
17. Impostor Syndrome — undervaluing competence despite evidence
18. Self-Serving Bias — attributing success to self, failure to circumstance
19. Fundamental Attribution Error (Self) — overestimating character in own behavior
20. Narrative Fallacy — constructing coherent stories about ourselves that may not be accurate

Belief:
21. Confirmation Bias — seeking info that confirms existing beliefs
22. Belief Perseverance — maintaining beliefs despite contradicting evidence
23. Illusory Truth Effect — repetition increases perceived truth
24. Appeal to Authority — accepting claims based on source status
25. Black and White Thinking — all-or-nothing categorization

Reasoning:
26. Gambler's Fallacy — believing past random events affect future probabilities
27. Post Hoc Reasoning — assuming correlation implies causation
28. Overgeneralization — one instance → universal rule
29. Catastrophizing — assuming worst-case scenario
30. Emotional Reasoning — assuming feelings reflect reality

For each bias, generate:
- slug: kebab-case name
- category: one of [memory, social, decision, self, belief, reasoning]
- description: 2-3 sentences, plain language
- example: one realistic scenario (1-2 sentences, first or third person)
- detection_signals: JSON array of text patterns that suggest this bias (for BiasClassifier labels)
```

---

## PROMPT 1C: Bias Explorer UI

```
Build the Bias Explorer — /explore and /explore/:slug pages.

This is the educational core of Sentio. It should feel like a premium reference guide.

/explore page requirements:
- Grid of BiasCard components (3 columns on desktop, 2 on tablet, 1 on mobile)
- Filter bar: category pills (Memory, Social, Decision, Self-Perception, Belief, Reasoning)
- Search input: filter by bias name or description
- Sort: alphabetical, by category, by "resonance" (user's personal score)
- Each BiasCard shows: bias name, category badge, 1-line description, personal resonance bar (if profile exists)
- Cards are clickable → navigate to /explore/:slug

/explore/:slug page requirements:
- Bias name (display font, large)
- Category badge
- Definition paragraph (clear, accessible, not jargon-heavy)
- "In real life" section: narrative example
- Research note: 1-2 sentences on research backing with fictional citation
- Related biases: 3-4 linked cards (smaller)
- Quick reflection prompt: "Have you noticed this in yourself recently? [Journal about it →]"
- Personal resonance score (from user's bias profile): "Our analysis suggests moderate resonance with this bias in your recent journal entries."

Disclaimer: "Bias scores are educational estimates, not clinical assessments."

API integration:
- GET /explore: fetch from Supabase biases table directly via Pinia store
- User's personal resonance: from useUserStore().biasProfile (load if available)
- If no bias profile yet: show "Complete your first journal entry to see your personal pattern"

Design notes:
- Each category has its own accent color (see DESIGN_SYSTEM.md)
- Bias cards have a 3px top border in the category color
- Resonance bar uses teal fill on gray track
- Keep it intellectual-looking, not gamified
```

---

## PROMPT 2A: BiasClassifier Training

```
Implement the complete BiasClassifier training pipeline.

Create directory: sentio-ml/
├── data/
│   ├── synthetic/
│   │   └── .gitkeep
│   └── processed/
│       └── .gitkeep
├── notebooks/
│   └── 01_bias_classifier.ipynb
├── src/
│   ├── data/
│   │   ├── __init__.py
│   │   ├── dataset.py      (BiasDataset class for PyTorch)
│   │   └── preprocessing.py (text cleaning, tokenization)
│   ├── models/
│   │   ├── __init__.py
│   │   └── bias_classifier.py  (DistilBERT + classification head)
│   └── training/
│       ├── __init__.py
│       ├── train.py        (full training loop with MLflow)
│       └── evaluate.py     (metrics: macro F1, per-class F1)
├── configs/
│   └── bias_classifier.yaml
├── requirements.txt
└── README.md

Implement train.py with:
- HuggingFace Trainer API OR custom PyTorch training loop (your choice, Trainer is easier)
- MLflow tracking: log all hyperparams, train/val loss, macro F1, per-class F1 per epoch
- BCEWithLogitsLoss (multi-label)
- Early stopping (patience=2 on val macro F1)
- Save best model checkpoint

Also create: generate_training_data.py
- Takes bias labels list as input
- Uses Anthropic API to generate synthetic training examples
- Prompt template for generating realistic journal entries exhibiting each bias
- Saves to data/synthetic/bias_training.jsonl
- Include validation step (basic sanity checks on generated data)

configs/bias_classifier.yaml:
model_name: distilbert-base-uncased
num_labels: 15
max_length: 256
batch_size: 16
learning_rate: 2e-5
num_epochs: 5
dropout: 0.3
threshold: 0.45
mlflow_experiment: sentio-bias-classifier
```

---

## PROMPT 3A: Dashboard with Bias Fingerprint

```
Build the Sentio Dashboard — /dashboard.

This is the user's personal cognitive profile. Make it feel like premium data analytics.

Components to build:

1. BiasFingerprint.vue (radar chart)
   - Chart.js radar, 5 axes: Memory, Social, Decision-Making, Self-Perception, Belief
   - Teal fill (#1D9E93 at 15% opacity), teal border
   - Animates on load
   - Shows "Not enough data" state if < 3 journal entries
   - Title: "Your Cognitive Pattern"
   - Subtitle: "Based on [N] journal entries and [M] assessments"

2. ArchetypeCard.vue
   - Large display-font archetype name (e.g., "The Pattern-Seeker")
   - 2-sentence description
   - Archetype icon (use a relevant lucide icon)
   - "How we determined this" expandable section
   - Shows "Archetype pending" if not enough data

3. InsightFeed.vue
   - List of personalized insights (from GET /insights/weekly)
   - Each insight: icon + text + optional CTA
   - Max 5 insights shown, "View all insights" link
   - Empty state: "Journal for 7 days to unlock weekly insights"

4. RecommendationPanel.vue  
   - Section title: "What to explore next"
   - 3 recommendation cards (from GET /insights/recommendations):
     * Next bias to explore (with explore link)
     * Next assessment to take (with assessment link)
     * Optional therapist suggestion (only if self-critical biases are high)
   - Each card: icon, title, 1-line reason, CTA button

5. QuickStats.vue
   - 4 metric cards: Journal entries, Assessments completed, Biases explored, Streak (days)
   - Simple numbers, no gamification language

Dashboard layout:
- Top row: QuickStats (4 columns)
- Middle: BiasFingerprint (left 60%) + ArchetypeCard (right 40%)
- Bottom: InsightFeed (left 60%) + RecommendationPanel (right 40%)

All components handle loading states and empty states gracefully.
```

---

## PROMPT 4A: AI Guide with RAG

```
Build the complete AI Guide feature.

Backend (sentio-api/):

1. services/rag_service.py:
   - embed_query(text) → vector using all-MiniLM-L6-v2
   - retrieve_articles(embedding, match_threshold=0.7, match_count=10) → list
   - rerank_articles(query, articles, top_n=3) → list (using Cohere)
   - build_context(articles) → formatted string

2. services/claude_service.py:
   - Full system prompt from ARCHITECTURE.md
   - async stream_response(user_message, user_context, rag_context) → AsyncGenerator
   - Safety check before sending to Claude
   - Safety check on output chunks before streaming to client

3. routers/ai.py:
   - POST /ai/chat — SSE streaming endpoint
     * Load user context (bias fingerprint + journal themes from DB)
     * Run RAG pipeline
     * Stream Claude response
     * Store in ai_conversations table
   - GET /ai/chat/history — return past conversations

4. db/knowledge_embedding.py:
   - Script to embed all knowledge_articles and store vectors
   - Supabase RPC function for pgvector similarity search

Frontend:

5. pages/ai-guide.vue:
   - Full-page chat interface
   - Disclaimer banner (sticky top): "Educational content only. Not therapy."
   - Crisis resource widget (always visible, subtle): "In crisis? iCall: 9152987821"
   - Suggested starter prompts (shown on empty state):
     * "What is confirmation bias and how does it affect decisions?"
     * "How can I recognize when I'm catastrophizing?"
     * "What does my journal pattern say about my thinking?"
     * "How do I find a therapist for anxiety?"

6. components/ai/ChatInterface.vue:
   - Message list (user + assistant bubbles)
   - Streaming text display (append characters as they arrive)
   - Source citations (expandable, shows article title + snippet)
   - Input with send button (disable while streaming)
   - Typing indicator (3 dots animation)

7. components/ai/MessageBubble.vue:
   - User: right-aligned, teal background
   - Assistant: left-aligned, surface-secondary background
   - Timestamps (subtle, on hover)
   - Source citations as collapsible footer

Important: Every AI response must include a source citation panel if RAG context was used.
```

---

## PROMPT 5A: GitHub Cleanup & Portfolio Polish

```
Prepare Sentio for portfolio presentation.

1. ROOT README.md — rewrite completely:
   - Project banner image (create a simple SVG banner using Sentio brand colors)
   - One-line: "Cognitive bias self-awareness platform powered by DistilBERT, UMAP, and RAG"
   - Tech stack badges
   - Architecture diagram (link to ARCHITECTURE.md)
   - Quick start instructions (frontend + backend)
   - ML models section: what each model does, dataset, performance metric
   - Screenshots (placeholder links for now)
   - Disclaimers section
   - License: MIT

2. sentio-ml/ README.md:
   - How to reproduce each model
   - Dataset download instructions
   - MLflow dashboard setup
   - Model performance table

3. .env.example files:
   - Both frontend and backend
   - Every required variable with description comment
   - NO real values

4. GitHub repo structure check:
   - .gitignore: node_modules, .env, __pycache__, *.pyc, checkpoints/, data/raw/
   - All sensitive data excluded
   - Clean commit history (squash if needed)

5. HuggingFace model card (create: sentio-ml/MODEL_CARD.md):
   - Model: sentio-bias-classifier
   - Task: Multi-label cognitive bias classification
   - Architecture: DistilBERT fine-tuned
   - Dataset: [description of synthetic + public data]
   - Performance: Macro F1 = X.XX (val set)
   - Limitations: [list known limitations]
   - Ethical considerations: [not for clinical use, etc.]
   - How to use: code snippet
```

---

## Notes for Running These Prompts

1. **Run prompts in order** — each builds on the previous
2. **Always verify after each prompt**: npm run dev / uvicorn main:app --reload
3. **Keep ARCHITECTURE.md, ML_PIPELINE.md, BUILD_PHASES.md, DESIGN_SYSTEM.md** in your project root — reference them in prompts as needed
4. **For ML prompts**: Run in Google Colab (free T4 GPU) — don't train locally unless you have GPU
5. **For HuggingFace deployment**: Create a free account at huggingface.co, create a Space with Gradio SDK
6. **Supabase**: Enable pgvector extension in Supabase SQL editor: `CREATE EXTENSION IF NOT EXISTS vector;`

---

## PHASE 6: Community, Gamification & Notifications — Full Plan

_Written: 2026-05-05. All dates below are absolute._

---

### 6A — Email & Scheduled Notifications (DONE ✅)

**Already implemented:**
- `sentio-api/services/email_service.py` — Resend-based transactional email (free tier: 3 000/month, 100/day). Functions: `send_daily_reminder`, `send_weekly_digest`, `send_assessment_complete`. Stub mode when `RESEND_API_KEY` absent.
- `sentio-api/services/scheduler.py` — APScheduler `AsyncIOScheduler` (no Redis/Celery needed). Jobs: daily journal nudge (19:00 UTC), weekly digest (Mon 08:00 UTC).
- `sentio-api/main.py` — Scheduler wired into FastAPI `lifespan` context manager; shuts down gracefully on exit.
- `sentio-api/requirements.txt` — `apscheduler>=3.10.0` added.
- `sentio-api/.env.example` — `RESEND_API_KEY`, `RESEND_FROM_EMAIL`, `APP_URL` documented.
- `src/pages/Learn.vue` — Educational resources page at `/learn` with 8 articles + 4 exercises.

**Remaining email task:**
- In `routers/assessments.py` submit endpoint, after saving result, call `await send_assessment_complete(email, name, assessment_title, score, archetype)`.

---

### 6B — Community Section Architecture

#### Overview
A lightweight async discussion board embedded in Sentio. No separate service — backed by Supabase tables. Designed to feel like a private, thoughtful space (not Reddit/Twitter).

#### Database tables (add to `db/schema.sql`)

```sql
-- Topics are the top-level categories (created by admins)
CREATE TABLE community_topics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  slug TEXT UNIQUE NOT NULL,
  description TEXT,
  icon TEXT,           -- lucide icon name
  color TEXT,          -- hex accent color
  thread_count INT DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Threads are user-created discussions within a topic
CREATE TABLE community_threads (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  topic_id UUID REFERENCES community_topics(id) ON DELETE CASCADE,
  author_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  upvotes INT DEFAULT 0,
  reply_count INT DEFAULT 0,
  is_pinned BOOLEAN DEFAULT false,
  is_locked BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- Replies to threads
CREATE TABLE community_replies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  thread_id UUID REFERENCES community_threads(id) ON DELETE CASCADE,
  author_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  body TEXT NOT NULL,
  upvotes INT DEFAULT 0,
  parent_reply_id UUID REFERENCES community_replies(id),  -- for nested replies (1 level)
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Upvote tracking (1 per user per item)
CREATE TABLE community_upvotes (
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  target_type TEXT NOT NULL,   -- 'thread' | 'reply'
  target_id UUID NOT NULL,
  PRIMARY KEY (user_id, target_type, target_id)
);

-- User badges
CREATE TABLE user_badges (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  badge_id TEXT NOT NULL,      -- matches BADGE_DEFINITIONS key
  awarded_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(user_id, badge_id)
);
```

#### RLS policies
- `community_threads`: anyone can read; only author can update/delete their own.
- `community_replies`: same pattern.
- `community_upvotes`: user can only insert/delete their own row.
- `user_badges`: read-only for all authenticated users; insert/delete via service role only.

---

### 6C — Badge System

#### Badge definitions (hardcoded in `services/badge_engine.py`)

| Badge ID | Name | Icon | Description | Trigger |
|---|---|---|---|---|
| `first_journal` | First Reflection | 📝 | Wrote your first journal entry | `journal_entries` count = 1 |
| `streak_7` | Week of Clarity | 🔥 | 7-day journaling streak | Streak = 7 |
| `streak_30` | Month of Mindfulness | 🌙 | 30-day journaling streak | Streak = 30 |
| `bias_3` | Pattern Spotter | 🔍 | 3 unique biases identified across journal entries | Unique detected_biases ≥ 3 |
| `bias_10` | Bias Hunter | 🎯 | 10 unique biases identified | Unique detected_biases ≥ 10 |
| `no_bias` | Clean Slate | ✨ | 5 journal entries with no dominant bias detected | 5 consecutive low-signal entries |
| `assessment_1` | Self-Examiner | 📊 | Completed first assessment | assessment_results count = 1 |
| `assessment_all` | Full Spectrum | 🌈 | Completed all available assessments | completed = total |
| `ai_convo` | Deep Thinker | 🧠 | First AI Guide conversation | ai_conversations count = 1 |
| `community_first` | Contributor | 💬 | First community thread or reply | community_threads or replies = 1 |
| `community_10` | Voice of Reason | 🎙️ | 10 community contributions | threads + replies ≥ 10 |
| `archetype_set` | Self-Aware | 🪞 | Archetype computed | user_bias_profiles has archetype |

#### Badge engine (`services/badge_engine.py`)

```python
async def check_and_award_badges(user_id: str, supabase) -> list[str]:
    """Check all badge conditions for user, award new ones, return newly awarded badge IDs."""
    awarded = {r['badge_id'] for r in supabase.table('user_badges').select('badge_id').eq('user_id', user_id).execute().data or []}
    newly_awarded = []

    def award(badge_id: str):
        if badge_id not in awarded:
            supabase.table('user_badges').insert({'user_id': user_id, 'badge_id': badge_id}).execute()
            newly_awarded.append(badge_id)

    # Journal entries
    entries = supabase.table('journal_entries').select('id,created_at,detected_biases').eq('user_id', user_id).execute().data or []
    if len(entries) >= 1: award('first_journal')
    streak = _compute_streak(entries)
    if streak >= 7: award('streak_7')
    if streak >= 30: award('streak_30')

    # Unique biases
    all_biases = set()
    for e in entries:
        for b in (e.get('detected_biases') or []):
            all_biases.add(b.get('bias_id') or b.get('label') or '')
    all_biases.discard('')
    if len(all_biases) >= 3: award('bias_3')
    if len(all_biases) >= 10: award('bias_10')

    # Assessments
    results = supabase.table('assessment_results').select('assessment_id').eq('user_id', user_id).execute().data or []
    total_assessments = supabase.table('assessments').select('id', count='exact').execute().count or 0
    if len(results) >= 1: award('assessment_1')
    if len(results) >= total_assessments and total_assessments > 0: award('assessment_all')

    # AI
    ai_convos = supabase.table('ai_conversations').select('id', count='exact').eq('user_id', user_id).execute().count or 0
    if ai_convos >= 1: award('ai_convo')

    # Archetype
    bp = supabase.table('user_bias_profiles').select('archetype').eq('user_id', user_id).execute().data or []
    if bp and bp[0].get('archetype'): award('archetype_set')

    return newly_awarded
```

Call `check_and_award_badges` after: journal submit, assessment submit, AI conversation save.

---

### 6D — Community Frontend Pages

#### Routes to add in `router/index.js`
```js
{ path: '/community', component: () => import('@/pages/community/Index.vue'), meta: { requiresAuth: true } },
{ path: '/community/:topicSlug', component: () => import('@/pages/community/Topic.vue'), meta: { requiresAuth: true } },
{ path: '/community/:topicSlug/:threadId', component: () => import('@/pages/community/Thread.vue'), meta: { requiresAuth: true } },
```

#### `src/pages/community/Index.vue`
- Header: "Community" + subtitle "A space to share patterns, ask questions, and support each other."
- Grid of topic cards (fetched from `GET /community/topics`)
- Each card: icon, title, description, thread count, accent color border
- Link to create new thread within any topic

#### `src/pages/community/Topic.vue`
- Topic header with description
- "New Thread" button (opens inline form or modal)
- Thread list: title, author avatar + name, reply count, upvote count, time ago
- Pinned threads shown first
- Pagination (20 threads per page)

#### `src/pages/community/Thread.vue`
- Full thread view: original post + reply chain
- Upvote button on thread + each reply
- Reply textarea (authenticated users only)
- Author badge display: small icons under username
- Nested replies (1 level): "Reply to X" shows indented

#### Sidebar addition in `DefaultLayout.vue`
```js
{ path: '/community', icon: MessageCircle, label: 'Community' },
```

---

### 6E — Community Backend (`routers/community.py`)

```
GET  /community/topics                    → list all topics
GET  /community/topics/:slug              → topic detail + thread list (paginated)
POST /community/topics/:slug/threads      → create thread (auth required)
GET  /community/threads/:id               → thread + replies
POST /community/threads/:id/replies       → add reply (auth required)
POST /community/threads/:id/upvote        → toggle upvote (auth required)
POST /community/replies/:id/upvote        → toggle reply upvote (auth required)
DELETE /community/threads/:id             → delete own thread
DELETE /community/replies/:id             → delete own reply
GET  /community/users/:id/badges          → user's badge list
GET  /users/me/badges                     → current user's badges
```

Content moderation: run all user-submitted text through `services/safety.py` crisis keyword check before saving.

---

### 6F — Profile Page: Badge Display

In `src/pages/Profile.vue`, add a "Badges" section:
- `GET /users/me/badges` on mount
- Display each badge as a pill: icon + name
- Tooltip on hover: badge description
- Locked badges shown as greyed-out with "How to earn" tooltip
- Progress bar for streak badges (current/target)

---

### 6G — Seeding Default Community Topics

```python
# Run once via: python sentio-api/db/seed_community.py
TOPICS = [
  { "title": "Bias Spotting", "slug": "bias-spotting", "description": "Share examples of biases you've caught in your own thinking this week.", "icon": "Eye", "color": "#9b94e8" },
  { "title": "Decision Help", "slug": "decision-help", "description": "Get perspective from the community on decisions you're wrestling with.", "icon": "Scale", "color": "#f59e0b" },
  { "title": "Journal Prompts", "slug": "journal-prompts", "description": "Share prompts that sparked meaningful reflection for you.", "icon": "BookOpen", "color": "#10b981" },
  { "title": "Wins & Breakthroughs", "slug": "wins", "description": "Celebrate moments when you caught a bias before it affected a decision.", "icon": "Zap", "color": "#ec4899" },
  { "title": "Questions & Confusion", "slug": "questions", "description": "Ask anything about cognitive biases, psychology, or how Sentio works.", "icon": "HelpCircle", "color": "#6366f1" },
]
```

---

### 6H — Implementation Priority Order

1. **Email on assessment complete** — 30 min, high impact, already wired up everywhere else
2. **Badge engine** — 2–3 hours; call from journal, assessment, AI endpoints
3. **Profile badge display** — 1–2 hours; purely frontend
4. **Community DB + backend routes** — 3–4 hours
5. **Community Index + Topic pages** — 3–4 hours
6. **Thread page + reply/upvote** — 3 hours
7. **Sidebar addition + route guards** — 30 min

Total estimated: ~1.5–2 working days for full community feature.

---

### 6I — Free Tool Stack Summary (2026)

| Need | Tool | Free Tier |
|---|---|---|
| Transactional email | Resend | 3 000/month, 100/day |
| In-process cron | APScheduler | Open source, no limits |
| Database | Supabase | 500 MB, unlimited API calls |
| Hosting | Render (API) + Vercel (frontend) | Free hobby plans |
| AI | Anthropic API | Pay-per-use (no free tier — budget ~$5/month for dev) |
| Auth | Supabase Auth | Free |
| Realtime (community) | Supabase Realtime | 200 concurrent connections free |

For community real-time updates (new replies appearing live), use Supabase Realtime channel subscriptions in the Thread view — no separate WebSocket server needed.
