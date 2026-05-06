-- Phase 6: Community tables, badge system, and helper RPC functions
-- Run in Supabase SQL editor

-- ───────────────────────────────────────────────────
-- Community tables
-- ───────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS community_topics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  slug TEXT UNIQUE NOT NULL,
  description TEXT,
  icon TEXT,
  color TEXT,
  thread_count INT DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS community_threads (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  topic_id UUID REFERENCES community_topics(id) ON DELETE CASCADE,
  author_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  upvotes INT DEFAULT 0,
  reply_count INT DEFAULT 0,
  is_pinned BOOLEAN DEFAULT false,
  is_locked BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS community_replies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  thread_id UUID REFERENCES community_threads(id) ON DELETE CASCADE,
  author_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  body TEXT NOT NULL,
  upvotes INT DEFAULT 0,
  parent_reply_id UUID REFERENCES community_replies(id),
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS community_upvotes (
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  target_type TEXT NOT NULL,
  target_id UUID NOT NULL,
  PRIMARY KEY (user_id, target_type, target_id)
);

CREATE TABLE IF NOT EXISTS user_badges (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  badge_id TEXT NOT NULL,
  awarded_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(user_id, badge_id)
);

-- ───────────────────────────────────────────────────
-- RLS policies
-- ───────────────────────────────────────────────────

ALTER TABLE community_topics    ENABLE ROW LEVEL SECURITY;
ALTER TABLE community_threads   ENABLE ROW LEVEL SECURITY;
ALTER TABLE community_replies   ENABLE ROW LEVEL SECURITY;
ALTER TABLE community_upvotes   ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_badges         ENABLE ROW LEVEL SECURITY;

-- Topics: anyone authenticated can read
CREATE POLICY "community_topics_read" ON community_topics FOR SELECT USING (true);

-- Threads: anyone can read; only author can update/delete
CREATE POLICY "community_threads_read"   ON community_threads FOR SELECT USING (true);
CREATE POLICY "community_threads_insert" ON community_threads FOR INSERT WITH CHECK (auth.uid() = author_id);
CREATE POLICY "community_threads_update" ON community_threads FOR UPDATE USING (auth.uid() = author_id);
CREATE POLICY "community_threads_delete" ON community_threads FOR DELETE USING (auth.uid() = author_id);

-- Replies: same pattern
CREATE POLICY "community_replies_read"   ON community_replies FOR SELECT USING (true);
CREATE POLICY "community_replies_insert" ON community_replies FOR INSERT WITH CHECK (auth.uid() = author_id);
CREATE POLICY "community_replies_delete" ON community_replies FOR DELETE USING (auth.uid() = author_id);

-- Upvotes: user can only manage their own row
CREATE POLICY "community_upvotes_read"   ON community_upvotes FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "community_upvotes_insert" ON community_upvotes FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "community_upvotes_delete" ON community_upvotes FOR DELETE USING (auth.uid() = user_id);

-- Badges: all authenticated users can read; insert/delete via service role only
CREATE POLICY "user_badges_read" ON user_badges FOR SELECT USING (true);

-- ───────────────────────────────────────────────────
-- Helper RPC functions for atomic counters
-- ───────────────────────────────────────────────────

CREATE OR REPLACE FUNCTION increment_topic_thread_count(p_topic_id UUID)
RETURNS void LANGUAGE sql SECURITY DEFINER AS $$
  UPDATE community_topics SET thread_count = thread_count + 1 WHERE id = p_topic_id;
$$;

CREATE OR REPLACE FUNCTION increment_thread_reply_count(p_thread_id UUID)
RETURNS void LANGUAGE sql SECURITY DEFINER AS $$
  UPDATE community_threads SET reply_count = reply_count + 1 WHERE id = p_thread_id;
$$;

CREATE OR REPLACE FUNCTION increment_thread_upvote(p_thread_id UUID)
RETURNS void LANGUAGE sql SECURITY DEFINER AS $$
  UPDATE community_threads SET upvotes = upvotes + 1 WHERE id = p_thread_id;
$$;

CREATE OR REPLACE FUNCTION decrement_thread_upvote(p_thread_id UUID)
RETURNS void LANGUAGE sql SECURITY DEFINER AS $$
  UPDATE community_threads SET upvotes = GREATEST(0, upvotes - 1) WHERE id = p_thread_id;
$$;

CREATE OR REPLACE FUNCTION increment_reply_upvote(p_reply_id UUID)
RETURNS void LANGUAGE sql SECURITY DEFINER AS $$
  UPDATE community_replies SET upvotes = upvotes + 1 WHERE id = p_reply_id;
$$;

CREATE OR REPLACE FUNCTION decrement_reply_upvote(p_reply_id UUID)
RETURNS void LANGUAGE sql SECURITY DEFINER AS $$
  UPDATE community_replies SET upvotes = GREATEST(0, upvotes - 1) WHERE id = p_reply_id;
$$;
