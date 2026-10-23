-- ARGUS PostgreSQL operational projection v1
-- Status: admitted projection, NOT approved for production cutover.
-- Canonical authority: GitHub. This migration is additive and idempotent.

BEGIN;

CREATE SCHEMA IF NOT EXISTS argus;
CREATE EXTENSION IF NOT EXISTS pg_trgm WITH SCHEMA public;

DO $roles$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'argus_reader') THEN
        CREATE ROLE argus_reader NOLOGIN;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'argus_writer') THEN
        CREATE ROLE argus_writer NOLOGIN;
    END IF;
END
$roles$;

CREATE TABLE IF NOT EXISTS argus.schema_migration (
    migration_id text PRIMARY KEY,
    applied_at timestamptz NOT NULL DEFAULT now(),
    description text NOT NULL,
    git_commit text,
    checksum_sha256 text
);

CREATE TABLE IF NOT EXISTS argus.object_type_registry (
    object_type text PRIMARY KEY,
    description text NOT NULL
);

INSERT INTO argus.object_type_registry(object_type, description) VALUES
    ('POLICY', 'Policy or formal policy instrument'),
    ('STRATEGY', 'Strategy or strategic plan'),
    ('PROGRAMME', 'Programme or program'),
    ('PROJECT', 'External government or public-sector project'),
    ('REQUIREMENT', 'Identified requirement or need'),
    ('PROCUREMENT_PLAN', 'Procurement planning object'),
    ('PACKAGE', 'Procurement package'),
    ('PROCUREMENT_PROCESS', 'Procurement process'),
    ('SOLICITATION', 'Tender, RFP, RFQ, EOI or equivalent solicitation'),
    ('LOT', 'Solicitation lot'),
    ('ITEM', 'Procurement item'),
    ('AWARD', 'Award decision'),
    ('CONTRACT', 'Contract'),
    ('ORGANIZATION', 'Organization or institution'),
    ('PERSON', 'Person'),
    ('PRODUCT', 'Product or solution'),
    ('PRODUCT_CATEGORY', 'Product or capability category'),
    ('SECTOR', 'Sector'),
    ('GEOGRAPHY', 'Geographic object'),
    ('FINANCING', 'Financing object'),
    ('DOCUMENT', 'Source or governed document identity'),
    ('OPPORTUNITY', 'ARGUS commercial opportunity'),
    ('BID', 'Access Asia bid or submission'),
    ('ACCESS_ASIA_PROJECT', 'Access Asia post-award project')
ON CONFLICT (object_type) DO NOTHING;

CREATE TABLE IF NOT EXISTS argus.status_registry (
    status text PRIMARY KEY,
    description text NOT NULL
);

INSERT INTO argus.status_registry(status, description) VALUES
    ('active', 'Current and active'),
    ('planned', 'Planned or pre-publication'),
    ('published', 'Published or open'),
    ('closed', 'Closed to new submissions'),
    ('awarded', 'Awarded'),
    ('cancelled', 'Cancelled'),
    ('superseded', 'Superseded by a newer object or state'),
    ('archived', 'Archived or historical')
ON CONFLICT (status) DO NOTHING;

CREATE TABLE IF NOT EXISTS argus.currency_registry (
    code text PRIMARY KEY,
    name text NOT NULL,
    CONSTRAINT currency_registry_code_format CHECK (code ~ '^[A-Z]{3}$')
);

INSERT INTO argus.currency_registry(code, name) VALUES
    ('AED', 'UAE Dirham'), ('AUD', 'Australian Dollar'), ('BDT', 'Bangladeshi Taka'),
    ('BRL', 'Brazilian Real'), ('CAD', 'Canadian Dollar'), ('CHF', 'Swiss Franc'),
    ('CNY', 'Chinese Yuan'), ('DKK', 'Danish Krone'), ('EUR', 'Euro'),
    ('GBP', 'Pound Sterling'), ('IDR', 'Indonesian Rupiah'), ('INR', 'Indian Rupee'),
    ('JPY', 'Japanese Yen'), ('KRW', 'South Korean Won'), ('KWD', 'Kuwaiti Dinar'),
    ('LKR', 'Sri Lankan Rupee'), ('MXN', 'Mexican Peso'), ('MYR', 'Malaysian Ringgit'),
    ('NOK', 'Norwegian Krone'), ('NZD', 'New Zealand Dollar'), ('OMR', 'Omani Rial'),
    ('PHP', 'Philippine Peso'), ('PKR', 'Pakistani Rupee'), ('QAR', 'Qatari Riyal'),
    ('RUB', 'Russian Ruble'), ('SAR', 'Saudi Riyal'), ('SEK', 'Swedish Krona'),
    ('SGD', 'Singapore Dollar'), ('THB', 'Thai Baht'), ('TRY', 'Turkish Lira'),
    ('USD', 'US Dollar'), ('ZAR', 'South African Rand')
ON CONFLICT (code) DO NOTHING;

CREATE TABLE IF NOT EXISTS argus.source_record (
    source_record_id text PRIMARY KEY,
    source_system text NOT NULL,
    native_id text NOT NULL,
    record_type text NOT NULL,
    source_url text,
    observed_at timestamptz NOT NULL,
    content_sha256 text,
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    CONSTRAINT source_record_id_nonempty CHECK (length(btrim(source_record_id)) > 0),
    CONSTRAINT source_record_system_nonempty CHECK (length(btrim(source_system)) > 0),
    CONSTRAINT source_record_native_id_nonempty CHECK (length(btrim(native_id)) > 0),
    CONSTRAINT source_record_unique_native UNIQUE (source_system, native_id)
);

CREATE TABLE IF NOT EXISTS argus.canonical_object (
    internal_id uuid PRIMARY KEY,
    canonical_id text NOT NULL UNIQUE,
    object_type text NOT NULL REFERENCES argus.object_type_registry(object_type) ON UPDATE RESTRICT ON DELETE RESTRICT,
    canonical_name text NOT NULL,
    status text NOT NULL DEFAULT 'active' REFERENCES argus.status_registry(status) ON UPDATE RESTRICT ON DELETE RESTRICT,
    jurisdiction text,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    attributes jsonb NOT NULL DEFAULT '{}'::jsonb,
    CONSTRAINT canonical_object_id_nonempty CHECK (length(btrim(canonical_id)) > 0),
    CONSTRAINT canonical_object_name_nonempty CHECK (length(btrim(canonical_name)) > 0),
    CONSTRAINT canonical_object_jurisdiction_format CHECK (jurisdiction IS NULL OR jurisdiction ~ '^[A-Z]{2}(-[A-Z0-9]{1,8})?$')
);

CREATE OR REPLACE FUNCTION argus.touch_updated_at()
RETURNS trigger
LANGUAGE plpgsql
SET search_path = pg_catalog, argus
AS $function$
BEGIN
    NEW.updated_at := now();
    RETURN NEW;
END
$function$;

DO $trigger$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_trigger
        WHERE tgname = 'canonical_object_set_updated_at'
          AND tgrelid = 'argus.canonical_object'::regclass
          AND NOT tgisinternal
    ) THEN
        CREATE TRIGGER canonical_object_set_updated_at
        BEFORE UPDATE ON argus.canonical_object
        FOR EACH ROW EXECUTE FUNCTION argus.touch_updated_at();
    END IF;
END
$trigger$;

CREATE TABLE IF NOT EXISTS argus.tender (
    canonical_tender_id text PRIMARY KEY REFERENCES argus.canonical_object(canonical_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    tender_reference text,
    project_code text,
    package_no text,
    title text NOT NULL,
    buyer_org_id text REFERENCES argus.canonical_object(canonical_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    buyer_name text,
    ministry_org_id text REFERENCES argus.canonical_object(canonical_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    ministry_name text,
    jurisdiction text NOT NULL,
    source_system text NOT NULL,
    source_record_id text NOT NULL REFERENCES argus.source_record(source_record_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    district text,
    procurement_method text,
    procurement_type text,
    status text NOT NULL DEFAULT 'active' REFERENCES argus.status_registry(status) ON UPDATE RESTRICT ON DELETE RESTRICT,
    publication_date date,
    closing_at timestamptz,
    opening_at timestamptz,
    pre_tender_meeting_at timestamptz,
    budget_source text,
    currency_code text REFERENCES argus.currency_registry(code) ON UPDATE RESTRICT ON DELETE RESTRICT,
    estimated_value numeric(20,2),
    tender_security numeric(20,2),
    source_url text,
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
    CONSTRAINT tender_jurisdiction_format CHECK (jurisdiction ~ '^[A-Z]{2}(-[A-Z0-9]{1,8})?$'),
    CONSTRAINT tender_source_system_nonempty CHECK (length(btrim(source_system)) > 0),
    CONSTRAINT tender_values_nonnegative CHECK (
        (estimated_value IS NULL OR estimated_value >= 0) AND
        (tender_security IS NULL OR tender_security >= 0)
    )
);

-- Tender references are unique only within their source/jurisdiction namespace.
-- Project codes intentionally remain non-unique because one project can issue many tenders.
CREATE UNIQUE INDEX IF NOT EXISTS uq_tender_reference_scope
    ON argus.tender (jurisdiction, source_system, lower(tender_reference))
    WHERE tender_reference IS NOT NULL AND length(btrim(tender_reference)) > 0;

CREATE INDEX IF NOT EXISTS idx_canonical_object_type_status
    ON argus.canonical_object (object_type, status);
CREATE INDEX IF NOT EXISTS idx_canonical_object_name_trgm
    ON argus.canonical_object USING gin (canonical_name public.gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_tender_reference_lower
    ON argus.tender (lower(tender_reference));
CREATE INDEX IF NOT EXISTS idx_tender_project_code_lower
    ON argus.tender (lower(project_code));
CREATE INDEX IF NOT EXISTS idx_tender_search_vector
    ON argus.tender USING gin (search_vector);
CREATE INDEX IF NOT EXISTS idx_tender_title_trgm
    ON argus.tender USING gin (title public.gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_tender_buyer_name_trgm
    ON argus.tender USING gin (buyer_name public.gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_tender_status_closing
    ON argus.tender (status, closing_at);
CREATE INDEX IF NOT EXISTS idx_tender_buyer_closing
    ON argus.tender (buyer_org_id, closing_at DESC);
CREATE INDEX IF NOT EXISTS idx_tender_publication_date
    ON argus.tender (publication_date DESC);

CREATE OR REPLACE FUNCTION argus.enforce_result_limit(p_limit integer)
RETURNS integer
LANGUAGE plpgsql
IMMUTABLE STRICT
SET search_path = pg_catalog
AS $function$
BEGIN
    IF p_limit < 1 OR p_limit > 100 THEN
        RAISE EXCEPTION 'result limit must be between 1 and 100' USING ERRCODE = '22023';
    END IF;
    RETURN p_limit;
END
$function$;

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
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = pg_catalog, public, argus
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
           WHEN p_mode = 'fts' THEN ts_rank_cd(t.search_vector, websearch_to_tsquery('simple', btrim(p_query)))::real
           WHEN p_mode = 'fuzzy' THEN public.similarity(t.title, btrim(p_query))::real
       END AS score
FROM argus.tender AS t
WHERE p_mode IN ('exact_reference', 'exact_project_code', 'fts', 'fuzzy')
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
RETURNS TABLE(
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
WHERE t.status = p_status
  AND (p_buyer_org_id IS NULL OR t.buyer_org_id = p_buyer_org_id)
ORDER BY t.closing_at NULLS LAST, t.canonical_tender_id
LIMIT argus.enforce_result_limit(p_limit)
$function$;

REVOKE ALL ON SCHEMA argus FROM PUBLIC;
GRANT USAGE ON SCHEMA argus TO argus_reader;
GRANT USAGE ON SCHEMA argus TO argus_writer;

REVOKE ALL ON FUNCTION argus.enforce_result_limit(integer) FROM PUBLIC;
REVOKE ALL ON FUNCTION argus.search_tenders(text, text, integer) FROM PUBLIC;
REVOKE ALL ON FUNCTION argus.list_tenders(text, text, integer) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION argus.search_tenders(text, text, integer) TO argus_reader, argus_writer;
GRANT EXECUTE ON FUNCTION argus.list_tenders(text, text, integer) TO argus_reader, argus_writer;

-- Runtime readers get function execution only; direct table access is intentionally absent.
GRANT SELECT, INSERT, UPDATE ON argus.source_record TO argus_writer;
GRANT SELECT, INSERT, UPDATE ON argus.canonical_object TO argus_writer;
GRANT SELECT, INSERT, UPDATE ON argus.tender TO argus_writer;
GRANT SELECT ON argus.object_type_registry, argus.status_registry, argus.currency_registry TO argus_writer;
GRANT SELECT, INSERT ON argus.schema_migration TO argus_writer;

ALTER ROLE argus_reader SET default_transaction_read_only = on;
ALTER ROLE argus_reader SET statement_timeout = '2s';

INSERT INTO argus.schema_migration(migration_id, description)
VALUES ('0001_argus_operational_projection', 'Initial governed PostgreSQL operational projection for ARGUS')
ON CONFLICT (migration_id) DO NOTHING;

COMMIT;
