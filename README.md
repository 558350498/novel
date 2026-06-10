# Narrative Mechanism Failure Harness

这是一个面向中文叙事机制与文风迁移的失败分析与约束 harness。

它不是小说 prompt 仓库，不是通用小说生成器，也不是文学质量裁判。项目目标是把一个固定叙事机制和对应文风表面拆成可检查、可复盘、可回归的工程流程：生成候选、识别失败、局部修复、记录用户判断，再用这些判断约束下一轮。

“原创”在本项目里只表示不复制原文、不长篇摘抄、不照搬句式或情节结构；它不是反模仿命令。机制级文风贴近、节奏贴近、翻译腔贴近和角色接收方式贴近，是 harness 要保留和检验的目标。

## Fixed Kernel

v1 只服务一个 fixed kernel

自动化只能筛掉明显失败和定位风险。最终 pass/fail 只能来自用户 review。

## Active Path

当前入口只看这一条路线：

```text
drafts/candidates/round6_codex_full_loop_20260609/
-> analysis/reports/candidates/round6_codex_full_loop_20260609/
-> needs_manual_triage / pending_user_review / failed_auto_gate
-> user review
-> review ledger
```

当前活跃 run：

| Role | Path |
|---|---|
| Candidate source | `drafts/candidates/round6_codex_full_loop_20260609/` |
| Latest candidate | `drafts/candidates/round6_codex_full_loop_20260609/candidate_002.md` |
| Latest candidate JSON | `drafts/candidates/round6_codex_full_loop_20260609/candidate_002.json` |
| Rewrite plan | `drafts/candidates/round6_codex_full_loop_20260609/rewrite_plan.json` |
| Gate manifest | `analysis/reports/candidates/round6_codex_full_loop_20260609/manifest.json` |
| Latest gate report | `analysis/reports/candidates/round6_codex_full_loop_20260609/candidate_002_gate.md` |
| Dialogue window review | `analysis/reports/candidates/round6_codex_full_loop_20260609/user_review_dialogue_window.md` |

Current latest gate state: `needs_manual_triage`.

Known latest machine reasons:

- 1-10 字短台词占比偏高。
- 11-40 字中段台词占比不足。
- 台词分布整体偏离源切片自检范围。
- Delta 第一名仍为 `adachi_daily`，不是 `adachi_pressure`。

## Working Loop

```text
candidate.md + candidate.json
-> machine gate + diagnostics
-> mandatory multi-agent review for full candidates
-> rewrite_plan.json
-> one local rewrite only
-> regression comparison
-> user review
-> review ledger
```

`novel-gate-harness` 保留为唯一顶层入口，但内部拆成两个 harness：

- `prompt_generation_harness`: 从 failure taxonomy、case registry、ledger 和 regression 风险生成 prompt / candidate spec / paired candidate。
- `result_harness`: 对 paired candidate 跑 gate、multi-agent review、rewrite policy、regression comparison 和 ledger handoff。

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
- `pending_user_review` 不是成功状态。

## Candidate Protocol

完整候选必须成对提交：

```text
drafts/candidates/<run_id>/candidate_001.md
drafts/candidates/<run_id>/candidate_001.json
```

`candidate_001.md` 给人读，保持小说自然形态。

`candidate_001.json` 给 harness 读，记录 speaker、utterance、response relation、surface terms、deep understanding risk、scene beats 等结构信号，避免 gate 从 prose 格式里猜角色关系。

短片段练习可以用 fragment scope，但 fragment 只能验证局部机制，不能证明完整候选 ready。

## Commands

检查项目入口和活跃路径：

```powershell
python tools/project_doctor.py
```

检查 harness 环境：

```powershell
python skills/novel-gate-harness/scripts/run_candidate_gate.py --check-only
```

检查完整候选：

```powershell
python skills/novel-gate-harness/scripts/run_candidate_gate.py --run-id round6_codex_full_loop_20260609 --candidates drafts/candidates/round6_codex_full_loop_20260609/candidate_002.md
```

检查短片段机制：

```powershell
python skills/novel-gate-harness/scripts/run_candidate_gate.py --run-id <run_id> --candidates drafts/candidates/<run_id>/candidate_001.md --scope fragment
```

运行本地 CI contract：

```powershell
python tools/project_ci.py --require-regression-review
```

单独检查 JSON schema / contract：

```powershell
python tools/schema_check.py
```

单独检查 multi-agent review contract：

```powershell
python tools/agent_review_runner.py --run-id round6_codex_full_loop_20260609 --require-regression
```

运行 fixture/unit tests：

```powershell
python -m unittest discover -s tests
```

当前 CI 默认不把 `project_doctor` warning 当作失败；如果需要把文档断链和缺失语料 warning 也升级为失败，使用：

```powershell
python tools/project_ci.py --strict-warnings --require-regression-review
```

## Progressive Disclosure

Use this order when entering the project:

1. `README.md`: current active path and hard rules.
2. `PROJECT_STATUS.md`: current state, latest risk, and next legal actions.
3. `skills/novel-gate-harness/SKILL.md`: Codex execution workflow.
4. `skills/novel-gate-harness/references/project_architecture.md`: directory roles and pipeline.
5. `analysis/README.md`: durable protocols and analysis artifacts.
6. `analysis/reports/README.md`: generated report layout and current run reports.
7. `INDEX.md`: corpus navigation and chapter locations.

## Active And Provenance Split

Active files should point to runnable paths and current evidence.

Provenance files explain how the project reached the current route, but should not dominate first-pass navigation. See `analysis/project_cleanup_plan.md` before moving, archiving, or deleting anything.

Do not delete source texts, user-reviewed evidence, or current protocol docs without explicit confirmation.
