# Sentio — Build Phases & Implementation Roadmap
## May 1 – August 31, 2026

---

## Time Budget (Realistic)

```
Available: May 1 – August 31 = 18 weeks
Effort split:
  - Sentio: 60% (primary focus)
  - DSA interview prep: 20% (1-2 hrs/day)
  - Psychology/domain learning: 10% (3-4 hrs/week, May-June)
  - Buffer/admin: 10%

Effective Sentio hours/week: ~30-35 hrs
Total Sentio hours: ~540-600 hrs
```

---

## Phase Overview

```
PHASE 0: Cleanup & Setup        [Week 1]          May 1-7
PHASE 1: Foundation             [Weeks 2-4]       May 8-28
PHASE 2: ML Models              [Weeks 5-8]       May 29-June 25
PHASE 3: Core Features          [Weeks 9-12]      June 26-July 23
PHASE 4: AI Integration         [Weeks 13-15]     July 24-August 13
PHASE 5: Polish & Launch        [Weeks 16-18]     August 14-31
```

---

## PHASE 0: Cleanup & Foundation Setup (Week 1, May 1-7)

### Goal
Take the existing Mindfluence/Veramind mess and transform it into Sentio's clean foundation.

### Claude Code Prompt for This Phase
```
You are rebuilding a Vue 3 + Vite project called "Sentio" from an existing messy codebase.

Current state:
- Project has files from two merged projects (Mindfluence + VeraMind)
- Some components are Vue 3, some may be Nuxt-era artifacts
- Design system is inconsistent (purple #9b87f5 theme)
- Has working: Supabase auth, basic routing, some component stubs

Tasks:
1. AUDIT current directory — list all files and categorize:
   - KEEP: Working auth composables, Supabase client, useful component shells
   - CLEAN: Remove Nuxt-specific files, duplicate components, dead code
   - RENAME: Project references from "Mindfluence"/"VeraMind" to "Sentio"

2. IMPLEMENT the Sentio Design System (from DESIGN_SYSTEM.md):
   - Rebuild main.css with new CSS variables
   - New color palette: deep teal + warm amber accent + clean neutrals
   - Typography: Import 'Instrument Serif' (display) + 'DM Sans' (body) from Google Fonts

3. SCAFFOLD new directory structure (from ARCHITECTURE.md):
   - Create all page files as stubs
   - Create component directory structure
   - Set up Pinia stores: useAuthStore, useUserStore, useBiasStore, useJournalStore

4. VERIFY: npm run dev starts without errors, auth flow works, router navigates
```

### Deliverables
- [ ] Clean repo, no dead code or naming conflicts
- [ ] Sentio design system in place (CSS variables, typography)
- [ ] All routes stubbed and navigable
- [ ] Supabase auth working
- [ ] README.md updated (Sentio branding, setup instructions)

---

## PHASE 1: Foundation Features (Weeks 2-4, May 8-28)

### Week 2: Backend + Database

**Goal:** FastAPI running, Supabase schema deployed, all endpoints stubbed

```
Claude Code Prompt:
Set up Sentio's FastAPI backend from scratch.

1. Initialize: fastapi, uvicorn, supabase-py, anthropic, python-dotenv
2. Create directory structure from ARCHITECTURE.md backend section
3. Deploy Supabase schema from ARCHITECTURE.md (all tables + pgvector extension)
4. Implement all router stubs (return placeholder data for now)
5. Implement: POST /auth/signup, POST /auth/login (Supabase JWT integration)
6. Set up CORS for localhost:5173 and Vercel domains
7. Add safety middleware (check ARCHITECTURE.md SafetyChecker)
8. Deploy to Railway/Render (free tier)

Validate: All endpoints return 200 with placeholder data. Auth flow works end-to-end.
```

**Deliverables:**
- [ ] FastAPI running on Railway
- [ ] Supabase schema deployed with all tables
- [ ] Auth working (signup → JWT → protected route)
- [ ] All API stubs returning placeholder data

### Week 3: Onboarding + Assessment Foundation

**Goal:** User can complete onboarding flow and take their first assessment

```
Claude Code Prompt:
Build Sentio's onboarding wizard (Vue 3, Pinia, custom CSS).

Pages to build:
1. /onboarding/welcome — Explain Sentio's purpose (NOT a therapy app)
2. /onboarding/baseline — 10-question "cognitive snapshot" (custom, not validated)
3. /onboarding/interests — What do you want to understand about your thinking?
4. /onboarding/complete — Bias fingerprint preview + dashboard redirect

Components needed:
- OnboardingLayout.vue (progress bar, step navigation)
- QuestionCard.vue (multiple choice, likert scale, free text variants)
- ProgressRing.vue (animated SVG progress indicator)

State: useOnboardingStore (tracks step, saves answers to Supabase on complete)

Design: Use Sentio design system. Calm, intellectual tone. NOT wellness-app style.
```

**Deliverables:**
- [ ] Onboarding flow works end-to-end
- [ ] Saves to Supabase profiles table
- [ ] At least 3 question types working

### Week 4: Bias Explorer (Educational Core)

**Goal:** Users can browse and learn about cognitive biases

```
Claude Code Prompt:
Build the Bias Explorer — Sentio's educational core.

Data: Seed the biases table with 30 cognitive biases (see ML_PIPELINE.md for list).
      Create a seed script: sentio-api/scripts/seed_biases.py

Pages:
1. /explore — Grid of bias cards, filterable by category
   - Categories: Memory, Social, Decision-Making, Self-Perception, Belief
   - Search by name or description
   - Show user's "personal resonance" score if bias profile exists

2. /explore/:slug — Individual bias deep-dive
   - Name, category, definition
   - Real-world example (narrative format)
   - Research backing (condensed citation)
   - "Have you noticed this in yourself?" quick self-reflection prompt
   - Related biases (linked cards)
   - "Explore in journal" CTA

Components:
- BiasCard.vue (compact: name, category badge, one-line description, resonance meter)
- BiasTag.vue (pill badge for category)
- BiasMeter.vue (shows user's personal score for this bias, 0-100)
- BiasDetailPage.vue (full layout)

Design: Make it feel like a beautiful reference guide, not a quiz app.
```

**Deliverables:**
- [ ] 30 biases seeded in DB
- [ ] /explore renders bias grid with filtering
- [ ] /explore/:slug shows full bias detail
- [ ] Feels like a premium reference, not a wellness app

---

## PHASE 2: ML Models (Weeks 5-8, May 29-June 25)

### Week 5: BiasClassifier Data + Training Setup

**Goal:** Training data constructed, model training pipeline ready

```
Tasks (you do this in Jupyter/Colab + local Python):

Day 1-2: Data Collection
- Download: social_bias_frames, crowspairs, go_emotions from HuggingFace datasets
- Run: notebooks/01_bias_data_exploration.ipynb
- Understand distribution, class balance, text lengths

Day 3-4: Training Data Construction
- Write bias_data_generator.py:
  → Use Claude API to generate 50 examples per bias label
  → Prompt: "Generate a short journal entry (50-150 words) written in first person
              that demonstrates [BIAS_NAME]. Be realistic and subtle, not obvious."
  → Save to data/synthetic/bias_training_v1.jsonl

Day 5: Augmentation + Validation
- Back-translation augmentation (English→French→English via Helsinki-NLP/opus-mt)
- Manual review: sample 10 examples per class, mark bad ones
- Split: 70/15/15 train/val/test

Claude Code Prompt for training pipeline:
Implement the BiasClassifier training pipeline in PyTorch + HuggingFace Transformers.
Follow ML_PIPELINE.md Model 1 specification exactly.
Include: MLflow tracking, evaluation metrics (macro F1, per-class F1), model saving.
Output: trained model + tokenizer saved to ./checkpoints/bias-clf-v1/
```

**Deliverables:**
- [ ] 750 labeled examples constructed and validated
- [ ] Training pipeline runs end-to-end on Colab (GPU)
- [ ] First model trained (even if F1 is low — iterate)

### Week 6: BiasClassifier Training + HuggingFace Deploy

**Goal:** Trained BiasClassifier deployed on HuggingFace Spaces

```
Tasks:
Day 1-2: Hyperparameter tuning
- Try: {lr: 1e-5, 2e-5, 3e-5} × {batch: 8, 16} × {epochs: 3, 5}
- Best run → final model

Day 3: Deploy to HuggingFace Spaces
- Create Gradio app (spaces/bias-classifier/app.py)
- Expose POST API endpoint
- Test from FastAPI service

Day 4-5: Integrate into Sentio backend
- bias_classifier.py service calls HF Space endpoint
- Journal entries trigger classification on create
- Store results in journal_entries.detected_biases
- Update user_bias_profiles incrementally

Claude Code Prompt:
Integrate the BiasClassifier HuggingFace Space into Sentio's FastAPI backend.
- Create services/bias_classifier.py with async HTTP calls to HF Space endpoint
- Add background task in POST /journal/ to classify new entries
- Implement update_user_bias_profile() function
- Add error handling: if classifier is down, continue without blocking journal save
```

**Deliverables:**
- [ ] Model trained, macro F1 ≥ 0.55 (aim for 0.65)
- [ ] HuggingFace Space live and accepting requests
- [ ] Journal entries automatically classified on creation
- [ ] Bias profile updates working

### Week 7: JournalNLP + ArchetypeModel

**Goal:** Full journal NLP pipeline + archetype clustering working

```
JournalNLP (Days 1-2):
- Use pre-trained bhadresh-savani/distilbert-base-uncased-emotion (no fine-tuning needed)
- Implement KeyBERT theme extraction
- Deploy as second HF Space endpoint or combine with BiasClassifier space
- Integrate into journal creation pipeline (alongside BiasClassifier)

ArchetypeModel (Days 3-5):
- Need: assessment results from at least synthetic users to test
- Generate 200 synthetic user profiles (realistic but fake data)
- Run UMAP + HDBSCAN
- Label 4-6 clusters manually with archetype names
- Create cluster centroid descriptions (used in dashboard)
- Save archetype mapping to Supabase
```

**Deliverables:**
- [ ] Journal NLP pipeline live (emotion + themes per entry)
- [ ] Archetype clustering producing meaningful clusters on synthetic data
- [ ] Archetypes stored and displayable in UI

### Week 8: EngagementPredictor + RecommendationEngine

**Goal:** Both models implemented (even with synthetic data initially)

```
EngagementPredictor:
- Generate synthetic engagement data (200 users × 30 days)
- Train XGBoost with MLflow tracking
- Deploy to HF Space or inline in FastAPI
- Wire: daily job checks, sends nudge notification if churn risk > 0.7

RecommendationEngine (content-based first):
- Implement bias relationship graph (which biases are adjacent/root-cause)
- Rule-based assessment recommender
- Therapist preference matching
- Test with 5 synthetic user profiles

Claude Code Prompt:
Implement Sentio's RecommendationEngine in services/recommender.py.
Follow ML_PIPELINE.md Model 4 specification.
Expose via: GET /insights/recommendations (returns: next_bias, next_assessment, therapist_match_reason)
```

**Deliverables:**
- [ ] EngagementPredictor trained and live
- [ ] RecommendationEngine returning sensible recommendations
- [ ] /insights/recommendations endpoint working

---

## PHASE 3: Core Product Features (Weeks 9-12, June 26-July 23)

### Week 9: Dashboard + Bias Fingerprint

```
Claude Code Prompt:
Build Sentio's Dashboard — the personal cognitive profile page.

Components:
1. BiasFingerprint.vue — Radar/spider chart showing user's top bias categories
   - 5 axes: Memory, Social, Decision, Self-Perception, Belief
   - Shows scores 0-100 per category
   - Animated on first load
   - Chart.js radar chart

2. ArchetypeCard.vue — Shows user's cognitive archetype
   - Archetype name (e.g., "The Pattern-Seeker")
   - 2-sentence description
   - Top 3 associated biases

3. InsightFeed.vue — Scrollable list of personalized insights
   - "You've completed 3 journal entries. Top theme: work stress."
   - "Your assessment shows high anchoring bias. [Learn more →]"
   - Insights generated by GET /insights/weekly

4. RecommendationPanel.vue — What to do next
   - "Explore: Availability Bias" (linked to /explore/availability-bias)
   - "Take: Metacognitive Awareness Assessment" (linked)
   - "Consider connecting with a therapist" (if high score on self-critical biases)

Design: Make it feel like a personal analytics dashboard, premium and data-rich.
```

### Week 10: Journal System

```
Claude Code Prompt:
Build Sentio's Journal — the primary data input and reflection tool.

Pages:
1. /journal — List of past entries with preview + detected biases as tags
2. /journal/new — Journal editor with:
   - Daily prompt (rotating, psychology-grounded)
   - Free-text editor (min 50 words for analysis)
   - Optional: "What triggered this?" structured field
   
3. /journal/:id — Entry view with full analysis:
   - Original text
   - Detected biases (highlighted spans + explanations)
   - Emotions timeline (from GoEmotions classifier)
   - Key themes (keyword pills)
   - "Reflect deeper" — 3 follow-up questions generated by Claude

Components:
- JournalEditor.vue (textarea with character count, prompt display, submit CTA)
- BiasHighlight.vue (colored text spans with bias tooltip on hover)
- InsightPanel.vue (emotion chart + themes + reflection questions)
- EntryCard.vue (list item: date, preview, bias tags, emotion indicator)

State: useJournalStore
API: POST /journal/, GET /journal/, GET /journal/{id}/insights
```

### Week 11: Assessment Hub

```
Claude Code Prompt:
Build the Assessment Hub with 5 validated assessments.

Assessments to implement (questions pre-written, scoring logic from research):
1. Need for Cognition Scale (NCS-18) — tendency to engage in effortful thinking
2. Cognitive Flexibility Inventory (CFI-20) — ability to adapt thinking
3. Metacognitive Awareness Inventory (MAI-52, short form: 30 items) — self-knowledge of thinking
4. Rational-Experiential Inventory (REI-40) — intuitive vs analytical thinking style
5. Multidimensional Locus of Control — internal vs external attribution style

Pages:
1. /assessments — Grid of assessment cards (locked if not onboarded)
2. /assessments/:id — Take assessment flow
   - Progress bar, one question at a time, back/next navigation
   - Time estimate shown
3. /assessments/:id/results — Results page
   - Score visualization
   - What this means (interpretation)
   - Which biases this relates to
   - Compare to previous attempt (if retaken)

Store all questions and scoring in Supabase assessments table.
Scoring logic in FastAPI: POST /assessments/{id}/submit
```

### Week 12: Therapist Directory

```
Claude Code Prompt:
Build the Therapist Directory.

Seed: Create 20 realistic therapist profiles (fictional but realistic for India).
Include: RCI-registered, various specializations, Hindi/English, online options.

Pages:
1. /therapists — Directory with filters:
   - Language (Hindi, English, Bengali, Tamil, Marathi)
   - Format (Online, In-person, Both)
   - Specialization (anxiety, relationships, career, grief, etc.)
   - Price range (₹500-1000, ₹1000-2000, ₹2000+)
   
2. /therapists/:id — Profile page:
   - Photo (placeholder), credentials, bio, approach
   - Specializations (tags)
   - Session details (format, duration, price)
   - "Request connection" button (NOT booking — routes to external/email)
   - Disclaimer: "Sentio helps you find therapists. The clinical relationship is directly between you and your therapist."

3. RecommendedTherapists.vue — component in dashboard
   - 2-3 recommendations with match reasons (preference-based only)

Important: Add disclaimer on every therapist-related page.
```

---

## PHASE 4: AI Integration (Weeks 13-15, July 24-August 13)

### Week 13: RAG Knowledge Base

```
Tasks:
Day 1-3: Content curation + embedding
- Scrape/collect 200+ psychology articles (Wikipedia, Simply Psychology)
- Write embedding pipeline (all-MiniLM-L6-v2 → pgvector)
- Validate retrieval quality on 20 test queries

Day 4-5: Cohere ReRank integration
- Set up Cohere free tier
- Implement reranking step
- A/B test: retrieval quality with vs without reranking

Claude Code Prompt:
Implement the RAG pipeline for Sentio's AI Guide.
Follow ARCHITECTURE.md RAG Pipeline specification exactly.
Create: db/supabase_match_knowledge.sql (pgvector similarity function)
       services/rag_service.py (embed → retrieve → rerank)
       services/claude_service.py (streaming Claude integration with system prompt)
Test: 10 test queries with expected retrieved articles.
```

### Week 14: AI Guide (Chat Interface)

```
Claude Code Prompt:
Build the AI Guide chat interface and backend.

Backend:
- POST /ai/chat — streaming response endpoint (SSE or WebSocket)
- Load user context: bias_fingerprint + recent journal themes
- RAG retrieval + Claude generation
- Safety check on every input AND output
- Store conversation in ai_conversations table

Frontend:
- /ai-guide page with chat interface
- ChatInterface.vue:
  - Message history (scrollable)
  - Input + send button
  - Streaming response display (character-by-character)
  - Source citations (when Claude cites knowledge base)
  - Suggested prompts on first load:
    * "Explain confirmation bias to me"
    * "How do I recognize when I'm catastrophizing?"
    * "What does my journal pattern say about my thinking?"
- Disclaimer banner: "AI Guide provides educational content, not therapy."
- Crisis intercept: if user input matches crisis keywords → show crisis resources, don't respond with AI
```

### Week 15: Journal Reflection AI + Integration Polish

```
Tasks:
- Implement "Reflect deeper" feature in journal entry view
  → POST /journal/{id}/reflections → Claude generates 3 follow-up questions
  → Questions are grounded in detected biases in the entry
  → Display as interactive prompts user can journal on

- Wire all ML model outputs into dashboard properly:
  → Bias fingerprint pulls from user_bias_profiles (updated by BiasClassifier)
  → Archetype pulls from latest batch run
  → Recommendations pull from RecommendationEngine

- End-to-end integration test:
  → New user signs up → onboards → takes assessment → journals 3 entries
  → Dashboard shows bias fingerprint + archetype + recommendations
  → AI Guide answers bias-related question with sources
  → Can find and connect with therapist
```

---

## PHASE 5: Polish, Validation & Launch (Weeks 16-18, August 14-31)

### Week 16: Beta Testing

```
Recruit 20 beta testers (IIT peers, friends):
- Give them: signup link + 5-minute setup guide
- Ask them to: complete onboarding, take 2 assessments, journal 5 times, try AI Guide
- Collect feedback via: Tally form (free) or Google Form

Metrics to track:
- Completion rate: % who finish onboarding
- Retention: % who return day 3, day 7
- Qualitative: "Was the bias detection accurate?" "Did the AI Guide feel helpful?"
- Safety: Any harmful outputs? Any crisis signals missed?

Iterate on top 3 pain points from beta feedback.
```

### Week 17: Performance + Reliability

```
Claude Code Prompt:
Optimize Sentio for production.

1. Frontend performance:
   - Lazy-load heavy components (Chart.js, journal editor)
   - Image optimization (WebP, lazy loading)
   - Bundle analysis: npm run build → identify large chunks

2. Backend performance:
   - Add Redis caching for GET /insights/* (TTL: 1 hour)
   - Optimize Supabase queries (add indexes on user_id, created_at)
   - Add request rate limiting (100 req/hour per user for AI endpoints)

3. Error handling:
   - Graceful degradation if BiasClassifier HF Space is down
   - User-friendly error messages (not stack traces)
   - Sentry integration for error tracking (free tier)

4. Monitoring:
   - Add /health endpoint
   - Set up uptime monitoring (UptimeRobot, free)
```

### Week 18: Portfolio Artifacts

```
Deliverables:
1. GitHub cleanup:
   - Clean README.md (Sentio branding, setup instructions, architecture diagram)
   - sentio-ml/ repo with notebooks, training pipeline, model cards
   - All secrets in .env.example (never committed)

2. Demo video (5 min):
   - Walkthrough: onboarding → assessment → journal → dashboard → AI Guide → therapist directory
   - Narrate: "Here's what happens technically when you submit a journal entry..."
   - Record with Loom (free)

3. Case study blog post (2000+ words):
   Title: "Building Sentio: Cognitive Bias Detection with DistilBERT, UMAP Archetypes, and RAG"
   Sections:
   - Product vision: what Sentio is and why
   - Psychology foundation: which frameworks, which validated tools
   - ML architecture: BiasClassifier training, ArchetypeModel clustering, RAG pipeline
   - Engineering decisions: why FastAPI, why Supabase, why pgvector
   - Safety: how I prevented harmful outputs
   - Results: beta metrics, model performance

4. Interview prep doc:
   - 5 key talking points per ML model
   - How to explain each system design decision
   - Trade-offs: what I'd do differently with more time
```

---

## Milestone Summary

```
Week 1  (May 7)   — Clean repo + design system + Sentio branding
Week 4  (May 28)  — Working backend + onboarding + bias explorer
Week 8  (June 25) — All 5 ML models trained and integrated
Week 12 (July 23) — Full feature set: dashboard + journal + assessments + therapists
Week 15 (Aug 13)  — AI Guide + full integration polish
Week 18 (Aug 31)  — Beta tested + portfolio artifacts ready
```

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| BiasClassifier F1 too low | Medium | High | Use pre-trained model if custom <0.5 F1; still counts as fine-tuning |
| HF Space cold start latency | High | Medium | Add loading state in UI; cache common classifications |
| Beta testers ghost | High | Low | Give them a task with clear output ("take 2 assessments and tell me X") |
| Claude API costs | Low | Medium | Rate limit aggressively (5 AI Guide requests/day free tier) |
| Therapist data quality | Medium | Low | 20 seeded profiles is enough for portfolio demo |
| Timeline slip in ML phase | High | High | If behind by week 7, drop EngagementPredictor and collaborative filtering |

---

## What to Cut If Behind Schedule

**Priority order (ship in this order if time-constrained):**
1. ✅ Core: Bias Explorer + Journal + BiasClassifier integration (non-negotiable)
2. ✅ Core: Assessment Hub + Dashboard (non-negotiable)
3. ✅ Core: AI Guide with RAG (portfolio requirement)
4. ⚡ Important: Therapist Directory (can be static if no time for matching)
5. 🔧 Nice: ArchetypeModel (can show as "in development")
6. 🔧 Nice: EngagementPredictor (cut entirely if behind)
7. 🔧 Nice: CollaborativeFiltering (replace with content-based only)
