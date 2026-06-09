---
name: novel-gate-harness
description: Orchestrate the single-kernel narrative mechanism harness from prompt/candidate generation through gate reports, multi-agent review, local rewrite policy, regression comparison, and user-led review. Use when working in the novel style lab, generating or revising candidates, tuning prompts, running gates, triaging results, or deciding the next action for a candidate.
---

# Novel Gate Harness

Use this skill in `C:\Users\33625\Documents\novel` for the fixed single-kernel project.

This is one orchestration skill with two internal harnesses:

```text
prompt/candidate generation harness
-> result/evaluation harness
-> user review and ledger
```

Do not split generation and evaluation into independent workflows unless a future project has a separate feedback bridge. The current project needs one loop so failure taxonomy, cases, review ledger, and regression results constrain the next generation pass.

## Required Project Truth

Before acting, read:

- `PROJECT_STATUS.md`
- `README.md`
- `analysis/failure_taxonomy.md`
- `analysis/failure_cases.json`
- `analysis/review_ledger.jsonl`
- `analysis/regression_comparison.md`
- `analysis/reports/README.md`

If the task is unfamiliar, also read [project_architecture.md](references/project_architecture.md).

## Fixed Kernel

Keep v1 fixed to this kernel:

> Emotional overload is real, but the spoken surface is lighter, smaller, displaced, or failed. The receiver catches surface terms, gives ordinary care, and temporarily stops the bleeding without solving the wound.

Do not switch styles, authors, genres, kernels, or quality targets.

## Orchestration Flow

1. Load project state, confirmed cases, provisional cases, and ledger entries.
2. If a new prompt or candidate is needed, follow [prompt_generation_harness.md](references/prompt_generation_harness.md).
3. Produce paired candidate artifacts:

   ```text
   drafts/candidates/<run_id>/candidate_001.md
   drafts/candidates/<run_id>/candidate_001.json
   ```

4. If evaluating an existing candidate, skip generation and follow [result_harness.md](references/result_harness.md).
5. Run the gate script:

   ```powershell
   python skills/novel-gate-harness/scripts/run_candidate_gate.py --run-id <run_id> --candidates drafts/candidates/<run_id>/candidate_001.md
   ```

6. For fragment exercises only, use:

   ```powershell
   python skills/novel-gate-harness/scripts/run_candidate_gate.py --run-id <run_id> --candidates drafts/candidates/<run_id>/candidate_001.md --scope fragment
   ```

7. For full candidates, run the mandatory multi-agent review round before user review.
8. If a local rewrite is allowed, create or update `drafts/candidates/<run_id>/rewrite_plan.json`, perform one local rewrite, rerun the gate, and stop.
9. Present only evidence and open questions to the user. Never declare success before user verdict.
10. After user review, append the decision to `analysis/review_ledger.jsonl` and update cases only when user-confirmed.

## Hard Stop Rules

- Gate and Delta are failure/localization tools, not quality scores.
- `pending_user_review` is not success.
- Missing full-candidate multi-agent review means `needs_manual_triage: missing_multi_agent_review_round`.
- No `case_id`, no formal taxonomy entry.
- No positive / negative / borderline triplet, no stable mechanism entry.
- Formal regression only uses `user_confirmed` cases.
- Automatic/local rewrite is at most once before user review or manual triage.

## Internal Harnesses

- [prompt_generation_harness.md](references/prompt_generation_harness.md): builds prompts, candidate specs, and paired candidate files from kernel constraints, cases, ledger, and regression risk.
- [result_harness.md](references/result_harness.md): runs gate reports, multi-agent review, rewrite policy, regression comparison, and ledger handoff.
- [candidate_json.md](references/candidate_json.md): paired JSON structure details.
- [corpus_profile_gate.md](references/corpus_profile_gate.md): compressed profile rules for gate-facing decisions.
