# Canonical ARGUS Registry Data

This directory is the interim physical canonical store for structured ARGUS records while GitHub is the active persistence layer.

## Preferred representation

Use JSON/JSONL conforming to the active ARGUS Registry schema.

Recommended files:

- `records.jsonl` — canonical records, one JSON object per line;
- optional type-specific partitions such as `entities.jsonl`, `projects.jsonl`, `procurements.jsonl`, `intelligence.jsonl`, `opportunities.jsonl`, `supplier-products.jsonl`, `knowledge.jsonl` when scale justifies partitioning;
- `index.json` — optional generated lookup/index metadata, never a competing source of truth.

Do not store raw tender/source documents here.

Every record should retain stable `argus_id`, revision, timestamps, evidence references, relationships, and provenance sufficient to migrate losslessly to a future operational database.
