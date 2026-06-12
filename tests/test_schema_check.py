from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.schema_check import check_failure_cases, discover_targets, load_json, run_checks  # noqa: E402


class SchemaCheckTests(unittest.TestCase):
    def test_project_json_contracts(self) -> None:
        findings = run_checks(discover_targets())
        errors = [finding for finding in findings if finding.severity == "error"]
        self.assertEqual([], errors)

    def test_required_failure_case_triplets_are_complete(self) -> None:
        findings = check_failure_cases(ROOT / "analysis" / "failure_cases.json")
        errors = [finding for finding in findings if finding.severity == "error"]
        self.assertEqual([], errors)

    def test_f006_f008_f009_are_not_missing_triplets(self) -> None:
        data = load_json(ROOT / "analysis" / "failure_cases.json")
        missing = set(data["missing_case_triplets"])
        required = set(data["required_triplet_failure_ids"])
        self.assertEqual(
            {
                "F006_dialogue_shape_collapse",
                "F008_dialogue_run_overextension",
                "F009_originality_overconstraint",
            },
            required,
        )
        self.assertFalse(required & missing)


if __name__ == "__main__":
    unittest.main()
