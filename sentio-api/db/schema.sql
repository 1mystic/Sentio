-- Sentio — PostgreSQL schema for Supabase
-- Run this in the Supabase SQL editor to initialise the database.

-- ─────────────────────────────────────────────
-- Extensions
-- ─────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ─────────────────────────────────────────────
-- 1. User profiles (linked to Supabase auth.users)
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS profiles (
  id UUID PRIMARY KEY REFERENCES auth.users ON DELETE CASCADE,
  username TEXT UNIQUE,
  display_name TEXT,
  bio TEXT,
  onboarding_completed BOOLEAN DEFAULT FALSE,
  cognitive_style JSONB DEFAULT '{}',
  preferences JSONB DEFAULT '{"notifications": {"daily": true, "weekly": true, "assessments": false}}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Auto-create profile on user signup
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS trigger AS $$
BEGIN
  INSERT INTO profiles (id, display_name)
  VALUES (NEW.id, NEW.raw_user_meta_data->>'full_name')
  ON CONFLICT DO NOTHING;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION handle_new_user();

-- ─────────────────────────────────────────────
-- 2. Cognitive bias taxonomy (seeded)
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS biases (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  slug TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  category TEXT NOT NULL CHECK (category IN ('memory','social','decision','self','belief','reasoning')),
  description TEXT NOT NULL,
  example TEXT NOT NULL,
  research_summary TEXT,
  detection_signals JSONB DEFAULT '[]',
  related_bias_slugs TEXT[] DEFAULT '{}',
  severity_weight FLOAT DEFAULT 1.0,
  prevalence_pct INT DEFAULT 50,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_biases_category ON biases(category);
CREATE INDEX IF NOT EXISTS idx_biases_slug ON biases(slug);

-- ─────────────────────────────────────────────
-- 3. Validated assessments (seeded)
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS assessments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  slug TEXT UNIQUE NOT NULL,
  title TEXT NOT NULL,
  description TEXT,
  validated_tool TEXT,
  research_citation TEXT,
  questions JSONB NOT NULL DEFAULT '[]',
  scoring_algorithm JSONB NOT NULL DEFAULT '{}',
  target_biases TEXT[] DEFAULT '{}',
  estimated_minutes INT DEFAULT 10,
  category TEXT DEFAULT 'general',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ─────────────────────────────────────────────
-- 4. User assessment results
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS assessment_results (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  assessment_id UUID REFERENCES assessments(id),
  raw_scores JSONB NOT NULL DEFAULT '{}',
  computed_scores JSONB NOT NULL DEFAULT '{}',
  bias_implications JSONB DEFAULT '{}',
  completed_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_results_user ON assessment_results(user_id);
CREATE INDEX IF NOT EXISTS idx_results_assessment ON assessment_results(assessment_id);

-- ─────────────────────────────────────────────
-- 5. Journal entries
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS journal_entries (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  content TEXT NOT NULL,
  prompt_used TEXT,
  mood TEXT,
  sentiment_score FLOAT,
  detected_biases JSONB DEFAULT '[]',
  themes JSONB DEFAULT '[]',
  emotions JSONB DEFAULT '[]',
  embedding VECTOR(384),
  processing_status TEXT DEFAULT 'pending' CHECK (processing_status IN ('pending','processing','done','failed')),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_journal_user ON journal_entries(user_id);
CREATE INDEX IF NOT EXISTS idx_journal_created ON journal_entries(created_at DESC);

-- ─────────────────────────────────────────────
-- 6. User bias profiles (updated by background tasks)
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS user_bias_profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE UNIQUE,
  bias_scores JSONB NOT NULL DEFAULT '{}',
  category_scores JSONB DEFAULT '{"memory":0,"social":0,"decision":0,"self":0,"belief":0,"reasoning":0}',
  dominant_category TEXT,
  archetype TEXT,
  archetype_description TEXT,
  confidence FLOAT DEFAULT 0.0,
  sources JSONB DEFAULT '{"journal_entries":0,"assessments":0}',
  last_updated TIMESTAMPTZ DEFAULT NOW()
);

-- ─────────────────────────────────────────────
-- 7. Therapist directory (seeded)
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS therapists (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  initials TEXT,
  credentials TEXT[] DEFAULT '{}',
  specializations TEXT[] DEFAULT '{}',
  languages TEXT[] DEFAULT '{"English"}',
  bio TEXT,
  approach TEXT,
  session_formats TEXT[] DEFAULT '{"online"}',
  price_range JSONB DEFAULT '{"min": 500, "max": 1500, "currency": "INR"}',
  availability JSONB DEFAULT '{"status": "available"}',
  contact_info JSONB DEFAULT '{}',
  verified BOOLEAN DEFAULT TRUE,
  rating FLOAT DEFAULT 4.5,
  review_count INT DEFAULT 0,
  experience_years INT DEFAULT 5,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ─────────────────────────────────────────────
-- 8. Booking / connection requests
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS bookings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  therapist_id UUID REFERENCES therapists(id),
  requested_at TIMESTAMPTZ,
  message TEXT,
  status TEXT DEFAULT 'pending' CHECK (status IN ('pending','accepted','declined','cancelled')),
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_bookings_user ON bookings(user_id);

-- ─────────────────────────────────────────────
-- 9. AI chat history
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS ai_conversations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  messages JSONB NOT NULL DEFAULT '[]',
  context_summary TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_conversations_user ON ai_conversations(user_id);

-- ─────────────────────────────────────────────
-- 10. RAG knowledge base (embeddings for psychology articles)
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS knowledge_articles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  category TEXT,
  source_url TEXT,
  source_citation TEXT,
  embedding VECTOR(384),
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_knowledge_category ON knowledge_articles(category);
