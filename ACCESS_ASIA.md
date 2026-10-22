# Access Asia Operating Overlay

This repository defines ARGUS Government Commercial Opportunity Intelligence. Access Asia's commercial identity and working-document lifecycle are governed by the machine-readable profile [`profiles/access-asia-opportunity-lifecycle.yaml`](profiles/access-asia-opportunity-lifecycle.yaml), while ATLAS OS remains the execution and promotion authority.

## Two-stage identity

A raw signal may remain an `INTELLIGENCE` record without becoming a persistent commercial opportunity.

When a credible commercial possibility requires persistent tracking, ARGUS may create a first-class `OPPORTUNITY` before any Access Asia PX exists. Its permanent intelligence identity is:

`ARGUS-OPP-YYYY-NNNNNN`

This identity persists through all later lifecycle changes.

When ATLAS authorizes `PROMOTE_TO_PX` or explicit commercial-pipeline registration, assign the Access Asia commercial identity:

`[Year]_[PXnnnnn]_[ShortName]`

The PX identifier does not replace the ARGUS opportunity identifier; both remain linked to the same underlying opportunity.

## Pre-PX working state

Pre-PX opportunity intelligence may be tracked structurally in the ARGUS Master Registry without requiring a SharePoint folder. When working documents are needed before promotion, the governed pre-PX home is:

`General/Business Intelligence/50_OPPORTUNITIES`

Typical work includes discovery, research, problem/need definition, government-project tracking, qualification, OEM/supplier research, solution shaping, partnerability analysis, procurement monitoring and Rapid Tender review.

Tender publication alone does not create a PX identity and does not imply `SUBMISSION_ACTIVE`.

## PX promotion

When ATLAS authorizes commercial pipeline promotion, the opportunity receives its `[Year]_[PXnnnnn]_[ShortName]` identity. If a physical pre-PX working folder exists, move the entire lineage to:

`General/REV/OPP Opportunities/[PX ID]`

Do not create a separate BID folder and do not duplicate the opportunity folder.

All promoted pre-award commercial pursuit work remains within that same REV/OPP lineage, including supplier/OEM engagement, customer engagement, capture, tender analysis, bid/no-bid, compliance planning and submission execution.

## Project transition

On award or contract activation, move the same commercial lineage to:

`General/OPS/PRJ Projects/[same PX ID]`

Preserve both:

- the ARGUS opportunity ID for intelligence lineage; and
- the PX ID for Access Asia commercial/project lineage.

## Non-submission outcomes

Pre-PX opportunities that remain `MONITOR`, `HOLD`, `REJECT`, `CANCELLED` or `CLOSED_BEFORE_SUBMISSION` stay in Business Intelligence and may be archived there. An ARGUS opportunity does not require procurement to occur in order to remain historically useful intelligence.

## Canonical ownership

- **ARGUS Master Registry:** structured government-commercial opportunity, supplier, event and evidence intelligence.
- **SharePoint:** working business documents for the current governed lifecycle stage.
- **ATLAS OS:** Mission Control, permissions, authoritative priority, `PROMOTE_TO_PX`, pursuit/bid decisions, external-action authorization, persistence governance and verification.

The rule is: ARGUS identifies, develops, matches and recommends; ATLAS authorizes commercial state changes and actions.
