-- Episteme V2 Feature Tables
-- Run this in Supabase SQL Editor

-- Add metacognitive_note column to learner_profiles if not exists
ALTER TABLE learner_profiles
ADD COLUMN IF NOT EXISTS metacognitive_note TEXT;

-- Session fingerprints
CREATE TABLE IF NOT EXISTS session_fingerprints (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
  dominant_reasoning_style TEXT DEFAULT 'unknown',
  state_frequencies JSONB DEFAULT '{"PROBE":0,"DEEPEN":0,"SCAFFOLD":0,"RECTIFY":0,"REDIRECT":0,"CONSOLIDATE":0,"COMPLETE":0}',
  avg_bkt_delta FLOAT DEFAULT 0,
  avg_quality_score FLOAT DEFAULT 0,
  bloom_distribution JSONB DEFAULT '{"SURFACE":0,"CONCEPTUAL":0,"ANALYTICAL":0,"SYNTHESIS":0}',
  strong_concepts TEXT[] DEFAULT '{}',
  weak_concepts TEXT[] DEFAULT '{}',
  active_misconceptions TEXT[] DEFAULT '{}',
  next_session_question TEXT,
  recommended_depth TEXT DEFAULT 'CONCEPTUAL',
  metacognitive_note TEXT,
  total_turns INT DEFAULT 0,
  breakthrough_turn INT,
  independent_reasoning_streak INT DEFAULT 0,
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(session_id)
);
CREATE INDEX IF NOT EXISTS idx_fingerprints_session ON session_fingerprints(session_id);
ALTER TABLE session_fingerprints ENABLE ROW LEVEL SECURITY;
CREATE POLICY "allow_all_fingerprints" ON session_fingerprints FOR ALL USING (true) WITH CHECK (true);

-- Notifications
CREATE TABLE IF NOT EXISTS notifications (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
  type TEXT NOT NULL,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  action_url TEXT,
  is_read BOOLEAN DEFAULT FALSE,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_notifications_session ON notifications(session_id);
CREATE INDEX IF NOT EXISTS idx_notifications_unread ON notifications(session_id, is_read);
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
CREATE POLICY "allow_all_notifications" ON notifications FOR ALL USING (true) WITH CHECK (true);

-- Notion connections
CREATE TABLE IF NOT EXISTS notion_connections (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
  notion_token TEXT NOT NULL,
  notion_page_id TEXT NOT NULL,
  notion_page_url TEXT,
  last_synced_at TIMESTAMPTZ,
  sync_count INT DEFAULT 0,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(session_id)
);
ALTER TABLE notion_connections ENABLE ROW LEVEL SECURITY;
CREATE POLICY "allow_all_notion" ON notion_connections FOR ALL USING (true) WITH CHECK (true);

-- Mastery ratings (flashcard self-assessment)
CREATE TABLE IF NOT EXISTS mastery_ratings (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
  concept TEXT NOT NULL,
  rating TEXT CHECK (rating IN ('got_it', 'needs_review', 'no_idea')),
  rated_at TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE mastery_ratings ENABLE ROW LEVEL SECURITY;
CREATE POLICY "allow_all_ratings" ON mastery_ratings FOR ALL USING (true) WITH CHECK (true);

-- Follow-up questions (quick capture)
CREATE TABLE IF NOT EXISTS follow_up_questions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
  question TEXT NOT NULL,
  is_addressed BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE follow_up_questions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "allow_all_followups" ON follow_up_questions FOR ALL USING (true) WITH CHECK (true);
