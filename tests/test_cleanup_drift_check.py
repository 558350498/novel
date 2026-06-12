from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from cleanup_drift_check import build_report, render_markdown  # noqa: E402


class CleanupDriftCheckTests(unittest.TestCase):
    def test_cleanup_drift_report_is_clean_for_active_run(self) -> None:
        report = build_report("round6_codex_full_loop_20260609", strict_warnings=True)
        self.assertTrue(report["ok"], report["findings"])
        self.assertEqual(0, report["error_count"])
        self.assertEqual("round6_codex_full_loop_20260609", report["active_run"]["run_id"])
        self.assertIn("status_counts", report["active_run"])

    def test_cleanup_drift_markdown_names_read_only_policy(self) -> None:
        report = build_report("round6_codex_full_loop_20260609", strict_warnings=True)
        markdown = render_markdown(report)
        self.assertIn("# Project Cleanup / Drift Summary", markdown)
        self.assertIn("This check is read-only.", markdown)


if __name__ == "__main__":
    unittest.main()
