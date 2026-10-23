# PostgreSQL Production Hardening

## Status

**Production cutover is NOT APPROVED.**

PostgreSQL is an admitted ARGUS operational projection only. GitHub remains authoritative for the ordered migration chain, query adapter, recovery procedure, tests and benchmark contract. SharePoint SQLite remains the active production structured store until every gate below passes and ATLAS authorizes cutover.

## Production migration gate

Production migration may proceed only when all of the following are evidenced:

1. The exact ordered PostgreSQL migration chain and recovery procedure are committed to ARGUS GitHub.
2. The PostgreSQL projection is registered in `argus-intelligence.yaml` and remains marked `ADMITTED_NOT_PRODUCTION` until approval.
3. The typed query adapter enforces parameterized projections, `LIMIT <= 100`, read-only execution, timeout and exact -> FTS -> fuzzy fallback.
4. Neon production branch protection, a named pre-migration snapshot and separate least-privilege roles are verified.
5. Schema integrity and canonical identity/source-lineage checks pass.
6. Cold, warm, concurrent and scale benchmarks pass the committed benchmark contract.
7. Migration, post-migration smoke and rollback/restore rehearsal pass end-to-end on a disposable branch.

A partial pass does not authorize production migration.

## Ordered migration chain

The authoritative PostgreSQL chain is ordered and append-only:

1. `migrations/postgres/0001_argus_operational_projection.sql`
2. `migrations/postgres/0002_argus_fuzzy_knn.sql`

Apply every migration in this order. Each migration must be safe to rerun. Once a numbered migration has been applied to an authoritative environment, never silently rewrite its semantics; corrections use the next numbered migration.

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

The repository migration creates non-login grant roles (`argus_reader`, `argus_writer`). Deployment-specific login roles may inherit them, but credentials are never committed to GitHub. Any legacy or unused login inheriting `neon_superuser`, `CREATEROLE` or `CREATEDB` is a production blocker even when it currently has no password; it must be retired or replaced before cutover approval.

## Migration rehearsal

Rehearse on a branch created from the current production head.

1. Verify source branch identity and schema fingerprint.
2. Apply `0001_argus_operational_projection.sql`, then `0002_argus_fuzzy_knn.sql` in order.
3. Reapply the complete chain; the second execution must be idempotent.
4. Run schema-contract tests and integrity checks.
5. Load representative synthetic data using deterministic seeds.
6. Run **post-migration smoke** checks.
7. Run the committed benchmark matrix.
8. Execute the **rollback** / forward-recovery procedure below.
9. Perform a **restore rehearsal** from the named snapshot or branch restore point.
10. Compare restored schema/data fingerprints with the pre-migration baseline.

Do not promote a rehearsal branch to production.

Run each concurrency cell from an independent network client with
`tools/postgres_benchmark.py`. Install the hash-locked dependencies from
`requirements-postgres-benchmark.lock`, inject the connection string through the
`ARGUS_BENCHMARK_DSN` environment variable, and pass the exact expected Neon
branch ID. The runner rejects a branch mismatch, accepts only the governed
1/8/32-reader and 0/1/4-writer levels, executes fixed projected SQL, and rolls
back every synthetic writer update. A writer scenario also requires the explicit
`--enable-rollback-writes` acknowledgement. Example:

```bash
python -m pip install --require-hashes --requirement requirements-postgres-benchmark.lock
ARGUS_BENCHMARK_DSN="$INJECTED_NONPRODUCTION_SECRET" python -m tools.postgres_benchmark \
  --expected-branch-id br-example \
  --dataset-scale 100000 \
  --cache-state warm \
  --readers 8 \
  --writers 1 \
  --duration 60 \
  --git-commit "$VALIDATED_ARGUS_COMMIT" \
  --enable-rollback-writes \
  --output benchmark-100k-r8-w1.json
```

Never run benchmark load against the production branch. Store credentials only
in the external secret injector; do not pass a DSN as a command-line argument or
commit it in a report.

## Post-migration smoke checks

The authorized production run must stop and restore if any mandatory smoke check fails.

- `argus.schema_migration` contains exactly one row for `0001_argus_operational_projection` and exactly one row for `0002_argus_fuzzy_knn`.
- `argus.canonical_object`, `argus.source_record` and `argus.tender` exist.
- all active canonical object types from `profiles/canonical-object-identity-standard-v1.0.yaml` are admitted, including `PROCUREMENT_PACKAGE`.
- canonical-object status and tender lifecycle status remain separate vocabularies.
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
- fuzzy top-N uses `idx_tender_title_trgm_gist` with trigram nearest-neighbor ordering rather than a sequential scan at 100k+ rows.
- statement timeout and read-only transaction behavior are verified.

## Rollback and forward recovery

The migrations are additive; the preferred recovery strategy is **restore**, not destructive down-migration.

### Before production cutover

If rehearsal fails, discard the disposable branch and correct the GitHub migration. Production remains unchanged.

### During an authorized production migration

If DDL application or mandatory smoke checks fail:

1. stop application traffic to the new PostgreSQL projection;
2. preserve migration logs and the failed branch/database state for diagnosis;
3. restore the named pre-migration snapshot / restore point to an isolated replacement branch;
4. verify schema and data fingerprints against the pre-migration receipt;
5. if direct finalized restore is supported, use the platform-supported cutover path; otherwise perform the application/endpoint rebind procedure below;
6. rebind application credentials only after verification;
7. record the failed migration attempt and remediation in GitHub/operational audit records.

Do not attempt ad-hoc `DROP TABLE`, `TRUNCATE` or manual row deletion as rollback.

### Neon Realtime restore boundary

As of the 2026-10-23 rehearsal, Neon rejected `finalize_restore=true` for the production snapshot because the source branch has Neon Realtime enabled. A non-finalized isolated snapshot restore succeeded and produced an empty schema diff against production.

Therefore, while Realtime remains enabled, production recovery must not assume that snapshot restore can atomically finalize onto the existing production routing. The supported fallback is an application-level rebind to a verified isolated restore branch.

#### Realtime-safe application/endpoint rebind procedure

1. Restore the named pre-migration snapshot with `finalize: false` into a new isolated branch.
2. Keep the existing production branch and endpoint unchanged while verification runs.
3. Verify restored database name, schema fingerprint, canonical row counts, source-lineage FKs and application smoke queries.
4. Resolve the restored branch's read-write compute endpoint and obtain fresh bounded application credentials for that branch; never reuse migration credentials.
5. Update the application/backend database secret or connection setting to the restored branch endpoint in the deployment system that owns the secret. Do not commit a connection string to GitHub.
6. Restart or redeploy the backend so connection pools drop the failed-production endpoint and reconnect to the restored branch.
7. Verify application read/write smoke, the typed ARGUS search functions, statement timeout/read-only behavior, and any Realtime-dependent workflow against the restored branch.
8. If Realtime must be reprovisioned or rebound for the restored branch, complete that platform step and verify token issuance/subscription behavior before accepting traffic.
9. Record the active branch ID, endpoint ID, credential identity, application deployment/version and verification timestamp in the recovery receipt.
10. Keep the old production branch isolated and unchanged until the restored branch has passed the complete acceptance checklist.

#### Reverse/fallback step

If the restored-branch application rebind fails before new authoritative writes are accepted, restore the application secret/configuration to the original production endpoint, restart/redeploy the backend, verify original production health, and record the failed recovery attempt. If authoritative writes have already occurred on the restored branch, do not switch back blindly; reconcile the write set under ATLAS governance first.

A successful isolated restore is necessary evidence but is not, by itself, equivalent to a rehearsed production traffic cutover. The application-level secret/configuration owner must therefore participate in the final recovery rehearsal before production approval.

### Forward recovery

Once production has intentionally written canonical state into PostgreSQL, corrections must use a new numbered migration. Never silently edit an already-applied numbered migration.

## RLS boundary

RLS is not required solely for a single-tenant, service-only database where clients cannot connect directly and least-privilege server roles are enforced. RLS becomes a required design review before enabling browser/Data API access, external tenant separation or user-scoped direct database access.

## Required migration receipt

Record at minimum:

- ARGUS Git commit and migration checksums;
- ordered migration list applied;
- Neon project, production branch and rehearsal branch IDs;
- production protection state;
- pre-migration snapshot ID;
- PostgreSQL version and compute configuration;
- migration role identity (never credentials);
- row counts and integrity results;
- smoke-check result;
- benchmark report pointer;
- restore rehearsal result and, where Realtime prevents finalized restore, the verified application/endpoint rebind procedure;
- ATLAS approval reference for production cutover.
