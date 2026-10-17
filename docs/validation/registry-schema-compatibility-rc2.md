# ARGUS 2.0.0-rc.2 — Registry Schema Compatibility Validation

**Status:** PASS WITH ONE ADDITIVE SCHEMA EVOLUTION REQUIRED  
**Date:** 2026-10-18  
**ARGUS:** 2.0.0-rc.2  
**Registry contract:** ARGUS-REG-001 v0.2.0  
**Registry schema:** ARGUS-SCHEMA-REG-001 v0.2.0  
**Registry API implementation baseline:** v0.1.1

## Decision

ARGUS rc.2 does **not** require a Master Registry redesign.

The Bangladesh route model and 360-degree intelligence collection model are compatible with the existing seven-record Registry contract because type-specific `attributes` are intentionally extensible. The only incompatible seam is the rc.2 evidence-semantic split between claim type and claim condition.

## Exact schema validation

The canonical Registry v0.2.0 JSON Schema snapshot has SHA-256:

`2dad9c73dc0236395fe0418f6694ee53b478ccc51c86996d8bc00abff5f2f808`

Representative `INTELLIGENCE` records were validated against the full schema for:

- `BD-GEN-EGP`
- `BD-DEV-GOB`
- `BD-DEV-DP`
- `BD-DEF-DGDP`
- `BD-PPP`

Each record included rc.2 fields for route classification, route confidence, project/funding/procurement-planning state, twelve-lens collection coverage, collection gaps, and source convergence. All five records validated without a Registry schema change.

Result: **PASS — additive attributes are compatible.**

## Evidence-semantic probe

Registry v0.2.0 evidence references use a closed object and require `analytical_label`. The legacy enum combines:

`FACT`, `DERIVED`, `INFERENCE`, `ASSUMPTION`, `UNKNOWN`, `CONFLICT`, `STALE`.

ARGUS rc.2 separates:

- claim type: `FACT`, `DERIVED`, `INFERENCE`, `ASSUMPTION`, `UNKNOWN`
- claim condition: `CURRENT`, `STALE`, `CONFLICT`

A representative evidence reference with `claim_condition: CURRENT` fails Registry v0.2.0 because the evidence object sets `additionalProperties: false`. A legacy `analytical_label: CONFLICT` continues to validate.

Result: **PATCH REQUIRED.**

## Compatibility classification

| Area | Result | Change class |
|---|---|---|
| Seven Registry record types | PASS | No change |
| Bangladesh route classification | PASS | Additive attribute |
| Project/funding/procurement-planning state | PASS | Additive attribute |
| 360-degree collection coverage | PASS | Additive attribute |
| Collection gaps | PASS | Additive attribute |
| Source convergence metadata | PASS | Additive attribute |
| I0-I9 maturity | PASS | Existing field |
| Decision vocabulary | PASS | Existing vocabulary |
| Evidence claim type vs condition | FAIL on v0.2.0 | Backward-compatible schema evolution required |

## Required Registry evolution

Create `ARGUS-SCHEMA-REG-001 v0.2.1` as a backward-compatible evolution.

Recommended rule:

1. preserve existing `analytical_label` support for v0.2.0 records during migration;
2. add explicit `claim_type` with values `FACT`, `DERIVED`, `INFERENCE`, `ASSUMPTION`, `UNKNOWN`;
3. add explicit `claim_condition` with values `CURRENT`, `STALE`, `CONFLICT`;
4. new rc.2 writes should use `claim_type` + `claim_condition`;
5. legacy reads remain valid and can be normalized without changing evidence provenance;
6. do not rewrite historical `CONFLICT` or `STALE` observations silently;
7. migration must be lossless and auditable.

## Registry API impact

The Registry API validator is schema-driven and imports a generated schema object. Therefore no Registry service redesign is indicated. The expected patch surface is:

- canonical Registry JSON Schema;
- generated schema source;
- record-validator tests;
- domain type if evidence fields are statically typed;
- mapper/round-trip tests to prove no evidence loss;
- API acceptance fixtures.

Existing reconciliation, authorization, idempotency, revision, audit and transaction behavior should remain unchanged.

## Operational baseline

The prior operational manifest records:

- canonical Registry: PostgreSQL 17 on Supabase;
- controlled Neon PostgreSQL 18 pilot;
- Registry API v0.1.1 local hardening: 50/50 tests PASS and build PASS;
- live service runtime acceptance still pending;
- production cutover not authorized.

This compatibility review does not authorize a database cutover or mutate the canonical Supabase Registry.

## Release-gate result

For ARGUS 2.0.0-rc.2:

- **Registry route/profile compatibility:** PASS
- **360-degree collection compatibility:** PASS
- **Evidence split compatibility:** BLOCKED pending Registry Schema v0.2.1 / API patch

Canonical promotion should remain blocked until the evidence patch is implemented and its migration/round-trip tests pass.
