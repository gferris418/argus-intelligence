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

## Pre-PX and tracked working state

Pre-PX opportunity intelligence may be tracked structurally in the ARGUS Master Registry without requiring a SharePoint folder. When working documents are needed, the governed working home is:

`General/Business Intelligence/50_OPPORTUNITIES`

`PROMOTE_TO_PX` assigns the commercial identity but **does not move the opportunity out of Business Intelligence**. The same working folder remains under `50_OPPORTUNITIES` through discovery, research, qualification, customer/OEM engagement, capture, live-tender review, bid/no-bid preparation and all pre-submission work.

Tender publication alone does not create a PX identity and does not imply `SUBMISSION_ACTIVE`.

## Submission activation

Only when ATLAS determines that `SUBMISSION_ACTIVE` is true — formal response-package execution has actually started for a specific solicitation after the bid decision — move the existing folder, without copying it, to:

`General/REV/OPP Opportunities/[PX ID]`

Do not create a separate BID folder and do not duplicate the opportunity folder.

The same REV/OPP lineage then holds submission execution, clarifications, negotiations and pre-award activity.

## Project transition

On award or contract activation, move the same commercial lineage to:

`General/OPS/PRJ Projects/[same PX ID]`

Preserve both:

- the ARGUS opportunity ID for intelligence lineage; and
- the PX ID for Access Asia commercial/project lineage.

## Non-submission outcomes

Opportunities that remain `MONITOR`, `HOLD`, `REJECT`, `CANCELLED` or `CLOSED_BEFORE_SUBMISSION` stay in Business Intelligence and may be archived there. An ARGUS opportunity does not require procurement to occur in order to remain historically useful intelligence.

## Canonical ownership

- **HubSpot:** canonical CRM identity, company/contact master data, Access Asia relationship state, communications/interactions and deal records for suppliers, customers and other commercial parties.
- **ARGUS Master Registry:** structured government-commercial intelligence, opportunity intelligence, supplier capability/partnerability assessment, events, evidence, matches and public-sector institutional intelligence. ARGUS links to CRM parties rather than duplicating their CRM master data.
- **SharePoint:** original/working documents and the governed opportunity/project file lineage for the current business lifecycle stage.
- **ATLAS OS:** Mission Control, permissions, authoritative priority, `PROMOTE_TO_PX`, pursuit/bid decisions, external-action authorization, persistence routing, governance and verification.

Cross-system integration follows **pointers, not copies**. A record should carry stable foreign references or integration keys to the canonical owner rather than replicate the owner's full record.

The rule is: ARGUS identifies, develops, matches and recommends; ATLAS authorizes commercial state changes and actions; HubSpot owns CRM party/relationship state; SharePoint owns documents and working files.
