# ARGUS Intelligence

ARGUS is Access Asia's government and public-sector opportunity-intelligence framework.

Its purpose is to identify credible business before formal tender publication, connect fragmented policy/project/funding/procurement evidence, prevent duplicate opportunity creation, prioritize decision-changing research, and promote commercially actionable signals into a permanent PX opportunity lineage. **PX activation does not mean submission activation:** under the Access Asia operating overlay, all tracked opportunity working files remain in Business Intelligence until formal response-package execution actually begins.

See [`ACCESS_ASIA.md`](ACCESS_ASIA.md) and [`profiles/access-asia-opportunity-lifecycle.yaml`](profiles/access-asia-opportunity-lifecycle.yaml) for the current Access Asia working-file lifecycle.

## Production relationship with ATLAS OS

Within the Access Asia governed environment, **ATLAS OS is the execution-governance backbone**. ARGUS is a nested specialist domain method and does not create a second execution spine.

ATLAS owns generic domain classification, taxonomy/product/service/capability context, material risk flags, and applicable law/standards/framework alignment. Before ARGUS executes, ATLAS transfers that context through the governed **Domain Context Handoff v1.1**.

Canonical execution flow:

`User objective → ATLAS classification/alignment → ATLAS Domain Context handoff → ARGUS Contextualize → ARGUS domain method → ARGUS domain result + exact handoff receipt + proposed actions → ATLAS correlation verification/approval → authorized action(s) → ATLAS delivery`

ARGUS may enrich the ATLAS context for opportunity discovery—aliases, local terminology, adjacent solution classes, installed-base interpretation, supplier/competitor relevance, Bangladesh route implications—but it must not silently redefine ATLAS taxonomy or standards conclusions.

In Access Asia production, ARGUS rejects dependent execution on a `BLOCKED` handoff and returns the exact `handoff_id`, contract version and `payload_sha256` in every `ATLAS_GOVERNED` domain result. Standalone execution remains available for portability, testing, recovery, or non-Access-Asia implementations.

The preferred executable interface is `Argus.analyze(AnalysisEnvelope)` in [`tools/argus_runtime.py`](tools/argus_runtime.py). It owns handoff validation, synchronization transitions, domain-method invocation, protected result metadata, digest correlation, and the final return receipt. A domain-method failure carries a retryable `FAILED` receipt instead of losing execution state. Existing synchronization functions remain available for compatibility and recovery workflows.

```python
from tools.argus_runtime import AnalysisEnvelope, Argus

runtime = Argus(domain_method, trusted_public_keys=operator_pinned_keys)
outcome = runtime.analyze(AnalysisEnvelope(
    handoff=atlas_handoff,
    atlas_attestation=atlas_attestation,
    started_at="2026-10-19T01:00:00+06:00",
))
```

The synchronization runtime pins ATLAS `2.0.0-rc.12` at commit `45a8bf828abb1ab5242c54f798c5c074fd797285`, verifies detached Ed25519 ATLAS attestations with operator-pinned public keys, rejects tampering and stale/replayed results, preserves partial context, reconciles retry/resume against actual registry state, and binds proposed canonical actions to exact ATLAS approvals. Reusable compiled validators avoid reparsing unchanged schemas on every call. Neither runtime mutates the Master Registry by itself.

The complete seam can be tested without persistent keys, network access, or
registry writes. Compact text is the default; NDJSON is available for a
machine consumer:

```bash
python -m tools.live_smoke
python -m tools.live_smoke --format ndjson
```

The command is explicitly test-only and generates a fresh in-memory signing
key. See [`docs/live-testing.md`](docs/live-testing.md) for its scope.

When an exact compatible ATLAS checkout is available beside this repository,
the real producer-consumer-return path can also be exercised end to end:

```bash
python -m tools.cross_repo_e2e --atlas-repo ../atlas-os
```

Unlike the self-contained smoke command, this imports the verified ATLAS
checkout and uses its execution, classification, alignment, routing, handoff,
attestation, and return-verification functions around the real ARGUS façade.
It remains read-only and test-only.

### Activation boundary

ARGUS does not activate from keywords, the mere mention of a government organization, or a background listener. ATLAS first classifies and plans the task. It activates ARGUS only when the structured requirement is `government_public_sector_opportunity_intelligence`, ARGUS is registered and available, and the required Domain Context Handoff is `READY` or an explicitly unresolved `PARTIAL`. `BLOCKED` context is rejected.

The machine-readable contract is [`contracts/atlas/argus-activation-v1.json`](contracts/atlas/argus-activation-v1.json). ATLAS owns the live workflow, execution spine, plan, approvals, verification, and delivery. ARGUS supplies the specialist framework and methodology, may use scenario playbooks and operational SOPs, and returns domain analysis and proposed actions without creating a second execution system.

External skills, search systems, capture methods, trade-intelligence tools and proposal systems remain bounded providers. They do not become ARGUS canonical semantics merely because they are installed or connected. See [`docs/architecture/capability-integration.md`](docs/architecture/capability-integration.md).

## Access Asia working-file lifecycle

The ARGUS decision `PROMOTE_TO_PX` activates the tracked opportunity lineage; it does **not** move the working folder to a submission workspace.

Access Asia uses the following physical working-document lifecycle:

```text
ARGUS signal / intelligence
  → PROMOTE_TO_PX or explicit tracked registration
  → General/Business Intelligence/50_OPPORTUNITIES/[Year]_[PXnnnnn]_[ShortName]
  → discovery / research / qualification / capture / live-tender review / bid-no-bid / pre-submission
  → SUBMISSION_ACTIVE only
  → General/REV/OPP Opportunities/[same ID]
  → award or contract activation
  → General/OPS/PRJ Projects/[same ID]
```

A tender becoming live, I9 maturity, or an intention to bid does not by itself set `SUBMISSION_ACTIVE`. `SUBMISSION_ACTIVE` means formal response-package execution has actually started for the specific solicitation after the bid decision.

There is no separate BID folder, only one physical working folder at a time, and the permanent identifier is preserved across every stage move. Opportunities that close without formal submission remain in Business Intelligence and may be archived there.

## Repository authority

- Manifest: [`argus-intelligence.yaml`](argus-intelligence.yaml)
- Access Asia operating overlay: [`ACCESS_ASIA.md`](ACCESS_ASIA.md)
- Access Asia lifecycle policy: [`profiles/access-asia-opportunity-lifecycle.yaml`](profiles/access-asia-opportunity-lifecycle.yaml)
- Core: [`spec/core.md`](spec/core.md)
- ATLAS alignment: [`alignments/atlas-os.md`](alignments/atlas-os.md)
- Capability integration: [`docs/architecture/capability-integration.md`](docs/architecture/capability-integration.md)
- Pinned ATLAS handoff contract: [`contracts/atlas/domain-context-handoff-v1.schema.json`](contracts/atlas/domain-context-handoff-v1.schema.json)
- Synchronization compatibility descriptor: [`contracts/atlas/synchronization-compatibility.yaml`](contracts/atlas/synchronization-compatibility.yaml)
- Synchronization receipt schema: [`schemas/atlas-argus-sync-receipt.schema.json`](schemas/atlas-argus-sync-receipt.schema.json)
- Bangladesh profile: [`profiles/bangladesh.md`](profiles/bangladesh.md)
- Domain result schema: [`schemas/domain-result.schema.json`](schemas/domain-result.schema.json)
- GitHub-first persistence architecture: [`docs/architecture/github-first-canonical-store.md`](docs/architecture/github-first-canonical-store.md)
- Registry schema candidate: [`registry/schema/argus-master-registry-v0.2.1.json`](registry/schema/argus-master-registry-v0.2.1.json)
- End-to-end validation: [`docs/validation/atlas-argus-bd-e2e.md`](docs/validation/atlas-argus-bd-e2e.md)
- Bangladesh lifecycle validation: [`docs/validation/bangladesh-lifecycle-release-gates-rc2.md`](docs/validation/bangladesh-lifecycle-release-gates-rc2.md)

## Current status

`2.0.0-rc.5` — candidate.

The ATLAS/ARGUS architecture, capability-provider boundaries, 360° collection contract, Registry compatibility design, representative Bangladesh lifecycle gates, governed ATLAS domain-context handoff, and Access Asia physical working-file lifecycle overlay are under repository governance. Operational database deployment remains deferred for the current phase; GitHub is the interim canonical structured-intelligence persistence layer while SharePoint holds the active working business documents for the current lifecycle stage.
