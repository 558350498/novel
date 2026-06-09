# User Review - Dialogue Window Constraint

Date: 2026-06-10

Reviewed artifact: `drafts/candidates/round6_codex_full_loop_20260609/candidate_002.md`

## User Finding

The dialogue problem has two layers:

- The old length-bin issue remains: short answers are still too frequent and mid-length utterances are still too rare.
- A separate source-shape issue is present: dialogue chains continue for too long before returning to Adachi's thought, body sensation, or object carrier.

## Operational Model

Use a two-agent writing split in future generation:

- `dialogue_agent`: writes only the constrained spoken surface inside a dialogue window.
- `stream_agent`: writes Adachi's thought, body sensation, object carrier, and after-response pressure between dialogue windows.

For each contiguous dialogue run, find:

```text
L[shimamura] = first Shimamura utterance in the run
R[shimamura] = last Shimamura utterance in the run
```

The span `L[shimamura]..R[shimamura]` must stay short. If one question-answer exchange is counted as one unit, the source rhythm is usually 1-2 and should rarely exceed 5.

## Round 6 Measurement

Report: `analysis/reports/candidates/round6_codex_full_loop_20260609/candidate_002_dialogue_window.md`

Observed:

- `max_pair_units`: 7
- `hard_exceeded_count`: 1
- `warn_count`: 10

Updated analyzer after dual-speaker/source-budget support:

- `budget_source`: `source_slice_profile`
- `source_slice_id`: `adachi_pressure`
- `source_pair_units_p75`: 1
- `source_pair_units_p90`: 2
- `source_pair_units_max`: 3
- `max_pair_units`: 7
- `alternating_max_pair_units`: 7
- `hard_exceeded_count`: 3
- `warn_count`: 28

This confirms `candidate_002` should remain `needs_manual_triage`.

## Next Generation Constraint

Do not fix this by only padding short replies.

Instead:

- after one or two Q-A units, return to Adachi thought/object/body narration;
- keep Shimamura's spoken surface ordinary and brief, but not as endless tiny replies;
- make the dialogue agent stop at the window limit;
- let the stream agent carry the pressure between windows.
