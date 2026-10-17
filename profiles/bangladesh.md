# ARGUS Bangladesh Country Profile

**Version:** 2.0.0-rc.1  
**Status:** Candidate  
**Country:** Bangladesh (`BD`)  
**Production runtime:** ATLAS OS required for Access Asia

## 1. Purpose

This profile specializes ARGUS for Bangladesh government and public-sector opportunity intelligence.

It does not redefine ARGUS Core and does not modify ATLAS OS.

In Access Asia production use:

`User objective → ATLAS OS → ARGUS Bangladesh method → ARGUS domain result + proposed actions → ATLAS verification/approval → authorized domain action(s) → ATLAS persistence/delivery`

The objective is to identify credible Bangladesh public-sector demand early enough to understand the institutional owner, project/budget/funding path, procurement route, timing, solution fit and next commercially useful action before or during formal procurement.

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

## 9. Independent project/funding/procurement states

Track these separately from I0–I9.

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

## 10. Bangladesh interpretation of I0–I9

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

Evidence is route-specific. A revenue procurement can reach I5 without a development project; a defence acquisition can reach I7 through evaluation/standardization without a public ADP trail.

## 11. Route-specific I4–I7 evidence

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

## 12. Procurement reconciliation

For every APP, package, tender, amendment, cancellation, re-tender, award, DGDP item, PPP notice or donor event:

`Extract → Preserve raw IDs → Normalize aliases → Resolve institution/project/package → Search canonical ARGUS → Compare underlying requirement → Match/update or create candidate → Update evidence and route state → Reassess maturity → Update next action`

Prefer stable identifiers:

- e-GP tender/APP/package ID;
- DGDP tender number/wing/section;
- project code/official title;
- ADP/approved-project identifier;
- PPP project identifier/title;
- development-partner project/financing IDs;
- PE/office;
- package number;
- fiscal year;
- approval/notice reference.

Names are secondary because Bangla/English transliteration, abbreviations, spelling and revised project titles vary.

## 13. Alias and naming rules

Preserve:

- official Bangla name where available;
- official English name;
- acronym;
- previous/renamed ministry/division/agency title;
- transliteration/spelling variants;
- project revision suffixes;
- portal IDs;
- raw tender/package reference exactly as published.

Normalization must not destroy the source string.

## 14. Fiscal-year and revision semantics

Track Bangladesh fiscal year explicitly, e.g. `2026-27`, alongside calendar dates.

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
- recurring lines ≠ separate opportunities when they belong to one system/programme lifecycle.

## 16. Commercial route flags

ARGUS may surface early participation/compliance flags without performing full bid compliance:

- international vs national procurement;
- possible local-partner/JV requirement;
- supplier/DGDP enlistment;
- foreign OEM eligibility uncertainty;
- beneficial-owner disclosure;
- sustainable-procurement requirement;
- development-partner framework;
- export/end-use sensitivity;
- local works/installation/training/service component;
- warranty/after-sales/spares lifecycle;
- import/LC/payment-route relevance;
- framework-agreement/recurring-demand potential.

Each flag requires source/applicability evidence. Route labels do not themselves prove legal requirements.

## 17. Defence mode

For Army, Navy, Air Force, defence ministry bodies or DGDP-related acquisition:

1. ATLAS applies defence/national-security sensitivity and authorization controls first.
2. ARGUS uses only public, authorized internal or otherwise lawful sources.
3. Monitor DGDP/e-DP separately from general e-GP.
4. Treat end user, service HQ/directorate, DGDP wing/section, acquisition/project authority and funding as separate roles until evidenced.
5. Capture evaluation/re-evaluation/standardization, EOI/RFP, pre-bid, tender, amendment and award as distinct events.
6. Use installed-base age, spares, training, maintenance and modernization signals for future opportunity discovery.
7. Do not infer classified capability, deployment, readiness, vulnerability or operational location from commercial procurement research.

## 18. PPP mode

For PPP/concession opportunities:

- monitor PPP Authority project/status information;
- distinguish project approval from live private-partner procurement;
- identify contracting authority, transaction adviser and stage;
- track EOI/IFB/corrigenda and PPP procurement guidance;
- preserve G2G-PPP and unsolicited-proposal distinctions where evidenced;
- do not force PPP opportunities into ordinary APP/e-GP assumptions.

## 19. Internal-first rule

Before new external research, search where available:

1. ARGUS Master Registry;
2. existing PX records;
3. authorized communications;
4. SharePoint/project/tender evidence;
5. `SUPPLIER_PRODUCT` and installed-base intelligence;
6. `KNOWLEDGE` and prior research;
7. reconciled DTIF legacy history;
8. then Bangladesh external sources appropriate to the route.

## 20. Research Frontier

Prioritize the unresolved question most likely to change the next commercial decision.

Typical questions:

- Is the need real and institutionally owned?
- Which entity is end user, implementing agency and PE?
- Which route applies?
- Does a project/budget/financing path exist?
- Is the project approved, ADP/RADP included or still processing?
- Is there an APP/package/procurement-plan signal?
- Is a development partner controlling the procurement framework?
- Is DGDP/e-DP the operative defence route?
- Is PPP/G2G more likely than standard procurement?
- What is the incumbent/installed base and replacement window?
- Does an existing PX already cover the requirement?
- Does the route create a local-partner/JV, enlistment or other participation issue?
- What event would materially change procurement probability?

Stop when additional research is unlikely to alter the decision or next action.

Under ATLAS governance, Research Frontier feeds the ATLAS plan/work-unit mechanism and never self-schedules execution.

## 21. Promotion gate

A live tender is not required for promotion.

Recommend `PROMOTE_TO_PX` when proportionately satisfied that:

- Access Asia has credible commercial relevance;
- a real or credibly emerging public-sector requirement exists;
- the institutional chain is sufficiently understood for action;
- the likely route is known or narrowed enough to act;
- there is a plausible project, budget, financing, acquisition or procurement path;
- duplicate review is complete enough;
- material evidence provenance is preserved;
- significant unknowns/blockers are explicit;
- the next commercial action is clear.

Possible `promotion_basis` values:

- `EARLY_STRATEGIC_REQUIREMENT`
- `APP_OR_PACKAGE`
- `FUNDED_PROJECT`
- `DEFENCE_PREPROCUREMENT`
- `PPP_TRANSACTION`
- `LIVE_TENDER`
- `REPLACEMENT_OR_INSTALLED_BASE`

`PROMOTE_TO_PX` is a domain recommendation. Permanent PX creation is a separate proposed action subject to ATLAS authorization/approval.

## 22. Monitoring events

Prefer event-based monitoring over generic website watching.

Useful events:

- APP/package change;
- tender/EOI/PQ/RFP/IFB;
- corrigendum/extension;
- pre-bid event;
- evaluation/re-evaluation/standardization;
- award/cancellation/re-tender;
- project approval/revision/extension;
- ADP/RADP allocation change;
- financing agreement/disbursement milestone;
- consultant/transaction-adviser appointment;
- PPP stage change;
- DGDP/e-DP supplier/procurement-policy change;
- installed-base lifecycle/obsolescence signal;
- material policy/regulatory change.

Detected events re-enter normal ARGUS resolution/reconciliation. They never create PX opportunities directly.

## 23. Bangladesh-specific fields

Do not add new top-level Master Registry record types. Use type-specific fields where useful:

- `bd_route_class`
- `bd_route_confidence`
- `fiscal_year_bd`
- `sponsoring_ministry_division`
- `implementing_agency`
- `end_user_operator`
- `procuring_entity`
- `approving_authority`
- `project_director_or_piu`
- `project_official_id`
- `project_approval_state`
- `adp_radp_state`
- `funding_state`
- `funding_source`
- `development_partner`
- `financing_reference`
- `procurement_strategy_reference`
- `app_reference`
- `package_reference`
- `portal_system`
- `portal_record_id`
- `procurement_method_raw`
- `procurement_category_raw`
- `local_partner_jv_flag`
- `supplier_enlistment_flag`
- `sensitivity_flag`
- `promotion_basis`
- `next_material_trigger`
- `last_verified_at`

Preserve raw source terminology alongside normalized values.

## 24. Evidence semantics

Claim type:

- `FACT`
- `DERIVED`
- `INFERENCE`
- `ASSUMPTION`
- `UNKNOWN`

Claim condition:

- `CURRENT`
- `STALE`
- `CONFLICT`

When ATLAS governs execution, its assurance classes and evidence health are independent. ARGUS `FACT` does not imply ATLAS `VERIFIED`.

## 25. ARGUS Bangladesh Domain Result Contract

The Bangladesh method returns a domain-result object to ATLAS. It is not the final user-facing answer.

Recommended fields:

- `objective`
- `candidate_or_opportunity`
- `bangladesh_route`
- `route_confidence`
- `decision`
- `maturity`
- `institutional_chain`
- `project_budget_funding`
- `procurement_planning_package`
- `procurement_state_horizon`
- `commercial_relevance`
- `evidence`
- `unknowns_conflicts`
- `research_frontier`
- `next_material_trigger`
- `next_recommended_action`
- `proposed_domain_actions`
- `proposed_registry_actions`

ATLAS verifies material claims, selects the final output profile, authorizes applicable actions, persists task artifacts/receipts and delivers.

## 26. Example: Coastal Surveillance Radar — Bangladesh Navy

For a seed only:

- route: `BD-DEF-DGDP` as a hypothesis, pending evidence;
- record: `INTELLIGENCE` candidate;
- maturity: normally I0;
- no assumption that procurement exists;
- resolve Navy/service end user, DGDP/e-DP role, acquisition/project path, funding and installed-base evidence;
- search authorized internal history and lawful DGDP evaluation/re-evaluation/standardization/pre-bid/tender signals;
- promote only after a credible requirement/path and commercial fit exist.

This demonstrates the central rule: route and institutional reality are researched, not assumed from the product name.

## 27. Implementation gates before canonical promotion

- Registry API can represent the Bangladesh fields or equivalent extensible attributes.
- Evidence representation can separate claim type, freshness and conflict.
- Route classification can be stored without breaking existing records.
- v1 → v2 profile compatibility is tested with existing Bangladesh records.
- General e-GP, GoB development, development-partner, DGDP/e-DP and PPP routes are tested.
- APP → tender → amendment → award reconciliation avoids duplicate opportunities.
- A defence pre-procurement evaluation/standardization signal is tested.
- A project carried across fiscal years/RADP does not duplicate the opportunity.
- Promotion-before-live-tender behavior is tested.

No ATLAS OS change, new top-level ARGUS record type or Registry API rewrite is justified solely by this profile.
