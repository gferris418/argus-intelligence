# ARGUS Bangladesh Procurement v2 Drift Repair Plan

## Objective
Correct the semantic and verification defects identified by the post-merge hallucination/drift audit without changing ATLAS OS or activating Bangladesh Procurement v2.

## Root causes
1. The composed v0.3 candidate removed standalone `record_state` but reused legacy envelope `status`, although existing envelope `status` carries procurement-process semantics.
2. `material_information_loss` and `rollback_exact` were receipt constants rather than independently computed behavioral proofs.
3. The persisted domain projection schema was shallow and depended on the materializer to have run standalone validation first.
4. The registry schema did not directly bind `domain_payload.data` to the persisted domain schema.
5. The `related_argus_ids` cache invariant was tested only as a subset relation.
6. v0.3 non-PROCUREMENT records were insufficiently constrained even though their migration is out of scope.

## Repair design
- v0.3 PROCUREMENT envelope owns `record_state`; legacy envelope `status` is prohibited on v0.3 PROCUREMENT and remains only for v0.2.x compatibility.
- Procurement process state remains only under `domain_payload.data.process.status_raw/status_normalized`.
- Materializer maps standalone `record_state` to envelope `record_state`; it does not carry legacy `status` into the v0.3 candidate.
- Reader returns `record_state` separately from process semantics.
- Domain projection schema becomes a strict projection of the standalone v2 schema using `$ref` to standalone `$defs` and explicit allowed root fields.
- Registry v0.3 PROCUREMENT `domain_payload.data` uses `$ref` to the domain projection schema.
- Schema v0.3 is restricted to PROCUREMENT until other record-type migrations are explicitly designed.
- `related_argus_ids` must exactly equal relationship targets unless an explicit future compatibility mechanism is designed; no untyped extras in this candidate.
- Add executable round-trip semantic preservation comparison between standalone v2 and materialized/read-back semantics.
- Replace declarative `material_information_loss: 0` with computed loss findings/count.
- Add an actual disposable activation/revert rehearsal in a temporary workspace: write staged candidates, overwrite disposable copies, restore snapshotted bytes, and verify exact hashes/bytes after revert. Never touch canonical paths.
- Validation report must distinguish source immutability from tested disposable rollback.

## TDD gates
1. RED: v0.3 candidate must require `record_state`, reject `status`, reject non-PROCUREMENT v0.3, and enforce deep invalid nested domain rejection.
2. RED: materializer must preserve v2 `record_state` and reject/avoid legacy status carryover.
3. RED: relationship cache exact equality.
4. RED: executable semantic-loss checker must detect an intentionally dropped field.
5. RED: disposable activate/revert test must physically mutate only a temporary copy and restore exact bytes.
6. GREEN: implement schemas/materializer/audit helpers.
7. Run full Contract Tests on PR head.
8. Scope review must show no `data/registry/current*`, baseline, manifest, or ATLAS changes.
9. Merge only on green exact head; rerun `main`; persist corrected validation record to Library.

## Production boundary
Bangladesh Procurement v1.3 remains active. Master Registry production authority remains unchanged. No live canonical migration occurs in this repair.
