from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.schema_check import discover_targets, run_checks  # noqa: E402


class SchemaCheckTests(unittest.TestCase):
    def test_project_json_contracts(self) -> None:
        findings = run_checks(discover_targets())
        errors = [finding for finding in findings if finding.severity == "error"]
        self.assertEqual([], errors)


if __name__ == "__main__":
    unittest.main()
