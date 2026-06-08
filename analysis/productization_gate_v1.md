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

Do not use project gate labels as the base linguistic taxonomy.

Use the general taxonomy in `tools/lexicon_taxonomy.json`:

- `affect_intensity`
- `stance_uncertainty`
- `cognitive_explanation`
- `dialogic_alignment`
- `concrete_grounding`
- `closure_resolution`
- `prompt_boundary`

Then map combined signals back to project gate language such as explanation leakage, receiver misalignment, mundane object support, and closure risk.

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

## Explanation Gate

The explanation gate should split signals into three levels.

### Lexical Signals

Markers such as:

- `因为`
- `所以`
- `其实`
- `我的意思是`
- `我想说明`
- `你要理解`
- `我并不是`
- `我之所以`

These are weak signals alone. They become more important when attached to Shimamura utterances or the candidate ending.

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
6. Record user review as feedback ledger entries after each candidate pass.

## Non-Goals

- Do not support arbitrary kernel switching in v1.
- Do not make Delta a quality score.
- Do not require the Markdown draft to use explicit `岛村：` speaker labels.
- Do not let the structure JSON replace user review.
- Do not turn the gate into a final literary judge.
