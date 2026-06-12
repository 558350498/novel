from __future__ import annotations

import json
import unittest
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUN_ID = "round6_codex_full_loop_20260609"
REPORTS_DIR = ROOT / "analysis" / "reports" / "candidates" / RUN_ID
CANDIDATE_DIR = ROOT / "drafts" / "candidates" / RUN_ID


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def project_path(raw_path: str) -> Path:
    return ROOT / raw_path.replace("\\", "/")


class FullRunContractSmokeTests(unittest.TestCase):
    def test_manifest_candidate_report_links_are_live(self) -> None:
        manifest_path = REPORTS_DIR / "manifest.json"
        self.assertTrue(manifest_path.exists())
        manifest = load_json(manifest_path)
        self.assertEqual(RUN_ID, manifest["run_id"])
        self.assertEqual(
            f"analysis/reports/candidates/{RUN_ID}",
            manifest["reports_dir"].replace("\\", "/"),
        )
        self.assertGreaterEqual(len(manifest["candidates"]), 1)

        for candidate in manifest["candidates"]:
            candidate_path = project_path(candidate["candidate_path"])
            self.assertTrue(candidate_path.exists(), candidate["candidate_path"])
            self.assertTrue(candidate_path.with_suffix(".json").exists(), candidate["candidate_path"])
            for report_path in candidate["reports"].values():
                self.assertTrue(project_path(report_path).exists(), report_path)

            gate_path = project_path(candidate["reports"]["gate_json"])
            gate = load_json(gate_path)
            self.assertEqual(candidate["status"], gate["status"])
            self.assertEqual(candidate["candidate_path"], gate["candidate_path"])

    def test_agent_reviews_link_to_candidate_and_gate(self) -> None:
        for role in ["agent_gate_auditor", "agent_close_reader", "agent_regression_checker"]:
            review_path = REPORTS_DIR / f"{role}.json"
            self.assertTrue(review_path.exists(), role)
            review = load_json(review_path)
            self.assertEqual(role, review["role"])
            self.assertTrue(project_path(review["candidate_path"]).exists(), review["candidate_path"])
            self.assertTrue(project_path(review["gate_report_path"]).exists(), review["gate_report_path"])
            self.assertIsInstance(review["claims"], list)
            self.assertIsInstance(review["dissent"], list)
            self.assertIsInstance(review["recommended_user_questions"], list)

    def test_ledger_entries_point_to_existing_handoff_artifacts(self) -> None:
        ledger_path = ROOT / "analysis" / "review_ledger.jsonl"
        entries = []
        for raw_line in ledger_path.read_text(encoding="utf-8-sig").splitlines():
            if not raw_line.strip():
                continue
            entry = json.loads(raw_line)
            if entry.get("entry_type") == "ledger_schema":
                continue
            entries.append(entry)

        self.assertGreaterEqual(len(entries), 1)
        for entry in entries:
            artifact_path = project_path(entry["artifact_path"])
            self.assertTrue(artifact_path.exists(), entry["artifact_path"])
            if entry["artifact_type"] == "candidate":
                self.assertTrue(str(artifact_path).startswith(str(CANDIDATE_DIR)), entry["artifact_path"])
            self.assertIn(entry["verdict"], {"pass", "fail", "mixed", "needs_manual_triage", "defer"})


if __name__ == "__main__":
    unittest.main()
