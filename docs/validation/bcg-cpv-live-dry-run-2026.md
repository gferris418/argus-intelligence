# Live End-to-End Dry Run — Bangladesh Coast Guard Coastal Patrol Vessel

**Scenario:** Coastal Patrol Vessel for Bangladesh Coast Guard  
**As of:** 2026-10-18  
**Status:** Architecture validation candidate  
**Purpose:** Show exactly how information moves from ATLAS OS into ARGUS, through Bangladesh normalization/reconciliation, and back to ATLAS without duplicate opportunity creation or semantic drift.

## Official evidence used

### Bangladesh Public Procurement Authority

Official solicitation:
`https://bppa.gov.bd/advertisement-works/details-98162.html`

Observed material facts:
- Ministry of Home Affairs;
- Bangladesh Coast Guard Force;
- Procuring Entity: Project Director;
- PE Code: `224392800`;
- Invitation Reference: `44.08.2680.033.02.106.26.160`;
- Procurement Method: `ICT One Stage & Two envelope Tendering Method`;
- Budget and Source: `Development Budget GOB`;
- Tender title: `Construction and Delivery of 4 (Four) in No. Coastal Patrol Vessel (CPV)`;
- Lot No: `1`;
- Lot Identification: `WD-2`;
- latest corrigendum status: Active;
- latest closing: `2026-10-25 12:00 Asia/Dhaka`;
- latest opening: `2026-10-25 12:30 Asia/Dhaka`;
- minimum stated experience: 10 years of shipbuilding and delivery of combat vessels/patrol craft, with other qualifications in the tender documents.

### Bangladesh Planning Commission — ADP

Official ADP page:
`https://adp.plancomm.gov.bd/exp/press-book.php?action=allocation&fiscal_year=2025&view=html`

Observed material facts:
- Implementing Agency: Coast Guard;
- Project Code: `224392800`;
- Project: `Acquisition of Replacement Vessel to Increase the Capacity of Bangladesh Coast Guard (1st Revised)`;
- implementation period: `2023-11-01` to `2027-06-30`;
- status: Approved;
- financing: GoB.

### UN Statistics Division classifications

- ISIC Rev.4 `3011` — Building of ships and floating structures.
- CPC Ver.2.1 `49319` — Other vessels, including the applicable broader vessel class.
- CPC Ver.2.1 `88821` — Ship building services.
- HS candidates under heading 8906 include `890610` (warships) and `890690` (other vessels). ARGUS does not choose between them; that remains unresolved in ATLAS until authoritative product/customs evidence establishes the correct subheading.

## Process trace

### 1. User seed

Input:
`Coastal Patrol Vessel for Bangladesh Coast Guard`

Output forwarded to ATLAS:
A business-intelligence seed only. It is not treated as proof of a project, funding, procurement, or new opportunity.

### 2. ATLAS task classification

ATLAS identifies the work as research + analysis + decision support in Bangladesh government/public-sector procurement context.

Output:
Governed execution context.

### 3. ATLAS domain classification

ATLAS resolves the generic domain before ARGUS discovery:
- jurisdiction: Bangladesh;
- operator context: Bangladesh Coast Guard / maritime security;
- supplier industry: ISIC 3011;
- product class: CPC 49319;
- shipbuilding service class: CPC 88821;
- capability context: maritime patrol/law enforcement/surveillance/interdiction/SAR;
- HS subheading unresolved between candidate codes pending authoritative evidence.

Output:
A governed domain-classification snapshot.

### 4. ATLAS domain/framework alignment

ATLAS records applicable procurement/domain framework context and unresolved technical standards/classification-society requirements.

Output:
Domain alignment plus unresolved material.

### 5. ATLAS domain-context handoff

ATLAS sends an immutable handoff to ARGUS with:
- handoff ID;
- task ID;
- classification snapshot;
- taxonomy references;
- alignment state;
- unresolved items;
- risk flags;
- payload SHA-256.

This case may proceed as `PARTIAL` because unresolved HS/technical standards do not block opportunity intelligence.

### 6. ARGUS Contextualize

ARGUS does not redefine the ATLAS taxonomy. It converts the governed context into opportunity-search semantics:
- Coastal Patrol Vessel;
- CPV;
- patrol vessel;
- patrol craft;
- related/adjacent vessel classes;
- Bangladesh Coast Guard;
- known identifiers such as `WD-2` and the invitation reference.

Output:
ARGUS search/context expansion.

### 7. ARGUS Registry lookup

ARGUS searches GitHub canonical Registry first.

Existing lineage found:
- `ENT-BD-COAST-GUARD`;
- `PRJ-BCG-CPV-WD2`;
- `PROC-BCG-LT001`.

Output:
Candidate existing lineage. No new opportunity is created.

### 8. Bangladesh source normalization

Official observations are mapped into the canonical Bangladesh field vocabulary.

Examples:
- `Ministry/Division` -> `institution.ministry_name`;
- `Agency` -> `institution.organization_name`;
- `Procuring Entity Code` -> `institution.pe_code`;
- Planning Commission `Project Code` -> `project.code`;
- `Budget and Source of Funds` -> separate `funding.budget_type` and `funding.source`;
- `Procurement Method` -> `procurement.method`;
- `Invitation Reference No` -> `solicitation.reference_no`;
- `Lot No` -> `procurement.lot_no`;
- `Identification` -> `procurement.lot_identification`;
- latest corrigendum closing/opening dates -> current solicitation dates.

Important typed-identifier result:
`institution.pe_code` and `project.code` both equal `224392800` in the two official sources. ARGUS preserves both typed fields and does not merge them merely because the string values are equal.

Important semantic correction:
The BPPA page leaves `Tender Package No` blank while publishing Lot `1`, Identification `WD-2`. Therefore `WD-2` is not coerced into `procurement.package_no`. The Bangladesh Data Standard now models lot number and lot identification explicitly.

### 9. Resolve and reconcile

ARGUS compares current official evidence to the existing Registry lineage.

Result:
`MATCHED_EXISTING`

Why:
- same Coast Guard institutional context;
- same four-CPV requirement;
- same `WD-2` identifier already present in legacy lineage;
- current official BPPA event resolves the previous stale procurement state;
- Planning Commission confirms an approved GoB replacement-vessel project in the same institutional context.

Output:
Refresh existing lineage; do not create another opportunity.

### 10. 360-degree coverage assessment

Current coverage:
- need/mission: ADEQUATE;
- institution/stakeholders: ADEQUATE;
- programme/project: ADEQUATE;
- budget/funding: ADEQUATE;
- procurement/acquisition: ADEQUATE;
- timing/triggers: ADEQUATE;
- policy/strategy: PARTIAL;
- technical/installed base: INSUFFICIENT;
- supplier/competitor: INSUFFICIENT;
- ecosystem/influence: PARTIAL;
- commercial participation: INSUFFICIENT;
- internal intelligence: PARTIAL.

Output:
Coverage matrix + material gaps.

### 11. ARGUS assessment

Current state as of 2026-10-18:
- maturity: `I9`;
- maturity condition: CURRENT;
- procurement state: OPEN;
- closing: 2026-10-25 12:00 Asia/Dhaka;
- project state: APPROVED;
- funding: GoB development budget evidenced;
- Bangladesh route: `BD-DEV-GOB`;
- decision: `INVESTIGATE`.

This explicitly solves the earlier temporal-maturity problem: the maturity is tied to an `as_of` date and current evidence rather than inheriting a stale historical I9 state.

### 12. Research Frontier

The highest-value question is not whether a tender exists; that is now verified.

Priority question:
`Does Access Asia have a commercially viable participation path before the 2026-10-25 closing date, considering full tender eligibility/specification requirements, suitable shipyard/OEM partners, representation/team structure, bid security and commercial economics?`

This is decision-driven because the answer changes the next action.

### 13. ARGUS domain result

ARGUS returns:
- current `I9` state;
- `INVESTIGATE` decision;
- existing lineage identity;
- no new opportunity;
- current normalized facts and provenance;
- Research Frontier;
- proposed actions to refresh the existing procurement record and continue decision-driven research.

### 14. ATLAS return receipt

ARGUS returns the exact upstream handoff/correlation identifiers. ATLAS verifies that the domain result corresponds to the same handoff and task.

Mismatch, stale handoff, missing receipt, or changed upstream context must fail closed.

### 15. ATLAS verification / authorization

ATLAS verifies:
- current official sources;
- evidence/claim separation;
- no duplicate opportunity;
- no silent taxonomy override;
- no unauthorized permanent PX creation.

### 16. GitHub persistence boundary

The dry run itself performs no canonical Registry mutation.

A later governed production write may persist:
- normalized current procurement state;
- source locators;
- current dates/status;
- synthesized assessment;
- Research Frontier;
- evidence references.

It must not upload the raw tender document or attachments to GitHub.

### 17. User delivery

ATLAS presents decision-ready intelligence, not a raw source dump.

## Architecture findings

### PASS
- ATLAS classification before ARGUS discovery;
- immutable ATLAS -> ARGUS handoff;
- ARGUS contextualization without taxonomy duplication;
- internal-first Registry lookup;
- cross-source normalization;
- typed identifiers preserved;
- one-lineage reconciliation;
- current time-qualified maturity;
- 360-degree coverage;
- decision-driven Research Frontier;
- structured-only GitHub persistence.

### Data-standard improvement discovered

The live BPPA page distinguishes:
- Tender Package No.;
- Lot No.;
- Lot Identification.

The prior Bangladesh standard did not model lot number/lot identification separately. The dry run therefore adds:
- `procurement.lot_no`;
- `procurement.lot_identification`.

### Additional datapoints observed but not yet canonicalized

The official BPPA notice also exposes:
- tender document price;
- tender security amount;
- completion period;
- pre-tender meeting details.

These are preserved in the scenario as unmapped material datapoints and should be considered in the next Bangladesh Data Standard expansion rather than being forced into incorrect existing fields.

## Dry-run decision

**Architecture result: PASS WITH DATA-DICTIONARY REFINEMENT.**

No ATLAS architecture change is required. ARGUS Bangladesh normalization improves through the additive lot fields. The next recommended step after merge is to extend the Bangladesh canonical dictionary for common tender-commercial fields, then rerun the same scenario as a production canonical-write simulation.
