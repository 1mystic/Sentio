# VeraMind Setup Guide

Complete setup instructions for the VeraMind project.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Supabase Setup](#supabase-setup)
4. [API Keys Setup](#api-keys-setup)
5. [Database Schema](#database-schema)
6. [Running the Application](#running-the-application)
7. [Deployment](#deployment)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before you begin, ensure you have:

- **Node.js** >= 18.0.0 ([Download](https://nodejs.org/))
- **npm** >= 9.0.0 (comes with Node.js)
- **Git** (for version control)
- **Supabase Account** ([Sign up](https://supabase.com) - Free tier available)
- **Google Gemini API Key** ([Get API Key](https://makersuite.google.com/app/apikey))
- **Cohere API Key** ([Sign up](https://cohere.com) - Free tier available)

---

## Local Development Setup

### Step 1: Clone/Navigate to Project

If you haven't already, navigate to the project directory:

```bash
cd /Users/1mystic/Shared-pc/1_Work/projects/veramind
```

### Step 2: Install Dependencies

```bash
npm install
```

This will install the project dependencies for a Vite + Vue 3 application including:
- Vue 3
- Vite
- Vue Router
- Supabase client (`@supabase/supabase-js`)
- Google Generative AI SDK (if used)
- LangChain.js (optional)
- And other dependencies

### Step 3: Create Environment File

Create a `.env` file in the root directory:

```bash
touch .env
```

Add the following variables (you'll fill in the values in the next steps). Vite exposes client-side env vars that start with `VITE_` — use these names so the variables are available in the browser.

```env
VITE_SUPABASE_URL=
VITE_SUPABASE_ANON_KEY=
VITE_GEMINI_API_KEY=
VITE_COHERE_API_KEY=
NODE_ENV=development
```

If you're migrating from Nuxt, note the older names `NUXT_PUBLIC_*` map to the `VITE_` names above in client code.

---

## Supabase Setup

### Step 1: Create Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Sign up or log in
3. Click "New Project"
4. Fill in:
   - **Name**: veramind (or your choice)
   - **Database Password**: (save this securely)
   - **Region**: Choose closest to you
5. Click "Create new project"
6. Wait for project to initialize (~2 minutes)

### Step 2: Get Supabase Credentials

1. In your Supabase project dashboard, go to **Settings** → **API**
2. Copy:
  - **Project URL** → `VITE_SUPABASE_URL`
  - **anon public** key → `VITE_SUPABASE_ANON_KEY`
3. Add these to your `.env` file

### Step 3: Enable pgvector Extension

1. In Supabase dashboard, go to **SQL Editor**
2. Run this query:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

3. Click "Run" to execute

### Step 4: Create Database Tables

Run the following SQL in the Supabase SQL Editor:

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Profiles table
CREATE TABLE IF NOT EXISTS profiles (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE UNIQUE NOT NULL,
  full_name TEXT,
  email TEXT,
  avatar_url TEXT,
  bio TEXT,
  archetype TEXT,
  engagement_score NUMERIC,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Journal entries table
CREATE TABLE IF NOT EXISTS journal_entries (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  date DATE NOT NULL,
  content TEXT NOT NULL,
  prompt TEXT,
  tags TEXT[] DEFAULT '{}',
  mood INTEGER CHECK (mood >= 1 AND mood <= 10),
  sentiment JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, date)
);

-- Assessments table
CREATE TABLE IF NOT EXISTS assessments (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  type TEXT NOT NULL, -- 'GAD-7', 'PHQ-9', 'cognitive-bias', 'core-values'
  score NUMERIC NOT NULL,
  severity TEXT, -- 'minimal', 'mild', 'moderate', 'severe'
  responses JSONB NOT NULL,
  completed_at TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Module progress table
CREATE TABLE IF NOT EXISTS module_progress (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  module_id TEXT NOT NULL,
  module_name TEXT NOT NULL,
  progress_percentage INTEGER DEFAULT 0 CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
  current_lesson INTEGER DEFAULT 1,
  completed_lessons INTEGER[] DEFAULT '{}',
  started_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, module_id)
);

-- Community posts table
CREATE TABLE IF NOT EXISTS community_posts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  category TEXT,
  tags TEXT[] DEFAULT '{}',
  is_anonymous BOOLEAN DEFAULT FALSE,
  likes_count INTEGER DEFAULT 0,
  replies_count INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Community replies table
CREATE TABLE IF NOT EXISTS community_replies (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  post_id UUID REFERENCES community_posts(id) ON DELETE CASCADE NOT NULL,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  content TEXT NOT NULL,
  parent_reply_id UUID REFERENCES community_replies(id) ON DELETE CASCADE,
  is_anonymous BOOLEAN DEFAULT FALSE,
  likes_count INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Educational articles table (with vector embeddings)
CREATE TABLE IF NOT EXISTS educational_articles (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  category TEXT,
  difficulty TEXT CHECK (difficulty IN ('beginner', 'intermediate', 'advanced')),
  read_time INTEGER, -- minutes
  author TEXT,
  tags TEXT[] DEFAULT '{}',
  embedding vector(768), -- For pgvector (adjust dimension based on your embedding model)
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Support groups table
CREATE TABLE IF NOT EXISTS support_groups (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  description TEXT,
  category TEXT,
  is_private BOOLEAN DEFAULT FALSE,
  member_count INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Group memberships table
CREATE TABLE IF NOT EXISTS group_memberships (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  group_id UUID REFERENCES support_groups(id) ON DELETE CASCADE NOT NULL,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  joined_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(group_id, user_id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_journal_entries_user_date ON journal_entries(user_id, date);
CREATE INDEX IF NOT EXISTS idx_assessments_user_type ON assessments(user_id, type);
CREATE INDEX IF NOT EXISTS idx_community_posts_category ON community_posts(category);
CREATE INDEX IF NOT EXISTS idx_educational_articles_category ON educational_articles(category);

-- Create vector index for RAG (adjust based on your embedding dimension)
-- CREATE INDEX IF NOT EXISTS idx_educational_articles_embedding ON educational_articles USING ivfflat (embedding vector_cosine_ops);

-- Enable Row Level Security (RLS)
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE journal_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE assessments ENABLE ROW LEVEL SECURITY;
ALTER TABLE module_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE community_posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE community_replies ENABLE ROW LEVEL SECURITY;
ALTER TABLE group_memberships ENABLE ROW LEVEL SECURITY;

-- RLS Policies (users can only access their own data)
CREATE POLICY "Users can view own profile" ON profiles FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can update own profile" ON profiles FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own profile" ON profiles FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can manage own journal entries" ON journal_entries FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own assessments" ON assessments FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own module progress" ON module_progress FOR ALL USING (auth.uid() = user_id);

-- Community posts are public but users can only edit their own
CREATE POLICY "Anyone can view community posts" ON community_posts FOR SELECT USING (true);
CREATE POLICY "Users can create posts" ON community_posts FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own posts" ON community_posts FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own posts" ON community_posts FOR DELETE USING (auth.uid() = user_id);

-- Similar policies for replies
CREATE POLICY "Anyone can view replies" ON community_replies FOR SELECT USING (true);
CREATE POLICY "Users can create replies" ON community_replies FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own replies" ON community_replies FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own replies" ON community_replies FOR DELETE USING (auth.uid() = user_id);

-- Educational articles are public
CREATE POLICY "Anyone can view educational articles" ON educational_articles FOR SELECT USING (true);

-- Support groups are public
CREATE POLICY "Anyone can view support groups" ON support_groups FOR SELECT USING (true);
CREATE POLICY "Users can manage own memberships" ON group_memberships FOR ALL USING (auth.uid() = user_id);
```

### Step 5: Set Up Auth Triggers

Create a function to automatically create a profile when a user signs up:

```sql
-- Function to create profile on user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (user_id, email, full_name)
  VALUES (
    NEW.id,
    NEW.email,
    NEW.raw_user_meta_data->>'full_name'
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to call function on user creation
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
```

---

## API Keys Setup

### Google Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the API key
5. Add to `.env` as `VITE_GEMINI_API_KEY`

### Cohere API Key

1. Go to [cohere.com](https://cohere.com)
2. Sign up for a free account
3. Go to API Keys section
4. Create a new API key
5. Copy the key
6. Add to `.env` as `VITE_COHERE_API_KEY`

---

## Running the Application

### Development Server

For a Vite app the dev server runs on port `5173` by default:

```bash
npm run dev
```

Open `http://localhost:5173` in your browser (or the URL printed by Vite).

### Build for Production

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

---

## Deployment

### Deployment (Free Tier Options)

This project is designed to be deployable on free-tier static hosting providers with serverless or edge functions for backend/API needs.

Recommended free-tier hosting options:

- **Vercel (Recommended for simplicity)**
  - Connect your Git repository (GitHub/GitLab/Bitbucket).
  - Vercel auto-detects Vite and builds with `vite build`.
  - You can add environment variables in the Vercel dashboard (use the `VITE_` names from above).
  - Vercel supports Serverless Functions on the free tier for light API work; for heavier AI workloads use an external API.

- **Netlify**
  - Connect repository, Netlify detects Vite projects.
  - Add environment variables in Site Settings.
  - Netlify Functions provide serverless endpoints (suitable for light API or proxying requests).

- **Supabase**
  - Use Supabase for the database and Authentication.
  - Supabase Edge Functions are available on the free tier and can host lightweight server-side logic (useful for secret-handling calls to AI APIs).

Deployment Steps (example with Vercel):

1. **Push to GitHub**:
  ```bash
  git init
  git add .
  git commit -m "Initial commit"
  git remote add origin <your-github-repo-url>
  git push -u origin main
  ```

2. **Connect to Vercel**:
  - Go to https://vercel.com and import your repository.
  - Vercel will auto-detect a Vite project and set build command to `vite build` and output directory to `dist`.

3. **Add Environment Variables** (in Vercel Project Settings):
  - `VITE_SUPABASE_URL`
  - `VITE_SUPABASE_ANON_KEY`
  - `VITE_GEMINI_API_KEY` (if used)
  - `VITE_COHERE_API_KEY` (if used)

4. **Deploy**:
  - Trigger a deploy from Vercel UI or push to main branch.

Notes on serverless / secrets:
- Do not call paid AI APIs directly from client-side code. Use a serverless function (Vercel Serverless, Netlify Functions, or Supabase Edge Function) to proxy requests and keep API keys secret. These serverless options are available on free tiers for light usage.
- If your AI usage will exceed free-tier limits, consider running AI logic on paid endpoints or using usage caps/monitoring.

### Update Supabase URLs

After deployment, update your Supabase project:
1. Go to Supabase Dashboard → Settings → API
2. Add your Vercel URL to "Redirect URLs"
3. Add `https://your-vercel-url.vercel.app/**` to allowed redirect URLs

---

## Troubleshooting

### Common Issues

**Issue**: `Cannot find module '@nuxtjs/supabase'`
- **Solution**: Run `npm install` again

**Issue**: `Supabase connection error`
- **Solution**: Check your `.env` file has correct Supabase URL and key

**Issue**: `Gemini API error`
- **Solution**: Verify your API key is correct and has quota remaining

**Issue**: `Database migration errors`
- **Solution**: Make sure pgvector extension is enabled first

**Issue**: `Port 3000 already in use`
- **Solution**: Change port: `npm run dev -- --port 3001`

### Getting Help

- Check the [Supabase Documentation](https://supabase.com/docs)
- Review error messages in browser console and terminal

---

## Next Steps

After setup:
1. ✅ Test authentication (sign up, sign in)
2. ✅ Verify database connection
3. ✅ Test API endpoints
4. 🔄 Start building features (see project plan)

---

**Setup complete! Happy coding! 🚀**

