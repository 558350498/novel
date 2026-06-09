# Harness Gate Report

- 候选：`drafts\candidates\round6_codex_full_loop_20260609\candidate_001.md`
- 状态：`failed_auto_gate`
- 范围：`candidate`
- Style：`analysis\reports\candidates\round6_codex_full_loop_20260609\candidate_001_style.md`
- Delta：`analysis\reports\candidates\round6_codex_full_loop_20260609\candidate_001_delta.md`

## 自动信号

- `char_count`: 5996
- `evaluation_scope`: candidate
- `dialogue_ratio`: 0.5789473684210527
- `max_dialogue_len`: 709
- `dialogue_ge_200`: 1
- `short_dialogue_pct_1_10`: 85.95
- `mid_dialogue_pct_11_40`: 13.22
- `dialogue_distribution_l1`: 75.3

## Candidate JSON

- path: `drafts\candidates\round6_codex_full_loop_20260609\candidate_001.json`
- adachi_max_len: 709
- adachi_ge_long_threshold: 1
- shimamura_utterance_count: 64
- shimamura_avg_len: 6.42
- shimamura_surface_terms: 下午, 不带, 不用, 创可贴, 到家, 卖完, 哪里, 哪里都可以, 喉咙, 喝水, 回去, 圆

## Hard Fail Reasons

- 文本长度 5996 低于 hard gate 最小值 6000
- 结尾封闭化 为 RISK

## Manual Triage Reasons

- 台词分布偏短：1-10 字占比 86.0% 高于 第五卷 第二话「岛村之刃」 自检上限 65.0%
- 台词分布中段不足：11-40 字占比 13.2% 低于 第五卷 第二话「岛村之刃」 自检下限 30.0%
- 台词分布整体偏离：bins L1 偏差 75.3 高于 第五卷 第二话「岛村之刃」 自检上限 60.0
- Delta 第一名为 adachi_daily，不是 adachi_pressure

## Suppressed Heuristic Reasons

- 无

## 边界

- Harness 只筛掉明显失败样本，不判定成功。
- 通过 gate 的候选最多进入 `pending_user_review`。
- 最终定性必须等待用户 review。
