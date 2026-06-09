# Regression Comparison v0

Regression comparison checks whether prompt, model, gate, JSON schema, rewrite policy, or review-process changes make confirmed cases worse.

This is not a quality leaderboard. It is a safety check against losing previously accepted constraints.

## Inputs

- `analysis/failure_taxonomy.md`
- `analysis/failure_cases.json`
- `analysis/review_ledger.jsonl`
- `analysis/reports/candidates/<run_id>/manifest.json`
- `analysis/reports/candidates/<run_id>/candidate_*_gate.json`
- agent review notes for full candidates

## Case Eligibility

| Case status | Regression use |
|---|---|
| `user_confirmed` | May enter formal regression suite. |
| `provisional` | May be reported separately as exploratory signal. |
| `user_rejected` | Must not be used as expected behavior. |

## Comparison Template

```text
baseline_run:
candidate_run:
changed_surface:
  - prompt
  - model
  - gate_config
  - json_schema
  - rewrite_policy
  - agent_review_process
confirmed_cases_checked:
  - case_id:
    expected:
    observed:
    status: preserved | improved | regressed | inconclusive
    evidence:
    dialogue_window:
      checked_speakers:
      budget_source:
      source_slice_id:
      source_pair_units_p90:
      source_pair_units_max:
      max_pair_units:
      alternating_max_pair_units:
      warning_or_hard_exceeded:
    prompt_policy:
      originality_overconstraint:
      copying_boundary:
      style_emulation_target:
provisional_cases_observed:
decision:
```

## Current Baselines

| Run | Current use |
|---|---|
| `round5_auto_prompt_20260608` | Active candidate evidence; currently `needs_manual_triage` because Delta ranks `adachi_daily` first. |
| `round5_self_prompt_20260608_distribution_check` | Provisional negative evidence for dialogue-shape collapse. |
| `round6_codex_full_loop_20260609` | Active F008 evidence; `candidate_002` showed overlong dialogue-window behavior and user-confirmed dialogue-run concern. |
| `ledger_20260610_originality_overconstraint` | Active F009 prompt-policy evidence; originality / anti-imitation language should not suppress source-like style mechanism transfer. |
| `existing_rounds_audit` | Historical evidence for early-round failure modes. |
| `round4_three_versions` | Historical manual-triage evidence. |

## Next Work

1. Promote only user-confirmed cases from `analysis/failure_cases.json`.
2. Add a generated comparison report per changed candidate run under `analysis/reports/candidates/<run_id>/regression_comparison.md`.
3. Require `agent_regression_checker` whenever prompt, model, gate config, JSON schema, rewrite policy, or multi-agent review process changes.
