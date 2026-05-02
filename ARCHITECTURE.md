# Sentio — System Architecture
## Cognitive Self-Awareness Platform

> Sentio is not a mental health app. It is a cognitive mirror — helping users discover their own biases, blind spots, and thinking patterns through validated psychology, ML-driven insight, and curated access to real therapists when needed.

---

## 1. North Star & Scope Clarification

### What Sentio IS
- A **self-awareness platform** grounded in cognitive psychology and behavioral science
- A tool to help users identify **cognitive biases, distorted thinking patterns, and metacognitive blind spots**
- A **bridge to real therapists** when users need clinical support (not a replacement)
- A portfolio-grade demonstration of: full-stack engineering + ML/DL + LLM integration + product design

### What Sentio IS NOT
- A therapy app or mental health treatment platform
- A crisis intervention tool (always redirect to 988 / professional help)
- A diagnostic tool (screens and educates, never diagnoses)
- A journaling app with random AI compliments

### Core Differentiation vs Wysa/Headspace/Woebot
| Dimension | Competitors | Sentio |
|---|---|---|
| Primary goal | Emotional support / relaxation | Cognitive self-awareness & bias detection |
| Psychology layer | Generic CBT tips | Validated cognitive bias taxonomy (100+ biases) |
| ML approach | Rule-based chatbots | Personalized bias fingerprinting + recommendation |
| Therapist access | Upsell/afterthought | Core feature — curated, real, bookable |
| Target user | Anyone stressed | Intellectually curious people who want to grow |

---

## 2. High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        SENTIO PLATFORM                       │
├──────────────────┬───────────────────┬───────────────────────┤
│   FRONTEND       │   BACKEND API     │   ML/AI LAYER         │
│   (Vue 3 + Vite) │   (FastAPI/Node)  │   (Python + HF)       │
├──────────────────┼───────────────────┼───────────────────────┤
│ • Bias Explorer  │ • Auth (Supabase) │ • Bias Classifier     │
│ • Assessment Hub │ • User Profiles   │ • Journal NLP         │
│ • Journal        │ • Journal API     │ • Archetype Model     │
│ • Therapist Dir. │ • Assessment API  │ • Recommendation      │
│ • AI Guide       │ • Booking API     │ • Claude Integration  │
│ • Dashboard      │ • Insights API    │ • Engagement Model    │
└──────────────────┴───────────────────┴───────────────────────┘
         │                   │                    │
    Vercel CDN          Supabase DB         HuggingFace
                      (PostgreSQL +           Spaces +
                       pgvector)             MLflow
```

---

## 3. Frontend Architecture (Vue 3)

### Tech Stack
- **Framework**: Vue 3 + Vite (existing, keep)
- **State**: Pinia
- **Router**: Vue Router 4
- **Styling**: Custom CSS/SCSS — unified Sentio Design System (see DESIGN_SYSTEM.md)
- **API**: Axios with composable wrappers
- **Charts**: Chart.js (lightweight)
- **Deploy**: Vercel

### Page/Route Map
```
/                          → Landing page
/onboarding                → Onboarding flow (assessment wizard)
/dashboard                 → Personal dashboard + bias fingerprint
/explore                   → Bias Explorer (educational library)
/explore/:bias-slug        → Individual bias deep-dive
/assessments               → Assessment Hub
/assessments/:id           → Take specific assessment
/journal                   → Journal (with AI analysis)
/journal/:id               → Individual entry + insights
/therapists                → Therapist Directory
/therapists/:id            → Therapist profile + booking
/ai-guide                  → AI Guide (RAG chat)
/profile                   → User profile + settings
/progress                  → Progress tracker + insights
```

### Component Hierarchy
```
App.vue
├── layouts/
│   ├── DefaultLayout.vue      (navbar + sidebar + main)
│   ├── AuthLayout.vue         (centered, no nav)
│   └── OnboardingLayout.vue   (progress stepper)
├── components/
│   ├── ui/                    (base: Button, Card, Badge, Input, Modal)
│   ├── bias/                  (BiasCard, BiasTag, BiasMeter)
│   ├── assessment/            (QuestionCard, ScoreDisplay, ResultCard)
│   ├── journal/               (JournalEditor, InsightPanel, ThemeCloud)
│   ├── therapist/             (TherapistCard, BookingModal, ReviewCard)
│   ├── dashboard/             (BiasFingerprint, ProgressRing, InsightFeed)
│   └── ai/                    (ChatInterface, MessageBubble, SourceCitation)
└── pages/                     (route-level components)
```

---

## 4. Backend Architecture

### Option A: FastAPI Monolith (Recommended for solo dev, 4-month timeline)
```
sentio-api/
├── main.py                    (FastAPI app, router registration)
├── routers/
│   ├── auth.py                (Supabase auth integration)
│   ├── users.py               (profile, preferences)
│   ├── assessments.py         (CRUD + scoring)
│   ├── journal.py             (CRUD + trigger NLP pipeline)
│   ├── insights.py            (aggregate + serve insights)
│   ├── therapists.py          (directory + booking)
│   └── ai.py                  (Claude RAG + guide)
├── models/                    (Pydantic schemas)
├── services/
│   ├── bias_classifier.py     (calls HF Space or local model)
│   ├── journal_nlp.py         (DistilBERT sentiment + themes)
│   ├── recommender.py         (bias recommendation logic)
│   ├── claude_service.py      (Anthropic API wrapper)
│   └── therapist_matching.py  (matching algorithm)
├── db/
│   ├── supabase_client.py
│   └── queries.py
└── utils/
    ├── validators.py
    └── safety.py              (content safety checks)
```

### Key API Endpoints
```
POST   /auth/signup
POST   /auth/login

GET    /users/me
PATCH  /users/me/preferences

GET    /assessments/                     # list available
POST   /assessments/{id}/submit          # score + store
GET    /assessments/{id}/history         # past results

POST   /journal/                         # create entry (triggers NLP)
GET    /journal/                         # list entries
GET    /journal/{id}/insights            # AI-generated insights for entry
GET    /journal/themes                   # aggregate themes over time

GET    /insights/bias-fingerprint        # personalized bias profile
GET    /insights/weekly                  # weekly pattern summary
GET    /insights/recommendations         # what to work on next

GET    /therapists/                      # directory (filterable)
GET    /therapists/{id}                  # profile
POST   /therapists/{id}/book             # booking request

POST   /ai/chat                          # streaming RAG chat
GET    /ai/chat/history                  # past conversations
```

---

## 5. Database Schema (Supabase PostgreSQL)

```sql
-- Core user profile
CREATE TABLE profiles (
  id UUID PRIMARY KEY REFERENCES auth.users,
  username TEXT UNIQUE,
  display_name TEXT,
  bio TEXT,
  onboarding_completed BOOLEAN DEFAULT FALSE,
  cognitive_style JSONB,           -- from onboarding assessment
  preferences JSONB,               -- UI + notification prefs
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Cognitive bias taxonomy
CREATE TABLE biases (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  slug TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  category TEXT NOT NULL,          -- memory/social/decision/belief/etc
  description TEXT NOT NULL,
  example TEXT NOT NULL,
  research_summary TEXT,
  detection_signals JSONB,         -- what patterns indicate this bias
  related_bias_ids UUID[],
  severity_weight FLOAT DEFAULT 1.0
);

-- Assessment definitions
CREATE TABLE assessments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  slug TEXT UNIQUE NOT NULL,
  title TEXT NOT NULL,
  description TEXT,
  validated_tool TEXT,             -- e.g. "Need for Cognition Scale"
  research_citation TEXT,
  questions JSONB NOT NULL,
  scoring_algorithm JSONB,
  target_biases UUID[],            -- which biases this probes
  estimated_minutes INT DEFAULT 10
);

-- User assessment results
CREATE TABLE assessment_results (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES profiles(id),
  assessment_id UUID REFERENCES assessments(id),
  raw_scores JSONB NOT NULL,
  computed_scores JSONB NOT NULL,
  bias_implications JSONB,         -- which biases flagged
  completed_at TIMESTAMPTZ DEFAULT NOW()
);

-- Journal entries
CREATE TABLE journal_entries (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES profiles(id),
  content TEXT NOT NULL,
  prompt_used TEXT,
  sentiment_score FLOAT,
  detected_biases JSONB,           -- [{bias_id, confidence, excerpt}]
  themes JSONB,                    -- extracted themes array
  embedding VECTOR(384),           -- for semantic search
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- User bias profile (updated incrementally)
CREATE TABLE user_bias_profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES profiles(id) UNIQUE,
  bias_scores JSONB NOT NULL,      -- {bias_id: score, ...}
  dominant_category TEXT,
  archetype TEXT,                  -- cognitive archetype label
  confidence FLOAT,
  sources JSONB,                   -- which data contributed
  last_updated TIMESTAMPTZ DEFAULT NOW()
);

-- Therapist directory
CREATE TABLE therapists (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  credentials TEXT[],
  specializations TEXT[],
  languages TEXT[],
  bio TEXT,
  approach TEXT,
  session_formats TEXT[],          -- in-person/online/both
  price_range JSONB,
  availability JSONB,
  contact_info JSONB,
  verified BOOLEAN DEFAULT FALSE,
  rating FLOAT,
  review_count INT DEFAULT 0
);

-- Booking requests
CREATE TABLE bookings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES profiles(id),
  therapist_id UUID REFERENCES therapists(id),
  requested_at TIMESTAMPTZ,
  message TEXT,
  status TEXT DEFAULT 'pending',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- AI chat history
CREATE TABLE ai_conversations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES profiles(id),
  messages JSONB NOT NULL,
  context_summary TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Educational content (RAG source)
CREATE TABLE knowledge_articles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  category TEXT,
  source_citation TEXT,
  embedding VECTOR(384),
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 6. ML/AI Layer Architecture

### Model Registry
| Model | Purpose | Approach | Dataset | Deploy |
|---|---|---|---|---|
| BiasClassifier | Detect cognitive biases in journal text | DistilBERT fine-tuned | Custom labeled + ThinkerBench | HF Space |
| ArchetypeModel | Cluster users into cognitive archetypes | UMAP + HDBSCAN | Assessment results | GitHub Actions batch |
| RecommendationEngine | Suggest next bias to explore / intervention | Collaborative + content | User-bias interactions | FastAPI service |
| JournalNLP | Sentiment + theme extraction | DistilBERT + KeyBERT | SemEval, IMDb, custom | HF Space |
| EngagementPredictor | Predict dropout, trigger nudges | XGBoost + MLflow | User activity logs | HF Space |
| AIGuide | Contextual RAG chat about cognitive biases | pgvector + Claude | Psychology corpus | Inline API |

### Data Flow (Journal Entry → Insights)
```
User submits journal entry
         ↓
FastAPI /journal/ POST
         ↓
Background task triggered
         ↓
    ┌────┴────┐
    │         │
Sentiment   BiasClassifier
(DistilBERT) (fine-tuned DLM)
    │         │
    └────┬────┘
         ↓
    ThemeExtraction (KeyBERT)
         ↓
    EmbeddingGeneration (all-MiniLM-L6-v2)
         ↓
    Store to Supabase (journal_entries)
         ↓
    UpdateUserBiasProfile (incremental)
         ↓
    ArchetypeReclassification (if enough new data)
         ↓
    Serve via /journal/{id}/insights
```

---

## 7. LLM Integration (Claude)

### Claude's Role in Sentio
Claude is used for three things ONLY (not generic chat):

1. **AI Guide** — RAG-powered Q&A about cognitive psychology and bias
2. **Journal Reflection** — structured prompts that help user examine their entries
3. **Therapist Match Explanation** — explaining why a particular therapist was recommended

### System Prompt Architecture (AI Guide)
```python
SYSTEM_PROMPT = """
You are Sentio's AI Guide — an expert in cognitive psychology, behavioral science, and metacognition.

Your role:
- Help users understand cognitive biases and how they manifest in real life
- Answer questions about psychology concepts grounded in research
- Gently illuminate patterns you notice in what users share
- Guide users toward self-reflection, NOT toward conclusions about themselves

You NEVER:
- Diagnose mental health conditions
- Provide therapy or clinical advice
- Make definitive claims about a user's psychology
- Suggest medications or clinical treatments

When users show signs needing professional support, say:
"This sounds like something worth exploring with a therapist. Sentio's therapist directory can connect you with a specialist in [area]."

Context provided per request:
- User's current bias fingerprint: {bias_fingerprint}
- Recent journal themes: {journal_themes}
- Current assessment results: {assessment_summary}
- Retrieved knowledge articles: {rag_context}
"""
```

### RAG Pipeline
```
User query
    ↓
Embed query (all-MiniLM-L6-v2)
    ↓
pgvector similarity search (knowledge_articles)
    ↓
Cohere ReRank (top-10 → top-3)
    ↓
Inject into Claude context window
    ↓
Claude streams response
    ↓
Display with source citations
```

---

## 8. Privacy & Safety Architecture

### Data Principles
- No raw behavioral monitoring (no keystroke, mouse, screen tracking)
- All journal content encrypted at rest (Supabase AES-256)
- Users own their data: full export + deletion available
- No selling data, no ad targeting, no third-party data sharing
- GDPR-compliant consent and retention (12-month default, configurable)

### Safety Guardrails
```python
class SafetyChecker:
    CRISIS_KEYWORDS = ["suicide", "self-harm", "end my life", ...]
    
    def check_input(self, text: str) -> SafetyResult:
        if self.contains_crisis_signal(text):
            return SafetyResult(
                action="REDIRECT",
                message="If you're in crisis, please contact iCall (9152987821) or Vandrevala Foundation (1860-2662-345)",
                block_ai_response=True
            )
        return SafetyResult(action="PROCEED")
    
    def check_output(self, text: str) -> bool:
        # Block: diagnoses, medication names, clinical claims
        return not self.contains_clinical_overreach(text)
```

### Therapist Verification
- All therapists manually verified (RCI / MCI credentials for India)
- No automated matching claims ("this therapist is perfect for you")
- User sees match reasons, makes own choice
- Sentio does not intermediate the clinical relationship

---

## 9. Therapist Directory Architecture

### Data Sources (India-first)
- iCall (TISS) — verified list
- Vandrevala Foundation partners
- Manual curated list (verified credentials)
- Eventually: API partnership with Practo/1to1help

### Matching Algorithm (Non-clinical, Preference-based)
```python
def match_therapists(user_profile, therapists):
    """
    Matches on preferences ONLY — not clinical need.
    Returns ranked list with explanation.
    """
    scores = {}
    for t in therapists:
        score = 0
        # Language preference
        if user_lang in t.languages: score += 3
        # Specialization alignment (user's stated interests, not diagnosis)
        score += len(set(user_interests) & set(t.specializations))
        # Format preference (online/in-person)
        if user_format == t.session_format: score += 2
        # Price range match
        if price_compatible(user_budget, t.price_range): score += 2
        scores[t.id] = score
    
    return sorted(therapists, key=lambda t: scores[t.id], reverse=True)
```

---

## 10. Deployment Architecture

```
GitHub (main branch)
    ↓ (push)
    ├── Vercel (Frontend auto-deploy)
    ├── Railway/Render (FastAPI backend)
    └── HuggingFace Spaces (ML models)
            ↓
        Supabase (DB + Auth + Storage)
```

### Environment Variables
```env
# Frontend (.env)
VITE_SUPABASE_URL=
VITE_SUPABASE_ANON_KEY=
VITE_API_BASE_URL=
VITE_CLAUDE_ENABLED=true

# Backend (.env)
SUPABASE_URL=
SUPABASE_SERVICE_KEY=
ANTHROPIC_API_KEY=
COHERE_API_KEY=
HF_API_TOKEN=
BIAS_CLASSIFIER_URL=     # HF Space endpoint
JOURNAL_NLP_URL=         # HF Space endpoint
```
