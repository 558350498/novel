# Corpus Profile Gate Rules

Load this reference when generating, revising, or triaging candidates with `$novel-gate-harness`.

Source report:

```text
analysis/reports/corpus_profile_adachi_pressure.md
analysis/reports/corpus_profile_adachi_pressure.json
```

## How to Use It

Use Corpus Profile as a prior for generation and triage. It helps decide what to look for before user review, but it does not judge quality or replace close reading.

Do not use it for RAG. Do not retrieve or quote source prose from it. Do not treat its weights as a success score.

## Current Priors

- The strongest `adachi_pressure` signals are `shape.dialogue_ge_200` and `shape.dialogue_max`.
- Long failed-transmission dialogue matters more than single emotion words.
- Dialogue distribution still matters: the target source chapter is not mostly tiny exchanges. Its dialogue bins are roughly `1-10`: `48.3%`, `11-40`: `48.3%`, `81-160`: `1.7%`, `321+`: `1.7%`.
- `cognitive_explanation` is lower in the target group than in comparison groups, so clean causal explanation is a risk.
- `affect_intensity` is slightly higher in the target group, but weaker than dialogue shape.
- `concrete_grounding` supports the scene, but object terms alone do not prove the candidate has the right shape.

## Generation Implications

- Include at least one long overload utterance that feels fast, tangled, self-correcting, and partly failed.
- Do not replace overload shape with many short emotional lines.
- Keep enough middle-length dialogue in the surrounding call. Avoid the lazy pattern where almost every line is `1-10` characters and the candidate relies on one long monologue to satisfy the gate.
- Treat dialogue-distribution repair as a line-shape pass, not a tokenizer pass. Tokenization can suggest local phrase seeds, but the gate checks parsed dialogue character-length bins.
- When short dialogue dominates, merge adjacent tiny utterances or expand them into ordinary `11-40` character lines. Do not inflate Shimamura into explanation or counseling.
- Do not let Adachi turn the overload into mature self-analysis.
- Do not let Shimamura explain the hidden wound; she should catch surface terms and provide ordinary care.
- Keep daily buildup and body/object carriers, but make them support the long pressure shape rather than substitute for it.

## Gate / Triage Implications

- If a candidate is long enough but lacks a long overload utterance, prefer `needs_manual_triage` or revision.
- If a candidate has the long overload line but its dialogue distribution is much shorter than the source shape, prefer `needs_manual_triage` and revise before user review.
- If a candidate has high affect words but no long pressure shape, treat it as a likely false positive.
- If `cognitive_explanation` appears in Shimamura lines, endings, or narrative summary, triage for explanation leakage.
- If Delta does not rank `adachi_pressure` first but the candidate has a credible long failed-transmission shape, preserve the conflict as a metric blind spot instead of auto-rejecting on Delta alone.
- If the profile signal and user reading conflict, user review wins and the profile should be noted as incomplete.
