# Autonomous ATLAS–ARGUS 360° Mission Flow Implementation Plan

> **For agentic workers:** Use the host's available task-by-task implementation workflow. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make ATLAS delegate one bounded intelligence mission to ARGUS, let ARGUS autonomously execute a deterministic buyer/identity/procurement/customer-intelligence startup sequence and adaptive 360° research, and return once unless a true escalation condition occurs.

**Architecture:** ATLAS remains the execution/governance owner and produces the collection mission. ARGUS remains the specialist intelligence engine and receives one validated mission containing an explicit bounded-autonomy policy. ARGUS keeps transient mission context inside the execution only; it does not add a new canonical record type. Current mutable structured state remains in the governed SharePoint SQLite registry and any writes remain ATLAS-authorized/batched.

**Tech Stack:** Python 3, JSON Schema 2020-12, YAML/Markdown contracts, GitHub Actions contract tests, SharePoint operating documentation.

## Global Constraints

- Preserve the ATLAS 3-step pre-execution model: understand/normalize -> minimal domain framing -> route.
- One normal ATLAS -> ARGUS handoff and one normal ARGUS -> ATLAS return.
- ARGUS startup order for government-commercial targets: institutional hierarchy -> internal canonical registry -> identity reconciliation -> official procurement sources -> internal customer intelligence -> Research Frontier -> adaptive 360° collection.
- Existing identity is auto-reused only for exact/high-confidence matches; clearly distinct evidence creates a new candidate; probable/unresolved identity is the user-escalation seam.
- ARGUS may follow evidence leads, choose source routes, search suppliers/products/competitors, and continue collection without routine ATLAS callbacks.
- Escalate only for material scope change, consequential authorization, policy/security conflict, or material ambiguity.
- 360° breadth is decision-driven; stop when additional collection is unlikely to change the commercial decision.
- Reads may be parallelized where independent. Canonical mutations remain serialized and batched through ATLAS.
- Do not create an `INTELLIGENCE_CASE` canonical registry type; mission context is transient execution state.

---

### Task 1: Extend the ATLAS collection mission contract

**Files:**
- Modify: `schemas/collection-mission.schema.json`
- Modify: `atlas_runtime/collection.py`
- Modify: `tests/unit/test_collection_architecture.py`
- Modify: `spec/collection-routing.yaml`

**Interfaces:**
- Consumes: `build_collection_mission(objective, task_id, plan_id, request_triage, risk_flags)`
- Produces: validated collection missions with `execution_policy` describing startup order, bounded autonomy, identity-resolution behavior, escalation conditions, persistence mode and transient mission-context behavior.

- [ ] Add a failing unit assertion for the execution policy and Coast Guard-compatible startup order.
- [ ] Verify the focused test fails because `execution_policy` is absent.
- [ ] Extend the schema and mission builder with the minimum policy fields.
- [ ] Verify focused tests pass and update the routing contract text.
- [ ] Run ATLAS validation workflow through the PR.

### Task 2: Make ARGUS consume the bounded-autonomy contract

**Files:**
- Modify: `schemas/collection-mission.schema.json`
- Modify: `tools/argus_runtime.py`
- Modify: `tests/test_argus_runtime.py`
- Modify: `spec/core.md`
- Modify: `spec/collection-method.yaml`

**Interfaces:**
- Consumes: ATLAS collection mission `execution_policy`.
- Produces: one domain-method input containing the validated mission and transient `mission_context_policy`; preserves the one `Argus.analyze(...)` external seam.

- [ ] Add a failing runtime test proving ARGUS receives the execution policy without creating a canonical IntelligenceCase.
- [ ] Verify failure because runtime does not expose mission-context policy.
- [ ] Add the minimum runtime propagation and contract text.
- [ ] Verify focused runtime tests pass.
- [ ] Run ARGUS contract suite through the PR.

### Task 3: Codify 360° sequence and identity escalation semantics

**Files:**
- Modify: `spec/core.md`
- Modify: `spec/commercial-opportunity-intelligence.yaml`
- Modify: `profiles/bangladesh.md`
- Modify: `docs/validation/bcg-cpv-live-dry-run-2026.md`
- Test: `tests/test_360_collection_contract.py`

**Interfaces:**
- Consumes: resolved target + existing canonical registry + official/public sources + authorized internal intelligence.
- Produces: identity outcome (`MATCHED_EXISTING`, `NEW_CANDIDATE`, or escalation for ambiguous probable/unresolved match), Research Frontier, decision-sufficient 360° result and optional batched mutation proposal.

- [ ] Add contract assertions for institutional-first sequence, automatic exact/high-confidence reuse, ambiguity-only user escalation and customer-intelligence stage.
- [ ] Verify assertions fail against the old doctrine.
- [ ] Update doctrine/profile/CPV dry run.
- [ ] Verify tests pass.

### Task 4: Synchronize SharePoint operating documentation

**Files:**
- Update SharePoint `20_ARCHITECTURE/CURRENT_ARCHITECTURE.md`
- Update SharePoint `20_ARCHITECTURE/TARGET_ARCHITECTURE.md`
- Update SharePoint `30_OPERATIONS/AI_EXECUTION_SOP.md`
- Update SharePoint `40_VALIDATION/CURRENT_STATUS.md`

**Interfaces:**
- Consumes: merged ATLAS and ARGUS contracts.
- Produces: human operating guidance matching the code/runtime.

- [ ] Update only affected sections.
- [ ] Preserve canonical ownership and single-writer SQLite rules.
- [ ] Read back exact SharePoint targets after upload.
- [ ] Record merged repository heads and validation state.

## Unresolved externally observable decisions

None. The user has approved the recommended autonomous bounded-investigation model; existing ATLAS approval and persistence rules remain unchanged.
