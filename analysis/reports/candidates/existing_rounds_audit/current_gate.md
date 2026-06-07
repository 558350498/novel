# Harness Gate Report

- 候选：`drafts\current.md`
- 状态：`failed_auto_gate`
- Style：`analysis\reports\candidates\existing_rounds_audit\current_style.md`
- Delta：`analysis\reports\candidates\existing_rounds_audit\current_delta.md`

## 自动信号

- `char_count`: 1804
- `dialogue_ratio`: 0.38235294117647056
- `max_dialogue_len`: 16
- `dialogue_ge_200`: 0
- `short_dialogue_pct_1_10`: 76.92

## Hard Fail Reasons

- 文本长度 1804 低于 hard gate 最小值 6000
- 过载长台词 为 RISK
- 分析概念泄漏 为 RISK
- 短台词 1-10 字占比 76.9% 且无 >=200 字台词

## Manual Triage Reasons

- 岛村回应解释化 为 WARN
- Delta 第一名为 adachi_daily，不是 adachi_pressure

## 边界

- Harness 只筛掉明显失败样本，不判定成功。
- 通过 gate 的候选最多进入 `pending_user_review`。
- 最终定性必须等待用户 review。
