# Canonical ARGUS Registry Data

This directory is the interim physical canonical store for structured ARGUS records while GitHub is the active persistence layer.

## Preferred representation

Use JSON/JSONL conforming to the active ARGUS Registry schema.

### Initial baseline

`records.jsonl` is the immutable initial GitHub canonical baseline imported from the accepted DTIF migration pilot. It remains authoritative for provenance of that initial migration state and should not be rewritten simply because a record later changes.

### DTIF historical reconciliation

`dtif-reconciliation-receipt.json` records the final archive-only disposition of the retired DTIF source estate. It pins the exact hashes of DB-001/DB-002/DB-003, fingerprints the previously accepted 131-record Wave-1 database state, and dispositions the remaining legacy classes without bulk-promoting stale or unverified records.

The historical Wave-1 database is **not** a second canonical store. Its 119 legacy current/published procurement rows remain historical lineage because their accepted migration status explicitly left current state unverified. Any future reuse must be re-collected/reverified through normal ARGUS evidence and reconciliation controls before it can update current canonical state.

The DTIF source workbooks remain retained read-only evidence; destructive deletion is not implied by archive-only disposition.

### Current-state records

`current-index.json` is the current-record overlay index.

When an `argus_id` appears in `current-index.json`, the referenced JSON record under `data/registry/current/` supersedes the same `argus_id` in `records.jsonl` **for current-state reads only**.

This preserves both:

- immutable historical baseline provenance; and
- a clean current canonical representation with explicit record revisions.

Canonical read order:

```text
records.jsonl initial baseline
        ↓
current-index.json
        ↓
referenced data/registry/current/<ARGUS_ID>.json
        ↓
current canonical state
```

Each current record must preserve the same stable `argus_id`, increment `revision`, retain evidence/provenance and remain compatible with the active Registry schema.

Optional future type-specific partitions such as `entities.jsonl`, `projects.jsonl`, `procurements.jsonl`, `intelligence.jsonl`, `opportunities.jsonl`, `supplier-products.jsonl` and `knowledge.jsonl` may be introduced when scale justifies partitioning, but they must not create competing canonical states.

Do not store raw tender/source documents here.

Every record should retain stable `argus_id`, revision, timestamps, evidence references, relationships and provenance sufficient to migrate losslessly to a future operational database.
