# ARGUS 360° Intelligence Collection — Architecture Validation

**Version:** 1.0.0  
**ARGUS candidate:** 2.0.0-rc.2  
**ATLAS baseline:** 2.0.0-rc.7  
**Status:** Candidate validation

## Decision

360° intelligence collection belongs in ARGUS Core as a **collection doctrine and coverage model**, not as a new record type, a new execution spine, or a replacement for the Research Frontier.

Governing principle:

> **360° breadth, decision-driven depth.**

## Why Core owns the doctrine

The need to examine an opportunity across mission, institutional, project, funding, procurement, technical, competitive, ecosystem, commercial, timing and internal-intelligence dimensions is jurisdiction-independent.

Country profiles specialize where and how those dimensions are collected.

Therefore:

`ARGUS Core defines WHAT to examine → Country Profile defines WHERE/HOW → Research Frontier decides WHAT NEXT → ATLAS governs execution`

## Twelve collection lenses

1. `need_mission`
2. `policy_strategy`
3. `institution_stakeholders`
4. `programme_project`
5. `budget_funding`
6. `procurement_acquisition`
7. `technical_installed_base`
8. `supplier_competitor`
9. `ecosystem_influence`
10. `commercial_participation`
11. `timing_triggers`
12. `internal_intelligence`

## Coverage states

- `NOT_APPLICABLE`
- `UNASSESSED`
- `INSUFFICIENT`
- `PARTIAL`
- `ADEQUATE`

Coverage is decision-relative and separate from claim type, claim condition, ATLAS evidence assurance and I0–I9 maturity.

## Source convergence

ARGUS distinguishes source count from independent source lineages.

Derivative copies of one source do not add independent confirmation.

Independent convergence is preferred for material claims when proportionate, but a uniquely authoritative primary source may be sufficient for the claim it is competent to establish.

## Research Frontier relationship

The coverage matrix exposes gaps. The Research Frontier ranks the gaps by expected decision value.

It does not attempt to close every gap.

`360° coverage assessment → material gaps → Research Frontier → ATLAS plan/work unit → collection → reassessment`

## ATLAS boundary

No ATLAS OS change is required.

ATLAS continues to own planning, routing, authorization, evidence assurance, verification, persistence and delivery.

ARGUS owns collection lenses, coverage semantics, collection-gap interpretation and domain decisions.

## Registry boundary

No eighth `COLLECTION` record type is created.

Coverage is assessment metadata attached to a domain result or the relevant ARGUS record context. Existing canonical source ownership remains unchanged.

## Bangladesh validation

The Bangladesh profile maps each Core lens to Bangladesh-relevant institutional and source surfaces, including general e-GP, development projects, development-partner routes, DGDP/e-DP defence procurement, SOE/autonomous entities, PPP, G2G/strategic routes and internal Access Asia evidence.

The defence mapping explicitly prohibits seeking sensitive operational detail merely to fill a lens.

## Coastal surveillance radar test

For a seed such as `Coastal Surveillance Radar — Bangladesh Navy`:

- the seed normally begins as an `INTELLIGENCE` candidate at I0;
- `BD-DEF-DGDP` is a route hypothesis, not a conclusion;
- first material lenses include mission/need, institutions, procurement route, technical installed base, suppliers/competitors, commercial participation, timing/triggers and internal intelligence;
- funding/project/policy/ecosystem lenses are expanded when they can alter the decision;
- gaps feed the Research Frontier;
- broad coverage does not imply procurement probability;
- no PX is created directly from collection completeness.

## Acceptance criteria

The rc.2 change passes when:

1. Core declares the doctrine and all twelve lenses.
2. Manifest declares breadth, depth and coverage states.
3. Domain-result schema exposes optional `collection_coverage` and `collection_gaps`.
4. Bangladesh profile maps all twelve lenses.
5. No ATLAS contract is modified.
6. No new top-level ARGUS record type is created.
7. The contract test in `tests/test_360_collection_contract.py` passes.
