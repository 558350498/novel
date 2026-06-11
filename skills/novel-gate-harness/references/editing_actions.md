# Editing Actions Reference

This is the agent-facing summary of project editing actions.

Source of truth: `analysis/editing_actions.md`.

Use this reference when creating a prompt, candidate spec, rewrite plan, or local rewrite. Do not treat editing actions as aesthetic verdicts. They only say what operation is allowed, why it is allowed, what must not be broken, and how the result will be checked.

## Rule

Never convert a source image or metric into a fixed symbol or quality score.

Use this flow:

```text
diagnostic evidence
-> editing action
-> rewrite_plan.json
-> one local rewrite
-> gate / review
```

Do not use:

```text
metric is bad
-> make it more like the source
```

## Current Actions

| action_id | Use when | Do not do |
|---|---|---|
| `reset_dialogue_window` | dialogue runs continue too long before thought/body/object reset | pad dialogue or add plot |
| `repair_dialogue_length_distribution` | tiny Q/A lines dominate and mid-length dialogue is missing | chase bins by filler |
| `intensify_failed_transmission` | target pressure beat reads as daily or clean explanation | copy source phrasing or add direct confession |
| `preserve_surface_receipt` | Shimamura understands too much or closes the wound | make ordinary care therapeutic |
| `relax_originality_boundary` | prompt/review policy overprotects originality | remove copying boundaries entirely |
| `reduce_imagery_overfit` | prompt/candidate repeats source-derived images mechanically | turn images into fixed symbols |

## How To Use In A Rewrite Plan

When translating diagnostics into `rewrite_plan.json`, write the selected action into the agent-layer task or risk notes:

```json
{
  "source": "agent_close_reading",
  "claim": "Use editing_action: reset_dialogue_window. The phone exchange exceeds the source-aligned dialogue-window budget."
}
```

The rewrite task should include:

- the action id;
- the local target beat or segment;
- allowed moves;
- forbidden moves;
- verification signal.

## Action Details

### `reset_dialogue_window`

Insert Adachi thought, body sensation, object carrier, delayed thought, or misread residue before a dialogue chain exceeds its budget.

Verification: rerun dialogue-window analysis or gate evidence; avoid new explanation leakage.

### `repair_dialogue_length_distribution`

Merge or expand local tiny dialogue lines into more mid-length utterances while keeping the response ordinary.

Verification: dialogue bins improve; do not turn care into explanation.

### `intensify_failed_transmission`

Repair a pressure beat by adding self-correction, interruption, failed repetition, displacement, or body/object interruption.

Verification: the beat no longer reads as clean causal self-analysis; do not optimize for Delta score.

### `preserve_surface_receipt`

Keep Shimamura's response at the level of surface terms, concrete care, and unresolved residue.

Verification: candidate JSON has `surface_terms_received`, no `deep_understanding`, and no new closure risk.

### `relax_originality_boundary`

Replace dominant anti-imitation language with narrow copying boundaries and explicit style-mechanism targets.

Verification: F009 policy evidence remains visible; no source-copying instruction is introduced.

### `reduce_imagery_overfit`

Turn repeated source-derived images or prompt anchors into local functional roles such as object carrier, body delay, or misread residue.

Verification: candidate repetitions carry distinct local functions; no fixed-symbol explanation or mechanical checkbox behavior.
