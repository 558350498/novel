---
name: novel-gate-harness
description: Generate or revise single-kernel fiction candidates with paired Markdown and JSON structure, then run project gates before deciding the next draft action. Use when working in the novel style lab, creating candidates, tuning gate/harness behavior, or deciding whether a draft should be revised, triaged, or sent to user review.
---

# Novel Gate Harness

## Quick Start

Use this skill in `C:\Users\33625\Documents\novel` when generating or revising candidates for the fixed single-kernel project. If the current working directory is elsewhere, pass the project root explicitly to bundled scripts.

Produce paired artifacts:

```text
drafts/candidates/<run_id>/candidate_001.md
drafts/candidates/<run_id>/candidate_001.json
```

Before writing, read:

- `PROJECT_STATUS.md` for the current truth.
- `analysis/generation_prompt_round4.md` for the current long-candidate prompt.
- `analysis/reports/corpus_profile_adachi_pressure.md` for shape and taxonomy priors.
- `analysis/reports/source_chapter_shape.md` for the source chapter dialogue-length distribution.
- `analysis/reports/README.md` for report roles.
- [corpus_profile_gate.md](references/corpus_profile_gate.md) for the compressed gate-facing profile rules.
- [project_architecture.md](references/project_architecture.md) if the project layout is unfamiliar.

Run the gate script after writing candidates:

```powershell
python skills/novel-gate-harness/scripts/run_candidate_gate.py --run-id <run_id> --candidates drafts/candidates/<run_id>/candidate_001.md
```

For a short mechanism exercise rather than a full candidate, use fragment scope:

```powershell
python skills/novel-gate-harness/scripts/run_candidate_gate.py --run-id <run_id> --candidates drafts/candidates/<run_id>/candidate_001.md --scope fragment
```

Use `--reports-root <path>` for smoke tests or temporary reports; omit it for normal project reports.

## Kernel

Keep the aesthetic kernel fixed:

> Emotional overload is real, but the spoken surface is lighter, smaller, displaced, or failed. Shimamura catches only surface terms, gives ordinary care, and temporarily stops the bleeding without truly solving the relationship.

Do not switch styles, authors, genres, or kernels in v1. Adjust only local variables such as daily buildup, phone overload, Shimamura response length, ambiguity, and ending openness.

## Workflow

1. Run `python skills/novel-gate-harness/scripts/run_candidate_gate.py --check-only` to verify the project has the required tools and configs.
2. Read the current prompt, status, source-shape report, Corpus Profile report, and relevant candidate reports.
3. Generate or revise the Markdown fiction draft.
4. Generate the paired JSON structure file. See [candidate_json.md](references/candidate_json.md) when schema details are needed.
5. Run the gate script on the Markdown candidate. Use `--scope candidate` for full candidates and `--scope fragment` for local mechanism checks.
6. Read `analysis/reports/candidates/<run_id>/manifest.json` and the candidate gate report.
7. For full candidates, run the mandatory multi-agent review round before presenting the candidate to the user. A single all-purpose review agent is a process violation.
8. If the gate flags dialogue distribution problems, run one dialogue-distribution repair pass before asking for user review:
   - Keep the scene chain, first-person voice, unresolved ending, and the core Adachi overload utterance.
   - Do not rewrite the whole candidate only to chase bins.
   - Merge or lightly expand about 25-35 tiny call-and-response lines into natural `11-40` character utterances.
   - Prefer ordinary surface-level dialogue such as small questions, repeated confirmations, and care instructions.
   - Keep Shimamura non-therapeutic: she may catch terms such as "烟花", "樽见", "明天", "太快", "喉咙", or "手痛", but she must not name Adachi's hidden wound.
   - Update the paired JSON `utterances` after revising Markdown.
   - Run the gate again and report `short_dialogue_pct_1_10`, `mid_dialogue_pct_11_40`, `dialogue_distribution_l1`, and status.
9. Decide the next action:
   - `failed_auto_gate`: revise before user review.
   - `needs_manual_triage`: inspect the flagged risk and either revise or ask the user to review the exact uncertainty.
   - `pending_user_review`: present the candidate as ready for user review, not as successful.

## Generation Rules

- Keep the Markdown readable as fiction. Do not force `岛村：` speaker labels just to help tools.
- Put structure in JSON, not in the prose.
- Make Shimamura ordinary and non-therapeutic.
- Make Adachi's overload produce failed transmission, not clean self-analysis.
- Preserve daily buildup and object/body carriers; do not write only the phone climax.
- Prioritize overload shape over emotion words: the target signal is at least one truly long, failed-transmission utterance, not a pile of affect terms.
- Match the source chapter's dialogue-length distribution as a shape constraint, not just the single longest line. The current target chapter has about `48.3%` dialogue in `1-10` chars, about `48.3%` in `11-40` chars, and one extreme `321+` overload line; do not let generated dialogue collapse into mostly tiny call-and-response lines.
- Before running the gate, do a self-check against `analysis/reports/source_chapter_shape.md`: if `1-10` char dialogue is far above the source shape or `11-40` char dialogue is far below it, revise before presenting the candidate.
- Keep cognitive explanation low, especially in Shimamura responses and narrative summaries.
- Keep the ending unresolved.

## Harness Decision Rules

Treat gate as a failure filter, never as a quality judge.

Scope matters:

- `candidate`: full-candidate gate. The length threshold remains active.
- `fragment`: short passage exercise. The length threshold is skipped, but the report is only a local mechanism check and cannot prove that the full candidate is ready.

Prioritize explanation leakage:

- Shimamura accurately naming Adachi's real wound is a serious kernel violation.
- Shimamura using causal explanation markers may require `needs_manual_triage`.
- Closure plus explanation can be `failed_auto_gate`.

Do not optimize for Delta rank alone. Delta is a relative-distance observer, not a quality score or imitation target.

Use Corpus Profile as a prior, not a judge:

- Strong target signals: `shape.dialogue_ge_200` and `shape.dialogue_max`.
- Required distribution self-check: do not treat `shape.dialogue_ge_200` as sufficient when short dialogue is over-concentrated. Compare the candidate's bins against the source chapter bins and flag `needs_manual_triage` when `1-10` chars dominates or `11-40` chars collapses.
- Risk signal: high `cognitive_explanation`, especially if it makes the overload clean or lets Shimamura understand too much.
- Weak signal alone: `affect_intensity`; emotion words cannot substitute for dialogue shape.

If the script or harness disagrees with close reading, preserve both signals and mark the issue as metric blind spot or manual triage. Do not overwrite the user's review path with automated confidence.

## Mandatory Multi-Agent Review Round

Full candidates must pass through separate role-bounded agent reviews after the machine gate and before user review. Do not replace this with one combined "literary evaluation" agent.

Required roles for every full candidate:

- `agent_gate_auditor`: checks whether the machine gate report has evidence, span refs, false positives, false negatives, or missing candidate JSON signals.
- `agent_close_reader`: binds close-reading claims to `failure_id`, `case_id` when available, and exact spans; it may ask user-review questions but must not give a final pass/fail.

Required role when the prompt, model, gate config, JSON schema, or rewrite policy changed:

- `agent_regression_checker`: compares the candidate against confirmed cases and earlier runs, then reports which failure cases improved, stayed unresolved, or regressed.

Each agent review should write a structured note under:

```text
analysis/reports/candidates/<run_id>/agent_<role>.md
analysis/reports/candidates/<run_id>/agent_<role>.json
```

Agent review output must contain only structured evidence:

```text
role
scope
candidate_path
gate_report_path
claims[{failure_id, case_id, span_ref, claim, evidence_type, confidence}]
dissent[{against, reason, span_ref}]
recommended_user_questions[]
```

Forbidden in agent reviews:

- final `pass` or `fail` verdicts;
- broad claims such as "more flavorful", "closer to the original", or "better literary quality";
- ungrounded rewrites outside the active `rewrite_plan.json`;
- collapsing gate audit, close reading, and regression comparison into one agent.

If multi-agent tooling is unavailable, mark the candidate as `needs_manual_triage` with the reason `missing_multi_agent_review_round`; do not present it as ready for user review.

## Feedback Ledger

After user review, record the decision in the project docs or reports:

- What the user accepted or rejected.
- Which line, beat, or response caused the judgment.
- Whether the issue belongs in prompt, lexicon, gate config, corpus labels, or JSON schema.
- Whether the gate missed the problem or over-warned.

Do not leave important review decisions only in chat.
