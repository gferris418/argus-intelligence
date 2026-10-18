import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORDS = ROOT / "data" / "registry" / "records.jsonl"
TRANSFORMER = ROOT / "tools" / "bangladesh_procurement_v2_migrate.py"
REHEARSAL = ROOT / "tests" / "fixtures" / "bangladesh-v2" / "historical-baseline-rehearsal.json"


def load_transformer():
    spec = importlib.util.spec_from_file_location("bd_v2_migrate_exact", TRANSFORMER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class BangladeshProcurementV2HistoricalRehearsalExact(unittest.TestCase):
    def test_committed_rehearsal_payloads_equal_transformer_output(self):
        self.assertTrue(REHEARSAL.exists())
        records = [json.loads(line) for line in RECORDS.read_text().splitlines() if line.strip()]
        procurements = [record for record in records if record["record_type"] == "PROCUREMENT"]
        module = load_transformer()
        expected = [module.transform_legacy_procurement(record) for record in procurements]
        rehearsal = json.loads(REHEARSAL.read_text())
        self.assertEqual(rehearsal["transformed_payloads"], expected)


if __name__ == "__main__":
    unittest.main()
