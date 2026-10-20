# DTIF Reconciliation and Archive-Only Disposition

**Control:** `DTIF-RECONCILIATION`  
**Date:** 2026-10-20  
**Decision:** `RECONCILED_ARCHIVE_ONLY`

## Decision

DTIF is no longer an operational authority or runtime dependency. Its three legacy workbook sources are retained read-only as historical migration evidence. The current ARGUS structured-intelligence authority remains the GitHub Master Registry (`data/registry/`). No legacy DTIF record is promoted into current truth solely because DTIF once labelled it active, published, planned, or commercially relevant.

This closes the data-reconciliation gate without a destructive purge and without a bulk legacy cutover.

## 1. Source provenance verification

The accepted migration pilot identified three read-only legacy source workbooks. On 2026-10-20 their actual Library bytes were materialized and SHA-256 verified against the hashes embedded in `ARGUS-DTIF-MIGRATION-PILOT-001 v0.1.0`:

| Source | File | Verified SHA-256 |
|---|---|---|
| DB-001 | `20261014_01_Opportunities_Master_v2.0.0.xlsx` | `1bd99cc3bf4f8b669c901fe198df2d6f6eeeb0c6f13f27272cfec296f2c60a77` |
| DB-002 | `20261014_02_Suppliers_Products_Master_v2.0.0.xlsx` | `a3ef7ae0efed440d6ed27dea2721c1f31207bd44300ea2cb8cfd17531e60daf7` |
| DB-003 | `20261010_03_Pursuits_Bids_Projects_v1.1.0.xlsx` | `26b204e536c3d2151df0e3b4da6cfaaac198c3e66d9b4585159542ba4b5803c2` |

The pilot JSON itself matches the GitHub baseline's pinned fixture SHA-256 `2cfb99c9045eb8bf2739f39db3591b618307bda4b3cc1b301461bb259e50f2b9`.

## 2. Canonical-baseline reconciliation

The GitHub baseline remains intentionally small: 11 representative records imported from the accepted pilot. `data/registry/baseline.json` explicitly records that this was an accepted synthesized migration pilot and **not** a fresh byte-for-byte export of the prior database runtime. Current-state reads use `data/registry/current-index.json` overlays.

That provenance boundary is retained. This reconciliation does not rewrite the baseline to pretend that a database cutover occurred.

## 3. Wave-1 database state recovered and fingerprinted

The previously accepted ARGUS Wave-1 database still exists in the surviving Supabase ARGUS schema. A read-only recheck on 2026-10-20 confirmed:

- 131 total registry records;
- 119 Wave-1 procurement records carrying status `published_or_active_source_current_status_unverified`;
- one Wave-1 supporting entity, `ENT-BD-AIR-FORCE`;
- zero broken relationship targets in the accepted Wave-1 validation;
- 136 evidence rows, 135 external-reference rows, 130 related-ID rows and 130 typed-relationship rows.

A deterministic ordered-content MD5 fingerprint was captured for each of the eight business tables used by the historical migration state. Those fingerprints are recorded in `data/registry/dtif-reconciliation-receipt.json` so later audits can distinguish the verified historical state from a reconstructed claim.

The Wave-1 records are **not** automatically restored into the GitHub current overlay. Their own accepted status says current state is unverified. They therefore remain historical lineage and require current-source reverification before re-entry into current ARGUS truth.

## 4. Remaining legacy-class disposition

The retirement manifest previously left four classes requiring disposition. They are now accounted for as follows:

| Legacy class | Known count | Disposition |
|---|---:|---|
| DB-001 current/published Wave-1 | 119 | historical lineage; reverify on trigger |
| DB-001 planned purchases | 702 | retain read-only; reverify on current requirement/procurement trigger |
| DB-002 supplier/product relationships | not asserted here | retain read-only; independently reverify before reuse |
| DB-003 pursuit/budget material | not asserted here | retain read-only; re-evaluate against current commercial/procurement evidence before active use |

Bulk import is prohibited for every class. This preserves the earlier migration principle that weak, stale, assumed, or merely planned legacy material must not be upgraded into canonical current truth.

## 5. Dependency and archive decision

The prior retirement controls already removed DTIF from operational use and prohibited new DTIF canonical writes. The current GitHub architecture does not use DTIF as a runtime dependency. The three original workbooks remain available as retained source evidence, while active ARGUS state is governed by the GitHub baseline/current-overlay model.

Accordingly:

- DTIF may be treated as **historical/archive-only**;
- original source bytes must be retained;
- destructive deletion is not authorized by this reconciliation;
- no DTIF runtime reactivation is permitted;
- any recovered legacy claim must enter through normal ARGUS current-evidence acquisition, reconciliation and verification.

## 6. Verification contract

`tests/test_dtif_reconciliation.py` enforces the durable parts of this decision:

1. exact source hashes and pilot-fixture identity;
2. historical Wave-1 counts and table fingerprints;
3. explicit disposition of every remaining legacy class;
4. canonical baseline integrity and current-overlay relationship resolution;
5. retain-only archive policy with no bulk-cutover/current-truth overclaim.

The ATLAS migration control may be marked closed only after this ARGUS change is merged through protected CI and the exact merged commit is recorded as the closure evidence.
