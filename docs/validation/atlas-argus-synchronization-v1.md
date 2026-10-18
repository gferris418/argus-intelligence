# ATLAS–ARGUS synchronization v1 validation

**Date:** 2026-10-18
**Status:** LOCAL_IMPLEMENTATION_PASS_REMOTE_CI_PENDING
**ARGUS base:** `fe7ef26ed90cda49b4962b9ab7f707640c4ddc62`
**Validated implementation head:** `7c4315d4405aac8f5d97d29e4140601e0db6c567`
**ATLAS baseline:** `2.0.0-rc.8` at `51130014352b30000f847623691f56390cf174aa`

## Outcome

The design-only synchronization seam is now executable. ARGUS verifies detached Ed25519 attestations for ATLAS handoffs and approvals against operator-pinned public keys, derives handoff state independently, creates a schema-valid local synchronization receipt, rejects BLOCKED/tampered/stale/wrong-consumer inputs, preserves PARTIAL context, binds result digest to the exact execution attempt, reconciles retry/resume, and gates proposed actions with exact action-bound ATLAS approval objects.

The runtime is pure with respect to `data/registry/`. It returns synchronization state and authorization evidence but performs no canonical mutation.

## Compatibility pins

| ATLAS source | SHA-256 |
|---|---|
| `schemas/domain-context-handoff.schema.json` | `fb2d5f87d1b98c2403656ddb56ffc738027aeafcee1f42be6ebc389608545cc6` |
| `schemas/domain-handoff-receipt.schema.json` | `17abe08ed4574cd59eab1c6a0bba48d53a54d7d1116dd60ac14fbb1cb267b738` |
| `schemas/approval.schema.json` | `ee4ccefe38069a7a1add8c347f3c486214a237aa209eb00b437bf9983ed244b7` |
| `spec/runtime.yaml` | `fc6b5e01eab5942712d4a8153436f8f7e93c980ff1327f597affe86f7ede33ab` |
| `spec/approvals.yaml` | `2b6fdb13a0ef5aae3e1cbcb88de37abd2a6566678ba7899384de3521308eeaf0` |
| `spec/verification.yaml` | `8c996bde7445df429f5e15fa6225ad16e8823217f73362e26159ef83d04fb2ad` |

## Test evidence

The initial focused tests failed because `tools/atlas_sync.py`, synchronization contracts, lifecycle functions, correlation, resume, and authorization functions did not exist. Each boundary was then implemented and rerun before the next unit.

Final local command:

```text
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -p 'test_*.py' -v
Ran 173 tests — OK
```

Additional checks:

- all three local ATLAS schema copies are byte-identical to the pinned RC8 source;
- Ed25519 trust tests cover unknown keys, changed records, changed signatures, and fabricated approvals;
- identical handoffs derive the same synchronization execution identity, while results bind to one exact attempt and digest;
- dependency resolution succeeds with `pip install --dry-run --require-hashes --requirement requirements-test.lock`;
- GitHub Actions are commit-pinned and dependency audit is configured;
- `git diff --check` passes;
- no `data/registry/current/*.json`, index, JSONL, Bangladesh v2 authority, or Registry v0.3 authority changed.

## Boundary disposition

- ATLAS unchanged during ARGUS implementation after RC8 pin: **yes**
- ATLAS remains execution/planning/approval/delivery authority: **yes**
- live ARGUS registry mutation: **false**
- Bangladesh Procurement v2 activation: **false**
- Registry v0.3 activation: **false**
- eighth Master Registry record type: **false**
- standalone mode may forge governed synchronization evidence: **false**
- untrusted code may self-assert an ATLAS handoff or approval: **false**
- remote exact-head CI: **pending push**

Production activation remains `No` until canonical branch governance and exact-head remote CI are verified.

Residual infrastructure constraint: `ubuntu-24.04` and Python `3.12.12` remove floating major/minor labels, but GitHub-hosted runner images are still vendor-maintained rather than immutable image digests. Stronger runner-image immutability requires a separately governed self-hosted runner and is not introduced in this release candidate.
