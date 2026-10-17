# Bangladesh Cross-Source Procurement Normalization v1.1

**Document ID:** ARGUS-BD-PROC-NORM-001  
**Status:** CANDIDATE  
**Date:** 2026-10-18  
**Scope:** Bangladesh public procurement, defence procurement, development-partner procurement and UN procurement notices relevant to Bangladesh

## Decision

ARGUS will normalize procurement intelligence by **concept and lifecycle stage**, not by portal or institution.

The same concept must use the same canonical field whether it originated from BPPA/e-GP, DGDP, World Bank, ADB, AIIB, JICA, UNGM, a ministry/agency portal or an authorized internal source. Source-specific terminology is preserved as evidence metadata and mapped only where semantic equivalence is clear.

The Bangladesh base data dictionary remains valid. v1.1 adds a procurement/financier extension rather than changing the seven Master Registry record types.

## Canonical lifecycle

`POLICY_STRATEGY → INSTITUTION → PROGRAMME_PROJECT → FUNDING → PROCUREMENT_PLAN → PROCUREMENT_PACKAGE → PRE_PROCUREMENT → SOLICITATION → AMENDMENT_PREBID → AWARD_CONTRACT → CONTRACT_EXECUTION → INSTALLED_BASE`

`PRE_PROCUREMENT` is newly explicit because Bangladesh and development-partner sources expose material advance signals that are not yet live solicitations: DGDP evaluation/re-evaluation/standardization, general procurement notices, advance notices and market-engagement events.

## Design improvements

### 1. Typed identity before fuzzy matching

Keep project IDs, financing references, procurement activity references, APP IDs, package numbers, lot identifiers, solicitation IDs/references and contract numbers as different identifier types even when values happen to match.

### 2. Common core plus structured repeatable modules

Flat fields are retained for single-valued concepts. Repeated source structures are preserved as arrays:

- `project.external_ids`
- `funding.financing_references`
- `procurement.lots`
- `procurement.milestones`

This avoids the common failure mode where multi-lot tenders or planned/actual procurement schedules are collapsed into one lossy value.

### 3. Procurement controls are independent dimensions

The following are separate concepts:

- procurement method;
- market approach;
- procurement process;
- financier review type;
- prequalification requirement;
- notice type;
- Bangladesh route;
- source of funding.

A World Bank activity can therefore be `Request for Bids`, `Open - National`, `Single Stage - One Envelope`, `Post Review`, under an IDA credit, without losing any dimension.

### 4. Participation requirements are decision-relevant

Preserve portal/vendor registration, source-country eligibility, local participation, sustainability requirements and submission channel separately from general eligibility text. These fields directly affect whether Access Asia can form a viable participation route.

### 5. Official source does not equal ATLAS VERIFIED

ARGUS records source authority and provenance. ATLAS independently evaluates evidence assurance, currency, conflicts and applicability.

## Source-pattern evidence

### BPPA / e-GP

Official BPPA notices expose Ministry/Division, Agency, PE, invitation reference, procurement method, budget/source of funds, project/package context, publication/selling/closing/opening dates, tender meeting, eligibility, tender document price, lot identification/location/security/completion period and inviting-official contact.

Observed official source:
`https://www.bppa.gov.bd/advertisement-goods/details-96495.html`

Normalization consequences:
- preserve tender document price as text when currency/lot allocation is ambiguous;
- parse tender-lot tables to `procurement.lots`;
- store pre-tender meeting and procurement contact separately;
- keep corrigenda as dated events, not overwritten source history.

### DGDP / e-DP

DGDP tender listings expose tender number, section, tender name, tender type, opening date, selling-from/to dates, notice/amendment/specification availability and updated-on date. DGDP separately publishes evaluation/re-evaluation/standardization notices by wing and publish date.

Observed official sources:
- `https://www.dgdp.gov.bd/open-tender/today`
- `https://www.dgdp.gov.bd/notice`

Normalization consequences:
- tender listings map to solicitation state;
- evaluation/re-evaluation/standardization maps to `PRE_PROCUREMENT` and must not be treated as a live tender without separate evidence.

### World Bank

World Bank procurement notices expose notice type, publication date, project ID, bid description, procurement category, procurement method and deadline. STEP-style procurement plans additionally expose project/loan identifiers, executing agency, activity reference, component, review type, market approach, procurement process, prequalification, estimated/actual amounts, process status and planned/actual milestone schedules.

Observed official sources:
- `https://projects.worldbank.org/en/projects-operations/procurement`
- `https://documents1.worldbank.org/curated/en/266291568644889519/pdf/Bangladesh-SOUTH-ASIA-P120843-BD-Private-Sector-Development-Procurement-Plan.pdf`

Normalization consequences:
- use typed `project.external_ids` and `funding.financing_references`;
- preserve Prior/Post review separately from method;
- preserve planned/actual milestones as `procurement.milestones`.

### Asian Development Bank

ADB procurement plans publish descriptions of goods/works/services, procurement method, contract estimates, threshold values, expected advertisement dates and ADB review procedure. ADB project pages expose tender title/type/status/posting/deadline and contract award information including contractor, executing agency, total contract amount and ADB-financed amount.

Observed official sources:
- `https://www.adb.org/site/business-opportunities/operational-procurement/goods-services-pp`
- `https://www.adb.org/business/project-procurement`

Normalization consequences:
- map ADB review procedure to `procurement.review_type`;
- map expected advertisement separately from actual publication;
- preserve total award amount separately from financier-financed portion.

### Asian Infrastructure Investment Bank

AIIB's project procurement opportunity list exposes issue date, member, project, contract description, contractor/supplier/consultant, contract price, contract signing date, sector, category and notice type, including Bangladesh general procurement notices and procurement plans.

Observed official source:
`https://www.aiib.org/en/opportunities/business/project-procurement/list.html`

Normalization consequences:
- route GPN/advance information to `PRE_PROCUREMENT`;
- preserve project/contract/award concepts using the same canonical fields as other financiers.

### JICA

JICA's ODA procurement architecture is borrower/executing-agency administered, generally using international competitive bidding and JICA standard procurement documents. Bangladesh ODA announcements can expose executing agency, project/package titles, planned release dates and procurement conditions; JICA rules additionally make eligible source countries material where applicable.

Observed official sources:
- `https://www.jica.go.jp/english/activities/schemes/finance_co/guide/tender/index.html`
- `https://www.jica.go.jp/english/information/press/2022/20230330_30.html`

Normalization consequences:
- preserve JICA loan reference in `funding.financing_references`;
- preserve procurement conditions and eligible-source-country conditions separately from general eligibility.

### UNGM / UN agencies

UNGM notices expose title, reference, beneficiary country/territory, organization, opportunity type, publication, deadline, registration level and goods/services classification. Individual notices may expose pre-bid/site visit information, submission portals, sustainability indicators and procurement contacts.

Observed official sources:
- `https://www.ungm.org/Public/Notice`
- `https://www.ungm.org/Public/Notice/297585`

Normalization consequences:
- Bangladesh beneficiary is jurisdiction context; the UN organization remains the procuring organization;
- preserve registration and submission-channel requirements;
- retain UNSPSC as a source classification reference/category for later ATLAS taxonomy alignment.

## Canonical write rule

A source observation proceeds:

`source → source-family identification → raw label/value preservation → canonical mapping → typed identity resolution → reconciliation → evidence assessment → Registry update/proposed action`

If the source concept has no safe canonical mapping, retain it as an unmapped material datapoint and extend the dictionary deliberately. Do not force it into the nearest-looking field.

## Storage boundary

GitHub stores schemas, mappings, structured observations, reconciled canonical data and synthesized intelligence. It does **not** store raw tender/bidding-document bytes, attachments or email payloads.
