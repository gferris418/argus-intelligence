# ARGUS Intelligence

ARGUS is Access Asia's government and public-sector opportunity-intelligence framework.

Its purpose is to identify credible business before formal tender publication, connect fragmented policy/project/funding/procurement evidence, prevent duplicate opportunity creation, prioritize decision-changing research, and promote only commercially actionable opportunities into the permanent PX pursuit pipeline.

## Production relationship with ATLAS OS

Within the Access Asia governed environment, **ATLAS OS is the execution-governance backbone**. ARGUS is a nested specialist domain method and does not create a second execution spine.

ATLAS owns generic domain classification, taxonomy/product/service/capability context, material risk flags, and applicable law/standards/framework alignment. Before ARGUS executes, ATLAS transfers that context through the governed **Domain Context Handoff v1**.

Canonical execution flow:

`User objective → ATLAS classification/alignment → ATLAS Domain Context handoff → ARGUS Contextualize → ARGUS domain method → ARGUS domain result + exact handoff receipt + proposed actions → ATLAS correlation verification/approval → authorized action(s) → ATLAS delivery`

ARGUS may enrich the ATLAS context for opportunity discovery—aliases, local terminology, adjacent solution classes, installed-base interpretation, supplier/competitor relevance, Bangladesh route implications—but it must not silently redefine ATLAS taxonomy or standards conclusions.

In Access Asia production, ARGUS rejects dependent execution on a `BLOCKED` handoff and returns the exact `handoff_id`, contract version and `payload_sha256` in every `ATLAS_GOVERNED` domain result. Standalone execution remains available for portability, testing, recovery, or non-Access-Asia implementations.

## Current persistence model: GitHub-first

For the current candidate phase, this private repository is the **interim physical canonical store** for ARGUS structured intelligence, synthesized intelligence, and database-related artifacts.

The logical ARGUS Master Registry remains platform-neutral. GitHub is the current storage implementation so the system can later shift to PostgreSQL, Supabase, Airtable, or another runtime without changing ARGUS identities or semantics.

Repository storage:

- `data/registry/` — canonical structured records, preferably JSON/JSONL;
- `data/syntheses/` — synthesized intelligence in Markdown/JSON;
- `data/exports/` — derived CSV/XLSX/JSON review and interchange views;
- `registry/` — Registry contracts, schemas, mappings, SQL migrations and future database materialization artifacts.

**Raw tender/source documents are not stored in GitHub.** GitHub stores only structured facts, synthesized intelligence, provenance, source references/locators, hashes where useful, reconciliation decisions, and commercial assessments. Original tender documents, email payloads, scans, attachments and other source files remain in their authorized source systems/document repositories.

See [`docs/architecture/github-first-canonical-store.md`](docs/architecture/github-first-canonical-store.md).

## Core operating loop

`Contextualize → Discover → Extract → Resolve → Reconcile → Validate → Assess → Prioritize → Decide → Promote/Monitor → Learn`

`Contextualize` is the first ARGUS operation in ATLAS-governed execution. It converts the governed ATLAS domain context into opportunity-intelligence search and interpretation context without changing upstream authority.

## 360° intelligence collection

ARGUS uses the doctrine **360° breadth, decision-driven depth**.

It examines all materially relevant intelligence lenses without requiring exhaustive collection. Coverage gaps feed the Research Frontier, which prioritizes only the questions likely to change the next commercial decision.

Core lenses:

- need / mission;
- policy / strategy;
- institution / stakeholders;
- programme / project;
- budget / funding;
- procurement / acquisition;
- technical / installed base;
- supplier / competitor;
- ecosystem / influence;
- commercial participation;
- timing / triggers;
- internal intelligence / history.

Coverage is recorded separately from evidence assurance and I0–I9 maturity.

## Canonical record types

- `ENTITY`
- `PROJECT`
- `PROCUREMENT`
- `INTELLIGENCE`
- `OPPORTUNITY`
- `SUPPLIER_PRODUCT`
- `KNOWLEDGE`

360° collection does not introduce an eighth record type.

## Repository authority

- Manifest: [`argus-intelligence.yaml`](argus-intelligence.yaml)
- Core: [`spec/core.md`](spec/core.md)
- ATLAS alignment: [`alignments/atlas-os.md`](alignments/atlas-os.md)
- Pinned ATLAS handoff contract: [`contracts/atlas/domain-context-handoff-v1.schema.json`](contracts/atlas/domain-context-handoff-v1.schema.json)
- Bangladesh profile: [`profiles/bangladesh.md`](profiles/bangladesh.md)
- Domain result schema: [`schemas/domain-result.schema.json`](schemas/domain-result.schema.json)
- GitHub-first persistence architecture: [`docs/architecture/github-first-canonical-store.md`](docs/architecture/github-first-canonical-store.md)
- Registry schema candidate: [`registry/schema/argus-master-registry-v0.2.1.json`](registry/schema/argus-master-registry-v0.2.1.json)
- End-to-end validation: [`docs/validation/atlas-argus-bd-e2e.md`](docs/validation/atlas-argus-bd-e2e.md)
- Bangladesh lifecycle validation: [`docs/validation/bangladesh-lifecycle-release-gates-rc2.md`](docs/validation/bangladesh-lifecycle-release-gates-rc2.md)

## Current status

`2.0.0-rc.2` — candidate.

The ATLAS/ARGUS architecture, 360° collection contract, Registry compatibility design, representative Bangladesh lifecycle gates, and governed ATLAS domain-context handoff are under CI validation. Operational database deployment remains deferred for the current phase; GitHub is the interim canonical persistence layer while ARGUS usage and integration requirements mature.
