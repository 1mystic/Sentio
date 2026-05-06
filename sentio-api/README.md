---
title: Sentio API
emoji: 🧠
colorFrom: purple
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
---

# Sentio API

FastAPI backend for the Sentio cognitive-bias platform.

## Required environment variables

Set these in **HuggingFace Spaces → Settings → Repository secrets**:

| Variable | Description |
|---|---|
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_SERVICE_KEY` | Supabase service-role key (secret) |
| `ANTHROPIC_API_KEY` | Anthropic API key for AI Guide chat |
| `COHERE_API_KEY` | Cohere API key for RAG reranking |
| `ALLOWED_ORIGINS` | Comma-separated list of allowed frontend origins, e.g. `https://your-app.vercel.app` |
| `FRONTEND_URL` | Your Vercel app URL (used in email links) |
| `APP_URL` | Same as `FRONTEND_URL` |
| `RESEND_API_KEY` | Resend API key for transactional email |
| `RESEND_FROM_EMAIL` | Verified sender address in Resend |
| `ADMIN_EMAIL` | Admin dashboard login email |
| `ADMIN_PASSWORD` | Admin dashboard login password |
| `ENVIRONMENT` | `production` |

## Local development

```bash
cp .env.example .env   # fill in real values
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
