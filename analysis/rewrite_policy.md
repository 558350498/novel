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
- Turning Shimamura into a therapist.
- Turning Adachi's overload into clean self-analysis.
- Closing the emotional wound.
- Declaring the rewrite better before user review.

## Next Work

Generate the first real `rewrite_plan.json` for the current active candidate run after the gate report and multi-agent review notes are available.
