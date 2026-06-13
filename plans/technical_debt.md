# Technical Debt

This list tracks repo-level debt, not candidate-specific prose problems.

## Highest Leverage

| Debt | Why It Matters | Preferred Shape |
|---|---|---|
| Incomplete case triplets for F001-F005 and F007 | Taxonomy entries without triplets are weaker regression anchors. | Add positive/negative/borderline cases with evidence refs, then require them in schema when ready. |
| Trend reporting is missing | Single-run diagnosis cannot show whether the harness is improving or drifting. | Generate a Markdown table from `analysis/reports/candidates/*/manifest.json` and ledger entries. |
| External report layer is not defined | Generated history still lives beside harness code. | Add a manifest-backed report layer before moving bulk artifacts. |
| Cleanup is review-only | The repo knows what may be stale, but does not automate archival decisions. | Keep deletion manual; automate stale summaries and archive proposals first. |
| GitHub surface is thin | Local docs carry most attention-routing work. | Convert stable plan items into issues and PRs once auth is available. |
| Commit history hygiene | Agent-readable history needs intentional messages, not file-list commits. | Use short purpose-first commits; keep accidental editor text out of history. |

## Guardrails

- Do not solve technical debt by broad refactors before a failing contract or issue exists.
- Do not introduce orchestration frameworks until local scripts can no longer express the workflow clearly.
- Keep Markdown as the human-readable view; keep JSON/JSONL as the machine contract.
- Keep evidence anchors in the main repository even when generated history moves out.
