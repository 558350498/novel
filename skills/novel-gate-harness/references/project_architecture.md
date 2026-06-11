# Project Architecture Reference

Load this reference when orienting inside `C:\Users\33625\Documents\novel` or when deciding where a candidate, report, or gate change belongs.

## Directory Roles

- `README.md`: project entrypoint and command examples.
- `INDEX.md`: fast navigation map for corpus files, reports, and tools.
- `PROJECT_STATUS.md`: authoritative current state and next-step tracker.
- `data/raw/`: physical source text files. Do not copy long source excerpts into reports or skills.
- `novel_index.json`: machine-readable logical index for volume/chapter locations.
- `analysis/`: durable analysis, prompts, plans, review checklists, and configs.
- `analysis/reports/`: generated evaluator reports, human review notes, diff records, and candidate gate outputs.
- `analysis/rewrite_plan_protocol.md`: current protocol for turning diagnostics into one local rewrite.
- `analysis/editing_actions.md`: source of truth for evidence-backed local editing actions.
- `analysis/project_cleanup_plan.md`: cleanup and archive guidance for old candidates and generated reports.
- `corpus_slices/`: Delta reference slice configuration by file path and line ranges.
- `drafts/`: current and historical drafts.
- `drafts/candidates/<run_id>/`: new candidate Markdown, paired candidate JSON, and future `rewrite_plan.json`.
- `tools/`: deterministic evaluators, profilers, tokenizers, and harness scripts.
- `skills/novel-gate-harness/`: this Codex skill.

## Execution Pipeline

1. Use the current generation prompt to create a candidate Markdown draft.
2. Write a paired JSON file that records speaker/response structure without forcing speaker labels into prose.
3. Read `analysis/reports/corpus_profile_adachi_pressure.md/json` before evaluating shape or lexicon signals.
4. Run `tools/style_evaluator.py` for rule-based draft risks.
5. Run `tools/delta_evaluator.py` for relative-distance comparison against configured reference groups.
6. Optionally run `tools/eder_delta_evaluator.py` for segment-level daily/pressure localization.
7. Run `tools/light_harness.py` through the skill wrapper to produce candidate gate reports and a manifest.
8. Use `--scope candidate` for full candidates, or `--scope fragment` for short mechanism exercises that should not fail solely on length.
9. If a local rewrite is allowed, select an editing action from `analysis/editing_actions.md` and create a `rewrite_plan.json` from deterministic report evidence plus agent-layer rewrite intent.
10. Stop after one local rewrite and rerun gate.
11. Stop at `failed_auto_gate`, `needs_manual_triage`, or `pending_user_review`.
12. Record user review feedback in project docs or reports before changing prompts, lexicons, gates, or corpus labels.

## Tool Boundaries

- `style_evaluator.py` catches rule risks such as explanation leakage, closed endings, and weak receiver misalignment.
- `delta_evaluator.py` is a comparative observer only. It does not score quality, author similarity, or success.
- `eder_delta_evaluator.py` is an experimental segment diagnostic. It localizes daily/pressure distribution but does not judge quality.
- `source_shape_analyzer.py` provides chapter-scale shape baselines; use it to avoid shrinking candidates into short fragments.
- `light_harness.py` aggregates style, Delta, and optional companion candidate JSON outputs; it only filters obvious failures.
- `corpus_tokenizer.py` supports lexicon discovery; it is not a quality score.
- `corpus_profiler.py` compares reference-group taxonomy and shape weights for gate tuning; it is not RAG and should not retrieve original prose into outputs.
- Editing actions translate diagnostics into allowed local operations; they are not quality judgments.

## Non-Negotiable Review Rules

- Keep Delta relative and subordinate to close reading.
- Keep `pending_user_review` as a non-success state.
- Keep `rewrite_plan.json` as an execution order, not a review conclusion.
- Do not declare a candidate better before user review.
- Do not let Codex, a subagent, or the harness replace the user's final aesthetic judgment.
- Do not use long source excerpts or imitation language as skill resources.
