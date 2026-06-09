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
provisional_cases_observed:
decision:
```

## Current Baselines

| Run | Current use |
|---|---|
| `round5_auto_prompt_20260608` | Active candidate evidence; currently `needs_manual_triage` because Delta ranks `adachi_daily` first. |
| `round5_self_prompt_20260608_distribution_check` | Provisional negative evidence for dialogue-shape collapse. |
| `existing_rounds_audit` | Historical evidence for early-round failure modes. |
| `round4_three_versions` | Historical manual-triage evidence. |

## Next Work

1. Promote only user-confirmed cases from `analysis/failure_cases.json`.
2. Add a generated comparison report per changed candidate run under `analysis/reports/candidates/<run_id>/regression_comparison.md`.
3. Require `agent_regression_checker` whenever prompt, model, gate config, JSON schema, rewrite policy, or multi-agent review process changes.
