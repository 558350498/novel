# Agent Map

This repo is a narrative-mechanism harness, not a general fiction generator.

Use this file as a directory map only. For project state, read `PROJECT_STATUS.md`. For runnable commands, read `README.md`.

## Read Order

1. `README.md` - active route, commands, and hard workflow boundaries.
2. `PROJECT_STATUS.md` - current run, latest gate state, and legal next actions.
3. `plans/README.md` - repo-level execution plans outside any single run.
4. `analysis/README.md` - durable protocols and analysis artifacts.
5. `analysis/reports/README.md` - generated report layout and current run reports.
6. `skills/novel-gate-harness/SKILL.md` - Codex orchestration rules for this project.

## Directory Map

| Path | Agent Use |
|---|---|
| `analysis/` | Durable protocols, case registry, ledger, cleanup plan, and analysis docs. |
| `analysis/reports/` | Generated gate, Delta, agent review, regression, and user-review evidence. |
| `corpus_slices/` | Source-slice metadata used by gates and profiles. |
| `drafts/candidates/` | Candidate Markdown/JSON pairs and per-run rewrite plans. |
| `demo/minimal_loop/` | Small runnable loop for contract smoke tests. |
| `plans/` | Repo-level productization and technical-debt execution plans. |
| `skills/novel-gate-harness/` | Agent-facing orchestration skill and references. |
| `tests/` | Unit, fixture, and contract smoke tests. |
| `tools/` | Executable harness checks, evaluators, contract validators, and CI wrapper. |
| `.github/workflows/` | Remote CI and scheduled summary workflows. |

External report layer: `../novel-reports/`. The main repo index is `analysis/artifacts_manifest.json`.

Trend row contract: `analysis/trend_report_contract.md`.

## Operating Rules

- Do not describe a candidate as successful before user review.
- Gate, Delta, and agent review are diagnostic evidence, not final judgment.
- Do not delete, archive, or move source text, user-reviewed evidence, current run artifacts, protocol docs, or skill files without explicit user confirmation.
- Prefer machine contracts over prose-only promises: update schema, doctor, CI, or tests when a rule must hold.
- Treat generated artifacts as external by default and pin only evidence anchors in the main repo.
- Run `python tools/project_ci.py --require-regression-review` after contract or workflow changes.
