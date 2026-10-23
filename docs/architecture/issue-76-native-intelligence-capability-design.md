# ARGUS Issue #76 — Native Intelligence Capability Design

- **Status:** Design approved; implementation not yet authorized
- **Date:** 2026-10-23
- **Branch:** `design/issue-76-verification-boundary`
- **Primary lifecycle:** S0–S9
- **Compatibility lifecycle:** I0–I9 only
- **Control plane:** ATLAS OS
- **Provider boundary:** ARGUS is a bounded intelligence provider and always returns to ATLAS

## 1. Objective

Issue #76 strengthens ARGUS as an early government-commercial intelligence system without creating a competing execution architecture. The target operating model detects needs and opportunities as early as public evidence permits, verifies the evidence, resolves canonical identity and lineage, forecasts probable procurement structure without fabricating procurement facts, identifies suitable international suppliers and produces decision-ready intelligence for ATLAS.

The design adds native methods for:

- Evidence Verification;
- Horizon Intelligence;
- Tender Intake;
- Entity Resolution strengthening;
- progressive Supplier Intelligence;
- Market Landscape;
- Competitive Landscape;
- Network Intelligence;
- Intelligence Brief output;
- repaired Procurement Package Forecasting integration.

## 2. Governance boundary

### ARGUS owns

- source discovery, acquisition, extraction and normalization;
- evidence provenance and source-lineage analysis;
- claim-level Evidence Verification;
- corroboration and contradiction search;
- entity/event/relationship resolution;
- early opportunity identity and S0–S9 tracking;
- Horizon Intelligence;
- Tender Intake;
- procurement-package hypothesis generation;
- supplier-universe construction;
- supplier capability, eligibility and partnerability assessment;
- market, competitive and network intelligence;
- advisory supplier matching and qualification;
- structured intelligence packaging and derived Intelligence Briefs.

### ATLAS owns

- Mission Control and the control plane;
- routing and activation;
- permissions and approvals;
- canonical evidence acceptance;
- Independent Assurance;
- persistence authorization;
- authoritative forecasting and scenario decisions;
- authoritative commercial priority;
- PROMOTE_TO_PX, pursuit and bid/no-bid decisions;
- external outreach authorization;
- provider-return reconciliation;
- all next-step authority and final delivery.

**Invariant:** ARGUS Evidence Verification does not equal ATLAS Independent Assurance.

## 3. Evidence Verification substrate

Evidence Verification is a mandatory cross-cutting ARGUS substrate for consequential findings.

### 3.1 Atomic unit

The atomic unit is the **Claim**, not the document, provider or URL.

A source receives provenance, authority, freshness and lineage characteristics. The claim receives verification state and evidence confidence.

### 3.2 Claim dimensions

Claim Type remains:

- `FACT`
- `DERIVED`
- `INFERENCE`
- `ASSUMPTION`
- `UNKNOWN`

Verification State is separate:

- `SUPPORTED`
- `PARTIALLY_SUPPORTED`
- `UNRESOLVED`
- `CONTRADICTED`
- `STALE`

A highly confident inference never becomes a fact merely because confidence is high.

### 3.3 Source independence

Independence is based on **originating evidence lineage**, not URL count or publisher count.

Example:

`Ministry release → newspaper A → newspaper B`

is one lineage.

A ministry project document, a finance-ministry budget and an independently issued development-partner procurement plan may be distinct lineages when they genuinely arise from independent evidentiary origins.

### 3.4 Corroboration policy

No mechanical two-source rule applies.

- a competent primary authoritative source may establish a fact;
- material secondary-source claims normally seek independent convergence;
- independent corroboration is required where the available source is ambiguous, interested, derivative, stale or contradicted.

### 3.5 Contradictions

ARGUS preserves material contradictions explicitly. It may state a preferred interpretation, but retains:

- the competing claims;
- supporting source lineages;
- the reason one interpretation is preferred;
- the unresolved discriminating question;
- the confidence impact.

A material unresolved contradiction prevents full `SUPPORTED` status.

### 3.6 Verification depth

- `V0_CAPTURE` — provenance and source identity.
- `V1_SCREEN` — source authority, freshness and basic claim/source fit.
- `V2_VERIFY` — contradiction search, lineage independence and corroboration.
- `V3_CRITICAL` — competing hypotheses, primary-source reacquisition, explicit falsification and evidence-gap closure.

Low-consequence discovery may remain V0/V1. A consequential finding must reach at least V2. High-impact, irreversible or externally actionable findings should reach V3 before ATLAS Independent Assurance.

### 3.7 Machine-readable finding model

New finding contracts should carry an optional `verification` block containing at least:

- state;
- depth;
- evidence confidence;
- source lineages;
- independent lineage count;
- contradiction references;
- verification timestamp;
- evidence gaps.

The block becomes mandatory for Consequential Findings. Legacy `claim_condition` remains compatibility-only during migration and must not disagree with the new verification model.

## 4. Horizon Intelligence

Horizon Intelligence is not a sixth persistent engine. It is a cross-cutting collection method spanning Demand Intelligence and Early Warning and feeding the existing Opportunity Engine.

It scans upstream evidence including:

- policy and strategy;
- institutional plans and capability gaps;
- programmes and projects;
- budgets and funding;
- development-partner pipelines;
- approvals and committees;
- market and technical signals;
- implementation and installed-base signals;
- procurement emergence indicators.

### 4.1 Weak signals

A weak signal may create or strengthen:

- an observation;
- a need/requirement hypothesis;
- an early commercial opportunity hypothesis when sufficiently distinct;
- monitoring signposts;
- research-frontier questions.

A weak signal does not establish that a canonical `PROJECT` or `PROCUREMENT` object exists.

### 4.2 PESTLE

PESTLE is an optional macro collection lens only. It is not an ontology, lifecycle, scoring system or control model.

ARGUS-specific lineage lenses remain primary:

`policy/strategy → institution → programme/project → budget/funding → procurement → installed base → supplier/market → triggers`

## 5. Tender Intake and Rapid Tender Mode

Tender Intake is the normalized ingestion method used by existing Rapid Tender Mode. It does not replace Rapid Tender Mode and does not create a parallel lifecycle.

Path:

`source release → Tender Intake → Evidence Verification → identity resolution → opportunity reconciliation → S0–S9 update → ATLAS return`

A tender does not automatically create a new opportunity.

### 5.1 Source releases

Original solicitations, amendments, corrigenda, addenda, clarifications and other material releases are immutable dated source events. Later releases update the current effective view without erasing earlier state.

### 5.2 Requirement Items

A Requirement Item is a stable child object representing a material obligation or condition that could affect participation, compliance, evaluation or award.

Recommended classes:

- `ELIGIBILITY`
- `QUALIFICATION`
- `TECHNICAL`
- `COMMERCIAL`
- `LEGAL_CONTRACTUAL`
- `SUBMISSION`
- `EVALUATION`
- `LOCAL_PARTNER`
- `OEM_AUTHORIZATION`
- `DISQUALIFIER`
- `OTHER`

Each item should preserve source-release and clause/page provenance, normalized meaning, obligation level, responsible party, evidence needed, deadline where applicable, verification state and unresolved interpretation.

Requirement Items receive stable IDs but are not initially promoted to a new top-level master-registry canonical type.

## 6. Continuous lineage

ARGUS maintains evidence-backed lineage across the commercial lifecycle where evidence supports the links:

`POLICY / STRATEGY`
→ `PROGRAMME`
→ `PROJECT`
→ `REQUIREMENT`
→ `PROCUREMENT_PLAN`
→ probable package hypothesis
→ `PROCUREMENT_PACKAGE`
→ `PROCUREMENT_PROCESS`
→ `SOLICITATION`
→ Requirement Items / lots / items
→ `AWARD`
→ `CONTRACT`
→ installed base
→ successor / expansion signal

Not every opportunity must populate every node.

## 7. Procurement Package Forecasting repair

PR #75 established the method, schema and collection-package field but requires integration repair.

### 7.1 Forecast basis anchor

New forecasts use an authoritative `basis_anchor`:

```yaml
basis_anchor:
  object_type: PROGRAMME | PROJECT | REQUIREMENT
  canonical_ref: <ARGUS canonical ID>
```

`project_ref` may remain for one compatibility release but is no longer the only authoritative anchor.

An anchor establishes the evidenced subject of the forecast; it does not prove that any future package exists.

### 7.2 Semantic repairs

Implementation must:

- reject `minimum > maximum` in numeric ranges;
- validate timing according to declared precision;
- tighten estimated-value structure;
- require hypotheses in `ACTIVE_HYPOTHESIS` state;
- require correct reconciliation when a hypothesis is `REALIZED`;
- constrain collection-package forecast items with the forecast schema;
- preserve realization probability separately from evidence confidence;
- preserve the rule that forecast hypotheses never become canonical facts through probability alone.

## 8. Supplier and Entity Intelligence

Supplier Intelligence is an evidence-backed overlay on a canonical `ORGANIZATION`.

Provider IDs, CRM IDs, domains, LinkedIn IDs and database IDs are aliases or evidence, never canonical identity authority.

Legal entity, parent company, subsidiary and business-unit distinctions must be resolved before merging.

### 8.1 Progressive supplier research

Research depth progresses on the same organization identity:

1. `DISCOVERY`
2. `FAST_QUALIFICATION`
3. `CAPABILITY_VALIDATION`
4. `FULL_DOSSIER`
5. `DUE_DILIGENCE`

Broad discovery remains shallow; deeper research is reserved for plausible candidates and serious shortlist suppliers.

### 8.2 Separate supplier assessments

Keep these dimensions distinct:

- **Capability Fit** — can the supplier technically and operationally deliver?
- **Eligibility Fit** — can the supplier qualify for the relevant procurement?
- **Partnerability** — can and will the supplier legitimately work with Access Asia?
- **Opportunity Match** — how well does this supplier/offering fit this specific opportunity?

A weighted advisory score cannot hide a hard eligibility blocker or confirmed partner conflict.

### 8.3 Product/offering identity

Organization identity and offering identity remain separate. Use canonical `PRODUCT` / supplier-product identity only when a product, platform, technology or service family is material enough to require stable cross-opportunity identity.

## 9. Market, Competitive and Network Intelligence

### Market Landscape

Describes technologies, supplier classes, standards, substitutes, delivery models, price structures and market dynamics.

### Competitive Landscape

Opportunity-relative assessment of plausible competitors, evidenced position, references, incumbency, channels, relevant offerings and likely advantages/disadvantages.

A market participant is not automatically a competitor.

### Network Intelligence

Represents materially relevant, evidence-backed relationships among institutions, organizations, projects, procurement entities, suppliers and persons when legitimately required for the authorized question.

It may represent authority, ownership, implementation, advisory role, representation, partnership, contract, reference project, installed base or public professional affiliation.

It must not infer improper influence, political allegiance, corruption, hidden control, confidential relationships or private leverage without competent evidence.

### Relationship Access

Relationship Access means legitimate organizational access/readiness: an existing business relationship, authorized contact, documented channel or feasible professional engagement path. It never means improper influence or privileged procurement information.

## 10. Unknown and negative states

Supplier and market research must distinguish:

- `NOT_FOUND` — research did not locate supporting evidence;
- `UNKNOWN` — unresolved;
- `NEGATIVE_EVIDENCE` — evidence supports absence/unsuitability;
- `CONTRADICTED` — material sources conflict.

Absence of evidence is not automatically evidence of absence.

## 11. Intelligence Brief

`argus-intelligence-brief` is a derived projection, not a new canonical object.

Structured sections:

1. Observations
2. Inferences
3. Assessments
4. Confidence
5. Contradictions / Unknowns
6. Commercial Relevance
7. Evidence Gaps
8. Next Triggers
9. Next Collection Questions

ATLAS remains free to render, combine, shorten or suppress this projection for final delivery.

## 12. Native Capability Registry

ARGUS will add one machine-readable Native Capability Registry. Every registered capability declares:

- capability ID;
- version;
- status;
- owning engine(s);
- method/profile or handler;
- input contract;
- output contract;
- minimum Evidence Verification depth;
- provider boundary;
- cross-cutting vs collection-mission role;
- ATLAS authority boundary.

Registration does not create a new collection type automatically.

## 13. Runtime architecture

ARGUS retains one governed runtime seam. Capabilities do not receive separate runtimes, agents, approval planes, persistence authorities or lifecycles.

An Executable Capability is a callable method/handler with:

- machine-readable inputs/outputs;
- deterministic contract validation;
- semantic validation and reconciliation;
- tests;
- governed return through ATLAS.

Reasoning-heavy analytical generation may use bounded model/provider reasoning. Deterministic code validates and reconciles outputs and enforces invariants.

## 14. Implementation sequence

### Foundation

**PR-A — Forecasting repair + capability registry**
- repair PR #75 contract/schema/runtime wiring;
- add Native Capability Registry;
- correct ownership terminology;
- add verification model to collection findings;
- index architecture documentation.

### P0

**PR-B — Evidence Verification substrate**

**PR-C — Horizon Intelligence**

**PR-D — Tender Intake**

### P1

**PR-E — Entity Resolution + progressive Supplier Intelligence**

**PR-F — Market + Competitive + Network Intelligence**

### P2

**PR-G — Intelligence Brief + E2E calibration**

Every PR follows tests-first development and independent verification before completion.

## 15. End-to-end acceptance fixtures

Issue #76 cannot close without at least three end-to-end cases:

### A. Pre-tender discovery

`upstream policy/project signal → requirement hypothesis → verified project/programme context → package forecast → monitoring signposts`

### B. Rapid tender recovery

`tender first → intake → canonical identity reconciliation → requirement extraction → supplier universe → shortlist/match → ATLAS return`

Reuse the Bangladesh Coast Guard CPV scenario where useful.

### C. Contradictory evidence

`conflicting sources → V2/V3 Evidence Verification → contradiction preservation → qualified/unresolved assessment`

The system must demonstrate that it does not convert disagreement into false certainty.

## 16. Explicit non-goals

Issue #76 does not:

- replace ATLAS;
- create another control plane;
- create a sixth persistent ARGUS engine;
- replace S0–S9;
- reinstate I0–I9 as primary;
- make provider confidence authoritative;
- turn probability into canonical procurement fact;
- merge proposal/RFP response generation into early intelligence;
- authorize external outreach;
- create a top-level canonical type for every analytical object;
- infer improper influence or confidential relationships.

## 17. Design completion gate

The design tree is complete. No implementation should begin until the user confirms this consolidated architecture as the shared understanding. After confirmation, the next step is to convert this approved design into a buildable technical specification and dependency-ordered implementation tickets/PRs.
