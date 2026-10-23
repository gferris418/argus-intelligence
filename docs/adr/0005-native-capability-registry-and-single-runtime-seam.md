# ADR 0005: Native Capability Registry and Single Governed Runtime Seam

- **Status:** Accepted for Issue #76 design
- **Date:** 2026-10-23
- **Decision owners:** ATLAS governance / ARGUS intelligence architecture

## Context

ARGUS already has one governed runtime seam that accepts bounded analysis methods and returns correlated results to ATLAS. New native capabilities are required for source verification, horizon intelligence, tender intake, supplier intelligence, market/competitive/network intelligence, intelligence briefs, and procurement-package forecasting. Creating a separate runtime, agent, lifecycle, or control plane for each capability would duplicate governance and increase semantic drift.

PR #75 also demonstrated a visibility gap: procurement-package forecasting has a schema, method profile and collection-package field but is not registered as a first-class native capability in the root contract.

## Decision

1. ARGUS will maintain an explicit machine-readable **Native Capability Registry**.
2. Each capability entry will declare at minimum:
   - capability ID and version;
   - status;
   - owning ARGUS engine(s);
   - method/profile or handler;
   - input contract;
   - output contract;
   - minimum Evidence Verification depth;
   - provider boundary;
   - cross-cutting vs collection-mission role;
   - ATLAS authority boundary.
3. Registration does not imply a new collection type. Cross-cutting capabilities such as Source Verification and Horizon Intelligence remain cross-cutting; Tender Intake operates through the existing RAPID_TENDER mission path.
4. All Native Capabilities execute through the existing governed ARGUS runtime seam. No capability receives its own independent execution spine, approval plane or persistence authority.
5. An **Executable Capability** means a callable method/handler with machine-readable validation, semantic reconciliation, tests and governed return through the ATLAS seam.
6. Reasoning-heavy analytical generation may use bounded model/provider reasoning. Deterministic runtime code validates, reconciles and enforces invariants rather than pretending arbitrary intelligence reasoning can be produced by static rules alone.
7. `argus-intelligence-brief` is a derived output projection, not a canonical record type.
8. Issue #76 is delivered through dependency-ordered incremental PRs rather than one monolithic change.

## Consequences

- Capabilities become discoverable and governable without expanding the number of runtimes.
- Cross-cutting methods do not pollute the collection-type taxonomy.
- All consequential outputs retain the existing ATLAS return, approval and persistence boundaries.
- Tests can assert that every registered capability has complete contracts and valid ownership metadata.
- Capability evolution can be versioned independently while preserving one execution architecture.

## Implementation sequence

1. Foundation repair: PR #75 wiring, capability registry, ownership terminology, verification schema.
2. Source Verification substrate.
3. Horizon Intelligence.
4. Tender Intake.
5. Entity Resolution strengthening.
6. Supplier Intelligence.
7. Market and Competitive Landscape.
8. Network Intelligence.
9. Intelligence Brief.
10. Cross-capability end-to-end validation and calibration.

## Delivery PRs

- PR-A: PR #75 repair + capability registry.
- PR-B: Evidence Verification substrate.
- PR-C: Horizon Intelligence.
- PR-D: Tender Intake.
- PR-E: Entity/Supplier progressive intelligence.
- PR-F: Market/Competitive/Network intelligence.
- PR-G: Intelligence Brief + E2E calibration.

## Required end-to-end fixtures

1. Pre-tender: upstream signal → requirement → package forecast → monitoring.
2. Rapid tender: solicitation first → intake → identity reconciliation → requirement extraction → supplier shortlist.
3. Contradictory evidence: conflicting sources → V2/V3 verification → unresolved or qualified assessment rather than false certainty.

The Bangladesh Coast Guard CPV dry run should be reused as one validation case, supplemented by true pre-tender and contradictory-evidence cases.
