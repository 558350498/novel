# Trend Report Contract

Trend reports are derived observability artifacts. They summarize run history; they do not create user verdicts and do not judge prose quality.

Generated files:

```text
../novel-reports/trend/runs.jsonl
../novel-reports/trend/weekly_summary.md
```

CI artifact output may use `.tmp/trend/` instead of the local report layer.

## Source Order

| Source | Role |
|---|---|
| `analysis/reports/candidates/*/manifest.json` | Per-run identity, generated time, status counts, latest candidate gate status, metrics, and report paths. |
| `analysis/reports/candidates/*/candidate_*_gate.json` | Gate metrics and Delta first signal through the manifest candidate entry. |
| `analysis/reports/candidates/*/candidate_*_dialogue_window.json` | Dialogue-run diagnostics for F008 when present. |
| `analysis/failure_cases.json` | Case-registry links from failure ids to run evidence. |
| `analysis/review_ledger.jsonl` | User-owned verdicts and user-confirmed failure ids. |
| `tools/evidence_ref_check.py` | Whether machine evidence references still resolve. |

## `runs.jsonl`

Each line is one JSON object with `version: 1`.

Required fields:

| Field | Type | Source | Meaning |
|---|---|---|---|
| `run_id` | string | manifest | Candidate/evaluation run id. |
| `generated_at` | string or null | manifest | Run generation timestamp. |
| `harness_commit` | string or null | git | Short local commit used when generating the trend row. |
| `reports_dir` | string | manifest | Report directory used by the row. |
| `manifest_path` | string | discovery | Manifest file path used by the row. |
| `candidate_count` | integer | manifest | Number of candidates in the manifest. |
| `latest_candidate` | string or null | manifest | Latest candidate path from the manifest. |
| `gate_state` | string or null | manifest | Latest candidate gate state. Allowed states are `failed_auto_gate`, `needs_manual_triage`, and `pending_user_review`. |
| `status_counts` | object | manifest | Gate state counts from manifest. |
| `metrics` | object | manifest candidate | Compact gate metrics used for trend columns. |
| `delta_first` | string or null | manifest candidate | First Delta label, diagnostic only. |
| `failure_hits` | object | derived | Boolean map for F006/F008/F009. |
| `failure_hit_sources` | object | derived | Separate lists for `gate_inferred`, `case_registry`, and `ledger`. |
| `dialogue_window` | object | dialogue-window report | F008-friendly window metrics when available. |
| `user_verdicts` | list | ledger | Ledger entries whose artifact path names this run. |
| `regression_review` | object | file existence | Whether regression comparison or regression agent artifacts exist. |
| `evidence_refs_ok` | boolean | evidence ref check | Whether local machine evidence refs resolve. |

## Failure Hit Semantics

`failure_hits` is a trend convenience field. It must not replace the case registry.

| Failure | May Be Set By |
|---|---|
| `F006_dialogue_shape_collapse` | Gate metric thresholds, case registry refs, or ledger entries. |
| `F008_dialogue_run_overextension` | Dialogue-window hard exceed, case registry refs, or ledger entries. |
| `F009_originality_overconstraint` | Ledger/case/prompt-policy evidence. It may appear in the ledger section even when no candidate run row owns it. |

## Validation

`tools/trend_report.py --check-only` must pass before treating the trend artifact as current.

The checker validates row shape, required keys, allowed gate states, required failure-hit keys, and evidence-ref status. It does not decide whether a candidate is good.
