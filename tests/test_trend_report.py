from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.trend_report import build_rows, load_jsonl, render_markdown, validate_rows, write_outputs  # noqa: E402


class TrendReportTests(unittest.TestCase):
    def test_build_rows_includes_active_run_signals(self) -> None:
        rows = build_rows(evidence_ok=True)
        by_run = {row["run_id"]: row for row in rows}
        self.assertIn("round6_codex_full_loop_20260609", by_run)
        active = by_run["round6_codex_full_loop_20260609"]
        self.assertEqual("needs_manual_triage", active["gate_state"])
        self.assertTrue(active["failure_hits"]["F006_dialogue_shape_collapse"])
        self.assertTrue(active["failure_hits"]["F008_dialogue_run_overextension"])
        self.assertIn("ledger", active["failure_hit_sources"])
        self.assertTrue(active["regression_review"]["present"])
        self.assertEqual([], validate_rows(rows))

    def test_render_markdown_is_derived_trend_view(self) -> None:
        rows = build_rows(evidence_ok=True)
        ledger_entries = load_jsonl(ROOT / "analysis" / "review_ledger.jsonl")
        markdown = render_markdown(rows, ledger_entries, ROOT.parent / "novel-reports" / "trend")
        self.assertIn("# Candidate Run Trend Summary", markdown)
        self.assertIn("This is a derived trend view", markdown)
        self.assertIn("round6_codex_full_loop_20260609", markdown)

    def test_write_outputs_creates_jsonl_and_markdown(self) -> None:
        rows = build_rows(evidence_ok=True)
        ledger_entries = load_jsonl(ROOT / "analysis" / "review_ledger.jsonl")
        with tempfile.TemporaryDirectory() as tmp:
            written = write_outputs(rows, ledger_entries, Path(tmp))
            jsonl_path = Path(written["runs_jsonl"])
            markdown_path = Path(written["weekly_summary"])
            self.assertTrue(jsonl_path.exists())
            self.assertTrue(markdown_path.exists())
            first = json.loads(jsonl_path.read_text(encoding="utf-8").splitlines()[0])
            self.assertIn("run_id", first)

    def test_validate_rows_rejects_missing_required_fields(self) -> None:
        findings = validate_rows([{"version": 1, "run_id": "broken"}])
        details = [finding.detail for finding in findings]
        self.assertIn("missing required field", details)


if __name__ == "__main__":
    unittest.main()
