# 报告目录

这里保存生成稿评估、agent review、人工 review、差异讨论和后续 Delta 报告。

## Current Active Route

当前活跃路线优先看：

```text
analysis/reports/candidates/round6_codex_full_loop_20260609/
```

当前候选源文件在：

```text
drafts/candidates/round6_codex_full_loop_20260609/
```

Latest gate state: `needs_manual_triage`.

## Current Run Reports

| Path | Role |
|---|---|
| `candidates/round6_codex_full_loop_20260609/manifest.json` | run summary and status counts |
| `candidates/round6_codex_full_loop_20260609/candidate_001_style.md/json` | original candidate style report |
| `candidates/round6_codex_full_loop_20260609/candidate_001_delta.md/json` | original candidate Delta report |
| `candidates/round6_codex_full_loop_20260609/candidate_001_gate.md/json` | original candidate gate report |
| `candidates/round6_codex_full_loop_20260609/candidate_002_style.md/json` | rewritten candidate style report |
| `candidates/round6_codex_full_loop_20260609/candidate_002_delta.md/json` | rewritten candidate Delta report |
| `candidates/round6_codex_full_loop_20260609/candidate_002_gate.md/json` | rewritten candidate gate report |
| `candidates/round6_codex_full_loop_20260609/candidate_002_dialogue_window.md/json` | dialogue-window diagnostic |
| `candidates/round6_codex_full_loop_20260609/agent_gate_auditor.md/json` | agent gate audit notes |
| `candidates/round6_codex_full_loop_20260609/agent_close_reader.md/json` | agent close-reading notes |
| `candidates/round6_codex_full_loop_20260609/agent_regression_checker.md/json` | agent regression notes |
| `candidates/round6_codex_full_loop_20260609/regression_comparison.md` | current run regression comparison |
| `candidates/round6_codex_full_loop_20260609/user_review_dialogue_window.md` | user-facing dialogue-window review |

Gate report 字段和状态语义见 `../gate_report_protocol.md`。报告只能筛选失败和定位风险，不能写最终成功结论。

后续如果生成新的 `rewrite_plan.json`，它应该放在对应 `drafts/candidates/<run_id>/`，报告目录只保留诊断证据。

## Prior Run Still Useful

| Path | Role |
|---|---|
| `candidates/round5_auto_prompt_20260608/` | previous automatic prompt candidate reports and segment Delta experiments |

Round 5 is useful provenance, but it is no longer the first active route.

## Corpus And Profile Reports

| Path | Role |
|---|---|
| `tokenization_vol05.md/json` | 第 5 卷整卷 tokenization，用于宽背景词表发现 |
| `tokenization_vol05_shimamura_blade.md/json` | 「岛村之刃」核心切片 tokenization |
| `tokenization_vol05_shimamura_blade_deepseek_v4_flash.md/json` | DeepSeek V4-Flash tokenizer 对照 |
| `corpus_profile_adachi_pressure.md/json` | 以 `adachi_pressure` 为目标组的 profile 权重 |
| `user_review_originality_overconstraint.md` | originality / overconstraint review note |

Tokenization 报告只做词表种子发现，不能直接把高频词当成 gate 规则。Corpus profile 用于辅助 gate 调参，不做 RAG，不检索原文片段，不判定质量。

## Report Principles

- `style_evaluator` 抓规则风险，例如直白情绪、结尾封闭、解释腔、日常物件不足。
- Delta v1 只做相对距离观察，不做质量评分，也不输出作者相似度百分比。
- Segment Delta 报告用于定位候选内部 daily/pressure 分布，不判定文本是否好看。
- Harness gate 报告只筛掉明显失败样本，不判定候选成功。
- 通过 gate 的候选只能进入 `pending_user_review`，最终结论等待用户 review。
- Agent review 只能记录 failure/risk/evidence/question，不能替代用户 verdict。
- 旧报告如果只用于 provenance，应在入口文档中降权。

## Expected Candidate Report Layout

Harness 候选报告使用：

```text
analysis/reports/candidates/<run_id>/candidate_001_style.md
analysis/reports/candidates/<run_id>/candidate_001_style.json
analysis/reports/candidates/<run_id>/candidate_001_delta.md
analysis/reports/candidates/<run_id>/candidate_001_delta.json
analysis/reports/candidates/<run_id>/candidate_001_gate.md
analysis/reports/candidates/<run_id>/candidate_001_gate.json
analysis/reports/candidates/<run_id>/manifest.json
```

`candidate_*_gate.md` 只记录自动 gate 状态和原因。允许状态为：

- `failed_auto_gate`
- `needs_manual_triage`
- `pending_user_review`

## Cleanup

清理候选见 `../project_cleanup_plan.md`。

推荐处理方式：

- 保留当前 run 的完整报告。
- 保留 profile、tokenization summary、用户 review、current candidate reports 等关键 evidence。
- 旧 round 报告可归档，避免占据入口目录。
- `.tokens.txt` 属于大型生成 token stream，确认后可删除或保持忽略状态。
