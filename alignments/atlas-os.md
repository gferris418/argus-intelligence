# ARGUS ↔ ATLAS OS Alignment Contract

**ARGUS version:** 2.0.0-rc.3
**Validated ATLAS baseline:** 2.0.0-rc.10 at `673a676a0b23518dad1a295a7cd36b5b75aa064e` + Domain Context Handoff v1.1
**Status:** Candidate

## 1. Governing rule

ATLAS OS is the execution-governance backbone for Access Asia production execution.

ARGUS is independently specified and portable as a government opportunity-intelligence framework, but every ARGUS execution inside the Access Asia governed environment runs under the current ATLAS OS execution contract.

ATLAS owns generic domain classification, taxonomy references, material risk flags, and domain-framework/standards alignment. ARGUS consumes that context through the governed ATLAS Domain Context handoff and must not silently redefine it.

## 2. Production chain

`User objective → ATLAS task/domain classification → ATLAS framework alignment → schema-valid domain-context handoff → ATLAS Domain Context → ARGUS Contextualize → ARGUS domain method → ARGUS domain result + exact handoff receipt + proposed domain actions → ATLAS return-correlation verification/approval → authorized domain action(s) → ATLAS delivery`

ATLAS remains the only user-visible execution spine and plan.

## 3. Ownership boundary

### ATLAS owns

- intent/context preservation;
- task classification;
- domain classification;
- taxonomy and industry/product/service/capability references;
- cross-taxonomy classification context;
- information-sensitivity and authorization controls;
- applicable law/regulation/framework/standards alignment;
- execution depth;
- one canonical plan and atomic work units;
- capability/tool/skill routing;
- evidence assurance;
- generic approval gates;
- independent verification;
- task/library persistence and receipts;
- output-profile selection;
- observability/dashboard;
- final delivery;
- production of the governed domain-context handoff.

### ARGUS owns

- contextualization of the ATLAS domain context for government opportunity intelligence;
- terminology/alias/search expansion that does not redefine ATLAS taxonomy authority;
- capability-to-solution and adjacent-product discovery relationships;
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

## 4. Mandatory domain-context handoff

Before dependent ARGUS execution in Access Asia production, ARGUS must receive a **schema-valid domain-context handoff** conforming to the pinned ATLAS contract in `contracts/atlas/domain-context-handoff-v1.schema.json`.

The handoff must include and preserve:

- `contract_version`;
- `handoff_id`;
- `source_task_id`;
- `source_plan_id`;
- `source_work_unit_id`;
- `producer`;
- `consumer`;
- `created_at`;
- handoff `state`;
- exact `domain_classification` snapshot;
- exact `domain_alignment` snapshot;
- `unresolved_material`;
- `risk_flags`;
- `payload_sha256`.

Rules:

1. `READY` may proceed normally.
2. `PARTIAL` may proceed only with unresolved facets/risk flags carried forward explicitly and never guessed away.
3. `BLOCKED` cannot authorize dependent ARGUS execution.
4. ARGUS may enrich the context for opportunity intelligence but must not redefine ATLAS taxonomy or standards conclusions.
5. If new evidence materially changes ATLAS-owned classification/alignment, ARGUS returns that finding to ATLAS; ATLAS must issue a new handoff.
6. ARGUS returns an upstream handoff receipt in every `ATLAS_GOVERNED` domain result.
7. ATLAS must reject mismatched, missing, mutated, stale or rejected handoff correlation before accepting the ARGUS result.
8. `handoff_id`, contract version, consumer and `payload_sha256` must match exactly end-to-end.

The executable synchronization boundary is implemented in `tools/atlas_sync.py`. It validates the pinned ATLAS contracts, verifies detached Ed25519 attestations with operator-pinned ATLAS public keys, maintains a local non-canonical synchronization receipt, rejects replay or stale results, reconciles retry/resume against the actual registry fingerprint, and binds proposed actions to exact ATLAS approval capabilities. Synchronization receipts do not create an eighth Master Registry record type.

## 5. Stage mapping

| ATLAS stage | ARGUS interaction |
|---|---|
| INTAKE | Receive opportunity seed/objective |
| CONTEXT_PRESERVATION | Preserve names, identifiers, product/service, institution, jurisdiction and constraints |
| NORMALIZATION | ATLAS normalizes task representation |
| COMPLETENESS_CHECK | Material missing execution context is resolved or exposed |
| TASK_CLASSIFICATION | ARGUS is a domain method, not a task class |
| DOMAIN_CLASSIFICATION | ATLAS resolves material jurisdiction/industry/product/service/capability/lifecycle/stakeholder/sensitivity context |
| DOMAIN_FRAMEWORK_ALIGNMENT | ATLAS resolves/revalidates applicable law, standards, professional frameworks and authoritative guidance |
| PLANNING | ATLAS creates the one canonical plan and atomic work units |
| ROUTING | ATLAS produces/validates the specialist domain-context handoff before delegation |
| EVIDENCE_ACQUISITION | ARGUS supplies domain-specific evidence priorities from the contextualized handoff |
| EXECUTION | ARGUS runs Contextualize → Discover → Extract → Resolve → Reconcile → Validate → Assess → Prioritize → Decide → Learn |
| VERIFICATION | ATLAS first verifies handoff correlation, then material claims, reconciliation conclusions and proposed actions |
| PERSISTENCE | ATLAS persists task/library artifacts/receipts; ARGUS canonical state uses its governed current store |
| DELIVERY | ATLAS selects the final output profile and delivers; ARGUS domain result is an input |

## 6. Contextualization seam

`ATLAS Domain Context → ARGUS Contextualize`

Contextualization translates governed ATLAS classification/alignment into specialist opportunity-intelligence semantics such as:

- preferred domain terminology and aliases;
- search/retrieval expansion;
- related/adjacent solution classes;
- capability-to-solution relationships;
- Bangladesh/local terminology;
- installed-base interpretation;
- supplier/competitor relevance;
- procurement/project/funding discovery implications;
- commercial meaning.

Contextualization does not replace the ATLAS classification record. Any ARGUS-added taxonomy-like term is an enrichment/reference unless and until ATLAS independently classifies it.

## 7. Planning and Research Frontier seam

ARGUS Research Frontier identifies the next unresolved question most likely to change the commercial decision.

It does not self-schedule or create a competing plan.

When more research is required:

`ARGUS Research Frontier → ATLAS plan/work-unit update → ATLAS routing/evidence acquisition → (new handoff if ATLAS context changed materially) → ARGUS analysis`

Safe read-only evidence acquisition may be batched within the active ATLAS work unit when allowed. A materially new dependent objective becomes the next ATLAS work unit.

## 8. Evidence seam

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

## 9. Domain result seam

ARGUS returns a domain-result object to ATLAS; it is not automatically the final user-facing answer.

In `ATLAS_GOVERNED` mode the result must include `upstream_handoff` containing the exact receipt fields:

- `contract_version`;
- `handoff_id`;
- `payload_sha256`;
- `consumer` = `ARGUS`;
- `status` = `ACCEPTED`;
- `received_at`.

The result may additionally include objective, candidate/opportunity, country route and confidence, domain decision, I0–I9 maturity, institutional chain, project/budget/funding state, procurement state/horizon, commercial relevance, evidence, unknowns/conflicts, Research Frontier, next trigger/action and proposed domain actions.

ATLAS verifies the receipt correlation before using the result, then chooses the final output profile, verifies material claims, applies approvals and delivers.

## 10. Domain action seam

ARGUS analytical decisions and domain mutations are separate.

Example:

- decision: `PROMOTE_TO_PX`
- proposed action: `CREATE_PX_OPPORTUNITY`

The decision is analytical. The action is governed execution.

Under ATLAS:

1. ARGUS proposes the action.
2. ATLAS verifies the originating handoff receipt and evaluates authorization/sensitivity/approval requirements.
3. The governed current canonical-store mechanism executes the authorized action.
4. ATLAS verifies the outcome.

Permanent PX creation, destructive merge, identity reassignment, or another **major canonical-state change** remains subject to the existing ATLAS approval controls. ARGUS does not create a separate approval framework.

## 11. Canonical-state vs ATLAS persistence seam

This distinction is mandatory.

### ARGUS canonical domain mutation

`ARGUS result → exact handoff correlation → proposed canonical action → ATLAS authorization/approval → governed ARGUS canonical store`

Current physical canonical store: private GitHub `data/registry/` JSON/JSONL lineage. Future database materialization is an implementation change.

### ATLAS persistence

`ATLAS verified task result → ATLAS PERSISTENCE → task-fit Library collection / durable artifact / execution receipt`

An ATLAS Library save never proves an ARGUS canonical-state mutation. An ARGUS canonical-state mutation never substitutes for required ATLAS task-artifact persistence.

## 12. Current-law/currency seam

Country profiles may maintain dated legal/institutional baselines as operational knowledge.

They are not the runtime authority for current law.

When law, regulation, procurement rules, financing rules, taxonomy editions, standards or authoritative guidance can materially change the result, ATLAS must revalidate them before producing the domain-context handoff used by ARGUS.

## 13. Classification seam

ATLAS classification and ARGUS opportunity contextualization are complementary, not competing.

ATLAS answers: what jurisdiction, operator/supplier industry, product/service, capability, lifecycle, stakeholder, sensitivity, taxonomy references and applicable frameworks govern the task?

ARGUS answers: what do those governed classifications mean for opportunity discovery, local terminology, solution adjacency, installed base, supplier/competitor intelligence, route interpretation, commercial relevance and opportunity development?

Country-route classification remains ARGUS domain analysis; it does not replace ATLAS taxonomy classification.

## 14. Persistence and history

ATLAS Library retention governs ATLAS-controlled artifacts.

ARGUS procurement, opportunity, relationship, installed-base, reconciliation and audit history remains governed by ARGUS domain retention requirements and the current canonical Git lineage.

ATLAS retention must not truncate ARGUS canonical history.

## 15. Source authority

Source authority is claim-specific.

- official procurement sources govern procurement-event claims;
- official project/budget/funding sources govern those claims;
- communications may govern Access Asia relationship/history claims;
- standards and professional frameworks govern applicable requirements and methods, not unrelated procurement facts.

ARGUS must use the strongest relevant source for each material claim within ATLAS routing/evidence controls.

## 16. Standalone mode

Standalone ARGUS execution remains permitted for portability, testing, recovery or non-Access-Asia implementations.

Inside Access Asia production, ARGUS does not bypass ATLAS classification, framework alignment, handoff, planning, sensitivity, authorization, verification, persistence or delivery.

## 17. Acceptance invariant

For every governed ARGUS execution:

1. ATLAS classification/alignment exists.
2. ATLAS emits a schema-valid handoff.
3. ARGUS validates the pinned contract before Contextualize.
4. ARGUS preserves unresolved/risk information and does not redefine ATLAS authority.
5. ARGUS returns the exact handoff correlation in its domain result.
6. ATLAS verifies the receipt before accepting the result.
7. Any material upstream-context change triggers a new handoff rather than silent mutation.
