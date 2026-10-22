PRAGMA foreign_keys = ON;

BEGIN IMMEDIATE;

INSERT OR IGNORE INTO object_type_registry(
    object_type, prefix, identity_layer, description, country_scoped
) VALUES
    ('PRODUCT_CATEGORY', 'PCAT', 'CANONICAL_OBJECT', 'Stable classification grouping products, platforms, solutions or services', 0),
    ('SECTOR', 'SEC', 'CANONICAL_OBJECT', 'Stable business or government sector classification', 0),
    ('GEOGRAPHY', 'GEO', 'CANONICAL_OBJECT', 'Geographic market or jurisdiction classification when first-class identity is useful', 0),
    ('BID', 'BID', 'CANONICAL_OBJECT', 'Access Asia or principal response/submission against a procurement or commercial request', 1),
    ('ACCESS_ASIA_PROJECT', 'AAPJ', 'CANONICAL_OBJECT', 'Access Asia execution project after award/contract activation; distinct from an external government PROJECT', 1);

INSERT INTO schema_meta(key, value) VALUES
    ('schema_version', '1.1.0'),
    ('identity_standard', 'canonical-object-identity-standard-v1.1'),
    ('commercial_data_standard', 'access-asia-commercial-data-standard-v1.0'),
    ('commercial_lineage_model', 'PX_OPPORTUNITY_TO_BID_TO_AWARD_TO_ACCESS_ASIA_PROJECT'),
    ('financial_fact_model', 'provenance_backed_observation_and_attribute_v1')
ON CONFLICT(key) DO UPDATE SET value = excluded.value;

PRAGMA user_version = 2;

COMMIT;
