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
- `corpus_slices/`: Delta reference slice configuration by file path and line ranges.
- `drafts/`: current and historical drafts.
- `drafts/candidates/<run_id>/`: new candidate Markdown plus paired candidate JSON.
- `tools/`: deterministic evaluators, profilers, tokenizers, and harness scripts.
- `skills/novel-gate-harness/`: this Codex skill.

## Execution Pipeline

1. Use the current generation prompt to create a candidate Markdown draft.
2. Write a paired JSON file that records speaker/response structure without forcing speaker labels into prose.
3. Run `tools/style_evaluator.py` for rule-based draft risks.
4. Run `tools/delta_evaluator.py` for relative-distance comparison against configured reference groups.
5. Run `tools/light_harness.py` through the skill wrapper to produce candidate gate reports and a manifest.
6. Stop at `failed_auto_gate`, `needs_manual_triage`, or `pending_user_review`.
7. Record user review feedback in project docs or reports before changing prompts, lexicons, gates, or corpus labels.

## Tool Boundaries

- `style_evaluator.py` catches rule risks such as explanation leakage, closed endings, and weak receiver misalignment.
- `delta_evaluator.py` is a comparative observer only. It does not score quality, author similarity, or success.
- `source_shape_analyzer.py` provides chapter-scale shape baselines; use it to avoid shrinking candidates into short fragments.
- `light_harness.py` aggregates style and Delta outputs and writes gate status; it only filters obvious failures.
- `corpus_tokenizer.py` and `corpus_profiler.py` support lexicon discovery and gate tuning; they are not RAG and should not retrieve original prose into outputs.

## Non-Negotiable Review Rules

- Keep Delta relative and subordinate to close reading.
- Keep `pending_user_review` as a non-success state.
- Do not declare a candidate better before user review.
- Do not let Codex, a subagent, or the harness replace the user's final aesthetic judgment.
- Do not use long source excerpts or imitation language as skill resources.
