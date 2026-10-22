---
description: "ARGUS Intelligence documentation home: government commercial opportunity intelligence under ATLAS governance."
icon: radar
---

# ARGUS Intelligence

ARGUS is the **ATLAS-governed government commercial opportunity intelligence system** for Access Asia. It identifies government needs, programmes, projects, budgets, approvals and procurements as early as legitimately observable; develops commercial opportunity hypotheses before a formal tender exists; tracks them through the full public-sector lifecycle; and identifies suitable international OEMs, suppliers, solution providers and contractors.

**Current candidate:** `3.0.0-rc.1`

## ATLAS governance boundary

ATLAS OS remains the operating architecture and owns Mission Control, Control Plane authority, permissions, approvals, canonical taxonomy, canonical evidence acceptance, authoritative commercial priority, pursuit decisions, persistence authorization, observability, Dashboard and final delivery.

ARGUS activates only for `ARGUS_COLLECTION` or `HYBRID` collection modes.

```text
USER / EVENT
  -> ATLAS Mission Control + Control Plane
  -> Intent + target interpretation
  -> Collection-Need Gate
       -> NONE             -> ATLAS
       -> ATLAS_DIRECT     -> ATLAS direct retrieval/research
       -> ARGUS_COLLECTION -> ARGUS bounded intelligence mission
       -> HYBRID           -> ARGUS intelligence + ATLAS analysis/decision
  -> ATLAS Evidence Governance / assurance / authorized action / delivery
```

## Five persistent engines

1. **Demand Intelligence** — needs, programmes, projects, budgets, approvals, procurement and installed base.
2. **Supply Intelligence** — OEMs, suppliers, contractors, technologies, products, references, exportability and partnerability.
3. **Opportunity Engine** — persistent opportunity identity and S0–S9 lifecycle reconciliation.
4. **Matching & Qualification** — demand-to-supplier matching, configurable scoring and recommended priority.
5. **Early Warning** — monitoring, watchlists, trigger detection and Rapid Tender Mode.

## Start here

- [ATLAS–ARGUS collection boundary](architecture/atlas-argus-collection-boundary.md)
- [ARGUS v3 government commercial opportunity intelligence](architecture/government-commercial-opportunity-v3.md)
- [Bangladesh Procurement Source Standard v1.0](architecture/bangladesh-procurement-source-standard-v1.md)
- [ARGUS Capability Integration Model](architecture/capability-integration.md)
- [GitHub-First Canonical Storage Architecture](architecture/github-first-canonical-store.md)
- [Live runtime testing](live-testing.md)
- [ATLAS OS → ARGUS Bangladesh → Results](validation/atlas-argus-bd-e2e.md)
- [ATLAS–ARGUS synchronization validation](validation/atlas-argus-synchronization-v1.md)

## Source of truth

The GitHub repository is authoritative for machine-readable contracts, schemas, lifecycle logic, validation evidence, release decisions, and documentation source. GitBook is the published human-readable documentation layer.

Published documentation: https://accessasia.gitbook.io/accessasia-docs/argus-intelligence/
