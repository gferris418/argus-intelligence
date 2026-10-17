# ARGUS Intelligence

ARGUS is Access Asia's government and public-sector opportunity-intelligence framework.

Its purpose is to identify credible business before formal tender publication, connect fragmented policy/project/funding/procurement evidence, prevent duplicate opportunity creation, prioritize decision-changing research, and promote only commercially actionable opportunities into the permanent PX pursuit pipeline.

## Production relationship with ATLAS OS

Within the Access Asia governed environment, **ATLAS OS is the unchanged execution-governance backbone**. ARGUS is a nested domain method and does not create a second execution spine.

Canonical production flow:

`User objective → ATLAS OS → ARGUS domain method → ARGUS domain result + proposed domain actions → ATLAS verification/approval → authorized domain action(s) → ATLAS task-artifact persistence → ATLAS delivery`

ARGUS remains independently specified and portable. Standalone execution is reserved for portability, testing, recovery, or non-Access-Asia implementations.

## Core operating loop

`Discover → Extract → Resolve → Reconcile → Validate → Assess → Prioritize → Decide → Promote/Monitor → Learn`

## Canonical record types

- `ENTITY`
- `PROJECT`
- `PROCUREMENT`
- `INTELLIGENCE`
- `OPPORTUNITY`
- `SUPPLIER_PRODUCT`
- `KNOWLEDGE`

## Repository authority

- Manifest: [`argus-intelligence.yaml`](argus-intelligence.yaml)
- Core: [`spec/core.md`](spec/core.md)
- ATLAS alignment: [`alignments/atlas-os.md`](alignments/atlas-os.md)
- Bangladesh profile: [`profiles/bangladesh.md`](profiles/bangladesh.md)
- Domain result schema: [`schemas/domain-result.schema.json`](schemas/domain-result.schema.json)
- End-to-end validation: [`docs/validation/atlas-argus-bd-e2e.md`](docs/validation/atlas-argus-bd-e2e.md)

## Current status

`2.0.0-rc.1` — candidate.

The system-level architecture has passed the ATLAS OS → ARGUS Bangladesh → result-path review. Canonical promotion remains gated by Registry API/schema compatibility checks and representative Bangladesh route tests.
