# ARGUS Core

**Version:** 2.0.0-rc.2  
**Status:** Candidate  
**Scope:** Pre-bid government and public-sector opportunity intelligence

## 1. Purpose

ARGUS identifies, develops, validates, reconciles, prioritizes and promotes government/public-sector opportunity intelligence before detailed supplier engagement, capture, bid preparation, contract execution or project delivery.

ARGUS is designed to answer, with evidence:

- What is likely to be procured?
- Why is it needed?
- Who owns, funds, procures, operates or uses the requirement?
- Which policy, programme, project, installed base, event or capability gap creates the need?
- How mature is the requirement?
- How mature are the project, funding and procurement paths?
- How close is procurement?
- What evidence supports the conclusion?
- What remains unknown, stale or conflicted?
- Have all materially relevant intelligence dimensions been examined?
- What research could still change the next commercial decision?
- Should Access Asia monitor, investigate, merge, promote, hold or reject the opportunity?
- What is the next commercially useful action?

## 2. Product boundary

ARGUS is a government opportunity-intelligence framework. It is not primarily:

- a generic memory system;
- an operating system;
- an ATLAS subsystem;
- a CRM;
- a tender portal;
- an email system;
- a document repository;
- a bid-management system;
- a project-management system;
- a proposal-writing system;
- a contract-delivery system;
- an indiscriminate data lake or surveillance platform.

Knowledge, provenance, monitoring, graphs, analytics and collection coverage support the intelligence mission but do not redefine the product.

## 3. Governing business principle

> Access Asia shall not wait for a tender to define an opportunity.

A formal tender is one evidence event in a longer lifecycle:

`Policy / Strategy / Need / Programme / Project / Funding / Procurement / Award / Installed Base / Replacement`

ARGUS works forward and backward across that chain and across related institutions, suppliers, consultants, financiers, technologies and historical procurements.

## 4. Production governance

Within the Access Asia governed environment, ATLAS OS is the execution-governance backbone.

ARGUS is independently specified and portable, but its production domain method executes inside the current ATLAS plan and execution spine. ARGUS does not create a second plan, scheduler, approval system, persistence model or output-delivery mechanism.

Canonical flow:

`ATLAS plan → ARGUS domain method → ARGUS domain result + proposed domain actions → ATLAS verification/approval → authorized action(s) → ATLAS task-artifact persistence → ATLAS delivery`

Standalone ARGUS execution is reserved for portability, testing, recovery or non-Access-Asia implementations.

## 5. Canonical operating loop

`Discover → Extract → Resolve → Reconcile → Validate → Assess → Prioritize → Decide → Promote/Monitor → Learn`

### Discover
Find relevant signals through one or more discovery vectors and materially relevant 360° collection lenses.

### Extract
Convert evidence into structured candidate facts, identifiers, actors, dates, values, scope and source references.

### Resolve
Determine whether observed entities, projects, procurements, suppliers or opportunities already exist.

### Reconcile
Compare observations with canonical records and determine match, duplicate, conflict, superseding update or new candidate.

### Validate
Assess provenance, source authority, freshness, contradictions, independence of source lineages and material unknowns.

### Assess
Evaluate opportunity-development maturity, independent decision dimensions and collection coverage.

### Prioritize
Use the Research Frontier to identify the unresolved question or collection gap most likely to change the next decision.

### Decide
Produce a domain decision and rationale.

### Promote / Monitor
Recommend PX promotion when justified, or retain the intelligence under governed research/monitoring.

### Learn
Capture reusable lessons, source-quality observations, aliases, patterns and post-mortems without rewriting historical evidence.

## 6. Architecture

ARGUS consists of:

1. **Core** — universal opportunity-intelligence method and semantics.
2. **Master Registry** — one logical structured-intelligence store.
3. **Country Profiles** — jurisdiction-specific institutions, sources, procurement routes and collection maps.
4. **Adapters** — replaceable interfaces to external systems.
5. **Alignment Contracts** — mappings to execution/governance environments such as ATLAS OS.
6. **Views / Consoles / Analytics** — non-authoritative presentation and analytical surfaces.

Applications adapt to ARGUS. ARGUS Core is not redesigned merely to fit an application.

## 7. Master Registry

ARGUS retains seven top-level record types:

| Record type | Purpose |
|---|---|
| `ENTITY` | Government/public-sector institutions, end users, PEs, project offices, consultants, financiers, regulators and related organizations |
| `PROJECT` | Programmes, projects, implementation vehicles, funding context, schedules and lineage |
| `PROCUREMENT` | Procurement plans, packages, RFIs/EOIs/PQs/RFPs/RFQs/tenders, amendments, cancellations, awards and contracts |
| `INTELLIGENCE` | Signals, hypotheses, validated needs, capability gaps, triggers and pre-PX candidates |
| `OPPORTUNITY` | Promoted Access Asia opportunities using the permanent PX identity |
| `SUPPLIER_PRODUCT` | OEM/supplier/consultant/product/service/capability/installed-base/contact intelligence |
| `KNOWLEDGE` | Reusable lessons, patterns, interpretations, aliases and post-mortems |

Minimum envelope:

`argus_id`, `record_type`, `canonical_name_or_title`, `status`, `related_argus_ids`, `evidence_refs`, `external_refs`, `created_at`, `updated_at`.

360° collection does **not** create an eighth record type. Coverage is assessment metadata attached to the relevant ARGUS result or record context.

## 8. Canonical ownership

Use one canonical owner per information class:

- ARGUS Master Registry — structured intelligence truth;
- communication system — communication truth;
- document repository — original document/evidence truth;
- CRM — active post-PX commercial-pursuit truth;
- governed framework repository / ATLAS Library — framework, alignment, decision and task artifacts;
- analytical engines — derived projections only;
- research tools — evidence sources, not canonical truth;
- monitoring tools — change detection, not opportunity authority.

**Rule:** store each item once in its natural canonical home and link elsewhere.

## 9. Discovery vectors

ARGUS supports converging discovery vectors, including:

- policy/top-down;
- product-to-buyer reverse discovery;
- procurement-backward;
- historical/installed-base;
- funding-led;
- ecosystem-led;
- trigger-event.

Independent convergence raises confidence but does not automatically establish procurement.

## 10. 360° Intelligence Collection Doctrine

### 10.1 Governing rule

ARGUS shall examine an opportunity through all **materially relevant** intelligence lenses rather than relying on one portal, one source class, one discovery direction or one institutional perspective.

The doctrine is:

> **360° breadth, decision-driven depth.**

360° collection is not exhaustive data gathering. Its purpose is to make material coverage, gaps, conflicts and source independence visible so that research effort is directed only where it can affect the commercial decision.

### 10.2 Core collection lenses

ARGUS defines twelve universal collection lenses:

1. `need_mission` — the mission, capability gap, operational/business need or public-service requirement.
2. `policy_strategy` — policy, strategy, mandate, modernization plan, regulation or institutional priority creating demand.
3. `institution_stakeholders` — owner, sponsor, approver, end user, operator, procuring entity, influencer and other material actors.
4. `programme_project` — programme, project, implementation vehicle, initiative or acquisition context through which the need may be delivered.
5. `budget_funding` — budget source, allocation, financing, donor/lender/G2G support and funding maturity.
6. `procurement_acquisition` — procurement route, plan, package, acquisition mechanism, pre-procurement activity, tender and award path.
7. `technical_installed_base` — current systems, specifications, age, lifecycle, capacity, obsolescence, interoperability and replacement/expansion context.
8. `supplier_competitor` — incumbents, OEMs, competing suppliers, competing technologies, prior bidders and historical awards.
9. `ecosystem_influence` — consultants, EPCs, integrators, advisers, donors, lenders, local partners and other actors capable of shaping the requirement or procurement path.
10. `commercial_participation` — eligibility, representation/JV/local-partner issues, enlistment, export/end-use, service obligations, payment/import constraints and other commercial-entry conditions.
11. `timing_triggers` — events that accelerate, delay, cancel, revive, replace or expand an opportunity.
12. `internal_intelligence` — Access Asia's prior correspondence, meetings, proposals, quotations, project history, relationships and lessons relevant to the opportunity.

Country profiles map these universal lenses to jurisdiction-specific institutions, sources, terminology and collection routes.

### 10.3 Coverage states

Each materially relevant lens may be assessed as:

- `NOT_APPLICABLE` — the lens is not material to the current decision.
- `UNASSESSED` — the lens has not yet been materially examined.
- `INSUFFICIENT` — collection occurred but evidence is too weak or incomplete for the current decision.
- `PARTIAL` — useful evidence exists, but a material gap or uncertainty remains.
- `ADEQUATE` — coverage is sufficient for the current decision, without implying exhaustive knowledge.

Coverage is decision-relative. `ADEQUATE` does not mean complete, and an opportunity does not require every lens to be `ADEQUATE` before ARGUS may decide.

### 10.4 Collection gaps

ARGUS records decision-relevant collection gaps separately from general unknowns. A gap should identify:

- lens;
- missing or conflicted information;
- why it matters;
- likely decision impact;
- next collection question or trigger where useful.

The Research Frontier ranks material collection gaps by expected decision value.

### 10.5 Source diversity and convergence

ARGUS distinguishes **source count** from **independent source lineages**.

Ten pages reproducing one original notice are one evidentiary lineage, not ten independent confirmations.

Where a claim is material, ARGUS should prefer independent convergence across competent source classes when proportionate, for example official transaction evidence + project/funding evidence + internal history + independent supplier/ecosystem evidence.

Single-source dependence is permitted only when the source is sufficiently authoritative for the claim or when additional independent confirmation would not materially affect the decision.

### 10.6 Internal-first collection

360° collection does not mean external-first collection. ARGUS should reuse authorized internal intelligence before duplicating external research.

Typical order:

`ARGUS Registry → existing PX/opportunities → communications → documents → supplier/product/installed-base history → knowledge/prior research → external collection appropriate to the task`

### 10.7 Proportionality and stopping rule

The breadth of assessment should cover all materially relevant lenses; the depth of collection is controlled by the Research Frontier.

Stop expanding collection when additional work is unlikely to change:

- the reality of the signal;
- I0–I9 maturity;
- route/institution/funding/procurement interpretation;
- merge/new-candidate judgment;
- `MONITOR`, `INVESTIGATE`, `PROMOTE_TO_PX`, `MERGE_EXISTING`, `HOLD` or `REJECT`;
- next action or next material trigger.

A weak early signal may justify only a few lens checks. A promotion recommendation may require broader coverage. A live tender may not require reconstructing every historical policy source when that work would not change the current decision.

## 11. Identity and reconciliation

Identity states:

- `EXACT`
- `HIGH_CONFIDENCE_MATCH`
- `PROBABLE_MATCH`
- `UNRESOLVED`
- `DISTINCT`

Only `EXACT` and sufficiently evidenced `HIGH_CONFIDENCE_MATCH` should normally auto-merge.

Procurement reconciliation outcomes:

- `MATCHED_EXISTING`
- `PROBABLE_EXISTING`
- `POSSIBLE_EXISTING`
- `NEW_CANDIDATE`
- `DUPLICATE`
- `SUPERSEDING_UPDATE`

A new document, tender, amendment or award does not automatically create a new commercial opportunity.

## 12. Evidence semantics

ARGUS separates **claim type**, **claim condition** and **collection coverage**.

Claim type:

- `FACT`
- `DERIVED`
- `INFERENCE`
- `ASSUMPTION`
- `UNKNOWN`

Claim condition:

- `CURRENT`
- `STALE`
- `CONFLICT`

Collection coverage:

- `NOT_APPLICABLE`
- `UNASSESSED`
- `INSUFFICIENT`
- `PARTIAL`
- `ADEQUATE`

Where ATLAS governs execution, ATLAS applies its own evidence assurance and health independently. ARGUS `FACT` never means ATLAS `VERIFIED` automatically, and `ADEQUATE` coverage never means the underlying claims are verified.

Every material decision must remain traceable to evidence. Contradictory evidence is preserved rather than silently overwritten.

## 13. Opportunity-development maturity

I0–I9 is an **opportunity-development maturity index**, not task progress, probability of winning, evidence confidence, collection completeness, project stage, funding stage or procurement stage alone.

| Level | State | Meaning |
|---|---|---|
| I0 | Signal | Potentially relevant observation |
| I1 | Hypothesis | Plausible public-sector requirement or procurement implication |
| I2 | Validated Need | Credible need/capability gap supported by evidence |
| I3 | Institutional Path | Owner/end-user/programme/institutional chain materially understood |
| I4 | Delivery/Funding Path | Credible project, budget, financing, acquisition or implementation route exists |
| I5 | Actionable Context | Sufficiently identifiable project/programme/budget/acquisition context for focused pursuit intelligence |
| I6 | Procurement Planning | Procurement plan/package/specification planning is evidenced |
| I7 | Pre-Procurement | Concrete pre-solicitation activity exists |
| I8 | Procurement Imminent | Strong evidence formal procurement is near |
| I9 | Live | Formal procurement/solicitation published |

Assess separately where material:

- project/implementation state;
- funding state;
- procurement state;
- evidence confidence;
- collection coverage;
- commercial attractiveness;
- procurement horizon;
- strategic fit;
- blockers and unknowns.

## 14. Research Frontier

Maintain only decision-relevant unresolved questions and collection gaps.

A question belongs in the Research Frontier when its answer may materially change the reality of the signal, maturity, timing, institutional path, funding path, procurement path, commercial attractiveness, duplicate/merge result, promotion decision or next action.

The 360° coverage matrix exposes gaps; the Research Frontier decides which gaps deserve further work.

Stop expanding a research branch when additional evidence is unlikely to change the next decision.

When ATLAS governs execution, the Research Frontier proposes the domain research priority; ATLAS owns work-unit creation, routing and execution timing.

## 15. Domain decisions

ARGUS domain decisions are:

- `MONITOR`
- `INVESTIGATE`
- `PROMOTE_TO_PX`
- `MERGE_EXISTING`
- `HOLD`
- `REJECT`

A decision is analytical. Any state mutation is a separate proposed domain action.

`PROMOTE_TO_PX` recommends promotion; it does not itself create the permanent PX identity.

## 16. Domain result contract

ARGUS returns a structured domain result to the governing runtime. It is not automatically the final user-facing answer.

The result contains, proportionately:

- objective;
- candidate/opportunity;
- domain decision;
- I0–I9 maturity;
- institutional chain;
- project/funding/procurement state;
- commercial relevance;
- evidence and provenance;
- 360° collection coverage where material;
- collection gaps where material;
- unknowns/conflicts;
- Research Frontier;
- next material trigger;
- next recommended action;
- proposed domain/registry actions.

The machine-readable contract is defined in `schemas/domain-result.schema.json`.

## 17. Domain actions and persistence

ARGUS structured-intelligence writes occur through the governed `RegistryStoreAdapter` / Registry API.

An ARGUS Registry mutation is a domain action, not ATLAS task-library persistence.

Under ATLAS governance:

1. ARGUS produces the domain result and proposed action.
2. ATLAS performs authorization/approval and pre-action checks.
3. The governed adapter executes the domain mutation.
4. ATLAS verifies the action result.
5. ATLAS separately persists the task report/decision/receipt under its own persistence contract.
6. ATLAS delivers the verified result.

Saving a report to a Library never proves that the Master Registry changed.

## 18. PX promotion and downstream handoff

Only promoted opportunities receive the permanent Access Asia `YYYY_PX####_SHORTNAME` identity.

Permanent PX creation, destructive merge or another major canonical-state change uses the governing runtime's approval controls where applicable.

After promotion, downstream CRM/workflows reuse the permanent PX identity and canonical references rather than creating a competing identity.

ARGUS does not own detailed capture, bid/no-bid, tender compliance, proposal preparation, pricing, submission, contract administration, project execution, invoicing, warranty or closeout.

## 19. Monitoring

Monitoring detects changes; it does not create opportunities directly.

Monitoring should be event- and lens-aware. Triggers may target funding changes, project approvals, procurement notices, technical obsolescence, institutional changes, consultant appointments, supplier moves, policy changes or other material events.

A detected event re-enters normal ARGUS resolution, reconciliation, validation, assessment and decision logic.

## 20. Portability

ARGUS requires stable ARGUS-owned IDs, vendor-neutral record definitions, external vendor IDs only as references, portable relationships and provenance, and open export formats.

A platform migration is an implementation change, not a Core redesign.

## 21. Capability boundary test

Before adding any feature, tool, database, workflow or application, ask:

1. Does an existing ARGUS capability already cover it?
2. Can it be an adapter, view or analytical projection instead of Core?
3. Will it create a competing source of truth?
4. Will identifiers and data remain portable?
5. Does it materially improve opportunity intelligence or a commercial decision?
6. Does it belong pre-PX or downstream?
7. Is ARGUS the correct owner?
8. Does the feature improve 360° coverage, evidence quality, reconciliation or decision quality without encouraging indiscriminate collection?

If not, keep it outside ARGUS Core.
