# Harness Gate Report

- 候选：`drafts\round3.md`
- 状态：`failed_auto_gate`
- Style：`analysis\reports\candidates\existing_rounds_audit\round3_style.md`
- Delta：`analysis\reports\candidates\existing_rounds_audit\round3_delta.md`

## 自动信号

- `char_count`: 1963
- `dialogue_ratio`: 0.425
- `max_dialogue_len`: 577
- `dialogue_ge_200`: 1
- `short_dialogue_pct_1_10`: 82.35

## Hard Fail Reasons

- 文本长度 1963 低于 hard gate 最小值 6000

## Manual Triage Reasons

- 对话占比 为 WARN
- 岛村回应解释化 为 WARN
- Delta 第一名为 adachi_daily，不是 adachi_pressure

## 边界

- Harness 只筛掉明显失败样本，不判定成功。
- 通过 gate 的候选最多进入 `pending_user_review`。
- 最终定性必须等待用户 review。
