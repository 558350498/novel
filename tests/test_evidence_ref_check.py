from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.evidence_ref_check import (  # noqa: E402
    resolve_json_pointer,
    run_checks,
    validate_evidence_ref,
)


class EvidenceRefCheckTests(unittest.TestCase):
    def test_project_evidence_ref_contracts(self) -> None:
        report = run_checks()
        self.assertTrue(report["ok"], report["findings"])
        self.assertGreaterEqual(report["target_count"], 1)

    def test_json_pointer_resolves_nested_values(self) -> None:
        data = {"metrics": {"short": [1, {"value": 2}]}}
        self.assertEqual(2, resolve_json_pointer(data, "/metrics/short/1/value"))

    def test_markdown_is_not_machine_evidence(self) -> None:
        findings = validate_evidence_ref("analysis/reports/example.md")
        self.assertEqual("error", findings[0].severity)
        self.assertIn("Markdown", findings[0].detail)


if __name__ == "__main__":
    unittest.main()
