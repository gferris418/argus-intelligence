# ATLAS OS ↔ ARGUS Synchronization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement an ARGUS-side synchronization runtime that enforces the approved ATLAS OS handoff, correlation, invalidation, retry/resume, and approval semantics without changing ATLAS OS or activating any pending ARGUS production migration.

**Architecture:** ATLAS OS remains the immutable upstream governance authority. ARGUS pins the approved ATLAS 2.0.0-rc.8 contracts at commit `51130014352b30000f847623691f56390cf174aa`, validates incoming handoffs and approvals against those contracts, maintains only local synchronization-execution state, and returns exactly correlated domain results. Synchronization receipts are interoperability evidence, not Master Registry records.

**Tech Stack:** Python 3.12 standard library, `jsonschema==4.23.0`, JSON Schema Draft 2020-12, `unittest`, GitHub Actions Contract Tests.

**Spec:** `docs/superpowers/specs/2026-10-18-atlas-argus-synchronization-design.md`

## Global Constraints

- Do not further modify `gferris418/atlas-os` during ARGUS implementation; approved ATLAS baseline is `2.0.0-rc.8` at `51130014352b30000f847623691f56390cf174aa`.
- Handoff contract version is `1.1.0`; ARGUS adapts to ATLAS rather than redefining ATLAS semantics.
- Bangladesh Procurement v1.3 remains the active ARGUS production procurement standard; no v2/v0.3 activation or live registry mutation belongs to this plan.
- Reuse the ATLAS approval schema; do not introduce a second authorization schema.
- `contracts/atlas/synchronization-compatibility.yaml` shall contain JSON syntax (valid YAML 1.2) so runtime/tests can parse it with Python `json` and no new YAML dependency.
- All synchronization helpers in `tools/atlas_sync.py` are pure with respect to canonical ARGUS state: they return values or raise fail-closed exceptions and do not write `data/registry/`.
- `ATLAS_GOVERNED` and `STANDALONE` remain distinct; standalone execution must never emit a forged ATLAS synchronization receipt.
- TDD is mandatory: each behavior is first demonstrated failing, then minimally implemented, then verified before the next task.

## Review Focus

- Tampered handoff payload with an otherwise schema-valid object must fail digest verification rather than reach ARGUS execution — Task 2.
- `PARTIAL` handoff must retain unresolved material and risk flags through the local synchronization receipt/result boundary — Task 2.
- A result correlated to an older handoff must be rejected after a newer handoff becomes active — Task 3.
- An ATLAS approval that is valid but does not cover every `expected_scope` element must fail closed — Task 4.
- Resume after actual ARGUS canonical-state fingerprint drift must fail and require reconciliation rather than incrementing attempt — Task 3.

---

## File Structure

**Create**
- `contracts/atlas/domain-handoff-receipt-v1.schema.json` — exact read-only copy of approved ATLAS receipt schema.
- `contracts/atlas/approval-v1.schema.json` — exact read-only copy of approved ATLAS approval schema.
- `contracts/atlas/synchronization-compatibility.yaml` — approved ATLAS version/commit and exact SHA-256 pins for normative synchronization sources.
- `schemas/atlas-argus-sync-receipt.schema.json` — compact ARGUS synchronization receipt contract.
- `tools/atlas_sync.py` — pure synchronization validation/lifecycle/authorization helpers.
- `tests/test_atlas_argus_synchronization.py` — executable synchronization contract tests.
- `tests/fixtures/atlas-sync/ready-handoff.json` — valid READY handoff with correct digest.
- `tests/fixtures/atlas-sync/partial-handoff.json` — valid PARTIAL handoff with unresolved/risk content.
- `tests/fixtures/atlas-sync/blocked-handoff.json` — valid BLOCKED handoff.
- `tests/fixtures/atlas-sync/approval-approved.json` — schema-valid required+APPROVED approval.
- `tests/fixtures/atlas-sync/approval-not-required.json` — schema-valid required=false+NOT_REQUIRED approval.
- `docs/validation/atlas-argus-synchronization-v1.md` — final evidence/decision record.

**Modify**
- `tests/test_atlas_domain_handoff_contract.py` — extend static pinning tests to reference the synchronization compatibility descriptor and copied receipt/approval contracts.
- `alignments/atlas-os.md` — document executable synchronization runtime and receipt without changing ownership boundaries.
- `argus-intelligence.yaml` — add candidate synchronization validation references only; do not change production procurement/registry authority.

## Task 1: Pin the approved ATLAS synchronization sources

**Files:**
- Create: `contracts/atlas/domain-handoff-receipt-v1.schema.json`
- Create: `contracts/atlas/approval-v1.schema.json`
- Create: `contracts/atlas/synchronization-compatibility.yaml`
- Modify: `tests/test_atlas_domain_handoff_contract.py`

**Interfaces:**
- Consumes: approved ATLAS commit `51130014352b30000f847623691f56390cf174aa` and exact upstream bytes from `schemas/domain-context-handoff.schema.json`, `schemas/domain-handoff-receipt.schema.json`, `schemas/approval.schema.json`, `spec/runtime.yaml`, `spec/approvals.yaml`, `spec/verification.yaml`.
- Produces: compatibility descriptor parsed by `json.loads(Path(...).read_text())`; local receipt and approval schema paths used by `tools/atlas_sync.py`.

- [ ] **Step 1: Write failing compatibility tests**

Add tests named:

```python
def test_sync_descriptor_pins_exact_atlas_baseline(): ...
def test_pinned_handoff_copy_hash_matches_descriptor(): ...
def test_pinned_receipt_copy_hash_matches_descriptor(): ...
def test_pinned_approval_copy_hash_matches_descriptor(): ...
def test_sync_descriptor_contains_no_placeholder_hashes(): ...
```

Assertions must require ATLAS version `2.0.0-rc.8`, commit `51130014352b30000f847623691f56390cf174aa`, contract version `1.1.0`, and 64-character lowercase SHA-256 values for all six source entries.

- [ ] **Step 2: Run the focused tests and confirm RED**

Run: `python -m unittest tests.test_atlas_domain_handoff_contract -v`

Expected: FAIL because copied contracts/descriptor do not yet exist.

- [ ] **Step 3: Copy the exact upstream receipt and approval schemas and compute source SHA-256 pins**

Copy exact ATLAS bytes into the two new schema files. Compute hashes with `hashlib.sha256(bytes).hexdigest()` for all six approved upstream sources; write actual values into `synchronization-compatibility.yaml` using JSON syntax.

- [ ] **Step 4: Run the focused tests and confirm GREEN**

Run: `python -m unittest tests.test_atlas_domain_handoff_contract -v`

Expected: PASS.

- [ ] **Step 5: Commit**

Commit message: `Pin ATLAS synchronization compatibility contracts`.

## Task 2: Implement handoff integrity and local synchronization lifecycle

**Files:**
- Create: `tools/atlas_sync.py`
- Create: `schemas/atlas-argus-sync-receipt.schema.json`
- Create: `tests/test_atlas_argus_synchronization.py`
- Create: `tests/fixtures/atlas-sync/ready-handoff.json`
- Create: `tests/fixtures/atlas-sync/partial-handoff.json`
- Create: `tests/fixtures/atlas-sync/blocked-handoff.json`

**Interfaces:**
- Consumes: Task 1 compatibility descriptor and pinned schemas.
- Produces these exact public interfaces in `tools/atlas_sync.py`:
  - `class SyncValidationError(ValueError):` with public attributes `code: str` and `atlas_failure_state: str`.
  - `canonical_handoff_sha256(handoff: dict[str, Any]) -> str`
  - `validate_handoff(handoff, *, atlas_attestation, trusted_public_keys) -> None`
  - `new_sync_receipt(sync_execution_id, handoff, started_at, *, atlas_attestation, trusted_public_keys) -> dict`
  - `transition_sync(receipt: dict[str, Any], target_state: str) -> dict[str, Any]`
  - `validate_sync_receipt(receipt: dict[str, Any]) -> None`
  - `mark_upstream_context_change(receipt: dict[str, Any], affected_facets: list[str], evidence_refs: list[str], reason: str) -> dict[str, Any]`

- [ ] **Step 1: Write failing schema/lifecycle tests**

Add tests for valid READY start; tampered digest rejection; wrong consumer rejection; unsupported contract version rejection; BLOCKED rejection; PARTIAL preservation; receipt schema validation; valid lifecycle transitions; illegal transition rejection; and context-change transition to `SUPERSEDED_PENDING_ATLAS`.

For PARTIAL preservation assert the receipt carries the exact handoff `unresolved_material` and `risk_flags` snapshots.

- [ ] **Step 2: Run focused tests and confirm RED**

Run: `python -m unittest tests.test_atlas_argus_synchronization -v`

Expected: FAIL because schema/runtime helpers do not exist.

- [ ] **Step 3: Implement the synchronization receipt schema**

Required receipt fields: `sync_execution_id`, `attempt`, `mode`, `atlas`, `argus`, `state`, `started_at`, `completed_at`, `unresolved_material`, `risk_flags`, `context_change_detected`, `upstream_refresh_required`, `proposed_actions`, `approval_refs`, `authorized_actions`, `failure_state`, `resume_from`.

State enum: `RECEIVED`, `VALIDATED`, `ACCEPTED`, `ACTIVE`, `RESULT_READY`, `RETURNED`, `REJECTED`, `INVALID`, `BLOCKED`, `SUPERSEDED_PENDING_ATLAS`, `STALE`, `FAILED`.

Failure enum/null: ATLAS runtime vocabulary only: `BLOCKED`, `PARTIAL`, `UNVERIFIED`, `CAPABILITY_UNAVAILABLE`, `AUTHORIZATION_REQUIRED`, `EVIDENCE_INSUFFICIENT`, `DEPENDENCY_FAILED`, `VALIDATION_FAILED`, or `null`.

- [ ] **Step 4: Implement the Task 2 public functions**

Canonical digest: UTF-8 JSON, sorted keys, compact separators, excluding `payload_sha256`, returned as `sha256:<64 hex>`.

`validate_handoff` must Draft-2020-12 validate, verify the detached Ed25519 ATLAS attestation with an operator-pinned public key, enforce the 24-hour activation window, independently derive state, enforce consumer `ARGUS`, supported version, digest equality, and fail closed on `BLOCKED`.

Lifecycle transitions are explicit allow-list transitions from the spec; no arbitrary state mutation.

- [ ] **Step 5: Run focused tests and confirm GREEN**

Run: `python -m unittest tests.test_atlas_argus_synchronization -v`

Expected: PASS for Task 2 tests.

- [ ] **Step 6: Commit**

Commit message: `Add ATLAS ARGUS handoff synchronization runtime`.

## Task 3: Add exact result correlation, stale/replay protection, retry and resume reconciliation

**Files:**
- Modify: `tools/atlas_sync.py`
- Modify: `tests/test_atlas_argus_synchronization.py`
- Modify: `schemas/domain-result.schema.json` only if needed to carry synchronization metadata without duplicating the upstream receipt.

**Interfaces:**
- Consumes: Task 2 receipt/lifecycle functions.
- Produces:
  - `validate_result_correlation(result, handoff, receipt, *, trusted_public_keys) -> dict`
  - `retry_sync(receipt, handoff, *, trusted_public_keys) -> dict`
  - `resume_sync(receipt: dict[str, Any], handoff: dict[str, Any], *, active_sync_execution_id: str, stored_registry_fingerprint: str, actual_registry_fingerprint: str) -> dict[str, Any]`
  - `map_atlas_failure(condition: str) -> str`

- [ ] **Step 1: Write failing tests**

Cover exact version/ID/hash/consumer/status correlation; stale result from old handoff; retry increments attempt while preserving `sync_execution_id`; retry rejects superseded/returned execution; resume rejects different active sync ID; resume rejects registry fingerprint drift; resume revalidates handoff; and each synchronization condition maps to the existing ATLAS failure vocabulary.

- [ ] **Step 2: Run focused tests and confirm RED**

Run: `python -m unittest tests.test_atlas_argus_synchronization -v`

Expected: FAIL on the new Task 3 tests.

- [ ] **Step 3: Implement Task 3 functions**

`validate_result_correlation` must also re-run `validate_handoff` and require the local receipt not be `SUPERSEDED_PENDING_ATLAS`, `STALE`, `BLOCKED`, `INVALID`, or `FAILED`.

`resume_sync` succeeds only when `active_sync_execution_id == receipt.sync_execution_id` and stored/actual registry fingerprints are identical; then it increments attempt and returns `ACTIVE`.

- [ ] **Step 4: Run focused tests and confirm GREEN**

Run: `python -m unittest tests.test_atlas_argus_synchronization -v`

Expected: PASS.

- [ ] **Step 5: Commit**

Commit message: `Enforce ATLAS ARGUS correlation retry and resume`.

## Task 4: Reuse ATLAS approval semantics and gate proposed mutations idempotently

**Files:**
- Modify: `tools/atlas_sync.py`
- Modify: `tests/test_atlas_argus_synchronization.py`
- Create: `tests/fixtures/atlas-sync/approval-approved.json`
- Create: `tests/fixtures/atlas-sync/approval-not-required.json`

**Interfaces:**
- Consumes: pinned `contracts/atlas/approval-v1.schema.json`, current synchronization receipt, ARGUS proposed action object from `schemas/domain-result.schema.json`.
- Produces:
  - `validate_action_authorization(action, approval, expected_scope, receipt, *, approval_attestation, trusted_public_keys) -> None`
  - `action_idempotency_key(action: dict[str, Any]) -> str`
  - `authorize_action(receipt, action, approval, expected_scope, *, approval_attestation, trusted_public_keys) -> dict`

- [ ] **Step 1: Write failing approval/idempotence tests**

Cover required+APPROVED success; required+PENDING/DENIED/EXPIRED rejection; `NOT_REQUIRED` rejection for canonical mutation; untrusted/fabricated attestation rejection; subset scope success; out-of-scope rejection; fuzzy string similarity rejection; superseded receipt rejection; deterministic cross-execution idempotency key; and repeated authorization not duplicating `authorized_actions`.

- [ ] **Step 2: Run focused tests and confirm RED**

Run: `python -m unittest tests.test_atlas_argus_synchronization -v`

Expected: FAIL on new Task 4 tests.

- [ ] **Step 3: Implement Task 4 functions**

Approval validation uses the exact pinned ATLAS schema plus a detached Ed25519 attestation verified with an operator-pinned ATLAS public key. Scope test is only `set(expected_scope).issubset(set(approval["scope"]))`; no normalization/fuzzy matching. `authorize_action` records approval ID and one action-derived deterministic idempotency key; an existing same key returns an unchanged receipt.

- [ ] **Step 4: Run focused tests and confirm GREEN**

Run: `python -m unittest tests.test_atlas_argus_synchronization -v`

Expected: PASS.

- [ ] **Step 5: Commit**

Commit message: `Gate ARGUS mutations with ATLAS approvals`.

## Task 5: Integrate compatibility declaration, documentation, and full conformance evidence

**Files:**
- Modify: `alignments/atlas-os.md`
- Modify: `argus-intelligence.yaml`
- Modify: `tests/test_atlas_domain_handoff_contract.py`
- Modify: `tests/test_atlas_argus_synchronization.py`
- Create: `docs/validation/atlas-argus-synchronization-v1.md`

**Interfaces:**
- Consumes: all Task 1-4 runtime/contracts.
- Produces: documented synchronization contract, manifest references, and final validation record; no production activation.

- [ ] **Step 1: Add failing integration/boundary tests**

Require the ARGUS manifest to reference the synchronization descriptor and sync receipt schema while still retaining `bangladesh_procurement_standard_version: 1.3.0`, `atlas_change_required: false`, and `standalone_argus: false` for Access Asia production. Assert no eighth Master Registry record type is introduced. Assert standalone mode cannot pass `validate_result_correlation` as governed execution without a handoff.

- [ ] **Step 2: Run the full suite and capture RED**

Run: `python -m unittest discover -s tests -p 'test_*.py' -v`

Expected: existing tests green; only newly added integration assertions fail.

- [ ] **Step 3: Update alignment/manifest and write validation record**

Document the executable runtime and compatibility upgrade rule without changing ATLAS ownership or production authority. Validation record must state exact ATLAS commit, ARGUS base/head, compatibility hashes, RED/GREEN test receipts, scope review, and explicit `ATLAS unchanged during ARGUS implementation: yes` / `live registry mutation: false` / `v2 activation: false`.

- [ ] **Step 4: Run the complete local contract suite**

Run: `python -m unittest discover -s tests -p 'test_*.py' -v`

Expected: all tests PASS.

- [ ] **Step 5: Open PR and verify GitHub Actions**

Open a PR against `main`; require Contract Tests workflow success on the exact final head.

- [ ] **Step 6: Perform base→head scope review**

Confirm changed files are limited to synchronization contracts/runtime/tests/docs/manifest references. Explicitly reject merge if the diff contains any `atlas-os` change, `data/registry/current/*.json`, `data/registry/current-index.json`, `data/registry/records.jsonl`, Bangladesh v2 production activation, or Registry v0.3 production activation.

- [ ] **Step 7: Merge with exact-head guard, then verify `main`**

Require post-merge Contract Tests success on the merge commit and read back `argus-intelligence.yaml`, synchronization descriptor, validation record, and current ATLAS `main` SHA.

- [ ] **Step 8: Commit final documentation changes if they were not already part of the verified head**

No unverified post-test implementation changes are permitted; if documentation changes after the final test head, rerun the complete suite before merge.

## Self-Review Result

- **Spec coverage:** All design sections are mapped: compatibility pinning (Task 1), handoff/lifecycle/context invalidation (Task 2), return correlation/retry/resume/failure mapping (Task 3), approval/action/idempotence (Task 4), persistence boundary/upgrade policy/production safety/conformance evidence (Task 5).
- **Step scan:** Every task contains an explicit RED test step, minimal implementation step, GREEN verification, and commit boundary.
- **Type consistency:** All later tasks consume the exact dictionary-based interfaces produced by `tools/atlas_sync.py`; receipt state names and ATLAS failure names match the approved spec.
- **Review Focus coverage:** tampering/PARTIAL in Task 2; stale replay and registry drift in Task 3; approval scope in Task 4.
- **Proportion:** Plan fixes interfaces and test obligations without embedding implementation bodies beyond algorithms explicitly fixed by ATLAS canonicalization/scope rules.
