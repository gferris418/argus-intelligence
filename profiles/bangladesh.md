# ARGUS Bangladesh Country Profile

**Version:** 2.0.0-rc.2  
**Status:** Candidate  
**Country:** Bangladesh (`BD`)  
**Production runtime:** ATLAS OS required for Access Asia

## 1. Purpose

This profile specializes ARGUS for Bangladesh government and public-sector opportunity intelligence.

It does not redefine ARGUS Core and does not modify ATLAS OS.

In Access Asia production use:

`User objective → ATLAS OS → ARGUS Bangladesh method → ARGUS domain result + proposed actions → ATLAS verification/approval → authorized domain action(s) → ATLAS persistence/delivery`

The objective is to identify credible Bangladesh public-sector demand early enough to understand the institutional owner, project/budget/funding path, procurement route, timing, solution fit, competitive context and next commercially useful action before or during formal procurement.

## 2. Governing principle

**A Bangladesh opportunity is not synonymous with a tender.**

The same underlying requirement may appear progressively through policy, budget, project, financing, APP/procurement plan, standardization, EOI/PQ, tender, amendment, award, implementation, installed base, upgrade, replacement or recurring-support evidence.

A published tender is one evidence event in a longer chain, not the default beginning of the opportunity.

## 3. Current-context rule

This profile may cache a dated Bangladesh legal/institutional baseline for operational use, but it is not the runtime authority for current law.

When procurement law, rules, financing conditions or other binding requirements can materially change the result, ATLAS must revalidate the current applicable requirement before relying on cached profile text.

## 4. First mandatory Bangladesh step: route classification

Before detailed research, classify the likely route. If evidence is insufficient, use `BD-UNKNOWN` and research the route before making downstream assumptions.

| Code | Route | Typical use |
|---|---|---|
| `BD-GEN-EGP` | General public procurement / e-GP | General goods, works, consulting and services |
| `BD-DEV-GOB` | GoB development-project procurement | ADP/RADP projects financed materially by GoB |
| `BD-DEV-DP` | Development-partner financed procurement | Loan/grant/project-aid projects with partner-specific procurement influence |
| `BD-DEF-DGDP` | Defence / DGDP / e-DP | Defence acquisitions, evaluation/standardization and DGDP procurement |
| `BD-SOE-AUT` | SOE/autonomous authority | Utilities, ports, authorities, corporations, boards and SOEs |
| `BD-PPP` | PPP/concession | PPP Authority / contracting-authority projects and transactions |
| `BD-G2G-STRAT` | G2G/direct/strategic | Bilateral, G2G or specially structured acquisition |
| `BD-LOCAL` | Local-government/public-body | City corporations, municipalities and decentralized public bodies |
| `BD-UNKNOWN` | Unresolved | Route not yet evidenced |

The route is a research hypothesis until supported by authoritative evidence. One project may contain packages following different routes.

## 5. Institutional-role model

Do not collapse all actors into `buyer`.

Resolve, where material:

- sponsoring ministry/division;
- parent ministry/division;
- implementing agency;
- end user/operator;
- project owner;
- project director / PIU;
- procuring entity (PE);
- approving authority;
- funding authority/source;
- development partner/lender/donor;
- regulator;
- consultant/transaction adviser/EPC/integrator;
- DGDP/defence procurement wing where applicable;
- service HQ/directorate/end-user command where applicable;
- PPP contracting authority where applicable;
- incumbent supplier/OEM;
- local partner/agent/representative where commercially relevant.

One entity may hold multiple roles, but roles must be evidenced rather than inferred from hierarchy alone.

## 6. Institutional graph

Use relationship concepts without forcing every opportunity to contain every node:

`Government priority → Ministry/Division → Agency/Authority/SOE → Programme/Project/Budget → End User → Project/PIU/PE → Funding → Procurement Plan/Strategy → Package → Pre-Procurement → Tender/Award → Installed Base`

Defence investigative pattern:

`Service need → Service HQ/directorate/end user → requirement/evaluation/standardization → DGDP/e-DP procurement path → tender/contract → installed base`

The pattern is investigative, not a presumption that every procurement follows an identical visible chain.

## 7. Bangladesh discovery vectors

### Policy-to-procurement
`National/sector priority → ministry/division → agency/end user → programme/project → budget/funding → procurement planning → package`

### Product-to-buyer reverse
`Product/service → Bangladesh use case → government mission → plausible users → actual institutions → current systems → capability gap → project/budget/procurement evidence`

### ADP/project-led
`ADP/RADP/approved project/project-processing signal → implementing agency → project office → funding → procurement plan/package → tender`

### Funding-led
`GoB allocation / ERD / loan / grant / bilateral / G2G / project aid → project → implementing entity → procurement package`

### Procurement-backward
`APP/package/tender/award → PE → project/budget → implementing agency → ministry/division → programme/policy/funding`

### Historical / installed-base
`Prior award → incumbent/OEM → delivery/installation age → support history → obsolescence/expansion → replacement/upgrade need`

### Defence pre-procurement
`Evaluation / re-evaluation / standardization / EOI / pre-bid / recurring equipment family / capability gap → likely acquisition path`

### PPP
`PPP project/approval → contracting authority → transaction adviser → EOI/IFB → private partner/O&M/equipment opportunities`

### Ecosystem
`Consultant / EPC / OEM / integrator / donor / lender / local partner → project → agency/end user → procurement route`

### Trigger event
Project approval/revision, budget allocation, ADP inclusion, financing agreement, consultant appointment, procurement-strategy activity, evaluation/standardization, installed-base age, capacity expansion, policy change or modernization trigger.

## 8. Source architecture

Source authority is claim-specific.

### Tier A — official transaction/legal primary

- BPPA legal/procedure materials;
- e-GP APP/package/tender/award records where accessible;
- official gazettes;
- DGDP/e-DP notices, tenders, amendments, pre-bid, evaluation/re-evaluation/standardization and supplier-enlistment materials;
- PPP Authority project/tender records;
- official budget/appropriation/project-approval records;
- official ministry/agency procurement/project publications.

### Tier B — project/funding/implementation primary

- Planning Commission ADP/RADP and approved-project data;
- project-processing/PEC signals;
- IMED project/implementation/monitoring outputs;
- ERD financing/project-aid records;
- official development-partner project/procurement portals;
- official SOE/authority reports and project/procurement publications.

### Tier C — Access Asia internal authoritative sources

- authorized communications;
- SharePoint/project/tender documents;
- prior quotations/proposals;
- OEM/consultant communications;
- meeting records;
- historical tender/award/project files;
- reconciled DTIF legacy history.

Internal evidence can be highly authoritative for Access Asia relationship/history claims but does not by itself establish a government approval or procurement event.

### Tier D — corroborating/open-source intelligence

OEM releases, consultant/EPC publications, credible industry sources, reputable media and event signals.

These may generate hypotheses but must not substitute for official evidence where official confirmation is materially required.

## 9. Bangladesh 360° Collection Map

Bangladesh specializes the twelve ARGUS Core collection lenses. The lens names and semantics remain Core-owned.

### `need_mission`

Determine the Bangladesh public-sector mission, service need, capability gap, statutory duty, modernization requirement, capacity constraint or recurring operational demand that could create procurement.

Typical evidence: official plans/statements, project rationale, recurring procurement, installed-base weakness, service/end-user requirements, capacity-expansion evidence and authorized internal history.

### `policy_strategy`

Identify the policy, sector strategy, ministry priority, reform, modernization programme, regulatory change or institutional mandate that supports or constrains the requirement.

Do not treat policy aspiration as procurement evidence by itself.

### `institution_stakeholders`

Resolve ministry/division, implementing agency, end user, operator, PE, project office/PIU, approving authority, DGDP wing/section where relevant, development partner, consultant/adviser and other actors capable of shaping the outcome.

### `programme_project`

Search for the programme, development project, acquisition context, PPP transaction, SOE programme, operational budget initiative or other implementation vehicle capable of delivering the requirement.

Preserve project revisions, official IDs and fiscal-year continuity.

### `budget_funding`

Assess GoB allocation, ADP/RADP context, project aid, ERD/financing evidence, loan/grant status, bilateral/G2G financing, SOE budget, PPP financing structure or other relevant source.

Budget indication, financing approval and actual procurement allocation remain separate claims.

### `procurement_acquisition`

Resolve the actual or likely Bangladesh route: e-GP/APP/package, project procurement plan, donor framework, DGDP/e-DP, PPP, SOE/autonomous channel, G2G/strategic route or local-government route.

Track pre-procurement, tender, amendment, award, cancellation and re-tender as related events rather than automatically separate opportunities.

### `technical_installed_base`

Identify current equipment/system/service, OEM/incumbent, age, delivery/installation history, support state, recurring spares/training, obsolescence, capacity shortfall, interoperability constraints and upgrade/replacement window where lawfully available.

For defence, do not infer classified capability, readiness, vulnerability, deployment or operational location.

### `supplier_competitor`

Map incumbents, historical suppliers, relevant OEMs, competing technologies, prior bidders/awardees and commercially plausible competitors.

Separate verified award/incumbent history from market speculation.

### `ecosystem_influence`

Map consultants, EPCs, system integrators, donors/lenders, transaction advisers, local partners/agents, technical advisers and other actors who may shape requirements, specifications, funding or route selection.

### `commercial_participation`

Assess early participation flags such as national/international method, possible JV/local-partner issue, supplier/DGDP enlistment, foreign OEM eligibility, development-partner rules, export/end-use sensitivity, local installation/training/service obligations, import/LC/payment route and after-sales lifecycle.

These are flags for downstream verification, not legal conclusions.

### `timing_triggers`

Track events that may accelerate, delay, cancel, revive or expand demand: project approval/revision, ADP/RADP inclusion, allocation change, financing agreement, consultant appointment, evaluation/standardization, APP/package creation, tender calendar, incumbent obsolescence, policy change and capacity expansion.

### `internal_intelligence`

Before duplicating external research, search the ARGUS Registry, existing PX records, authorized communications, SharePoint evidence, prior quotations/proposals, meeting records, supplier/product history, installed-base knowledge and prior research.

Internal evidence supports Access Asia relationship/history claims but does not automatically prove a government procurement event.

## 10. Bangladesh collection coverage

Use Core coverage states:

- `NOT_APPLICABLE`
- `UNASSESSED`
- `INSUFFICIENT`
- `PARTIAL`
- `ADEQUATE`

The profile does not require every lens to become `ADEQUATE`.

Examples:

- an I0 signal may justify rapid checks of `need_mission`, `institution_stakeholders`, `procurement_acquisition` and `internal_intelligence` first;
- a defence pre-procurement candidate may require stronger `technical_installed_base`, `institution_stakeholders`, `procurement_acquisition`, `supplier_competitor` and `commercial_participation` coverage before promotion;
- a development project may require stronger `programme_project`, `budget_funding` and `procurement_acquisition` coverage;
- a live tender may not require reconstruction of every historic policy source when the result would not change the commercial decision.

The Research Frontier ranks only material gaps.

## 11. Independent project/funding/procurement states

Track these separately from I0–I9 and from collection coverage.

### Project state

- `NO_PROJECT_IDENTIFIED`
- `CONCEPT_OR_PROPOSAL`
- `PROCESSING_OR_APPRAISAL`
- `APPROVED`
- `ADP_RADP_INCLUDED`
- `IMPLEMENTING`
- `REVISED_OR_EXTENDED`
- `COMPLETED`
- `UNKNOWN`

Preserve raw terms such as DPP/RDPP/TAPP/RTAPP/PEC when evidenced; do not infer document status from a title alone.

### Funding state

- `UNIDENTIFIED`
- `BUDGET_HYPOTHESIS`
- `GOB_INDICATED`
- `PROJECT_AID_INDICATED`
- `LOAN_GRANT_NEGOTIATION`
- `FINANCING_APPROVED_OR_SIGNED`
- `ALLOCATION_CONFIRMED`
- `DISBURSEMENT_OR_IMPLEMENTATION_EVIDENCE`
- `UNKNOWN`

### Procurement-planning state

- `NO_PLAN_FOUND`
- `NEED_IDENTIFIED`
- `PROCUREMENT_STRATEGY_SIGNAL`
- `APP_OR_PLAN_SIGNAL`
- `PACKAGE_IDENTIFIED`
- `PRE_PROCUREMENT`
- `TENDER_READY_OR_IMMINENT`
- `LIVE`
- `AWARDED`
- `CANCELLED_OR_RETENDER`

These axes feed I0–I9 but do not replace it.

## 12. Bangladesh interpretation of I0–I9

| Level | Bangladesh interpretation | Typical evidence |
|---|---|---|
| I0 | Signal | user seed, policy mention, product-fit hypothesis, weak lead |
| I1 | Hypothesis | plausible government requirement from mission/history/institutional signal |
| I2 | Validated Need | official rationale, capability gap, recurring demand or current-system gap |
| I3 | Institutional Path | owner/end user/implementing/PE chain materially understood |
| I4 | Delivery/Funding Path | credible budget/project/financing/defence/PPP route exists |
| I5 | Actionable Context | approved/actionable project, programme, budget or acquisition context |
| I6 | Procurement Planning | procurement strategy/APP/package/purchase plan/specification planning evidenced |
| I7 | Pre-Procurement | EOI/PQ/consultant/specification/evaluation/standardization/pre-market activity |
| I8 | Procurement Imminent | strong evidence formal solicitation is near |
| I9 | Live | formal solicitation published |

Coverage is not maturity. A candidate may have broad 360° coverage and still remain I1; another may be I9 while some non-material lenses remain `UNASSESSED`.

## 13. Route-specific I4–I7 evidence

### `BD-GEN-EGP`
- I4/I5: budget/purchase need, agency programme, allocation or approved operational requirement;
- I6: APP/procurement strategy/package;
- I7: EOI/PQ/specification/market/pre-tender activity.

### `BD-DEV-GOB`
- I4: project-processing/approval and GoB funding path;
- I5: approved project and/or ADP/RADP context;
- I6: project procurement plan/APP/package;
- I7: consultant/EOI/PQ/specification/pre-tender activity.

### `BD-DEV-DP`
- I4: credible external financing path;
- I5: financing/project approval context;
- I6: partner or GoB procurement plan/package;
- I7: partner-specific EOI/PQ/consultant/specification activity.

### `BD-DEF-DGDP`
- I4: evidenced service/defence acquisition path;
- I5: actionable acquisition/evaluation/standardization trajectory;
- I6: procurement/tender preparation or identified DGDP/e-DP path/package;
- I7: evaluation/re-evaluation/standardization, EOI/RFP/pre-bid or equivalent concrete activity.

### `BD-SOE-AUT`
- I4/I5: entity budget/project/board/approved programme evidence;
- I6: procurement plan/package;
- I7: EOI/PQ/specification/market activity.

### `BD-PPP`
- I4: PPP project/approval/transaction structure;
- I5: approved PPP project and contracting-authority context;
- I6: adviser/procurement preparation;
- I7: EOI/IFB/prequalification/transaction process.

### `BD-G2G-STRAT`
- I4: bilateral/G2G/strategic route evidenced;
- I5: approval/financing/implementation vehicle materially established;
- I6/I7: formal negotiation, arrangement, selection/procurement step or invitation where authoritatively evidenced.

## 14. Procurement reconciliation

For every APP, package, tender, amendment, cancellation, re-tender, award, DGDP item, PPP notice or donor event:

`Extract → Preserve raw IDs → Normalize aliases → Resolve institution/project/package → Search canonical ARGUS → Compare underlying requirement → Match/update or create candidate → Update evidence and route state → Reassess maturity and coverage → Update next action`

Prefer stable identifiers over fuzzy names.

Do not create duplicate opportunities merely because:

- the same project appears in successive ADPs/RADPs;
- a revision changes cost/duration/title;
- a package is re-tendered;
- an APP entry is carried forward;
- the PE/project office changes;
- an amendment creates a new notice date.

Revisions update lineage unless evidence supports a genuinely distinct underlying commercial requirement.

## 15. False-positive controls

Explicitly distinguish:

- policy aspiration ≠ funded procurement;
- ADP/project inclusion ≠ guaranteed package procurement;
- budget allocation ≠ tender authorization;
- financing agreement ≠ approved procurement schedule;
- APP/package ≠ live tender;
- tender ≠ new opportunity if the underlying requirement already exists;
- DGDP evaluation/standardization ≠ guaranteed contract;
- media report ≠ official requirement;
- OEM marketing visit ≠ procurement evidence;
- recurring lines ≠ separate opportunities when they belong to one system/programme lifecycle;
- broad 360° coverage ≠ high procurement probability;
- high source count ≠ independent evidence convergence.

## 16. Defence mode

For Army, Navy, Air Force, defence ministry bodies or DGDP-related acquisition:

1. ATLAS applies defence/national-security sensitivity and authorization controls first.
2. ARGUS uses only public, authorized internal or otherwise lawful sources.
3. Monitor DGDP/e-DP separately from general e-GP.
4. Treat end user, service HQ/directorate, DGDP wing/section, acquisition/project authority and funding as separate roles until evidenced.
5. Capture evaluation/re-evaluation/standardization, EOI/RFP, pre-bid, tender, amendment and award as distinct events.
6. Use installed-base age, spares, training, maintenance and modernization signals for future-opportunity discovery.
7. Do not infer classified capability, deployment, readiness, vulnerability or operational location from commercial procurement research.
8. Apply 360° collection proportionately; do not seek sensitive operational detail merely to fill a lens.

## 17. PPP mode

For PPP/concession opportunities:

- monitor PPP project/status information;
- distinguish project approval from live private-partner procurement;
- identify contracting authority, transaction adviser and stage;
- track EOI/IFB/corrigenda and PPP procurement guidance;
- preserve G2G-PPP and unsolicited-proposal distinctions where evidenced;
- do not force PPP opportunities into ordinary APP/e-GP assumptions.

## 18. Internal-first rule

Before new external research, search where available:

1. ARGUS Master Registry;
2. existing PX records;
3. authorized communications;
4. SharePoint/project/tender evidence;
5. `SUPPLIER_PRODUCT` and installed-base intelligence;
6. `KNOWLEDGE` and prior research;
7. reconciled DTIF legacy history;
8. then Bangladesh external sources appropriate to the route and the unresolved 360° lens.

## 19. Research Frontier

Prioritize the unresolved question or collection gap most likely to change the next commercial decision.

Typical questions:

- Is the need real and institutionally owned?
- Which entity is end user, implementing agency and PE?
- Which route applies?
- Does a project/budget/financing path exist?
- Is the project approved, ADP/RADP included or still processing?
- Is there an APP/package/procurement-plan signal?
- Is a development partner controlling the procurement framework?
- Is DGDP/e-DP the operative defence route?
- Is a PPP/G2G route more likely than standard procurement?
- What is the incumbent/installed base and replacement window?
- Which supplier/competitor or ecosystem actor materially shapes the opportunity?
- Does an existing PX already cover the requirement?
- What participation constraint could prevent pursuit?
- What event would materially increase or decrease procurement probability?

Stop when additional work is unlikely to alter the domain decision or next action.

## 20. Promotion gate

A Bangladesh candidate may be recommended for `PROMOTE_TO_PX` without a live tender when proportionately satisfied that:

- Access Asia has credible commercial relevance;
- a real or credibly emerging public-sector requirement exists;
- the institutional chain is sufficiently understood for action;
- the likely route is known or narrowed enough to act;
- there is a plausible project, budget, financing, acquisition or procurement path;
- duplicate review is sufficiently complete;
- material evidence provenance is preserved;
- materially relevant 360° collection gaps are explicit;
- significant unknowns/blockers are explicit;
- the next commercial action is clear.

Do not impose a fixed number of `ADEQUATE` lenses. Promotion sufficiency is proportional to the opportunity, route, maturity and decision risk.

Promotion basis may include:

- `EARLY_STRATEGIC_REQUIREMENT`
- `APP_OR_PACKAGE`
- `FUNDED_PROJECT`
- `DEFENCE_PREPROCUREMENT`
- `PPP_TRANSACTION`
- `LIVE_TENDER`
- `REPLACEMENT_OR_INSTALLED_BASE`

Permanent PX creation remains a separate governed action under ATLAS.

## 21. Monitoring events

Monitoring is event- and lens-aware rather than generic website watching.

Useful events include:

- APP/package creation or change;
- tender/EOI/PQ/RFP/IFB;
- amendment/corrigendum/extension;
- pre-bid activity;
- evaluation/re-evaluation/standardization;
- award/cancellation/re-tender;
- project approval/revision/extension;
- ADP/RADP inclusion or allocation change;
- financing agreement/disbursement milestone;
- consultant/transaction-adviser appointment;
- PPP status change;
- supplier/incumbent change;
- lifecycle/obsolescence trigger;
- relevant policy/regulatory change.

Detected events re-enter normal ARGUS reconciliation and do not create PX opportunities directly.

## 22. Domain result for Bangladesh

The ARGUS domain result may include:

- objective;
- candidate/opportunity;
- Bangladesh route and confidence;
- decision and rationale;
- I0–I9 maturity;
- institutional chain;
- project/budget/funding state;
- procurement planning/package state;
- procurement state/horizon;
- commercial relevance;
- evidence and provenance;
- `collection_coverage` across materially relevant 360° lenses;
- `collection_gaps` ranked by decision impact;
- source convergence information where useful;
- unknowns/conflicts;
- Research Frontier;
- next material trigger;
- next recommended action;
- proposed domain/registry actions.

This is an ARGUS domain result returned to ATLAS, not the final user-facing output contract.

## 23. Example: Coastal Surveillance Radar — Bangladesh Navy

Seed only:

- likely route hypothesis: `BD-DEF-DGDP`, pending evidence;
- record: `INTELLIGENCE` candidate;
- maturity: normally I0;
- no assumption that a procurement exists;
- initial 360° checks should include `need_mission`, `institution_stakeholders`, `procurement_acquisition`, `technical_installed_base`, `supplier_competitor`, `commercial_participation`, `timing_triggers` and `internal_intelligence`;
- `budget_funding`, `programme_project`, `policy_strategy` and `ecosystem_influence` are assessed when material to the decision rather than mechanically filled;
- search DGDP/e-DP evaluation/standardization/pre-bid/tender signals and authorized Access Asia history;
- distinguish source count from independent confirmation;
- promotion only after a credible requirement/path, commercial fit and explicit material collection gaps are understood.

This demonstrates the profile rule: route, institutional reality and collection sufficiency are researched, not assumed from the product name.

## 24. Implementation impact

No ATLAS OS change is required.

No new ARGUS top-level record type is required.

No Registry API rewrite is justified solely by the 360° doctrine.

Before canonical promotion of this profile, confirm that the implementation can represent:

- Bangladesh route fields;
- claim type vs claim condition;
- collection coverage states;
- collection gaps;
- source-lineage/convergence metadata where used;
- existing record compatibility without forced migration of every historic record.

Coverage fields are optional and should be added proportionately rather than backfilled mechanically across the entire Registry.
