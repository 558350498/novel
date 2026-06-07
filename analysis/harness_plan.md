# Lightweight Harness v1 Plan

用途：定义一个不依赖 LangChain 的轻量候选筛选流程。Harness 只筛掉明显失败样本，不判断文学质量，不替代用户 review。

## 目标

第一版 harness 先做“已有候选评分器”，不自动生成候选。

它读取候选草稿，统一运行现有评估工具，汇总 gate 结果，并把候选标记为三种状态之一：

- `failed_auto_gate`：自动指标已足够说明该候选不应进入用户 review。
- `needs_manual_triage`：自动指标冲突或不完整，需要人工先判断是否值得 review。
- `pending_user_review`：自动 gate 未发现硬失败，但最终定性仍等待用户 review。

通过 gate 不等于成功，只表示“可以交给用户 review”。

## 文件协议

候选草稿：

```text
drafts/candidates/<run_id>/candidate_001.md
drafts/candidates/<run_id>/candidate_002.md
drafts/candidates/<run_id>/candidate_003.md
```

候选报告：

```text
analysis/reports/candidates/<run_id>/candidate_001_style.md
analysis/reports/candidates/<run_id>/candidate_001_delta.md
analysis/reports/candidates/<run_id>/candidate_001_delta.json
analysis/reports/candidates/<run_id>/candidate_001_gate.md
analysis/reports/candidates/<run_id>/manifest.json
```

已实现入口：

```text
tools/light_harness.py
analysis/harness_config.json
```

## Harness v1 流程

1. 用户或 Codex/subagent 先把候选写入 `drafts/candidates/<run_id>/`。
2. Harness 对每个候选运行 `tools/style_evaluator.py --mode draft`。
3. Harness 对每个候选运行 `tools/delta_evaluator.py`。
4. Harness 解析 style / Delta 输出中的结构化信号。
5. Harness 写出每个候选的 gate 报告。
6. Harness 写出 `manifest.json`，汇总候选状态、报告路径和自动 gate 原因。

第一版不负责调用模型生成文本。

## Hard Fail

以下情况初版直接标记为 `failed_auto_gate`：

- `过载长台词` 为 `RISK`。
- `分析概念泄漏` 为 `RISK`。
- `结尾封闭化` 为 `RISK`。
- `接收端错位` 为 `RISK` 或没有有效命中。
- 台词长度分布明显短碎化：`1-10` 字台词占比过高，且没有 `>=200` 字台词。
- 草稿低于可信长度阈值。

这些 gate 只用于排除明显失败样本，不用于证明候选成功。

## Manual Triage

以下情况标记为 `needs_manual_triage`，不自动淘汰：

- `对话占比` 为 `WARN`。
- 未检测到 `岛村：` 这类显式说话人标记，导致岛村回应长度无法估算。
- Delta 排序没有把 `adachi_pressure` 放在第一。
- Delta 与 style 指标互相冲突。
- 候选在表层指标上接近参照组，但存在可能的“长解释冒充过载”风险。

Manual triage 的目标是决定候选是否值得进入用户 review，而不是给出最终质量判断。

## Pending User Review

候选只有在没有 hard fail、且没有必须先 triage 的严重冲突时，才能标记为 `pending_user_review`。

该状态表示：

- 可以交给用户阅读。
- Codex 可以写 provisional notes。
- 不能写最终回归结论。
- 不能宣布“这一版更好”。

## 永远留给用户

以下判断必须等待用户 review：

- 长台词到底像安达过载，还是清晰长解释。
- 岛村是否真的只接收到表层词。
- 是否仍有 GPT 化、太工整、太会写的问题。
- 轻小说口吻和轻微翻译腔是否成立。
- 樽见、岛村、安达的关系伦理是否被写歪。
- 结尾是否保留未解决感，而不是完成漂亮收束。
- Delta 与读感冲突时，是否记录为指标盲区。

## Subagent 分工

Subagent 可以承担：

- 候选生产者：按同一 prompt 生成不同候选。
- 盲读记录员：给出 provisional notes 和待用户确认的问题。
- 指标复核员：检查 harness 报告是否存在明显解析错误。

Subagent 不能承担：

- 最终裁判。
- 最终回归结论作者。
- 用户 review 的替代者。
- 绕过 gate 直接宣布候选成功。

## 设计边界

- 不引入 LangChain。
- 不实现长期 agent 记忆或任务队列。
- 不让 LLM 自行打总分。
- 不把 Delta 当质量分。
- 不把 hard gate 扩展成自动创作审美判断。
