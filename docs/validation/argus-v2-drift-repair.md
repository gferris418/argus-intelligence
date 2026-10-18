# ARGUS v2 Drift Repair Validation

**Document ID:** ARGUS-BD-PROC-V2-DRIFT-REPAIR-001  
**Date:** 2026-10-18  
**Status:** CORRECTIVE_VALIDATION_PENDING_FINAL_CI  
**Scope:** ARGUS only  
**ATLAS unchanged:** yes  
**Production authority:** Bangladesh Procurement v1.3 remains active

## Purpose

This record supersedes the validation conclusion in `docs/validation/bangladesh-procurement-v2-registry-envelope-materialization.md` after a read-only hallucination/drift audit identified semantic and verification defects in the candidate v0.3 composition.

## Defects corrected

1. `record_state` is now distinct from procurement-process status. Candidate v0.3 PROCUREMENT uses envelope `record_state`; legacy envelope `status` is prohibited in v0.3 and retained only as migration provenance.
2. `material_information_loss` is no longer a declared constant. The rehearsal computes material information loss from standalone-v2 semantics plus legacy generic-envelope preservation checks.
3. Rollback proof is upgraded from source non-mutation to a real **disposable activation/revert** cycle in a temporary workspace: temporary source copies are overwritten with candidate bytes, then restored and verified by SHA-256 and byte count.
4. The persisted domain schema is deeply typed using the standalone-v2 semantic definitions.
5. Registry v0.3 binds `domain_payload.data` to that deep domain schema.
6. `related_argus_ids` must exactly match the target set of `relationships[]` for candidate v0.3.
7. Candidate v0.3 is restricted to PROCUREMENT; unsupported v0.3 non-PROCUREMENT records fail validation.

## Record-state ownership

The corrected authority model is:

```text
envelope.record_state
    = state of the ARGUS registry record

domain_payload.data.process.status_raw
    = exact/raw procurement-process status when available

domain_payload.data.process.status_normalized
    = normalized procurement-process status

legacy v0.2.x envelope.status
    = overloaded compatibility field; not reinterpreted as record_state
```

The legacy v0.2.x status string is copied only into an envelope observation with `field_path = legacy_registry.status` so migration provenance is not lost.

## Computed material information loss

The corrective rehearsal computes material information loss. It checks:

- ARGUS ID, canonical title, record state and record revision;
- all persisted v2 domain fields;
- standalone observations;
- typed v2 related-record relationships;
- aliases, evidence refs, external refs, timestamps and classification metadata from the current generic envelope;
- preservation of current typed relationships;
- representation of legacy context IDs in relationships, v2 related-record links or party-role links;
- preservation of the legacy overloaded status as migration provenance.

The rehearsal must return an empty findings set before the repair can be considered green.

## Disposable activation/revert

The corrected rehearsal performs a physical but isolated activate/revert cycle:

1. source bytes are copied to a temporary directory;
2. pre-activation SHA-256 and byte counts are captured;
3. temporary copies are overwritten with candidate composed records;
4. the test requires at least one byte-level change during activation;
5. original source bytes are restored;
6. post-rollback SHA-256 and byte counts must exactly equal the pre-activation snapshot.

No canonical GitHub registry file is written by this test. This proves disposable rollback behavior rather than merely proving that production was never mutated.

## Schema correction

The domain projection schema now reuses standalone-v2 `$defs` for all nested procurement structures. The Registry v0.3 candidate references the domain schema directly. Validation therefore rejects malformed nested identifiers/process/lots/items/notices/milestones/events/requirements/commercial/award/contract/implementation/intelligence structures even if a caller bypasses the Python materializer.

Schema resolution is local through a registered JSON-Schema resource registry; no network lookup is required.

## Relationship invariant

For candidate v0.3:

```text
set(related_argus_ids) == set(relationship.target_argus_id for relationship in relationships)
```

Unrelated/untyped IDs are not permitted in the compatibility cache.

## Production boundary

This repair does not change:

- `argus-intelligence.yaml` production authority;
- `data/registry/current-index.json`;
- any `data/registry/current/*.json` canonical record;
- immutable `data/registry/records.jsonl`;
- ATLAS OS.

**v1.3 remains active.**

## Decision

**NO-GO for live activation** until the corrective PR is fully green, merged, re-read from `main`, and a later activation gate is separately approved.

Final PR-head and post-merge CI receipts are added only after fresh verification.
