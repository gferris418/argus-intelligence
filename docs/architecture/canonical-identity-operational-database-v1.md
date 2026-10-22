# Canonical Identity and Operational Database v1

## Decision

ARGUS uses a **three-layer identity model** and one mutable operational structured store.

- **GitHub** is authoritative for schemas, identity rules, migration logic, tests, release contracts and code.
- **SharePoint SQLite** is authoritative for the current mutable operational ARGUS structured state used by ATLAS/ARGUS in Access Asia production.
- Existing GitHub JSON/JSONL registry records remain migration/audit/bootstrap material and versioned release evidence; they are not a parallel routine write store after database activation.
- SharePoint source and working documents remain files and are referenced by source records rather than copied into public Git.

## Three identity layers

### 1. Canonical objects

A unique real-world or business object gets one permanent canonical identity:

- `internal_id` — opaque immutable UUID database primary key;
- `canonical_id` — immutable unique human-readable ARGUS identifier;
- zero or more source-native external identifiers.

New canonical IDs use `<TYPE>-<JURISDICTION>-<SEQUENCE>`, for example `REQ-BD-000001` or `PROC-BD-000001`.

Existing ARGUS IDs are grandfathered and remain immutable. They are not renumbered just to conform to the new display format.

Canonical object types cover policy, strategy, programme, project, requirement, procurement plan, package, procurement process, solicitation, lot, item, award, contract, organization, person, product, financing, document and opportunity.

A supplier, OEM, buyer, procuring entity, implementing agency, end user or funder is an **ORGANIZATION role**, not a separate identity universe.

### 2. Source records

A BPPA/e-GP/DGDP/e-DP/World Bank/ADB/agency record is evidence about canonical objects. It receives its own `source_record_id`, preserves native IDs and source labels, and links to the relevant canonical object(s).

A portal ID never replaces the ARGUS canonical ID.

### 3. Events and observations

Changes and evidence are separately identified:

- events: publication, corrigendum, deadline extension, cancellation, re-tender, award, signing, etc.;
- observations: field-level evidence with raw value, normalized value, source and claim state.

A corrigendum is an event, not a new tender. An official re-tender/reissue can create a new procurement/solicitation cycle while preserving the same underlying requirement lineage when evidence supports that relationship.

## Policy-to-tender lineage

```text
POLICY
  -> STRATEGY / MASTER PLAN
  -> PROGRAMME
  -> PROJECT
  -> REQUIREMENT
  -> PROCUREMENT PLAN
  -> PROCUREMENT PACKAGE
  -> PROCUREMENT PROCESS
  -> TENDER / SOLICITATION
  -> LOT / ITEM
  -> AWARD
  -> CONTRACT
```

Missing upstream links remain `UNKNOWN` until evidence is found. A tender must never cause ARGUS to fabricate a parent project, programme or policy.

## Identity resolution

Resolve a discovered record in this order:

1. exact authoritative identifier;
2. exact source-system identifier;
3. reconciled project/package relationship;
4. entity plus reference number;
5. requirement semantics and lineage;
6. dates, amounts, items and other material characteristics;
7. fuzzy title similarity as supporting evidence only.

Title similarity alone never authorizes a merge.

## Operational SQLite location

Access Asia production path:

`General/Business Intelligence/30_OPERATIONS/ARGUS_Master_Registry.sqlite`

The public repository records only the logical SharePoint path. SharePoint drive IDs, item IDs and sharing tokens must never be committed to public Git.

## Single-writer update protocol

For every operational data mutation:

1. Fetch the latest SharePoint SQLite file.
2. Verify SharePoint target/version metadata and run `PRAGMA integrity_check` before mutation.
3. Resolve identity before creating a new canonical object.
4. Apply one local SQLite transaction.
5. Preserve source provenance, external identifiers, events and observations.
6. Record the mutation in `mutation_log`.
7. Run SQLite integrity and foreign-key checks after mutation.
8. Replace the same SharePoint file; do not create parallel routine database copies.
9. Verify the uploaded target/version.
10. Use SharePoint version history for rollback and audit.

Never open/mutate the database in place over a SharePoint-synced filesystem and never perform concurrent writers against separate copies.

## Source of truth split

| Information class | Authority |
|---|---|
| Identity rules / schema / code / migrations | GitHub |
| Current mutable ARGUS structured operational state | SharePoint SQLite |
| Raw/working business documents | SharePoint |
| Historical GitHub registry baseline | Migration/bootstrap/audit evidence |
| CRM company/contact/relationship state | HubSpot, according to Access Asia system routing |

## Failure rule

If identity is unresolved, create a candidate object only when a distinct object is genuinely warranted, or leave the relationship unresolved. Never silently merge two records and never fabricate missing lineage.
