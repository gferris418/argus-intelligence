-- ARGUS PostgreSQL operational projection v1.1
-- Additive fuzzy-search hardening discovered during final-schema benchmarking.
-- This migration adds a GiST trigram KNN index and replaces search_tenders in place
-- with mode-specific branches so fuzzy top-N queries can use nearest-neighbor ordering.

BEGIN;

CREATE INDEX IF NOT EXISTS idx_tender_title_trgm_gist
    ON argus.tender USING gist (title public.gist_trgm_ops);

CREATE OR REPLACE FUNCTION argus.search_tenders(
    p_mode text,
    p_query text,
    p_limit integer DEFAULT 20
)
RETURNS TABLE(
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
LANGUAGE plpgsql
STABLE
SECURITY DEFINER
SET search_path = pg_catalog, public, argus
AS $function$
DECLARE
    v_query text := btrim(p_query);
    v_limit integer := argus.enforce_result_limit(p_limit);
BEGIN
    IF length(v_query) = 0 THEN
        RETURN;
    END IF;

    IF p_mode = 'exact_reference' THEN
        RETURN QUERY
        SELECT t.canonical_tender_id,
               t.tender_reference,
               t.project_code,
               t.title,
               t.buyer_name,
               t.status,
               t.closing_at,
               t.source_url,
               1.0::real AS score
        FROM argus.tender AS t
        WHERE lower(t.tender_reference) = lower(v_query)
        ORDER BY t.closing_at DESC NULLS LAST, t.canonical_tender_id
        LIMIT v_limit;
        RETURN;
    END IF;

    IF p_mode = 'exact_project_code' THEN
        RETURN QUERY
        SELECT t.canonical_tender_id,
               t.tender_reference,
               t.project_code,
               t.title,
               t.buyer_name,
               t.status,
               t.closing_at,
               t.source_url,
               1.0::real AS score
        FROM argus.tender AS t
        WHERE lower(t.project_code) = lower(v_query)
        ORDER BY t.closing_at DESC NULLS LAST, t.canonical_tender_id
        LIMIT v_limit;
        RETURN;
    END IF;

    IF p_mode = 'fts' THEN
        RETURN QUERY
        SELECT t.canonical_tender_id,
               t.tender_reference,
               t.project_code,
               t.title,
               t.buyer_name,
               t.status,
               t.closing_at,
               t.source_url,
               ts_rank_cd(t.search_vector, websearch_to_tsquery('simple', v_query))::real AS score
        FROM argus.tender AS t
        WHERE t.search_vector @@ websearch_to_tsquery('simple', v_query)
        ORDER BY ts_rank_cd(t.search_vector, websearch_to_tsquery('simple', v_query)) DESC,
                 t.closing_at DESC NULLS LAST,
                 t.canonical_tender_id
        LIMIT v_limit;
        RETURN;
    END IF;

    IF p_mode = 'fuzzy' THEN
        RETURN QUERY
        SELECT t.canonical_tender_id,
               t.tender_reference,
               t.project_code,
               t.title,
               t.buyer_name,
               t.status,
               t.closing_at,
               t.source_url,
               (1.0 - (t.title OPERATOR(public.<->) v_query))::real AS score
        FROM argus.tender AS t
        ORDER BY t.title OPERATOR(public.<->) v_query,
                 t.canonical_tender_id
        LIMIT v_limit;
        RETURN;
    END IF;

    RAISE EXCEPTION 'unsupported tender search mode: %', p_mode USING ERRCODE = '22023';
END
$function$;

REVOKE ALL ON FUNCTION argus.search_tenders(text, text, integer) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION argus.search_tenders(text, text, integer) TO argus_reader, argus_writer;

INSERT INTO argus.schema_migration(migration_id, description)
VALUES (
    '0002_argus_fuzzy_knn',
    'Add GiST trigram nearest-neighbor fuzzy search and mode-specific search execution.'
)
ON CONFLICT (migration_id) DO NOTHING;

COMMIT;
