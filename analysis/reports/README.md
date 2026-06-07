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
- `round3_style.md`：Round 3 规则型文本风格评估报告。
- `delta_round3.md`：Round 3 Delta v1 人类可读报告。
- `delta_round3.json`：Round 3 Delta v1 机器可读报告。
- `round3_pending_user_review.md`：Round 3 等待用户 review 的 provisional 自动信号说明。

## 使用原则

- `style_evaluator` 抓规则风险，例如直白情绪、结尾封闭、解释腔、日常物件不足。
- `diff.md` 记录人工发现的高级失败模式，例如分析泄漏、安达过度清醒、电话段错位不足。
- Delta v1 只做相对距离观察，不做质量评分，也不输出作者相似度百分比。
