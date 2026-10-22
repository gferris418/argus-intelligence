# Bangladesh Canonical Procurement Schema v2.1

**Status:** Candidate  
**Country:** Bangladesh (`BD`)  
**Machine schema:** `schemas/bangladesh-procurement-v2.1.schema.json`  
**International alignment:** `profiles/bangladesh-procurement-international-alignment-v1.0.yaml`  
**Production authority:** v1.3 remains active until a separate governed migration decision.

## Purpose

Provide one portal-neutral database model for procurement information published through BPPA, e-GP, DGDP/e-DP, PPP, ministries/agencies/SOEs and development partners while preserving source-native terminology and supporting international interoperability.

## International design baseline

### OCDS 1.1.5

Use the Open Contracting Data Standard as the lifecycle/interchange backbone:

`parties -> planning -> tender -> awards -> contracts -> implementation`

ARGUS keeps a stable internal `procurement_id`, can optionally map to an `ocid`, preserves related processes, stores immutable source releases and derives a compiled current record.

Reference: https://standard.open-contracting.org/latest/en/schema/reference/

### World Bank

World Bank IPF Procurement Regulations and STEP inform planning, bidder/evaluation and award transparency fields. The v2.1 schema can retain bidder/proposer identities, opening values, evaluated values, responsiveness/rejection state and reason, successful supplier, final award value, contract duration, scope summary, intention-to-award/standstill dates, award notice and a beneficial-ownership disclosure reference where applicable.

Reference: https://www.worldbank.org/en/projects-operations/products-and-services/brief/procurement-new-framework

### Asian Development Bank

ADB procurement planning informs package-level planning fields: package description, method, bidding document type, estimated cost, expected advertisement date, review procedure and contract-supervision arrangement.

Reference: https://www.adb.org/site/business-opportunities/operational-procurement/goods-services-pp

## Canonical lifecycle

```text
PROCUREMENT
  |
  +-- identifiers
  +-- related_processes
  +-- parties
  |
  +-- planning
  |     +-- project
  |     +-- budget
  |     +-- financing
  |     +-- procurement_plan
  |
  +-- tender
  |     +-- method / category / route
  |     +-- lots
  |     +-- items
  |     +-- milestones
  |     +-- requirements
  |     +-- fees
  |     +-- securities
  |     +-- submissions / evaluation outcomes
  |
  +-- notices
  +-- documents
  +-- events
  +-- complaints
  |
  +-- awards
  |
  +-- contracts
  |     +-- implementation
  |           +-- milestones
  |           +-- transactions
  |           +-- modifications
  |
  +-- source_releases
  +-- observations / provenance
  +-- ARGUS intelligence
```

## Core parameters

| Section | Canonical parameters | Meaning |
|---|---|---|
| Identity | `procurement_id`, `ocid`, `requirement_ref`, `title`, `record_state`, `record_revision` | Stable database identity, optional international interchange ID and underlying requirement lineage |
| Identifiers | typed `scheme`, `value`, `scope`, `source_system`, `source_label` | Preserve APP IDs, e-GP Tender IDs, tender references, DGDP Tender Nos, package, lot, project, PE, award and contract IDs without conflation |
| Parties | `party_id`, `roles`, source name/ID, unit label, contacts | Keep ministry, agency, PE, end user, implementing agency, funder, supplier, consultant and DGDP wing/section roles distinct |
| Planning | project, project code/status/cost, budget, financing, procurement plan | Capture pre-tender signals and package planning |
| Procurement plan | `plan_id`, type/version/status, package description, estimated cost, planned method, bidding document type, review type, expected advertisement, supervision arrangement | Supports APP, STEP, ADB and agency planning records |
| Tender | route, source category, normalized category/method, competition scope, process configuration, status, estimate, periods | One normalized process while preserving BPPA/DGDP/e-GP source wording |
| Lots/items | lot and item identity, description, quantity, UOM, value, classification, location | Supports single-lot, multi-lot and line-item procurement |
| Requirements | registration, enlistment, legal, experience, financial, technical, OEM, source-country, JV, local participation, standards, sustainability, security clearance | Structured bidder/product participation requirements |
| Submissions | bidder IDs, opening value, evaluated value, status, rejection reason, rank | Preserves evaluation transparency where legally/publicly available |
| Notices | GPN, plan, EOI, PQ, IFT/RFB/RFP/RFQ, corrigendum, addendum, award, cancellation, re-tender, implementation update | Publication objects are distinct from procurement state |
| Documents | notice, tender document, SBD, specification, BOQ, drawing, TOR, evaluation report, amendment, award notice, contract, implementation report | References source material without duplicating raw documents into Git |
| Events | publication, amendment, extension, cancellation, reissue, award, signing, modification, payment, completion | Append-only change history |
| Awards | selected supplier, value, scope, duration, intention to award, standstill, award notice, beneficial-ownership disclosure reference | Award decision is separate from signed contract |
| Contracts | number, supplier, value, signed date, period, status | Legal contract object |
| Implementation | progress, period, actual completion, current value, milestones, payments/transactions, modifications | Contract-execution history |
| Source releases | immutable release ID/system/type/date/hash/supersession | OCDS-style change history for every materially new publication/change |
| Observations | canonical field path, raw label/value, source, access class, claim type, condition, confidence | Field-level provenance |
| Intelligence | S0-S9 stage, SHAPE/POSITION/REACT/EXPAND, unknowns, contradictions, supplier state, next collection action | ARGUS-derived intelligence, never source fact |

## Bangladesh-specific normalization

### BPPA / e-GP

Preserve Ministry/Division, Agency, PE, PE code, district, invitation reference, source category (`Invitation For`), procurement method wording, budget source, project/programme fields, package fields, APP/e-GP IDs, selling/closing/opening dates, tender fees, securities and corrigenda.

### DGDP / e-DP

Preserve DGDP Tender No, wing, section/unit, tender name, source tender type, selling period, opening date, specification/amendment links, enlistment conditions and pre-procurement evaluation/re-evaluation/standardization signals.

### Development partners

Preserve financier IDs, financing references, lender review type, procurement-plan packages, eligible-country/financing conditions and financier-specific notice/award IDs.

## Hard semantic distinctions

Never collapse:

- `procurement_id` with any portal ID;
- `buyer` with `procuring entity`, `implementing agency`, `end user`, `approving authority` or `funder`;
- `project total cost` with `procurement estimate`, `bid value`, `evaluated value`, `award value` or `contract value`;
- `award` with `contract`;
- `notice` with `event`;
- `milestone` with `event`;
- `corrigendum` with `re-tender`;
- DGDP Tender No with e-GP Tender ID;
- source method/category wording with normalized interpretation.

## Change history

```text
SOURCE PUBLICATION / CHANGE
        |
        v
IMMUTABLE source_release
        |
        +--> notice / document
        +--> event(s)
        +--> field observations
        |
        v
COMPILED CURRENT PROCUREMENT RECORD
```

Original authoritative values remain recoverable even when the compiled current value changes.

## Missing data

A valid procurement record may be sparse. If a BPPA tender leaves Project/Programme Code, Project Name or Package No blank, ARGUS leaves those fields absent/UNKNOWN and searches upstream sources separately. Completeness must never be fabricated.

## Production migration rule

v2.1 is a successor **candidate**, not live production authority. Activation requires representative BPPA/e-GP, DGDP/e-DP, World Bank and ADB fixtures, no material information loss, passing contract tests and ATLAS↔ARGUS cross-repository validation.
