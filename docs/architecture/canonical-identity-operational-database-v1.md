# Canonical Identity and Operational Database v1

## Decision

ARGUS uses a two-layer identity model and one mutable operational structured store.

- **GitHub** is authoritative for schemas, identity rules, migration logic, tests, release contracts and code.
- **SharePoint SQLite** is authoritative for mutable operational ARGUS structured data used by ATLAS/ARGUS in Access Asia production.
- Existing GitHub JSON/JSONL registry content is retained as migration/audit/bootstrap material and must not remain a competing live write authority after database activation.
- SharePoint documents remain evidence/working files and are referenced from the database rather than copied into it.

## Identity model

Every distinct canonical object has:

1. `internal_uuid` — opaque immutable database primary key.
2. `canonical_id` — immutable unique human-readable business key.
3. zero or more source-native external identifiers.

Canonical IDs use `<TYPE>-<JURISDICTION>-<SEQUENCE>` such as `PROC-BD-000001`.

Supported object families include policy, strategy, programme, project, requirement, procurement plan, package, procurement process, tender, lot, item, entity, person, award, contract, event, document, source record, observation and product/solution.

Suppliers and OEMs are ENTITY roles, not separate identity universes.

## Policy-to-tender lineage

```text
POLICY
  -> STRATEGY / MASTER PLAN
  -> PROGRAMME
  -> PROJECT
  -> REQUIREMENT
  -> PROCUREMENT PLAN
  -> PACKAGE
  -> PROCUREMENT PROCESS
  -> TENDER / SOLICITATION
  -> LOT / ITEM
  -> AWARD
  -> CONTRACT
```

Missing upstream links remain unknown until evidence is found. A tender must never cause ARGUS to fabricate a parent project, programme or policy.

## Source and evidence model

A canonical object is not a portal record. BPPA, e-GP, DGDP/e-DP, World Bank, ADB and agency-native records are stored as source records with their native identifiers and linked to the appropriate canonical object.

Material facts are stored as observations with source provenance. Changes are append-only events. Corrigenda do not create new tenders; genuine re-tenders create new procurement/tender identities but may retain the same requirement lineage.

## Operational SQLite location

Access Asia production path:

`General/Business Intelligence/30_OPERATIONS/ARGUS_OPERATIONAL.sqlite`

The path is an operational configuration and is not embedded with SharePoint drive/item secrets in public Git.

## Update protocol

For a governed data change:

1. Fetch the current SharePoint SQLite file.
2. Run `integrity-check` before mutation.
3. Resolve identity before creating anything new.
4. Apply one transaction using canonical IDs and source provenance.
5. Run `PRAGMA integrity_check` and foreign-key validation.
6. Record the mutation in `change_log`.
7. Replace the same SharePoint file; do not create parallel database copies for routine updates.
8. Rely on SharePoint file version history for recoverability.
9. Update GitHub only when the schema, rules, migrations or code change.

## Identity resolution

Match in this order:

1. exact official identifier;
2. exact source-system identifier;
3. project/package relationship;
4. entity plus reference number;
5. requirement semantics;
6. dates, amounts and item characteristics;
7. fuzzy title similarity.

Title similarity alone never authorizes a merge.

## Failure rule

If identity is unresolved, create a `CANDIDATE` object or leave the relationship unresolved. Never silently merge two records and never fabricate missing lineage.
