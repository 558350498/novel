# Prompt / Candidate Generation Harness

This internal harness creates or revises prompts and candidate drafts while preserving the feedback loop from failure taxonomy, cases, ledger, and regression.

It does not judge final quality.

## Inputs

Read before generating:

- `README.md`
- `PROJECT_STATUS.md`
- `analysis/failure_taxonomy.md`
- `analysis/failure_cases.json`
- `analysis/review_ledger.jsonl`
- `analysis/regression_comparison.md`
- `analysis/reports/corpus_profile_adachi_pressure.md`
- `analysis/reports/source_chapter_shape.md`
- `analysis/generation_prompt_round4.md` when using the current long-candidate prompt
- [corpus_profile_gate.md](corpus_profile_gate.md)

## Output Options

Use the smallest output that satisfies the task:

```text
analysis/generation_prompt_<run_id>.md        # prompt artifact, if tuning prompt
drafts/candidates/<run_id>/candidate_spec.json
drafts/candidates/<run_id>/candidate_001.md
drafts/candidates/<run_id>/candidate_001.json
```

`candidate_spec.json` is optional but useful when a run needs explicit targets before prose generation.

## Generation Contract

Every full candidate must preserve:

- fixed kernel;
- daily buildup and object/body carriers;
- at least one credible long failed-transmission utterance;
- Shimamura as ordinary, surface-level receiver;
- unresolved ending;
- paired JSON structure for utterances, responses, surface terms, and deep-understanding risk.

Every full candidate must avoid:

- Shimamura naming Adachi's hidden wound;
- Adachi turning overload into clean causal self-analysis;
- closure after ordinary care;
- pressure made only from emotion words;
- dialogue collapsing into tiny call-and-response lines;
- optimizing for Delta rank as an imitation target.

## Using Failure Cases

Before drafting, select active constraints:

```json
{
  "target_failure_ids_to_avoid": [],
  "positive_case_ids_to_preserve": [],
  "negative_case_ids_to_avoid": [],
  "borderline_case_ids_to_probe": [],
  "regression_case_ids_to_check_after_generation": []
}
```

Rules:

- `user_confirmed` cases outrank provisional cases.
- Provisional cases may guide generation but must not be treated as final truth.
- If a case is missing its positive / negative / borderline triplet, mark it as a risk, not a stable rule.

## Candidate Spec Shape

When useful, write a spec before prose:

```json
{
  "version": 1,
  "run_id": "",
  "kernel_id": "adachi_misaligned_overload_v1",
  "prompt_source": "",
  "active_failure_ids": [],
  "case_targets": [],
  "scene_beats": [
    {
      "id": "b001",
      "type": "daily_buildup",
      "purpose": ""
    }
  ],
  "dialogue_shape_targets": {
    "requires_long_failed_transmission": true,
    "avoid_short_dialogue_collapse": true
  },
  "must_avoid": []
}
```

## Self-Check Before Gate

Before handing off to the result harness:

- Candidate length should satisfy full-candidate scope unless this is a fragment exercise.
- JSON must exist and parse.
- Adachi must have at least one long overload utterance.
- Shimamura responses should remain short and surface-level.
- The draft should not contain obvious closure or therapist-style explanation.
- Dialogue shape should not obviously collapse into mostly `1-10` char exchanges.

Then hand off to [result_harness.md](result_harness.md).
