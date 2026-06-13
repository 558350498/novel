# Execution Plans

This directory holds repo-level execution plans that should survive beyond a single candidate run.

Keep plans short, actionable, and linked to machine-verifiable artifacts when possible. Do not use this directory for generated run reports; those belong under `analysis/reports/`.

| Plan | Purpose |
|---|---|
| `current_productization.md` | Current productization work for turning the harness into a reliable record system. |
| `technical_debt.md` | Known structural debt that should shape future issues and PRs. |

## Update Rules

- Update these files when the repo workflow changes, not for every candidate diagnosis.
- Keep user verdicts in `analysis/review_ledger.jsonl`.
- Keep run-specific evidence under `analysis/reports/candidates/<run_id>/`.
- Turn stable plan items into GitHub Issues or PRs when the GitHub workflow is available.
