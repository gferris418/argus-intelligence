# Bangladesh Opportunity Intelligence v3

## Purpose

This document defines the Bangladesh semantic foundation for ARGUS without creating a parallel intelligence system. It specializes the existing ARGUS opportunity architecture while preserving ATLAS as the control, approval, verification and persistence authority.

## Primary lifecycle authority

**S0–S9 remains primary.**

`S0 Need/Gap → S1 Concept → S2 Planning → S3 Budget Formation → S4 Approval → S5 Procurement Planning → S6 Pre-Tender → S7 Tender Published → S8 Evaluation/Award → S9 Delivery/Expansion`

**I0–I9 remains compatibility-only.** It may be retained for historical interpretation and migration but is not the primary Bangladesh opportunity lifecycle and must not control lifecycle transitions.

Opportunity mode (`SHAPE`, `POSITION`, `REACT`, `EXPAND`) is independent from lifecycle stage. Project, funding, procurement, institutional resolution and commercial decision states are also independent axes; none replaces S0–S9.

## W-question contract

Every substantive Bangladesh semantic object should be understandable through the following documentation completeness lens:

- `who`: actors, owners, authorities, beneficiaries, influencers and counterparties;
- `what`: exact concept, object, action, state or event;
- `when`: effective dates, triggers, lifecycle position and entry/exit conditions;
- `where`: jurisdiction, institution, administrative level, source system and project/package scope;
- `why`: purpose and government/commercial significance;
- `which`: applicable route, alternative, method, subtype, authority or option;
- `how`: process, transitions, dependencies, reconciliation or calculation;
- `how_much_or_many`: amount, quantity, threshold, duration, count or scale when material;
- `evidence`: provenance, observation date, confidence and contradictions;
- `decision_impact`: what the evidence changes and the next commercially useful action.

When a dimension is genuinely irrelevant, use `NOT_APPLICABLE` rather than silently omitting it. This contract is a **documentation completeness lens**, not another state machine.

## Structural graphs

### INSTITUTION_GRAPH

Answers who governs, sponsors, approves, funds, implements, procures, evaluates, uses, regulates and monitors. Hierarchy alone never proves functional authority.

### OPPORTUNITY_GRAPH

Represents the persistent underlying government requirement and its lifecycle evidence: policy, project, budget, approval, procurement planning, package, tender, award, delivery, installed base, replacement and expansion.

### MARKET_GRAPH

Represents OEMs, suppliers, contractors, technologies, incumbents, competitors, consultants, integrators and legitimate local partners that may satisfy or influence the requirement.

These graphs are structural views of the same opportunity intelligence system, not separate canonical stores.

## Investigation traversal

Traversal directions are ways to investigate the graphs; they are **not lifecycle stages**:

- `TOP_DOWN` — policy/priority to institution to project to procurement;
- `BOTTOM_UP` — tender/award/package back to project, owner, need and policy;
- `UPSTREAM` — move toward requirement, policy, approval and funding origin;
- `DOWNSTREAM` — move toward procurement, award, delivery and installed base;
- `LATERAL_GOVERNMENT` — related institutions, programmes and authorities;
- `LATERAL_MARKET` — suppliers, competitors, partners and advisers;
- `HISTORICAL` — prior procurements, awards, installed base and precedent;
- `SUCCESSOR` — replacement, upgrade or follow-on lifecycle hypothesis;
- `ADJACENT` — related but distinct requirements or opportunities.

## Analytical capabilities

The following capabilities operate across graph and lifecycle evidence:

- `EVENT_RECONCILIATION` — reconcile new observations against existing entities, projects, procurements and requirements;
- `HYPOTHESIS_TESTING` — maintain competing explanations and disconfirming evidence;
- `INDICATORS_SIGNPOSTS` — detect evidence that may strengthen, weaken, accelerate or delay an opportunity hypothesis;
- `RESEARCH_FRONTIER` — rank unresolved questions by decision impact, uncertainty, urgency and information value.

Event detection may trigger reassessment but never forces a lifecycle transition without sufficient evidence.

## Persistent requirement lineage

`requirement_ref` remains the stable link to the underlying government need across procurement cycles.

A tender amendment, re-tender, project revision or repeated product family does not by itself create a new requirement or opportunity. A successor opportunity requires evidence of a genuinely distinct replacement, upgrade, expansion or new lifecycle.

## Authority path

For material Bangladesh opportunities, ARGUS should attempt to resolve, without guessing:

1. need owner;
2. sponsor;
3. project owner;
4. implementing agency;
5. funding authority;
6. approving authority;
7. procuring entity;
8. evaluation authority;
9. end user;
10. monitoring authority.

Each resolved role should preserve the party reference, evidence references, confidence, validity period and scope. Unknowns stay unknown and enter the Research Frontier.

## Continuous search learning

**Every search must leave ARGUS better informed than before, even when the search returns no useful result.**

Each bounded search attempt produces a `research_learning_record` that captures the research question, query and method, source family, results examined, information gain, source assessment, discoveries, unknowns, hypothesis movement, what worked, what failed, terminology learned and the recommended next search.

`UNKNOWN means a research task, not a stop condition.` When a material question is unanswered, ARGUS should place it on the Research Frontier, choose the highest-value lawful source or traversal path, search again, and record what the attempt taught the system.

ARGUS maintains distinct learning views:

- `EPISODIC_MEMORY` — what happened during a particular investigation;
- `SEMANTIC_MEMORY` — validated entities, relationships, events and domain knowledge;
- `STRATEGY_MEMORY` — which queries, source sequences and research techniques work for a problem class;
- `CALIBRATION_MEMORY` — how prior confidence, timing and hypotheses compare with later observed outcomes;
- `SOURCE_MEMORY` — how source families perform for different questions without confusing popularity with authority;
- `VOCABULARY_MEMORY` — aliases, abbreviations, translations, project terminology and effective query variants.

Learning is guarded. A single observation is only `OBSERVED`. Repetition may become a `REPEATED_PATTERN`. Only a repeated pattern that has been backtested may become a `VALIDATED_HEURISTIC`. Even then, the heuristic may optimize search strategy but does not prove a current-case fact, authority relationship, procurement route or lifecycle transition.

**Patterns guide investigation; evidence determines conclusions.** Historical performance may change where ARGUS searches first and how it allocates research effort, but current evidence remains required for current claims.

The continuous loop is:

`partial signal → existing memory → research questions → best search strategy → search → learning record → evidence reconciliation → Research Frontier → search again or assess → outcome calibration → improved future strategy`

ATLAS remains the persistence, evidence-acceptance, approval and final decision authority. Continuous learning does not expand mission scope, self-activate ARGUS or create a second canonical business store.

## Evidence and safety invariants

- ATLAS authority is unchanged.
- ARGUS remains the specialist intelligence subsystem.
- Procurement v2 remains authoritative for procurement lineage and `requirement_ref`.
- Access Asia lifecycle, `PROMOTE_TO_PX`, `SUBMISSION_ACTIVE`, HubSpot ownership and SharePoint ownership remain unchanged.
- Public Git stores canonical structured intelligence and references, not raw sensitive source documents or secrets.
- Contradictions are preserved, not overwritten.
- Institution hierarchy is never inferred as approval/procurement authority without evidence.
- No duplicate canonical business store is introduced.
- Legal baselines are dated operating references, not permanent runtime legal truth.
