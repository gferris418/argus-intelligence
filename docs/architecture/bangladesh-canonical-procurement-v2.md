# Bangladesh Canonical Procurement Standard v2.0 — Semantic Design

**Document ID:** ARGUS-BD-PROC-V2-DESIGN-001  
**Status:** CANDIDATE  
**Date:** 2026-10-18  
**Live-record migration:** DEFERRED

## Decision

ARGUS will move from the incrementally grown Bangladesh procurement field vocabulary toward a semantically normalized contracting-process model in which **one real-world concept has one canonical home**.

The v2 candidate does not yet replace v1.3 for live writes. It defines the target model and an exhaustive v1.x migration map first. Current registry records remain unchanged until a separate migration is tested and approved.

## International design basis

The design is informed by:

- Open Contracting Data Standard (OCDS) 1.1.5: contracting-process lifecycle, parties/roles, items, awards, contracts, implementation and milestones;
- EU eForms/TED: explicit distinction between procurement procedure identity, notice identity/version and lot identity;
- UNCITRAL Model Law on Public Procurement: objective, transparent and competitive procurement with clear participation/qualification semantics;
- World Bank procurement framework: separation of procurement strategy/planning, procurement activity/control and contract management.

The ARGUS model is not an OCDS publication profile and does not copy those standards mechanically. It adopts the semantic distinctions that reduce ambiguity while retaining Bangladesh-specific identifiers, routes and source terminology.

## Core architectural changes

### 1. Institutions become references, not repeated strings

Ministry, division, department/directorate/authority/SOE/force, procuring entity and end user are canonical ENTITY records. A PROCUREMENT record links those entities through typed `party_role_links` such as `SPONSORING_MINISTRY`, `IMPLEMENTING_AGENCY`, `PROCURING_ENTITY`, `PROCUREMENT_AGENT`, `END_USER` and `FUNDER`.

Government hierarchy stays on ENTITY relationships. It is not copied into every procurement record.

### 2. External identifiers use one typed collection

System Tender/Proposal ID, PE Tender/Invitation Reference No., APP ID, package number, financing reference and other identifiers remain semantically distinct through `identifiers[]` with scheme/value/scope/source metadata.

Legacy generic `solicitation.id` is deprecated because its identifier type is ambiguous.

### 3. Category, method, competition scope and process configuration are independent

- `process.category`: Goods / Works / Consulting Services / Non-Consulting Services.
- `process.method`: internationally normalized Open / Selective / Limited / Direct / Other, while source code/label such as OTM/LTM/RFQ/DPM is retained.
- `process.competition_scope`: National / International / Restricted by Financing / Other. Bangladesh NCT/ICT maps here, not into method.
- `process.configuration`: One-stage one-envelope, one-stage two-envelope, two-stage etc.

This prevents OTM, ICT and One Stage Two Envelope from being treated as competing values of the same field.

### 4. Notices, milestones and events are distinct

A notice is a publication about a procurement process. A milestone is a scheduled/actual lifecycle point. An event records something that happened or changed.

Examples:

- tender notice -> `notices[]`;
- submission deadline -> `milestones[]`;
- corrigendum -> `events[]` plus its notice;
- deadline extension -> event changing a milestone;
- re-tender -> new PROCUREMENT cycle linked to predecessor plus `RETENDER` event.

Original/current closing/opening/validity dates no longer require duplicate authoritative scalar fields. Milestone history plus events preserves both values.

### 5. Derived counters are not authoritative stored facts

`extension_count`, `validity_extension_count` and `variation_count` are derived from canonical arrays. They can be cached for performance later, but the underlying events/modifications remain the authority.

### 6. Qualification and participation conditions use typed requirements

Registration, DGDP enlistment, experience, financial capacity, technical capability, OEM authorization, source-country eligibility, local participation/JV, standards, sustainability and security-clearance conditions all use `requirements[]` with a semantic `type`, source-grounded text and optional normalized value.

This replaces overlapping eligibility/registration/experience/technical/standards scalar fields.

### 7. Fees and securities are repeatable typed obligations

Document price and schedule purchase charges use `fees[]`. Tender security, performance security and other guarantees use `securities[]`. This supports multi-lot and multi-currency cases without creating portal-specific scalar fields.

### 8. Award is not contract

An award represents the decision linking suppliers/items/lots/value. A contract represents the signed legal agreement. Official contract number and signing date therefore belong to the contract object, not award.

### 9. Project, policy, installed base and supplier intelligence are linked

Project attributes stay on PROJECT records. Policy/context stays in linked KNOWLEDGE/INTELLIGENCE records. Supplier identity/product data stays on ENTITY/SUPPLIER_PRODUCT. Installed-base evidence remains linked intelligence. The procurement references these records instead of duplicating their fields.

### 10. Evidence is field-level

Each material canonical value can be supported by `observations[]` containing canonical field path, normalized value, raw source label/value, source system/id/locator, observation/publication time, ARGUS claim type/condition and ATLAS assurance when applicable.

## Migration controls

`profiles/bangladesh-procurement-v1-to-v2-migration.yaml` accounts for every canonical v1.0.1/v1.1/v1.2/v1.3 field using only:

- `KEEP`
- `RENAME`
- `MERGE`
- `DERIVE`
- `DEPRECATE`

Ambiguous v1 fields are not automatically coerced. Examples:

- `solicitation.id` -> DEPRECATE until identifier semantics are known;
- `procurement.financial_year` -> DEPRECATE until the source makes clear whether it means APP/plan/budget fiscal year;
- `procurement.actual_amount` -> DEPRECATE until resolved as award value, contract value or another amount;
- `procurement.actual_currency` follows the resolved monetary concept.

## Deployment sequence

1. Define v2 candidate and exhaustive migration map. **Completed.**
2. Validate all current contract tests with v1.3 still active. **Completed.**
3. Build representative v1 -> v2 transformed fixtures for e-GP, DGDP, BCG CPV and development-partner procurement.
4. Compare semantic equivalence and information loss.
5. Define v2 JSON Schema/registry write contract if required.
6. Obtain governed approval for live canonical migration.
7. Migrate current records with readback verification.
8. Change active manifest authority from v1.3 to v2 only after migration passes.

## Non-goals in this candidate

- no live PROCUREMENT record is rewritten;
- no new Master Registry record type is introduced;
- ATLAS taxonomy ownership is unchanged;
- no raw tender/source documents are committed to GitHub;
- no operational database deployment is introduced.
