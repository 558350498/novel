# Failure Taxonomy v0

This file defines executable failure categories for the current single-kernel harness.

It is not a literary taxonomy. A failure category is only useful when it can drive a gate, a review question, a local rewrite policy, or a regression check.

## Entry Rules

- No `case_id`, no formal taxonomy entry.
- No positive / negative / borderline case triplet, no stable taxonomy entry.
- Cases may be provisional, but regression cases must be `user_confirmed`.
- A taxonomy entry must point to evidence paths, not just describe taste.
- Agent review may add claims, but user verdict owns final pass/fail.

## Case Types

| Type | Meaning |
|---|---|
| `positive` | Mechanism works or is acceptable for this kernel. |
| `negative` | Mechanism clearly fails and should trigger gate, rewrite, or rejection. |
| `borderline` | Needs user judgment; useful for training review questions. |

## Review Status

| Status | Meaning |
|---|---|
| `provisional` | Added by Codex/agent from reports or close reading; not yet confirmed by user. |
| `user_confirmed` | User accepted this case classification. May enter regression. |
| `user_rejected` | User rejected this classification; keep as a metric blind spot or discarded case. |

## Initial Failure IDs

### F001_shimamura_over_understanding

Shimamura catches more than surface terms and names Adachi's hidden wound too clearly.

- Gate signals: `deep_understanding: true`, Shimamura explanation markers, long causal Shimamura response, therapeutic phrasing.
- Gate action: `needs_manual_triage`; hard fail if paired with closure or direct explanation of the wound.
- Rewrite policy: shorten Shimamura response, keep surface-term reception, remove causal naming.
- Required case triplet:
  - positive: `F001_POS_001`
  - negative: `F001_NEG_001`
  - borderline: `F001_BORDER_001`

### F002_adachi_clean_self_analysis

Adachi's overload becomes clean causal self-analysis instead of failed transmission.

- Gate signals: long utterance has orderly explanation, repeated causal markers, low correction/hesitation, direct naming of the real wound.
- Gate action: `needs_manual_triage`; can become `failed_auto_gate` if the passage resolves the wound through explanation.
- Rewrite policy: keep pressure shape but add interruption, self-correction, displacement, and failed semantic transfer.
- Required case triplet:
  - positive: `F002_POS_001`
  - negative: `F002_NEG_001`
  - borderline: `F002_BORDER_001`

### F003_closure_after_care

Ordinary care is converted into mutual understanding or emotional resolution.

- Gate signals: closure terms near ending, promise of full understanding, relationship lesson, "now it is fine" ending.
- Gate action: `failed_auto_gate` when closure plus explanation is explicit; otherwise `needs_manual_triage`.
- Rewrite policy: keep temporary care, remove final lesson, leave residue or unresolved aftertaste.
- Required case triplet:
  - positive: `F003_POS_001`
  - negative: `F003_NEG_001`
  - borderline: `F003_BORDER_001`

### F004_pressure_without_failed_transmission

The candidate has intensity or long dialogue, but the pressure does not fail in transmission.

- Gate signals: high affect words without dialogue shape, long utterance reads like clean confession, Delta/segment pressure unsupported by close reading.
- Gate action: `needs_manual_triage`.
- Rewrite policy: preserve one long utterance, but make its surface less accurate than the hidden wound.
- Required case triplet:
  - positive: `F004_POS_001`
  - negative: `F004_NEG_001`
  - borderline: `F004_BORDER_001`

### F005_daily_buildup_missing

The candidate jumps to the phone/high-pressure scene without enough daily waiting, object/body carriers, or ordinary scene movement.

- Gate signals: short candidate, weak daily beats, missing object/body carriers, pressure segment dominates.
- Gate action: `needs_manual_triage`; hard fail if below full-candidate length threshold.
- Rewrite policy: add or repair only local daily buildup beats; do not invent new plot.
- Required case triplet:
  - positive: `F005_POS_001`
  - negative: `F005_NEG_001`
  - borderline: `F005_BORDER_001`

### F006_dialogue_shape_collapse

Dialogue distribution collapses into tiny call-and-response lines or lacks the required mid-length / overload shape.

- Gate signals: `short_dialogue_pct_1_10` too high, `mid_dialogue_pct_11_40` too low, no `dialogue_ge_200`, high distribution L1.
- Gate action: `needs_manual_triage`; hard fail when short-dialogue dominance violates config and no long overload exists.
- Rewrite policy: merge or lightly expand local dialogue lines; do not rewrite the whole candidate to chase bins.
- Required case triplet:
  - positive: `F006_POS_001`
  - negative: `F006_NEG_001`
  - borderline: `F006_BORDER_001`

### F008_dialogue_run_overextension

Dialogue continues as a long chain of question-answer turns instead of returning to Adachi's thought, body sensation, or object carrier after one or two exchanges.

- Gate signals: a contiguous dialogue run has an oversized `L[speaker]..R[speaker]` window for `adachi` or `shimamura`, or an oversized two-speaker alternating window; when one question-answer exchange is counted as one unit, the passage lacks intervening narration / inner response before the source-derived budget is exhausted.
- Budget source priority: `beat_source_alignment` > `source_slice_profile` > `chapter_profile_warning_only` > `missing_source_window_budget`.
- Gate action: if beat-level or slice-level source budget exists, use that budget for `needs_manual_triage` / hard exceed decisions; if only chapter-level weak profile exists, emit warning only; if no source or slice profile exists, emit `missing_source_window_budget` warning only.
- Rewrite policy: `beat_planner` owns the window budget; `dialogue_agent` writes the spoken surface within budget for both Adachi and Shimamura; `stream_agent` must reset the window with Adachi thought, body sensation, object carrier, delayed thought, or misread residue. Do not merely pad short replies.
- Required case triplet:
  - positive: `F008_POS_001`
  - negative: `F008_NEG_001`
  - borderline: `F008_BORDER_001`

### F007_delta_imitation_trap

Delta or segment diagnostics are treated as quality or copying targets instead of localization evidence.

- Gate signals: outputs claim "better because Delta", optimize for reference rank while ignoring user review, or try to copy source text / exclusive phrasing from Delta evidence.
- Gate action: process violation; mark report/candidate `needs_manual_triage`.
- Rewrite policy: no prose rewrite from Delta alone; translate only localized evidence into `rewrite_plan.json`.
- Required case triplet:
  - positive: `F007_POS_001`
  - negative: `F007_NEG_001`
  - borderline: `F007_BORDER_001`

### F009_originality_overconstraint

The prompt, gate, or agent review overprotects "originality" and suppresses the style transfer the harness is supposed to study.

- Gate signals: prompt says "original" or "do not imitate" as a dominant command; agent avoids source-like rhythm, translation texture, dialogue timing, or interior monologue shape because it treats style proximity as copying risk.
- Allowed target: mechanism-level and style-surface emulation is permitted and desired when it does not copy source text, long excerpts, exact scene structure, or exclusive phrasing.
- Gate action: `needs_manual_triage` for prompt/spec/review policy; not a prose-quality judgment by itself.
- Rewrite policy: remove anti-imitation language locally from the prompt/spec/review note; replace it with copying boundaries plus explicit style-mechanism targets.
- Required case triplet:
  - positive: `F009_POS_001`
  - negative: `F009_NEG_001`
  - borderline: `F009_BORDER_001`

## Next Work

Populate `analysis/failure_cases.json` with provisional case triplets for each failure id, then promote only user-confirmed cases into regression.
