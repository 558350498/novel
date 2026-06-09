# User Review: Originality Overconstraint

- date: 2026-06-10
- reviewer: user
- related_failure_id: `F009_originality_overconstraint`
- related_case_id: `F009_NEG_001`

## Verdict

The current prompt/review language overemphasizes originality. That can make agents avoid useful style transfer and become too conservative about imitating the source's rhythm, tone, dialogue timing, translation texture, and interior-monologue shape.

## Policy Change

Do not use "original" or "do not imitate" as dominant generation commands.

Keep these boundaries:

- do not copy source text;
- do not quote long source excerpts;
- do not trace exact source paragraph or scene structure;
- do not lift exclusive phrasing.

Preserve these targets:

- mechanism-level style emulation;
- source-like rhythm and pauses;
- light-novel translation texture;
- dialogue timing and length distribution;
- Adachi interior drift and correction loops;
- Shimamura surface-level receiving cadence.
