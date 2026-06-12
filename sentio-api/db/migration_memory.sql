-- WS-1 Three-tier memory — run in Supabase SQL editor
-- Safe to re-run (all statements are idempotent).

-- ─────────────────────────────────────────────────────────────
-- 1. Episodic layer: one row per conversation session
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS memory_episodes (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         UUID REFERENCES profiles(id) ON DELETE CASCADE,
  conversation_id UUID REFERENCES ai_conversations(id) ON DELETE SET NULL,
  summary         TEXT NOT NULL,
  embedding       VECTOR(384),
  importance      FLOAT DEFAULT 1.0,
  consolidated    BOOLEAN DEFAULT FALSE,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_episodes_user_created
  ON memory_episodes(user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_episodes_embedding
  ON memory_episodes USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 20);

CREATE UNIQUE INDEX IF NOT EXISTS idx_episodes_conv
  ON memory_episodes(conversation_id)
  WHERE conversation_id IS NOT NULL;

-- ─────────────────────────────────────────────────────────────
-- 2. Semantic layer: consolidated, long-lived user facts
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS user_facts (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id             UUID REFERENCES profiles(id) ON DELETE CASCADE,
  fact                TEXT NOT NULL,
  embedding           VECTOR(384),
  importance          FLOAT DEFAULT 1.0,
  source_episode_ids  UUID[] DEFAULT '{}',
  consolidated_at     TIMESTAMPTZ DEFAULT NOW(),
  last_reinforced_at  TIMESTAMPTZ DEFAULT NOW(),
  access_count        INT DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_facts_user
  ON user_facts(user_id);

CREATE INDEX IF NOT EXISTS idx_facts_embedding
  ON user_facts USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 10);

-- ─────────────────────────────────────────────────────────────
-- 3. Decay-weighted retrieval across both tables
--
--    score = cosine_sim(q, m) × exp(−λ × age_days) × importance
--
--    λ_ep   = 0.05  → half-life ≈ 14 days  (fresh episodes decay faster)
--    λ_fact = 0.005 → half-life ≈ 140 days (facts persist much longer)
--
--    Cites: MemGPT (Packer 2023), generative-agents memory-stream (Park 2023)
-- ─────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION match_memory(
  p_user_id       UUID,
  query_embedding VECTOR(384),
  lambda_ep       FLOAT DEFAULT 0.05,
  lambda_fact     FLOAT DEFAULT 0.005,
  match_count     INT   DEFAULT 5
)
RETURNS TABLE (
  id         UUID,
  source     TEXT,
  content    TEXT,
  importance FLOAT,
  age_days   FLOAT,
  score      FLOAT
)
LANGUAGE sql STABLE AS $$
  SELECT
    id,
    'episode'::TEXT AS source,
    summary         AS content,
    importance,
    EXTRACT(EPOCH FROM (NOW() - created_at)) / 86400.0 AS age_days,
    (1 - (embedding <=> query_embedding))
      * EXP(-lambda_ep * EXTRACT(EPOCH FROM (NOW() - created_at)) / 86400.0)
      * importance AS score
  FROM memory_episodes
  WHERE user_id = p_user_id
    AND consolidated = FALSE
    AND embedding IS NOT NULL

  UNION ALL

  SELECT
    id,
    'fact'::TEXT AS source,
    fact         AS content,
    importance,
    EXTRACT(EPOCH FROM (NOW() - consolidated_at)) / 86400.0 AS age_days,
    (1 - (embedding <=> query_embedding))
      * EXP(-lambda_fact * EXTRACT(EPOCH FROM (NOW() - consolidated_at)) / 86400.0)
      * importance AS score
  FROM user_facts
  WHERE user_id = p_user_id
    AND embedding IS NOT NULL

  ORDER BY score DESC
  LIMIT match_count;
$$;

-- ─────────────────────────────────────────────────────────────
-- 4. Helper: increment fact access_count atomically
-- ─────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION increment_fact_access(p_fact_id UUID)
RETURNS void LANGUAGE sql SECURITY DEFINER AS $$
  UPDATE user_facts SET access_count = access_count + 1 WHERE id = p_fact_id;
$$;

-- ─────────────────────────────────────────────────────────────
-- 5. RLS policies
-- ─────────────────────────────────────────────────────────────
ALTER TABLE memory_episodes ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_facts      ENABLE ROW LEVEL SECURITY;

-- Users can only see and delete their own rows; writes go through service role
CREATE POLICY "episodes_select" ON memory_episodes FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "episodes_delete" ON memory_episodes FOR DELETE USING (auth.uid() = user_id);

CREATE POLICY "facts_select" ON user_facts FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "facts_delete" ON user_facts FOR DELETE USING (auth.uid() = user_id);
