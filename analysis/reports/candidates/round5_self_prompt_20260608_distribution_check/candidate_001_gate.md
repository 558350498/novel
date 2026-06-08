# Harness Gate Report

- 候选：`drafts\candidates\round5_self_prompt_20260608\candidate_001.md`
- 状态：`needs_manual_triage`
- 范围：`candidate`
- Style：`analysis\reports\candidates\round5_self_prompt_20260608_distribution_check\candidate_001_style.md`
- Delta：`analysis\reports\candidates\round5_self_prompt_20260608_distribution_check\candidate_001_delta.md`

## 自动信号

- `char_count`: 6645
- `evaluation_scope`: candidate
- `dialogue_ratio`: 0.41254125412541254
- `max_dialogue_len`: 766
- `dialogue_ge_200`: 1
- `short_dialogue_pct_1_10`: 89.6
- `mid_dialogue_pct_11_40`: 9.6
- `dialogue_distribution_l1`: 82.6

## Candidate JSON

- path: `drafts\candidates\round5_self_prompt_20260608\candidate_001.json`
- adachi_max_len: 766
- adachi_ge_long_threshold: 1
- shimamura_utterance_count: 22
- shimamura_avg_len: 7.0
- shimamura_surface_terms: 吵, 喉咙, 在家, 外面, 太吵, 太快, 学校, 家, 小测, 手, 手痛, 明天

## Hard Fail Reasons

- 无

## Manual Triage Reasons

- 台词分布偏短：1-10 字占比 89.6% 高于 第五卷 第二话「岛村之刃」 自检上限 65.0%
- 台词分布中段不足：11-40 字占比 9.6% 低于 第五卷 第二话「岛村之刃」 自检下限 30.0%
- 台词分布整体偏离：bins L1 偏差 82.6 高于 第五卷 第二话「岛村之刃」 自检上限 60.0
- Delta 第一名为 adachi_daily，不是 adachi_pressure

## Suppressed Heuristic Reasons

- 使用 JSON 岛村 utterance 结构替代 Markdown 说话人格式 WARN

## 边界

- Harness 只筛掉明显失败样本，不判定成功。
- 通过 gate 的候选最多进入 `pending_user_review`。
- 最终定性必须等待用户 review。
