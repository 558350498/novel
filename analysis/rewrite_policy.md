# Rewrite Policy v0

This is the operational policy for candidate repair. The schema source remains `analysis/rewrite_plan_protocol.md`.

## Policy

- A candidate may receive at most one automatic/local rewrite before stopping for review or triage.
- A rewrite must be driven by evidence from gate reports, segment diagnostics, agent review, or user feedback.
- A rewrite must target a local beat, segment, utterance group, or dialogue-shape issue.
- A rewrite must not rewrite the whole candidate to chase metrics.
- A rewrite must not let Delta become an imitation or quality target.
- A rewrite must preserve the fixed kernel and user review boundary.

## Required Artifact

```text
drafts/candidates/<run_id>/rewrite_plan.json
```

The rewrite plan records this run's evidence and permitted action. Rules and thresholds stay in `analysis/harness_config.json`.

## Minimum Fields

```json
{
  "version": 1,
  "run_id": "",
  "candidate": "candidate_001.md",
  "allowed_auto_rewrite": true,
  "rewrite_scope": "local",
  "target": {
    "beat": "",
    "segments": [],
    "local_role": ""
  },
  "planner": {
    "mode": "deterministic",
    "triggered_checks": [],
    "segment_signals": []
  },
  "agent_layer": {
    "close_reading_notes": [],
    "rewrite_task": {
      "intent": "",
      "do": [],
      "avoid": []
    }
  },
  "conflicts": [],
  "stop_after_rewrite": true
}
```

## Forbidden Fixes

- Global rewrite without a local target.
- Adding new plot only to satisfy length or dialogue bins.
- Padding short replies instead of changing the dialogue-window mechanism.
- Turning Shimamura into a therapist.
- Turning Adachi's overload into clean self-analysis.
- Closing the emotional wound.
- Declaring the rewrite better before user review.

## Dialogue-Window Repair

When `F008_dialogue_run_overextension` is triggered, the rewrite plan must stay local to the affected dialogue run or beat.

Required handling:

- Use the strongest available budget source: `beat_source_alignment` > `source_slice_profile` > `chapter_profile_warning_only` > `missing_source_window_budget`.
- If only `chapter_profile_warning_only` or `missing_source_window_budget` is available, record the issue as warning/manual triage instead of inventing a hard threshold.
- Add `dialogue_windows` budget objects to the rewrite plan before editing prose.
- Treat `stream_agent` as the window reset agent: it must insert Adachi thought, body sensation, object carrier, delayed thought, or misread residue between overlong spoken windows.
- Keep `dialogue_agent` responsible only for spoken surface; it must not use long Q/A chains as the pressure carrier.

Suggested `dialogue_windows` entry:

```json
{
  "window_id": "",
  "beat_id": "",
  "budget_source": "",
  "speakers": ["adachi", "shimamura"],
  "pair_units_target": null,
  "pair_units_warn": null,
  "pair_units_hard": null,
  "handoff_after": "",
  "stream_agent_required": ["body", "object", "delayed_thought"]
}
```

## Next Work

Generate the first real `rewrite_plan.json` for the current active candidate run after the gate report and multi-agent review notes are available.
