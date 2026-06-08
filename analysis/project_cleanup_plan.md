# Project Cleanup Plan

## Goal

Reduce navigation noise without losing useful provenance.

This project has accumulated early prompts, old candidates, generated reports, tokenizer outputs, and experimental methods. The current product direction is now:

```text
candidate.md + candidate.json
-> gate + segment diagnosis
-> rewrite_plan.json
-> one controlled local rewrite
-> user review
```

Cleanup should make that path easy to find.

## Rule

Do not delete source texts, user-reviewed evidence, or current protocol docs.

Generated artifacts can usually be regenerated, but deletion should happen only after user confirmation.

## Keep As Active

| path | reason |
|---|---|
| `README.md` | project entrypoint |
| `PROJECT_STATUS.md` | current truth and high-level tracker |
| `analysis/rewrite_plan_protocol.md` | current agent-loop protocol |
| `analysis/productization_gate_v1.md` | product boundary and gate role |
| `analysis/harness_config.json` | rule configuration |
| `tools/light_harness.py` | gate aggregator |
| `tools/eder_delta_evaluator.py` | segment-level diagnostic experiment |
| `drafts/candidates/round5_auto_prompt_20260608/` | current generated candidate set |
| `analysis/reports/candidates/round5_auto_prompt_20260608/` | current candidate reports |
| `skills/novel-gate-harness/` | project skill source |

## Keep As Provenance

These are useful for understanding how the project reached the current route, but they should not dominate navigation:

| path | reason |
|---|---|
| `analysis/reports/diff.md` | user/Codex review evidence from early failure modes |
| `analysis/reports/source_chapter_shape.md/json` | chapter-scale baseline |
| `analysis/reports/corpus_profile_adachi_pressure.md/json` | reference-group profile |
| `analysis/reports/candidates/existing_rounds_audit/` | explains why early rounds failed |
| `analysis/reports/candidates/round4_three_versions/` | explains the shared Round 4 manual-triage issue |
| `drafts/current.md`, `drafts/round2.md`, `drafts/round3.md` | early draft history |
| `drafts/candidates/round4_three_versions/` | Round 4 candidate history |

Recommended action: move to an `archive/` area only after confirming links do not need to stay stable.

## Candidate For Archive

These can be archived out of the active path:

| path | suggested action |
|---|---|
| `analysis/generation_prompt_round3.md` | archive as superseded prompt |
| `analysis/generation_prompt_round4.md` | keep one link from README or archive after rewrite-plan prompt exists |
| `analysis/reports/round2_*` | archive under early-round reports |
| `analysis/reports/round3_*` | archive under early-round reports |
| `analysis/reports/source_shape_stats.md` | archive if `source_chapter_shape.md/json` remains the canonical baseline |
| `analysis/reports/candidates/round5_self_prompt_20260608/` | confirm whether this is a user-owned experiment before archiving |
| `analysis/reports/candidates/round5_self_prompt_20260608_distribution_check/` | confirm whether this is a user-owned experiment before archiving |
| `drafts/candidates/round5_self_prompt_20260608/` | confirm whether this is a user-owned experiment before archiving |

## Candidate For Deletion After Confirmation

These appear generated and regenerable, but delete only after confirmation:

| path pattern | reason |
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

1. Update entrypoint docs so active files are clear.
2. Generate the first real `rewrite_plan.json` for the current candidate.
3. Confirm which `round5_self_prompt_20260608` files are user-owned.
4. Archive old prompts and early-round reports.
5. Delete generated `.tokens.txt` files only after confirmation.

## Do Not Remove

- `data/raw/`
- `novel_index.json`
- `corpus_slices/slices.json`
- user review records
- current candidate and reports
- skill source files
