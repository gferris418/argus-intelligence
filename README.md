# ARGUS Intelligence

ARGUS is the **ATLAS-governed intelligence collection subsystem**. It performs structured target and procurement collection when ATLAS determines that ordinary direct research is insufficient. ATLAS OS remains the fixed operating architecture and owns Mission Control, the Control Plane, planning, permissions, approvals, canonical taxonomy, substantive analysis and decisions, assurance, persistence authorization, observability, the Dashboard and final delivery.

**Current candidate:** `2.2.0-rc.1`

## Activation boundary

ATLAS separates task intent from collection mode. ARGUS activates only for collection modes `ARGUS_COLLECTION` or `HYBRID` and the semantic capability `intelligence_collection`.

```text
USER / EVENT
  -> ATLAS Mission Control + Control Plane
  -> Intent and target interpretation
  -> Collection-Need Gate
       -> NONE             -> ATLAS
       -> ATLAS_DIRECT     -> ATLAS direct retrieval/research
       -> ARGUS_COLLECTION -> ARGUS bounded collection mission
       -> HYBRID           -> ARGUS collection + ATLAS analysis/decision
  -> ATLAS assurance / delivery
```

A government, company or policy keyword does not self-activate ARGUS. ATLAS interprets whether the request creates a structured collection mission. Policy/regulatory explanation normally stays in ATLAS; a named strategic commercial target, buyer-product target, procurement plan/pipeline, installed-base question, supplier/competitor landscape or monitoring target normally creates ARGUS collection need.

Representative behavior:

- `Bangladesh Bank foreign exchange policy` -> ATLAS direct.
- `ST Engineering` -> ARGUS target collection.
- `coastal patrol vessel for Bangladesh Coast Guard` -> ARGUS buyer/product collection.
- `seed cum cleaner for BADC` -> ARGUS buyer/product/procurement collection.
- `share the annual procurement plan of Bangladesh Navy` -> ARGUS procurement-plan collection.
- `compare ST Engineering and L3Harris for Bangladesh opportunities` -> HYBRID: ARGUS collects; ATLAS compares and decides.

## ARGUS processing

`Contextualize -> Resolve Targets -> Plan Collection -> Discover -> Acquire -> Extract -> Normalize -> Resolve Entities -> Deduplicate -> Classify -> Corroborate -> Detect Conflicts -> Assess Coverage -> Package -> Learn`

ARGUS returns an `IntelligenceCollectionPackage`; it does not own the final business judgment.

## Public-sector opportunity specialization

Bangladesh/public-sector opportunity intelligence remains a first-class collection specialization. The mature source mappings, 360-degree collection lenses, institutional graph, procurement lineage and I0-I9 maturity model remain available for that specialization. `PROMOTE_TO_PX`, bid/no-bid and other pursuit decisions are not universal ARGUS semantics; ATLAS and the Access Asia business-policy overlay own the decision and governed action.

## Machine-readable authority

- Manifest: `argus-intelligence.yaml`
- Core collection contract: `spec/general-intelligence.yaml`
- ATLAS alignment: `alignments/atlas-os-triage-v2.yaml`
- Activation contract: `contracts/atlas/argus-activation-v1.json`
- Collection mission: `schemas/collection-mission.schema.json`
- Collection package: `schemas/intelligence-collection-package.schema.json`
- Historical/specialization domain result: `schemas/domain-result.schema.json`
- Public-sector specialization: `spec/core.md`
- Bangladesh profile: `profiles/bangladesh.md`
- Architecture boundary: `docs/architecture/atlas-argus-collection-boundary.md`

The existing synchronization runtime and signed ATLAS domain-context handoff remain valid interoperability seams. They do not transfer ATLAS governance ownership to ARGUS.
