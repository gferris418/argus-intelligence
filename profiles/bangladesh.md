# ARGUS Bangladesh Country Profile

**Version:** 2.1.0-rc.1  
**Status:** Candidate  
**Country:** Bangladesh (`BD`)  
**Production runtime:** ATLAS OS required for Access Asia

## 1. Purpose

This profile specializes ARGUS for Bangladesh government and public-sector commercial opportunity intelligence.

It does not redefine ARGUS Core. It maps the Core mission model to Bangladesh institutions, procurement routes, source families, terminology and operating patterns.

In Access Asia production use:

`User objective → ATLAS OS → one bounded ARGUS mission → ARGUS domain result + proposed batched action → ATLAS verification/approval/persistence → ATLAS delivery`

The objective is to identify credible Bangladesh public-sector demand early enough to understand the government hierarchy, end user, project/budget/funding path, procurement route, timing, internal customer history, solution fit, supplier/competitor context and next commercially useful action before or during formal procurement.

## 2. Governing principle

**A Bangladesh opportunity is not synonymous with a tender.**

The same underlying requirement may appear progressively through policy, strategy, institutional need, programme, project, financing, APP/procurement plan, standardization, EOI/PQ, tender, amendment, award, implementation, installed base, upgrade, replacement or recurring-support evidence.

A published tender is one evidence event in a longer chain, not the default beginning of the opportunity.

## 3. Current-context rule

This profile may cache a dated Bangladesh institutional and source baseline for operational use, but it is not the runtime authority for current law or current procurement status.

When law, rules, financing conditions, organizational control, publication channels or other current facts materially affect the result, ARGUS/ATLAS must revalidate them from competent current sources.

## 4. First mandatory Bangladesh step: institutional hierarchy

For a named Bangladesh government buyer/end user, resolve the hierarchy before broad procurement or supplier research:

`Bangladesh Government → Ministry/Division → Agency/Authority/SOE → subordinate unit/project office/procuring entity → end user/operator`

Resolve only what evidence supports. Do not infer that the parent ministry is the procuring entity, that the agency is the end user, or that a project director is a permanent institutional entity.

Example pattern for the Bangladesh Coast Guard CPV case:

`Government of Bangladesh → Ministry of Home Affairs → Bangladesh Coast Guard Force → Project Director / applicable project or procuring office → operational end user as evidenced`

The hierarchy is reusable institutional intelligence. Once canonically resolved and still current, future Coast Guard investigations should reuse it rather than reconstruct it from scratch, while time-sensitive roles remain subject to revalidation.

## 5. Second mandatory Bangladesh step: internal canonical identity check

Before creating a new requirement, project, procurement, tender or opportunity, search the current ARGUS canonical registry.

Preferred identity evidence order:

1. exact official identifier;
2. exact source-system identifier;
3. project/package/procurement relationships;
4. buyer/entity + official reference;
5. buyer + requirement/product/capability + quantity/timing where material;
6. corroborated requirement semantics;
7. fuzzy title similarity only as a candidate signal, never as merge authority.

Identity behavior:

- `EXACT` / `HIGH_CONFIDENCE_MATCH` → continue on the existing canonical object without routine user confirmation;
- `DISTINCT` → continue as a new candidate without routine user confirmation;
- `PROBABLE_MATCH` / `UNRESOLVED` → ask only when selecting incorrectly could duplicate, merge or mutate the wrong opportunity.

Do not create a new commercial opportunity merely because a new tender, amendment, corrigendum, re-tender, award or portal record appears.

## 6. Third mandatory Bangladesh step: route classification and official procurement check

After institutional and internal identity resolution, classify the likely procurement route and check the competent official/public source families. If evidence is insufficient, use `BD-UNKNOWN` and research the route before making downstream assumptions.

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

The route is a research hypothesis until supported by evidence. One project may contain packages following different routes.

For Bangladesh Coast Guard, do **not** assume `BD-DEF-DGDP` merely because the requirement is maritime/security-related. Determine the competent procurement route from the actual procuring authority, publication source, governing method and project/funding evidence.

## 7. Fourth mandatory Bangladesh step: internal customer intelligence

After checking the applicable official procurement/publication sources, reconcile the external state with authorized Access Asia internal intelligence before broad supplier/market research.

Search where relevant and authorized:

1. ARGUS structured history already linked to the buyer/requirement;
2. SharePoint Business Intelligence, opportunity and project files;
3. HubSpot company/contact relationship state, interactions, notes and deals;
4. prior correspondence and meeting records;
5. quotations, proposals and concept material;
6. historical project, tender and award files;
7. supplier/product/installed-base history and prior research.

Internal evidence can be highly authoritative for Access Asia relationship/history claims but does not by itself establish a Bangladesh government approval, budget or procurement event.

Keep canonical masters in their owning systems. Use pointers/references rather than duplicate CRM or document masters inside ARGUS.

## 8. Bangladesh adaptive startup flow

Normal government-commercial mission flow:

`Institution hierarchy → internal canonical registry → identity reconciliation → official procurement sources → internal customer intelligence → Research Frontier → adaptive 360° collection`

The first five stages establish who the buyer is, whether the opportunity already exists, whether formal procurement has surfaced and what Access Asia already knows. After that, ARGUS chooses only intelligence capabilities that can materially change the commercial decision.

Examples:

- live tender + short deadline → prioritize tender requirements, disqualifiers, technical scope, supplier universe and partnerability;
- approved/planned project without tender → prioritize project/funding/approvals, stakeholders, shaping window and supplier strategy;
- early buyer need without project → prioritize policy/mission, installed base, capability gap, project-formation signals and suitable solution/OEM universe;
- supplier-led lead → identify Bangladesh government use cases, institutional owners, unmet need and existing opportunity identity before creating a new hypothesis.

## 9. Institutional-role model

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

## 10. Institutional graph

Use relationship concepts without forcing every opportunity to contain every node:

`Government priority → Ministry/Division → Agency/Authority/SOE → Programme/Project/Budget → End User → Project/PIU/PE → Funding → Procurement Plan/Strategy → Package → Pre-Procurement → Tender/Award → Installed Base`

Defence investigative pattern:

`Service need → Service HQ/directorate/end user → requirement/evaluation/standardization → DGDP/e-DP procurement path → tender/contract → installed base`

The pattern is investigative, not a presumption that every procurement follows an identical visible chain.

## 11. Bangladesh discovery vectors

### Policy-to-procurement
`National/sector priority → ministry/division → agency/end user → programme/project → budget/funding → procurement planning → package`

### Institution-downward
`Ministry/division → agency/authority → subordinate units/projects → end-user mission → current/planned requirements → procurement evidence`

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

## 12. Source architecture

Source authority is claim-specific. Use `profiles/bangladesh-procurement-source-standard-v1.0.yaml` for detailed source-family capabilities and stage-aware routing rather than recreating portal assumptions here.

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
- HubSpot relationship/interaction/deal state;
- prior quotations/proposals;
- OEM/consultant communications;
- meeting records;
- historical tender/award/project files;
- reconciled legacy history.

### Tier D — corroborating/open-source intelligence

OEM releases, consultant/EPC publications, credible industry sources, reputable media and event signals.

These may generate hypotheses but must not substitute for official evidence where official confirmation is materially required.

## 13. Bangladesh 360° Collection Map

Bangladesh specializes the twelve ARGUS Core collection lenses. The lens names and semantics remain Core-owned.

### `need_mission`
Determine the Bangladesh public-sector mission, service need, capability gap, statutory duty, modernization requirement, capacity constraint or recurring operational demand that could create procurement.

### `policy_strategy`
Identify policy, sector strategy, ministry priority, reform, modernization programme, regulatory change or institutional mandate that supports or constrains the requirement. Policy aspiration alone is not procurement evidence.

### `institution_stakeholders`
Resolve ministry/division, agency, implementing entity, end user, operator, PE, project office/PIU, approving authority, DGDP wing/section where relevant, development partner, consultant/adviser and other actors capable of shaping the outcome.

### `programme_project`
Search for the programme, development project, acquisition context, PPP transaction, SOE programme, operational budget initiative or other implementation vehicle capable of delivering the requirement. Preserve revisions, official IDs and fiscal-year continuity.

### `budget_funding`
Assess GoB allocation, ADP/RADP context, project aid, ERD/financing evidence, loan/grant status, bilateral/G2G financing, SOE budget, PPP financing structure or other relevant source. Budget indication, financing approval and procurement allocation remain separate claims.

### `procurement_acquisition`
Resolve the actual or likely Bangladesh route: e-GP/APP/package, project procurement plan, donor framework, DGDP/e-DP, PPP, SOE/autonomous channel, G2G/strategic route or local-government route. Track pre-procurement, tender, amendment, award, cancellation and re-tender as related events rather than automatically separate opportunities.

### `technical_installed_base`
Identify current equipment/system/service, OEM/incumbent, age, delivery/installation history, support state, recurring spares/training, obsolescence, capacity shortfall, interoperability constraints and upgrade/replacement window where lawfully available. For defence, do not infer classified capability, readiness, vulnerability, deployment or operational location.

### `supplier_competitor`
Map incumbents, historical suppliers, relevant OEMs, competing technologies, prior bidders/awardees and commercially plausible competitors. Separate verified award/incumbent history from market speculation.

### `ecosystem_influence`
Map consultants, EPCs, system integrators, donors/lenders, transaction advisers, local partners/agents, technical advisers and other actors who may shape requirements, funding or route selection.

### `commercial_participation`
Assess national/international method, JV/local-partner issues, supplier/DGDP enlistment, foreign OEM eligibility, development-partner rules, export/end-use sensitivity, local installation/training/service obligations, import/LC/payment route and after-sales lifecycle. These are flags for downstream verification, not legal conclusions.

### `timing_triggers`
Track events that may accelerate, delay, cancel, revive or expand demand: project approval/revision, ADP/RADP inclusion, allocation change, financing agreement, consultant appointment, evaluation/standardization, APP/package creation, tender calendar, incumbent obsolescence, policy change and capacity expansion.

### `internal_intelligence`
Use authorized Access Asia prior correspondence, meetings, proposals, quotations, project history, relationships, customer files, supplier/product history and prior research. Reconcile them with external evidence rather than treating them as independent proof of a government procurement event.

## 14. Bangladesh collection coverage

Use Core coverage states:

- `NOT_APPLICABLE`
- `UNASSESSED`
- `INSUFFICIENT`
- `PARTIAL`
- `ADEQUATE`

The profile does not require every lens to become `ADEQUATE`.

Examples:

- an I0 signal may justify rapid checks of hierarchy, `need_mission`, `institution_stakeholders`, `procurement_acquisition` and `internal_intelligence` first;
- a defence pre-procurement candidate may require stronger `technical_installed_base`, `institution_stakeholders`, `procurement_acquisition`, `supplier_competitor` and `commercial_participation` coverage before promotion;
- a development project may require stronger `programme_project`, `budget_funding` and `procurement_acquisition` coverage;
- a live tender may not require reconstruction of every historic policy source when that work would not change the commercial decision.

The Research Frontier ranks only material gaps.

## 15. Independent project/funding/procurement states

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

## 16. Bangladesh interpretation of I0–I9

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

## 17. Route-specific I4–I7 evidence

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

## 18. Procurement reconciliation

For every APP, package, tender, amendment, cancellation, re-tender, award, DGDP item, PPP notice or donor event:

`Extract → Preserve raw IDs → Normalize aliases → Resolve institution/project/package → Search canonical ARGUS → Compare underlying requirement → Match/update or create candidate → Update evidence and route state → Reassess maturity and coverage → Update next action`

Prefer stable identifiers over fuzzy names.

**Do not create duplicate opportunities** merely because:

- the same project appears in successive ADPs/RADPs;
- a revision changes cost/duration/title;
- a package is re-tendered;
- an APP entry is carried forward;
- the PE/project office changes;
- an amendment creates a new notice date.

Revisions update lineage unless evidence supports a genuinely distinct underlying commercial requirement.

## 19. False-positive controls

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

## 20. Defence mode

For Army, Navy, Air Force, defence ministry bodies or DGDP-related acquisition:

1. ATLAS applies defence/national-security sensitivity and authorization controls first.
2. ARGUS uses only public, authorized internal or otherwise lawful sources.
3. Monitor DGDP/e-DP separately from general e-GP.
4. Treat end user, service HQ/directorate, DGDP wing/section, acquisition/project authority and funding as separate roles until evidenced.
5. Capture evaluation/re-evaluation/standardization, EOI/RFP, pre-bid, tender, amendment and award as distinct events.
6. Use installed-base age, spares, training, maintenance and modernization signals for future-opportunity discovery.
7. Do not infer classified capability, deployment, readiness, vulnerability or operational location from commercial procurement research.
8. Apply 360° collection proportionately; do not seek sensitive operational detail merely to fill a lens.

## 21. PPP mode

For PPP/concession opportunities:

- monitor PPP project/status information;
- distinguish project approval from live private-partner procurement;
- identify contracting authority, transaction adviser and stage;
- track EOI/IFB/corrigenda and PPP procurement guidance;
- preserve G2G-PPP and unsolicited-proposal distinctions where evidenced;
- do not force PPP opportunities into ordinary APP/e-GP assumptions.

## 22. Research Frontier

Prioritize the unresolved question or collection gap most likely to change the next commercial decision.

Typical questions:

- Is the need real and institutionally owned?
- Which ministry/division controls the agency and which entity is end user, implementing agency and PE?
- Does an existing ARGUS/PX opportunity already cover the requirement?
- Which procurement route applies?
- Has an official procurement source published anything material?
- What does Access Asia already know from customer intelligence and relationship history?
- Does a project/budget/financing path exist?
- Is the project approved, ADP/RADP included or still processing?
- Is there an APP/package/procurement-plan signal?
- Is a development partner controlling the procurement framework?
- Is DGDP/e-DP the operative defence route?
- Is a PPP/G2G route more likely than standard procurement?
- What is the incumbent/installed base and replacement window?
- Which supplier/product/competitor or ecosystem actor materially shapes the opportunity?
- What participation constraint could prevent pursuit?
- What event would materially increase or decrease procurement probability?

Stop when additional work is unlikely to alter the identity outcome, domain decision, supplier strategy or next action.

## 23. Promotion gate

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

Permanent PX creation remains a separate governed action under ATLAS.

## 24. Monitoring events

Monitoring is event- and lens-aware rather than generic website watching.

Useful events include APP/package creation/change, tender/EOI/PQ/RFP/IFB, amendments/corrigenda/extensions, pre-bid activity, evaluation/re-evaluation/standardization, awards/cancellation/re-tender, project approval/revision/extension, ADP/RADP inclusion/allocation changes, financing milestones, consultant appointments, PPP changes, supplier/incumbent changes, lifecycle/obsolescence triggers and relevant policy changes.

Detected events re-enter institutional and canonical-identity reconciliation before changing an opportunity.

## 25. Domain result for Bangladesh

The ARGUS domain result may include:

- objective;
- resolved institutional hierarchy;
- candidate/opportunity and identity outcome;
- Bangladesh route and confidence;
- decision and rationale;
- I0–I9 maturity;
- project/budget/funding state;
- procurement planning/package/tender state;
- internal customer-intelligence summary;
- supplier/product/competitor assessment where material;
- commercial relevance;
- evidence and provenance;
- `collection_coverage` across materially relevant 360° lenses;
- `collection_gaps` ranked by decision impact;
- source convergence information where useful;
- unknowns/conflicts;
- Research Frontier;
- next material trigger;
- next recommended action;
- one proposed mutation batch where canonical persistence is useful.

This is an ARGUS domain result returned to ATLAS, not the final user-facing output contract.

## 26. Example: Bangladesh Coast Guard — Coastal Patrol Vessel

Seed: `Coastal Patrol Vessel for Bangladesh Coast Guard`.

Required startup behavior:

1. resolve `Bangladesh → Ministry of Home Affairs → Bangladesh Coast Guard Force → applicable project/procuring office/end-user role` from authoritative evidence;
2. search the current ARGUS registry for existing Coast Guard patrol-vessel requirements, projects, procurements, tenders and opportunities before creating anything new;
3. reconcile identity using official reference/project/package IDs first and escalate only if an existing CPV opportunity is materially ambiguous;
4. check BPPA/e-GP, Coast Guard/Ministry sources and relevant project/funding systems according to the evidenced route; do not assume DGDP;
5. check authorized Access Asia customer intelligence, relationship history, prior files/correspondence/proposals and supplier history;
6. build the Research Frontier from remaining gaps such as upstream project, budget, technical specification, decision-makers, incumbents or likely competition;
7. activate supplier/OEM/product/competitor research when it can change participation or commercial strategy.

A live tender can establish I9 while upstream project/package identifiers remain `UNKNOWN`. Blank portal fields must not be fabricated.

## 27. Implementation impact

This profile uses the shared ATLAS collection-mission execution policy and ARGUS bounded-autonomous runtime. It does not create a new top-level ARGUS record type or a second orchestration spine.

The current mutable structured state remains in the governed SharePoint SQLite registry; GitHub remains schema/method/migration/test/release-snapshot authority.

Before production use, verify cross-repository contract compatibility and the current source/persistence adapters. Coverage fields remain proportional and should not be mechanically backfilled across every historic record.
