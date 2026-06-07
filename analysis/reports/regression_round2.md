# Round 1 -> Round 2 回归分析

用途：判断 Delta v1 是否能跟人工 review 的方向产生可解释的同向变化。本报告根据用户 review 修正 Round 2 定性，不调参。

## 输入

| 项目 | Round 1 | Round 2 |
|---|---|---|
| 草稿 | `drafts/current.md` | `drafts/round2.md` |
| 规则报告 | `analysis/reports/current.md` | `analysis/reports/round2_style.md` |
| Delta 报告 | `analysis/reports/delta_current.md` | `analysis/reports/delta_round2.md` |
| 人工 review | `analysis/reports/diff.md` | `analysis/reports/round2_review.md` |

## 人工回归结论

人工判断：Round 2 失败，不是有效改进。

原因：

- Round 2 把“岛村只能听到断续声音”误写成“安达自己只说短句碎片”。
- 过载时应出现长篇、快速、混乱的输出，而不是一问一答式短对话。
- 语义错位应发生在接收端：安达大量输出，岛村只能抓到零散表层词。
- Round 2 虽然减少了分析概念泄漏，但核心机制方向错了。

## 规则评估对比

| 指标 | Round 1 | Round 2 | 变化 |
|---|---:|---:|---|
| 字符数 | 1778 | 1633 | 略短 |
| 段落数 | 68 | 109 | 明显增加 |
| 对话占比 | 39.7% | 45.0% | 升高到 WARN |
| 情绪表达直白度 | 0.00/千字 | 0.00/千字 | 持平 |
| 含混与自我修正 | 45.56/千字 | 49.60/千字 | 略升 |
| 日常物件承载 | 23.06/千字 | 18.37/千字 | 下降但仍 OK |
| 结尾封闭化 | OK | OK | 持平 |
| 过度文学化风险 | OK | OK | 持平 |

解释：规则评估捕捉到了 Round 2 对话占比升高，但没有直接判断“过载输出是否应为长篇失控发话”。

## Delta 对比

| 参照组 | Round 1 Delta | Round 2 Delta | 变化 |
|---|---:|---:|---:|
| `adachi_daily` | 0.242134 | 0.279374 | +0.037240 |
| `shimamura_view` | 0.280171 | 0.310551 | +0.030380 |
| `adachi_pressure` | 0.332526 | 0.384257 | +0.051731 |
| `analysis_docs` | 0.388067 | 0.430674 | +0.042607 |

排序没有变化：

1. `adachi_daily`
2. `shimamura_view`
3. `adachi_pressure`
4. `analysis_docs`

句长变化：

| 指标 | Round 1 | Round 2 |
|---|---:|---:|
| 平均句长 | 11.03 | 7.59 |
| 中位句长 | 9.00 | 6.00 |
| P90 句长 | 21.00 | 14.00 |

## Delta 工程意义判断

本次结果判定为：**Delta 报警有效**。

Delta 没有证明 Round 2 更好；相反，它正确暴露了 Round 2 的表层方向错误：

- Round 2 到所有参照组的距离都变远。
- Round 2 到 `adachi_pressure` 变远最多。
- Round 2 的平均句长、中位句长和 P90 句长都显著低于 Round 1，也明显低于 `adachi_pressure`。
- 这与用户 review 一致：Round 2 把过载误写成短碎，而核心段需要长篇失控输出。

因此，Delta v1 当前的工程意义不是“判断机制是否成功”，而是“报警表层形态是否偏离参照组”。本次它成功报警。

## 修正后的结论

Round 2 作为草稿失败，但作为回归实验有价值：

- 它暴露了 Codex 对 `diff.md` 的错误理解。
- 它验证了 Delta v1 的一个有效用途：发现过度短碎化和表层漂移。
- 下一版不应继续压短句子，而应写“长篇失控输出 + 接收端断续理解”。

## 未来流程规则

以后任何新版草稿必须先进入 `pending user review` 状态：

- Codex 可以写 provisional review，但不能自行判定“新版更好”。
- 回归报告中的最终人工结论必须等用户 review 后再写入。
- Delta 结论只能作为证据，不能替代用户 review。
