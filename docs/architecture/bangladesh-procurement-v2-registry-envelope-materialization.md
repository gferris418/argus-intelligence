# Bangladesh Procurement v2 — Registry Envelope / Materialization Architecture

**Status:** SUPERSEDED  
**Superseded on:** 2026-10-18  
**Superseded by:** `docs/architecture/bangladesh-procurement-v2-registry-envelope-materialization-v1.1.md`

The original v1.0 candidate architecture at merge commit `89ae842da1acaa1a6eba8c79e402e00af8861eb2` is retained in Git history for auditability.

It was superseded after a hallucination/drift audit identified a material semantic defect: legacy envelope `status` was being used as the authoritative home for standalone-v2 `record_state`, although the existing v0.2.x status values represent procurement/process-oriented state and v2 defines record state separately.

Do not use the v1.0 document as an activation basis. Use the v1.1 candidate architecture and `docs/validation/argus-v2-drift-repair.md`.

Bangladesh Procurement v1.3 remains active. ATLAS OS is unchanged.
