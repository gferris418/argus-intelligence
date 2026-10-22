# GitHub-First Canonical Storage Architecture — Legacy Baseline

**Status:** SUPERSEDED  
**Original effective date:** 2026-10-18  
**Superseded:** 2026-10-22  
**Superseded by:** [Canonical Identity and Operational Database v1](canonical-identity-operational-database-v1.md)

## Historical decision

This document records the interim phase in which the public `argus-intelligence` GitHub repository served as the physical canonical structured store while an operational database was deferred.

That interim storage decision is no longer the active Access Asia persistence architecture.

## Current authority

The current architecture is:

- **GitHub:** canonical identity/schema governance, code, migrations, tests, release contracts, historical registry baselines and versioned release snapshots.
- **SharePoint SQLite:** current mutable ARGUS operational structured state at the governed logical location defined in `profiles/access-asia-system-registry.yaml`.
- **SharePoint files:** original/working business documents and evidence payloads.
- **HubSpot:** CRM master identity and commercial relationship state according to the Access Asia system registry.

The three-layer identity model, single-writer database protocol, security rules and source-of-truth split are defined in `canonical-identity-operational-database-v1.md` and `profiles/canonical-object-identity-standard-v1.0.yaml`.

## Historical compatibility

Existing GitHub JSON/JSONL registry files remain valuable as migration, provenance, audit and bootstrap material. They must not be treated as a second routine live-write authority once the SharePoint SQLite operational registry is active.

Existing stable ARGUS identifiers remain valid and are not renumbered merely because the new canonical ID format is more regular.

## Security rule retained

The GitHub repository is public. Credentials, authentication material, SharePoint sharing tokens, SharePoint drive/item IDs, HubSpot native private IDs, personal contact data, restricted source payloads and confidential source documents must not be committed.
