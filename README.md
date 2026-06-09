# Narrative Mechanism Failure Harness

这是一个面向中文原创短篇的叙事机制失败分析与约束 harness。

它不是小说 prompt 仓库，不是通用小说生成器，也不是文学质量裁判。项目目标是把一个固定叙事机制拆成可检查、可复盘、可回归的工程流程：生成候选、识别失败、局部修复、记录用户判断，再用这些判断约束下一轮。

## Project Shape

v1 只服务一个 fixed kernel：

> 情绪过载真实存在，但说出口的表层更轻、更小、更错位、更失败；接收者只接住表层词，给出普通照顾，暂时止血，但不真正解决关系伤口。

当前主线：

```text
candidate.md + candidate.json
-> machine gate + diagnostics
-> mandatory multi-agent review
-> rewrite_plan.json
-> one local rewrite only
-> regression comparison
-> user review
-> review ledger
```

自动化只能筛掉明显失败和定位风险。最终 pass/fail 只能来自用户 review。

## Hard Artifacts

这个项目的门面产物不是 prompt，而是下面这组 harness artifact：

| Artifact | Purpose | Current home |
|---|---|---|
| Failure taxonomy | 可执行失败分类，避免滑成泛化文学评论 | `analysis/failure_taxonomy.md` |
| Case registry | 每个机制绑定 positive / negative / borderline case，并带 `case_id` 溯源 | `analysis/failure_cases.json` |
| Gate report | 每次候选输出具体失败点、指标、证据路径 | `analysis/gate_report_protocol.md`, `analysis/reports/candidates/<run_id>/` |
| Rewrite policy | 失败后只允许证据约束下的一次局部修复 | `analysis/rewrite_policy.md`, `analysis/rewrite_plan_protocol.md` |
| Review ledger | 用户最终判断 `pass/fail/why`，沉淀审美回归记录 | `analysis/review_ledger.jsonl` |
| Regression comparison | prompt / model / gate 改动后检查旧 case 是否退化 | `analysis/regression_comparison.md` |

硬规则：

- 没有 `case_id` 的失败分类不能进入正式 taxonomy。
- 没有 positive / negative / borderline 三件套的机制只能算 provisional。
- 正式 regression 只收 `user_confirmed` case。
- Agent 可以参与评估，但不能替代用户判定。

## Candidate Protocol

完整候选必须成对提交：

```text
drafts/candidates/<run_id>/candidate_001.md
drafts/candidates/<run_id>/candidate_001.json
```

`candidate_001.md` 给人读，保持小说自然形态。

`candidate_001.json` 给 harness 读，记录 speaker、utterance、response relation、surface terms、deep understanding risk、scene beats 等结构信号，避免 gate 从 prose 格式里猜角色关系。

短片段练习可以用 fragment scope，但 fragment 只能验证局部机制，不能证明完整候选 ready。

## Gate And Review Flow

1. 生成或修改 paired candidate。
2. 运行 machine gate。
3. `failed_auto_gate` 直接停止，不进入用户 review。
4. `needs_manual_triage` 必须检查具体风险，不能包装成成功。
5. full candidate 在给用户前必须跑多角色 agent review：
   - `agent_gate_auditor`
   - `agent_close_reader`
   - `agent_regression_checker`，当 prompt、model、gate config、JSON schema 或 rewrite policy 变化时必跑
6. Agent review 只能输出 `failure_id`、`case_id`、`span_ref`、claim、dissent、user question，不能写综合文学总评。
7. 如需修复，只能通过 `rewrite_plan.json` 做一次局部改稿。
8. 重跑 gate 后停在 `failed_auto_gate`、`needs_manual_triage` 或 `pending_user_review`。
9. 用户 review 后，把判定和原因写入 ledger。

如果无法完成 mandatory multi-agent review，full candidate 必须标记为 `needs_manual_triage: missing_multi_agent_review_round`。

## Commands

检查 harness 环境：

```powershell
python skills/novel-gate-harness/scripts/run_candidate_gate.py --check-only
```

检查完整候选：

```powershell
python skills/novel-gate-harness/scripts/run_candidate_gate.py --run-id <run_id> --candidates drafts/candidates/<run_id>/candidate_001.md
```

检查短片段机制：

```powershell
python skills/novel-gate-harness/scripts/run_candidate_gate.py --run-id <run_id> --candidates drafts/candidates/<run_id>/candidate_001.md --scope fragment
```

## Key Docs

- [PROJECT_STATUS.md](./PROJECT_STATUS.md): 当前项目状态和已确认决策。
- [analysis/failure_taxonomy.md](./analysis/failure_taxonomy.md): 可执行失败分类。
- [analysis/failure_cases.json](./analysis/failure_cases.json): case registry scaffold。
- [analysis/gate_report_protocol.md](./analysis/gate_report_protocol.md): gate report artifact contract。
- [analysis/rewrite_policy.md](./analysis/rewrite_policy.md): 局部改稿策略。
- [analysis/review_ledger.jsonl](./analysis/review_ledger.jsonl): 用户判定 ledger schema。
- [analysis/regression_comparison.md](./analysis/regression_comparison.md): 回归比较协议。
- [analysis/productization_gate_v1.md](./analysis/productization_gate_v1.md): single-kernel 产品边界与 gate 规则。
- [analysis/rewrite_plan_protocol.md](./analysis/rewrite_plan_protocol.md): 一次局部改稿协议。
- [analysis/harness_config.json](./analysis/harness_config.json): 当前 gate 配置。
- [analysis/reports/README.md](./analysis/reports/README.md): 报告目录和证据角色。
- [skills/novel-gate-harness/SKILL.md](./skills/novel-gate-harness/SKILL.md): Codex 执行 workflow。

完整章节索引和旧报告导航放在 [INDEX.md](./INDEX.md) 与 [analysis/README.md](./analysis/README.md)。
