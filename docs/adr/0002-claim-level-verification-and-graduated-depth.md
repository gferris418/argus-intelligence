# ADR 0002: Claim-Level Evidence Verification with Graduated Depth

- **Status:** Accepted for Issue #76 design
- **Date:** 2026-10-23
- **Decision owners:** ATLAS governance / ARGUS intelligence architecture

## Context

ARGUS must verify evidence consistently across horizon intelligence, project/package forecasting, tender intake, supplier intelligence, market intelligence and network intelligence. Verification must be rigorous enough to protect quality, but applying maximum-depth verification to every low-value discovery would unnecessarily degrade performance.

Document-level or provider-level verification is too coarse: one source can strongly establish one proposition while being weak, derivative or irrelevant for another. A mechanical two-source rule is also unreliable because multiple publishers may repeat the same originating evidence.

## Decision

1. **The atomic unit of ARGUS Evidence Verification is the claim.**
   - Sources receive provenance, authority, freshness and lineage characteristics.
   - Verification state and evidence confidence attach to claims.

2. **Claim Type and Verification State are separate dimensions.**
   - Claim Type: `FACT`, `DERIVED`, `INFERENCE`, `ASSUMPTION`, `UNKNOWN`.
   - Verification State: `SUPPORTED`, `PARTIALLY_SUPPORTED`, `UNRESOLVED`, `CONTRADICTED`, `STALE`.
   - A high-confidence inference does not become a fact merely because its confidence is high.

3. **Source independence is lineage-based, not URL- or publisher-based.**
   - Multiple reports derived from one originating source count as one evidence lineage.
   - Independent official, financing, procurement, technical or other evidentiary origins may count as separate lineages when genuinely independent.

4. **Corroboration is authority-sensitive rather than mechanically source-count-based.**
   - A competent primary authoritative source may establish a fact by itself.
   - Material secondary-source claims normally seek independent convergence.
   - Independent corroboration is required when the available source is materially ambiguous, interested, stale, derivative or contradicted.

5. **Contradictions remain explicit until resolved.**
   ARGUS may identify a preferred interpretation, but preserves competing claims, source lineages, the reason for preference, the discriminating question and the confidence impact. A material unresolved contradiction prevents full `SUPPORTED` status.

6. **Verification uses graduated depth.**
   - `V0_CAPTURE`: provenance and source identity.
   - `V1_SCREEN`: source authority, freshness and basic claim/source fit.
   - `V2_VERIFY`: contradiction search, source-lineage independence and corroboration.
   - `V3_CRITICAL`: competing hypotheses, primary-source reacquisition, explicit falsification and evidence-gap closure.

7. **Minimum depth is consequence-sensitive.**
   - Low-consequence discovery may remain at V0/V1.
   - A finding that materially changes opportunity, procurement, supplier or monitoring state must reach at least V2.
   - High-impact, irreversible or externally actionable findings should reach V3 before ATLAS Independent Assurance.

8. **Legacy `atlas_assurance` inside ARGUS evidence is compatibility-only.**
   New contracts distinguish ARGUS Evidence Verification from downstream ATLAS Independent Assurance. Compatibility adapters may map legacy results while the older domain-result contract remains supported.

## Consequences

- ARGUS can preserve quality without applying maximum-cost verification to every signal.
- Source-count inflation from syndication or copied reporting is reduced.
- Claim semantics remain distinct from evidence quality.
- Contradictions and uncertainty remain visible rather than being overwritten by the currently preferred source.
- Future capabilities can depend on one verification substrate instead of inventing their own confidence logic.
- Tests must cover lineage collapse, contradiction preservation, claim-type/state separation and minimum verification depth for consequential findings.

## Alternatives considered

### Document-level verification
Rejected because evidence strength varies by claim inside the same document.

### Provider-level trust score
Rejected because provider quality cannot establish the truth of every returned claim and would improperly collapse provider confidence into ARGUS evidence confidence.

### Mechanical two-source corroboration
Rejected because duplicate reporting can create false independence and because authoritative primary evidence may be sufficient on its own.

### Always run maximum-depth verification
Rejected because it would create avoidable latency and cost for low-consequence discovery while adding little decision value.

### Resolve contradictions by discarding the weaker source
Rejected because unresolved disagreement is itself decision-relevant intelligence and should remain auditable.
