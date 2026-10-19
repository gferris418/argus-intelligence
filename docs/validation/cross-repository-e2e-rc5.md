# ATLAS ↔ ARGUS Cross-Repository E2E — rc.5

**Status:** PENDING_REMOTE_PR_E2E  
**ARGUS candidate:** `2.0.0-rc.5`  
**ARGUS PR:** `#35` (`release/argus-rc5-atlas-rc12`)  
**ATLAS baseline:** `2.0.0-rc.12`  
**ATLAS commit:** `45a8bf828abb1ab5242c54f798c5c074fd797285`  
**ATLAS control revision:** `chatgpt-bootstrap-2026-10-19-r4`  
**Domain Context Handoff:** `1.1.0`

## Purpose

Refresh the production compatibility proof after ATLAS introduced provider-independent capability-admission, untrusted-content assurance, memory-integrity, forecasting/foresight, and learning/calibration governance in rc.12.

The compatibility refresh must prove the real producer-consumer-return path rather than infer compatibility from unchanged schema text or unit tests alone.

## Invariants under test

1. The exact ATLAS rc.12 commit is checked out, not a moving branch.
2. ATLAS produces the governed classification/alignment and domain-context handoff.
3. ARGUS validates the pinned handoff contract and operator-pinned ATLAS attestation.
4. ARGUS returns a correlated rc.5 synchronization receipt and domain result.
5. ATLAS verifies the returned handoff identity and result correlation.
6. Text and NDJSON paths both complete through the same real ATLAS and ARGUS runtime boundaries.
7. The fixture performs no external evidence collection and no canonical Registry write.
8. The ARGUS contract suite passes on the same PR head.
9. The ATLAS activation contract remains byte-identical to the hash already pinned by ATLAS: `sha256:3aa1abac8283e7f40418fe04e9882a5d241a0c6b323bcfab855a6f4eca74bac7`.

## Evidence gates

| Gate | Required result | Current state |
|---|---|---|
| TDD RED | New rc.5/rc.12 expectations fail only because production still reports rc.4/rc.11 | PASS — 182 tests, 5 intended version/workflow failures |
| ARGUS Contract Tests | Entire suite passes | PENDING |
| Cross-repository E2E | `tests/cross_repo` passes against exact ATLAS commit | PENDING |
| Text path | `ATLAS→ARGUS VERIFIED`, route `ACTIVATE`, receipt `RETURNED` | PENDING |
| NDJSON path | `atlas_handoff → argus_result → atlas_verified` | PENDING |
| Exact pin | Runtime descriptor and workflow use the same ATLAS commit | PENDING |
| No canonical mutation | Fixture reports no Registry writes | PENDING |

## Historical integrity

`docs/validation/cross-repository-e2e-rc4.md` remains an immutable historical validation record for the rc.4 / ATLAS rc.11 baseline. This rc.5 record supersedes it only as the current compatibility evidence after all gates above pass.

## Completion rule

Do not change this record to `REMOTE_CI_PASS`, do not merge PR #35, and do not describe rc.5 as validated against rc.12 until both GitHub Actions workflows succeed on the exact final PR head. Record the final workflow run IDs and tested head SHA when that evidence exists.
