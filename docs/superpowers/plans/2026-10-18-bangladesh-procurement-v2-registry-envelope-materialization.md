# Bangladesh Procurement v2 Registry Envelope / Materialization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement and prove a backward-compatible Master Registry envelope composition for Bangladesh Procurement v2 without changing production write authority.

**Architecture:** Keep the generic Master Registry as the physical root and add a candidate v0.3.0 PROCUREMENT composition with a typed Bangladesh procurement `domain_payload`. Record identity, title, revision/state, graph relationships, generic evidence and field-level observations remain envelope-owned; procurement semantics remain domain-owned. Validate only in fixtures/in-memory rehearsal and preserve v1.3 production authority.

**Tech Stack:** Python 3.12 stdlib, `jsonschema==4.23.0`, JSON Schema Draft 2020-12, JSON, unittest, GitHub Actions.

**Spec:** `docs/architecture/bangladesh-procurement-v2-registry-envelope-materialization.md`

## Global Constraints

- Bangladesh procurement v1.3 remains the active production/write standard throughout this gate.
- Do not modify `data/registry/records.jsonl`, `data/registry/current-index.json`, `data/registry/current/*.json`, or the manifest write-authority pointer.
- Master Registry envelope is the only persisted root shape.
- `domain_payload.data` must not duplicate `argus_id`, canonical title, record revision/state, cross-record relationships, or observations.
- Typed domain `identifiers[]` are authoritative for procurement identifier semantics; envelope `external_refs[]` are compatibility/lookup mirrors only.
- `relationships[]` is authoritative graph state; `related_argus_ids[]` is a validated compatibility cache.
- Adapters must be deterministic, pure, and write no files.
- Raw source/tender documents remain prohibited in GitHub.

## Review Focus

- Envelope/domain duplication must be rejected by schema/tests.
- Legacy v0.2.x records must continue to validate/read without rewrite.
- A title/revision/ARGUS-ID mismatch between current registry record and standalone-v2 candidate must fail materialization.
- Field-level observations must be lifted to the envelope without evidence-state upgrades.
- Activation/revert rehearsal must restore exact source hashes, counts and ID sets.

---

### Task 1: Write the RED composition contract

**Files:**
- Create: `tests/test_bangladesh_procurement_v2_registry_envelope.py`
- Create: `tests/test_bangladesh_procurement_v2_materialization_rehearsal.py`

**Interfaces:**
- Consumes: approved architecture spec, Master Registry v0.2.1 schema, standalone v2 schema, six current v2 fixtures, historical baseline rehearsal.
- Produces: executable acceptance contract for schemas, adapter, compatibility reader and rehearsal.

- [ ] Write failing tests requiring candidate registry v0.3.0 schema, procurement-domain projection schema, pure materializer/read adapter, no overlapping domain fields, six-current-record coverage, historical fixture coverage and exact rollback reconciliation.
- [ ] Run full contract suite; verify failures are limited to missing new artifacts/behavior.

### Task 2: Define candidate composed schemas

**Files:**
- Create: `registry/schema/argus-master-registry-v0.3.0-candidate.json`
- Create: `schemas/bangladesh-procurement-v2-domain.schema.json`

**Interfaces:**
- Consumes: v0.2.1 envelope schema and standalone v2 schema semantics.
- Produces: backward-compatible registry candidate plus persisted domain-only procurement schema.

- [ ] Implement candidate schema accepting v0.2.0/v0.2.1 unchanged and v0.3.0 PROCUREMENT with `domain_payload` + envelope `observations`.
- [ ] Exclude `argus_id`, `title`, `record_state`, `record_revision`, `related_record_refs`, and `observations` from domain schema.
- [ ] Verify schema tests GREEN and legacy fixture compatibility remains GREEN.

### Task 3: Implement pure materializer and compatibility reader

**Files:**
- Create: `tools/bangladesh_procurement_v2_materialize.py`
- Modify: `tests/test_bangladesh_procurement_v2_registry_envelope.py`

**Interfaces:**
- Produces:
  - `materialize_registry_procurement(current_record: dict, standalone_v2: dict) -> dict`
  - `read_procurement_semantics(record: dict) -> dict`
  - `project_legacy_procurement_view(record: dict) -> dict`

- [ ] RED tests for identity/title/revision mismatch rejection, purity/determinism, observation lifting, overlap removal, relationship cache validation and legacy-v0.2 read support.
- [ ] Implement minimal adapter/reader behavior.
- [ ] Run targeted then full contract suite to GREEN.

### Task 4: Rehearse all current + historical records

**Files:**
- Create: `tests/fixtures/bangladesh-v2/registry-envelope-materialization-rehearsal.json`
- Modify: `tests/test_bangladesh_procurement_v2_materialization_rehearsal.py`

**Interfaces:**
- Consumes: six current registry PROCUREMENT records + mapped standalone-v2 fixtures + historical baseline rehearsal.
- Produces: disposable materialized candidates, hashes/counts/IDs, validation results and rollback proof.

- [ ] Require 6/6 current IDs, schema-valid composed candidates, relationship targets resolvable in current index, source/output ID equality, zero authoritative-domain loss, and exact source rollback hashes.
- [ ] Include historical baseline fixture as compatibility/provenance proof without consulting current overlay to upgrade it.
- [ ] Run full contract suite to GREEN.

### Task 5: Write validation decision and integrate

**Files:**
- Create: `docs/validation/bangladesh-procurement-v2-registry-envelope-materialization.md`

**Interfaces:**
- Consumes: executable rehearsal evidence.
- Produces: GO/NO-GO decision for a later activation branch.

- [ ] Document authority matrix, backward-read behavior, rehearsal counts, exact activation/revert findings and unresolved risks.
- [ ] Require explicit `v1.3 remains active`, `NO-GO for live activation in this gate`, and later activation prerequisites.
- [ ] Compare base→head and prove no production registry/index/manifest/baseline mutation.
- [ ] Run/observe full GitHub Contract Tests on exact final head.
- [ ] Open/update PR with RED→GREEN and scope evidence; merge only after green CI using expected head SHA.
- [ ] Verify `main` CI after merge and persist the final validation report to `/ARGUS` with byte-for-byte readback.
