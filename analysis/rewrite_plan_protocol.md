# Rewrite Plan Protocol v1

## Purpose

`rewrite_plan.json` is the bridge between candidate diagnostics and one controlled local rewrite.

It is not a quality judgment, a style score, or a replacement for user review. It answers:

- where the candidate needs work;
- which evidence triggered the rewrite;
- what one local rewrite is allowed to change;
- what the rewrite must not break.

The protocol is designed so the current human-in-the-loop process can later be replaced by an agent loop or function-call loop without changing the artifact shape.

## Loop

```text
candidate.md + candidate.json
-> gate reports + segment diagnostics
-> rewrite_plan.json
-> one local rewrite
-> candidate_002.md + candidate_002.json
-> gate again
-> stop at failed_auto_gate / needs_manual_triage / pending_user_review
```

Only one automatic rewrite is allowed before returning to user review or manual triage.

## Product Boundary

The project should not compete with black-box authorship-attribution research. Its value is:

- interpretable diagnostics;
- local rewrite plans;
- evidence-backed constraints;
- preserved user judgment.

The diagnostic layer should explain which section is too `daily`, which section has `pressure`, and where explanation leakage appears. It should not declare whether the draft is good.

## Core Schema

The core fields are stable. Additional fields may be added by future projects or agents, but these fields should remain present.

```json
{
  "version": 1,
  "run_id": "round_x",
  "candidate": "candidate_001.md",
  "allowed_auto_rewrite": true,
  "rewrite_scope": "local",
  "diagnostic_sources": [
    "metric",
    "segment_delta",
    "agent_close_reading",
    "user_feedback"
  ],
  "priority": [
    "user_feedback",
    "blocking_metric",
    "segment_delta",
    "agent_close_reading"
  ],
  "target": {
    "beat": "daily_waiting",
    "segments": ["draft_p004", "draft_p005"],
    "local_role": "电话前等待后半段"
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
  "dialogue_constraints": {
    "blocking_checks": [],
    "rewrite_triggers": [],
    "review_warnings": []
  },
  "conflicts": [],
  "stop_after_rewrite": true
}
```

## Diagnostic Sources

Every diagnosis must name its source. Do not collapse all signals into "the system says".

| source | role |
|---|---|
| `metric` | Rule-based measurements such as length, dialogue distribution, explanation markers, or JSON utterance statistics. |
| `segment_delta` | Segment-level relative-distance signals such as `adachi_daily`, `adachi_pressure`, or `shimamura_view` proximity. |
| `agent_close_reading` | Agent reading notes for risks that cannot be reduced to simple metrics. |
| `user_feedback` | User review decisions and aesthetic judgment. |

Priority for conflicts:

```text
user_feedback > blocking_metric > segment_delta > agent_close_reading
```

Signals should not overwrite each other. Conflicts must be recorded under `conflicts`.

## Deterministic Planner

The deterministic planner should not improvise. It should only copy structured evidence from reports:

- triggered check id;
- source;
- observed value;
- threshold or target;
- affected segment;
- report path.

Example:

```json
{
  "source": "metric",
  "id": "shimamura_explanation_markers",
  "observed": 1,
  "threshold": 0,
  "action": "rewrite_trigger",
  "evidence": "candidate_json.shimamura_explanation_marker_hits"
}
```

## Agent Layer

The agent layer may translate evidence into a prose rewrite task, but it must stay inside the planner evidence.

Allowed:

- summarize why a target beat needs local rewriting;
- write `intent`, `do`, and `avoid`;
- add close-reading warnings with `source: agent_close_reading`;
- ask a `style_owner_question` when user judgment is needed.

Not allowed:

- invent untriggered metric failures;
- declare a draft successful;
- rewrite beats outside `target`;
- turn a metric into a quality score.

## Dialogue Constraints

Dialogue is a generation budget, not just a literary label.

Use execution-oriented buckets:

```json
{
  "dialogue_constraints": {
    "blocking_checks": [
      {
        "id": "adachi_long_overload",
        "metric": "max_adachi_utterance_chars",
        "operator": ">=",
        "threshold": 300,
        "evidence_source": "candidate_json.utterances",
        "on_violation": "failed_auto_gate"
      }
    ],
    "rewrite_triggers": [
      {
        "id": "shimamura_avg_len",
        "metric": "shimamura_avg_chars",
        "target": "<=18",
        "tolerance": "<=28",
        "on_violation": "rewrite_plan"
      }
    ],
    "review_warnings": [
      {
        "id": "long_utterance_too_clean",
        "signal": "long utterance may read like clear confession instead of failed transmission",
        "evidence_source": "agent_close_reading",
        "on_violation": "needs_manual_triage"
      }
    ]
  }
}
```

Definitions:

- `blocking_checks`: machine-checkable failures that block progression.
- `rewrite_triggers`: machine-checkable issues that generate one local rewrite plan.
- `review_warnings`: evidence or close-reading risks that require human judgment.

## Open Fields

Do not freeze literary action labels such as `extend_prewarm` or `shorten_shimamura` into a product-level enum.

The schema fixes containers and flow, not the vocabulary of every possible project. Future projects may add:

- `tags`;
- `confidence`;
- `risk_notes`;
- `metric_blind_spot`;
- `style_owner_question`.

These fields are optional and must not replace the core fields.

## Rewrite Guardrails

`rewrite_task.avoid` is required because it prevents metric gaming.

Common guardrails for the current kernel:

- do not add new plot just to satisfy metrics;
- do not let Shimamura explain Adachi;
- do not turn Adachi's long utterance into a clean confession;
- do not pile emotion words when `pressure` is weak;
- do not close the ending;
- do not rewrite beats outside the target.

## Current Implementation Status

- `candidate.md + candidate.json` exists.
- `tools/light_harness.py` produces gate reports and manifests.
- `tools/eder_delta_evaluator.py` produces experimental segment-level cosine Delta reports.
- `rewrite_plan.json` is not yet generated automatically.
- Until a deterministic planner exists, rewrite plans may be written manually from report evidence.
