-- WS-4: Crash-gap fix — analysis_status column on journal_entries
-- Idempotent: safe to re-run.
--
-- Purpose: track whether the background bias+NLP pipeline has processed each entry.
-- The scheduler sweeps for 'pending' entries older than 5 min and re-queues them,
-- recovering from server crashes that killed in-flight background tasks.

ALTER TABLE journal_entries
    ADD COLUMN IF NOT EXISTS analysis_status TEXT NOT NULL DEFAULT 'pending'
    CHECK (analysis_status IN ('pending', 'processing', 'done', 'failed'));

-- Back-fill existing rows that already have results (non-null detected_biases means done)
UPDATE journal_entries
   SET analysis_status = 'done'
 WHERE analysis_status = 'pending'
   AND detected_biases IS NOT NULL;

-- Partial index for the scheduler sweep — only indexes rows that need work
CREATE INDEX IF NOT EXISTS idx_journal_pending
    ON journal_entries (created_at)
    WHERE analysis_status = 'pending';
