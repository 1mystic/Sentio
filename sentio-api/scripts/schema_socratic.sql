-- Socratic sessions (run in Supabase SQL editor)
-- Creates 4 tables for the Episteme Socratic engine integration

CREATE TABLE IF NOT EXISTS socratic_sessions (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id      UUID REFERENCES profiles(id) ON DELETE CASCADE,
  domain       TEXT NOT NULL DEFAULT 'general',
  turns_count  INT DEFAULT 0,
  is_complete  BOOLEAN DEFAULT FALSE,
  created_at   TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS socratic_messages (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id    UUID REFERENCES socratic_sessions(id) ON DELETE CASCADE,
  role          TEXT CHECK (role IN ('user', 'assistant')),
  content       TEXT NOT NULL,
  turn_number   INT NOT NULL,
  algo_state    TEXT,
  clarity_score INT,
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS socratic_insight_cards (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id    UUID REFERENCES socratic_sessions(id) ON DELETE CASCADE,
  concept       TEXT NOT NULL,
  insight       TEXT NOT NULL,
  gaps          TEXT[] DEFAULT '{}',
  clarity_score INT DEFAULT 0,
  next_question TEXT,
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS socratic_concepts (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id    UUID REFERENCES socratic_sessions(id) ON DELETE CASCADE,
  user_id       UUID REFERENCES profiles(id),
  name          TEXT NOT NULL,
  depth_reached TEXT CHECK (depth_reached IN ('SURFACE','CONCEPTUAL','ANALYTICAL','SYNTHESIS')),
  clarity_score INT DEFAULT 0,
  bkt_pl        FLOAT DEFAULT 0.20,
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- RLS policies
ALTER TABLE socratic_sessions     ENABLE ROW LEVEL SECURITY;
ALTER TABLE socratic_messages     ENABLE ROW LEVEL SECURITY;
ALTER TABLE socratic_insight_cards ENABLE ROW LEVEL SECURITY;
ALTER TABLE socratic_concepts     ENABLE ROW LEVEL SECURITY;

CREATE POLICY "users own socratic sessions"
  ON socratic_sessions FOR ALL
  USING (auth.uid() = user_id);

CREATE POLICY "users own socratic messages"
  ON socratic_messages FOR ALL
  USING (session_id IN (SELECT id FROM socratic_sessions WHERE user_id = auth.uid()));

CREATE POLICY "users own socratic insight cards"
  ON socratic_insight_cards FOR ALL
  USING (session_id IN (SELECT id FROM socratic_sessions WHERE user_id = auth.uid()));

CREATE POLICY "users own socratic concepts"
  ON socratic_concepts FOR ALL
  USING (auth.uid() = user_id);
