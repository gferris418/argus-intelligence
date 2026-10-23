# ARGUS Domain Context

This file defines stable domain language only. Implementation details, workflow steps and design rationale belong in specifications or ADRs.

## Verification language

### Evidence Verification
ARGUS-domain evaluation of whether a claim is adequately supported by its evidence. It covers provenance, source authority, source-lineage independence, freshness, contradictions, claim type/condition, and evidence confidence. Evidence Verification does not authorize persistence or a business decision.

### Independent Assurance
ATLAS-governed evaluation of whether verified evidence is sufficient for a consequential governed decision, canonical acceptance, persistence authorization, or external action. Independent Assurance is separate from ARGUS Evidence Verification.

### Verification Substrate
A mandatory cross-cutting ARGUS capability used by consequential intelligence findings rather than an optional standalone collection mode. It may be invoked by horizon intelligence, project/package forecasting, tender intake, supplier intelligence, market intelligence, network intelligence, and other ARGUS collection work.

### Consequential Finding
An ARGUS finding capable of materially changing opportunity lifecycle state, procurement realization probability, supplier-match assessment, canonical mutation, monitoring priority, or the next ATLAS action.

### Claim
The atomic proposition evaluated by ARGUS Evidence Verification. A source may support multiple claims with different strength; verification therefore attaches to claims rather than treating an entire document or provider result as uniformly verified.

### Claim Type
The semantic nature of a claim: FACT, DERIVED, INFERENCE, ASSUMPTION, or UNKNOWN. Claim Type is independent of Verification State and Evidence Confidence.

### Verification State
ARGUS assessment of the current evidentiary status of a claim. Canonical states are SUPPORTED, PARTIALLY_SUPPORTED, UNRESOLVED, CONTRADICTED, and STALE.

### Evidence Confidence
A bounded assessment of how strongly the available evidence and reasoning support a claim. Evidence Confidence is distinct from Verification State, procurement probability, supplier-match confidence, business success probability, and ATLAS Independent Assurance.

### Source Lineage
The originating evidence chain behind a source or observation. Multiple URLs, publishers, or provider results that derive from the same originating evidence are one lineage for corroboration purposes.

### Independent Source Lineage
A source lineage whose evidentiary origin is materially independent of another lineage supporting or contradicting the same claim. Independence concerns origin and derivation, not merely different domains or publishers.

### Corroboration
Additional independent evidence that materially strengthens or challenges a claim. Corroboration is authority-sensitive: a competent primary authoritative source may establish a fact without a mechanical two-source requirement.

### Contradiction
A material incompatibility between claims or evidence that cannot be resolved by simple differences in wording, scope, time, or granularity. Contradictions remain explicit until discriminating evidence resolves them.

### Provider Confidence
A confidence or score emitted by an external provider. Provider Confidence is evidence about the provider output only and must not be treated as ARGUS Evidence Confidence or ATLAS Independent Assurance without ARGUS reconciliation and ATLAS governance.

### Verification Depth
The rigor applied to Evidence Verification, proportionate to consequence and uncertainty. Higher Verification Depth means stronger contradiction search, source-lineage testing, corroboration, primary-source reacquisition, falsification, and evidence-gap closure.
