# Bangladesh Procurement v2 — Historical/Baseline Migration Rehearsal

**Document ID:** ARGUS-BD-PROC-V2-HIST-MIG-VAL-001  
**Date:** 2026-10-18  
**Candidate standard:** `profiles/bangladesh-canonical-procurement-standard-v2.0.yaml`  
**Machine write contract:** `schemas/bangladesh-procurement-v2.schema.json`  
**Legacy-registry migration contract:** `profiles/bangladesh-procurement-v2-registry-legacy-migration.json`  
**Transformer:** `tools/bangladesh_procurement_v2_migrate.py`  
**Active production/write standard:** v1.3  
**Live registry mutation:** false

## Decision

**GO to envelope-design gate.** The historical baseline rehearsal is successful and demonstrates that the entire immutable baseline PROCUREMENT population can be transformed deterministically into the v2 candidate without material information loss or unsafe semantic upgrading.

**NO-GO for live activation.** A new architecture decision is required before v2 may become the active production write authority:

> **Registry envelope/materialization contract: BLOCKER**

The Bangladesh v2 schema currently defines a normalized PROCUREMENT payload. Existing canonical `data/registry/current/*.json` records use the generic ARGUS Master Registry envelope (`schema_version`, `argus_id`, `record_type`, `canonical_name_or_title`, relationships, evidence metadata, attributes, etc.). Those are related but not identical physical shapes. **Do not mix direct v2 payloads with registry-envelope records** in one canonical store without an explicit composition/materialization contract.

**Next gate: registry envelope/materialization contract.** That gate must decide how the seven-record-type Master Registry envelope composes with the Bangladesh procurement v2 domain payload while preserving one authoritative home per concept, backwards-compatible reads, evidence semantics and current-index resolution.

**v1.3 remains active.**

## Rehearsal population

The immutable GitHub baseline contains 11 canonical records across the seven ARGUS record types. Exactly one is a historical `PROCUREMENT` record.

**Historical baseline PROCUREMENT records: 1/1**

| Baseline record | Result | Notes |
|---|---|---|
| `PROC-BCG-LT001` | PASS | Deterministic v2 transform; identity preserved; stale legacy evidence preserved; ambiguous `WD-2` references not retyped |

Baseline file:

`data/registry/records.jsonl`

Baseline SHA-256:

`a43cb9555f3c82a827d16508d4e3af9764f4445e99df44853895eb2d505bbc31`

The existing baseline hash contract remains authoritative. **data/registry/records.jsonl remains immutable** and was not modified during this rehearsal.

## Rehearsal result

- Source PROCUREMENT count: **1**
- Output PROCUREMENT count: **1**
- Source ID set: `PROC-BCG-LT001`
- Output ID set: `PROC-BCG-LT001`
- Schema validation: **PASS**
- Determinism: **PASS**
- Input immutability: **PASS**
- Evidence-state preservation: **PASS**
- Unsafe identifier retyping: **0**
- **Material information loss: 0**
- Live registry mutation: **false**

The committed rehearsal artifact is:

`tests/fixtures/bangladesh-v2/historical-baseline-rehearsal.json`

A contract test regenerates the v2 payload from the immutable baseline and requires the committed rehearsal payload to equal the transformer output exactly. The fixture is therefore not an independently hand-maintained interpretation of the source record.

## Deterministic migration behavior

### Identity and lineage

The transformer preserves:

- `argus_id` → `argus_id`;
- legacy `revision` → `record_revision`;
- canonical title → v2 `title`;
- existing relationship targets and relation types → `related_record_refs`;
- explicit `project_id` only as a linked PROJECT reference when not already represented by an existing relationship.

The rehearsal assigns `record_state: BASELINE_PROVENANCE`. This describes the migration payload's data-record role; it is not a claim about current procurement status.

### Party roles

The baseline explicitly identifies one Coast Guard entity as both buyer and procuring entity. The transformer therefore emits two party-role links to the same canonical ENTITY:

- `BUYER`
- `PROCURING_ENTITY`

It does not infer Ministry, end-user, project office or other roles from later/current evidence.

### Quantity

The legacy quantity object `4 vessels` remains attached to the procurement scope and is represented as one generic v2 item. No lot structure is fabricated.

### Method and process state

The legacy code `OSTETM` is preserved only as:

`process.method_source_code = OSTETM`

The rehearsal does **not** infer normalized `OPEN`, competition scope, or procedure configuration from that code alone.

The legacy workflow/process text `Published_snapshot_unverified_current` is preserved only as `process.status_raw`. It is not normalized into current truth.

### Ambiguous identifiers

Both legacy fields below contain `WD-2`:

- `attributes.official_reference`
- `attributes.package_reference`

Current reconciliation has already demonstrated that `WD-2` is a lot identification, not the official tender reference or package number. Historical migration therefore does not emit `WD-2` in `identifiers[]` at all. Both source values remain available as provenance observations.

This is the intended behavior for ambiguous legacy references generally: **preserve first, type only after semantic resolution**.

### Currency and procurement type

Legacy `currency = BDT` is not mapped to `process.currency` because no procurement estimate/value accompanies it in the baseline record. The currency is preserved as a provenance observation.

Legacy `procurement_type = goods_and_shipbuilding_procurement` is not coerced into v2 `GOODS` or `WORKS`. The string is retained in provenance because the legacy label does not supply the normalized semantic boundary required by v2.

### Funding wording

`Development Budget GOB` is retained as source wording in provenance. The historical transformer does not create a normalized budget or financing entry from this string alone.

### Evidence-state preservation

The baseline contains two evidence entries marked `STALE`. The transformer emits them as observations with:

- `claim_type = UNKNOWN`
- `condition = STALE`
- `assurance = LEGACY_ANALYTICAL_LABEL_STALE`

This intentionally avoids converting the old overloaded `analytical_label` into a stronger v2 claim. Staleness is preserved as staleness; no current FACT is fabricated.

## Machine migration contract

`profiles/bangladesh-procurement-v2-registry-legacy-migration.json` accounts for every top-level field and every `attributes.*` field present on the baseline PROCUREMENT record.

Supported actions are:

- `KEEP`
- `MAP`
- `PRESERVE_ONLY`
- `DROP_REDUNDANT`

The contract expressly prohibits:

- generic legacy reference → typed identifier without semantic resolution;
- standalone currency → process currency;
- descriptive legacy procurement type → normalized category;
- stale evidence → current fact;
- current-overlay backfill into a historical-baseline rehearsal;
- legacy method code → normalized method without an explicit mapping;
- legacy record/process status → current procurement truth.

## Separation from the current-overlay dry run

This gate is deliberately independent from the earlier current-state v2 write-contract dry run.

The earlier gate validated six current `PROC-*` overlays plus a World Bank planning fixture. This gate starts only from the immutable baseline `records.jsonl` and prohibits reading `current-index.json` or `data/registry/current/*` to improve the historical record.

That separation matters because a migration rehearsal must prove what the historical record itself can safely become. Later evidence may supersede or enrich it in the current layer, but it must not retroactively alter provenance.

# Reversible activation design

The following procedure is a **design for a later governed activation**. It was not executed in this gate.

## 1. Pre-activation snapshot

Immediately before any future activation branch is created, capture a signed/checksummed migration receipt containing at minimum:

- exact `main` commit SHA;
- SHA-256 and byte count of `argus-intelligence.yaml`;
- SHA-256 and byte count of `data/registry/current-index.json`;
- ordered list of all current PROCUREMENT IDs;
- path, SHA-256 and byte count for every current PROCUREMENT file;
- baseline ID, baseline record count, baseline PROCUREMENT count and baseline SHA-256;
- active Bangladesh standard version and active registry-envelope schema version;
- full Contract Tests result at that exact pre-activation commit.

The baseline SHA must still equal:

`a43cb9555f3c82a827d16508d4e3af9764f4445e99df44853895eb2d505bbc31`

Any mismatch is an immediate activation stop.

## 2. Staging namespace

**Staging namespace:** use a disposable, non-canonical workspace keyed by a migration ID, for example:

`/tmp/argus-migration/bd-proc-v2/<migration-id>/`

or the equivalent isolated CI/worktree artifact directory.

Do not stage candidate records under `data/registry/current/`, do not update `current-index.json`, and do not change the manifest while generating or validating candidate materialization.

The staging receipt must record:

- transformer version/commit;
- migration-contract version;
- source file hashes;
- output file hashes;
- source/output record counts and ID sets;
- schema validation result;
- semantic-preservation findings;
- unresolved migration exceptions.

## 3. Registry envelope/materialization contract: BLOCKER

Before staged v2 payloads can become canonical records, ARGUS must define one physical composition model.

### Option A — recommended direction: composed registry envelope

Keep the generic Master Registry envelope as the cross-domain physical contract and define a new compatible registry schema version that composes a domain-specific Bangladesh procurement payload without duplicating identity/evidence concepts.

This likely requires schema composition rather than simply nesting the current full v2 object unchanged, because the current v2 payload itself already contains `argus_id`, title, record state and revision concepts that overlap with the generic envelope.

The next design gate must establish exactly which layer owns:

- permanent record identity;
- record revision/state;
- canonical title;
- cross-record relationships;
- generic evidence/provenance;
- domain procurement semantics;
- ARGUS intelligence fields.

The contract must preserve the rule: **one concept, one authoritative home**.

### Option B — direct v2 root only for PROCUREMENT: reject for now

Writing v2 PROCUREMENT objects directly at the root while ENTITY/PROJECT/OPPORTUNITY/etc. continue to use the generic registry envelope would make the physical store heterogeneous and would break assumptions in the current resolver/tests unless a new polymorphic registry contract were explicitly introduced.

Do not adopt this implicitly.

### Option C — duplicate full v2 object inside existing `attributes`: reject for now

Embedding the complete v2 object under `attributes` while retaining duplicate `argus_id`, title, state/revision and evidence concepts in the outer envelope creates two authoritative homes and violates the canonical deduplication principle.

Do not adopt this implicitly.

**Next gate: registry envelope/materialization contract.**

## 4. Candidate activation branch

Only after the envelope/materialization blocker is resolved should a future activation branch be created from the exact snapshotted `main` SHA.

That branch should contain, in one governed change set:

1. the approved registry-envelope/schema change if required;
2. transformed current PROCUREMENT records in the approved physical shape;
3. any strictly necessary current-index changes;
4. compatibility readers/adapters;
5. migration receipt with before/after hashes and counts;
6. activation tests;
7. manifest pointer switch from v1.3 to the approved v2 production version.

The immutable baseline is not rewritten.

## 5. Validation gates before merge

The activation PR must remain blocked unless all of the following pass:

- all transformed records validate against the approved composed schema;
- source and output current PROCUREMENT ID sets are identical unless a separately approved identity migration exists;
- record counts reconcile;
- relationship targets resolve;
- typed identifiers remain semantically distinct;
- no evidence condition/claim is upgraded without evidence;
- award/contract/lifecycle events reconcile;
- no current record disappears;
- no material value disappears;
- compatibility reads of v1.3-era records remain defined;
- full repository Contract Tests are green;
- a reverse transformation/revert test demonstrates rollback viability.

## 6. Atomic activation boundary

**Atomic activation boundary:** the merge of the single governed activation PR into `main`.

The merge must use an expected-head SHA guard and must be based on the snapshotted base commit (or a newly revalidated snapshot if `main` changed). Do not apply a sequence of manual production edits before/after the merge.

If `main` changes materially after the pre-activation snapshot, regenerate the snapshot, rerun staging, and revalidate before merge.

## 7. Post-activation readback

**Post-activation readback:** immediately after the activation merge, read the merged artifacts back from `main` by the merge commit SHA and recompute:

- manifest hash and active standard pointer;
- current-index hash and ID/path mapping;
- each current PROCUREMENT file hash;
- record counts and ID sets;
- relationship-target resolution;
- schema validation;
- material-field reconciliation;
- full Contract Tests on the merge commit.

Activation is not considered complete until these readbacks match the approved migration receipt.

## 8. Rollback order

**Rollback order:**

1. Freeze further procurement-schema writes/merges.
2. Create a normal Git **revert** of the activation merge/commit; do not rewrite shared Git history.
3. Verify the manifest again points to v1.3 and the previous registry-envelope schema.
4. Verify `current-index.json` SHA-256 and ID/path mappings match the Pre-activation snapshot.
5. Verify every previous current PROCUREMENT file SHA-256 and byte count match the Pre-activation snapshot.
6. Verify baseline SHA remains unchanged.
7. Run the full Contract Tests suite on the reverted `main` state.
8. Record rollback cause, failed gate and resulting hashes in a migration incident receipt before resuming migration work.

A rollback is successful only when the entire pre-activation state is reproduced by hash/ID/count and tests, not merely when the manifest version string changes back.

# GO / NO-GO

## GO

Proceed with the next design/engineering gate:

**GO to envelope-design gate**

That gate should produce:

- an explicit generic-registry ↔ Bangladesh-v2 materialization model;
- a schema-composition decision;
- compatibility/read-resolution rules;
- migration adapter tests for all six current PROCUREMENT overlays plus the historical baseline fixture;
- a disposable end-to-end activation/revert rehearsal.

## NO-GO

**NO-GO for live activation** at this stage.

Do not yet:

- change the manifest from v1.3 to v2;
- rewrite `data/registry/current/*.json` into direct v2 payloads;
- change `current-index.json` for this transition;
- rewrite `data/registry/records.jsonl`;
- mix direct v2 payloads and generic registry-envelope records without an approved polymorphic/composed schema;
- duplicate the full v2 payload inside legacy `attributes` while leaving duplicate authoritative identity/evidence fields outside it;
- use current evidence to retroactively upgrade stale historical baseline facts.

**v1.3 remains active.**
