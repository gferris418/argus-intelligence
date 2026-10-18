# ARGUS 2.0.0-rc.3 runtime simplification validation

**Date:** 2026-10-19  
**Status:** REMOTE_CI_PASS
**Validated implementation head:** `2269c961d2fa1f7df648f6b7f8cc2d223b53cb1f`
**Exact-head CI:** PASS — [Contract Tests run 39157293626](https://github.com/gferris418/argus-intelligence/actions/runs/39157293626)
**ATLAS baseline:** `2.0.0-rc.10` at `673a676a0b23518dad1a295a7cd36b5b75aa064e`

## Outcome

ARGUS now has one preferred governed analysis interface: `Argus.analyze(AnalysisEnvelope)`. The interface validates the authenticated ATLAS handoff, advances the synchronization lifecycle, invokes one injected domain method, protects governance-owned result fields, computes the result digest, verifies exact correlation and returns the final receipt. Existing synchronization functions remain available for compatibility, retry/resume and action authorization.

No canonical registry record is written by this interface.

## Local evidence

- focused façade and synchronization tests: **PASS**;
- complete local suite: **177 tests PASS**;
- domain methods cannot supply `governance_mode`, synchronization identity, result digest or upstream receipt fields;
- input handoffs remain unmodified;
- successful analysis returns a `RETURNED` receipt with the exact bound result digest;
- domain-method failure returns a `FAILED` receipt with `DEPENDENCY_FAILED`, preserving retry/resume state;
- ARGUS receipt version: `2.0.0-rc.3`;
- `git diff --check`: **PASS**.

## Controlled validation benchmark

Workload: validate the same schema-valid ATLAS handoff 200 times with Python 3.12 and jsonschema 4.26.0 in the same environment.

| Validation method | Total | Mean |
|---|---:|---:|
| One-shot `jsonschema.validate` | 1,564.052 ms | 7.8203 ms |
| Reusable compiled Draft 2020-12 validator | 30.157 ms | 0.1508 ms |

Observed speedup for this validation step: approximately **51.9×**. This is a controlled local measurement, not a universal end-to-end latency claim. Cryptographic verification, domain analysis, source acquisition and network time are outside this microbenchmark.

## Compatibility disposition

- ATLAS remains execution, planning, approval and delivery authority: **yes**;
- ARGUS still returns the existing Domain Result and synchronization receipt schemas: **yes**;
- low-level synchronization functions removed: **no**;
- Master Registry mutation introduced: **no**;
- Bangladesh Procurement v2 activated: **no**;
- Registry v0.3 activated: **no**.
