-- Sentio — pgvector similarity search functions for Supabase RPC
-- Run this in the Supabase SQL editor after schema.sql.

-- ─────────────────────────────────────────────
-- Match knowledge articles by embedding similarity (for RAG)
-- ─────────────────────────────────────────────
CREATE OR REPLACE FUNCTION match_knowledge(
  query_embedding VECTOR(384),
  match_threshold FLOAT DEFAULT 0.7,
  match_count INT DEFAULT 10
)
RETURNS TABLE (
  id UUID,
  title TEXT,
  content TEXT,
  category TEXT,
  source_citation TEXT,
  similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    ka.id,
    ka.title,
    ka.content,
    ka.category,
    ka.source_citation,
    1 - (ka.embedding <=> query_embedding) AS similarity
  FROM knowledge_articles ka
  WHERE 1 - (ka.embedding <=> query_embedding) > match_threshold
  ORDER BY ka.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;

-- ─────────────────────────────────────────────
-- Match journal entries by semantic similarity
-- ─────────────────────────────────────────────
CREATE OR REPLACE FUNCTION match_journal_entries(
  query_embedding VECTOR(384),
  target_user_id UUID,
  match_threshold FLOAT DEFAULT 0.6,
  match_count INT DEFAULT 5
)
RETURNS TABLE (
  id UUID,
  content TEXT,
  themes JSONB,
  detected_biases JSONB,
  created_at TIMESTAMPTZ,
  similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    je.id,
    je.content,
    je.themes,
    je.detected_biases,
    je.created_at,
    1 - (je.embedding <=> query_embedding) AS similarity
  FROM journal_entries je
  WHERE je.user_id = target_user_id
    AND je.embedding IS NOT NULL
    AND 1 - (je.embedding <=> query_embedding) > match_threshold
  ORDER BY je.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;
