# Regression Comparison - round6_codex_full_loop_20260609

baseline_run: `round5_auto_prompt_20260608`
candidate_run: `round6_codex_full_loop_20260609`

changed_surface:
- prompt
- candidate
- corpus_slices analysis_docs paths
- local rewrite from `candidate_001` to `candidate_002`

confirmed_cases_checked:
- none

Reason: `analysis/failure_cases.json` currently contains only provisional cases. Formal regression uses `user_confirmed` cases only.

provisional_cases_observed:
- `F006_NEG_001`: observed again in `candidate_001` and still present after one local rewrite in `candidate_002`, though hard failure was cleared. The remaining issue is short/mid dialogue distribution, not absence of a long overload utterance.
- `F007_BORDER_001`: observed again because Delta first remains `adachi_daily`, not `adachi_pressure`. This is exploratory signal only, not a quality score.

process_notes:
- `corpus_slices/slices.json` was updated because the old `analysis_docs` paths pointed to missing files. The new active docs paths allow Delta to run, but old and new Delta reports should not be compared without noting this reference change.
- `candidate_002` cleared hard fail reasons from `candidate_001`: length is now above 6000 and the ending no longer triggers the closure marker.
- `candidate_002` remains `needs_manual_triage`: short dialogue remains above the configured limit, 11-40 character dialogue remains below target, bins L1 remains high, and Delta remains `adachi_daily` first.

decision: `needs_manual_triage`

Stop condition: one local rewrite has been performed and the gate has been rerun. Further revision requires user review or an explicit new run.
