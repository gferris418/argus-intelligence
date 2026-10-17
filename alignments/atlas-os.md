# ARGUS ↔ ATLAS OS Alignment Contract

**ARGUS version:** 2.0.0-rc.1  
**Validated ATLAS baseline:** 2.0.0-rc.7  
**Status:** Candidate

## 1. Governing rule

ATLAS OS is the unchanged execution-governance backbone for Access Asia production execution.

ARGUS is independently specified and portable as a government opportunity-intelligence framework, but every ARGUS execution inside the Access Asia governed environment runs under the current ATLAS OS execution contract.

If ARGUS conflicts with an existing ATLAS execution-governance contract, ARGUS or this alignment layer must change. ARGUS does not require changes to ATLAS Core, runtime, execution spine, classification, evidence model, approvals, persistence semantics, output profiles, routing or surface adapters.

## 2. Production chain

`User objective → ATLAS OS governance → ARGUS domain method → ARGUS domain result + proposed domain actions → ATLAS verification/approval → authorized domain action(s) → ATLAS task-artifact persistence → ATLAS delivery`

ATLAS remains the only user-visible execution spine and plan.

## 3. Ownership boundary

### ATLAS owns

- intent/context preservation;
- task classification;
- generic domain classification;
- information-sensitivity and authorization controls;
- execution depth;
- one canonical plan and atomic work units;
- capability/tool/skill routing;
- applicable-law/framework alignment;
- evidence assurance;
- generic approval gates;
- independent verification;
- task/library persistence and receipts;
- output-profile selection;
- observability/dashboard;
- final delivery.

### ARGUS owns

- government/public-sector opportunity-intelligence semantics;
- discovery vectors;
- entity resolution and procurement reconciliation;
- Master Registry record semantics;
- ARGUS IDs and PX lineage;
- I0–I9 opportunity-development maturity;
- independent project/funding/procurement/commercial dimensions;
- Research Frontier;
- country profiles;
- domain decisions;
- domain claim types/conditions and provenance;
- PX promotion recommendation;
- standalone portability semantics.

## 4. Stage mapping

| ATLAS stage | ARGUS interaction |
|---|---|
| INTAKE | Receive opportunity seed/objective |
| CONTEXT_PRESERVATION | Preserve names, identifiers, product/service, institution, jurisdiction and constraints |
| NORMALIZATION | ATLAS normalizes task representation; ARGUS later resolves domain aliases/entities |
| COMPLETENESS_CHECK | Unknown opportunity facts become research questions unless a missing user decision/authorization blocks work |
| TASK_CLASSIFICATION | ARGUS is a domain method, not a task class |
| DOMAIN_CLASSIFICATION | Provides jurisdiction/industry/product/capability/lifecycle/sensitivity context; does not replace country-route classification |
| DOMAIN_FRAMEWORK_ALIGNMENT | ATLAS resolves/revalidates current binding law, regulation and applicable frameworks when material |
| PLANNING | ATLAS creates the one canonical plan and atomic work units |
| ROUTING | ATLAS selects Registry, communications, documents, research and monitoring capabilities |
| EVIDENCE_ACQUISITION | ARGUS supplies internal-first/domain-specific evidence priorities |
| EXECUTION | ARGUS runs Discover → Extract → Resolve → Reconcile → Validate → Assess → Prioritize → Decide → Learn |
| VERIFICATION | ATLAS verifies material claims, reconciliation conclusions and proposed actions |
| PERSISTENCE | ATLAS persists task/library artifacts and receipts; it is not the ARGUS Registry write destination |
| DELIVERY | ATLAS selects the final output profile and delivers; ARGUS domain result is an input |

## 5. Planning and Research Frontier seam

ARGUS Research Frontier identifies the next unresolved question most likely to change the commercial decision.

It does not self-schedule or create a competing plan.

When more research is required:

`ARGUS Research Frontier → ATLAS plan/work-unit update → ATLAS routing/evidence acquisition → ARGUS analysis`

Safe read-only evidence acquisition may be batched within the active ATLAS work unit when allowed. A materially new dependent objective becomes the next ATLAS work unit.

## 6. Evidence seam

ARGUS claim type:

- `FACT`
- `DERIVED`
- `INFERENCE`
- `ASSUMPTION`
- `UNKNOWN`

ARGUS claim condition:

- `CURRENT`
- `STALE`
- `CONFLICT`

ATLAS assurance remains independent:

- `VERIFIED`
- `SUPPORTED`
- `INFERRED`
- `ASSUMED`
- `SPECULATIVE`
- `UNKNOWN`

ATLAS evidence health remains independent.

`ARGUS FACT` never implies `ATLAS VERIFIED` automatically.

## 7. Domain result seam

ARGUS returns a domain-result object to ATLAS; it is not automatically the final user-facing answer.

The result may include:

- objective;
- candidate/opportunity;
- country route and confidence where applicable;
- domain decision;
- I0–I9 maturity;
- institutional chain;
- project/budget/funding state;
- procurement planning/package state;
- procurement state/horizon;
- commercial relevance;
- claim types/conditions and evidence references;
- unknowns/conflicts;
- Research Frontier;
- next material trigger;
- next recommended action;
- `proposed_domain_actions` / `proposed_registry_actions`.

ATLAS then chooses the final output profile, verifies material claims, applies approvals, persists task artifacts and delivers.

## 8. Domain action seam

ARGUS analytical decisions and domain mutations are separate.

Example:

- decision: `PROMOTE_TO_PX`
- proposed action: `CREATE_PX_OPPORTUNITY`

The decision is analytical. The action is governed execution.

Under ATLAS:

1. ARGUS proposes the action.
2. ATLAS evaluates authorization, sensitivity and applicable approval requirements.
3. The governed adapter executes the authorized action.
4. ATLAS verifies the outcome.

Routine reversible research and preparation can proceed autonomously within authorization. Permanent PX creation, destructive/high-impact merges and other major canonical-state changes map to the existing ATLAS approval controls.

ARGUS does not create a separate approval framework.

## 9. Registry mutation vs ATLAS persistence seam

This distinction is mandatory.

### ARGUS domain mutation

`ARGUS result → proposed registry action → ATLAS authorization/approval → RegistryStoreAdapter / Registry API → ARGUS Master Registry`

### ATLAS persistence

`ATLAS verified task result → ATLAS PERSISTENCE → task-fit Library collection / durable artifact / execution receipt`

A Library save never proves a Registry mutation. A Registry mutation never substitutes for required ATLAS task-artifact persistence.

## 10. Current-law/currency seam

Country profiles may maintain dated legal/institutional baselines as operational knowledge.

They are not the runtime authority for current law.

When law, regulation, procurement rules, financing rules or authoritative guidance can materially change the result, ATLAS DOMAIN_FRAMEWORK_ALIGNMENT must revalidate the current binding requirements before relying on cached profile text.

## 11. Classification seam

ATLAS generic domain classification and ARGUS country-route classification are complementary.

ATLAS answers contextual questions such as jurisdiction, operator industry, supplier industry, product/service, capability, lifecycle, stakeholder and information sensitivity.

ARGUS answers domain-specific questions such as which procurement/acquisition route currently best explains the opportunity.

Country-route classification does not require an ATLAS taxonomy extension.

## 12. Persistence and history

ATLAS Library retention governs ATLAS-controlled artifacts.

ARGUS procurement, opportunity, relationship, installed-base, reconciliation and audit history remains governed by ARGUS domain retention requirements.

ATLAS retention must not be used to truncate ARGUS canonical history.

## 13. Source authority

Source authority is claim-specific.

- official procurement sources govern procurement-event claims;
- official project/budget/funding sources govern those claims;
- communications may govern Access Asia relationship/history claims;
- standards and professional frameworks govern applicable requirements and methods, not unrelated procurement facts.

ARGUS must use the strongest relevant source for each material claim within ATLAS routing/evidence controls.

## 14. Standalone mode

Standalone ARGUS execution remains permitted for portability, testing, recovery or non-Access-Asia implementations.

Inside Access Asia production, ARGUS does not bypass ATLAS startup, planning, sensitivity, authorization, verification, persistence or delivery.

`ATLAS INIT | CURRENT` is not a required ARGUS technical command. ARGUS executes within the already-active ATLAS control plane.

## 15. Acceptance invariant

For every ARGUS capability ask:

> Can this capability operate correctly under ATLAS OS exactly as it exists?

- **Yes:** retain the ARGUS design.
- **No:** redesign ARGUS or its adapter/alignment layer.
- Do not change ATLAS solely to accommodate ARGUS.
