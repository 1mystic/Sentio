# Sentio Deployment Guide

Backend → HuggingFace Spaces · Frontend → Vercel

---

## Before you start

You need accounts on three services:
- [HuggingFace](https://huggingface.co/join) — free
- [Vercel](https://vercel.com/signup) — free
- [GitHub](https://github.com) — to connect both services

Your code must be pushed to a GitHub repository. If it isn't yet:

```bash
git init
git add .
git commit -m "initial commit"
git remote add origin https://github.com/YOUR_USERNAME/sentio.git
git push -u origin main
```

---

## Step 1 — Deploy the backend to HuggingFace Spaces

The `sentio-api/` folder becomes its own HuggingFace Space (a Docker container).

### 1.1 Create a new Space

1. Go to [huggingface.co/new-space](https://huggingface.co/new-space)
2. Fill in:
   - **Owner**: your username
   - **Space name**: `sentio-api` (or any name you like)
   - **License**: MIT
   - **SDK**: select **Docker**
   - **Visibility**: Public (required for free tier)
3. Click **Create Space**

You now have an empty HF Space with a git remote URL like:
```
https://huggingface.co/spaces/YOUR_USERNAME/sentio-api
```

### 1.2 Push only the backend folder

HuggingFace Spaces expects the **root of the repo** to contain the `Dockerfile` and `README.md`. Our files are inside `sentio-api/`, so we use `git subtree push` — this pushes just that subfolder as the root of the HF Space repo, without creating a nested `.git` or breaking your main project tracking.

```bash
# Run everything from the PROJECT ROOT (not inside sentio-api)

# 1. Add the HF Space as a remote (one time only)
git remote add hf-space https://huggingface.co/spaces/mozoj4/sentio-backend

# 2. Push the sentio-api/ subfolder as the root of the HF Space
git subtree push --prefix=sentio-api hf-space main
```

> **Credentials:** HuggingFace will ask for your username and password.
> Use your HF username and a HF **Access Token** (not your account password).
> Create one at: huggingface.co → Profile → Settings → Access Tokens → New token (select **write** permission).

> **If `git subtree push` is rejected** (HF Space already has commits that differ from yours):
> ```bash
> git subtree push --prefix=sentio-api hf-space main --force
> ```
> This is safe — it only affects the HF remote, not your local repo.

The Space will start building. You can watch the build logs by clicking **Logs** in the Space page. The first build takes **5–10 minutes** because it installs ML packages and downloads the embedding model.

### 1.3 Set environment variables (secrets)

Never commit your `.env` file. Set variables in the HF Spaces UI instead:

1. In your Space page click **Settings** (top right)
2. Scroll to **Repository secrets**
3. Add each variable one by one:

| Name | Value |
|---|---|
| `SUPABASE_URL` | `https://xxxx.supabase.co` |
| `SUPABASE_SERVICE_KEY` | Your service-role key (from Supabase → Settings → API) |
| `ANTHROPIC_API_KEY` | Your Anthropic API key |
| `COHERE_API_KEY` | Your Cohere API key (or leave blank if not using RAG reranking) |
| `RESEND_API_KEY` | Your Resend API key |
| `RESEND_FROM_EMAIL` | e.g. `noreply@yourdomain.com` |
| `ADMIN_EMAIL` | Your admin login email |
| `ADMIN_PASSWORD` | A strong password |
| `ENVIRONMENT` | `production` |
| `ALLOWED_ORIGINS` | Leave blank for now — you'll fill this after Vercel deploy |
| `APP_URL` | Leave blank for now |
| `FRONTEND_URL` | Leave blank for now |

After adding secrets, click **Restart Space** (top right of the Logs page).

### 1.4 Confirm the backend is running

Once the build finishes, click **App** in the Space page. You should see:
```json
{"message": "Welcome to the Sentio API", "docs": "/docs", "health": "/health"}
```

Your backend URL is:
```
https://YOUR_USERNAME-sentio-api.hf.space
```

Copy this URL — you need it in the next step.

---

## Step 2 — Deploy the frontend to Vercel

### 2.1 Import the project

1. Go to [vercel.com/new](https://vercel.com/new)
2. Click **Add GitHub Account** if not connected, authorise Vercel
3. Find your `sentio` repository and click **Import**

### 2.2 Configure the build

Vercel should auto-detect Vite. Confirm these settings:

| Setting | Value |
|---|---|
| **Framework Preset** | Vite |
| **Root Directory** | `.` (project root, not sentio-api) |
| **Build Command** | `npm run build` |
| **Output Directory** | `dist` |

### 2.3 Set environment variables

In the **Environment Variables** section (before clicking Deploy), add:

| Name | Value |
|---|---|
| `VITE_SUPABASE_URL` | `https://xxxx.supabase.co` |
| `VITE_SUPABASE_ANON_KEY` | Your Supabase anon key (from Supabase → Settings → API) |
| `VITE_API_BASE_URL` | `https://YOUR_USERNAME-sentio-api.hf.space` |

Click **Deploy**. Vercel builds and deploys in about 1–2 minutes.

Your frontend URL will be something like:
```
https://sentio-xxxx.vercel.app
```

---

## Step 3 — Connect backend and frontend

Now that both are live, you need to wire them together.

### 3.1 Update CORS in HuggingFace Spaces

1. Go back to your HF Space → **Settings** → **Repository secrets**
2. Update these three variables with your actual Vercel URL:

| Name | Value |
|---|---|
| `ALLOWED_ORIGINS` | `https://sentio-xxxx.vercel.app` |
| `APP_URL` | `https://sentio-xxxx.vercel.app` |
| `FRONTEND_URL` | `https://sentio-xxxx.vercel.app` |

3. Click **Restart Space**

### 3.2 Allow your Vercel domain in Supabase Auth

1. Go to your Supabase project → **Authentication** → **URL Configuration**
2. Set **Site URL** to `https://sentio-xxxx.vercel.app`
3. Under **Redirect URLs**, add:
   ```
   https://sentio-xxxx.vercel.app/**
   ```
4. Save

---

## Step 4 — Run database migrations

Your production database needs the Phase 6 tables. Run the migration SQL once:

1. Go to [supabase.com](https://supabase.com) → your project → **SQL Editor**
2. Open `sentio-api/db/migration_phase6.sql`, copy its entire contents
3. Paste into the SQL Editor and click **Run**

Then seed the community topics:

```bash
# From your local machine, with sentio-api/.env filled in
cd sentio-api
python db/seed_community.py
```

---

## Step 5 — Smoke test

Open your Vercel URL in an incognito window and check:

- [ ] Can sign up and log in
- [ ] Dashboard loads without 401 errors in the browser console
- [ ] Journal entry can be created
- [ ] AI Guide responds (may take a few seconds on first message)
- [ ] Community topics page loads

If the AI Guide returns an error, check the HF Space **Logs** tab — the most common cause is a missing or wrong `ANTHROPIC_API_KEY`.

---

## Updating after code changes

### Backend update
```bash
# From the project root — commit your changes normally first
git add sentio-api/
git commit -m "update backend"

# Then push the subfolder to HF Spaces
git subtree push --prefix=sentio-api hf-space main
```
HuggingFace rebuilds automatically on push.

### Frontend update
```bash
# From project root
git add .
git commit -m "update"
git push origin main
```
Vercel redeploys automatically when it detects a push to your connected GitHub branch.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| 401 on all API calls | `SUPABASE_SERVICE_KEY` wrong or missing | Check HF secrets |
| AI chat returns error | `ANTHROPIC_API_KEY` wrong or missing | Check HF secrets, check HF Logs |
| CORS error in browser | `ALLOWED_ORIGINS` doesn't match Vercel URL | Update HF secret, restart Space |
| HF build fails | Pip install error | Check Logs → usually a package version conflict |
| Vercel build fails | Missing env var at build time | Add to Vercel env vars, redeploy |
| Login redirect loops | Supabase redirect URL not set | Add Vercel URL to Supabase → Auth → Redirect URLs |
