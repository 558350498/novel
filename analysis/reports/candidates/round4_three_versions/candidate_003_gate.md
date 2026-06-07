# Harness Gate Report

- 候选：`drafts\candidates\round4_three_versions\candidate_003.md`
- 状态：`needs_manual_triage`
- Style：`analysis\reports\candidates\round4_three_versions\candidate_003_style.md`
- Delta：`analysis\reports\candidates\round4_three_versions\candidate_003_delta.md`

## 自动信号

- `char_count`: 6527
- `dialogue_ratio`: 0.26905829596412556
- `max_dialogue_len`: 778
- `dialogue_ge_200`: 1
- `short_dialogue_pct_1_10`: 78.33

## Hard Fail Reasons

- 无

## Manual Triage Reasons

- 岛村回应解释化 为 WARN
- Delta 第一名为 adachi_daily，不是 adachi_pressure

## 边界

- Harness 只筛掉明显失败样本，不判定成功。
- 通过 gate 的候选最多进入 `pending_user_review`。
- 最终定性必须等待用户 review。
