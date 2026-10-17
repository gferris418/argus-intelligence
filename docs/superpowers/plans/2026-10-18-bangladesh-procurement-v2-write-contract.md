# Bangladesh Procurement v2 Write Contract Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert the semantically validated Bangladesh Procurement v2 candidate into a machine-validating write-contract candidate and prove it can represent every current PROCUREMENT record without mutating production data.

**Architecture:** Keep v1.3 as the active write standard. Fold the representative-validation milestone additions into the v2 candidate, define a strict Draft 2020-12 JSON Schema for the v2 PROCUREMENT payload, validate the existing representative fixtures, add fixture-only transformations for the remaining current PROCUREMENT records, and prove current-index coverage. The schema validates only the `v2_candidate` payload; fixture wrappers remain test/provenance envelopes.

**Tech Stack:** YAML/JSON specifications, JSON Schema Draft 2020-12, Python 3.12 `unittest`, `jsonschema` 4.x in test CI, GitHub Actions.

**Spec:** `profiles/bangladesh-canonical-procurement-standard-v2.0.yaml` and `docs/validation/bangladesh-procurement-v2-representative-fixtures.md`

## Global Constraints

- `profiles/bangladesh-canonical-procurement-standard-v1.3.yaml` remains the active Bangladesh production/write standard.
- Do not rewrite `data/registry/current/*.json` or `data/registry/current-index.json`.
- Do not alter ATLAS ownership or ARGUS record-type boundaries.
- Do not commit raw tender/source documents.
- Sparse evidence is valid: unknown/unobserved values must not be fabricated merely to satisfy schema completeness.
- Canonical v2 payloads must reject unknown field names so schema drift is visible.
- Project/institution/supplier context remains linked rather than duplicated.
- Planned publication is a milestone; actual publication is a notice/event.
- Retender/reissue must not be promoted from inference to fact.

## Review Focus

1. Sparse DGDP records must validate without invented project, security, competition-scope, or technical fields.
2. DAE successor inference must preserve uncertainty and predecessor lineage without asserting an official re-tender event.
3. World Bank planning dates must validate as planned milestones without fabricating a notice.
4. Strict `additionalProperties: false` boundaries must reject duplicate/legacy field creep while allowing evidence values to retain arbitrary JSON values.
5. Every current PROCUREMENT in `current-index.json` must have a non-mutating v2 dry-run fixture; no non-PROCUREMENT record should be required.

---

### Task 1: Fold representative-validation discoveries into the v2 candidate

**Files:**
- Modify: `profiles/bangladesh-canonical-procurement-standard-v2.0.yaml`
- Delete after fold: `profiles/bangladesh-canonical-procurement-standard-v2.0-validation-addendum.yaml`
- Test: `tests/test_bangladesh_procurement_v2_write_contract.py`

**Interfaces:**
- Consumes: v2 candidate milestone vocabulary and validation addendum.
- Produces: one self-contained v2 candidate with `PROCUREMENT_DOCUMENT_READY` and `EXPECTED_PUBLICATION` plus a pointer to the machine schema.

- [ ] Write failing tests requiring both milestone types in the main v2 candidate and requiring no surviving validation-addendum authority.
- [ ] Run the full contract test command and confirm RED for missing folded state/schema artifacts.
- [ ] Fold the two milestone definitions/rules into the v2 candidate and remove the temporary addendum.
- [ ] Re-run focused tests.

### Task 2: Define the machine-validating v2 PROCUREMENT JSON Schema

**Files:**
- Create: `schemas/bangladesh-procurement-v2.schema.json`
- Create: `requirements-test.txt`
- Modify: `.github/workflows/contract-tests.yml`
- Test: `tests/test_bangladesh_procurement_v2_write_contract.py`

**Interfaces:**
- Consumes: structured types and vocabularies from the v2 candidate.
- Produces: Draft 2020-12 schema validating a `v2_candidate` PROCUREMENT payload.

- [ ] Add failing tests for schema presence, Draft 2020-12 identity, strict top-level/nested properties, sparse minimum required fields, typed identifiers/roles, lifecycle objects, monetary values, observation provenance, and rejection of legacy fields such as `extension_count`.
- [ ] Add `jsonschema` as a pinned test dependency and install it in CI.
- [ ] Implement the schema with only `argus_id`, `title`, `record_state`, and `record_revision` required globally; other semantic structures remain optional/sparse.
- [ ] Validate the four representative fixtures with `Draft202012Validator`.
- [ ] Add negative tests proving unknown top-level fields, invalid party roles, invalid process categories, and `extension_count` are rejected.

### Task 3: Dry-run every current PROCUREMENT record

**Files:**
- Create: `tests/fixtures/bangladesh-v2/dae-low-lift-pump-successor.json`
- Create: `tests/fixtures/bangladesh-v2/dgdp-inflatable-boat.json`
- Create: `tests/fixtures/bangladesh-v2/dgdp-scuba.json`
- Create: `tests/fixtures/bangladesh-v2/current-procurement-fixture-map.json`
- Modify as required for strict schema compliance: existing four representative fixtures
- Test: `tests/test_bangladesh_procurement_v2_write_contract.py`

**Interfaces:**
- Consumes: current registry records and v2 schema.
- Produces: non-mutating dry-run fixture coverage for every current `PROC-*` record.

- [ ] Add failing coverage test that reads `current-index.json`, extracts every `PROC-*` record, and requires an exact fixture-map entry for each.
- [ ] Add/normalize the three missing current-record fixtures and map the three existing current-record fixtures.
- [ ] Preserve DAE successor uncertainty through relationship/evidence/intelligence fields without asserting an official re-tender event.
- [ ] Preserve DGDP sparse unknowns and foreign-currency basis as observations rather than inferred competition scope.
- [ ] Run schema validation across all current-record dry-run fixtures plus the World Bank planning fixture.

### Task 4: Record migration-gate result

**Files:**
- Create: `docs/validation/bangladesh-procurement-v2-write-contract-dry-run.md`
- Test: `tests/test_bangladesh_procurement_v2_write_contract.py`

**Interfaces:**
- Consumes: schema validation and current-index coverage results.
- Produces: evidence-backed GO/NO-GO recommendation for the next migration stage.

- [ ] Add failing report-contract assertions for current procurement count, zero live mutations, schema-validation result, information-loss result, remaining migration blockers, and activation decision.
- [ ] Write the report from verified test evidence.
- [ ] Run the complete repository contract suite.
- [ ] Review the full branch diff for any live-registry or manifest-authority mutation before PR/merge.
