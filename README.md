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
- Bangladesh profile: [`profiles/bangladesh.md`](profiles/bangladesh.md)
- Domain result schema: [`schemas/domain-result.schema.json`](schemas/domain-result.schema.json)
- End-to-end validation: [`docs/validation/atlas-argus-bd-e2e.md`](docs/validation/atlas-argus-bd-e2e.md)
- 360° collection validation: [`docs/validation/360-intelligence-collection.md`](docs/validation/360-intelligence-collection.md)
- 360° contract test: [`tests/test_360_collection_contract.py`](tests/test_360_collection_contract.py)

## Current status

`2.0.0-rc.2` — candidate.

The system-level architecture has passed the ATLAS OS → ARGUS Bangladesh → result-path review. The rc.2 candidate adds governed 360° collection coverage while preserving the ATLAS boundary, seven-record Registry model and decision-driven Research Frontier. Canonical promotion remains gated by Registry API/schema compatibility checks and representative Bangladesh route tests.
