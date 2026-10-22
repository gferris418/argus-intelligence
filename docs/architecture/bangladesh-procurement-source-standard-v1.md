# Bangladesh Procurement Source Standard v1.0

**Status:** Candidate  
**Machine authority:** `profiles/bangladesh-procurement-source-standard-v1.0.yaml`  
**Purpose:** Tell ARGUS what each Bangladesh procurement-related source can normally reveal, when to use it, and what not to assume.

## Core distinction

ARGUS must distinguish:

- procurement policy / oversight authority;
- transaction and publication platform;
- specialist procurement authority;
- project planning / approval source;
- implementation-monitoring source;
- funding / development-partner source;
- high-level approval source;
- budget / financial-control source;
- PPP pipeline / transaction source;
- procuring-entity native source;
- development-partner procurement source;
- legal / gazette source.

**Authority ≠ platform ≠ approval body ≠ project system ≠ funding system ≠ procuring entity.**

## Main Bangladesh source families

| Source family | Primary role | Typical information |
|---|---|---|
| BPPA | Procurement policy and oversight | law, rules, guidance, standard documents, circulars, oversight, debarment/review context |
| e-GP | National procurement transaction/publication platform | APP, package, tender, amendment, award and some contract/implementation information |
| DGDP / e-DP | Specialist defence procurement | defence tenders, enlistment, amendments, evaluation/re-evaluation/standardization and related notices when published |
| Planning Commission / ADP-RADP | Project planning and approval | projects, implementing agency, cost, funding mix, allocation, implementation period, approval/processing signals |
| ECNEC / NEC | High-level project approval signal | approval/revision summaries and project-level decision signals when published |
| IMED / e-PMIS | Implementation monitoring | implementation, monitoring, delay, completion and follow-on signals |
| ERD / AIMS | External financing / development-partner information | partner, project, agreement, commitment, disbursement, executing agency, implementation status |
| Cabinet / CCGP / CCEA | High-level purchase/economic approval | committee approval signals and special/high-value route context when public |
| Finance / public budget sources | Funding and financial-control context | national/ministry budget, allocation and public funding signals |
| PPP Authority | PPP pipeline and transactions | PPP project profiles, status, contracting authority, EOI/IFB/prequalification and updates |
| Procuring entity native sources | Requirement owner / implementing entity | plans, project notices, studies, procurement notices, specifications and implementation updates |
| Development partner portals | Partner-financed procurement | procurement plans, consulting/PQ notices, bid notices, awards and project documents |
| Gazette / official legal publications | Legal authority | laws, rules, amendments, notifications and effective dates |

## Search rule

ARGUS does **not** start with “search every portal.”

It asks:

```text
What information are we trying to establish?
        ↓
Which source family should normally contain it?
        ↓
Search that source first
        ↓
Preserve raw IDs and terminology
        ↓
Normalize
        ↓
Cross-check upstream / downstream / adjacent sources
        ↓
Reconcile
        ↓
Unsupported fields remain UNKNOWN
```

## Stage-aware use

```text
Need / policy signal
  → end-user / agency / ministry / gazette / project-pipeline sources

Concept / proposal
  → procuring entity / Planning Commission / ERD / PPP / DGDP pre-procurement / development partner

Project approval
  → Planning Commission / ECNEC-NEC / implementing entity / ERD / Cabinet signals

Funding
  → ADP-RADP / Finance / ERD-AIMS / development partner / entity budget

Procurement planning
  → e-GP APP / entity procurement plan / DGDP-eDP / donor plan / PPP transaction preparation

Pre-procurement
  → evaluation / standardization / EOI / PQ / consultant / pre-bid / market-engagement signals

Tender
  → e-GP / DGDP-eDP / PPP / entity / development-partner portal as applicable

Award
  → e-GP / DGDP / entity / development partner / high-level approval source where relevant

Implementation
  → IMED-ePMIS / entity / e-GP contract-management signals / ERD / development partner

Completion / follow-on
  → IMED / entity annual reports / installed-base / successor procurement
```

## Route-aware defaults

```text
General public procurement
  → e-GP + BPPA + procuring entity

GoB development project
  → Planning/ADP + procuring entity + e-GP

Development-partner financed
  → ERD/AIMS + partner portal + Planning/ADP + implementing entity

Defence
  → DGDP/e-DP + relevant defence entity sources
  → e-GP only where applicable and evidenced

PPP
  → PPP Authority + contracting authority

SOE / autonomous authority
  → entity-native source + applicable e-GP / budget / project sources

G2G / strategic
  → entity + Cabinet/approval + legal/budget/financing sources as applicable
```

## Access classification

Every source observation should record one of:

- `PUBLIC_STRUCTURED`
- `PUBLIC_DOCUMENT`
- `PUBLIC_SUMMARY`
- `LOGIN_REQUIRED`
- `RESTRICTED`
- `NOT_PUBLISHED`
- `UNKNOWN`

`Not found publicly` must never be treated as equivalent to `does not exist`.

## Normalized procurement-intelligence record

ARGUS should normalize source observations into the existing Bangladesh procurement vocabulary across these groups:

- source and provenance;
- procurement regime / route;
- organizations and institutional roles;
- project and funding;
- procurement plan and package;
- solicitation;
- requirement;
- award;
- execution;
- intelligence state, confidence, contradictions and unknowns.

The full field list is machine-readable in `profiles/bangladesh-procurement-source-standard-v1.0.yaml`.

## Relationship to existing standards

This standard complements, and does not replace:

- `profiles/bangladesh-canonical-procurement-standard-v1.3.yaml`
- `profiles/bangladesh-source-mappings-v1.3.yaml`
- `profiles/bangladesh-institution-standard.yaml`
- `profiles/bangladesh.md`

The canonical procurement standard defines normalized procurement concepts. The source mappings define source-label normalization. **This source standard defines where ARGUS should look and what information each source family can reasonably be expected to contain.**

## Runtime rule

The registry is a collection guide, not a timeless factual database. Current legal rules, platform availability, public-access scope, procurement channels and source fields must be revalidated when materially relied upon.
