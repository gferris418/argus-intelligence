# Bangladesh Procurement v2 — Registry Envelope / Materialization Architecture

**Document ID:** ARGUS-BD-PROC-V2-ENVELOPE-001  
**Version:** 1.0.0-candidate  
**Date:** 2026-10-18  
**Status:** DESIGN_CANDIDATE  
**Base commit:** `ee1b73d4defe5e23cc6ca4871dc12399540d080a`  
**Production write authority:** Bangladesh procurement v1.3 remains active throughout this design/engineering gate.

## 1. Objective

Define one authoritative physical composition model between the generic ARGUS Master Registry envelope and the Bangladesh Procurement v2 domain model so that PROCUREMENT records can adopt v2 semantics without:

- creating heterogeneous canonical root shapes;
- duplicating record identity, title, revision/state, relationships or evidence semantics;
- embedding a complete standalone v2 record inside legacy `attributes`;
- rewriting the immutable baseline;
- breaking current-index resolution or legacy reads.

This document resolves the blocker identified by the historical migration rehearsal. It does **not** activate v2.

## 2. Current contracts

### 2.1 Master Registry v0.2.1

Current canonical records use a generic registry envelope with fields including:

- `schema_version`
- `argus_id`
- `record_type`
- `canonical_name_or_title`
- `status`
- `aliases`
- `related_argus_ids`
- `relationships`
- `evidence_refs`
- `external_refs`
- `information_classification`
- `revision`
- `created_at`
- `updated_at`
- `attributes`
- optional classification/standards references.

### 2.2 Bangladesh Procurement v2 standalone candidate

The standalone v2 candidate currently includes both record-level and procurement-domain concepts:

- record-level: `argus_id`, `title`, `record_state`, `record_revision`, `related_record_refs`, `observations`;
- procurement-domain: requirement link, typed identifiers, party roles, budget/financing, process, lots/items, notices, milestones/events, requirements, fees/securities, contacts, awards/contracts, implementation and ARGUS procurement intelligence.

The standalone shape is useful for semantic validation and interchange, but writing it directly beside generic registry-envelope records would create two physical record families.

## 3. Architectural decision

Adopt a **composed registry envelope**.

Create a backward-compatible candidate Master Registry schema `v0.3.0` in which the generic registry envelope remains the physical root for all seven record types. A v0.3.0 PROCUREMENT record carries Bangladesh v2 procurement semantics in a typed `domain_payload`, while overlapping record-level concepts remain owned by the generic envelope.

Do **not**:

1. write direct Bangladesh-v2 root objects into `data/registry/current/`;
2. place the full standalone v2 object under legacy `attributes`;
3. keep two authoritative copies of identity/title/revision/relationships/evidence.

## 4. Candidate physical shape

```json
{
  "schema_version": "0.3.0",
  "argus_id": "PROC-...",
  "record_type": "PROCUREMENT",
  "canonical_name_or_title": "...",
  "status": "...",
  "aliases": [],
  "related_argus_ids": [],
  "relationships": [],
  "evidence_refs": [],
  "external_refs": [],
  "information_classification": "internal",
  "revision": 1,
  "created_at": "...",
  "updated_at": "...",
  "observations": [],
  "domain_payload": {
    "profile": "BANGLADESH_PROCUREMENT",
    "version": "2.0.0-candidate",
    "data": {
      "requirement_ref": "...",
      "identifiers": [],
      "party_role_links": [],
      "budget": {},
      "financing_entries": [],
      "process": {},
      "lots": [],
      "items": [],
      "notices": [],
      "milestones": [],
      "events": [],
      "requirements": [],
      "fees": [],
      "securities": [],
      "contacts": [],
      "awards": [],
      "contracts": [],
      "implementation": {},
      "intelligence": {}
    }
  }
}
```

For a v0.3.0 PROCUREMENT record, legacy `attributes` is not an authoritative procurement store. It should be absent or empty under the candidate schema. Legacy v0.2.x records continue to require/use `attributes` exactly as before.

## 5. Authority matrix — one concept, one home

| Concept | Authoritative home in composed record | Standalone-v2 field removed from persisted domain payload | Notes |
|---|---|---|---|
| Permanent record identity | envelope `argus_id` | `argus_id` | Exact equality is an adapter precondition |
| Canonical title | envelope `canonical_name_or_title` | `title` | Domain item/lot titles remain domain data |
| Record revision | envelope `revision` | `record_revision` | Procurement lifecycle status remains in `process` |
| Generic record status | envelope `status` | `record_state` | Must not substitute for `process.status_*` |
| Cross-record graph | envelope `relationships` | `related_record_refs` | `related_argus_ids` is a derived compatibility index/cache, not a second semantic home |
| Source-level evidence | envelope `evidence_refs` | none | Evidence refs identify sources/supporting claims |
| Field-level provenance | envelope `observations` | `observations` | Observation paths may point into `domain_payload.data` |
| Aliases | envelope `aliases` | none | Search/retrieval aliases only |
| External locators/legacy refs | envelope `external_refs` | none | Non-authoritative lookup/lineage references; typed procurement identity lives in domain `identifiers` |
| Information classification | envelope `information_classification` | none | Generic governance metadata |
| Generic taxonomy | envelope `domain_classification_refs` | none | ATLAS-governed external taxonomy/classification |
| Standards references | envelope `standard_refs` | none | Generic standards metadata |
| Typed procurement identifiers | `domain_payload.data.identifiers` | retained | Tender ID, PE reference, APP ID, package, lot etc. remain semantically typed |
| Party roles | `domain_payload.data.party_role_links` | retained | A party role is not the same as generic graph relation |
| Procurement lifecycle/commercial data | `domain_payload.data.*` | retained | Process, lots, items, notices, milestones, events, fees, securities, awards/contracts etc. |
| Procurement intelligence | `domain_payload.data.intelligence` | retained | ARGUS opportunity/procurement assessment |

## 6. `related_argus_ids` compatibility rule

For v0.3.0 records, `relationships[]` is the authoritative typed graph.

`related_argus_ids[]` remains only because current resolvers and compatibility tests depend on it. It becomes a **derived compatibility cache** and must satisfy:

```text
set(related_argus_ids) == set(relationship.target_argus_id for relationship in relationships)
                         union explicitly approved untyped context links
```

A later registry major version may remove the cache after consumers migrate. Until then, discrepancies are validation failures.

## 7. `external_refs` versus typed `identifiers`

These are not co-authoritative.

- `domain_payload.data.identifiers[]` is the canonical semantic home for procurement identifiers and explicitly records scheme + scope.
- envelope `external_refs[]` is a retrieval/lineage/locator index. It must not be used to decide whether a value is a Tender ID, Tender Reference, APP ID, Package No., Project Code, Contract No., etc.
- During materialization, duplicate external references may remain temporarily for backward-compatible lookup, but they are explicitly **non-authoritative mirrors**. A future cleanup may remove mirrors after resolver compatibility is proven.
- If a conflict exists, typed domain `identifiers[]` wins and the conflict must be represented in evidence/observation state rather than silently reconciled.

This preserves one semantic authority while allowing reversible compatibility.

## 8. Evidence and observation model

Evidence and observations are complementary, not duplicates:

- `evidence_refs[]`: source-level evidence objects attached to the canonical registry record;
- `observations[]`: field-level assertions preserving raw label/value, source, time, claim type and condition.

For v0.3.0, observations move to the generic envelope because field-level provenance is useful across record types. Bangladesh v2 observations are therefore removed from the persisted `domain_payload.data` during materialization.

No observation may upgrade evidence state. `STALE`, `CONFLICT`, `INFERENCE`, `ASSUMPTION` and `UNKNOWN` semantics remain explicit.

## 9. Candidate schemas

The engineering gate should create:

1. `registry/schema/argus-master-registry-v0.3.0-candidate.json`
   - accepts legacy `0.2.0` / `0.2.1` records without rewrite;
   - accepts `0.3.0` records;
   - for `0.3.0 + PROCUREMENT`, requires typed `domain_payload` and permits generic `observations`;
   - preserves all seven record types;
   - does not make v0.3.0 production authority.

2. `schemas/bangladesh-procurement-v2-domain.schema.json`
   - defines only persisted procurement-domain fields;
   - reuses canonical definitions from the existing standalone v2 schema where practical;
   - excludes `argus_id`, `title`, `record_state`, `record_revision`, `related_record_refs`, and `observations`.

The existing standalone `schemas/bangladesh-procurement-v2.schema.json` remains useful as the semantic/interchange candidate and is not replaced by the domain projection.

## 10. Materialization adapter

Create a pure adapter:

```python
materialize_registry_procurement(current_record: dict, standalone_v2: dict) -> dict
```

Preconditions:

- both inputs have the same `argus_id`;
- standalone `title` equals the registry canonical title, or the mismatch is explicitly rejected/reconciled before materialization;
- standalone `record_revision` equals registry `revision` unless a governed revision bump is supplied;
- input record is `PROCUREMENT`;
- standalone payload validates against the v2 standalone schema.

Behavior:

- copy generic envelope identity/governance metadata from the current registry record;
- set candidate `schema_version = 0.3.0` only in disposable materialization output;
- remove overlapping standalone fields before storing `domain_payload.data`;
- lift standalone observations into envelope `observations`;
- preserve envelope relationships/evidence/external refs/classification metadata;
- set legacy `attributes` absent/empty according to candidate schema;
- never consult unrelated current records to invent missing fields;
- never write files or mutate either input object.

## 11. Read compatibility

A resolver/reader contract must support both shapes during transition:

### Legacy read

`schema_version in {0.2.0, 0.2.1}` → existing `attributes` semantics remain unchanged.

### Candidate composed read

`schema_version == 0.3.0 and record_type == PROCUREMENT` → procurement semantics come from `domain_payload.data`; generic identity/evidence come from the envelope.

### Compatibility projection

If an old consumer still expects selected legacy procurement attributes, a read adapter may project a **derived in-memory compatibility view** from v2 domain data. That projection must never be persisted as a second canonical copy.

`current-index.json` continues to resolve ARGUS IDs to record files; no index schema change is required merely because the record envelope version changes.

## 12. Validation population

The gate must validate the composition against all six current PROCUREMENT records:

- `PROC-BCG-LT001`
- `PROC-DAE-1318662`
- `PROC-DAE-CHAR28-R2`
- `PROC-DGDP-248-07-075-26`
- `PROC-DGDP-248-07-076-26`
- `PROC-DGDP-248-07-078-26`

and against the immutable historical baseline rehearsal for `PROC-BCG-LT001`.

No current canonical file is rewritten during this gate.

## 13. Disposable activation/revert rehearsal

The gate must simulate, entirely in fixtures/in-memory staging:

1. snapshot hashes/counts/ID sets of current canonical procurement files;
2. materialize all six current records into composed v0.3.0 candidates;
3. validate each candidate against the composed registry/domain schemas;
4. build a disposable candidate index using the same ARGUS IDs;
5. verify all relationship targets resolve against the existing registry population;
6. verify source/output ID sets and counts match;
7. verify no material v2 domain data disappears;
8. simulate rollback by restoring the snapshotted source bytes/objects;
9. verify rollback hashes/counts/IDs exactly match the snapshot.

This is a rehearsal only. No canonical path, manifest pointer or index is changed.

## 14. Activation gates for a later PR

A later live activation PR remains blocked until all of these are true:

- composed schema is green across all current and historical test fixtures;
- standalone-v2 → composed-envelope adapter is deterministic and lossless for authoritative concepts;
- legacy read compatibility is tested;
- relationship/index resolution is tested;
- activation/revert rehearsal restores exact pre-activation hashes;
- full repository Contract Tests are green;
- migration receipt captures before/after hashes, byte counts, IDs and schema versions;
- a separate governed decision explicitly approves production activation.

## 15. Non-goals

This gate does not:

- switch Bangladesh production writes from v1.3 to v2;
- rewrite `data/registry/current/*.json`;
- modify `data/registry/current-index.json`;
- modify the immutable `data/registry/records.jsonl` baseline;
- activate Master Registry v0.3.0;
- migrate ENTITY/PROJECT/OPPORTUNITY/etc. to new domain payloads;
- introduce an operational database.

## 16. Decision

**Recommended design:** composed Master Registry envelope + typed domain payload.

**GO for engineering validation after spec approval.**

**NO-GO for production activation.**
