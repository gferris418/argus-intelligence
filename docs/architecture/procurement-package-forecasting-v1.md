# Procurement Package Forecasting v1

**Status:** Candidate  
**Owner:** ARGUS domain intelligence, governed by ATLAS  
**Method:** `profiles/procurement-package-forecasting-v1.0.yaml`  
**Schema:** `schemas/procurement-package-forecast.schema.json`

## Purpose

ARGUS must not wait for a tender or procurement plan to reveal the commercial shape of an already evidenced government project. The missing capability is the systematic ability to decompose a real project or requirement into a bounded set of probable future procurement-package hypotheses, then monitor for the authoritative evidence that confirms, changes, combines, splits or disproves those hypotheses.

This capability answers a narrower question than general forecasting:

> Given an evidenced project or requirement, what procurement packages are plausibly likely to appear, in what sequence and approximate period, under which procurement routes, and what evidence would confirm or falsify each hypothesis?

## Control boundary

ATLAS remains the only control plane and retains final forecasting/scenario authority. ARGUS owns evidence-bounded package-hypothesis generation inside an authorized collection mission.

```text
ATLAS authorized intelligence mission
              |
              v
ARGUS establishes project / requirement baseline
              |
              v
ARGUS decomposes scope and delivery structure
              |
              v
ARGUS generates package hypotheses
              |
              v
ARGUS corroborates, falsifies and scores
              |
              v
ARGUS returns evidence-bounded forecast payload
              |
              v
ATLAS verifies / compares / decides next action
```

A probability is never evidence that a package exists. `PACKAGE_IDENTIFIED` remains an evidence-backed procurement state, not a forecast state.

## Canonical identity rule

Forecast hypotheses do **not** receive canonical `PROCUREMENT_PACKAGE` identity merely because they are plausible. They remain derived intelligence.

When authoritative or otherwise competent evidence reveals a real package:

1. reconcile the observed package against existing hypotheses;
2. create or update the canonical `PROCUREMENT_PACKAGE` object using the existing PKG identity standard;
3. link it to the underlying project and `requirement_ref`;
4. mark the matching forecast hypothesis `REALIZED` and record the observed package reference;
5. retain unmatched hypotheses for weakening, rejection, supersession or continued monitoring.

This prevents forecast artifacts from contaminating canonical procurement truth.

## Decomposition method

ARGUS evaluates materially relevant lenses rather than mechanically splitting the project by headings. Important lenses include:

- physical and technical outputs;
- project components and subcomponents;
- financing and expenditure categories;
- works / goods / consulting / non-consulting separation;
- implementation sequencing and dependencies;
- local versus imported/OEM delivery split;
- interoperability and integration constraints;
- procurement thresholds and approval structure;
- buyer packaging history and comparable prior projects;
- development-partner procurement rules;
- market structure and supplier concentration;
- installed-base compatibility;
- sites, geography and lots;
- training, spares, software, support and lifecycle services.

The objective is the **smallest materially distinct hypothesis set supported by evidence**, not the largest list ARGUS can imagine.

## Evidence and verification

Every material package hypothesis must preserve:

- supporting evidence references;
- contradicting evidence references;
- assumptions;
- at least one falsifier;
- monitoring signposts;
- realization probability;
- evidence confidence;
- timing precision appropriate to the evidence;
- procurement-route hypotheses where useful.

Material claims should prefer primary sources and independent source lineages. Historical analogues and institutional patterns may increase plausibility but never prove the future package structure.

## Probability separation

ARGUS keeps these concepts separate:

- **Evidence confidence** — how strongly the evidence supports the reasoning.
- **Package realization probability** — how likely a materially similar package is to enter procurement.
- **Opportunity qualification / commercial priority** — separate Access Asia business assessment.
- **Supplier match confidence** — separate fit assessment.

None may be substituted for another.

## Timing discipline

Forecast timing may use:

- exact/date range only when supported;
- month range;
- quarter range;
- fiscal year;
- relative sequence;
- unknown.

ARGUS must not invent an exact tender date merely because a project implementation period is known.

## Monitoring and early warning

Typical signposts include:

- APP or project procurement-plan publication;
- DPP/RDPP or project-document revision;
- World Bank/ADB/development-partner procurement-plan updates;
- ADP/RADP or budget allocation changes;
- consultant/PMC/design appointments;
- RFI, EOI, PQ or market-sounding activity;
- specification/BOQ preparation evidence;
- package number or lot reference appearing in a portal or project document;
- tender publication.

Each material trigger causes reacquisition of primary evidence, reconciliation against the forecast set and an updated return to ATLAS when the change affects a decision.

## Relationship to the ARGUS-native skill architecture

This capability becomes the bridge between horizon/project intelligence and tender intake:

```text
Horizon / policy / budget intelligence
              |
              v
Opportunity and project discovery
              |
              v
PROJECT / REQUIREMENT EVIDENCED
              |
              v
PROCUREMENT PACKAGE FORECASTING   <-- this capability
              |
              +------ monitor signposts ------+
              |                               |
              v                               v
Observed procurement plan/package       Tender published directly
              |                               |
              v                               v
Canonical procurement reconciliation   Tender intake / extraction
```

The wider ARGUS-native capability stack should remain bounded:

1. horizon intelligence;
2. opportunity discovery;
3. tender intake;
4. entity resolution;
5. supplier intelligence;
6. source verification;
7. market landscape;
8. network intelligence;
9. intelligence briefing.

Proposal/RFP response execution remains downstream of the pursuit/PX boundary and is not part of early ARGUS discovery.
