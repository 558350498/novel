# 报告目录

这里保存生成稿评估、人工 review、差异讨论和后续 Delta 报告。

## 当前文件

- `current.md`：`tools/style_evaluator.py` 对 `drafts/current.md` 的规则型评估报告。
- `codex_review.md`：Codex 基于 `analysis/review_checklist.md` 写的第一轮人工 review。
- `diff.md`：用户与 Codex 对第一轮稿件问题句、GPT 化倾向、安达过载表达的讨论记录。
- `delta_current.md`：Delta v1 人类可读报告。
- `delta_current.json`：Delta v1 机器可读报告。
- `round2_style.md`：Round 2 规则型文本风格评估报告。
- `delta_round2.md`：Round 2 Delta v1 人类可读报告。
- `delta_round2.json`：Round 2 Delta v1 机器可读报告。
- `round2_review.md`：Round 2 人工 review。
- `regression_round2.md`：Round 1 到 Round 2 的同场景回归分析。
- `source_shape_stats.md`：原著参照切片、Round 1、Round 2 的形状统计报告。
- `source_chapter_shape.md`：全篇章形状统计报告，包含第五卷第二话 8311 字与 Round 3 1963 字对照。
- `source_chapter_shape.json`：全篇章形状统计机器可读报告。
- `round3_style.md`：Round 3 规则型文本风格评估报告。
- `delta_round3.md`：Round 3 Delta v1 人类可读报告。
- `delta_round3.json`：Round 3 Delta v1 机器可读报告。
- `round3_pending_user_review.md`：Round 3 等待用户 review 的 provisional 自动信号说明。
- `round3_full_arc_analysis.md`：Round 3 全场景链路形状分析，记录篇幅过短与日常段不足风险。
- `tokenization_vol05.md/json`：第 5 卷整卷 tokenization 报告，用于宽背景词表发现。
- `tokenization_vol05_shimamura_blade.md/json`：「岛村之刃」核心切片 tokenization 报告，用于当前 kernel 词表发现。
- `tokenization_vol05_shimamura_blade_deepseek_v4_flash.md/json`：「岛村之刃」核心切片的 DeepSeek V4-Flash tokenizer 对照报告。
- `corpus_profile_adachi_pressure.md/json`：以 `adachi_pressure` 为目标组的可解释语料 profile 权重报告。
- `candidates/existing_rounds_audit/`：Harness v1 对 Round 1 / Round 2 / Round 3 的回看报告。

## 使用原则

- `style_evaluator` 抓规则风险，例如直白情绪、结尾封闭、解释腔、日常物件不足。
- `diff.md` 记录人工发现的高级失败模式，例如分析泄漏、安达过度清醒、电话段错位不足。
- Delta v1 只做相对距离观察，不做质量评分，也不输出作者相似度百分比。
- Harness gate 报告只筛掉明显失败样本，不判定候选成功。
- 通过 gate 的候选只能进入 `pending_user_review`，最终结论等待用户 review。
- Tokenization 报告只做词表种子发现，不能直接把高频词当成 gate 规则。
- Tokenization 报告优先按 `tools/lexicon_taxonomy.json` 的泛化分类汇总，再映射到当前项目 gate 标签。
- OpenAI `tiktoken` 可作为模型侧 tokenization 对照，但不作为中文语言学分词。
- Hugging Face/DeepSeek tokenizer 可作为模型侧 tokenization 对照；DeepSeek 写作表现不能从 tokenizer 单独推出。
- Corpus profile 用于辅助 gate 调参，不做 RAG，不检索原文片段，不判定质量。

## 后续候选报告目录

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
