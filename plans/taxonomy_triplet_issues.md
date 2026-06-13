# Taxonomy Triplet Issue Queue

This local issue queue mirrors GitHub Issues until the repo-native issue flow is available.

Scope: failure ids still listed in `analysis/failure_cases.json` under `missing_case_triplets`.

Goal: turn protocol-strong taxonomy entries into regression-ready case anchors without doing all case-writing in one pass.

Completion rule: close one local issue only when its failure id has positive, negative, and borderline entries in `analysis/failure_cases.json`, evidence refs resolve, and the id is removed from `missing_case_triplets`.

## Queue

| Local Issue | Failure ID | Type | Blocked By | Status |
|---|---|---|---|---|
| `TRIPLET-F001` | `F001_shimamura_over_understanding` | AFK | None | open |
| `TRIPLET-F002` | `F002_adachi_clean_self_analysis` | AFK | None | open |
| `TRIPLET-F003` | `F003_closure_after_care` | AFK | None | open |
| `TRIPLET-F004` | `F004_pressure_without_failed_transmission` | AFK | None | open |
| `TRIPLET-F005` | `F005_daily_buildup_missing` | AFK | None | open |
| `TRIPLET-F007` | `F007_delta_imitation_trap` | HITL | None | open |

## Common Acceptance Checks

- [ ] `analysis/failure_cases.json` contains positive, negative, and borderline cases for the issue failure id.
- [ ] Every new case uses legal `case_type`, `source_type`, `expected_gate`, and `review_status` values.
- [ ] Every new case uses machine-checkable `evidence_refs`; fixture refs such as `tests/fixtures/failure_fixtures.json#/fixtures/<index>/cases/<type>/case_id` are valid for provisional anchors.
- [ ] `review_status` stays `provisional` unless a matching user ledger entry exists.
- [ ] The failure id is removed from `missing_case_triplets` only after the complete triplet is present.
- [ ] `python tools/schema_check.py` passes.
- [ ] `python tools/evidence_ref_check.py` passes.
- [ ] `python tools/project_ci.py --require-regression-review` passes.

## TRIPLET-F001: Add F001 Shimamura Over-Understanding Triplet

Type: AFK

Blocked by: None - can start immediately.

User story covered: a future agent can distinguish ordinary surface reception from Shimamura naming Adachi's hidden wound.

### What to Build

Add a complete provisional triplet for `F001_shimamura_over_understanding` to `analysis/failure_cases.json`.

Use the existing synthetic fixture as the minimum anchor. Add stronger candidate or agent-review evidence only if it can point to JSON/JSONL fields without quoting long prose.

### Acceptance Criteria

- [ ] Add `F001_POS_001`, `F001_NEG_001`, and `F001_BORDER_001` as case entries.
- [ ] The positive case preserves surface-term reception and no deep wound naming.
- [ ] The negative case captures Shimamura over-understanding or therapeutic naming.
- [ ] The borderline case captures partial emotional inference that still does not solve the wound.
- [ ] Remove `F001_shimamura_over_understanding` from `missing_case_triplets` after the triplet is complete.

### Non-Goals

- Do not mark any F001 case `user_confirmed` without a ledger entry.
- Do not rewrite the active candidate.
- Do not change gate thresholds unless a later issue is opened for that change.

## TRIPLET-F002: Add F002 Adachi Clean Self-Analysis Triplet

Type: AFK

Blocked by: None - can start immediately.

User story covered: a future agent can tell failed overload from a clean causal confession.

### What to Build

Add a complete provisional triplet for `F002_adachi_clean_self_analysis` to `analysis/failure_cases.json`.

Use the existing fixture as the minimum anchor. Candidate or agent-review evidence from the current run may be referenced if it stays diagnostic and does not become a user verdict.

### Acceptance Criteria

- [ ] Add `F002_POS_001`, `F002_NEG_001`, and `F002_BORDER_001` as case entries.
- [ ] The positive case keeps overload fragmented by object, body, interruption, or displacement.
- [ ] The negative case captures orderly causal explanation of the real wound.
- [ ] The borderline case captures a coherent self-report that is still interrupted or displaced enough to need review.
- [ ] Remove `F002_adachi_clean_self_analysis` from `missing_case_triplets` after the triplet is complete.

### Non-Goals

- Do not treat long Adachi utterance length alone as success.
- Do not promote agent close-reading claims into user-confirmed regression.
- Do not rewrite prompt policy in this issue.

## TRIPLET-F003: Add F003 Closure-After-Care Triplet

Type: AFK

Blocked by: None - can start immediately.

User story covered: a future agent can separate temporary ordinary care from emotional resolution.

### What to Build

Add a complete provisional triplet for `F003_closure_after_care` to `analysis/failure_cases.json`.

The triplet should make the ending-state distinction explicit: care may stop bleeding, but it must not solve the relationship wound.

### Acceptance Criteria

- [ ] Add `F003_POS_001`, `F003_NEG_001`, and `F003_BORDER_001` as case entries.
- [ ] The positive case preserves unresolved residue after ordinary care.
- [ ] The negative case captures explicit resolution, promise of understanding, or lesson-like closure.
- [ ] The borderline case captures heavy care pressure that still leaves the wound unresolved.
- [ ] Remove `F003_closure_after_care` from `missing_case_triplets` after the triplet is complete.

### Non-Goals

- Do not turn all care into failure; the kernel needs ordinary care.
- Do not add new closure vocabulary to gates without a separate evidence-backed issue.
- Do not change the active run status.

## TRIPLET-F004: Add F004 Pressure-Without-Failed-Transmission Triplet

Type: AFK

Blocked by: None - can start immediately.

User story covered: a future agent can distinguish emotional intensity from the specific failed-transmission mechanism.

### What to Build

Add a complete provisional triplet for `F004_pressure_without_failed_transmission` to `analysis/failure_cases.json`.

The triplet should anchor the difference between pressure existing and pressure failing through surface speech and partial reception.

### Acceptance Criteria

- [ ] Add `F004_POS_001`, `F004_NEG_001`, and `F004_BORDER_001` as case entries.
- [ ] The positive case contains pressure, failed outlet, and surface-level reception.
- [ ] The negative case captures affect-word intensity without failed transmission.
- [ ] The borderline case captures pressure with overly clear outlet or weak reception failure.
- [ ] Remove `F004_pressure_without_failed_transmission` from `missing_case_triplets` after the triplet is complete.

### Non-Goals

- Do not collapse F004 into F002; clean explanation and missing failed transmission may overlap but remain separate cases.
- Do not add a quality score.
- Do not require source-text quotation.

## TRIPLET-F005: Add F005 Daily-Buildup-Missing Triplet

Type: AFK

Blocked by: None - can start immediately.

User story covered: a future agent can see whether pressure is carried by daily scene movement before the high-pressure beat.

### What to Build

Add a complete provisional triplet for `F005_daily_buildup_missing` to `analysis/failure_cases.json`.

The triplet should focus on daily waiting, objects, body sensation, and ordinary scene movement as carriers, not decoration.

### Acceptance Criteria

- [ ] Add `F005_POS_001`, `F005_NEG_001`, and `F005_BORDER_001` as case entries.
- [ ] The positive case uses daily objects/body/waiting as pressure carriers.
- [ ] The negative case jumps into high pressure without daily buildup.
- [ ] The borderline case has daily objects that may be decorative rather than structurally carrying pressure.
- [ ] Remove `F005_daily_buildup_missing` from `missing_case_triplets` after the triplet is complete.

### Non-Goals

- Do not invent new plot requirements.
- Do not use candidate length alone as proof of daily buildup.
- Do not move generated run artifacts.

## TRIPLET-F007: Add F007 Delta-Imitation-Process Triplet

Type: HITL

Blocked by: None - can start immediately, but the taxonomy boundary may need user confirmation.

User story covered: a future agent can use Delta as localization evidence without treating Delta rank as a copying or quality target.

### What to Build

Clarify and complete `F007_delta_imitation_trap` in `analysis/failure_cases.json`.

The existing borderline case only observes `delta_first`; before adding the full triplet, verify that the negative case is a process violation, not merely a daily-first Delta result. If the work shows these are separate concepts, keep F007 missing and open a follow-up taxonomy-split issue.

### Acceptance Criteria

- [ ] Add `F007_POS_001`, `F007_NEG_001`, and `F007_BORDER_001` as case entries, or document why F007 must split before it can be completed.
- [ ] The positive case treats Delta as localization evidence only.
- [ ] The negative case captures using Delta to chase quality, source rank, copied texture, or exclusive phrasing.
- [ ] The borderline case keeps daily-first Delta as exploratory signal unless a process violation is present.
- [ ] Remove `F007_delta_imitation_trap` from `missing_case_triplets` only if the completed triplet keeps that boundary clean.

### Non-Goals

- Do not treat `delta_first != adachi_pressure` as a formal regression failure by itself.
- Do not use Delta as a quality score or author-similarity score.
- Do not make copying-boundary changes here; use the F009 prompt-policy path for that.
