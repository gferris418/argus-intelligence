# GitHub-First Canonical Storage Architecture

**Status:** ACTIVE INTERIM ARCHITECTURE  
**Effective date:** 2026-10-18  
**Reviewed:** 2026-10-22  
**Applies to:** ARGUS Intelligence candidate work until superseded

## Decision

For the current ARGUS phase, the `argus-intelligence` GitHub repository is the **interim physical canonical store** for ARGUS structured intelligence, synthesized intelligence, schemas, database designs, migrations, and controlled exports.

The logical ARGUS Master Registry contract remains platform-neutral. GitHub is the current physical implementation, not a permanent semantic dependency.

**Repository visibility verified on 2026-10-22: public.** Therefore repository content must be treated as public even when the underlying business systems are private. Credentials, sharing tokens, personal data, confidential CRM details, SharePoint/HubSpot native identifiers that could expose private records, and restricted source payloads **must not be committed**.

## Access Asia system-of-record rule

The integration rule is **pointers, not copies**. Each information class has one canonical owner; other systems store only the minimum reference or derived intelligence necessary for their own function.

| Information class | Canonical owner | ARGUS/GitHub treatment |
|---|---|---|
| ATLAS execution policy, routing, approvals, persistence governance | ATLAS GitHub | Reference the ATLAS contract/revision; do not duplicate ATLAS authority |
| Supplier/customer/OEM/company CRM identity | HubSpot COMPANY | Store a stable non-sensitive integration key and intelligence overlay; resolve current CRM master data at runtime |
| Individual contacts | HubSpot CONTACT | Do not replicate contact details into ARGUS |
| Access Asia relationship state, communication history, tasks and commercial interactions | HubSpot | Store derived intelligence only when required, with provenance; do not copy CRM history |
| CRM deal/pipeline records | HubSpot DEAL | Link by governed integration key when required; do not treat ARGUS as the deal pipeline |
| Original and working business documents | SharePoint | Store evidence metadata and logical locator only; do not copy source bytes into GitHub |
| Tracked opportunity working folders through pre-submission | SharePoint `General/Business Intelligence/50_OPPORTUNITIES` | Store lifecycle state and logical folder pointer only |
| Formal submission working folders | SharePoint `General/REV/OPP Opportunities` | Store lifecycle state and logical folder pointer only |
| Awarded project working folders | SharePoint `General/OPS/PRJ Projects` | Store lifecycle state and logical folder pointer only |
| ARGUS structured government-commercial intelligence | ARGUS GitHub `data/registry/` | Canonical here |
| ARGUS synthesized intelligence | ARGUS GitHub `data/syntheses/` | Canonical synthesis here |
| ARGUS schemas/contracts/database mappings/migrations | ARGUS GitHub | Canonical here |
| Derived tabular exports | ARGUS GitHub `data/exports/` | Controlled derived view only |

Machine-readable Access Asia system pointers are maintained in `profiles/access-asia-system-registry.yaml`.

## SharePoint logical locator

GitHub may retain the following non-secret logical navigation information so future agents can locate the governed document workspace without relying on chat memory:

```yaml
sharepoint:
  hostname: accessasiaccl.sharepoint.com
  site_path: /sites/accessasia
  site_display_name: Access Asia Limited
  document_library: Documents
  business_intelligence_root: General/Business Intelligence
```

Allowed folder-name metadata includes the governed Business Intelligence structure (`10_SOURCE_MAP`, `20_ARCHITECTURE`, `30_OPERATIONS`, `40_VALIDATION`, `50_OPPORTUNITIES`, `90_ARCHIVE`, `99_INBOX`).

Do **not** commit SharePoint sharing URLs containing access/query tokens, Graph drive IDs, item IDs, permission IDs, authentication artifacts, or private recipient information. Resolve native identifiers at runtime through the authorized SharePoint integration.

## HubSpot linking rule

HubSpot is the canonical CRM for suppliers, OEMs, customers, partners, contacts and Access Asia commercial relationships.

ARGUS supplier/company records use a stable `integration_key`, normally the ARGUS supplier/party identifier. The preferred integration is to mirror that stable key into a HubSpot custom property so either system can resolve the other without committing HubSpot-native IDs to this public repository.

A HubSpot-native company/contact/deal ID may be used transiently by an authorized connector at runtime, but committed ARGUS records must leave such fields null while the repository is public.

## Format policy

### Primary canonical structured format

Use **JSON or JSONL** for canonical ARGUS records because it is deterministic, machine-readable, diffable, schema-validatable and portable.

### Supporting formats

- **Markdown** — synthesized briefs, decision records, research notes, validation reports, ADRs.
- **CSV** — flat interchange, review tables, analysis extracts, import/export.
- **XLSX** — human review or operational interchange only; not preferred canonical state.
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
- raw archive bundles;
- CRM exports containing contacts or private relationship history;
- SharePoint source files copied solely for AI convenience.

GitHub may contain synthesized or structured derivatives such as official reference number, title/package name, public buyer/procuring entity/end user, publication/closing dates, procurement method/status, project/funding relationship, extracted facts, analytical assessment, evidence metadata, source-system label, safe logical locator, source hash where available, provenance, `as_of` date, conflicts/unknowns/staleness, reconciliation decision and next action.

The repository must never become a duplicate CRM or document-management system.

## Evidence references

A canonical record may reference a source without storing source bytes. Evidence references should capture enough non-sensitive metadata to retrieve or verify the source later.

Recommended public-safe shape:

```json
{
  "source_system": "SHAREPOINT",
  "source_id": "logical-business-reference",
  "source_locator": "General/Business Intelligence/50_OPPORTUNITIES/2026_PX00012_CPV",
  "title": "Working opportunity folder",
  "as_of": "2026-10-22",
  "claim_type": "FACT",
  "claim_condition": "CURRENT",
  "source_sha256": null
}
```

`source_sha256` is provenance metadata only. It does not imply source bytes are stored in GitHub.

## Repository layout

```text
argus-intelligence/
├── argus-intelligence.yaml
├── data/
│   ├── registry/       # canonical structured intelligence records
│   ├── syntheses/      # synthesized intelligence only
│   └── exports/        # controlled derived views
├── registry/
│   ├── contract/
│   ├── schema/
│   ├── migrations/
│   └── ...
├── profiles/
│   └── access-asia-system-registry.yaml
├── schemas/
├── spec/
├── docs/
└── tests/
```

## Canonical write discipline

1. Resolve/reconcile identity before creating a new canonical ARGUS record.
2. Preserve stable `argus_id` values and cross-system integration keys.
3. Prefer one record per line in JSONL for growing registries; use deterministic ordering where practical.
4. Every canonical ARGUS mutation occurs through a reviewed Git commit/PR or equivalently controlled repository write.
5. Preserve provenance and revision/history.
6. Do not silently overwrite conflicts.
7. Do not promote a derivative or snapshot into the canonical owner for another system.
8. Resolve HubSpot and SharePoint native IDs at runtime rather than persisting them in public Git.

## Database deferral

Operational PostgreSQL/Supabase/Neon deployment is **deferred**, not abandoned. Move to an operational database when concurrent multi-user writes, high-frequency automated ingestion, transactional workflows, large record volumes, fine-grained permissions, event workloads or low-latency API/UI needs make GitHub unsuitable.

A future database should materialize the GitHub-governed logical Registry and preserve ARGUS IDs, evidence, relationships, history and provenance. It must not replace HubSpot as CRM or SharePoint as document/work-file authority.

## Security and sensitivity

Regardless of repository visibility, do not commit credentials, API keys, passwords, connection strings, sharing tokens, restricted/classified tender payloads, personal data unless explicitly authorized and materially necessary, operational-security-sensitive material, confidential CRM exports, or source documents whose handling rules prohibit repository storage.

Where sensitivity is material, store only the minimum synthesized intelligence necessary for the decision and retain the original in the authorized source system.
