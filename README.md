# ARGUS Intelligence

ARGUS is the **ATLAS-governed government commercial opportunity intelligence system** for Access Asia. It is designed to identify government needs, programmes, projects, budgets, approvals and procurements as early as legitimately observable; develop credible commercial opportunity hypotheses before a formal project or tender exists; track them through the full public-sector lifecycle; and simultaneously identify international OEMs, suppliers, solution providers and contractors capable of meeting the requirement.

**Current candidate:** `3.0.0-rc.2`

Tender intelligence is one subsystem. The target condition is that by tender publication ARGUS should already understand the underlying need, buyer, institutional path, project/funding status, likely procurement route, competitor context, supplier universe, preferred OEM candidates, Access Asia positioning strategy and unresolved intelligence requirements. If it does not, ARGUS enters Rapid Tender Mode.

## ATLAS governance boundary

ATLAS OS remains the fixed operating architecture. It owns Mission Control, the Control Plane, task interpretation, collection-need routing, permissions, approvals, canonical taxonomy, canonical evidence acceptance, authoritative commercial priority, pursuit decisions, bid/no-bid, persistence authorization, observability, the Dashboard and final delivery.

ARGUS activates only for collection modes `ARGUS_COLLECTION` or `HYBRID` and semantic capability `intelligence_collection`.

```text
USER / EVENT
  -> ATLAS Mission Control + Control Plane
  -> Intent + target interpretation
  -> Collection-Need Gate
       -> NONE             -> ATLAS
       -> ATLAS_DIRECT     -> ATLAS direct retrieval/research
       -> ARGUS_COLLECTION -> ARGUS bounded intelligence mission
       -> HYBRID           -> ARGUS intelligence + ATLAS analysis/decision
  -> ATLAS Evidence Governance / assurance / authorized action / delivery
```

ARGUS may compute supplier matches, opportunity qualification and priority recommendations. Those outputs are advisory domain intelligence; ATLAS owns authoritative pipeline state and commercial decisions.

## Five persistent ARGUS engines

1. **Demand Intelligence** — policy, needs, capability gaps, programmes, projects, budgets, funding, approvals, procurement and installed base.
2. **Supply Intelligence** — OEMs, suppliers, contractors, technologies, products, capabilities, references, exportability and partnerability.
3. **Opportunity Engine** — persistent commercial opportunity identity and S0–S9 lifecycle reconciliation.
4. **Matching & Qualification** — demand-to-supplier matching, configurable scoring and recommended priority.
5. **Early Warning** — event-driven monitoring, watchlists, trigger detection and Rapid Tender Mode.

## Opportunity lifecycle

ARGUS uses S0–S9 as the primary government-opportunity lifecycle:

`S0 Need/Gap -> S1 Concept -> S2 Planning -> S3 Budget Formation -> S4 Approval -> S5 Procurement Planning -> S6 Pre-Tender -> S7 Tender Published -> S8 Evaluation/Award -> S9 Delivery/Expansion`

Opportunity mode is a separate dimension:

- `SHAPE` — develop a legitimate opportunity from an observable government need before procurement is defined.
- `POSITION` — secure the correct OEM/supplier strategy before tender publication.
- `REACT` — recover rapidly when a tender is already live.
- `EXPAND` — detect follow-on, maintenance, upgrade, spares, training, replacement and adjacent opportunities.

Legacy I0–I9 maturity remains compatibility-only for older public-sector records; it is no longer the primary lifecycle model.

## Opportunity identity

A credible commercial possibility that requires persistent tracking may receive an ARGUS identity before any Access Asia PX exists:

`ARGUS-OPP-YYYY-NNNNNN`

When ATLAS authorizes commercial pipeline promotion, the same opportunity receives the Access Asia commercial identity:

`YYYY_PXNNNNN_SHORTNAME`

The ARGUS identity remains permanent and the PX identity follows the governed Access Asia lineage into `REV/OPP` and, after award/contract activation, `OPS/PRJ`.

A tender does not automatically create a new opportunity. One opportunity may legitimately link to multiple procurement packages, tenders, amendments, rebids or follow-on procurements.

## Bidirectional discovery

ARGUS works in both directions:

`Government need -> capability/solution -> supplier universe -> Access Asia opportunity`

and

`OEM/technology -> capability -> Bangladesh applicability -> government users -> unmet need -> opportunity hypothesis`

This supports both discovery of emerging government requirements and legitimate market-development opportunities where Access Asia can introduce an internationally proven solution.

## Supplier partnerability

Technical fit is not enough. ARGUS separately assesses whether a supplier can legitimately and commercially partner with Access Asia, including existing Bangladesh representation, exclusivity, channel model, direct-sales preference, local-support requirements, willingness to partner, relationship status and conflicts.

## Distinct measures

ARGUS must never collapse these into one confidence score:

- evidence confidence;
- procurement realization probability;
- Access Asia success probability;
- supplier-match confidence.

It also records detection lag:

`first_detected_at - earliest_known_publicly_observable_at`

so early-warning performance can be calibrated over time.

## Rapid Tender Mode

When ARGUS first materially discovers an opportunity at S7 or with a critically short closing horizon, the first pass prioritizes closing date, procurement method, eligibility, experience/financial/technical requirements, OEM/country/JV/local-agent restrictions, securities/guarantees, delivery/Incoterms, evaluation method and critical disqualifiers. It then builds and filters the supplier universe and returns the top actionable candidates.

## Collection method

ARGUS still uses professional collection tradecraft inside the ATLAS-authorized mission:

`PIR -> EEI -> Collection Plan -> Source Plan -> Collect -> Resolve -> Grade -> Competing Hypotheses -> Gaps -> Package`

The expanded runtime additionally develops opportunity context, builds supplier universes, assesses partnerability, matches demand and supply and calculates advisory qualification before packaging evidence for ATLAS.

## Machine-readable authority

- Manifest: `argus-intelligence.yaml`
- Core: `spec/general-intelligence.yaml`
- Commercial opportunity doctrine: `spec/commercial-opportunity-intelligence.yaml`
- Collection method: `spec/collection-method.yaml`
- Collection mission: `schemas/collection-mission.schema.json`
- Collection package: `schemas/intelligence-collection-package.schema.json`
- Opportunity: `schemas/opportunity.schema.json`
- Opportunity event: `schemas/opportunity-event.schema.json`
- Supplier intelligence: `schemas/supplier-intelligence.schema.json`
- Opportunity-supplier match: `schemas/opportunity-supplier-match.schema.json`
- Access Asia lifecycle: `profiles/access-asia-opportunity-lifecycle.yaml`
- ATLAS activation contract: `contracts/atlas/argus-activation-v1.json`

The activation contract remains unchanged: ARGUS is still subordinate to the ATLAS Collection-Need Gate and does not create a second operating architecture.
