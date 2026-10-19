# Access Asia Operating Overlay

This repository defines ARGUS Intelligence. Access Asia's physical working-document lifecycle is governed by the machine-readable profile [`profiles/access-asia-opportunity-lifecycle.yaml`](profiles/access-asia-opportunity-lifecycle.yaml).

## Mandatory lifecycle rule

A raw intelligence signal may exist only in the ARGUS Master Registry. When it becomes a tracked Access Asia opportunity (`PROMOTE_TO_PX` or explicit registration), assign the permanent identifier:

`[Year]_[PXnnnnn]_[ShortName]`

Create the working folder at:

`General/Business Intelligence/50_OPPORTUNITIES/[ID]`

Keep all discovery, research, qualification, customer/OEM engagement, capture, procurement monitoring, live-tender review, bid/no-bid analysis and pre-submission working material there.

**Tender publication alone does not move the folder.** `PROMOTE_TO_PX` also does not move it to the submission workspace.

The folder moves only when `SUBMISSION_ACTIVE` is true: formal response-package execution has actually started for a specific solicitation after the bid decision.

At that point move the entire existing folder, with the same identifier, to:

`General/REV/OPP Opportunities/[same ID]`

Do not create a separate BID folder and do not duplicate the opportunity folder.

On award or contract activation, move the same folder/lineage to:

`General/OPS/PRJ Projects/[same ID]`

Opportunities that never enter formal submission execution remain in Business Intelligence and may be archived there when inactive.

## Canonical ownership

- ARGUS GitHub: structured opportunity intelligence and domain semantics.
- SharePoint: working business documents for the current lifecycle stage.
- ATLAS OS: execution governance, approvals, verification and mutation control.

The SharePoint AI bootstrap and lifecycle SOP are maintained in `General/Business Intelligence`.
