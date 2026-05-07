-- ─────────────────────────────────────────────────────────────────────────────
-- Sentio — therapists table DELTA migration
-- Adds new columns for scraper data alongside existing columns.
-- Run in Supabase SQL Editor. Safe to re-run.
--
-- Existing columns (kept as-is):
--   id, name, initials, credentials (ARRAY), specializations, languages,
--   bio, approach, session_formats (ARRAY), price_range (jsonb),
--   availability (jsonb), contact_info (jsonb), verified, rating,
--   review_count, experience_years, created_at
-- ─────────────────────────────────────────────────────────────────────────────

-- 1. Add new scraper columns (no-op if already present)
ALTER TABLE therapists ADD COLUMN IF NOT EXISTS pronouns        TEXT;
ALTER TABLE therapists ADD COLUMN IF NOT EXISTS photo_url       TEXT;
ALTER TABLE therapists ADD COLUMN IF NOT EXISTS city            TEXT;
ALTER TABLE therapists ADD COLUMN IF NOT EXISTS session_format  TEXT;        -- singular: 'online'|'in-person'|'both'
ALTER TABLE therapists ADD COLUMN IF NOT EXISTS fee             INTEGER;     -- INR per session
ALTER TABLE therapists ADD COLUMN IF NOT EXISTS session_duration TEXT;
ALTER TABLE therapists ADD COLUMN IF NOT EXISTS qualifications  TEXT[];      -- mirrors credentials ARRAY
ALTER TABLE therapists ADD COLUMN IF NOT EXISTS experience      TEXT;        -- free-text from TheMindClan
ALTER TABLE therapists ADD COLUMN IF NOT EXISTS source          TEXT;        -- 'themindclan'|'practo'|'manual'
ALTER TABLE therapists ADD COLUMN IF NOT EXISTS source_url      TEXT;        -- upsert key + "Connect" link
ALTER TABLE therapists ADD COLUMN IF NOT EXISTS accepting_clients BOOLEAN DEFAULT TRUE;
ALTER TABLE therapists ADD COLUMN IF NOT EXISTS lat             DOUBLE PRECISION;
ALTER TABLE therapists ADD COLUMN IF NOT EXISTS lng             DOUBLE PRECISION;
ALTER TABLE therapists ADD COLUMN IF NOT EXISTS updated_at      TIMESTAMPTZ DEFAULT NOW();

-- 2. Unique index on source_url (enables upsert on_conflict)
CREATE UNIQUE INDEX IF NOT EXISTS therapists_source_url_idx
    ON therapists (source_url)
    WHERE source_url IS NOT NULL;

-- 3. Trigger: keep updated_at current
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS therapists_updated_at ON therapists;
CREATE TRIGGER therapists_updated_at
    BEFORE UPDATE ON therapists
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 4. Haversine nearest-therapist function (fixed: alias in subquery)
CREATE OR REPLACE FUNCTION get_nearest_therapists(
    user_lat   DOUBLE PRECISION,
    user_lng   DOUBLE PRECISION,
    radius_km  DOUBLE PRECISION DEFAULT 50,
    max_rows   INTEGER DEFAULT 20
)
RETURNS TABLE (
    id               UUID,
    name             TEXT,
    city             TEXT,
    session_format   TEXT,
    specializations  TEXT[],
    qualifications   TEXT[],
    languages        TEXT[],
    fee              INTEGER,
    photo_url        TEXT,
    source_url       TEXT,
    verified         BOOLEAN,
    accepting_clients BOOLEAN,
    distance_km      DOUBLE PRECISION
) AS $$
    SELECT * FROM (
        SELECT
            id, name, city, session_format, specializations, qualifications,
            languages, fee, photo_url, source_url, verified, accepting_clients,
            (6371 * acos(LEAST(1.0,
                cos(radians(user_lat)) * cos(radians(lat)) *
                cos(radians(lng) - radians(user_lng)) +
                sin(radians(user_lat)) * sin(radians(lat))
            ))) AS distance_km
        FROM therapists
        WHERE lat IS NOT NULL AND lng IS NOT NULL AND verified = TRUE
    ) sub
    WHERE sub.distance_km < radius_km
    ORDER BY sub.distance_km
    LIMIT max_rows;
$$ LANGUAGE sql STABLE;

-- 5. RLS (adds policy if missing; existing policies are untouched)
ALTER TABLE therapists ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "anyone can read verified therapists" ON therapists;
CREATE POLICY "anyone can read verified therapists"
    ON therapists FOR SELECT
    USING (verified = TRUE);
