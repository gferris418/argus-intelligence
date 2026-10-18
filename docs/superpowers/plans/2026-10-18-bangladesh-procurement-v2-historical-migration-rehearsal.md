# Bangladesh Procurement v2 Historical Migration Rehearsal Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove that every historical/baseline `PROCUREMENT` record in the immutable GitHub baseline can be deterministically transformed into the Bangladesh procurement v2 candidate without mutating production state, while defining a reversible activation/rollback procedure for a later governed migration.

**Architecture:** Keep `data/registry/records.jsonl` immutable and treat it as provenance input. Add a machine-readable legacy-registry migration contract plus a pure Python transformer that emits v2 candidate payloads only; it must never update live registry files. Rehearse the transformer against the entire baseline PROCUREMENT population, validate outputs against `schemas/bangladesh-procurement-v2.schema.json`, reconcile identity/evidence/material values, and document an activation transaction and rollback plan without executing it.

**Tech Stack:** Python 3.12 stdlib, `jsonschema==4.23.0`, JSON/JSONL, unittest, GitHub Actions.

**Spec:** `profiles/bangladesh-canonical-procurement-standard-v2.0.yaml`; `schemas/bangladesh-procurement-v2.schema.json`; `profiles/bangladesh-procurement-v1-to-v2-migration.yaml`.

## Global Constraints

- `profiles/bangladesh-canonical-procurement-standard-v1.3.yaml` remains the active Bangladesh write authority throughout this gate.
- Do not modify `data/registry/records.jsonl`, `data/registry/current-index.json`, `data/registry/current/*.json`, or the manifest write-authority pointer.
- Historical baseline identity and evidence state must not be upgraded by inference.
- Ambiguous legacy identifiers must be preserved in provenance observations rather than typed into v2 identifiers without semantic resolution.
- The migration transformer must be deterministic, pure with respect to its input object, and write no files.
- Rehearsal output is disposable validation data, not canonical state.
- Raw source/tender documents remain prohibited in GitHub.

## Review Focus

- Legacy fields named like identifiers but semantically wrong or ambiguous must not become typed v2 identifiers.
- A stale/legacy evidence label must never be upgraded to a current fact.
- Standalone currency without an amount/scope must not become process currency by guess.
- Legacy procurement type strings must not be coerced into GOODS/WORKS when source semantics are unclear.
- Rollback design must restore the previous manifest/index/current-record state exactly and preserve the immutable baseline.

---

### Task 1: Pin the historical population and migration acceptance contract

**Files:**
- Create: `tests/test_bangladesh_procurement_v2_historical_migration.py`
- Create: `profiles/bangladesh-procurement-v2-registry-legacy-migration.json`

**Interfaces:**
- Consumes: `data/registry/records.jsonl`, `data/registry/baseline.json`, v2 JSON Schema.
- Produces: exact source-field rules and acceptance tests used by the transformer.

- [ ] Write failing tests asserting the immutable baseline has exactly one `PROCUREMENT` record, `PROC-BCG-LT001`, and that every top-level/attribute field used by that record is accounted for by the migration contract.
- [ ] Add tests that ambiguous `official_reference`/`package_reference` values cannot be emitted as typed v2 identifiers, stale evidence remains stale, and no current overlay is consulted.
- [ ] Run the full contract suite and verify the new tests fail because the migration contract/transformer artifacts do not yet exist.
- [ ] Add the minimal machine-readable migration contract covering safe mappings, preserve-only fields and prohibited inferences.

### Task 2: Implement the pure legacy-registry transformer

**Files:**
- Create: `tools/bangladesh_procurement_v2_migrate.py`
- Modify: `tests/test_bangladesh_procurement_v2_historical_migration.py`

**Interfaces:**
- Consumes: one registry `PROCUREMENT` record plus the machine migration contract.
- Produces: `transform_legacy_procurement(record: dict) -> dict` v2 candidate payload with no side effects.

- [ ] Extend tests to import and execute the transformer, require schema validity, deterministic repeated output, input immutability, identity/revision preservation, party-role mapping, related-record preservation, quantity-to-item mapping, material-unknown preservation and provenance observations.
- [ ] Run tests and verify RED on missing transformer behavior.
- [ ] Implement only evidence-safe mappings. Preserve ambiguous/legacy-only semantics as observations; do not infer category, competition scope, normalized method, package/tender identity, notice, event, award or contract state.
- [ ] Run targeted and full contract tests to GREEN.

### Task 3: Rehearse the full historical population and reconcile

**Files:**
- Create: `tests/fixtures/bangladesh-v2/historical-baseline-rehearsal.json`
- Modify: `tests/test_bangladesh_procurement_v2_historical_migration.py`

**Interfaces:**
- Consumes: all baseline PROCUREMENT records via the pure transformer.
- Produces: one deterministic rehearsal artifact with source/output counts, IDs, baseline SHA-256 and transformed payloads.

- [ ] Write failing tests requiring source count = output count = 1, identical ARGUS ID set, baseline SHA-256 `a43cb9555f3c82a827d16508d4e3af9764f4445e99df44853895eb2d505bbc31`, schema-valid payloads, zero live mutations and zero material-loss findings.
- [ ] Create the rehearsal artifact from the transformer output and explicit preservation assessment.
- [ ] Run targeted and full tests to GREEN.

### Task 4: Define reversible activation and rollback controls

**Files:**
- Create: `docs/validation/bangladesh-procurement-v2-historical-migration-rehearsal.md`
- Modify: `tests/test_bangladesh_procurement_v2_historical_migration.py`

**Interfaces:**
- Consumes: rehearsal results and current overlay/write-contract architecture.
- Produces: activation transaction sequence, rollback procedure, readback checks and GO/NO-GO decision.

- [ ] Write failing tests requiring the report to document pre-migration snapshot hashes/counts, staged transformation, validation gates, atomic activation boundary, rollback order, post-activation readback, and explicit `v1.3 remains active` / `NO-GO for live activation` wording.
- [ ] Write the report with exact baseline population and findings, distinguishing historical baseline rehearsal from current overlay dry-runs.
- [ ] Run the full suite to GREEN.

### Task 5: Final scope verification and integration

**Files:** no new production-state files.

**Interfaces:**
- Consumes: branch diff and CI.
- Produces: merge-ready PR evidence and durable Library report.

- [ ] Compare base→head and verify there are no changes to immutable baseline, current registry, current index or manifest write authority.
- [ ] Run/observe the full GitHub Contract Tests workflow and require success.
- [ ] Open/update PR with RED→GREEN evidence and explicit GO/NO-GO result.
- [ ] Merge only with a head-SHA guard after green CI.
- [ ] Verify post-merge CI on `main`.
- [ ] Persist the final validation report to `/ARGUS`, materialize/read back, and verify exact bytes before reporting `SAVED`.
