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
- `drafts/candidates/<run_id>/prompt.md` only when explicitly reusing a prior run prompt
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
- source-like rhythm, translation texture, dialogue timing, and interior-monologue shape when supported by source/slice evidence;
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
- optimizing for Delta rank as a copying target;
- long Q/A chains carrying pressure after the dialogue-window budget is exhausted.

## Style Boundary

Do not use "original" as a dominant generation command. In this harness, originality means only:

- do not copy source text;
- do not quote long source excerpts;
- do not trace exact source paragraph or scene structure;
- do not lift exclusive phrasing as a target.

Style-mechanism emulation is allowed and expected:

- sentence rhythm and pause pattern;
- light-novel translation texture;
- short/mid/long dialogue distribution;
- Adachi interior drift, correction, and object fixation;
- Shimamura's surface-level receiving cadence;
- unresolved aftertaste.

If prompt text says "do not imitate" or "original Chinese short story", rewrite that line into a narrower boundary:

```text
Do not copy source text or exact phrasing. Do preserve the source-derived rhythm, dialogue timing, interior drift, and receiver misalignment mechanisms.
```

## Beat Planner And Dialogue Windows

Use a three-role generation split when the run involves dialogue-heavy pressure:

```text
beat_planner -> dialogue_agent -> stream_agent
```

Responsibilities:

- `beat_planner` owns dialogue-window budgets and chooses the strongest available source.
- `dialogue_agent` writes the spoken surface for both `adachi` and `shimamura` within that budget.
- `stream_agent` resets the window between spoken runs with Adachi thought, body sensation, object carrier, delayed thought, or misread residue.

Budget source priority:

```text
beat_source_alignment > source_slice_profile > chapter_profile_warning_only > missing_source_window_budget
```

Rules:

- If beat-level source alignment exists, inherit the beat-level window shape.
- If no beat alignment exists but slice analysis exists, inherit the source-slice profile.
- If only chapter-level weak profile exists, treat it as warning guidance, not a hard generation limit.
- If no source or slice profile exists, emit `missing_source_window_budget` and do not invent a hard threshold.

Suggested candidate spec field:

```json
{
  "dialogue_windows": [
    {
      "window_id": "",
      "beat_id": "",
      "budget_source": "",
      "speakers": ["adachi", "shimamura"],
      "pair_units_target": null,
      "pair_units_warn": null,
      "pair_units_hard": null,
      "handoff_after": "",
      "stream_agent_required": ["body", "object", "delayed_thought"]
    }
  ]
}
```

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
    "avoid_short_dialogue_collapse": true,
    "avoid_dialogue_run_overextension": true
  },
  "dialogue_windows": [],
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
- Dialogue pressure should hand off from `dialogue_agent` to `stream_agent` before Adachi or Shimamura windows overrun their source-derived budget.

Then hand off to [result_harness.md](result_harness.md).
