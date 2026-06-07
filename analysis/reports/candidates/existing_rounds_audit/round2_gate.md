# Harness Gate Report

- 候选：`drafts\round2.md`
- 状态：`failed_auto_gate`
- Style：`analysis\reports\candidates\existing_rounds_audit\round2_style.md`
- Delta：`analysis\reports\candidates\existing_rounds_audit\round2_delta.md`

## 自动信号

- `char_count`: 1633
- `dialogue_ratio`: 0.44954128440366975
- `max_dialogue_len`: 24
- `dialogue_ge_200`: 0
- `short_dialogue_pct_1_10`: 89.8

## Hard Fail Reasons

- 文本长度 1633 低于 hard gate 最小值 6000
- 过载长台词 为 RISK
- 短台词 1-10 字占比 89.8% 且无 >=200 字台词

## Manual Triage Reasons

- 对话占比 为 WARN
- 岛村回应解释化 为 WARN
- Delta 第一名为 adachi_daily，不是 adachi_pressure

## 边界

- Harness 只筛掉明显失败样本，不判定成功。
- 通过 gate 的候选最多进入 `pending_user_review`。
- 最终定性必须等待用户 review。
