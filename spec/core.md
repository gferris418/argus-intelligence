# ARGUS Core

**Version:** 2.1.0-rc.1  
**Status:** Candidate  
**Scope:** Government and public-sector commercial opportunity intelligence

## 1. Purpose

ARGUS identifies, develops, validates, reconciles, prioritizes and promotes government/public-sector opportunity intelligence before and through formal procurement, while preserving a continuous evidence-backed lineage from policy/need to project, procurement, supplier strategy and follow-on opportunity.

ARGUS is designed to answer, with evidence:

- What is likely to be procured?
- Why is it needed?
- Who owns, funds, procures, operates or uses the requirement?
- Where does the buyer sit in the government hierarchy?
- Which policy, programme, project, installed base, event or capability gap creates the need?
- Does the requirement or opportunity already exist in the internal canonical registry?
- Has an authoritative procurement signal been published?
- What does Access Asia already know from authorized internal customer intelligence?
- Which products, OEMs, suppliers, competitors and delivery models are relevant?
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

ARGUS is a government commercial-opportunity intelligence framework. It is not primarily:

- a generic memory system;
- an operating system;
- a second orchestration/control plane;
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

## 4. Production governance and ATLAS handoff

Within the Access Asia governed environment, ATLAS OS is the execution-governance backbone.

ATLAS owns generic intent/target interpretation, taxonomy references, material risk flags, mission authorization, approvals, persistence authorization, verification and final delivery. Before substantive ARGUS execution, ATLAS transfers the governed domain context plus one bounded collection mission.

ARGUS must not redefine ATLAS taxonomy, approval, security or persistence conclusions. ARGUS may enrich the mission for government-commercial intelligence: institutional hierarchy, terminology, aliases, solution adjacency, local context, installed base, supplier/competitor relationships, procurement routes, commercial meaning and discovery semantics.

The handoff is mandatory in Access Asia production. ARGUS validates the pinned handoff and collection-mission schemas, preserves unresolved facets and risk flags, rejects `BLOCKED` handoffs for dependent execution, and returns the exact handoff correlation in the domain result.

Normal execution uses **one handoff and one return**:

`ATLAS understand/normalize/frame/route → ATLAS governed handoff + collection mission → ARGUS bounded-autonomous investigation → ARGUS domain result + proposed batched mutation → ATLAS verify/approve/persist → ATLAS delivery`

ARGUS does not return to ATLAS for routine research choices. Within an accepted mission and lease, ARGUS may follow evidence leads, choose lawful source routes, resolve identities, search official procurement sources, inspect authorized internal intelligence, investigate suppliers/products/competitors and continue decision-relevant research until the stopping rule is met.

ARGUS escalates before normal return only when one of these conditions is material:

- `MATERIAL_SCOPE_CHANGE` — evidence shows the mission target itself must materially change;
- `AUTHORIZATION_REQUIRED` — a consequential external action or governed mutation requires ATLAS approval/authorization;
- `POLICY_OR_SECURITY_CONFLICT` — policy, legal, security or access controls prohibit or constrain the next action;
- `MATERIAL_AMBIGUITY` — continuing would risk investigating or mutating the wrong real-world object.

Unknown project IDs, budgets, quantities, technical specifications, suppliers, procurement routes or lifecycle states are research questions, not callback triggers by themselves.

Standalone ARGUS execution is reserved for portability, testing, recovery or non-Access-Asia implementations.

The preferred executable interface is `Argus.analyze(AnalysisEnvelope)`. It owns the governed synchronization lifecycle and protected result correlation around an injected ARGUS domain method. Lower-level synchronization functions remain available for recovery, retry/resume, authorization and compatible integrations; callers should not manually recreate the standard path.

## 5. Canonical operating model

### 5.1 Institution-first autonomous startup

For a government-commercial target, ARGUS performs this deterministic startup before broad collection:

1. `RESOLVE_INSTITUTIONAL_HIERARCHY` — resolve country → ministry/division → agency/authority → subordinate unit/project office/procuring entity → end user/operator where evidence supports the chain.
2. `CHECK_INTERNAL_CANONICAL_REGISTRY` — search the current ARGUS registry for the buyer, requirement, project, procurement, tender and opportunity using official identifiers first and progressively weaker identity evidence only when needed.
3. `RECONCILE_OPPORTUNITY_IDENTITY` — decide whether the observation is an existing object, a clearly distinct new candidate, or materially ambiguous.
4. `CHECK_OFFICIAL_PROCUREMENT_SOURCES` — determine whether the requirement has become externally visible in the applicable authority/platform/agency/development-partner channels.
5. `CHECK_INTERNAL_CUSTOMER_INTELLIGENCE` — inspect authorized Access Asia customer intelligence, working files, CRM relationship context, prior meetings/correspondence/proposals/quotations and relevant historical records without duplicating their canonical masters.
6. `BUILD_RESEARCH_FRONTIER` — reconcile public and internal evidence, contradictions and material unknowns; rank gaps by expected decision impact.
7. `EXECUTE_ADAPTIVE_360_COLLECTION` — activate only the intelligence capabilities that can materially change the commercial decision.

The deterministic startup rule places official procurement sources before internal customer intelligence after canonical-registry identity reconciliation. This ordering establishes the external procurement state first while still reusing internal intelligence before broader market collection.

The mission uses a **transient mission context** for queries run, sources inspected, discovered entities, hypotheses, contradictions, open questions, closed questions and next-best actions. This context exists only for the mission and does not create an eighth canonical registry record type.

After startup, the adaptive loop is:

`Discover → Extract → Resolve → Reconcile → Validate → Assess → Prioritize → Decide → Promote/Monitor → Learn`

### Discover
Find relevant signals through one or more discovery vectors and materially relevant 360° collection lenses, using contextualized taxonomy/product/capability vocabulary to improve recall and avoid category errors.

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

The runtime has one primary external seam: an authenticated analysis envelope enters `Argus.analyze`, and a correlated domain result plus synchronization receipt returns. Collection, normalization, reconciliation and assessment remain inside the injected domain-method implementation rather than expanding the external interface.

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

360° collection and transient mission context do **not** create an eighth record type. Mission coordination state is execution-local; durable facts are persisted only into their proper canonical objects after governed verification and authorization.

## 8. Canonical ownership

Use one canonical owner per information class:

- current mutable ARGUS structured state — SharePoint SQLite `General/Business Intelligence/30_OPERATIONS/ARGUS_Master_Registry.sqlite`;
- ARGUS schema, identity rules, migration logic, tests, methods and release snapshots — ARGUS GitHub;
- communication system — communication truth;
- external document repository/source system — original document/evidence truth;
- HubSpot — CRM company/contact identity, relationship, interaction and deal truth;
- SharePoint business-intelligence/opportunity/project folders — original/working business documents and lifecycle files;
- analytical engines — derived projections only;
- research tools — evidence sources, not canonical truth;
- monitoring tools — change detection, not opportunity authority.

**Rule:** store each item once in its natural canonical home and link elsewhere. Raw tender/source documents and CRM master data do not belong in public ARGUS GitHub.

## 9. Discovery vectors

ARGUS supports converging discovery vectors, including:

- policy/top-down;
- institution/buyer-downward;
- product-to-buyer reverse discovery;
- procurement-backward;
- historical/installed-base;
- funding-led;
- ecosystem-led;
- supplier/product-led;
- trigger-event.

Contextualization expands governed ATLAS classifications into search/discovery vocabulary such as aliases, abbreviations, adjacent solution classes, mission terms and local terminology. These enrichments are ARGUS discovery semantics, not replacement taxonomy authority.

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

### 10.6 Ordered startup and internal reuse

ARGUS reuses authorized internal intelligence while preserving the institution-first startup sequence. The default order for a government-commercial mission is:

`institution hierarchy → ARGUS canonical registry → identity reconciliation → official procurement sources → internal customer intelligence → Research Frontier → adaptive external/internal 360° collection`

The purpose is not to force every source into every mission. It is to establish buyer context and object identity early, detect authoritative procurement signals quickly, reuse Access Asia knowledge before duplicating broad research, and then spend effort only on material gaps.

Internal customer intelligence may include, where authorized and relevant:

- SharePoint customer/opportunity/project files and prior research;
- HubSpot company/contact relationship state, interactions, notes and deals;
- prior correspondence, meetings, proposals, quotations and supplier/customer history;
- previous ARGUS observations, opportunities, supplier/product records and lessons.

Canonical masters remain in their owning systems; ARGUS uses pointers/references rather than copying CRM or source-document masters.

### 10.7 Proportionality and stopping rule

The breadth of assessment should cover all materially relevant lenses; the depth of collection is controlled by the Research Frontier.

Stop expanding collection when additional work is unlikely to change:

- the reality of the signal;
- I0–I9 maturity;
- route/institution/funding/procurement interpretation;
- merge/new-candidate judgment;
- supplier/product/competitor strategy;
- `MONITOR`, `INVESTIGATE`, `PROMOTE_TO_PX`, `MERGE_EXISTING`, `HOLD` or `REJECT`;
- next action or next material trigger.

A weak early signal may justify only a few lens checks. A promotion recommendation may require broader coverage. A live tender may not require reconstruction of every historic policy source when that work would not change the current decision.

Independent safe reads may run in parallel after the deterministic startup dependencies are satisfied. Canonical mutations remain serialized.

## 11. Identity and reconciliation

Identity states:

- `EXACT`
- `HIGH_CONFIDENCE_MATCH`
- `PROBABLE_MATCH`
- `UNRESOLVED`
- `DISTINCT`

Identity behavior under the bounded-autonomous mission is explicit:

- `EXACT` and `HIGH_CONFIDENCE_MATCH` continue without user confirmation on the existing canonical object when supported by adequate identity evidence;
- `DISTINCT` continues as a new candidate without user confirmation when the evidence clearly establishes a different real-world object;
- `PROBABLE_MATCH` and `UNRESOLVED` are the identity-confirmation escalation seam when choosing incorrectly could duplicate, merge or mutate the wrong opportunity;
- title similarity alone never authorizes a merge.

Procurement reconciliation outcomes:

- `MATCHED_EXISTING`
- `PROBABLE_EXISTING`
- `POSSIBLE_EXISTING`
- `NEW_CANDIDATE`
- `DUPLICATE`
- `SUPERSEDING_UPDATE`

A new document, tender, amendment, re-tender or award does not automatically create a new commercial opportunity. One underlying requirement/opportunity may link to multiple procurement cycles, packages and solicitations.

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

A question belongs in the Research Frontier when its answer may materially change the reality of the signal, maturity, timing, institutional path, funding path, procurement path, commercial attractiveness, duplicate/merge result, supplier strategy, promotion decision or next action.

The 360° coverage matrix exposes gaps; the Research Frontier decides which gaps deserve further work.

Within a bounded ATLAS mission, ARGUS owns the ordering of internal research branches and may follow new evidence leads without requesting a new ATLAS callback. ATLAS owns the outer mission scope, authorization, approvals and execution lease. A new handoff is required only when an escalation condition is met, particularly a material scope/classification change.

Stop expanding a research branch when additional evidence is unlikely to change the next commercial decision.

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

ARGUS returns one structured domain result to the governing runtime under the normal one-handoff/one-return path. It is not automatically the final user-facing answer.

In `ATLAS_GOVERNED` mode, the result must contain the exact accepted upstream handoff receipt so ATLAS can verify `contract_version`, `handoff_id`, `payload_sha256` and consumer identity before accepting the result.

The result contains, proportionately:

- governance mode and upstream handoff receipt where applicable;
- objective;
- candidate/opportunity;
- domain decision;
- I0–I9 maturity;
- institutional chain;
- existing/new/ambiguous identity outcome;
- project/funding/procurement state;
- commercial relevance;
- evidence and provenance;
- 360° collection coverage where material;
- collection gaps where material;
- unknowns/conflicts;
- Research Frontier;
- supplier/product/competitor assessment where material;
- next material trigger;
- next recommended action;
- proposed domain/registry actions as one batched mutation proposal when persistence is useful.

The machine-readable contract is defined in `schemas/domain-result.schema.json`.

## 17. Domain actions and persistence

Current mutable ARGUS structured state is canonical in the governed SharePoint SQLite store:

`General/Business Intelligence/30_OPERATIONS/ARGUS_Master_Registry.sqlite`

ARGUS GitHub remains authoritative for schema, canonical identity rules, migration logic, tests, methods and versioned release snapshots. GitHub registry JSON/JSONL is migration/bootstrap/audit or release-snapshot material, not a competing live write target.

An ARGUS canonical mutation is a domain action, not an automatic side effect of research.

Under ATLAS governance:

1. ATLAS provides the validated domain-context handoff, collection mission and execution lease.
2. ARGUS performs the institution-first startup and bounded-autonomous investigation.
3. ARGUS returns the domain result, exact upstream handoff correlation and, where useful, one proposed mutation bundle.
4. ATLAS verifies return correlation, material claims, identity resolution, authorization and approval requirements.
5. ATLAS fetches the latest SharePoint SQLite target, verifies target metadata/version and database integrity, and resolves canonical identity again before mutation.
6. Authorized changes are applied locally in one serialized transaction with provenance and mutation-log entries.
7. Integrity/foreign-key checks run, the SharePoint target is re-checked, the same file is replaced, and the uploaded result is verified.
8. ATLAS delivers the verified result.

ARGUS should not persist every intermediate discovery. Candidate observations and relationships remain in transient mission context until a decision-sufficient result can be proposed as a coherent batch.

Saving a report never proves that canonical structured state changed. A canonical structured mutation never substitutes for required ATLAS verification or business-file persistence.

## 18. PX promotion and downstream handoff

Only promoted opportunities receive the permanent Access Asia `YYYY_PX####_SHORTNAME` identity.

Permanent PX creation, destructive merge or another major canonical-state change uses the governing runtime's approval controls where applicable.

After promotion, downstream CRM/workflows reuse the permanent PX identity and canonical references rather than creating a competing identity.

ARGUS does not own detailed capture, bid/no-bid, tender compliance, proposal preparation, pricing, submission, contract administration, project execution, invoicing, warranty or closeout.

## 19. Monitoring

Monitoring detects changes; it does not create opportunities directly.

Monitoring should be event- and lens-aware. Triggers may target funding changes, project approvals, procurement notices, technical obsolescence, institutional changes, consultant appointments, supplier moves, policy changes or other material events.

A detected event re-enters normal ARGUS institutional/identity reconciliation, validation, assessment and decision logic. If the event changes ATLAS-owned mission scope/classification materially, ARGUS raises `MATERIAL_SCOPE_CHANGE` before dependent work continues.

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
7. Is ARGUS the correct owner, or is the capability already owned by ATLAS?
8. Does the feature improve institutional resolution, 360° coverage, evidence quality, reconciliation or decision quality without encouraging indiscriminate collection?
9. Does it preserve the one-handoff/one-return seam and avoid routine cross-application callbacks?

If not, keep it outside ARGUS Core.
