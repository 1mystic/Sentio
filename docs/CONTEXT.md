# Sentio Project Context
Last updated: 2026-05-15 — Session 0

## Deployment URLs
- Frontend: https://sentio-go.vercel.app
- Backend API: https://mozoj4-sentio-backend.hf.space/docs
- Supabase: [project ref]

## Tech Stack (verified)
- Frontend: Vue 3 + Vite + Pinia + Vue Router 4
- Backend: FastAPI / Python 3.11 / Pydantic v2 / APScheduler
- Database: Supabase (PostgreSQL + pgvector + RLS + Auth)
- AI: Anthropic Claude via async streaming SDK (claude-haiku-4-5-20251001, claude-sonnet-4-6)

## API Routes — Status
- /socratic/chat [POST] — REAL — 2026-05-15
- /insights/weekly [GET] — REAL (Claude synthesizes data) — 2026-05-15
- /therapists/{id}/book [POST] — REAL (Notification sent) — 2026-05-15

## Services — Status
- claude_service.py — REAL — Streams AI responses
- safety.py — REAL — check_input is used, check_output regex drops clinical overreach in SSE streams
- journal_nlp.py — REAL — HF integration exists, fallback is VADER sentiment analysis

## Episteme Algorithm Integration Status
- RDSE — TS-IMPLEMENTED — WIRED-TO-BACKEND
- SDSM — TS-IMPLEMENTED — WIRED-TO-BACKEND
- CBKT-CS — TS-IMPLEMENTED — WIRED-TO-BACKEND
- BGDC — TS-IMPLEMENTED — WIRED-TO-BACKEND
- CPGAB — TS-IMPLEMENTED — WIRED-TO-BACKEND
- EGP — TS-IMPLEMENTED — WIRED-TO-BACKEND
- SM-2 — TS-IMPLEMENTED — WIRED-TO-BACKEND

## RLS Policy Status
- journal_entries — RLS-POLICY-EXISTS
- user_bias_profiles — RLS-POLICY-EXISTS
- assessment_results — RLS-POLICY-EXISTS
- socratic_sessions — RLS-POLICY-EXISTS
- notifications — RLS-POLICY-EXISTS
- user_badges — RLS-POLICY-EXISTS
- ai_conversations — RLS-POLICY-EXISTS
- bookings — RLS-POLICY-EXISTS
- community tables — RLS-POLICY-EXISTS

## Known Issues (open)
- None
