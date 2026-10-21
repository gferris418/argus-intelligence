# ATLAS–ARGUS collection boundary

## Fixed architecture

ATLAS OS is the operating architecture. Mission Control is the human command boundary; the Control Plane owns authoritative machine governance; the Data Plane performs substantive work; Domain Context Services owns canonical semantics and classification; Assurance/Verification checks results; Observability produces operational state; the Dashboard is a read-only projection.

ARGUS is nested inside ATLAS as the governed intelligence collection subsystem. It is not a peer operating system and does not own planning, approvals, analysis, final decisions, persistence authorization or delivery.

```text
Human
  -> Mission Control
  -> ATLAS Control Plane
  -> Input / Intent / Target Interpretation
  -> Collection-Need Gate
       -> NONE
       -> ATLAS_DIRECT
       -> ARGUS_COLLECTION -> ARGUS collection package
       -> HYBRID           -> ARGUS collection package + ATLAS substantive work
  -> ATLAS Domain Context Services
  -> ATLAS Data Plane analysis / decision
  -> Assurance / Verification
  -> Output / Persistence
  -> Observability
  -> Dashboard
```

## Core rule

The activation question is not `Is this intelligence?` It is `Does this ATLAS task require structured intelligence collection?`

Examples:

| Request | Collection mode |
| --- | --- |
| Bangladesh Bank foreign exchange policy | ATLAS_DIRECT |
| ST Engineering | ARGUS_COLLECTION |
| Coastal patrol vessel for Bangladesh Coast Guard | ARGUS_COLLECTION |
| Seed cum cleaner for BADC | ARGUS_COLLECTION |
| Annual procurement plan of Bangladesh Navy | ARGUS_COLLECTION |
| Compare ST Engineering vs L3Harris for Bangladesh opportunities | HYBRID |

## Responsibility split

ARGUS: find, collect, acquire, extract, normalize, resolve, deduplicate, corroborate, expose gaps/conflicts and package evidence.

ATLAS: understand, govern, classify canonically, plan, analyze, forecast, compare, qualify opportunities, decide, verify, persist and deliver.

`PROMOTE_TO_PX`, bid/no-bid and other Access Asia pursuit decisions are ATLAS/business-policy decisions. ARGUS may return the evidence needed for them through the public-sector opportunity specialization.
