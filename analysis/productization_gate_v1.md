# Gate v1 Productization Plan

## Product Position

This project is a single-kernel tuning lab for one work and one aesthetic direction.

The first product version should not support arbitrary style switching. It should help a high-participation creator and Codex iterate one stable aesthetic kernel until the gate, lexicon, corpus labels, prompts, and review notes become reliable.

Current kernel:

> A person is emotionally overloaded, but what they can say is lighter, smaller, more displaced, and less accurate than the real wound. The receiver catches only surface words, gives ordinary care, and temporarily stops the bleeding without truly solving the relationship.

## Gate Priority

Gate v1 is not a quality judge. It is the first product capability because it can reject obvious failures before user review.

The first gate priority is explanation leakage, especially Shimamura understanding Adachi too well.

This is higher priority than Delta calibration because Delta can easily pull the workflow back toward imitation. Gate should instead protect the project kernel:

- Adachi may speak too much, too fast, or too poorly.
- Shimamura should not become a therapist.
- Shimamura should not accurately name Adachi's hidden need.
- A candidate that explains the real wound too clearly should stop at `needs_manual_triage` or `failed_auto_gate`.

## Lexicon Taxonomy

Use `analysis/lexicon_taxonomy.md` as the source of truth for taxonomy granularity.

This productization plan should only consume mapped gate signals such as explanation leakage, receiver misalignment, mundane object support, and closure risk. Do not redefine taxonomy categories here.

## Candidate File Protocol

Candidates should use paired files:

```text
drafts/candidates/<run_id>/candidate_001.md
drafts/candidates/<run_id>/candidate_001.json
```

The Markdown file is the readable fiction draft.

The JSON file is the harness-readable structure layer. It is not displayed as prose and should not force the fiction draft into screenplay formatting.

## Structure JSON Goals

The first JSON version should only include fields needed for gate reliability:

```json
{
  "version": 1,
  "candidate": "candidate_001.md",
  "kernel_id": "adachi_misaligned_overload_v1",
  "utterances": [
    {
      "id": "u001",
      "speaker": "adachi",
      "text": "..."
    },
    {
      "id": "u002",
      "speaker": "shimamura",
      "text": "...",
      "responds_to": ["u001"],
      "surface_terms_received": ["樽见", "明天"],
      "deep_understanding": false
    }
  ],
  "scene_beats": [
    {
      "id": "b001",
      "type": "daily_waiting",
      "summary": "回家、手机、房间、等待"
    },
    {
      "id": "b002",
      "type": "phone_overload",
      "summary": "安达大量输出，岛村只接住表层词"
    }
  ]
}
```

The initial purpose is not perfect literary parsing. It is to stop the evaluator from guessing who said which line.

## Rewrite Plan Protocol

After candidate gate and segment diagnostics, the next product artifact is:

```text
drafts/candidates/<run_id>/rewrite_plan.json
```

The rewrite plan is an execution order for one local rewrite. It is not a rules database and not a review conclusion.

Rules and thresholds belong in `analysis/harness_config.json`.

The rewrite plan should record:

- deterministic evidence copied from gate and segment reports;
- the affected beat and segment ids;
- one rewrite intent;
- concrete `do` and `avoid` constraints;
- dialogue constraints for the current rewrite;
- conflicts between metric signals, segment Delta, agent close reading, and user feedback.

See `analysis/rewrite_plan_protocol.md` for the current schema.

## Diagnostic Source Priority

The product should keep diagnostic sources explicit:

```text
user_feedback > blocking_metric > segment_delta > agent_close_reading
```

Metric signals can block or trigger a rewrite. Segment Delta can localize where a candidate is too `daily` or where `pressure` appears. Agent close reading can add warnings, but it must not pretend to be a metric. User feedback is the final aesthetic authority.

## Explanation Gate

The explanation gate should split signals into three levels.

### Lexical Signals

These are `cognitive_explanation` candidates when they appear in the wrong role or location:

- `因为`
- `所以`
- `其实`
- `我的意思是`
- `我想说明`
- `你要理解`
- `我并不是`
- `我之所以`

These are weak signals alone. They become important when attached to Shimamura utterances, narrative summaries, or the candidate ending.

### Role Violation Signals

These are stronger than lexical hits:

- Shimamura names Adachi's real wound.
- Shimamura explains why Adachi is hurt.
- Shimamura promises emotional priority too clearly.
- Shimamura turns the phone scene into counseling.
- Adachi's overload becomes a clean causal self-analysis.

### Narrative Summary Signals

These are strongest near paragraph endings and candidate endings:

- The narrator explains the relationship mechanism.
- The text resolves the wound into a clear lesson.
- The ending converts temporary care into mutual understanding.

## Gate Status Rules

Recommended first rules:

- `failed_auto_gate`: explicit closure plus direct explanation of the real wound.
- `needs_manual_triage`: Shimamura utterance has explanation markers, high average length, or `deep_understanding: true`.
- `pending_user_review`: no hard failure, no major structure conflict, but still awaiting user review.

Passing the gate only means the candidate is worth reading. It never means the draft succeeded.

## Near-Term Implementation Order

1. Keep the current single aesthetic kernel fixed.
2. Add JSON companion files for new candidates.
3. Update `light_harness.py` to read optional candidate JSON when present.
4. Make Shimamura explanation checks use JSON utterances first.
5. Fall back to current text heuristics when JSON is missing.
6. Add segment-level Delta diagnostics for local daily/pressure localization.
7. Generate a deterministic `rewrite_plan.json` skeleton from gate and segment reports.
8. Let the agent layer translate that skeleton into one local rewrite task.
9. Record user review as feedback ledger entries after each candidate pass.

## Non-Goals

- Do not support arbitrary kernel switching in v1.
- Do not make Delta a quality score.
- Do not require the Markdown draft to use explicit `岛村：` speaker labels.
- Do not let the structure JSON replace user review.
- Do not let `rewrite_plan.json` replace user review.
- Do not hard-code literary action labels such as `extend_prewarm` as product-level enums.
- Do not turn the gate into a final literary judge.
