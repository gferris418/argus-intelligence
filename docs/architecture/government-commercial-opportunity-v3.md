# ARGUS v3 — Government Commercial Opportunity Intelligence

## Mission

ARGUS is Access Asia's ATLAS-governed government commercial opportunity intelligence system. Its purpose is to detect government needs, programmes, projects, funding paths, approvals and procurements as early as legitimately observable; develop credible commercial opportunity hypotheses before procurement exists; track them through delivery and expansion; identify international OEMs/suppliers/contractors/technologies capable of meeting the need; match demand and supply; and return evidence-backed commercial intelligence to ATLAS.

Tender intelligence is a subsystem, not the product definition.

## Architecture

```text
                         ATLAS OS
             Mission Control + Control Plane
                          |
                  Collection-Need Gate
                          |
                          v
+---------------------------------------------------------------+
|                           ARGUS                               |
|        Government Commercial Opportunity Intelligence         |
|                                                               |
|  +---------------------+       +---------------------------+   |
|  | Demand Intelligence |       | Supply Intelligence       |   |
|  | need / policy       |       | OEM / supplier           |   |
|  | programme / project |       | technology / capability  |   |
|  | budget / approval   |       | references / export      |   |
|  | procurement / base  |       | partnerability           |   |
|  +----------+----------+       +-------------+-------------+   |
|             |                                |                 |
|             +----------------+---------------+                 |
|                              v                                 |
|                    Opportunity Engine                          |
|                     S0 -> S9 lifecycle                         |
|                              |                                 |
|          SHAPE / POSITION / REACT / EXPAND                    |
|                              |                                 |
|                              v                                 |
|              Matching & Qualification Engine                  |
|                              |                                 |
|                              v                                 |
|                    Early-Warning Engine                        |
|               events / watchlists / triggers                  |
+-----------------------------+---------------------------------+
                              |
                              v
               Intelligence Collection Package
                              |
                              v
                           ATLAS
           evidence acceptance / final analysis /
       authoritative priority / pursuit authorization
                              |
                              v
                 Access Asia commercial pipeline
```

## Lifecycle

| Stage | Government state | ARGUS objective |
| --- | --- | --- |
| S0 | Need / Gap | Detect the unmet need or capability gap |
| S1 | Concept | Identify emerging solution/project concepts |
| S2 | Planning | Determine probable project shape |
| S3 | Budget Formation | Establish seriousness and funding path |
| S4 | Approval | Detect competent-authority approval |
| S5 | Procurement Planning | Resolve acquisition/package/specification path |
| S6 | Pre-Tender | Position suitable OEMs and Access Asia |
| S7 | Tender Published | Rapidly qualify participation and mobilize suppliers |
| S8 | Evaluation / Award | Track outcome and competitive intelligence |
| S9 | Delivery / Expansion | Detect variations, follow-on, maintenance, upgrades and adjacent needs |

Lifecycle stage is not probability, confidence or commercial mode.

## Commercial modes

- **SHAPE** — develop an opportunity from an observable need before procurement is defined.
- **POSITION** — prepare the correct OEM/supplier and Access Asia strategy before tender.
- **REACT** — recover quickly when formal procurement is already live.
- **EXPAND** — develop follow-on, upgrade, maintenance, spares, training, replacement or adjacent opportunities.

## Opportunity identity

A credible commercial possibility may receive a persistent ARGUS identity before a PX exists:

`ARGUS-OPP-YYYY-NNNNNN`

ATLAS promotion later assigns:

`YYYY_PXNNNNN_SHORTNAME`

Both identify the same underlying commercial opportunity. The ARGUS identity is permanent intelligence lineage; the PX identity is the governed Access Asia commercial/project lineage.

## Demand and supply matching

ARGUS supports both demand-first and supply-first discovery.

```text
Government need -> capability -> solution -> supplier universe -> partnerability -> shortlist
```

```text
OEM/technology -> capability -> Bangladesh applicability -> government users -> unmet need -> opportunity hypothesis
```

Technical capability alone is insufficient. Supplier matching also evaluates exportability, references, Bangladesh fit, local support, channel conflicts, willingness to partner and Access Asia relationship/access.

## Qualification and authority

ARGUS calculates advisory opportunity qualification and supplier-match scores. ATLAS owns authoritative priority and pursuit decisions.

Default opportunity qualification dimensions:

| Dimension | Weight |
| --- | ---: |
| Strategic fit | 20% |
| Commercial attractiveness | 20% |
| Procurement probability | 20% |
| Supplier availability | 15% |
| Access advantage | 15% |
| Competitive difficulty | 10% |

Recommended bands are PRIORITY (80–100), ACTIVE (65–79.99), WATCH (50–64.99) and MONITOR (<50).

## Distinct measures

ARGUS keeps separate:

1. evidence confidence;
2. procurement realization probability;
3. Access Asia success probability;
4. supplier-match confidence.

None is a substitute for another.

## Early warning

Material events update the same opportunity rather than producing disconnected reports. Examples include policy signals, feasibility studies, project proposals, DPP/TAPP preparation, budget allocation, financing agreements, approval, APP inclusion, specification activity, market consultation, RFI/EOI/PQ, tender publication, amendments, cancellation/rebid, award, delivery and follow-on expansion.

Detection lag is measured from the earliest known public observability of a material signal to ARGUS's first detection.

## Rapid Tender Mode

When first material discovery occurs at S7, or closing time is critically short, ARGUS prioritizes eligibility and disqualifiers before historical depth. The first pass extracts buyer, tender ID, deadline, procurement method, eligibility, experience/financial/technical requirements, OEM/country/JV/local-agent restrictions, bid/performance securities, delivery/Incoterms and evaluation methodology, then builds and filters the supplier universe.

## Procurement-integrity boundary

Permitted activity includes technical education, demonstrations, concept notes, legitimate market engagement, transparent pre-procurement discussions, industry consultation and solution discovery.

Prohibited activity includes bribery/inducements, collusion, improper procurement influence, unlawful specification manipulation, confidential bid-information acquisition, procurement-evaluation interference and misrepresentation of government support.

## Authority boundary

**ARGUS calculates and recommends. ATLAS authorizes and decides.**

ARGUS owns opportunity detection, early identity, lifecycle tracking, supplier intelligence, partnerability, supplier matching, advisory qualification and event monitoring. ATLAS owns canonical evidence acceptance, authoritative priority, PX promotion, pursuit/bid decisions, external-action authorization, persistence and final delivery.
