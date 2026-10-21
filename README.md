# ARGUS Intelligence

ARGUS is Access Asia's governed specialist for **strategic and decision intelligence**. It supports strategic, market, opportunity, competitive, stakeholder, political-economic, monitoring, forecasting, scenario, and decision-intelligence work when ATLAS classifies a request as `INTELLIGENCE`.

Ordinary factual/current-information searches and ordinary tasks stay in ATLAS. ARGUS is not activated merely because a government body, tender, company, market, or political subject is mentioned. The purpose of this boundary is to keep normal execution fast while preserving deeper intelligence methods for requests that actually need them.

Government and public-sector opportunity intelligence remains a first-class ARGUS specialization. For Access Asia, that specialization identifies credible business before formal tender publication, connects fragmented policy/project/funding/procurement evidence, prevents duplicate opportunity creation, prioritizes decision-changing research, and promotes commercially actionable signals into a permanent PX opportunity lineage. **PX activation does not mean submission activation:** under the Access Asia operating overlay, all tracked opportunity working files remain in Business Intelligence until formal response-package execution actually begins.

See [`ACCESS_ASIA.md`](ACCESS_ASIA.md) and [`profiles/access-asia-opportunity-lifecycle.yaml`](profiles/access-asia-opportunity-lifecycle.yaml) for the current Access Asia working-file lifecycle.

## Production relationship with ATLAS OS

Within the Access Asia governed environment, **ATLAS OS is the execution-governance backbone**. ARGUS is a nested specialist intelligence method and does not create a second execution spine.

The first semantic decision is lightweight ATLAS request triage:

```text
User request
  → ATLAS REQUEST_TRIAGE
      → GENERAL_SEARCH → ATLAS direct execution
      → GENERAL_TASK   → ATLAS direct execution
      → INTELLIGENCE   → governed ARGUS delegation
```

ATLAS owns user/mission authority, permissions, planning, approvals, provider routing, execution state, verification, persistence authorization, dashboard projection, and final delivery. For `INTELLIGENCE`, ATLAS may transfer a `READY` or governed `PARTIAL` Domain Context Handoff. ARGUS preserves the upstream context, enriches intelligence-specific domain context, performs the specialist analysis, and returns a correlated result. A `BLOCKED` handoff cannot authorize dependent ARGUS execution.

Canonical intelligence flow:

`User objective → ATLAS triage = INTELLIGENCE → ATLAS plan/routing/approval → READY or PARTIAL Domain Context Handoff → ARGUS Contextualize → ARGUS intelligence method → correlated ARGUS result + proposed actions → ATLAS verification/approval → authorized action(s) → ATLAS delivery`

This removes the previous requirement to complete deep taxonomy/classification/framework work before ARGUS activation. Deep intelligence context is resolved only when the intelligence task needs it. ARGUS may add terminology, aliases, solution adjacency, local context, installed-base interpretation, supplier/competitor relationships, political-economic context, signals, scenarios, forecasts, benchmarks, and commercial meaning, but it must not silently replace ATLAS-owned authority, permissions, or source facts.

The preferred executable interface is `Argus.analyze(AnalysisEnvelope)` in [`tools/argus_runtime.py`](tools/argus_runtime.py). It owns handoff validation, synchronization transitions, domain-method invocation, protected result metadata, digest correlation, and the final return receipt. A domain-method failure carries a retryable `FAILED` receipt instead of losing execution state. Existing synchronization functions remain available for compatibility and recovery workflows.

```python
from tools.argus_runtime import AnalysisEnvelope, Argus

runtime = Argus(domain_method, trusted_key_registry=operator_pinned_registry)
outcome = runtime.analyze(AnalysisEnvelope(
    handoff=atlas_handoff,
    atlas_attestation=atlas_attestation,
    execution_lease=execution_lease,
    execution_lease_attestation=execution_lease_attestation,
    started_at="2026-10-19T01:00:00+06:00",
))
```

The existing synchronization runtime retains its validated ATLAS `2.0.1` compatibility baseline at commit `b8b8559c57eef5fbb97d914d924077ba20b1883d`. That historical pin remains evidence for the synchronization protocol; the `2.1.0-rc.1` candidate adds the new ATLAS request-triage/general-intelligence activation contract. Neither runtime mutates the Master Registry by itself.

The complete seam can be tested without persistent keys, network access, or registry writes. Compact text is the default; NDJSON is available for a machine consumer:

```bash
python -m tools.live_smoke
python -m tools.live_smoke --format ndjson
```

The command is explicitly test-only and generates a fresh in-memory signing key. See [`docs/live-testing.md`](docs/live-testing.md) for its scope.

When an exact compatible ATLAS checkout is available beside this repository, the real producer-consumer-return path can also be exercised end to end:

```bash
python -m tools.cross_repo_e2e --atlas-repo ../atlas-os
```

Unlike the self-contained smoke command, this imports the verified ATLAS checkout and exercises the real handoff, ARGUS analysis, return receipt, and ATLAS verification path. It remains read-only and test-only.

### Activation boundary

ARGUS activation is defined by [`contracts/atlas/argus-activation-v1.json`](contracts/atlas/argus-activation-v1.json):

- ATLAS route must be `INTELLIGENCE` (or an explicit admissible ARGUS request must resolve to that route);
- canonical specialist capability is `intelligence_analysis`;
- keyword activation is disabled;
- background activation is disabled;
- a government/public-sector mention alone is not sufficient;
- a simple tender/current-information lookup is not sufficient;
- strategic assessment, opportunity qualification, competitive/stakeholder intelligence, political-economic assessment, monitoring, forecasting, scenarios, probability estimation, or decision intelligence may activate ARGUS;
- `READY` and `PARTIAL` handoffs may proceed under the contract; `BLOCKED` cannot.

ATLAS owns the live workflow, execution spine, plan, approvals, verification, and delivery. ARGUS supplies specialist intelligence methodology and returns analysis and proposed actions without creating a competing execution system.

External skills, search systems, capture methods, trade-intelligence tools and proposal systems remain bounded providers. They do not become ARGUS canonical semantics merely because they are installed or connected. See [`docs/architecture/capability-integration.md`](docs/architecture/capability-integration.md).

## Machine-readable authority

Current AI/agent authority is machine-readable by default:

- Manifest: [`argus-intelligence.yaml`](argus-intelligence.yaml)
- General-intelligence core: [`spec/general-intelligence.yaml`](spec/general-intelligence.yaml)
- ATLAS fast-triage alignment: [`alignments/atlas-os-triage-v2.yaml`](alignments/atlas-os-triage-v2.yaml)
- Activation contract: [`contracts/atlas/argus-activation-v1.json`](contracts/atlas/argus-activation-v1.json)
- Domain-context handoff: [`contracts/atlas/domain-context-handoff-v1.schema.json`](contracts/atlas/domain-context-handoff-v1.schema.json)
- Domain-result schema: [`schemas/domain-result.schema.json`](schemas/domain-result.schema.json)

The detailed public-sector opportunity doctrine remains in [`spec/core.md`](spec/core.md) as the active specialization rather than the universal ARGUS product boundary. The earlier ATLAS alignment narrative remains in [`alignments/atlas-os.md`](alignments/atlas-os.md) as a historical/compatibility companion.

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

## Repository authority and specializations

- Access Asia operating overlay: [`ACCESS_ASIA.md`](ACCESS_ASIA.md)
- Access Asia lifecycle policy: [`profiles/access-asia-opportunity-lifecycle.yaml`](profiles/access-asia-opportunity-lifecycle.yaml)
- Public-sector opportunity specialization: [`spec/core.md`](spec/core.md)
- Bangladesh profile: [`profiles/bangladesh.md`](profiles/bangladesh.md)
- GitHub-first persistence architecture: [`docs/architecture/github-first-canonical-store.md`](docs/architecture/github-first-canonical-store.md)
- Capability integration: [`docs/architecture/capability-integration.md`](docs/architecture/capability-integration.md)
- Historical synchronization descriptor: [`contracts/atlas/synchronization-compatibility.yaml`](contracts/atlas/synchronization-compatibility.yaml)
- Synchronization receipt schema: [`schemas/atlas-argus-sync-receipt.schema.json`](schemas/atlas-argus-sync-receipt.schema.json)

## Current status

`2.1.0-rc.1` — candidate.

The last released stable ARGUS version remains `2.0.1`. The current candidate broadens the product from government/public-sector opportunity intelligence into the general ATLAS intelligence specialist while preserving the mature public-sector/Bangladesh opportunity model as a specialization. Operational database deployment remains deferred for the current phase; GitHub remains the interim canonical structured-intelligence persistence layer while SharePoint holds active working business documents for the Access Asia lifecycle.
