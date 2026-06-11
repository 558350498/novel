# 分析产物目录

这里保存围绕「岛村之刃」的 durable 协议、gate 配置、审稿边界、语料分析和生成辅助文件。

当前目录按三层阅读：active protocol、supporting evidence、provenance/archive candidates。入口文件应只指向存在的当前路径；旧 round 如果只用于溯源，不再作为快速入口。

## Active Protocols

| Path | Role |
|---|---|
| `harness_config.json` | 当前 gate 配置和可执行阈值 |
| `harness_plan.md` | Harness v1 状态、范围和 review 边界 |
| `failure_taxonomy.md` | 可执行失败分类，不做泛化文学评论 |
| `failure_cases.json` | case registry scaffold，含 `case_id` 和 review 状态 |
| `gate_report_protocol.md` | gate report 字段、状态和证据规则 |
| `rewrite_plan_protocol.md` | 把诊断证据翻译成一次局部重写任务的协议 |
| `editing_actions.md` | 证据到局部改稿操作的动作目录 |
| `rewrite_policy.md` | 局部修复策略入口，schema 仍以 `rewrite_plan_protocol.md` 为准 |
| `review_ledger.jsonl` | 用户最终 review 判定 ledger |
| `regression_comparison.md` | prompt/model/gate/schema/rewrite policy 改动后的回归比较协议 |
| `productization_gate_v1.md` | Single-kernel tuning lab 产品边界 |
| `lexicon_taxonomy.md` | 泛化语言学 taxonomy，项目 gate 标签只是映射层 |
| `project_cleanup_plan.md` | active/provenance/archive/generated 清理策略 |

## Active Run

当前候选主线：

```text
drafts/candidates/round6_codex_full_loop_20260609/candidate_002.md
drafts/candidates/round6_codex_full_loop_20260609/candidate_002.json
-> analysis/reports/candidates/round6_codex_full_loop_20260609/candidate_002_gate.md/json
-> analysis/reports/candidates/round6_codex_full_loop_20260609/user_review_dialogue_window.md
```

当前状态：`needs_manual_triage`。

当前主要风险：

- 短台词 1-10 字占比偏高。
- 11-40 字中段台词占比不足。
- 台词分布整体偏离源切片自检范围。
- Delta 第一名为 `adachi_daily`，不是 `adachi_pressure`。

## Current Loop

当前项目主线是受控局部改稿，而不是继续堆 prompt 或黑箱分类器：

```text
candidate.md + candidate.json
-> gate + segment diagnosis
-> rewrite_plan.json
-> one controlled local rewrite
-> gate again
-> user review
```

`rewrite_plan.json` 是执行单，不是质量结论。诊断证据可以来自：

- `metric`: 长度、台词分布、解释标记、结构 JSON 统计。
- `segment_delta`: 片段级 daily/pressure/shimamura_view 相对距离。
- `agent_close_reading`: 指标无法覆盖的近读风险。
- `user_feedback`: 用户审稿结论，优先级最高。

## Tools

| Tool | Role |
|---|---|
| `../tools/project_doctor.py` | 检查 active 路径、候选配对和文档断链 |
| `../tools/project_ci.py` | 本地 CI contract：doctor、gate check、schema check、agent review contract、unit tests |
| `../tools/schema_check.py` | JSON contract 检查：candidate、rewrite plan、agent review、ledger、case registry |
| `../tools/agent_review_runner.py` | multi-agent review contract runner，不替代 agent 判断，只检查结构和禁区 |
| `../tools/style_evaluator.py` | 规则风险，例如解释泄漏、封闭结尾、接收端错位不足 |
| `../tools/delta_evaluator.py` | 相对距离观察，不做质量评分 |
| `../tools/eder_delta_evaluator.py` | 实验性片段级 Eder/Cosine Delta 诊断 |
| `../tools/dialogue_window_analyzer.py` | 对话窗口和接收端预算诊断 |
| `../tools/light_harness.py` | 聚合 style、Delta 和 candidate JSON，输出 gate |
| `../tools/source_shape_analyzer.py` | 章节级形状基线 |
| `../tools/corpus_tokenizer.py` | 语料 tokenization 与词表发现 |
| `../tools/corpus_profiler.py` | 语料 profile 与可解释特征权重，不做 RAG |

## Corpus And Profile Evidence

| Path | Role |
|---|---|
| `../corpus_slices/slices.json` | Delta reference slice 配置 |
| `reports/tokenization_vol05.md/json` | 第 5 卷整卷 tokenization 宽背景 |
| `reports/tokenization_vol05_shimamura_blade.md/json` | 「岛村之刃」核心切片 tokenization |
| `reports/tokenization_vol05_shimamura_blade_deepseek_v4_flash.md/json` | DeepSeek V4-Flash tokenizer 对照 |
| `reports/corpus_profile_adachi_pressure.md/json` | `adachi_pressure` 目标组 profile 权重 |

Corpus profile 和 tokenization 只辅助 gate 调参，不做 RAG，不召回原文片段，不替代人工 review。

## Skill References

| Path | Role |
|---|---|
| `../skills/novel-gate-harness/SKILL.md` | 顶层 Codex orchestration skill |
| `../skills/novel-gate-harness/references/project_architecture.md` | 目录角色与执行 pipeline |
| `../skills/novel-gate-harness/references/prompt_generation_harness.md` | 生成侧内部 harness |
| `../skills/novel-gate-harness/references/result_harness.md` | 结果侧内部 harness |
| `../skills/novel-gate-harness/references/editing_actions.md` | agent-facing editing action 摘要 |
| `../skills/novel-gate-harness/references/candidate_json.md` | paired candidate JSON 结构 |
| `../skills/novel-gate-harness/references/corpus_profile_gate.md` | gate-facing corpus profile 规则 |

## CI And Fixtures

本地 CI 入口：

```powershell
python tools/project_ci.py --require-regression-review
```

测试夹具入口：

```text
tests/fixtures/failure_fixtures.json
```

`failure_fixtures.json` 为每个 failure id 保留 positive / negative / borderline 最小边界样本；其中 F006 目前带 executable gate fixture，用于回归台词形状 gate 行为。其他 failure id 先作为 contract fixture，后续可以逐步升级成可执行 gate 或 analyzer fixture。

完整链路最小样例位于：

```text
demo/minimal_loop/
```

## Provenance

旧 prompt、早期草稿、早期 round 报告、重复 distribution-check 报告属于 provenance。它们可以解释路线如何形成，但不应放在当前入口的第一层。

清理、归档或删除前先看 `project_cleanup_plan.md`。不要删除源文本、用户确认记录、当前 candidate、当前 reports 或 skill source。

## Boundaries

- 不长篇摘录原文。
- 不复刻原文句式。
- 不复制作者专属表达；允许机制级、节奏级、翻译腔级的文风贴近。
- 不把 Delta、Segment Delta、corpus profile 或 rewrite plan 当作质量评分。
- 不让 harness、Codex 或 subagent 替代用户最终 review。
