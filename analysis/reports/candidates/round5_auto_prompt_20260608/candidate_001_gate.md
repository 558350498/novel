# Harness Gate Report

- 候选：`drafts\candidates\round5_auto_prompt_20260608\candidate_001.md`
- 状态：`needs_manual_triage`
- 范围：`candidate`
- Style：`analysis\reports\candidates\round5_auto_prompt_20260608\candidate_001_style.md`
- Delta：`analysis\reports\candidates\round5_auto_prompt_20260608\candidate_001_delta.md`

## 自动信号

- `char_count`: 6423
- `evaluation_scope`: candidate
- `dialogue_ratio`: 0.34763948497854075
- `max_dialogue_len`: 557
- `dialogue_ge_200`: 1
- `short_dialogue_pct_1_10`: 61.73
- `mid_dialogue_pct_11_40`: 37.04
- `dialogue_distribution_l1`: 50.62

## Candidate JSON

- path: `drafts\candidates\round5_auto_prompt_20260608\candidate_001.json`
- adachi_max_len: 557
- adachi_ge_long_threshold: 1
- shimamura_utterance_count: 41
- shimamura_avg_len: 9.76
- shimamura_surface_terms: 一直盯, 下午, 人很多, 人挤, 什么都可以, 刚才没有, 到家, 哪里都可以, 喝什么, 声音小, 太快, 学校附近

## Hard Fail Reasons

- 无

## Manual Triage Reasons

- Delta 第一名为 adachi_daily，不是 adachi_pressure

## Suppressed Heuristic Reasons

- 无

## 边界

- Harness 只筛掉明显失败样本，不判定成功。
- 通过 gate 的候选最多进入 `pending_user_review`。
- 最终定性必须等待用户 review。
