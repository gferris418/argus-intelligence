# PostgreSQL Production Hardening

## Status

**Production cutover is NOT APPROVED.**

PostgreSQL is an admitted ARGUS operational projection only. GitHub remains authoritative for the migration, query adapter, recovery procedure, tests and benchmark contract. SharePoint SQLite remains the active production structured store until every gate below passes and ATLAS authorizes cutover.

## Production migration gate

Production migration may proceed only when all of the following are evidenced:

1. The exact PostgreSQL migration and recovery procedure are committed to ARGUS GitHub.
2. The PostgreSQL projection is registered in `argus-intelligence.yaml` and remains marked `ADMITTED_NOT_PRODUCTION` until approval.
3. The typed query adapter enforces parameterized projections, `LIMIT <= 100`, read-only execution, timeout and exact -> FTS -> fuzzy fallback.
4. Neon production branch protection, a named pre-migration snapshot and separate least-privilege roles are verified.
5. Schema integrity and canonical identity/source-lineage checks pass.
6. Cold, warm, concurrent and scale benchmarks pass the committed benchmark contract.
7. Migration, post-migration smoke and rollback/restore rehearsal pass end-to-end on a disposable branch.

A partial pass does not authorize production migration.

## Pre-migration safeguards

### Production branch protection

Before any production migration, verify **production branch protection** is enabled and record the branch ID in the migration receipt. Branch protection is a deployment control; it does not replace database privileges.

### Named pre-migration snapshot

Create a named **pre-migration snapshot** immediately before the authorized migration. Record the snapshot identifier, source branch identifier, creation timestamp and the Git commit containing the migration. Do not reuse an old snapshot as proof for a new migration attempt.

### Role separation

Use a **dedicated migration role** for DDL. Do not use runtime search credentials for migration work.

Keep these authorities separate:

- migration role: temporary DDL authority required for the approved migration;
- writer role: bounded DML for authorized ingestion/reconciliation;
- reader/search role: read-only, function-level search access only;
- application credentials: separate from migration credentials and rotated independently.

The repository migration creates non-login grant roles (`argus_reader`, `argus_writer`). Deployment-specific login roles may inherit them, but credentials are never committed to GitHub.

## Migration rehearsal

Rehearse on a branch created from the current production head.

1. Verify source branch identity and schema fingerprint.
2. Apply `migrations/postgres/0001_argus_operational_projection.sql` twice; the second execution must be idempotent.
3. Run schema-contract tests and integrity checks.
4. Load representative synthetic data using deterministic seeds.
5. Run **post-migration smoke** checks.
6. Run the committed benchmark matrix.
7. Execute the **rollback** / forward-recovery procedure below.
8. Perform a **restore rehearsal** from the named snapshot or branch restore point.
9. Compare restored schema/data fingerprints with the pre-migration baseline.

Do not promote a rehearsal branch to production.

## Post-migration smoke checks

The authorized production run must stop and restore if any mandatory smoke check fails.

- `argus.schema_migration` contains exactly one row for migration `0001_argus_operational_projection`.
- `argus.canonical_object`, `argus.source_record` and `argus.tender` exist.
- canonical IDs and source-native identities satisfy uniqueness constraints.
- all tender buyer/ministry/source references resolve.
- project codes are permitted to repeat.
- tender references are unique only within `(jurisdiction, source_system)` scope.
- invalid object types, statuses and currencies are rejected by FK constraints.
- `updated_at` advances on canonical-object update.
- `argus_reader` cannot insert, update or delete table rows.
- `argus_reader` can execute the approved search/list functions.
- result limits above 100 are rejected.
- exact reference, project code, FTS and fuzzy searches return expected fixture records.
- statement timeout and read-only transaction behavior are verified.

## Rollback and forward recovery

This migration is additive; the preferred recovery strategy is **restore**, not destructive down-migration.

### Before production cutover

If rehearsal fails, discard the disposable branch and correct the GitHub migration. Production remains unchanged.

### During an authorized production migration

If DDL application or mandatory smoke checks fail:

1. stop application traffic to the new PostgreSQL projection;
2. preserve migration logs and the failed branch/database state for diagnosis;
3. restore the named pre-migration snapshot / restore point to a replacement production branch;
4. verify schema and data fingerprints against the pre-migration receipt;
5. rebind application credentials only after verification;
6. record the failed migration attempt and remediation in GitHub/operational audit records.

Do not attempt ad-hoc `DROP TABLE`, `TRUNCATE` or manual row deletion as rollback.

### Forward recovery

Once production has intentionally written canonical state into PostgreSQL, corrections must use a new numbered migration. Never silently edit `0001_argus_operational_projection.sql` after it has been applied to an authoritative environment.

## RLS boundary

RLS is not required solely for a single-tenant, service-only database where clients cannot connect directly and least-privilege server roles are enforced. RLS becomes a required design review before enabling browser/Data API access, external tenant separation or user-scoped direct database access.

## Required migration receipt

Record at minimum:

- ARGUS Git commit and migration checksum;
- Neon project, production branch and rehearsal branch IDs;
- production protection state;
- pre-migration snapshot ID;
- PostgreSQL version and compute configuration;
- migration role identity (never credentials);
- row counts and integrity results;
- smoke-check result;
- benchmark report pointer;
- restore rehearsal result;
- ATLAS approval reference for production cutover.
