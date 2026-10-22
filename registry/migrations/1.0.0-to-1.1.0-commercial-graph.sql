PRAGMA foreign_keys = ON;
BEGIN IMMEDIATE;

INSERT OR IGNORE INTO object_type_registry(object_type, prefix, identity_layer, description, country_scoped) VALUES
    ('PRODUCT_CATEGORY', 'PCAT', 'CANONICAL_OBJECT', 'Stable classification grouping products, platforms, solutions or services', 0),
    ('SECTOR', 'SEC', 'CANONICAL_OBJECT', 'Stable business or government sector classification', 0),
    ('GEOGRAPHY', 'GEO', 'CANONICAL_OBJECT', 'Geographic market or jurisdiction classification when first-class identity is useful', 0),
    ('BID', 'BID', 'CANONICAL_OBJECT', 'Access Asia or principal response/submission against a procurement or commercial request', 1),
    ('ACCESS_ASIA_PROJECT', 'AAPJ', 'CANONICAL_OBJECT', 'Access Asia execution project created after award or contract activation', 1);

CREATE TABLE IF NOT EXISTS organization_role (
    role_assignment_id TEXT PRIMARY KEY,
    organization_internal_id TEXT NOT NULL REFERENCES canonical_object(internal_id) ON DELETE CASCADE,
    role_type TEXT NOT NULL,
    context_object_internal_id TEXT REFERENCES canonical_object(internal_id) ON DELETE CASCADE,
    source_record_id TEXT REFERENCES source_record(source_record_id),
    valid_from TEXT,
    valid_to TEXT,
    status TEXT NOT NULL DEFAULT 'CURRENT',
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_organization_role_org ON organization_role(organization_internal_id);
CREATE INDEX IF NOT EXISTS idx_organization_role_context ON organization_role(context_object_internal_id);
CREATE INDEX IF NOT EXISTS idx_organization_role_type ON organization_role(role_type);

CREATE TABLE IF NOT EXISTS commercial_lineage (
    commercial_px_id TEXT PRIMARY KEY,
    opportunity_internal_id TEXT NOT NULL UNIQUE REFERENCES canonical_object(internal_id) ON DELETE RESTRICT,
    assigned_at TEXT NOT NULL,
    assigned_by TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'ACTIVE',
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
);

CREATE TABLE IF NOT EXISTS commercial_lineage_member (
    member_id TEXT PRIMARY KEY,
    commercial_px_id TEXT NOT NULL REFERENCES commercial_lineage(commercial_px_id) ON DELETE CASCADE,
    object_internal_id TEXT NOT NULL UNIQUE REFERENCES canonical_object(internal_id) ON DELETE CASCADE,
    member_type TEXT NOT NULL CHECK (member_type IN ('OPPORTUNITY','BID','AWARD','ACCESS_ASIA_PROJECT')),
    sequence_no INTEGER NOT NULL DEFAULT 1 CHECK (sequence_no >= 1),
    created_at TEXT NOT NULL,
    UNIQUE (commercial_px_id, member_type, sequence_no)
);

CREATE INDEX IF NOT EXISTS idx_commercial_lineage_member_px ON commercial_lineage_member(commercial_px_id);
CREATE INDEX IF NOT EXISTS idx_commercial_lineage_member_type ON commercial_lineage_member(member_type);

CREATE TABLE IF NOT EXISTS financial_fact (
    financial_fact_id TEXT PRIMARY KEY,
    fact_type TEXT NOT NULL,
    commercial_px_id TEXT REFERENCES commercial_lineage(commercial_px_id) ON DELETE SET NULL,
    subject_object_internal_id TEXT REFERENCES canonical_object(internal_id) ON DELETE SET NULL,
    access_asia_project_internal_id TEXT REFERENCES canonical_object(internal_id) ON DELETE SET NULL,
    contract_internal_id TEXT REFERENCES canonical_object(internal_id) ON DELETE SET NULL,
    value_decimal TEXT NOT NULL,
    unit TEXT NOT NULL DEFAULT 'MONEY',
    currency_code TEXT,
    source_record_id TEXT REFERENCES source_record(source_record_id),
    effective_date TEXT,
    observed_at TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'CURRENT',
    created_at TEXT NOT NULL,
    CHECK (unit <> 'MONEY' OR currency_code IS NOT NULL)
);

CREATE INDEX IF NOT EXISTS idx_financial_fact_px ON financial_fact(commercial_px_id);
CREATE INDEX IF NOT EXISTS idx_financial_fact_type ON financial_fact(fact_type);
CREATE INDEX IF NOT EXISTS idx_financial_fact_project ON financial_fact(access_asia_project_internal_id);
CREATE INDEX IF NOT EXISTS idx_financial_fact_contract ON financial_fact(contract_internal_id);

CREATE VIEW IF NOT EXISTS reporting_fact_opportunity AS
SELECT
    l.commercial_px_id,
    o.internal_id AS opportunity_internal_id,
    o.canonical_id AS opportunity_id,
    o.title,
    o.status,
    o.jurisdiction,
    l.assigned_at,
    l.assigned_by
FROM commercial_lineage l
JOIN canonical_object o ON o.internal_id = l.opportunity_internal_id;

CREATE VIEW IF NOT EXISTS reporting_fact_bid AS
SELECT
    m.commercial_px_id,
    m.sequence_no,
    o.internal_id AS bid_internal_id,
    o.canonical_id AS bid_id,
    o.title,
    o.status,
    o.jurisdiction,
    o.created_at,
    o.updated_at
FROM commercial_lineage_member m
JOIN canonical_object o ON o.internal_id = m.object_internal_id
WHERE m.member_type = 'BID';

CREATE VIEW IF NOT EXISTS reporting_fact_award AS
SELECT
    m.commercial_px_id,
    m.sequence_no,
    o.internal_id AS award_internal_id,
    o.canonical_id AS award_id,
    o.title,
    o.status,
    o.jurisdiction,
    o.created_at,
    o.updated_at
FROM commercial_lineage_member m
JOIN canonical_object o ON o.internal_id = m.object_internal_id
WHERE m.member_type = 'AWARD';

CREATE VIEW IF NOT EXISTS reporting_fact_project AS
SELECT
    m.commercial_px_id,
    m.sequence_no,
    o.internal_id AS project_internal_id,
    o.canonical_id AS access_asia_project_id,
    o.title,
    o.status,
    o.jurisdiction,
    o.created_at,
    o.updated_at
FROM commercial_lineage_member m
JOIN canonical_object o ON o.internal_id = m.object_internal_id
WHERE m.member_type = 'ACCESS_ASIA_PROJECT';

CREATE VIEW IF NOT EXISTS reporting_financial_fact AS
SELECT
    f.financial_fact_id,
    f.fact_type,
    f.commercial_px_id,
    f.value_decimal,
    f.unit,
    f.currency_code,
    f.effective_date,
    f.observed_at,
    f.status,
    s.canonical_id AS subject_id,
    p.canonical_id AS access_asia_project_id,
    c.canonical_id AS contract_id
FROM financial_fact f
LEFT JOIN canonical_object s ON s.internal_id = f.subject_object_internal_id
LEFT JOIN canonical_object p ON p.internal_id = f.access_asia_project_internal_id
LEFT JOIN canonical_object c ON c.internal_id = f.contract_internal_id;

INSERT INTO schema_meta(key, value) VALUES ('schema_version', '1.1.0')
ON CONFLICT(key) DO UPDATE SET value = excluded.value;
INSERT INTO schema_meta(key, value) VALUES ('commercial_data_standard', 'access-asia-commercial-data-standard-v1.0')
ON CONFLICT(key) DO UPDATE SET value = excluded.value;
INSERT INTO schema_meta(key, value) VALUES ('commercial_graph_migration', '1.0.0-to-1.1.0-commercial-graph')
ON CONFLICT(key) DO UPDATE SET value = excluded.value;

PRAGMA user_version = 2;
COMMIT;
