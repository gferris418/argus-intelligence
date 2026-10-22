PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA synchronous = FULL;

CREATE TABLE IF NOT EXISTS metadata (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS id_counters (
  object_prefix TEXT NOT NULL,
  jurisdiction TEXT NOT NULL,
  next_value INTEGER NOT NULL CHECK(next_value >= 1),
  PRIMARY KEY (object_prefix, jurisdiction)
);

CREATE TABLE IF NOT EXISTS canonical_objects (
  internal_uuid TEXT PRIMARY KEY,
  canonical_id TEXT NOT NULL UNIQUE,
  object_type TEXT NOT NULL,
  jurisdiction TEXT,
  title TEXT NOT NULL,
  description TEXT,
  record_state TEXT NOT NULL DEFAULT 'CURRENT',
  valid_from TEXT,
  valid_to TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  CHECK (record_state IN ('CANDIDATE','CURRENT','SUPERSEDED','ARCHIVED'))
);
CREATE INDEX IF NOT EXISTS idx_canonical_objects_type ON canonical_objects(object_type);
CREATE INDEX IF NOT EXISTS idx_canonical_objects_title ON canonical_objects(title);

CREATE TABLE IF NOT EXISTS external_identifiers (
  external_identifier_id TEXT PRIMARY KEY,
  object_uuid TEXT NOT NULL REFERENCES canonical_objects(internal_uuid),
  source_system TEXT NOT NULL,
  scheme TEXT NOT NULL,
  value TEXT NOT NULL,
  scope TEXT,
  source_label TEXT,
  first_seen_at TEXT NOT NULL,
  last_seen_at TEXT NOT NULL,
  UNIQUE(source_system, scheme, value, object_uuid)
);
CREATE INDEX IF NOT EXISTS idx_external_identifier_lookup ON external_identifiers(source_system, scheme, value);

CREATE TABLE IF NOT EXISTS relationships (
  relationship_id TEXT PRIMARY KEY,
  subject_uuid TEXT NOT NULL REFERENCES canonical_objects(internal_uuid),
  predicate TEXT NOT NULL,
  object_uuid TEXT NOT NULL REFERENCES canonical_objects(internal_uuid),
  status TEXT NOT NULL DEFAULT 'CURRENT',
  source_record_id TEXT,
  valid_from TEXT,
  valid_to TEXT,
  created_at TEXT NOT NULL,
  UNIQUE(subject_uuid, predicate, object_uuid, valid_from)
);
CREATE INDEX IF NOT EXISTS idx_relationship_subject ON relationships(subject_uuid);
CREATE INDEX IF NOT EXISTS idx_relationship_object ON relationships(object_uuid);

CREATE TABLE IF NOT EXISTS source_records (
  source_record_id TEXT PRIMARY KEY,
  source_system TEXT NOT NULL,
  native_id TEXT,
  native_reference TEXT,
  source_url TEXT,
  source_record_type TEXT,
  title_raw TEXT,
  published_at TEXT,
  observed_at TEXT NOT NULL,
  content_hash TEXT,
  access_class TEXT,
  supersedes_source_record_id TEXT REFERENCES source_records(source_record_id),
  canonical_object_uuid TEXT REFERENCES canonical_objects(internal_uuid),
  raw_payload_ref TEXT
);
CREATE INDEX IF NOT EXISTS idx_source_native ON source_records(source_system, native_id);
CREATE INDEX IF NOT EXISTS idx_source_object ON source_records(canonical_object_uuid);

CREATE TABLE IF NOT EXISTS events (
  event_id TEXT PRIMARY KEY,
  event_type TEXT NOT NULL,
  subject_uuid TEXT NOT NULL REFERENCES canonical_objects(internal_uuid),
  occurred_at TEXT,
  published_at TEXT,
  source_record_id TEXT REFERENCES source_records(source_record_id),
  reason_raw TEXT,
  payload_json TEXT,
  created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_events_subject ON events(subject_uuid);

CREATE TABLE IF NOT EXISTS observations (
  observation_id TEXT PRIMARY KEY,
  subject_uuid TEXT NOT NULL REFERENCES canonical_objects(internal_uuid),
  field_path TEXT NOT NULL,
  normalized_value_json TEXT,
  raw_label TEXT,
  raw_value TEXT,
  source_record_id TEXT REFERENCES source_records(source_record_id),
  claim_type TEXT NOT NULL,
  condition TEXT NOT NULL,
  observed_at TEXT NOT NULL,
  confidence REAL,
  CHECK (claim_type IN ('FACT','DERIVED','INFERENCE','ASSUMPTION','UNKNOWN')),
  CHECK (condition IN ('CURRENT','STALE','CONFLICT','UNKNOWN'))
);
CREATE INDEX IF NOT EXISTS idx_observations_subject ON observations(subject_uuid);
CREATE INDEX IF NOT EXISTS idx_observations_field ON observations(field_path);

CREATE TABLE IF NOT EXISTS change_log (
  change_id TEXT PRIMARY KEY,
  changed_at TEXT NOT NULL,
  actor TEXT NOT NULL,
  operation TEXT NOT NULL,
  target_table TEXT NOT NULL,
  target_id TEXT NOT NULL,
  summary TEXT NOT NULL,
  prior_hash TEXT,
  new_hash TEXT
);

CREATE TABLE IF NOT EXISTS database_versions (
  version_id INTEGER PRIMARY KEY AUTOINCREMENT,
  schema_version TEXT NOT NULL,
  created_at TEXT NOT NULL,
  note TEXT
);
