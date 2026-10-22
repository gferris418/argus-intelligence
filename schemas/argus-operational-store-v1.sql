PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS schema_meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

INSERT OR IGNORE INTO schema_meta(key, value) VALUES
    ('schema_name', 'ARGUS Operational Master Registry'),
    ('schema_version', '1.0.0'),
    ('identity_standard', 'canonical-object-identity-standard-v1.0'),
    ('storage_model', 'single_writer_sqlite_sharepoint_materialization');

CREATE TABLE IF NOT EXISTS object_type_registry (
    object_type TEXT PRIMARY KEY,
    prefix TEXT NOT NULL UNIQUE,
    identity_layer TEXT NOT NULL DEFAULT 'CANONICAL_OBJECT',
    description TEXT NOT NULL,
    country_scoped INTEGER NOT NULL DEFAULT 1 CHECK (country_scoped IN (0,1)),
    active INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0,1))
);

INSERT OR IGNORE INTO object_type_registry(object_type, prefix, identity_layer, description, country_scoped) VALUES
    ('POLICY', 'POL', 'CANONICAL_OBJECT', 'Government policy or authoritative policy instrument', 1),
    ('STRATEGY', 'STR', 'CANONICAL_OBJECT', 'Strategy, master plan or sector plan', 1),
    ('PROGRAMME', 'PRG', 'CANONICAL_OBJECT', 'Programme grouping related projects or initiatives', 1),
    ('PROJECT', 'PRJ', 'CANONICAL_OBJECT', 'Project or implementation initiative', 1),
    ('REQUIREMENT', 'REQ', 'CANONICAL_OBJECT', 'Underlying government or commercial requirement/need', 1),
    ('PROCUREMENT_PLAN', 'PLN', 'CANONICAL_OBJECT', 'APP, procurement plan or equivalent planning object', 1),
    ('PROCUREMENT_PACKAGE', 'PKG', 'CANONICAL_OBJECT', 'Procurement package beneath a plan/project', 1),
    ('PROCUREMENT_PROCESS', 'PROC', 'CANONICAL_OBJECT', 'One procurement process/cycle', 1),
    ('SOLICITATION', 'TND', 'CANONICAL_OBJECT', 'Tender, RFP, RFQ, EOI or other solicitation', 1),
    ('LOT', 'LOT', 'CANONICAL_OBJECT', 'Separately identifiable lot within a procurement', 1),
    ('ITEM', 'ITM', 'CANONICAL_OBJECT', 'Separately identifiable procured item or service line', 1),
    ('AWARD', 'AWD', 'CANONICAL_OBJECT', 'Award decision', 1),
    ('CONTRACT', 'CTR', 'CANONICAL_OBJECT', 'Contract resulting from an award', 1),
    ('ORGANIZATION', 'ENT', 'CANONICAL_OBJECT', 'Organization, authority, agency, supplier, OEM or other legal/organizational entity', 0),
    ('PERSON', 'PER', 'CANONICAL_OBJECT', 'Person when identity is materially required and lawfully retained', 0),
    ('PRODUCT', 'PRD', 'CANONICAL_OBJECT', 'Product, platform, solution or service offering', 0),
    ('FINANCING', 'FND', 'CANONICAL_OBJECT', 'Financing instrument or facility', 1),
    ('DOCUMENT', 'DOC', 'CANONICAL_OBJECT', 'Material document when it requires first-class identity', 1),
    ('OPPORTUNITY', 'OPP', 'CANONICAL_OBJECT', 'Commercial opportunity object; legacy ARGUS-OPP identifiers remain valid', 1);

CREATE TABLE IF NOT EXISTS id_sequence (
    object_type TEXT NOT NULL REFERENCES object_type_registry(object_type),
    jurisdiction TEXT NOT NULL,
    next_value INTEGER NOT NULL DEFAULT 1 CHECK (next_value >= 1),
    PRIMARY KEY (object_type, jurisdiction)
);

CREATE TABLE IF NOT EXISTS canonical_object (
    internal_id TEXT PRIMARY KEY,
    canonical_id TEXT NOT NULL UNIQUE,
    object_type TEXT NOT NULL REFERENCES object_type_registry(object_type),
    jurisdiction TEXT,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'CURRENT',
    legacy_identity INTEGER NOT NULL DEFAULT 0 CHECK (legacy_identity IN (0,1)),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_canonical_object_type ON canonical_object(object_type);
CREATE INDEX IF NOT EXISTS idx_canonical_object_jurisdiction ON canonical_object(jurisdiction);
CREATE INDEX IF NOT EXISTS idx_canonical_object_title ON canonical_object(title);

CREATE TABLE IF NOT EXISTS source_record (
    source_record_id TEXT PRIMARY KEY,
    canonical_source_id TEXT UNIQUE,
    source_system TEXT NOT NULL,
    source_authority TEXT,
    native_id TEXT,
    record_type TEXT NOT NULL,
    source_url TEXT,
    published_at TEXT,
    observed_at TEXT NOT NULL,
    content_hash TEXT,
    raw_title TEXT,
    access_class TEXT,
    immutable INTEGER NOT NULL DEFAULT 1 CHECK (immutable IN (0,1)),
    UNIQUE (source_system, native_id, record_type)
);

CREATE INDEX IF NOT EXISTS idx_source_record_system ON source_record(source_system);
CREATE INDEX IF NOT EXISTS idx_source_record_native ON source_record(native_id);

CREATE TABLE IF NOT EXISTS source_release (
    source_release_id TEXT PRIMARY KEY,
    source_record_id TEXT NOT NULL REFERENCES source_record(source_record_id) ON DELETE CASCADE,
    recorded_at TEXT NOT NULL,
    release_type TEXT NOT NULL,
    content_hash TEXT,
    supersedes_release_id TEXT REFERENCES source_release(source_release_id),
    raw_payload_json TEXT,
    immutable INTEGER NOT NULL DEFAULT 1 CHECK (immutable = 1)
);

CREATE TABLE IF NOT EXISTS source_object_link (
    source_record_id TEXT NOT NULL REFERENCES source_record(source_record_id) ON DELETE CASCADE,
    object_internal_id TEXT NOT NULL REFERENCES canonical_object(internal_id) ON DELETE CASCADE,
    relation_type TEXT NOT NULL,
    PRIMARY KEY (source_record_id, object_internal_id, relation_type)
);

CREATE TABLE IF NOT EXISTS external_identifier (
    identifier_id TEXT PRIMARY KEY,
    object_internal_id TEXT NOT NULL REFERENCES canonical_object(internal_id) ON DELETE CASCADE,
    source_system TEXT NOT NULL,
    scheme TEXT NOT NULL,
    value TEXT NOT NULL,
    scope TEXT NOT NULL DEFAULT 'OBJECT',
    source_record_id TEXT REFERENCES source_record(source_record_id),
    valid_from TEXT,
    valid_to TEXT,
    created_at TEXT NOT NULL,
    UNIQUE (source_system, scheme, value, scope)
);

CREATE INDEX IF NOT EXISTS idx_external_identifier_object ON external_identifier(object_internal_id);
CREATE INDEX IF NOT EXISTS idx_external_identifier_lookup ON external_identifier(source_system, scheme, value);

CREATE TABLE IF NOT EXISTS relationship (
    relationship_id TEXT PRIMARY KEY,
    from_object_internal_id TEXT NOT NULL REFERENCES canonical_object(internal_id) ON DELETE CASCADE,
    to_object_internal_id TEXT NOT NULL REFERENCES canonical_object(internal_id) ON DELETE CASCADE,
    relation_type TEXT NOT NULL,
    source_record_id TEXT REFERENCES source_record(source_record_id),
    valid_from TEXT,
    valid_to TEXT,
    status TEXT NOT NULL DEFAULT 'CURRENT',
    created_at TEXT NOT NULL,
    CHECK (from_object_internal_id <> to_object_internal_id)
);

CREATE INDEX IF NOT EXISTS idx_relationship_from ON relationship(from_object_internal_id);
CREATE INDEX IF NOT EXISTS idx_relationship_to ON relationship(to_object_internal_id);
CREATE INDEX IF NOT EXISTS idx_relationship_type ON relationship(relation_type);

CREATE TABLE IF NOT EXISTS event (
    event_id TEXT PRIMARY KEY,
    canonical_event_id TEXT UNIQUE,
    subject_object_internal_id TEXT NOT NULL REFERENCES canonical_object(internal_id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,
    occurred_at TEXT,
    published_at TEXT,
    source_record_id TEXT REFERENCES source_record(source_record_id),
    payload_json TEXT,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_event_subject ON event(subject_object_internal_id);
CREATE INDEX IF NOT EXISTS idx_event_type ON event(event_type);

CREATE TABLE IF NOT EXISTS observation (
    observation_id TEXT PRIMARY KEY,
    canonical_observation_id TEXT UNIQUE,
    subject_object_internal_id TEXT NOT NULL REFERENCES canonical_object(internal_id) ON DELETE CASCADE,
    field_path TEXT NOT NULL,
    value_json TEXT,
    raw_label TEXT,
    raw_value TEXT,
    source_record_id TEXT REFERENCES source_record(source_record_id),
    observed_at TEXT NOT NULL,
    published_at TEXT,
    claim_type TEXT NOT NULL DEFAULT 'FACT',
    condition TEXT NOT NULL DEFAULT 'CURRENT',
    confidence REAL,
    created_at TEXT NOT NULL,
    CHECK (confidence IS NULL OR (confidence >= 0 AND confidence <= 1))
);

CREATE INDEX IF NOT EXISTS idx_observation_subject ON observation(subject_object_internal_id);
CREATE INDEX IF NOT EXISTS idx_observation_field ON observation(field_path);

CREATE TABLE IF NOT EXISTS object_attribute (
    attribute_id TEXT PRIMARY KEY,
    object_internal_id TEXT NOT NULL REFERENCES canonical_object(internal_id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    value_json TEXT,
    value_type TEXT,
    source_record_id TEXT REFERENCES source_record(source_record_id),
    valid_from TEXT,
    valid_to TEXT,
    is_current INTEGER NOT NULL DEFAULT 1 CHECK (is_current IN (0,1)),
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_object_attribute_lookup ON object_attribute(object_internal_id, name, is_current);

CREATE TABLE IF NOT EXISTS object_payload (
    payload_id TEXT PRIMARY KEY,
    object_internal_id TEXT NOT NULL REFERENCES canonical_object(internal_id) ON DELETE CASCADE,
    schema_id TEXT NOT NULL,
    schema_version TEXT,
    payload_json TEXT NOT NULL,
    content_hash TEXT,
    compiled_at TEXT NOT NULL,
    is_current INTEGER NOT NULL DEFAULT 1 CHECK (is_current IN (0,1))
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_object_payload_current
ON object_payload(object_internal_id, schema_id)
WHERE is_current = 1;

CREATE TABLE IF NOT EXISTS mutation_log (
    mutation_id TEXT PRIMARY KEY,
    applied_at TEXT NOT NULL,
    actor TEXT NOT NULL,
    operation TEXT NOT NULL,
    object_internal_id TEXT REFERENCES canonical_object(internal_id),
    before_hash TEXT,
    after_hash TEXT,
    note TEXT
);

CREATE INDEX IF NOT EXISTS idx_mutation_log_applied ON mutation_log(applied_at);
