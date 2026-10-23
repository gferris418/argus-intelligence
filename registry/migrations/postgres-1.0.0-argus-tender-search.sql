BEGIN;

CREATE EXTENSION IF NOT EXISTS pg_trgm WITH SCHEMA public;
CREATE EXTENSION IF NOT EXISTS moddatetime WITH SCHEMA public;
CREATE SCHEMA IF NOT EXISTS argus AUTHORIZATION argus_owner;

CREATE TABLE IF NOT EXISTS argus.schema_migration (
    migration_id text PRIMARY KEY,
    applied_at timestamptz NOT NULL DEFAULT now(),
    description text NOT NULL
);

CREATE TABLE IF NOT EXISTS argus.canonical_object (
    canonical_id text PRIMARY KEY,
    object_type text NOT NULL,
    canonical_name text NOT NULL,
    status text NOT NULL DEFAULT 'active',
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    attributes jsonb NOT NULL DEFAULT '{}'::jsonb,
    CONSTRAINT canonical_object_id_nonempty CHECK (length(btrim(canonical_id)) > 0),
    CONSTRAINT canonical_object_name_nonempty CHECK (length(btrim(canonical_name)) > 0),
    CONSTRAINT canonical_object_type_format CHECK (object_type ~ '^[A-Z][A-Z0-9_]*$'),
    CONSTRAINT canonical_object_status_format CHECK (status ~ '^[a-z][a-z0-9_]*$')
);

CREATE TABLE IF NOT EXISTS argus.tender (
    canonical_tender_id text PRIMARY KEY
        REFERENCES argus.canonical_object(canonical_id) ON DELETE RESTRICT,
    tender_reference text,
    project_code text,
    package_no text,
    title text NOT NULL,
    buyer_org_id text REFERENCES argus.canonical_object(canonical_id) ON DELETE RESTRICT,
    buyer_name text,
    ministry_org_id text REFERENCES argus.canonical_object(canonical_id) ON DELETE RESTRICT,
    ministry_name text,
    district text,
    procurement_method text,
    procurement_type text,
    status text NOT NULL DEFAULT 'active',
    publication_date date,
    closing_at timestamptz,
    opening_at timestamptz,
    pre_tender_meeting_at timestamptz,
    budget_source text,
    currency text,
    estimated_value numeric(20, 2),
    tender_security numeric(20, 2),
    source_url text,
    source_document_id text,
    attributes jsonb NOT NULL DEFAULT '{}'::jsonb,
    search_vector tsvector GENERATED ALWAYS AS (
        setweight(to_tsvector('simple', coalesce(tender_reference, '')), 'A') ||
        setweight(to_tsvector('simple', coalesce(project_code, '')), 'A') ||
        setweight(to_tsvector('simple', coalesce(title, '')), 'A') ||
        setweight(to_tsvector('simple', coalesce(buyer_name, '')), 'B') ||
        setweight(to_tsvector('simple', coalesce(ministry_name, '')), 'B') ||
        setweight(to_tsvector('simple', coalesce(procurement_method, '')), 'C') ||
        setweight(to_tsvector('simple', coalesce(district, '')), 'C')
    ) STORED,
    CONSTRAINT tender_title_nonempty CHECK (length(btrim(title)) > 0),
    CONSTRAINT tender_status_format CHECK (status ~ '^[a-z][a-z0-9_]*$'),
    CONSTRAINT tender_currency_iso3 CHECK (currency IS NULL OR currency ~ '^[A-Z]{3}$'),
    CONSTRAINT tender_values_nonnegative CHECK (
        (estimated_value IS NULL OR estimated_value >= 0) AND
        (tender_security IS NULL OR tender_security >= 0)
    )
);

CREATE INDEX IF NOT EXISTS idx_canonical_object_type_status
    ON argus.canonical_object (object_type, status);
CREATE INDEX IF NOT EXISTS idx_canonical_object_name_trgm
    ON argus.canonical_object USING gin (canonical_name public.gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_tender_reference_lower
    ON argus.tender (lower(tender_reference));
CREATE INDEX IF NOT EXISTS idx_tender_project_code_lower
    ON argus.tender (lower(project_code));
CREATE INDEX IF NOT EXISTS idx_tender_status_closing
    ON argus.tender (status, closing_at);
CREATE INDEX IF NOT EXISTS idx_tender_buyer_closing
    ON argus.tender (buyer_org_id, closing_at DESC);
CREATE INDEX IF NOT EXISTS idx_tender_publication_date
    ON argus.tender (publication_date DESC);
CREATE INDEX IF NOT EXISTS idx_tender_search_vector
    ON argus.tender USING gin (search_vector);
CREATE INDEX IF NOT EXISTS idx_tender_title_trgm
    ON argus.tender USING gin (title public.gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_tender_buyer_name_trgm
    ON argus.tender USING gin (buyer_name public.gin_trgm_ops);

CREATE OR REPLACE TRIGGER canonical_object_set_updated_at
BEFORE UPDATE ON argus.canonical_object
FOR EACH ROW EXECUTE FUNCTION public.moddatetime(updated_at);

CREATE OR REPLACE FUNCTION argus.enforce_result_limit(p_limit integer)
RETURNS integer
LANGUAGE sql
IMMUTABLE
STRICT
SET search_path = pg_catalog
AS $function$
SELECT CASE
    WHEN p_limit BETWEEN 1 AND 100 THEN p_limit
    ELSE 1 / (p_limit - p_limit)
END
$function$;

CREATE OR REPLACE FUNCTION argus.search_tenders(
    p_mode text,
    p_query text,
    p_limit integer DEFAULT 20
)
RETURNS TABLE (
    canonical_tender_id text,
    tender_reference text,
    project_code text,
    title text,
    buyer_name text,
    status text,
    closing_at timestamptz,
    source_url text,
    score real
)
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = pg_catalog, public, argus
SET statement_timeout = '2s'
AS $function$
SELECT t.canonical_tender_id,
       t.tender_reference,
       t.project_code,
       t.title,
       t.buyer_name,
       t.status,
       t.closing_at,
       t.source_url,
       CASE
           WHEN p_mode IN ('exact_reference', 'exact_project_code') THEN 1.0::real
           WHEN p_mode = 'fts' THEN
               ts_rank_cd(t.search_vector, websearch_to_tsquery('simple', btrim(p_query)))::real
           WHEN p_mode = 'fuzzy' THEN public.similarity(t.title, btrim(p_query))::real
       END AS score
FROM argus.tender AS t
WHERE p_limit BETWEEN 1 AND 100
  AND length(btrim(p_query)) > 0
  AND (
      (p_mode = 'exact_reference' AND lower(t.tender_reference) = lower(btrim(p_query))) OR
      (p_mode = 'exact_project_code' AND lower(t.project_code) = lower(btrim(p_query))) OR
      (p_mode = 'fts' AND t.search_vector @@ websearch_to_tsquery('simple', btrim(p_query))) OR
      (p_mode = 'fuzzy' AND t.title OPERATOR(public.%) btrim(p_query))
  )
ORDER BY score DESC, t.closing_at DESC NULLS LAST, t.canonical_tender_id
LIMIT argus.enforce_result_limit(p_limit)
$function$;

CREATE OR REPLACE FUNCTION argus.list_tenders(
    p_status text DEFAULT 'active',
    p_buyer_org_id text DEFAULT NULL,
    p_limit integer DEFAULT 20
)
RETURNS TABLE (
    canonical_tender_id text,
    tender_reference text,
    project_code text,
    title text,
    buyer_name text,
    status text,
    closing_at timestamptz,
    source_url text
)
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = pg_catalog, argus
SET statement_timeout = '2s'
AS $function$
SELECT t.canonical_tender_id,
       t.tender_reference,
       t.project_code,
       t.title,
       t.buyer_name,
       t.status,
       t.closing_at,
       t.source_url
FROM argus.tender AS t
WHERE p_limit BETWEEN 1 AND 100
  AND t.status = p_status
  AND (p_buyer_org_id IS NULL OR t.buyer_org_id = p_buyer_org_id)
ORDER BY t.closing_at NULLS LAST, t.canonical_tender_id
LIMIT argus.enforce_result_limit(p_limit)
$function$;

REVOKE ALL ON SCHEMA argus FROM PUBLIC;
REVOKE ALL ON ALL TABLES IN SCHEMA argus FROM PUBLIC, argus_reader, argus_writer;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA argus FROM PUBLIC;

GRANT USAGE ON SCHEMA argus TO argus_reader, argus_writer;
GRANT SELECT, INSERT, UPDATE ON argus.canonical_object, argus.tender TO argus_writer;
GRANT SELECT, INSERT ON argus.schema_migration TO argus_writer;
GRANT EXECUTE ON FUNCTION argus.search_tenders(text, text, integer) TO argus_reader, argus_writer;
GRANT EXECUTE ON FUNCTION argus.list_tenders(text, text, integer) TO argus_reader, argus_writer;

ALTER DEFAULT PRIVILEGES FOR ROLE argus_owner IN SCHEMA argus
    REVOKE ALL ON TABLES FROM PUBLIC;
ALTER DEFAULT PRIVILEGES FOR ROLE argus_owner IN SCHEMA argus
    REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;

INSERT INTO argus.schema_migration (migration_id, description)
VALUES (
    'postgres-1.0.0-argus-tender-search',
    'Versioned high-speed tender search schema with bounded read contracts'
)
ON CONFLICT (migration_id) DO NOTHING;

COMMIT;
