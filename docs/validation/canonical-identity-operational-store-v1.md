# Canonical Identity / Operational Store v1 Validation

Status: candidate pending contract-test completion and SharePoint materialization.

Validation targets:
- canonical object identity is separate from source-system identity;
- existing ARGUS IDs are grandfathered and not renumbered silently;
- new objects receive immutable UUID primary keys and stable human-readable canonical IDs;
- supplier/OEM is an ORGANIZATION role, not a duplicate identity family;
- SQLite uses a single-file journal mode suitable for download/replace workflows;
- SharePoint is the mutable operational store and GitHub remains schema/governance authority;
- writes are single-writer, transactionally applied and integrity-checked;
- existing registry data is migrated without upgrading stale/unverified evidence to verified fact.
