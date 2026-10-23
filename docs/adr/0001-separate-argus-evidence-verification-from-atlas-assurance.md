# ADR 0001: Separate ARGUS Evidence Verification from ATLAS Independent Assurance

- **Status:** Accepted for Issue #76 design
- **Date:** 2026-10-23
- **Decision owners:** ATLAS governance / ARGUS intelligence architecture

## Context

ARGUS needs stronger source verification across horizon intelligence, project and procurement-package forecasting, tender intake, supplier intelligence, market intelligence and network intelligence. A single generic `verified=true` concept would collapse two different responsibilities:

1. whether evidence adequately supports an intelligence claim; and
2. whether that evidence is sufficient for a governed decision, canonical acceptance, persistence or external action.

External providers may also emit their own confidence scores, which creates another risk of conflating provider scoring with ARGUS evidence quality or ATLAS assurance.

## Decision

1. **ARGUS owns Evidence Verification.** It evaluates provenance, source authority, source-lineage independence, freshness, contradictions, claim type/condition, evidence gaps and evidence confidence.
2. **ATLAS owns Independent Assurance.** It decides whether verified evidence is sufficient for canonical acceptance, persistence authorization, consequential governed decisions and external actions.
3. `argus-source-verification` is a **mandatory cross-cutting substrate for consequential findings**, not merely an optional collection type.
4. Verification results use existing evidence/observation/finding lineage and mission-local verification state. **No new canonical record type is introduced** solely for verification.
5. Provider confidence is advisory input. It cannot automatically become ARGUS evidence confidence or ATLAS assurance.
6. Evidence confidence remains distinct from procurement realization probability, supplier-match confidence and business success probability.

## Consequences

- Horizon, forecasting, tender-intake and supplier workflows can share one verification vocabulary and contract.
- ARGUS can reject or qualify weak provider output without assuming ATLAS decision authority.
- ATLAS retains an independent governance gate instead of inheriting ARGUS or provider confidence mechanically.
- Existing canonical identity remains stable; verification enriches evidence lineage rather than creating competing identities.
- Contracts and tests must prohibit ambiguous generic verification flags where the verification/assurance distinction matters.

## Alternatives considered

### Verification entirely in ATLAS
Rejected because provenance reconciliation, source grading, contradiction handling and claim-level evidence quality are intrinsic to ARGUS collection work and must happen before provider return.

### Verification entirely in ARGUS
Rejected because canonical acceptance, persistence authorization and final governed action belong to the ATLAS control plane.

### Optional source-verification skill
Rejected because consequential findings from different ARGUS capabilities require consistent evidence treatment; an optional skill would allow bypass paths and semantic drift.

### New canonical VERIFICATION record type
Rejected because verification is evidence state and assessment attached to existing claims/observations, not a distinct real-world business object.
