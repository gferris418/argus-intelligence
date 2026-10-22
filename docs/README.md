---
description: "ARGUS Intelligence documentation home: government commercial opportunity intelligence under ATLAS governance."
icon: radar
---

# ARGUS Intelligence

ARGUS is the **ATLAS-governed government commercial opportunity intelligence system** for Access Asia. It identifies government needs, programmes, projects, budgets, approvals and procurements as early as legitimately observable; develops commercial opportunity hypotheses before a formal tender exists; tracks them through the full public-sector lifecycle; and identifies suitable international OEMs, suppliers, solution providers and contractors.

**Current candidate:** `3.0.0-rc.2`  
**Current ATLAS compatibility:** `ATLAS-OS 3.0.2` at `95e78eb4f386c7434193014811ef8d2ce5254c30`

## ATLAS governance boundary

ATLAS OS remains the operating architecture and owns Mission Control, Control Plane authority, preprocessing, routing, permissions, approvals, canonical taxonomy, canonical evidence acceptance, authoritative commercial priority, pursuit decisions, persistence authorization, observability, verification, Dashboard and final delivery.

When ATLAS is active, every user prompt enters Mission Control first. Mission Control is the governance entry gate and does not add a fourth preprocessing step. The ATLAS preprocessing sequence remains exactly **Understand + Normalize → Minimal Domain Framing → Route**.

ARGUS is the bounded provider for semantic capability `intelligence_collection`. It does not self-activate. ATLAS must route to `ARGUS` or `MULTI_CAPABILITY`, and explicit user approval for `ARGUS_ACTIVATION` is required before ARGUS executes. Every ARGUS result returns to ATLAS; ATLAS remains next-step authority.

```text
USER / EVENT
  -> ATLAS Mission Control [FIRST GOVERNANCE GATE]
  -> ATLAS Control Plane
  -> Understand + Normalize
  -> Minimal Domain Framing
  -> Route
       -> DIRECT_SEARCH / DEEP_RESEARCH -> ATLAS
       -> ARGUS -> explicit ARGUS_ACTIVATION approval -> ARGUS bounded collection
       -> MULTI_CAPABILITY -> approved ARGUS collection + ATLAS analysis/decision
  -> ARGUS provider result
  -> ATLAS provider-return reconciliation
  -> ATLAS verification / authorized action / delivery
```

The previous signed ATLAS 2.x handoff/lease/synchronization transport remains in the repository only as tested backward-compatibility evidence. It is not the current ATLAS integration authority.

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

The GitHub repository is authoritative for machine-readable contracts, schemas, lifecycle logic, validation evidence, release decisions, and documentation source. SharePoint SQLite remains the current mutable Access Asia ARGUS commercial state; GitHub stores schemas, governance, migrations and release/audit snapshots rather than a parallel live database.

Published documentation: https://accessasia.gitbook.io/accessasia-docs/argus-intelligence/
