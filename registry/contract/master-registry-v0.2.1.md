# ARGUS Master Registry Data Contract v0.2.1 — Evidence Evolution

**Status:** Candidate  
**Effective date:** 2026-10-18  
**Supersedes:** v0.2.0 only where evidence semantics are concerned  
**Record model:** unchanged — seven canonical record types

## Purpose

v0.2.1 is a deliberately narrow, backward-compatible evolution of the Registry v0.2.0 contract. It aligns persisted evidence with ARGUS 2.0.0-rc.2 by separating **what kind of analytical claim is being made** from **the current condition of that claim**.

No record type, identity rule, relationship rule, reconciliation rule, PX rule, or canonical-ownership rule changes.

## Evidence semantics

### New form

New evidence references should use:

- `claim_type`: `FACT | DERIVED | INFERENCE | ASSUMPTION | UNKNOWN`
- `claim_condition`: `CURRENT | STALE | CONFLICT`

Example:

```json
{
  "source_system": "BPPA",
  "source_id": "example-id",
  "claim_type": "FACT",
  "claim_condition": "CURRENT"
}
```

### Legacy form

Existing v0.2.0 evidence remains valid using:

- `analytical_label`: `FACT | DERIVED | INFERENCE | ASSUMPTION | UNKNOWN | CONFLICT | STALE`

Legacy values are historical source-state records and MUST NOT be silently rewritten.

### Dual form during migration

A controlled migration or adapter may temporarily return both the legacy and new fields. Where both exist, the explicit v0.2.1 fields govern current analytical semantics; `analytical_label` remains historical/backward-compatibility metadata.

## Validation rule

An evidence reference must contain:

1. `source_system`;
2. at least one of `source_id` or `source_locator`; and
3. either:
   - legacy `analytical_label`, or
   - both `claim_type` and `claim_condition`.

`claim_type` and `claim_condition` are a pair; partial split semantics are invalid.

## Schema-version compatibility

The v0.2.1 candidate schema accepts records declaring `schema_version` `0.2.0` or `0.2.1` so the current single-schema Registry API validator can read legacy and new records during transition.

New canonical writes after deployment of the v0.2.1 API patch should declare `schema_version: 0.2.1`.

## Physical PostgreSQL migration

`registry/migrations/0.2.0-to-0.2.1-evidence.sql`:

- adds nullable `claim_type` and `claim_condition` to `argus.record_evidence`;
- relaxes `analytical_label` from NOT NULL;
- preserves the legacy analytical-label check;
- requires either legacy semantics or a complete new type/condition pair;
- performs no data rewrite, delete, truncate, or table replacement.

Relationship-level evidence is already retained as JSONB and therefore requires no physical-column migration; JSON Schema/API validation governs its shape.

## Registry API patch surface

Registry API v0.1.1 is schema-driven. A compatible API source update should:

1. replace/generated-load the v0.2.1 schema;
2. change `ArgusRecord.schema_version` from literal `0.2.0` to `0.2.0 | 0.2.1`;
3. change `EvidenceRef` so `analytical_label` is optional and add optional `claim_type`/`claim_condition` fields;
4. preserve mapper spread/round-trip behavior;
5. add validator tests for legacy, new, dual, and invalid half-pair evidence;
6. add mapper/repository round-trip tests proving both new fields survive persistence;
7. retain all existing authorization, reconciliation, idempotency, revision, audit and PX controls.

## Deployment boundary

This repository change defines and tests the candidate contract only. It does not apply SQL to the canonical Supabase Registry or the controlled Neon pilot and does not authorize production cutover.
