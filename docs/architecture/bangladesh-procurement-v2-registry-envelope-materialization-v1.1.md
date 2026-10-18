# Bangladesh Procurement v2 — Registry Envelope / Materialization Architecture v1.1

**Document ID:** ARGUS-BD-PROC-V2-ENVELOPE-001  
**Version:** 1.1.0-candidate  
**Date:** 2026-10-18  
**Status:** DESIGN_CANDIDATE  
**Production write authority:** Bangladesh procurement v1.3 remains active.

## Correction basis

This version supersedes the v1.0 candidate architecture after the hallucination/drift audit found that legacy envelope `status` was being treated as if it were the standalone-v2 `record_state`. Existing v0.2.x PROCUREMENT records use `status` for procurement/process-oriented state, while v2 explicitly defines `record_state` as the state of the ARGUS data record. They are different concepts.

ATLAS OS is unchanged. This is an ARGUS-only correction.

## Authoritative composition

The generic ARGUS Master Registry remains the physical root. Candidate v0.3.0 is restricted to `PROCUREMENT` until other record types receive their own governed migration design.

```text
Master Registry envelope v0.3 PROCUREMENT
├── argus_id
├── record_type = PROCUREMENT
├── canonical_name_or_title
├── record_state                  [ARGUS record lifecycle]
├── revision
├── aliases
├── relationships                 [authoritative typed graph]
├── related_argus_ids             [exact derived cache of relationship targets]
├── evidence_refs
├── external_refs                 [lookup/lineage mirror only]
├── observations                  [field-level provenance]
└── domain_payload
    ├── profile = BANGLADESH_PROCUREMENT
    ├── version = 2.0.0-candidate
    └── data
        ├── identifiers
        ├── party_role_links
        ├── budget / financing
        ├── process               [procurement status lives here]
        ├── lots / items
        ├── notices / milestones / events
        ├── requirements
        ├── fees / securities / contacts
        ├── awards / contracts / implementation
        └── intelligence
```

## Record state versus procurement status

For legacy v0.2.x records:

- envelope `status` remains readable for backward compatibility;
- it is treated as a legacy overloaded field and is **not** reinterpreted as v2 `record_state`.

For candidate v0.3.0 PROCUREMENT:

- envelope `record_state` is required;
- envelope `status` is prohibited;
- procurement status belongs only in `domain_payload.data.process.status_raw` and/or `process.status_normalized`;
- the legacy envelope status string is retained only as non-authoritative migration provenance in `observations`.

This restores the rule: **one real-world concept → one authoritative home**.

## Domain schema binding

The persisted domain projection is deeply typed. `schemas/bangladesh-procurement-v2-domain.schema.json` reuses the standalone v2 `$defs` for identifiers, parties, process, lots, items, notices, milestones, events, requirements, fees, securities, contacts, awards, contracts, implementation and intelligence.

`registry/schema/argus-master-registry-v0.3.0-candidate.json` binds `domain_payload.data` to that domain schema. Validators must register the standalone, domain and registry schema resources together so the cross-schema references are resolved locally and deterministically.

A malformed nested procurement object must therefore fail both domain validation and composed-registry validation.

## Relationship/cache invariant

`relationships[]` is the sole authoritative typed graph.

For candidate v0.3 PROCUREMENT:

```text
set(related_argus_ids) == set(relation.target_argus_id for relation in relationships)
```

No implicit/untyped extras are allowed in the compatibility cache. Context that is not a graph relationship belongs in the appropriate domain structure, for example `party_role_links`, or must receive an explicit typed relationship before entering the cache.

## Materialization invariants

The pure materializer must:

1. validate the standalone v2 input;
2. require exact ARGUS ID, title and revision agreement;
3. copy v2 `record_state` to the v0.3 envelope;
4. preserve existing typed envelope relationships and lift typed v2 related-record relationships;
5. derive `related_argus_ids` exactly from the composed relationships;
6. preserve generic aliases, evidence refs, external refs, classification metadata and timestamps;
7. lift standalone observations to the envelope;
8. preserve the legacy overloaded `status` only as migration provenance, not as an authoritative v0.3 field;
9. remove envelope-owned fields from the persisted domain payload;
10. validate the domain payload and final composed record;
11. never write canonical files or mutate its inputs.

## Executable semantic-loss proof

`material_information_loss` may not be a declared constant.

The repair contract computes loss by comparing:

- standalone-v2 identity, record state/revision, domain structures, observations and typed related-record links against the composed record;
- legacy generic envelope aliases/evidence/external refs/classification/timestamps and typed graph against the composed record;
- legacy `related_argus_ids` against a representation in either the typed graph, v2 related-record links or party-role links;
- legacy overloaded status against preserved migration provenance.

The rehearsal passes only when the computed finding set is empty.

## Disposable activation/revert proof

Source immutability and rollback are different claims.

The corrected rehearsal must physically:

1. copy current source bytes into a temporary disposable workspace;
2. snapshot hashes and byte counts;
3. overwrite those temporary copies with candidate composed records;
4. verify bytes changed during the disposable activation;
5. restore the original snapshot bytes;
6. verify exact SHA-256 and byte-count restoration.

Canonical `data/registry/current/*`, `current-index.json`, the immutable baseline and the manifest remain untouched.

## Legacy compatibility

Candidate schema v0.3.0 continues to validate legacy v0.2.0/v0.2.1 records with their existing `status + attributes` representation.

The read adapter:

- returns legacy `status` explicitly as `legacy_status` and does not fabricate a v2 `record_state`;
- returns v0.3 `record_state` independently from domain procurement-process status;
- may produce an in-memory legacy compatibility view from v2 domain data, but that view is never persisted.

## Non-PROCUREMENT v0.3 records

Candidate v0.3.0 is **not** a general seven-record-type migration. A `schema_version = 0.3.0` record is valid only when `record_type = PROCUREMENT` under this candidate. ENTITY, PROJECT, INTELLIGENCE, OPPORTUNITY, SUPPLIER_PRODUCT and KNOWLEDGE remain on their existing registry contract until separately designed.

## Production boundary

This repair does not:

- activate Bangladesh Procurement v2;
- change the manifest authority pointer;
- rewrite any current canonical record;
- change the current index;
- rewrite the immutable baseline;
- change ATLAS OS;
- activate Master Registry v0.3.0.

**v1.3 remains active.**

## Decision

The prior v1.0 architecture conclusion is superseded. This v1.1 candidate may proceed through corrective TDD and disposable rehearsal. Live activation remains **NO-GO** until a later governed activation decision.
