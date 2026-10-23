# PostgreSQL tender search v1 validation

**Date:** 2026-10-23  
**Database:** Neon PostgreSQL 18, `AccessAsia ARGUS`, database `argus`  
**Migration:** `registry/migrations/postgres-1.0.0-argus-tender-search.sql`

## Governance

The migration is versioned in GitHub and declared in `argus-intelligence.yaml`. Neon production is the runtime materialization; GitHub remains the schema authority.

Required platform roles already exist:

- `argus_owner`: migration owner;
- `argus_reader`: no-login read capability;
- `argus_writer`: no-login ingest capability;
- `argus_runtime`: login role inheriting the writer capability.

The migration grants the reader only function execution. It grants the writer select, insert and update, but not delete or truncate.

## Prepared-branch verification

Prepared branch: `mcp-migration-2026-10-23T00-12-58` / `br-weathered-shape-a1vgp1dc`.

The branch was populated with 10,000 synthetic tenders and 50 organizations. Verification established:

- exact reference returned the intended single tender;
- exact project code returned the intended single tender;
- full-text search returned the coastal patrol vessel tender;
- fuzzy fallback returned the same tender for `Coastal Patrl Vessel`;
- active-tender listing returned exactly 20 rows;
- a requested limit of 101 failed closed;
- `argus_reader` could execute search functions but could not select the tender table;
- `argus_writer` could select/insert/update but could not delete;
- the canonical-object update trigger advanced `updated_at`;
- PostgreSQL statistics recorded use of the exact-reference, project-code, full-text, status/closing and trigram indexes.

Warm server-side execution observed through the admitted functions:

| Path | Execution time |
|---|---:|
| Exact tender reference | 0.208 ms |
| Exact project code | 0.236 ms |
| Full-text search | 0.335 ms |
| Active + closing date, 20 rows | 0.289 ms |
| Fuzzy fallback | 0.467 ms |

These are synthetic warm-cache measurements, not production latency guarantees. Capacity validation at 100k and 1M records remains workload-driven follow-up.

## Production procedure

1. Require green ARGUS contract tests and cross-repository E2E for the exact GitHub revision.
2. Protect the production branch.
3. Create a named pre-migration snapshot.
4. Apply the exact prepared migration.
5. Verify migration receipt, tables, functions, grants, trigger and empty production row counts.
6. Run read-only smoke calls with limits 20 and 101.
7. On any failure, restore the named snapshot; do not patch production ad hoc.

Synthetic prepared-branch records are test data and are not copied into production.
