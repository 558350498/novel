# Editing Actions

This file is the project source of truth for editing actions.

An editing action is not an aesthetic verdict and not a prompt phrase. It is an evidence-backed operation that tells an agent what it may change, why that change is allowed, what it must not break, and how the result will be checked.

Editing actions sit between diagnostics and prose:

```text
source/profile evidence
-> gate / report signal
-> editing action
-> rewrite_plan.json
-> local candidate change
-> gate / review / ledger
```

## Boundary

Editing actions may use source-derived evidence, but they must not turn source text into a copying library.

Allowed into an editing action:

- source slice id, report path, case id, failure id;
- profile or frequency signal;
- functional role such as `object_carrier`, `body_delay`, `surface_receipt`, or `dialogue_window_reset`;
- granularity alignment;
- allowed and forbidden moves;
- verification signals.

Not allowed:

- long source excerpts;
- exact source phrasing;
- required-symbol instructions such as "must repeatedly use this image";
- author-similarity scores;
- global instructions like "make it more like the source".

## Record Shape

The action vocabulary is still fluid, so this is not yet a hard JSON schema. Every action should still be documented with these fields:

| Field | Meaning |
|---|---|
| `action_id` | Stable id used in rewrite plans and agent notes. |
| `purpose` | What failure this action repairs. |
| `failure_ids` | Failure taxonomy ids this action can address. |
| `evidence_role` | `profile_hint`, `review_warning`, `rewrite_trigger`, or `blocking_metric`. |
| `source_basis` | Report paths, source slice ids, case ids, or ledger refs. |
| `trigger_signals` | Metrics, profile signals, agent notes, or user feedback that can activate the action. |
| `granularity` | Source and target level, e.g. source slice -> beat, dialogue run -> dialogue run. |
| `allowed_moves` | Specific local operations the agent may perform. |
| `forbidden_moves` | Operations that would game the metric or violate the kernel. |
| `verification` | Gate, JSON, report, or review signals used after the edit. |
| `promotion_state` | `provisional`, `case_aligned`, or `user_confirmed`. |

Frequency/profile signals start as `profile_hint`. They can become `review_warning` or `rewrite_trigger` only after user review, case alignment, and regression checks.

## Core Actions

### `reset_dialogue_window`

Purpose: repair overlong Q/A chains by returning to Adachi thought, body sensation, object carrier, delayed thought, or misread residue.

- Failure ids: `F008_dialogue_run_overextension`, sometimes `F006_dialogue_shape_collapse`.
- Evidence role: `rewrite_trigger` only when source-aligned or user-confirmed dialogue-window budget exists; otherwise `review_warning`.
- Source basis: `tools/dialogue_window_analyzer.py`, `analysis/harness_config.json`, user review entries for F008.
- Trigger signals:
  - dialogue window exceeds preferred or hard pair-unit budget;
  - dual alternating window runs too long;
  - user review confirms Q/A chain overextension.
- Granularity: source slice or beat profile -> local dialogue run.
- Allowed moves:
  - insert Adachi thought after one or two exchanges;
  - insert body sensation before the next spoken turn;
  - insert an ordinary object carrier;
  - split one long dialogue chain into smaller windows.
- Forbidden moves:
  - pad dialogue with filler;
  - let Shimamura explain Adachi's hidden wound;
  - add new plot only to break the window;
  - treat every source dialogue run as a fixed template.
- Verification:
  - dialogue-window report no longer exceeds the relevant budget;
  - candidate JSON still marks speaker and surface receipt correctly;
  - gate does not newly trigger closure or explanation leakage.
- Promotion state: `case_aligned`.

### `repair_dialogue_length_distribution`

Purpose: repair a candidate whose dialogue distribution collapses into tiny call-and-response lines or lacks mid-length utterances.

- Failure ids: `F006_dialogue_shape_collapse`.
- Evidence role: `rewrite_trigger` when full-candidate dialogue bins violate current gate config.
- Source basis: `analysis/harness_config.json`, gate reports, F006 cases.
- Trigger signals:
  - `short_dialogue_pct_1_10` too high;
  - `mid_dialogue_pct_11_40` too low;
  - dialogue distribution L1 exceeds threshold.
- Granularity: source slice distribution -> full candidate or target beat; not every utterance.
- Allowed moves:
  - merge adjacent tiny responses when the same speaker turn can naturally carry one surface function;
  - expand local utterances into 11-40 character lines when they still sound ordinary;
  - preserve at least one overload utterance if already present.
- Forbidden moves:
  - pad lines only to satisfy bins;
  - turn ordinary care into explanation;
  - rewrite the whole candidate to chase distribution.
- Verification:
  - gate report improves dialogue bins;
  - close reading still sees failed transmission rather than clean explanation.
- Promotion state: `case_aligned`.

### `intensify_failed_transmission`

Purpose: make pressure fail in transmission rather than become clean confession or tidy self-analysis.

- Failure ids: `F002_adachi_clean_self_analysis`, `F004_pressure_without_failed_transmission`, sometimes `F005_daily_buildup_missing`.
- Evidence role: `rewrite_trigger` only when a target beat is identified; otherwise `review_warning`.
- Source basis: gate report, segment Delta, agent close reading, user-confirmed cases.
- Trigger signals:
  - target pressure beat ranks closer to `adachi_daily` than expected;
  - long Adachi utterance reads as orderly explanation;
  - agent close reading flags clean causal self-analysis.
- Granularity: segment or beat -> local pressure beat.
- Allowed moves:
  - add self-correction, interruption, failed repetition, or displacement;
  - let an object/body carrier interrupt explanation before it completes;
  - make the surface wording smaller than the hidden wound.
- Forbidden moves:
  - copy source phrasing;
  - add direct confession;
  - optimize for Delta score;
  - make Shimamura understand the wound.
- Verification:
  - no new F001 / F003 risk;
  - Delta remains evidence, not a quality score;
  - user review decides final acceptability.
- Promotion state: `provisional`.

### `preserve_surface_receipt`

Purpose: keep Shimamura's response at the level of surface terms and ordinary care.

- Failure ids: `F001_shimamura_over_understanding`, `F003_closure_after_care`.
- Evidence role: `rewrite_trigger` when candidate JSON or style evaluator flags deep understanding or explanation markers.
- Source basis: candidate JSON, style evaluator, F001/F003 cases.
- Trigger signals:
  - `deep_understanding: true`;
  - Shimamura explanation markers;
  - receiver response names the hidden wound;
  - closure terms near ordinary care.
- Granularity: utterance or short dialogue window -> local response.
- Allowed moves:
  - shorten Shimamura's response;
  - retain concrete care;
  - mark only received surface terms in JSON;
  - keep unresolved residue after the response.
- Forbidden moves:
  - therapeutic interpretation;
  - mutual-understanding conclusion;
  - causal explanation of Adachi's hidden wound.
- Verification:
  - candidate JSON has `surface_terms_received`;
  - no `deep_understanding` ids;
  - closure gate does not newly fire.
- Promotion state: `case_aligned`.

### `relax_originality_boundary`

Purpose: prevent prompt or agent review policy from overprotecting originality and suppressing useful style-mechanism transfer.

- Failure ids: `F009_originality_overconstraint`.
- Evidence role: `rewrite_trigger` for prompt/spec/review policy; not a prose-quality judgment.
- Source basis: user review `ledger_20260610_originality_overconstraint`, F009 cases, prompt policy report.
- Trigger signals:
  - originality / anti-imitation language dominates the prompt or review note;
  - prompt forbids style proximity instead of only forbidding copying;
  - agent avoids rhythm, translation texture, dialogue timing, or interior-monologue shape.
- Granularity: prompt policy or agent review process -> prompt/spec/review note.
- Allowed moves:
  - narrow copying boundaries to no source text copying, no long excerpts, no exact phrasing, no scene tracing;
  - explicitly allow mechanism-level rhythm, texture, timing, and surface-style emulation.
- Forbidden moves:
  - remove copying boundaries entirely;
  - instruct the agent to imitate exact author wording;
  - use originality as a dominant generation objective.
- Verification:
  - prompt mode style evaluator does not over-detect unsafe imitation language;
  - F009 regression evidence remains visible;
  - user review owns final policy acceptance.
- Promotion state: `user_confirmed` for current negative case.

### `reduce_imagery_overfit`

Purpose: prevent source-derived images, objects, or keywords from becoming fixed symbols or mechanical prompt/candidate checkboxes.

- Failure ids: provisional; may become a new taxonomy entry if user-confirmed cases accumulate.
- Evidence role: starts as `profile_hint` or `review_warning`; can become `rewrite_trigger` only after case alignment.
- Source basis: corpus tokenizer/profile reports, prompt text, candidate text, user review.
- Trigger signals:
  - prompt repeats one image/keyword as a required anchor beyond its functional role;
  - candidate repeats that anchor without changing local function;
  - source-derived image is explained as a fixed symbol rather than used as a local object/body carrier.
- Granularity: prompt -> candidate echo, or source profile -> beat-level function.
- Allowed moves:
  - replace a repeated noun with a functional role such as object carrier or body delay;
  - vary the local function of repeated objects;
  - remove symbolic explanation while keeping ordinary physical action.
- Forbidden moves:
  - require the same source image to appear repeatedly;
  - explain an image as a fixed literary symbol;
  - mechanically swap in synonyms while preserving the same overfit role.
- Verification:
  - prompt keyword repetition decreases or becomes role-based;
  - candidate repetitions carry distinct local functions;
  - no source phrasing or exclusive imagery is copied.
- Promotion state: `provisional`.

## Delta-Triggered Actions

Delta may trigger rewrite only through a named action.

Valid:

```text
segment Delta says target pressure beat is closest to adachi_daily
-> F004 / F002 risk
-> intensify_failed_transmission
```

Invalid:

```text
Delta is low
-> make the draft more like the source
```

Delta triggers must name:

- sub-signal;
- failure id;
- source and target granularity;
- editing action;
- forbidden moves;
- regression checks.

## Promotion Path

Editing actions are promoted through:

```text
analysis/profile
-> agent proposal
-> user review
-> case alignment
-> regression check
-> gate config or rewrite trigger
```

Single observations remain `profile_hint` or `review_warning`. Do not promote them to `rewrite_trigger` without case evidence.
