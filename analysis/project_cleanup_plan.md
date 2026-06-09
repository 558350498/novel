# Project Cleanup Plan

## Goal

Reduce navigation noise without losing useful provenance.

The current product direction is:

```text
candidate.md + candidate.json
-> gate + segment diagnosis
-> rewrite_plan.json
-> one controlled local rewrite
-> user review
```

Cleanup should make that path easy to find. Entry-point docs should not link to missing early-round files as active material.

## Rule

Do not delete source texts, user-reviewed evidence, current candidates, current reports, current protocol docs, or skill source files without explicit user confirmation.

Generated artifacts can usually be regenerated, but deletion should happen only after user confirmation.

## Keep As Active

| Path | Reason |
|---|---|
| `README.md` | project entrypoint |
| `INDEX.md` | fast active/project/corpus index |
| `PROJECT_STATUS.md` | current truth and next legal actions |
| `analysis/README.md` | durable protocol map |
| `analysis/reports/README.md` | generated report map |
| `tools/project_doctor.py` | active path and doc drift checker |
| `analysis/rewrite_plan_protocol.md` | current agent-loop protocol |
| `analysis/productization_gate_v1.md` | product boundary and gate role |
| `analysis/harness_config.json` | rule configuration |
| `analysis/failure_taxonomy.md` | executable failure taxonomy |
| `analysis/failure_cases.json` | case registry |
| `analysis/gate_report_protocol.md` | gate report contract |
| `analysis/rewrite_policy.md` | one-rewrite policy |
| `analysis/review_ledger.jsonl` | user verdict ledger |
| `analysis/regression_comparison.md` | regression protocol |
| `tools/light_harness.py` | gate aggregator |
| `tools/eder_delta_evaluator.py` | segment-level diagnostic experiment |
| `tools/dialogue_window_analyzer.py` | dialogue-window diagnostic |
| `drafts/candidates/round6_codex_full_loop_20260609/` | current candidate run |
| `analysis/reports/candidates/round6_codex_full_loop_20260609/` | current candidate reports |
| `skills/novel-gate-harness/` | project skill source |

## Keep As Supporting Evidence

These remain useful, but should not replace the active run as the first route:

| Path | Reason |
|---|---|
| `analysis/reports/corpus_profile_adachi_pressure.md/json` | reference-group profile |
| `analysis/reports/tokenization_vol05.md/json` | broad volume tokenization background |
| `analysis/reports/tokenization_vol05_shimamura_blade.md/json` | current kernel tokenization evidence |
| `analysis/reports/tokenization_vol05_shimamura_blade_deepseek_v4_flash.md/json` | model-side tokenizer comparison |
| `analysis/reports/user_review_originality_overconstraint.md` | user-facing review note |
| `drafts/candidates/round5_auto_prompt_20260608/` | previous automatic prompt candidate set |
| `analysis/reports/candidates/round5_auto_prompt_20260608/` | previous candidate reports and segment Delta evidence |

## Archive Candidates

Archive only after confirming the path still exists and is not user-owned:

| Path pattern | Suggested action |
|---|---|
| old prompt drafts | archive under `analysis/archive/prompts/` |
| early-round reports | archive under `analysis/reports/archive/early_rounds/` |
| superseded candidate runs | archive under `drafts/archive/candidates/` and `analysis/reports/archive/candidates/` |
| `round5_self_prompt_20260608` paths | confirm whether this was a user-owned experiment before archiving |

## Deletion Candidates After Confirmation

These appear generated and regenerable, but delete only after confirmation:

| Path pattern | Reason |
|---|---|
| `analysis/reports/*.tokens.txt` | large generated token streams; Markdown/JSON summaries are usually enough |
| duplicate candidate report reruns | regenerated from candidate + harness config |
| stale distribution-check report directories | useful only while debugging the specific metric |

## Suggested Folder Policy

Future layout:

```text
analysis/
  rewrite_plan_protocol.md
  productization_gate_v1.md
  harness_config.json
  archive/
    prompts/
    early_rounds/
    reports/
drafts/
  candidates/
    <active_run_id>/
  archive/
    candidates/
analysis/reports/
  candidates/
    <active_run_id>/
  archive/
    candidates/
```

## Cleanup Sequence

1. Keep entrypoint docs focused on active files.
2. Run `python tools/project_doctor.py` after doc edits.
3. Confirm which historical candidate paths are user-owned.
4. Archive old prompts and early-round reports.
5. Delete generated `.tokens.txt` files only after confirmation.

## Do Not Remove

- `data/raw/`
- `novel_index.json`
- `corpus_slices/slices.json`
- user review records
- current candidate and reports
- current protocol docs
- skill source files
