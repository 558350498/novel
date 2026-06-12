from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

import sys

sys.path.insert(0, str(ROOT))

from tools.editing_action_check import collect_action_refs, load_action_ids, run_checks  # noqa: E402


class EditingActionCheckTests(unittest.TestCase):
    def test_project_editing_action_contracts(self) -> None:
        report = run_checks()
        self.assertTrue(report["ok"], report["findings"])
        self.assertGreaterEqual(report["action_count"], 1)
        self.assertGreaterEqual(report["checked_action_refs"], 1)

    def test_declared_actions_are_loaded_from_markdown(self) -> None:
        action_ids, findings = load_action_ids()
        errors = [finding for finding in findings if finding.severity == "error"]
        self.assertEqual([], errors)
        self.assertIn("repair_dialogue_length_distribution", action_ids)
        self.assertIn("reset_dialogue_window", action_ids)

    def test_nested_action_refs_are_discovered(self) -> None:
        data = {
            "editing_actions": ["preserve_surface_receipt"],
            "agent_layer": {
                "recommended_editing_actions": [
                    {"action_id": "reset_dialogue_window"},
                ],
            },
        }
        self.assertEqual(
            ["preserve_surface_receipt", "reset_dialogue_window"],
            collect_action_refs(data),
        )


if __name__ == "__main__":
    unittest.main()
