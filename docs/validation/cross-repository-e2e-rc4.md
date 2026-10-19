# ATLAS–ARGUS cross-repository validation

**Status:** LOCAL_EXACT_HEAD_PASS / REMOTE_MANUAL_WORKFLOW_READY  
**Validated on:** 2026-10-19  
**Mode:** TEST_ONLY / READ_ONLY

## Exact inputs

- ATLAS OS `2.0.0-rc.11` at `3bfad80a84a8e7fa0bd68795b0e4442f55df9948`
- ARGUS Intelligence `2.0.0-rc.4` based on `5192bedffcb9b86b786620d22fb0ae64a80811d8`
- Objective: `Assess coastal surveillance radar for Bangladesh Navy`

## Executed path

```text
ATLAS execute
→ ATLAS classify_domain_context
→ ATLAS align_domain_practices
→ ATLAS prepare_domain_context_handoff
→ ATLAS route_domain_method = ACTIVATE
→ ATLAS attest_control_record
→ ARGUS Argus.analyze
→ ARGUS synchronization state = RETURNED
→ ATLAS verify_domain_handoff_receipt = true
```

Observed result:

```text
ATLAS→ARGUS VERIFIED | Route ACTIVATE | Receipt RETURNED
Context PARTIAL | Decision INVESTIGATE | Maturity I1
```

The `PARTIAL` state is expected: `lifecycle-stage` remains unresolved and is
preserved through the handoff rather than guessed.

## Boundaries

- Ephemeral in-memory Ed25519 key; no production trust-store claim.
- No external source acquisition.
- No Master Registry mutation.
- No ChatGPT or Work deployment proof.
- Remote execution requires the separately configured read-only
  `ATLAS_READ_TOKEN` secret because GitHub scopes the default token to one
  private repository.
