# Gate Report Artifact v0

Gate reports are the machine-readable and human-readable evidence produced for each candidate run.

They are failure filters, not quality judgments. A gate report may stop a candidate, send it to manual triage, or allow it to reach `pending_user_review`, but it never declares success.

## Current Output Location

```text
analysis/reports/candidates/<run_id>/
```

Expected files:

```text
candidate_001_style.md
candidate_001_style.json
candidate_001_delta.md
candidate_001_delta.json
candidate_001_gate.md
candidate_001_gate.json
manifest.json
```

Optional files:

```text
candidate_001_eder_delta.md
candidate_001_eder_delta.json
candidate_001_eder_delta_500.md
candidate_001_eder_delta_500.json
candidate_001_dialogue_window.md
candidate_001_dialogue_window.json
candidate_001_dialogue_window_adachi.md
candidate_001_dialogue_window_adachi.json
candidate_001_dialogue_window_shimamura.md
candidate_001_dialogue_window_shimamura.json
agent_gate_auditor.md/json
agent_close_reader.md/json
agent_regression_checker.md/json
```

## Required Gate JSON Fields

```json
{
  "status": "failed_auto_gate | needs_manual_triage | pending_user_review",
  "hard_fail_reasons": [],
  "manual_triage_reasons": [],
  "metrics": {},
  "candidate_json": {
    "present": true,
    "path": "",
    "errors": []
  },
  "delta_first": "",
  "candidate_path": "",
  "reports": {}
}
```

## Status Semantics

| Status | Meaning |
|---|---|
| `failed_auto_gate` | Do not send to user review. Revise or discard first. |
| `needs_manual_triage` | Inspect the specific uncertainty; may require agent review, user question, or one local rewrite. |
| `pending_user_review` | Automation found no blocking issue, but the user still owns final verdict. |

## Evidence Rules

- Every reason should map to a metric, JSON field, report path, or agent claim.
- Delta findings must be phrased as relative localization, not quality.
- Missing mandatory multi-agent review for a full candidate should appear as `needs_manual_triage: missing_multi_agent_review_round`.
- Missing source-derived dialogue-window budget should appear as a warning such as `missing_source_window_budget`, not as an invented hard fail.
- F008 dialogue-window evidence must name the checked speaker(s), budget source, `pair_units`, warn/hard thresholds if available, and the report path.
- If close reading disagrees with a metric, preserve both as a conflict instead of overwriting either one.

## Current Evidence Examples

- `analysis/reports/candidates/round5_auto_prompt_20260608/candidate_001_gate.json`
- `analysis/reports/candidates/round5_self_prompt_20260608_distribution_check/candidate_001_gate.json`
