# Harness Gate Report

- 候选：`drafts\candidates\round6_codex_full_loop_20260609\candidate_002.md`
- 状态：`needs_manual_triage`
- 范围：`candidate`
- Style：`analysis\reports\candidates\round6_codex_full_loop_20260609\candidate_002_style.md`
- Delta：`analysis\reports\candidates\round6_codex_full_loop_20260609\candidate_002_delta.md`

## 自动信号

- `char_count`: 6367
- `evaluation_scope`: candidate
- `dialogue_ratio`: 0.5789473684210527
- `max_dialogue_len`: 709
- `dialogue_ge_200`: 1
- `short_dialogue_pct_1_10`: 75.21
- `mid_dialogue_pct_11_40`: 23.97
- `dialogue_distribution_l1`: 78.94

## Candidate JSON

- path: `drafts\candidates\round6_codex_full_loop_20260609\candidate_002.json`
- adachi_max_len: 709
- adachi_ge_long_threshold: 1
- shimamura_utterance_count: 64
- shimamura_avg_len: 6.42
- shimamura_surface_terms: 下午, 不带, 不用, 创可贴, 到家, 卖完, 哪里, 哪里都可以, 喉咙, 喝水, 回去, 圆

## Hard Fail Reasons

- 无

## Manual Triage Reasons

- 台词分布偏短：1-10 字占比 75.2% 高于 第五卷 第二话「岛村之刃」 自检上限 65.0%
- 台词分布中段不足：11-40 字占比 24.0% 低于 第五卷 第二话「岛村之刃」 自检下限 30.0%
- 台词分布整体偏离：bins L1 偏差 78.9 高于 第五卷 第二话「岛村之刃」 自检上限 60.0
- Delta 第一名为 adachi_daily，不是 adachi_pressure

## Suppressed Heuristic Reasons

- 无

## 边界

- Harness 只筛掉明显失败样本，不判定成功。
- 通过 gate 的候选最多进入 `pending_user_review`。
- 最终定性必须等待用户 review。
