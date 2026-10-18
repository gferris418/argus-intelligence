# Bangladesh Procurement v2 — Machine Write Contract Dry Run

**Document ID:** ARGUS-BD-PROC-V2-WRITE-VAL-001  
**Date:** 2026-10-18  
**Candidate standard:** `profiles/bangladesh-canonical-procurement-standard-v2.0.yaml`  
**Machine contract:** `schemas/bangladesh-procurement-v2.schema.json`  
**Active production/write standard:** v1.3  
**Live registry mutation: false**

## Decision

**GO / NO-GO:** **GO** to the next governed migration-design gate: prepare a reversible migration plan and broaden migration rehearsal to historical/baseline procurement records. **NO-GO for live migration** or changing the active Bangladesh write authority from v1.3 at this stage.

The v2 candidate now has a Draft 2020-12 JSON Schema write contract. The contract is intentionally strict about field names and controlled vocabularies while remaining sparse: only `argus_id`, `title`, `record_state`, and `record_revision` are globally required. Missing evidence is therefore not fabricated to satisfy schema completeness.

**Current PROCUREMENT records covered: 6/6**  
**Schema validation: PASS**  
**Material information loss: 0** across the six current-record dry-run transformations based on source/current-record preservation review.  
**Live registry mutation: false**

## Current-record coverage

The dry-run fixture map is `tests/fixtures/bangladesh-v2/current-procurement-fixture-map.json` and covers every current `PROC-*` entry in `data/registry/current-index.json`:

| Current ARGUS ID | Dry-run fixture | Primary semantic stress |
|---|---|---|
| `PROC-BCG-LT001` | `bcg-cpv.json` | typed institutional roles, lot identity, fee/security, two deadline extensions |
| `PROC-DAE-1318662` | `dae-low-lift-pump.json` | e-GP IDs, OTM vs NCT, validity/security dates, linked project |
| `PROC-DAE-CHAR28-R2` | `dae-low-lift-pump-successor.json` | probable successor/reissue without falsely asserting a factual re-tender event |
| `PROC-DGDP-248-07-075-26` | `dgdp-inflatable-boat.json` | sparse defence tender, DGDP enlistment, foreign-currency evidence |
| `PROC-DGDP-248-07-076-26` | `dgdp-rhib.json` | sparse defence tender, procurement-unit label, technical unknowns |
| `PROC-DGDP-248-07-078-26` | `dgdp-scuba.json` | separate DGDP procurement cycle, quantity/unit, technical unknowns |

The existing World Bank SITA `PMIPSD/G-01` representative planning fixture is also schema-valid and remains outside the current-registry count because it is a development-partner validation fixture rather than a current Master Registry PROCUREMENT record.

## Write-contract behavior validated

### 1. Strict semantic boundaries

The schema uses `additionalProperties: false` at the PROCUREMENT root and at structured semantic objects. This makes accidental field drift visible rather than silently accepting new portal-specific or duplicate fields.

Negative contract tests reject, among other examples:

- top-level `extension_count` as duplicate derived state;
- legacy `solicitation` payloads;
- repeated `ministry_name` strings;
- invalid party role `MINISTRY_NAME`;
- invalid procurement category `EQUIPMENT`.

### 2. Sparse records remain legal

A minimum v2 procurement with only:

- `argus_id`
- `title`
- `record_state`
- `record_revision`

validates. All other procurement facts are optional until supported by evidence. This is deliberate protection against filling fields merely because a source template normally contains them.

### 3. Planning milestone semantics are folded into v2

The temporary validation addendum has been retired. The main v2 candidate now contains:

- `PROCUREMENT_DOCUMENT_READY`
- `EXPECTED_PUBLICATION`

The rules distinguish both from actual notice publication. A procurement plan may contain future dates without creating a fabricated `notices[]` record.

### 4. Source wording belongs in provenance

Representative BCG and DAE fixtures previously carried source-only financing text as `source_raw` inside canonical financing objects. The strict contract exposed that as canonical-field contamination. The raw source wording is now retained in `observations[]`, while `financing_entries[]` holds only semantic financing fields.

This is a non-lossy normalization: source evidence is preserved, but it no longer creates an unofficial canonical field.

### 5. DAE probable successor remains qualified

`PROC-DAE-CHAR28-R2` retains:

- the later invitation reference;
- package/product/project lineage;
- probable predecessor/reissue relationship;
- mirror publication and closing evidence;
- I9/current commercial urgency;
- authoritative e-GP verification as the Research Frontier.

It does **not** create a `RETENDER` or `REISSUE` event. That event remains unasserted until authoritative evidence explicitly establishes the lifecycle event.

### 6. DGDP foreign-currency basis does not imply market scope

All three NP-8 fixtures retain foreign-currency tender basis in provenance observations. None derives `competition_scope: INTERNATIONAL` from currency alone. The source must separately establish national/international or other market scope.

### 7. One DGDP notice family does not become one multi-lot procurement

The inflatable boat, RHIB and SCUBA requirements remain three separate PROCUREMENT records with separate DGDP tender numbers. The v2 schema does not flatten them into one artificial multi-lot process.

## Machine-contract scope

The JSON Schema defines typed contracts for:

- identifiers;
- linked-record references;
- party-role links;
- budget and financing;
- procurement process controls;
- lots and items;
- notices;
- milestones and events;
- requirements;
- fees and securities;
- contacts;
- awards and contracts;
- implementation;
- field-level observations/provenance;
- ARGUS intelligence.

Observation values and raw values intentionally accept arbitrary JSON because authoritative source data may be scalar, structured, or list-valued. Canonical objects themselves remain strict.

## Information-preservation result

| Case | Identity/lineage | Parties | Process semantics | Dates/events | Commercial obligations | Evidence/intelligence | Material loss |
|---|---|---|---|---|---|---|---:|
| BCG CPV | PASS | PASS | PASS | PASS | PASS | PASS | 0 |
| DAE original LLP | PASS | PASS | PASS | PASS | PASS | PASS | 0 |
| DAE probable successor | PASS | PASS | PASS | PASS | N/A / unverified | PASS | 0 |
| DGDP inflatable boat | PASS | PASS | PASS | PASS | PASS for known fee | PASS | 0 |
| DGDP RHIB | PASS | PASS | PASS | PASS | PASS for known fee | PASS | 0 |
| DGDP SCUBA | PASS | PASS | PASS | PASS | PASS for known fee | PASS | 0 |
| World Bank SITA planning fixture | PASS | PASS | PASS | PASS | N/A in plan snapshot | PASS | 0 |

“Material information loss: 0” means source-supported decision-relevant facts in these dry-run transformations were retained either as canonical v2 values, links, milestones/events, or provenance observations. It does not claim that every historical procurement record has already been rehearsed.

## What remains before live activation

The current overlay is now covered, but live migration remains premature. Before changing write authority, ARGUS should still:

1. dry-run historical/baseline PROCUREMENT records, not only the six current overlays;
2. define deterministic transformation rules for ambiguous legacy fields rather than resolving them ad hoc;
3. define migration transaction boundaries, backup/rollback and readback verification;
4. define how v1.3 compatibility reads continue during transition;
5. run a full migration rehearsal against a disposable copy of canonical state;
6. compare record counts, identifiers, relationship targets, evidence/provenance and material values before/after migration;
7. obtain governed approval before changing `argus-intelligence.yaml` write authority or rewriting current records.

## Activation gate

### GO

Proceed with:

- historical/baseline v2 migration rehearsal;
- a deterministic migration transformer or governed transformation contract;
- rollback/readback controls;
- migration acceptance tests.

### NO-GO

Do **not** yet:

- rewrite `data/registry/current/*.json` into v2;
- change `data/registry/current-index.json` for this schema transition;
- switch the manifest from v1.3 to v2;
- delete v1.3 compatibility semantics;
- turn an inference into a FACT merely to satisfy v2;
- infer missing project, competition, security, award, contract or technical fields.

**v1.3 remains active.**
