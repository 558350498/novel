# Project Status

## Objective

Build a single-kernel narrative mechanism failure harness for Chinese prose generation and review.

The project is not a prompt pile, a generic fiction generator, or a literary quality judge. It is an executable workflow for one fixed aesthetic kernel:

> 情绪过载真实存在，但说出口的表层更轻、更小、更错位、更失败；接收者只接住表层词，给出普通照顾，暂时止血，但不真正解决关系伤口。

## Current State

Current active run: `round6_codex_full_loop_20260609`.

Current latest candidate:

- Markdown: `drafts/candidates/round6_codex_full_loop_20260609/candidate_002.md`
- Structure JSON: `drafts/candidates/round6_codex_full_loop_20260609/candidate_002.json`
- Rewrite plan: `drafts/candidates/round6_codex_full_loop_20260609/rewrite_plan.json`
- Reports: `analysis/reports/candidates/round6_codex_full_loop_20260609/`
- Gate manifest: `analysis/reports/candidates/round6_codex_full_loop_20260609/manifest.json`

Latest gate status: `needs_manual_triage`.

The candidate is not approved and should not be described as successful before user review.

## Latest Gate Signals

From `analysis/reports/candidates/round6_codex_full_loop_20260609/candidate_002_gate.json`:

| Signal | Current value | Gate expectation |
|---|---:|---|
| `char_count` | 6367 | full candidate must be >= 6000 |
| `short_dialogue_pct_1_10` | 75.21 | should be <= 65.0 |
| `mid_dialogue_pct_11_40` | 23.97 | should be >= 30.0 |
| `dialogue_distribution_l1` | 78.94 | should be <= 60.0 |
| `delta_first` | `adachi_daily` | expected `adachi_pressure` |

Candidate JSON is present and structurally usable:

- `utterance_count`: 122
- `adachi_utterance_count`: 57
- `adachi_max_len`: 709
- `adachi_ge_long_threshold`: 1
- `shimamura_utterance_count`: 64
- `shimamura_avg_len`: 6.42
- `shimamura_deep_understanding_ids`: none

## Current Next Actions

Only these next actions are legal without changing the project direction:

1. Triage `candidate_002` manually against the gate signals and dialogue-window review.
2. If the user gives a verdict, append it to `analysis/review_ledger.jsonl`.
3. If more repair is requested, create a new run or explicitly reopen the one-rewrite limit; do not silently rewrite `candidate_002`.
4. If prompt, model, gate config, JSON schema, or rewrite policy changes, rerun regression comparison and agent review.
5. Keep the project map clean by running `python tools/project_doctor.py` after entrypoint doc edits.

## Active Workflow

```text
candidate.md + candidate.json
-> gate + segment diagnosis
-> mandatory multi-agent review for full candidates
-> rewrite_plan.json
-> one controlled local rewrite
-> gate again
-> user review
-> review ledger
```

Gate and Delta are failure/localization tools. They do not produce quality scores.

Allowed gate states:

- `failed_auto_gate`
- `needs_manual_triage`
- `pending_user_review`

`pending_user_review` is not success.

## Active Artifacts

| Artifact | Path |
|---|---|
| Project entrypoint | `README.md` |
| Agent map | `AGENTS.md` |
| Project CI workflow | `.github/workflows/ci.yml` |
| Cleanup / drift workflow | `.github/workflows/cleanup-drift.yml` |
| Trend report workflow | `.github/workflows/trend-report.yml` |
| Fast index | `INDEX.md` |
| Execution plans | `plans/` |
| Analysis directory map | `analysis/README.md` |
| Reports directory map | `analysis/reports/README.md` |
| Cleanup plan | `analysis/project_cleanup_plan.md` |
| Project doctor | `tools/project_doctor.py` |
| Cleanup / drift checker | `tools/cleanup_drift_check.py` |
| Orchestration skill | `skills/novel-gate-harness/SKILL.md` |
| Project architecture reference | `skills/novel-gate-harness/references/project_architecture.md` |
| Gate wrapper | `skills/novel-gate-harness/scripts/run_candidate_gate.py` |
| Gate aggregator | `tools/light_harness.py` |
| Gate config | `analysis/harness_config.json` |
| Corpus slices | `corpus_slices/slices.json` |
| Local CI runner | `tools/project_ci.py` |
| Schema checker | `tools/schema_check.py` |
| Evidence ref checker | `tools/evidence_ref_check.py` |
| Agent review contract runner | `tools/agent_review_runner.py` |
| Failure fixtures | `tests/fixtures/failure_fixtures.json` |
| Minimal loop demo | `demo/minimal_loop/` |

## Durable Protocols

| Protocol | Path |
|---|---|
| Failure taxonomy | `analysis/failure_taxonomy.md` |
| Case registry | `analysis/failure_cases.json` |
| Gate report protocol | `analysis/gate_report_protocol.md` |
| Rewrite policy | `analysis/rewrite_policy.md` |
| Rewrite plan protocol | `analysis/rewrite_plan_protocol.md` |
| Editing actions | `analysis/editing_actions.md` |
| Review ledger | `analysis/review_ledger.jsonl` |
| Regression comparison | `analysis/regression_comparison.md` |
| Productization gate v1 | `analysis/productization_gate_v1.md` |
| Lexicon taxonomy | `analysis/lexicon_taxonomy.md` |
| Artifact manifest | `analysis/artifacts_manifest.json` |
| Trend report contract | `analysis/trend_report_contract.md` |

## Tool Roles

Artifact boundary protocol: `analysis/artifact_boundary.md`.

Generated artifacts are external by default; evidence anchors are pinned in the main repository.

- `tools/style_evaluator.py`: rule risks such as explanation leakage, closed endings, and receiver misalignment.
- `tools/delta_evaluator.py`: comparative surface-distance observer only.
- `tools/eder_delta_evaluator.py`: experimental segment-level daily/pressure localization.
- `tools/dialogue_window_analyzer.py`: dialogue-window and receiver-budget diagnostics.
- `tools/light_harness.py`: style + Delta + candidate JSON gate aggregation.
- `tools/source_shape_analyzer.py`: source chapter shape baselines.
- `tools/corpus_tokenizer.py`: lexicon discovery, not quality scoring.
- `tools/corpus_profiler.py`: reference-group feature weighting, not RAG.
- `tools/project_doctor.py`: active path, candidate pairing, and doc drift checks.
- `tools/cleanup_drift_check.py`: read-only cleanup-plan automation, active-path summary, and drift artifact generator.
- `tools/trend_report.py`: derived run trend extractor and row-contract checker writing `../novel-reports/trend/runs.jsonl` and `weekly_summary.md`.
- `tools/schema_check.py`: candidate JSON, rewrite plan, agent review, ledger, and case registry contract checks.
- `tools/evidence_ref_check.py`: verifies machine evidence refs point to existing JSON/JSONL fields; Markdown remains a human-readable view.
- `tools/agent_review_runner.py`: verifies mandatory agent review artifacts exist and avoid final verdict claims.
- `tools/project_ci.py`: local CI wrapper for doctor, cleanup/drift, gate check, schema check, evidence/action checks, trend contract check, agent review contract, and tests.

## Confirmed Boundaries

- Do not output long source excerpts.
- Do not copy source sentence patterns or plot structure.
- Do not treat “originality” as an anti-style-transfer command.
- Do not treat statistics as style essence.
- Do not use Delta as a quality score, author-similarity percentage, or copying target.
- Do not let Codex, a subagent, or the harness replace the user's final aesthetic judgment.
- Do not restore deleted early-round files just because old docs mention them.

## Provenance Policy

Early prompts, early drafts, and old generated reports are provenance. They can explain how the current workflow emerged, but they should not dominate first-pass navigation.

Before moving, archiving, or deleting anything, read `analysis/project_cleanup_plan.md`.

Do not delete source texts, user-reviewed evidence, current candidate files, current reports, current protocol docs, or skill source files without explicit user confirmation.
