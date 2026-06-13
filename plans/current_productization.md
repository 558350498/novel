# Current Productization Work

## Goal

Make the harness trustworthy as a record system: a future agent should be able to find the current state, verify contracts, and understand what work remains without reconstructing the project from chat.

## Active Threads

| Thread | Current State | Next Useful Step |
|---|---|---|
| Editing action contract | `editing_actions` is machine-checkable and wired into CI. | Keep action ids stable; require new rewrite-plan actions to cite legal ids. |
| Evidence references | JSON/JSONL evidence refs are machine-checkable. | Prefer JSON pointers for new agent claims, rewrite plans, and case entries. |
| Case triplets | F006/F008/F009 have complete positive/negative/borderline triplets; F001-F005/F007 are captured in `plans/taxonomy_triplet_issues.md`. | Work one triplet issue at a time and remove ids from `missing_case_triplets` only after complete evidence refs exist. |
| Full run smoke test | Minimal/full artifact chain is covered by tests. | Extend only when a new required artifact joins the run contract. |
| Cleanup/drift summary | Read-only checker and scheduled workflow exist. | Review summary artifacts before archiving or deleting anything. |
| Artifact boundary | Main repo keeps evidence anchors; generated history should move outward by default. | Use `analysis/artifacts_manifest.json` and `../novel-reports/` before moving complete run history. |
| Trend reporting | `tools/trend_report.py` generates `../novel-reports/trend/runs.jsonl` / `weekly_summary.md` and validates `analysis/trend_report_contract.md`. | Keep it derived from manifest, gate report, and ledger data; add charts only after the table stabilizes. |
| GitHub workflow | Intended model is issue -> branch -> PR -> merge. | Use issues as the attention queue when authentication/workflow is ready. |

## Acceptance Checks

Run these before marking productization work done:

```powershell
python tools/project_doctor.py --strict-warnings
python tools/project_ci.py --require-regression-review
```

For cleanup/drift work, also run:

```powershell
python tools/cleanup_drift_check.py --strict-warnings --output .tmp/project_drift_summary.md
```
