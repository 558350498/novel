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
- `analysis/reports/README.md` for report roles.
- [project_architecture.md](references/project_architecture.md) if the project layout is unfamiliar.

Run the gate script after writing candidates:

```powershell
python skills/novel-gate-harness/scripts/run_candidate_gate.py --run-id <run_id> --candidates drafts/candidates/<run_id>/candidate_001.md
```

Use `--reports-root <path>` for smoke tests or temporary reports; omit it for normal project reports.

## Kernel

Keep the aesthetic kernel fixed:

> Emotional overload is real, but the spoken surface is lighter, smaller, displaced, or failed. Shimamura catches only surface terms, gives ordinary care, and temporarily stops the bleeding without truly solving the relationship.

Do not switch styles, authors, genres, or kernels in v1. Adjust only local variables such as daily buildup, phone overload, Shimamura response length, ambiguity, and ending openness.

## Workflow

1. Run `python skills/novel-gate-harness/scripts/run_candidate_gate.py --check-only` to verify the project has the required tools and configs.
2. Read the current prompt, status, source-shape report, and relevant candidate reports.
3. Generate or revise the Markdown fiction draft.
4. Generate the paired JSON structure file. See [candidate_json.md](references/candidate_json.md) when schema details are needed.
5. Run the gate script on the Markdown candidate.
6. Read `analysis/reports/candidates/<run_id>/manifest.json` and the candidate gate report.
7. Decide the next action:
   - `failed_auto_gate`: revise before user review.
   - `needs_manual_triage`: inspect the flagged risk and either revise or ask the user to review the exact uncertainty.
   - `pending_user_review`: present the candidate as ready for user review, not as successful.

## Generation Rules

- Keep the Markdown readable as fiction. Do not force `岛村：` speaker labels just to help tools.
- Put structure in JSON, not in the prose.
- Make Shimamura ordinary and non-therapeutic.
- Make Adachi's overload produce failed transmission, not clean self-analysis.
- Preserve daily buildup and object/body carriers; do not write only the phone climax.
- Keep the ending unresolved.

## Harness Decision Rules

Treat gate as a failure filter, never as a quality judge.

Prioritize explanation leakage:

- Shimamura accurately naming Adachi's real wound is a serious kernel violation.
- Shimamura using causal explanation markers may require `needs_manual_triage`.
- Closure plus explanation can be `failed_auto_gate`.

Do not optimize for Delta rank alone. Delta is a relative-distance observer, not a quality score or imitation target.

If the script or harness disagrees with close reading, preserve both signals and mark the issue as metric blind spot or manual triage. Do not overwrite the user's review path with automated confidence.

## Feedback Ledger

After user review, record the decision in the project docs or reports:

- What the user accepted or rejected.
- Which line, beat, or response caused the judgment.
- Whether the issue belongs in prompt, lexicon, gate config, corpus labels, or JSON schema.
- Whether the gate missed the problem or over-warned.

Do not leave important review decisions only in chat.
