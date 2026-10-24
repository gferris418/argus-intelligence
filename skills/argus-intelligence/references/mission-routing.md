# ARGUS Mission Routing

Use this reference only after ATLAS has authorized an ARGUS `intelligence_collection` mission.

## Procedure

1. Preserve the ATLAS mission ID, exact objective, scope, constraints, exclusions, jurisdiction, time horizon, and known canonical object IDs.
2. Read `spec/mission-skill-routing.yaml` and classify the current mission state from competent evidence.
3. Set the orthogonal stale-revalidation flag when evidence is old, contradictory, deadline-sensitive, or current lifecycle is unresolved.
4. Build `mission_skill_plan` using `schemas/mission-skill-plan.schema.json`.
5. Mark each specialist `REQUIRED`, `CONDITIONAL`, or `SKIP`. Activate only work that can change a decision-relevant gap.
6. Preserve all canonical IDs across specialist transitions. Similar evidence is a reconciliation candidate, not permission to create a duplicate identity.
7. Collect through the Research Frontier until the stopping rule is satisfied or a material gap remains unresolved.
8. Reconcile specialist returns into one ARGUS collection package and return it to ATLAS. ATLAS remains next-step authority.

## Mission states

`SEED → NEED_OBSERVED → PROJECT_IDENTIFIED → PROCUREMENT_EXPECTED → PROCUREMENT_LIVE → PROCUREMENT_CLOSED → AWARD_OBSERVED → POST_AWARD`

`STALE_REVALIDATION_REQUIRED` is an orthogonal overlay, not another lifecycle stage.

A lifecycle promotion requires evidence competent to establish the new state. Secondary sources may trigger collection or revalidation but cannot by themselves promote canonical procurement lifecycle when a competent originating source is required.

## Procurement modes

- `DISCOVERY` — investigate procurement route, planning signals, applicable authority, likely method, and evidence gaps without asserting a live solicitation.
- `LIVE_PROCUREMENT` — prioritize current solicitation documents, amendments/corrigenda, eligibility, evaluation, timing, bidder constraints, supplier feasibility, and Access Asia positioning.
- `POST_DEADLINE_REVALIDATION` — establish whether the procurement closed, extended, cancelled, reissued, retendered, awarded, or remains unresolved; never infer the outcome from a passed date alone.

## Pilot invariants

- Coastal Patrol Vessel / Bangladesh Coast Guard: `PROCUREMENT_LIVE`, reuse resolved lineage, latest competent corrigendum controls current tender dates.
- Coastal Surveillance Radar / Bangladesh Navy: begin `SEED` unless stronger evidence exists; a procurement route is a hypothesis until verified.
- Seed Cleaner Cum Grader / BADC: retain historical need as provenance but require current authoritative evidence before assigning current procurement lifecycle.
