# Bangladesh Procurement v2 — Registry Envelope / Materialization Validation

**Status:** SUPERSEDED  
**Superseded on:** 2026-10-18  
**Superseded by:** `docs/validation/argus-v2-drift-repair.md`

The original validation report at merge commit `89ae842da1acaa1a6eba8c79e402e00af8861eb2` is retained in Git history for auditability.

Its high-level production safety conclusion remains valid: Bangladesh Procurement v1.3 stayed active and no live registry migration occurred. However, the report overstated three candidate-level conclusions:

1. it treated legacy envelope `status` as if it could own standalone-v2 `record_state`;
2. it reported `material information loss: 0` from a declared receipt value rather than an executable semantic-loss calculation;
3. it described rollback as proven even though the rehearsal had only demonstrated source non-mutation.

Those defects are corrected by the drift-repair validation record. Do not use this superseded report as an activation basis.

ATLAS OS is unchanged.
