# DGDP Navy Wing NP-8 — Live Boat and SCUBA Tenders

**As of:** 2026-10-18  
**Source notice:** user-provided `tender_20261014114803.pdf`  
**Official corroboration:** DGDP Navy Wing tender listing (`https://www.dgdp.gov.bd/navy-wing`)

## Decision

The uploaded notice contains three separately numbered DGDP solicitations, not one multi-lot procurement. Each tender is therefore represented as a separate PROCUREMENT record while retaining a common institutional chain: Ministry of Defence → Directorate General Defence Purchase → Navy Wing / NP-8 → Bangladesh Navy end user.

## Canonical procurements

| ARGUS ID | DGDP Tender No. | Requirement | Qty | Schedule price | Current state |
|---|---|---|---:|---:|---|
| `PROC-DGDP-248-07-075-26` | `248.07.075.26` | Inflatable Boat (IB) Without Engines | 3 Nos | BDT 1,000 | OPEN / I9 |
| `PROC-DGDP-248-07-076-26` | `248.07.076.26` | Rigid Hull Inflatable Boat (RHIB) with Twin Engine | 3 Nos | BDT 5,000 | OPEN / I9 |
| `PROC-DGDP-248-07-078-26` | `248.07.078.26` | Twin Cylinder Open Circuit (SCUBA) Diving Set Complete | 50 Set | BDT 5,000 | OPEN / I9 |

## Shared current mechanics

- Bangladesh route: `BD-DEF-DGDP`
- Wing: Navy Wing
- Section: NP-8
- Tender type: Open
- selling from: 2026-10-15
- selling through: 2026-11-25
- submission deadline: 2026-11-26 12:00 Asia/Dhaka
- opening: 2026-11-26 12:05 Asia/Dhaka
- tender currency basis: Foreign currency
- eligible tenderer wording: bona fide Manufacturer/Dealer/Suppliers/Importers enlisted with DGDP
- detailed tender schedules are non-refundable purchases; official DGDP listing also exposes specification downloads for the three rows

## Identifier boundary

For these DGDP notices, the published Tender Number is stored as the solicitation reference. No e-GP-style Tender/Proposal system ID, APP ID, project code, package number or lot number is inferred because the source does not provide them.

## Institutional normalization

- `ENT-BD-MOD` — Ministry of Defence
- `ENT-BD-DGDP` — Directorate General Defence Purchase
- `ENT-BD-NAVY` — Bangladesh Navy, normalized as military end-user service

Official DGDP guidance states Navy Wing is the central procurement entity for Bangladesh Navy and procures operational requirements originating from Naval Headquarters.

## Technical and commercial boundary

The source notice does not provide the detailed technical schedules. The DGDP public listing shows specification downloads are available, but those files were not successfully retrieved/reviewed in this run. Therefore supplier discovery and compliance assessment remain blocked at `PENDING_TECHNICAL_SCHEDULE` rather than being populated from generic market knowledge.

## Research Frontier

Retrieve and review each DGDP technical schedule/specification, then independently run supplier discovery for:

1. Inflatable Boat without engines;
2. RHIB with twin engine; and
3. Twin-cylinder open-circuit SCUBA diving set.

The review should resolve dimensions/performance, materials, engine requirements where applicable, standards/classification, delivery, warranty/training/spares, security requirements, country-of-origin restrictions, and DGDP enlistment category before supplier shortlisting or compliance scoring.
