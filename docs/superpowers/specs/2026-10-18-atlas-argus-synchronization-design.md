# ATLAS OS ↔ ARGUS Synchronization Design v1

**Date:** 2026-10-18  
**Status:** DESIGN_FOR_REVIEW  
**Scope:** ARGUS implementation against immutable ATLAS OS contracts  
**ATLAS baseline:** `2.0.0-rc.7` at `a9e709e10a0187b342520baa06dbf4a3e05fbb24`  
**ARGUS baseline:** `2.0.0-rc.2` at `36b611e96d37b048b5b2e8ea076db70315ce38b9`  
**ATLAS modification required:** No  
**Production activation:** No

## 1. Purpose

Harden the synchronization seam between ATLAS OS and ARGUS so Access Asia production execution has one governing execution system, one specialist intelligence method, and executable synchronization guarantees between them.

The governing principle is:

> **ATLAS governs the work. ARGUS understands the opportunity.**

ATLAS remains the immutable upstream execution-governance authority. ARGUS remains the specialist government/public-sector opportunity-intelligence method. This design adds no competing execution spine, approval framework, taxonomy authority, or persistence authority.

## 2. Existing authority

### ATLAS OS owns

- user intent/context preservation;
- task and domain classification;
- taxonomy references;
- framework/law/standards alignment;
- execution planning and work units;
- routing;
- generic risk and sensitivity controls;
- evidence assurance and independent verification;
- approval gates;
- task persistence and receipts;
- final output and delivery;
- production of the governed domain-context handoff.

The ATLAS execution spine remains unchanged:

`INTAKE → CONTEXT_PRESERVATION → NORMALIZATION → COMPLETENESS_CHECK → TASK_CLASSIFICATION → DOMAIN_CLASSIFICATION → DOMAIN_FRAMEWORK_ALIGNMENT → PLANNING → ROUTING → EVIDENCE_ACQUISITION → EXECUTION → VERIFICATION → PERSISTENCE → DELIVERY`

### ARGUS owns

- contextualization of ATLAS domain context for government opportunity intelligence;
- discovery and search expansion;
- entity/project/procurement resolution and reconciliation;
- project/funding/procurement interpretation;
- supplier/competitor/installed-base intelligence;
- Master Registry domain semantics and ARGUS IDs;
- I0–I9 maturity;
- 360° collection coverage;
- Research Frontier;
- commercial assessment;
- domain decisions;
- proposed domain actions and PX-promotion recommendations.

ARGUS does not redefine ATLAS-owned taxonomy, classification, standards conclusions, approvals, plan state, or final delivery.

## 3. Chosen architecture

### Selected: ARGUS-side synchronization runtime against immutable ATLAS contracts

ATLAS stays unchanged. ARGUS adds a small synchronization layer that consumes pinned ATLAS contracts and enforces compatibility, handoff integrity, lifecycle, return correlation, invalidation, retry/resume, and action-authorization preconditions.

Rejected alternatives:

1. **Duplicate synchronization state machines in ATLAS and ARGUS** — rejected because it creates two implementations of the same interoperability semantics and increases drift risk.
2. **Shared package used by both repositories** — rejected because it would require changing ATLAS packaging/dependencies and violates the immutable-backbone constraint.

## 4. Synchronization boundary

Canonical flow:

```text
User objective
    ↓
ATLAS intent/context preservation
    ↓
ATLAS task + domain classification
    ↓
ATLAS framework/law/standards alignment
    ↓
ATLAS planning / work unit
    ↓
ATLAS governed domain-context handoff
    ↓
ARGUS synchronization validator
    ↓
ARGUS Contextualize → Discover → Extract → Resolve → Reconcile →
Validate → Assess → Prioritize → Decide → Promote/Monitor → Learn
    ↓
ARGUS domain result + exact upstream receipt + proposed actions
    ↓
ATLAS correlation verification
    ↓
ATLAS assurance / approval / authorization
    ↓
Authorized ARGUS canonical action where applicable
    ↓
ATLAS persistence and final delivery
```

The synchronization boundary is bidirectional but authority is asymmetric: ATLAS context flows down; ARGUS intelligence and proposed actions flow up.

## 5. Compatibility contract

ARGUS shall maintain an executable compatibility descriptor for the approved ATLAS baseline. It shall pin:

```yaml
atlas_compatibility:
  atlas_version: 2.0.0-rc.7
  atlas_commit: a9e709e10a0187b342520baa06dbf4a3e05fbb24
  handoff_contract_version: 1.0.0
  source_contracts:
    domain_context_handoff:
      source_path: schemas/domain-context-handoff.schema.json
      sha256: <computed>
    domain_handoff_receipt:
      source_path: schemas/domain-handoff-receipt.schema.json
      sha256: <computed>
    approval:
      source_path: schemas/approval.schema.json
      sha256: <computed>
    runtime:
      source_path: spec/runtime.yaml
      sha256: <computed>
    approvals:
      source_path: spec/approvals.yaml
      sha256: <computed>
    verification:
      source_path: spec/verification.yaml
      sha256: <computed>
```

Build/test compatibility fails closed if a pinned contract or normative ATLAS source changes without a separately reviewed compatibility update.

ARGUS may keep local read-only copies of the schemas it must validate at runtime. Those copies are compatibility artifacts, not independent authorities.

## 6. Reuse of ATLAS approval schema

ARGUS will **not** invent an `atlas-authorization-receipt` schema.

ATLAS already defines `schemas/approval.schema.json` with:

- `id`;
- `required`;
- `reason`;
- `scope[]`;
- `status` (`NOT_REQUIRED`, `PENDING`, `APPROVED`, `DENIED`, `EXPIRED`);
- request/approval timestamps;
- approver.

ARGUS shall pin and validate that ATLAS approval schema for actions that require governed authorization.

For synchronization, ARGUS only needs to reference validated ATLAS approval objects by approval ID and verify that the approval scope covers the proposed action/target/material impact. ARGUS does not decide the actual approval requirement; ATLAS does.

## 7. Handoff validation

Before dependent ARGUS execution in `ATLAS_GOVERNED` mode:

1. validate the incoming handoff against the pinned ATLAS handoff schema;
2. verify `producer = ATLAS_OS`;
3. verify `consumer = ARGUS` for ARGUS execution;
4. recompute canonical SHA-256 excluding `payload_sha256` and require exact equality;
5. verify supported contract version;
6. enforce handoff state:
   - `READY` → normal execution;
   - `PARTIAL` → execute only while preserving unresolved material/risk flags;
   - `BLOCKED` → dependent ARGUS execution prohibited;
7. create the local synchronization execution state only after these checks succeed.

## 8. ARGUS local synchronization lifecycle

The local synchronization state machine is implementation metadata; it does not add ATLAS handoff states.

Success path:

`RECEIVED → VALIDATED → ACCEPTED → ACTIVE → RESULT_READY → RETURNED`

Failure/control states:

- `REJECTED` — contract/consumer/state not acceptable;
- `INVALID` — schema or digest failure;
- `BLOCKED` — upstream ATLAS handoff is BLOCKED;
- `SUPERSEDED_PENDING_ATLAS` — ARGUS found material evidence that may change ATLAS-owned context;
- `STALE` — handoff/result no longer current for the execution;
- `FAILED` — execution failed and requires retry/resume evaluation.

These states describe ARGUS synchronization execution only. They never replace ATLAS execution/failure states.

## 9. Synchronization identity and replay protection

Each governed ARGUS execution receives:

```yaml
sync_execution_id: ARGUS-SYNC-<stable-unique-id>
attempt: 1
```

Rules:

- one handoff may support multiple attempts of the same synchronization execution;
- retry increments `attempt` and does not create a new ATLAS handoff by itself;
- a new ATLAS handoff starts a new synchronization execution;
- a completed or superseded synchronization execution cannot silently become active again;
- results from previous handoffs cannot satisfy a newer handoff;
- repeated processing of an already accepted result is idempotent and must not duplicate canonical mutations.

## 10. Context-change invalidation

ARGUS may discover evidence that materially affects ATLAS-owned classification/alignment, for example:

- jurisdiction;
- operator/supplier industry classification;
- product/service/capability classification;
- lifecycle or stakeholder classification;
- sensitivity/risk flags;
- applicable law, standard or professional framework.

ARGUS must not silently rewrite upstream context.

Instead it emits a structured upstream-change finding:

```yaml
upstream_context_change:
  detected: true
  affected_facets: []
  evidence_refs: []
  reason: "..."
```

The current local synchronization state becomes `SUPERSEDED_PENDING_ATLAS` for dependent work.

Continuation requires:

`ARGUS finding → ATLAS reclassification/realignment → new handoff_id + payload_sha256 → new ARGUS synchronization execution`

Already-valid independent findings may be retained as evidence, but dependent conclusions must not proceed under the superseded context.

## 11. Exact return correlation

Before emitting an `ATLAS_GOVERNED` result, ARGUS must verify that its upstream receipt matches the active handoff exactly:

```text
result.upstream_handoff.contract_version == handoff.contract_version
result.upstream_handoff.handoff_id        == handoff.handoff_id
result.upstream_handoff.payload_sha256    == handoff.payload_sha256
result.upstream_handoff.consumer          == ARGUS
result.upstream_handoff.status            == ACCEPTED
```

The active handoff digest must also still verify.

Any mismatch yields `VALIDATION_FAILED`; no usable governed domain result is emitted.

A receipt from a superseded handoff is stale even if internally valid.

## 12. Failure-state mapping

ARGUS synchronization errors shall map to ATLAS's existing runtime failure vocabulary rather than inventing competing generic failure semantics.

| Synchronization condition | ATLAS-compatible failure |
|---|---|
| Invalid schema/digest/correlation | `VALIDATION_FAILED` |
| Upstream handoff BLOCKED | `BLOCKED` |
| Required dependency failed | `DEPENDENCY_FAILED` |
| Required capability unavailable | `CAPABILITY_UNAVAILABLE` |
| Evidence insufficient for dependent conclusion | `EVIDENCE_INSUFFICIENT` |
| Canonical mutation awaiting governed approval | `AUTHORIZATION_REQUIRED` |
| Material result not adequately verified | `UNVERIFIED` |
| Partial but usable context/result | `PARTIAL` |

The ARGUS local synchronization state and ATLAS-compatible failure code are separate fields.

## 13. Retry and resume

Retry and resume are distinct.

### Retry

Retry is another attempt of the same synchronization execution against the same validated handoff when the upstream context is still current.

### Resume

Resume must never continue from memory alone. It shall:

1. reload persisted synchronization metadata;
2. reload/reconcile the actual current ARGUS canonical state relevant to the work;
3. revalidate the pinned ATLAS compatibility contract;
4. revalidate the original handoff schema and digest;
5. verify the handoff has not been superseded by a newer synchronization execution;
6. verify pending approval/dependency state against actual current state;
7. increment `attempt`;
8. resume only if all dependent assumptions remain valid.

If ATLAS-owned context changed, resume fails closed and requires a new handoff.

## 14. Decision/action/authorization separation

ARGUS analytical decisions and canonical mutations remain distinct.

Example:

```yaml
decision: PROMOTE_TO_PX
proposed_domain_actions:
  - action: CREATE_PX_OPPORTUNITY
    target_argus_id: null
    rationale: "..."
    reversible: false
```

ARGUS may classify a proposed action as potentially destructive, irreversible, security-sensitive or a major canonical-state change for advisory purposes only.

ATLAS remains authoritative for whether approval is required.

A governed mutation may execute only when:

1. the originating synchronization execution is current and exactly correlated;
2. the proposed action matches the action being authorized;
3. any required ATLAS approval object validates against the pinned ATLAS approval schema;
4. approval status is `APPROVED` or ATLAS explicitly determines `NOT_REQUIRED`;
5. approval scope covers the described action, target and material impact;
6. the mutation implementation remains idempotent;
7. outcome is independently verified after mutation.

Permanent PX creation, destructive merge, identity reassignment and other major canonical-state changes remain subject to ATLAS approval controls.

## 15. Synchronization receipt

ARGUS shall persist a compact synchronization receipt as execution/interoperability evidence, not as an eighth Master Registry record type.

Candidate shape:

```yaml
sync_execution_id:
attempt:
mode: ATLAS_GOVERNED

atlas:
  version:
  commit:
  handoff_contract_version:
  handoff_id:
  payload_sha256:

argus:
  version:
  result_sha256:

state:
started_at:
completed_at:

context_change_detected:
upstream_refresh_required:

proposed_actions: []
approval_refs: []
authorized_actions: []

failure_state:
resume_from:
```

The receipt must be schema-valid and deterministic for material correlation fields. It must not duplicate the full handoff, result, evidence set or registry record.

## 16. Persistence boundary

ARGUS synchronization receipts are execution/interoperability evidence.

They do not replace:

- ARGUS Master Registry canonical domain state;
- ATLAS task-state persistence;
- ATLAS Library artifacts/receipts.

An ATLAS Library save does not prove an ARGUS canonical mutation. An ARGUS canonical mutation does not prove completion of the ATLAS task persistence stage.

## 17. Compatibility and upgrade policy

ATLAS remains upstream authority.

When any pinned ATLAS source changes:

1. current ARGUS production compatibility stays pinned to the last approved baseline;
2. CI marks the new ATLAS baseline unsupported until explicitly reviewed;
3. compatibility analysis determines whether change is:
   - byte-only/non-semantic;
   - backward compatible;
   - contract-breaking;
4. ARGUS updates local copies/hashes only through a reviewed compatibility PR;
5. synchronization tests must pass against the proposed ATLAS baseline before the compatibility declaration changes;
6. no automatic ATLAS mutation is permitted from ARGUS.

ARGUS version changes alone do not require ATLAS changes unless ARGUS asks for new upstream semantics; the default is to adapt ARGUS to the existing ATLAS contract.

## 18. Executable conformance tests

Implementation must add tests covering at minimum:

1. **ATLAS source compatibility** — pinned local contract copies match approved upstream source bytes/hashes.
2. **Unsupported version rejection** — unsupported ATLAS/handoff version fails closed.
3. **Digest integrity** — post-production handoff mutation is detected.
4. **Consumer enforcement** — handoff for another consumer cannot drive ARGUS.
5. **BLOCKED rejection** — dependent ARGUS execution cannot begin.
6. **PARTIAL preservation** — unresolved material/risk flags cannot disappear.
7. **Exact return correlation** — mismatched version/ID/hash/consumer/status fails.
8. **Context invalidation** — material upstream-context change supersedes the synchronization execution for dependent work.
9. **Stale-result rejection** — older handoff result cannot satisfy current handoff.
10. **Retry behavior** — same handoff retry increments attempt without fabricating a new handoff.
11. **Resume reconciliation** — actual persisted state and handoff validity are checked before continuation.
12. **Failure mapping** — conditions map to the existing ATLAS failure vocabulary.
13. **Approval reuse** — ATLAS approval schema is reused; no duplicate authorization schema is introduced.
14. **Mutation gating** — major canonical mutation cannot execute without valid current ATLAS authorization where required.
15. **Approval scope** — an approved but out-of-scope approval cannot authorize a different action/target.
16. **Idempotence** — repeated accepted result/action processing does not duplicate canonical mutations.
17. **Synchronization receipt validation** — receipt shape/correlation fields validate.
18. **Standalone isolation** — standalone ARGUS remains possible but cannot masquerade as ATLAS-governed execution.
19. **ATLAS immutability** — ARGUS implementation changes no `atlas-os` file and tests are read/fixture based.
20. **Production boundary** — no ARGUS live registry mutation or manifest authority change is part of this synchronization hardening gate.

## 19. Planned ARGUS repository changes

Expected implementation paths:

```text
contracts/atlas/
  domain-context-handoff-v1.schema.json          # existing pinned copy
  domain-handoff-receipt-v1.schema.json          # new pinned copy
  approval-v1.schema.json                        # new pinned copy
  synchronization-compatibility.yaml             # approved upstream hashes/versions

schemas/
  atlas-argus-sync-receipt.schema.json

argus_runtime/ or tools/
  atlas_sync.py                                   # pure validation/lifecycle helpers

tests/
  test_atlas_argus_synchronization.py
  fixtures/atlas-sync/...

docs/architecture/
  atlas-argus-synchronization-v1.md               # durable architecture copy if useful
```

No change is planned to the ATLAS repository.

No live ARGUS registry/index/manifest migration belongs in this gate.

## 20. Non-goals

This design does not:

- modify ATLAS OS;
- add a second execution spine;
- add a second approval framework;
- make ARGUS a task scheduler;
- activate Bangladesh Procurement v2;
- activate Registry v0.3;
- migrate live canonical records;
- redesign the seven ARGUS Master Registry record types;
- make ATLAS Library the ARGUS canonical store;
- make ARGUS evidence assurance replace ATLAS verification;
- automatically upgrade ATLAS compatibility when upstream files change.

## 21. Acceptance criteria

The synchronization hardening gate is complete only when all are true:

1. ATLAS repository remains byte/state unchanged from the approved baseline.
2. ARGUS declares one approved ATLAS compatibility baseline with verifiable hashes.
3. all pinned ATLAS runtime schemas used by ARGUS match the approved ATLAS source.
4. handoff schema, digest, consumer and state are executable preconditions to governed ARGUS execution.
5. exact result correlation is executable, not documentation-only.
6. material upstream-context changes invalidate dependent work and require a new ATLAS handoff.
7. retry and resume behavior is deterministic and tested.
8. ATLAS failure vocabulary is reused.
9. ATLAS approval schema is reused and action scope is checked.
10. destructive/major canonical mutations remain impossible without required current authorization.
11. synchronization receipts are machine-valid and do not become canonical intelligence records.
12. standalone mode remains distinct from ATLAS-governed execution.
13. full ARGUS regression suite passes.
14. no live canonical data or production-authority switch occurs in this gate.
15. architecture/validation evidence is persisted only after post-merge readback succeeds.

## 22. Final invariant

For every Access Asia production ARGUS execution:

1. ATLAS owns the governing task, classification, alignment, plan and approval context.
2. ARGUS receives and validates one current immutable ATLAS handoff.
3. ARGUS may enrich domain meaning but cannot redefine upstream authority.
4. a material upstream-context change stops dependent execution until ATLAS issues a new handoff.
5. ARGUS returns a result correlated exactly to the handoff it consumed.
6. ATLAS verifies the correlation and material claims before accepting the result.
7. ARGUS canonical mutations execute only under the applicable ATLAS authorization state.
8. execution synchronization state, ARGUS canonical domain state and ATLAS task persistence remain separate.

> **ATLAS governs the work; ARGUS understands the opportunity; the synchronization contract proves they are operating on the same governed context.**
