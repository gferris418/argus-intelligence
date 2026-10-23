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

## Horizon and procurement language

### Horizon Intelligence
Cross-cutting ARGUS collection of upstream policy, strategy, institutional, programme, budget, funding, market and weak-signal evidence that may indicate an emerging government need, project, procurement path or commercial opportunity. Horizon Intelligence feeds existing Demand Intelligence, Early Warning and Opportunity Engine semantics; it is not a separate lifecycle or persistent engine.

### Weak Signal
An early, incomplete or low-resolution observation that may indicate an emerging need, programme, project, funding path, procurement path or opportunity but does not by itself establish that a canonical PROJECT or PROCUREMENT object exists.

### Tender Intake
The ARGUS normalization method for published solicitation and procurement-release evidence. Tender Intake resolves buyer, authority, project, package, procurement-process and requirement lineage, extracts material dates and requirements, invokes Evidence Verification, and reconciles the release against existing opportunity and procurement context. Tender Intake is used by Rapid Tender Mode rather than replacing it.

### Source Release
A dated, attributable publication or issuance of procurement-related source content, including an original solicitation, amendment, corrigendum, addendum, clarification, notice or other materially relevant release. Later releases do not erase earlier ones; current effective state is derived from the release/event history.

### Requirement Item
A stable child object representing a normalized obligation, eligibility condition, technical requirement, commercial condition, submission requirement, evaluation condition, local-partner or OEM-authorization requirement, or disqualifier whose satisfaction or interpretation can materially affect participation, compliance, evaluation or award. A Requirement Item belongs to procurement/package requirement lineage and is not initially a top-level master-registry record type.

### Requirement Lineage
The evidence-backed chain connecting upstream need or requirement context to programme/project, probable or observed procurement package, procurement process, Requirement Items, award/contract, installed base and successor or expansion signals. Not every node must exist, but later evidence should link backward where evidence supports the relationship.

### Forecast Basis Anchor
The canonical PROGRAMME, PROJECT, or REQUIREMENT object that establishes the evidence-bounded subject from which a procurement-package forecast is derived. A Forecast Basis Anchor does not prove that any future PROCUREMENT_PACKAGE exists.

## Supplier, market and network language

### Supplier Intelligence
The evidence-backed ARGUS intelligence overlay for a canonical ORGANIZATION acting or potentially acting as an OEM, supplier, contractor, solution provider or commercial partner. Research depth may increase over time without changing the underlying organization identity.

### Supplier Research Depth
The progressively deeper level of supplier research applied to the same canonical organization: DISCOVERY, FAST_QUALIFICATION, CAPABILITY_VALIDATION, FULL_DOSSIER, or DUE_DILIGENCE. Research Depth describes investigative rigor and completeness, not supplier status or identity.

### Capability Fit
Assessment of whether a supplier or offering can technically and operationally satisfy a defined requirement or opportunity scope. Capability Fit is distinct from Eligibility Fit, Partnerability and Opportunity Match.

### Eligibility Fit
Assessment of whether a supplier appears able to satisfy procurement-specific legal, procedural, qualification, authorization, certification, export, financial or other participation conditions. A hard eligibility blocker cannot be hidden by a high aggregate match score.

### Partnerability
Assessment of whether a supplier is commercially willing, available and structurally able to work with Access Asia for the relevant market or opportunity, including known channel conflicts, exclusivity, local-support expectations and legitimate relationship readiness.

### Opportunity Match
Opportunity-relative assessment of how well a particular supplier and, where relevant, a particular offering fit a specific commercial opportunity. Opportunity Match may aggregate advisory dimensions but remains separate from the supplier's canonical identity and from general Supplier Intelligence.

### Market Landscape
Evidence-backed description of the relevant market structure, including supplier classes, technologies, standards, substitutes, delivery models, price structures and other market dynamics. Presence in the Market Landscape does not by itself make an organization a competitor for a specific opportunity.

### Competitive Landscape
Opportunity-relative assessment of plausible competitors, their evidenced position, references, incumbency, channels, relevant offerings and likely advantages or disadvantages. Competitor status is contextual and evidence-backed rather than a permanent property of an organization.

### Network Intelligence
Evidence-backed representation of materially relevant relationships among institutions, organizations, projects, procurement entities, suppliers and persons where legitimately necessary for an authorized intelligence purpose. It does not infer private influence, political allegiance, corruption, hidden control or confidential relationships without competent evidence.

### Relationship Access
Legitimate organizational access or engagement readiness, such as an existing business relationship, known authorized contact, documented channel relationship or feasible professional engagement path. Relationship Access never means improper influence, privileged access to confidential procurement information or unauthorized personal leverage.

### Negative Evidence
Evidence that materially supports the conclusion that a claimed capability, qualification, relationship or condition does not exist or is unsuitable. Negative Evidence is distinct from NOT_FOUND, UNKNOWN and CONTRADICTED states; failure to locate evidence does not itself prove a negative fact.

## Capability and output language

### Native Capability
A versioned ARGUS analytical or collection capability with explicit ownership, method, input/output contract, verification requirement and ATLAS authority boundary. A Native Capability may be cross-cutting or may support one or more collection mission types; it does not create a new execution spine.

### Executable Capability
A Native Capability that can be invoked through the existing governed ARGUS runtime seam with machine-readable input/output validation and deterministic reconciliation. Analytical generation may use bounded reasoning or providers, but all results return through ARGUS validation and the ATLAS governance boundary.

### Intelligence Brief
A derived, evidence-backed ARGUS projection that organizes observations, inferences, assessments, confidence, contradictions/unknowns, commercial relevance, evidence gaps, next triggers and next collection questions. An Intelligence Brief is not a canonical business object and is not the final ATLAS user-facing decision or delivery.
