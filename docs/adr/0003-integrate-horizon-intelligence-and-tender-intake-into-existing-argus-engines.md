# ADR 0003: Integrate Horizon Intelligence and Tender Intake into Existing ARGUS Engines

- **Status:** Accepted for Issue #76 design
- **Date:** 2026-10-23
- **Decision owners:** ATLAS governance / ARGUS intelligence architecture

## Context

ARGUS already has persistent Demand Intelligence, Opportunity Engine and Early Warning capabilities, plus `event_driven_early_warning`, `rapid_tender_mode`, canonical procurement identity and requirement lineage. Adding horizon scanning and tender intake as independent engines would duplicate lifecycle, routing and state semantics.

ARGUS also needs to preserve the distinction between weak early signals and authoritative project/procurement facts, while allowing published tenders and subsequent amendments to reconcile into existing opportunities and procurement history.

## Decision

1. **Horizon Intelligence is a cross-cutting collection method, not a sixth persistent engine.**
   It spans Demand Intelligence and Early Warning and feeds the existing Opportunity Engine and S0-S9 lifecycle.

2. **Weak signals do not establish canonical project or procurement facts by themselves.**
   A weak signal may create or strengthen evidence observations, need/requirement hypotheses, sufficiently distinct early commercial opportunity hypotheses, monitoring signposts and research questions.

3. **PESTLE is an optional coverage lens only.**
   It may be used where macro political, economic, social, technological, legal or environmental factors materially affect the opportunity. It is not a lifecycle, ontology, scoring model or mandatory six-section template.

4. **Tender Intake is the normalized ingestion method used by Rapid Tender Mode.**
   It does not replace Rapid Tender Mode and a tender does not automatically create a new opportunity.

5. **Tender Intake follows the existing ARGUS path.**
   Source release -> Tender Intake -> Evidence Verification -> identity resolution -> opportunity/procurement reconciliation -> S0-S9 context update -> ATLAS provider return.

6. **Procurement source releases are immutable historical events.**
   Amendments, corrigenda, addenda and clarifications are new Source Releases. The current effective procurement view is derived from release history rather than overwriting prior state.

7. **Requirement Items are stable child objects under existing procurement/package requirement lineage.**
   They receive durable identity and history but do not initially become a new top-level master-registry record type.

8. **Requirement Item scope is decision-relevant.**
   It covers normalized obligations or conditions capable of materially affecting participation, compliance, evaluation or award, including eligibility, qualification, technical, commercial, legal/contractual, submission, evaluation, local-partner, OEM-authorization and disqualifier categories.

9. **One continuous requirement lineage is preserved where evidence supports it.**
   Policy/strategy signal -> need/requirement -> programme/project -> probable package hypothesis -> observed package -> procurement process/tender -> Requirement Items -> award/contract -> installed base -> successor/expansion signal.

## Consequences

- ARGUS avoids duplicate engines and parallel lifecycles.
- Early signals remain useful without being promoted prematurely to project/procurement fact.
- Rapid Tender Mode gains a precise normalization method.
- Amendments remain auditable and historical state is preserved.
- Tender requirements can be tracked precisely without expanding the master-registry type system prematurely.
- Forecast package hypotheses can reconcile naturally into observed package and tender evidence.

## Alternatives considered

### Add Horizon Intelligence as a sixth engine
Rejected because upstream scanning already belongs across Demand Intelligence and Early Warning; a new engine would duplicate collection and lifecycle semantics.

### Let any tender create an opportunity automatically
Rejected because one opportunity may span multiple procurements, rebids and follow-ons, and a tender may belong to an existing opportunity.

### Overwrite tender state when amendments arrive
Rejected because prior releases are evidentiary history and may be necessary to reconstruct deadlines, scope changes and compliance evolution.

### Make Requirement Item a new top-level canonical type immediately
Rejected because stable child identity and lineage solve the current need without expanding canonical record taxonomy before independent justification exists.
