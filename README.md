<div align="center">

<br>

<img src="https://img.shields.io/badge/-%20S%20E%20N%20T%20I%20O-352b38?style=for-the-badge&labelColor=352b38&color=9b94e8" height="40" alt="Sentio" />

<h3>Cognitive bias self‑awareness, built for people who want to think better — not just feel better.</h3>

<br>

[![Vue 3](https://img.shields.io/badge/Vue%203-352b38?style=flat-square&logo=vuedotjs&logoColor=dad8f9)](https://vuejs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-352b38?style=flat-square&logo=fastapi&logoColor=dad8f9)](https://fastapi.tiangolo.com)
[![Supabase](https://img.shields.io/badge/Supabase-352b38?style=flat-square&logo=supabase&logoColor=dad8f9)](https://supabase.com)
[![Claude](https://img.shields.io/badge/Claude%20Sonnet-352b38?style=flat-square&logo=anthropic&logoColor=dad8f9)](https://anthropic.com)
[![License MIT](https://img.shields.io/badge/License-MIT-352b38?style=flat-square&logoColor=dad8f9)](LICENSE)

<br>

</div>

---

## Overview

Sentio is a full-stack mental clarity platform that helps users identify and move past the cognitive biases shaping their decisions, conversations, and self-image. Rather than giving users pre-packaged insights, Sentio puts them through the process — structured dialogue, reflective journaling, and validated assessments — so the understanding they reach is genuinely their own.

The platform has two modes of AI interaction: a context-aware chat assistant grounded in your personal bias history, and a Socratic learning engine that never gives direct answers, only better questions.

<br>

---

## Features

<br>

### AI Guide — dual-mode assistant

<details open>
<summary><strong>Guide mode</strong></summary>

<br>

A RAG-enhanced Claude chat grounded in your bias profile and recent journal themes. Responses stream via SSE. Conversation history is persisted and reloadable.

</details>

<details open>
<summary><strong>Socratic mode</strong></summary>

<br>

A purpose-built educational dialogue engine ported from the [Episteme](https://github.com/mozoj4/episteme) project. It adapts its questioning strategy in real time based on how you reason — tracking mastery probability, Bloom's taxonomy depth, and dialogue state simultaneously.

Seven deterministic algorithms run **client-side** (zero added latency):

| Algorithm | Role |
|:----------|:-----|
| **RDSE** | Scores reasoning quality from connectives, uncertainty markers, and Bloom taxonomy verbs |
| **SDSM** | 7-state dialogue machine: `PROBE → DEEPEN → SCAFFOLD → RECTIFY → REDIRECT → CONSOLIDATE → COMPLETE` |
| **CBKT-CS** | 4-parameter Bayesian Knowledge Tracing — mastery probability updated every turn |
| **BGDC** | Maps responses to Bloom's taxonomy levels via domain-specific keyword classification |
| **CPGAB** | Infers knowledge gaps from concepts covered per domain |
| **EGP** | Retention decay and gap urgency scoring for adaptive next-step prompting |
| **SM-2** | Spaced repetition interval scheduling for concept reinforcement |

The right panel tracks Clarity score (BKT), dialogue state, Bloom depth, and session progress in real time. Cognitive signals (Analysis %, Depth, Clarity) animate as you type — before you send.

Sessions persist to Supabase. Past sessions can be resumed from a history panel. Insight cards (generated after ≥4 turns) export to Markdown, PDF, or clipboard.

</details>

<br>

### Journal — markdown-native

A personal journal that reads your writing as you write it.

- **Write / Preview toggle** — switch between raw markdown and rendered output at any time
- **Formatting toolbar** — Bold, Italic, Heading, List, Inline code, Code block, Quote
- **Keyboard shortcuts** — <kbd>Ctrl</kbd>+<kbd>B</kbd>, <kbd>Ctrl</kbd>+<kbd>I</kbd>, <kbd>Tab</kbd> indent
- **Live bias detection** — 6 bias patterns matched in real time as you type, shown in the sidebar
- **Full GFM rendering** in saved entries — headings, blockquotes, code blocks, tables, lists
- **Background analysis** — sentiment scoring and bias extraction run via APScheduler after save, keeping write latency fast

<br>

### Cognitive assessments

Validated self-assessment instruments that build your personal bias profile. Results feed directly into the AI assistant's context, personalising responses across the platform.

<br>

### Bias library

Structured knowledge base of cognitive biases with detail pages, real examples, and cross-links to your own journal entries where each pattern appeared.

<br>

### Therapist directory

Directory of licensed therapists populated by a custom Python scraper, stored in Supabase with lat/lng geolocation. Filter by session format (online/in-person), specialty, and location.

<br>

### Community

Threaded discussion boards built on Supabase Realtime, organised by topic.

<br>

### Progress

Longitudinal view of your clarity score, bias frequency trends, and assessment history over time.

<br>

---

## Architecture

```
Browser (Vue 3 + Pinia)
│
├─ Educational algorithms (TypeScript — runs client-side)
│    └─ RDSE · SDSM · CBKT-CS · BGDC · CPGAB · EGP · SM-2
│
└─ FastAPI (Python 3.11)
     │
     ├─ /socratic   ──► SSE streaming · session persistence · history
     ├─ /ai         ──► RAG-enhanced guide chat (SSE)
     ├─ /journal    ──► CRUD · APScheduler background analysis
     ├─ /assessments
     ├─ /therapists
     ├─ /community
     └─ /insights   ──► Cross-domain insight synthesis
          │
          └─ Supabase (PostgreSQL · Row-Level Security · Auth · Realtime)
```

<details>
<summary><strong>Engineering notes</strong></summary>

<br>

**Client-side algorithm layer** — All 7 educational algorithms run in the browser. The client sends computed signals (quality score, BKT state, next SDSM state) with each message so Claude's prompt is fully enriched without any extra round-trip.

**SSE with separate parsing paths** — Socratic uses `{"text":"..."}` / `{"done":true}`, Guide uses `{"chunk":"..."}` / `[DONE]`. Both modes target sub-100ms first-token latency on warm connections.

**Row-Level Security at the Postgres layer** — every table has RLS policies tied to `auth.uid()`. Users cannot access each other's data regardless of API behaviour; no application-level filtering needed.

**APScheduler background tasks** — bias analysis and embedding generation run after save. Write latency stays under 200ms even for long entries.

**Safety gate** — every AI endpoint runs crisis detection before invoking Claude. Crisis language short-circuits to a redirect response (no token spend) with mental health resources.

**Supabase OAuth fallback** — supports both email/password and OAuth providers via a unified Pinia session store.

</details>

<br>

---

## Stack

<div align="center">

| Layer | Technology |
|:------|:-----------|
| **Frontend** | Vue 3 · Vite · Pinia · Vue Router · Lucide · Urbanist |
| **Markdown** | `marked` (GFM, line breaks) |
| **Backend** | FastAPI · Python 3.11 · Pydantic v2 · APScheduler |
| **AI** | Anthropic Claude `claude-sonnet-4-6` — streaming SDK |
| **Database** | Supabase — PostgreSQL · RLS · Auth · Realtime |
| **Deployment** | Hugging Face Spaces (API) · Vercel (frontend) |

</div>

<br>

---

## Local setup

**Prerequisites:** Node 18+, Python 3.11+, a Supabase project, an Anthropic API key.

```bash
# 1. Frontend
npm install
cp .env.example .env
# VITE_API_BASE_URL=http://localhost:8000
# VITE_SUPABASE_URL=...
# VITE_SUPABASE_ANON_KEY=...
npm run dev
```

```bash
# 2. Backend
cd sentio-api
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux
pip install -r requirements.txt
cp .env.example .env
# ANTHROPIC_API_KEY=...
# SUPABASE_URL=...
# SUPABASE_SERVICE_ROLE_KEY=...
# ALLOWED_ORIGINS=http://localhost:5173
uvicorn main:app --reload
```

```sql
-- 3. Run in Supabase SQL editor
-- sentio-api/scripts/schema_socratic.sql
```

API docs available at `http://localhost:8000/docs`.

<br>

---

## Project structure

```
sentio/
├── src/
│   ├── pages/
│   │   ├── AIGuide.vue              # Dual-mode AI assistant
│   │   ├── journal/
│   │   │   ├── Index.vue            # Entry list with filters
│   │   │   ├── New.vue              # Markdown editor with live bias detection
│   │   │   └── Entry.vue            # Full GFM renderer
│   │   ├── assessments/
│   │   ├── explore/                 # Bias library
│   │   ├── therapists/
│   │   └── community/
│   ├── composables/
│   │   └── useEpistemeChat.ts       # Socratic engine — state, streaming, session history
│   └── lib/episteme/
│       ├── algorithms.ts            # All 7 algorithms — pure TypeScript, no dependencies
│       ├── prompts.ts               # Socratic + insight card prompt builders
│       └── types.ts                 # Shared types
│
└── sentio-api/
    ├── routers/
    │   ├── socratic.py              # Session CRUD · SSE chat · history endpoints
    │   ├── ai.py                    # Guide chat with RAG context
    │   └── journal.py
    └── services/
        ├── claude_service.py        # Streaming wrappers for both chat modes
        ├── rag_service.py           # Sentence-transformer embeddings
        └── safety.py                # Crisis detection gate
```

<br>

---

<div align="center">

*Not a replacement for professional mental health support.*
&nbsp;·&nbsp;
[![MIT](https://img.shields.io/badge/License-MIT-9b94e8?style=flat-square)](LICENSE)

</div>
