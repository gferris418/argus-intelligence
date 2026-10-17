-- ARGUS Master Registry v0.2.0 -> v0.2.1 evidence-semantics migration
-- Additive/lossless: preserves every legacy analytical_label value and row.
-- This file is a candidate migration artifact. It is not executed by repository CI.

BEGIN;

ALTER TABLE argus.record_evidence
    ADD COLUMN IF NOT EXISTS claim_type text,
    ADD COLUMN IF NOT EXISTS claim_condition text;

-- New v0.2.1 evidence may use claim_type + claim_condition without a legacy label.
-- Existing v0.2.0 rows keep analytical_label unchanged.
ALTER TABLE argus.record_evidence
    ALTER COLUMN analytical_label DROP NOT NULL;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conrelid = 'argus.record_evidence'::regclass
          AND conname = 'ck_record_evidence_claim_type'
    ) THEN
        ALTER TABLE argus.record_evidence
            ADD CONSTRAINT ck_record_evidence_claim_type
            CHECK (claim_type IS NULL OR claim_type IN ('FACT','DERIVED','INFERENCE','ASSUMPTION','UNKNOWN'));
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conrelid = 'argus.record_evidence'::regclass
          AND conname = 'ck_record_evidence_claim_condition'
    ) THEN
        ALTER TABLE argus.record_evidence
            ADD CONSTRAINT ck_record_evidence_claim_condition
            CHECK (claim_condition IS NULL OR claim_condition IN ('CURRENT','STALE','CONFLICT'));
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conrelid = 'argus.record_evidence'::regclass
          AND conname = 'ck_record_evidence_semantics_v021'
    ) THEN
        ALTER TABLE argus.record_evidence
            ADD CONSTRAINT ck_record_evidence_semantics_v021
            CHECK (
                (
                    (claim_type IS NULL AND claim_condition IS NULL)
                    OR
                    (claim_type IS NOT NULL AND claim_condition IS NOT NULL)
                )
                AND
                (
                    analytical_label IS NOT NULL
                    OR
                    (claim_type IS NOT NULL AND claim_condition IS NOT NULL)
                )
            );
    END IF;
END
$$;

COMMENT ON COLUMN argus.record_evidence.analytical_label IS
    'Legacy ARGUS v0.2.0 analytical label. Retained for lossless backward compatibility; new v0.2.1 writes should use claim_type + claim_condition.';
COMMENT ON COLUMN argus.record_evidence.claim_type IS
    'ARGUS v0.2.1 analytical claim type: FACT, DERIVED, INFERENCE, ASSUMPTION, UNKNOWN.';
COMMENT ON COLUMN argus.record_evidence.claim_condition IS
    'ARGUS v0.2.1 claim condition: CURRENT, STALE, CONFLICT.';

COMMIT;
