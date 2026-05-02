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
