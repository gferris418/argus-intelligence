# ADR 0004: Progressive Supplier, Market and Network Intelligence

- **Status:** Accepted for Issue #76 design
- **Date:** 2026-10-23
- **Decision owners:** ATLAS governance / ARGUS intelligence architecture

## Context

ARGUS must discover and qualify foreign OEMs, suppliers, contractors and solution providers quickly enough to support early opportunity shaping and rapid tender recovery, while preserving canonical identity, evidence quality and commercial safety. The repository already separates canonical organization identity, supplier-intelligence overlay, opportunity-supplier matching, and landscape/network collection modes.

A monolithic supplier score or one-shot full dossier would either collapse distinct commercial questions or impose excessive cost and latency on broad supplier discovery.

## Decision

1. **Supplier identity remains the canonical ARGUS ORGANIZATION identity.** Provider, CRM, social, trade-database and website identifiers are aliases/evidence only.
2. **Supplier Intelligence is a progressive overlay** on the same organization identity, with research depth states:
   - `DISCOVERY`
   - `FAST_QUALIFICATION`
   - `CAPABILITY_VALIDATION`
   - `FULL_DOSSIER`
   - `DUE_DILIGENCE`
3. **Organization identity and offering identity remain distinct.** Use a stable offering/product identity only when the product, platform, technology or service family is materially relevant across opportunities. Marketing labels alone do not justify new canonical product identities.
4. **Capability Fit, Eligibility Fit, Partnerability and Opportunity Match remain separate assessments.** Aggregate scores are advisory and cannot conceal hard eligibility blockers or confirmed partner conflicts.
5. **Market Landscape and Competitive Landscape remain distinct.** Market Landscape describes the broader market and solution space; Competitive Landscape is opportunity-relative and evidence-backed.
6. **Network Intelligence is a material relationship graph, not a general people database.** Collect person-level information only when legitimately relevant to the authorized commercial/intelligence objective. Do not infer private influence, political allegiance, corruption, hidden control or confidential relationships without competent evidence.
7. **Progressive narrowing is the default research strategy.** Broad discovery is shallow; deeper research is reserved for plausible candidates and shortlisted suppliers.
8. **Unknown and negative states remain distinct.** `NOT_FOUND`, `UNKNOWN`, `NEGATIVE_EVIDENCE`, and `CONTRADICTED` must not be collapsed. Absence of evidence is not a negative fact.
9. **Relationship Access means legitimate organizational access/readiness only.** It excludes improper influence, confidential procurement access and unauthorized personal leverage.

## Consequences

- Supplier research can remain fast at broad discovery scale without sacrificing quality on shortlisted candidates.
- External-provider identities cannot fragment the canonical supplier graph.
- Technical capability, procurement eligibility and commercial partnerability remain independently auditable.
- Market mapping can discover new suppliers without falsely treating every market participant as a live competitor.
- Network Intelligence remains useful for institutional and commercial context without drifting into unsupported influence analysis.
- Tests and schemas should preserve hard blockers, negative-evidence semantics and research-depth progression.

## Alternatives considered

### Separate supplier record per research depth
Rejected because depth is an investigative state, not a new entity identity.

### One aggregate supplier score
Rejected because a high aggregate can obscure disqualifying eligibility, export, channel or partner conflicts.

### Full dossier on every discovered supplier
Rejected because it imposes unnecessary latency and cost before basic fit is established.

### Treat every market participant as a competitor
Rejected because competitor status is opportunity-relative and requires evidence of plausible participation or positioning.

### Broad people/influence graph
Rejected because it creates privacy, evidentiary and governance risks and is unnecessary for the authorized commercial objective.
