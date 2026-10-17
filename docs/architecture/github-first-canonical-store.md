# GitHub-First Canonical Storage Architecture

**Status:** ACTIVE INTERIM ARCHITECTURE  
**Effective date:** 2026-10-18  
**Applies to:** ARGUS Intelligence `2.0.0-rc.2` and subsequent candidate work until superseded

## Decision

For the current ARGUS phase, the private `argus-intelligence` GitHub repository is the **interim physical canonical store** for ARGUS structured intelligence, synthesized intelligence, schemas, database designs, migrations, and controlled exports.

The logical ARGUS Master Registry contract remains platform-neutral. GitHub is the current physical implementation, not a permanent semantic dependency.

This allows ARGUS to defer commitment to PostgreSQL, Supabase, Airtable, or another operational database until usage patterns, workflow requirements, scale, permissions, and integration needs justify that move.

## Canonical ownership

| Information class | Interim canonical home |
|---|---|
| ARGUS structured records | `data/registry/` in GitHub |
| Synthesized opportunity/project/procurement intelligence | `data/syntheses/` in GitHub |
| Schemas/contracts/database mappings/migrations | `registry/` in GitHub |
| Human-readable framework/governance/validation | repository Markdown/YAML/JSON |
| Derived tabular exports | `data/exports/` in GitHub |
| Raw tender/source documents | **Not GitHub** |
| Original emails/correspondence | source communication system; GitHub stores references/synthesis only |
| Original source documents | external document repository/source system; GitHub stores references/synthesis only |

## Format policy

### Primary canonical structured format

Use **JSON or JSONL** for canonical ARGUS records.

Reasons:
- deterministic and machine-readable;
- diffable in Git;
- directly maps to the ARGUS JSON Schema;
- portable into PostgreSQL, document databases, analytics systems, Python, JavaScript, and API payloads;
- preserves nested evidence, relationships, classifications, coverage, and unknowns better than flat spreadsheets.

### Supporting formats

- **Markdown** — synthesized briefs, decision records, research notes, validation reports, ADRs.
- **CSV** — flat interchange, review tables, analysis extracts, import/export.
- **XLSX** — permitted for human review or operational interchange when spreadsheet structure materially helps; it is not the preferred source of truth because Git cannot meaningfully diff binary workbooks.
- **YAML** — manifests/configuration.
- **SQL** — database schemas/migrations/materialization scripts only.

## Tender/source-document rule

GitHub MUST NOT contain raw tender documents or other original source-document payloads.

Examples that must remain outside GitHub:
- tender/RFP/RFQ/EOI/PQ PDF or Word files;
- scanned notices and attachments;
- original bid documents;
- original technical specifications received from buyers;
- original email `.msg`/`.eml` payloads;
- raw archive bundles.

GitHub may contain only synthesized or structured derivatives such as:
- official reference number;
- title/package name;
- buyer/procuring entity/end user;
- publication/closing dates;
- procurement method/status;
- project/funding relationship;
- extracted requirements/facts;
- analytical assessment;
- evidence/source metadata;
- source URL or external repository locator;
- source hash where available;
- provenance and `as_of` date;
- conflicts, unknowns, stale-state indicators;
- reconciliation/identity decision;
- commercial decision/next action.

The repository must never become a duplicate document-management system.

## Evidence references

A canonical record may reference a source without storing the source bytes. Evidence references should capture enough metadata to retrieve or verify the source later.

Recommended fields:

```json
{
  "source_system": "BPPA",
  "source_id": "external-reference",
  "source_locator": "https://... or external repository path",
  "title": "Official tender/package title",
  "as_of": "2026-10-18",
  "claim_type": "FACT",
  "claim_condition": "CURRENT",
  "source_sha256": "optional when the source can be hashed externally"
}
```

`source_sha256` is provenance metadata only. It does not imply that the source file is stored in GitHub.

## Repository layout

```text
argus-intelligence/
├── argus-intelligence.yaml
├── data/
│   ├── registry/       # canonical structured records
│   ├── syntheses/      # synthesized intelligence only
│   └── exports/        # derived CSV/XLSX views
├── registry/
│   ├── contract/
│   ├── schema/
│   ├── migrations/
│   └── ...             # physical DB mappings/materialization artifacts
├── profiles/
├── schemas/
├── spec/
├── docs/
└── tests/
```

## Canonical write discipline

1. Resolve/reconcile identity before creating a new canonical record.
2. Preserve stable `argus_id` values.
3. Prefer one record per line in JSONL when maintaining a growing registry; use deterministic ordering where practical.
4. Every canonical mutation occurs through a reviewed Git commit/PR or an equivalently controlled repository write.
5. Material changes must preserve provenance and revision/history through Git plus record-level revision metadata.
6. Do not silently overwrite conflicts; preserve the current state plus evidence/conflict metadata.
7. A synthesized Markdown brief may summarize records but does not supersede structured Registry state unless explicitly designated as the canonical record representation.

## Database deferral

Operational PostgreSQL/Supabase/Neon deployment is **deferred**, not abandoned.

All database-related information remains versioned in GitHub:
- logical contracts;
- JSON Schema;
- physical schema designs;
- SQL migrations;
- mapper/API contracts;
- indexes/constraints;
- seed/synthetic fixtures;
- validation reports;
- deployment runbooks;
- portability mappings.

When an operational database is later selected, it should be treated as a materialized runtime of the GitHub-governed logical Registry. Migration must preserve ARGUS IDs, evidence, relationships, history, and provenance.

## Security and sensitivity

This repository is private, but private GitHub storage does not remove information-classification obligations.

Do not commit:
- credentials, API keys, passwords, connection strings, or secrets;
- restricted/classified tender payloads;
- personal data unless materially necessary and authorized;
- operational-security-sensitive source files;
- source documents whose license, confidentiality, or handling rules prohibit repository storage.

Where sensitivity is material, store only the minimum synthesized information necessary for the commercial intelligence decision and retain the original in the authorized source system.

## Exit criteria for moving to a database

Move from GitHub-first storage to an operational database when one or more become material:
- concurrent multi-user writes;
- high-frequency automated ingestion;
- row-level permissions beyond repository controls;
- transactional workflows;
- large record volumes or search latency;
- API-driven CRM/Outlook/SharePoint synchronization;
- event/monitoring workloads;
- analytics requiring frequent structured queries;
- UI workflows needing low-latency CRUD.

The shift must be a storage/runtime migration, not a redesign of ARGUS semantics.
