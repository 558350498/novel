# Result / Evaluation Harness

This internal harness evaluates candidate artifacts and decides the next process action.

It does not generate fresh prompts and does not judge final literary quality.

## Inputs

Expected candidate files:

```text
drafts/candidates/<run_id>/candidate_001.md
drafts/candidates/<run_id>/candidate_001.json
```

Read:

- `analysis/gate_report_protocol.md`
- `analysis/rewrite_policy.md`
- `analysis/rewrite_plan_protocol.md`
- `analysis/failure_taxonomy.md`
- `analysis/failure_cases.json`
- `analysis/regression_comparison.md`
- `analysis/reports/README.md`

## Machine Gate

Run full-candidate gate:

```powershell
python skills/novel-gate-harness/scripts/run_candidate_gate.py --run-id <run_id> --candidates drafts/candidates/<run_id>/candidate_001.md
```

For fragment-only mechanism checks:

```powershell
python skills/novel-gate-harness/scripts/run_candidate_gate.py --run-id <run_id> --candidates drafts/candidates/<run_id>/candidate_001.md --scope fragment
```

Read:

```text
analysis/reports/candidates/<run_id>/manifest.json
analysis/reports/candidates/<run_id>/candidate_001_gate.md
analysis/reports/candidates/<run_id>/candidate_001_gate.json
```

## Dialogue-Window Check

When `F008_dialogue_run_overextension` is active or dialogue shape is under review, run the dialogue-window analyzer.

Single-speaker form, when isolating one receiver/speaker:

```powershell
python tools/dialogue_window_analyzer.py --draft drafts/candidates/<run_id>/candidate_001.md --candidate-json drafts/candidates/<run_id>/candidate_001.json --speaker adachi --config analysis/harness_config.json --slices corpus_slices/slices.json --source-slice-id adachi_pressure --output-prefix analysis/reports/candidates/<run_id>/candidate_001_dialogue_window_adachi
python tools/dialogue_window_analyzer.py --draft drafts/candidates/<run_id>/candidate_001.md --candidate-json drafts/candidates/<run_id>/candidate_001.json --speaker shimamura --config analysis/harness_config.json --slices corpus_slices/slices.json --source-slice-id adachi_pressure --output-prefix analysis/reports/candidates/<run_id>/candidate_001_dialogue_window_shimamura
```

Multi-speaker form. This produces both per-speaker `L[speaker]..R[speaker]` windows and dual alternating windows:

```powershell
python tools/dialogue_window_analyzer.py --draft drafts/candidates/<run_id>/candidate_001.md --candidate-json drafts/candidates/<run_id>/candidate_001.json --speakers adachi shimamura --config analysis/harness_config.json --slices corpus_slices/slices.json --source-slice-id adachi_pressure --output-prefix analysis/reports/candidates/<run_id>/candidate_001_dialogue_window
```

Interpretation rules:

- Source-aligned beat budget outranks source-slice budget.
- Source-slice budget outranks chapter-level weak profile.
- Chapter-level weak profile emits warning only.
- Missing source-derived budget emits `missing_source_window_budget` warning only unless the user has confirmed a temporary threshold for the run.
- Track Adachi and Shimamura separately; do not treat a Shimamura-only check as coverage for Adachi.
- Track `dual_alternating` windows separately; these catch Q/A chains that neither single-speaker view fully explains.

## Mandatory Multi-Agent Review

For every full candidate, run separate role-bounded reviews before user review:

- `agent_gate_auditor`
- `agent_close_reader`

Also run:

- `agent_regression_checker` whenever prompt, model, gate config, JSON schema, rewrite policy, or review process changed.

Write notes under:

```text
analysis/reports/candidates/<run_id>/agent_gate_auditor.md
analysis/reports/candidates/<run_id>/agent_gate_auditor.json
analysis/reports/candidates/<run_id>/agent_close_reader.md
analysis/reports/candidates/<run_id>/agent_close_reader.json
analysis/reports/candidates/<run_id>/agent_regression_checker.md
analysis/reports/candidates/<run_id>/agent_regression_checker.json
```

Each note must contain structured evidence only:

```text
role
scope
candidate_path
gate_report_path
claims[{failure_id, case_id, span_ref, claim, evidence_type, confidence}]
dissent[{against, reason, span_ref}]
recommended_user_questions[]
```

Forbidden:

- final pass/fail verdicts;
- broad literary totalizing claims;
- "closer to original" scoring;
- collapsing multiple roles into one review;
- rewriting outside an active `rewrite_plan.json`.

If this round cannot be completed, mark the candidate:

```text
needs_manual_triage: missing_multi_agent_review_round
```

## Next-Action Rules

Use gate status plus agent notes:

| Status | Action |
|---|---|
| `failed_auto_gate` | Do not show as review-ready. Revise or discard. |
| `needs_manual_triage` | Inspect exact uncertainty; create user question or one local rewrite plan. |
| `pending_user_review` | Present evidence and open questions to user; do not claim success. |

## Local Rewrite

If a rewrite is allowed:

1. Create or update `drafts/candidates/<run_id>/rewrite_plan.json`.
2. Use evidence from gate, segment diagnostics, agent notes, or user feedback.
3. Target one local beat, segment, utterance group, or dialogue-shape issue.
4. Perform at most one local rewrite.
5. Update paired JSON.
6. Rerun the gate.
7. Stop again at `failed_auto_gate`, `needs_manual_triage`, or `pending_user_review`.

Do not globally rewrite the candidate to chase metrics.

## Regression Comparison

When any generation/evaluation surface changes, compare against confirmed cases:

- prompt;
- model;
- gate config;
- JSON schema;
- rewrite policy;
- multi-agent review process.

Use `analysis/regression_comparison.md` as the report contract.

Only `user_confirmed` cases can be formal regression expectations. Provisional cases may be reported separately.

## User Review And Ledger

When the user gives a verdict, append a JSONL entry to:

```text
analysis/review_ledger.jsonl
```

Only user verdicts can confirm cases for formal regression.
