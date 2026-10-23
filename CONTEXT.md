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

### Evidence Confidence
A bounded assessment of how strongly the available evidence and reasoning support a claim. Evidence Confidence is distinct from procurement probability, supplier-match confidence, business success probability, and ATLAS Independent Assurance.

### Provider Confidence
A confidence or score emitted by an external provider. Provider Confidence is evidence about the provider output only and must not be treated as ARGUS Evidence Confidence or ATLAS Independent Assurance without ARGUS reconciliation and ATLAS governance.
