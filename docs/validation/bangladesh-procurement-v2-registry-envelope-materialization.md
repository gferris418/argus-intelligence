# Bangladesh Procurement v2 — Registry Envelope / Materialization Validation

**Document ID:** ARGUS-BD-PROC-V2-ENVELOPE-VAL-001  
**Date:** 2026-10-18  
**Architecture:** `docs/architecture/bangladesh-procurement-v2-registry-envelope-materialization.md`  
**Candidate registry schema:** `registry/schema/argus-master-registry-v0.3.0-candidate.json`  
**Domain projection schema:** `schemas/bangladesh-procurement-v2-domain.schema.json`  
**Materializer:** `tools/bangladesh_procurement_v2_materialize.py`  
**Production write authority:** **v1.3 remains active**  
**Live registry mutation:** false

## Decision

**GO for a later activation PR design/rehearsal.** The registry-envelope/materialization blocker is resolved at the candidate architecture level: Bangladesh Procurement v2 can be materialized into one generic ARGUS Master Registry root without duplicating authoritative identity, title, revision/state, graph, or observation concepts.

**NO-GO for live activation in this gate.** This branch does not switch production writes, rewrite current canonical records, modify the current index, modify the immutable baseline, or change the manifest authority pointer.

A **later activation PR** must be separately governed and must carry a pre-activation snapshot/receipt, candidate-record rewrite in the approved composed shape, compatibility controls, exact post-merge readback, and rollback proof.

## Validated physical model

The approved candidate is a **composed Master Registry envelope**:

```text
Master Registry envelope
├── argus_id
├── record_type
├── canonical_name_or_title
├── status
├── revision
├── aliases
├── relationships
├── related_argus_ids   [derived compatibility cache]
├── evidence_refs
├── external_refs       [non-authoritative lookup/lineage mirror]
├── observations        [field-level provenance]
└── domain_payload
    ├── profile = BANGLADESH_PROCUREMENT
    ├── version = 2.0.0-candidate
    └── data
        ├── typed identifiers
        ├── party roles
        ├── budget / financing
        ├── process
        ├── lots / items
        ├── notices / milestones / events
        ├── requirements
        ├── fees / securities / contacts
        ├── awards / contracts / implementation
        └── procurement intelligence
```

The persisted domain payload excludes the envelope-owned standalone fields:

- `argus_id`
- `title`
- `record_state`
- `record_revision`
- `related_record_refs`
- `observations`

This implements the rule **one real-world concept → one authoritative home**.

## Schema behavior

### Legacy compatibility

Candidate Master Registry v0.3.0 accepts legacy `0.2.0` / `0.2.1` records without rewrite and keeps their existing `attributes` representation.

### Candidate composed PROCUREMENT

For `schema_version = 0.3.0` and `record_type = PROCUREMENT`:

- `domain_payload` is required;
- envelope `observations` is required;
- legacy `attributes` is prohibited;
- generic envelope fields remain the root identity/governance contract.

The standalone Bangladesh v2 schema remains the strict semantic validation precondition. The domain projection schema is intentionally a persisted projection boundary: materialization first validates the full standalone candidate, then removes envelope-owned fields and validates the projected domain shape.

## Relationship authority

`relationships[]` is the authoritative persisted graph.

The materializer:

1. preserves all existing envelope relationships;
2. lifts any additional typed `related_record_refs` from the validated standalone v2 candidate into the envelope relationship list;
3. ensures every relationship target is represented in `related_argus_ids[]`.

Thus removing `related_record_refs` from the domain payload does not cause semantic loss.

`related_argus_ids[]` remains a compatibility cache only; it is not a second semantic graph authority.

## Identifier authority

- `domain_payload.data.identifiers[]` is the canonical semantic home for procurement identifiers such as system Tender ID, PE reference, APP ID, package number, lot identity, award/contract references and financing references.
- envelope `external_refs[]` remains a lookup/lineage mirror for backward compatibility.
- conflicts must be represented through evidence/observation semantics; `external_refs[]` does not override typed domain identity.

## Evidence / provenance authority

- `evidence_refs[]` remains generic source-level evidence at the envelope.
- `observations[]` is envelope-owned field-level provenance.
- standalone-v2 observations are lifted into the envelope during materialization.
- no evidence state is upgraded by the adapter.

## Dual-read compatibility

The pure reader supports both shapes:

- v0.2.x PROCUREMENT → existing `attributes` semantics;
- v0.3.0 composed PROCUREMENT → `domain_payload.data` procurement semantics plus envelope observations.

A separate `project_legacy_procurement_view()` produces only a derived, in-memory compatibility view. It is never persisted as a duplicate canonical copy.

## 6/6 current PROCUREMENT records

The disposable rehearsal covers all **6/6 current PROCUREMENT records**:

1. `PROC-BCG-LT001`
2. `PROC-DAE-1318662`
3. `PROC-DAE-CHAR28-R2`
4. `PROC-DGDP-248-07-075-26`
5. `PROC-DGDP-248-07-076-26`
6. `PROC-DGDP-248-07-078-26`

Results:

- source count: **6**
- candidate output count: **6**
- source/output ARGUS ID sets: **identical**
- standalone-v2 validation: **PASS**
- composed registry validation: **PASS**
- domain projection validation: **PASS**
- relationship target resolution against current index: **PASS**
- material information loss: **0**
- live registry mutation: **false**

The deterministic receipt is committed at:

`tests/fixtures/bangladesh-v2/registry-envelope-materialization-rehearsal.json`

Each materialized candidate is represented by a canonical JSON SHA-256 in the receipt rather than by a second bulky canonical copy.

## Historical baseline separation

The immutable historical baseline remains separate provenance input:

- baseline SHA-256: `a43cb9555f3c82a827d16508d4e3af9764f4445e99df44853895eb2d505bbc31`
- historical PROCUREMENT count: **1**
- historical ID: `PROC-BCG-LT001`
- current-overlay backfill into historical migration: **prohibited**

The materialization gate does not rewrite or enrich historical provenance using later current-state facts.

## Activation / rollback rehearsal

The rehearsal snapshots every current PROCUREMENT source file using byte count + SHA-256 before materialization. Materialization is pure and writes no canonical files.

The candidate ID set remains identical to the source ID set. Relationship targets are resolved against the unchanged current index. Because all source files remain byte-identical during and after the disposable candidate build, **rollback exact** is proven for this rehearsal: returning from candidate materialization to pre-gate canonical state requires no mutation because production state was never changed.

A live activation must repeat this principle at PR scale:

1. capture pre-activation manifest/index/current-record hashes and counts;
2. materialize candidate records in staging;
3. validate schemas, IDs, relationships, values and evidence semantics;
4. merge one atomic activation PR;
5. read back `main` by merge SHA and recompute approved hashes/counts;
6. if any gate fails, revert the activation merge and verify exact restoration.

## Test history

TDD RED was observed first: the full repository suite ran with the new contracts and failed only because candidate schemas, materializer, rehearsal receipt and report were absent.

After candidate schemas and the pure adapter were implemented, schema/materialization/dual-read tests passed and only the expected rehearsal/report gaps remained.

The final gate requires the entire repository Contract Tests suite to be green on the exact PR head before merge and again on the merge commit.

## Production safety

This gate intentionally does **not** change:

- `data/registry/records.jsonl`
- `data/registry/current-index.json`
- any `data/registry/current/*.json`
- the Bangladesh procurement v1.3 active-standard pointer
- Master Registry production authority
- the operational database deferral

**v1.3 remains active.**

## GO / NO-GO

### GO

Proceed, in a separate governed step, to design the **later activation PR** and its pre/post migration receipt using the composed Master Registry envelope proven here.

### NO-GO

**NO-GO for live activation in this gate.** Do not yet switch the production manifest, rewrite canonical current PROCUREMENT records, or publish Master Registry v0.3.0 as active authority without the separate activation approval and exact migration receipt.
