# Candidate JSON Reference

Use paired JSON so the harness can evaluate speaker roles and response structure without forcing screenplay formatting into the Markdown draft.

## Minimal Schema

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
      "deep_understanding": false,
      "explanation_markers": []
    }
  ],
  "scene_beats": [
    {
      "id": "b001",
      "type": "daily_waiting",
      "summary": "回家、手机、房间、等待"
    }
  ],
  "revision_notes": [
    {
      "source": "generator",
      "note": "本候选把重点放在日常等待而不是只写电话爆发。"
    }
  ]
}
```

## Speaker Values

Use lowercase stable values:

- `adachi`
- `shimamura`
- `tarumi`
- `narration`
- `other`

## Shimamura Fields

For Shimamura utterances, include:

- `responds_to`: utterance IDs she is responding to.
- `surface_terms_received`: words she appears to catch literally.
- `deep_understanding`: `true` only if the line shows she understands Adachi's hidden wound.
- `explanation_markers`: causal or explanatory markers present in the line.

`deep_understanding: true` should usually lead to manual triage. It may be a hard failure if paired with closure or explicit emotional promise.

## Scene Beat Types

Recommended first values:

- `festival_afterimage`
- `walk_home`
- `daily_waiting`
- `phone_overload`
- `surface_response`
- `temporary_care`
- `unresolved_ending`

## Consistency Rules

- Every quoted dialogue line in Markdown should have an `utterances` entry unless the line is intentionally ambiguous.
- Do not add interpretive claims to JSON that the Markdown draft does not support.
- JSON is for harness decisions, not for replacing user review.
