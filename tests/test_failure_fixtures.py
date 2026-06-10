from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.light_harness import evaluate_gate  # noqa: E402


FIXTURE_PATH = ROOT / "tests" / "fixtures" / "failure_fixtures.json"


class FailureFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    def test_every_failure_id_has_triplet(self) -> None:
        for fixture in self.data["fixtures"]:
            cases = fixture["cases"]
            self.assertIn("positive", cases, fixture["failure_id"])
            self.assertIn("negative", cases, fixture["failure_id"])
            self.assertIn("borderline", cases, fixture["failure_id"])

    def test_executable_gate_fixtures(self) -> None:
        config = self.data["gate_config"]
        executable = [
            fixture
            for fixture in self.data["fixtures"]
            if fixture.get("executable_gate_cases")
        ]
        self.assertGreaterEqual(len(executable), 1)
        for fixture in executable:
            for case_name, case in fixture["executable_gate_cases"].items():
                with self.subTest(failure_id=fixture["failure_id"], case=case_name):
                    gate = evaluate_gate(
                        case["style_report"],
                        case["delta_report"],
                        config,
                        case["candidate_structure"],
                        case.get("scope", "candidate"),
                    )
                    self.assertEqual(gate["status"], case["expected_status"])
                    for expected_reason in case.get("expected_reason_contains", []):
                        reasons = "\n".join(gate["hard_fail_reasons"] + gate["manual_triage_reasons"])
                        self.assertIn(expected_reason, reasons)


if __name__ == "__main__":
    unittest.main()
