# 项目索引

本索引用于快速定位当前 harness 路线、工具、报告和源文本章节。它只记录路径、标题和行号，不摘录正文。

## Active Navigation

| 用途 | 入口 |
|---|---|
| 项目总览 | [README.md](./README.md) |
| 当前状态与下一步 | [PROJECT_STATUS.md](./PROJECT_STATUS.md) |
| 分析产物目录 | [analysis/README.md](./analysis/README.md) |
| 报告目录 | [analysis/reports/README.md](./analysis/reports/README.md) |
| 清理/归档策略 | [analysis/project_cleanup_plan.md](./analysis/project_cleanup_plan.md) |
| 项目自检 | [tools/project_doctor.py](./tools/project_doctor.py) |
| Novel Gate Harness skill | [skills/novel-gate-harness/SKILL.md](./skills/novel-gate-harness/SKILL.md) |
| Skill 架构参考 | [skills/novel-gate-harness/references/project_architecture.md](./skills/novel-gate-harness/references/project_architecture.md) |
| Skill gate wrapper | [skills/novel-gate-harness/scripts/run_candidate_gate.py](./skills/novel-gate-harness/scripts/run_candidate_gate.py) |

## Current Run

| 用途 | 路径 |
|---|---|
| Run 目录 | `drafts/candidates/round6_codex_full_loop_20260609/` |
| 最新候选 | `drafts/candidates/round6_codex_full_loop_20260609/candidate_002.md` |
| 最新候选 JSON | `drafts/candidates/round6_codex_full_loop_20260609/candidate_002.json` |
| Rewrite plan | `drafts/candidates/round6_codex_full_loop_20260609/rewrite_plan.json` |
| 报告目录 | `analysis/reports/candidates/round6_codex_full_loop_20260609/` |
| Manifest | `analysis/reports/candidates/round6_codex_full_loop_20260609/manifest.json` |
| 最新 gate | `analysis/reports/candidates/round6_codex_full_loop_20260609/candidate_002_gate.md` |
| 对话窗口 review | `analysis/reports/candidates/round6_codex_full_loop_20260609/user_review_dialogue_window.md` |

当前最新 gate 状态：`needs_manual_triage`。

## Core Protocols

| 用途 | 文件 |
|---|---|
| Gate 配置 | [analysis/harness_config.json](./analysis/harness_config.json) |
| Gate report 协议 | [analysis/gate_report_protocol.md](./analysis/gate_report_protocol.md) |
| Rewrite plan 协议 | [analysis/rewrite_plan_protocol.md](./analysis/rewrite_plan_protocol.md) |
| Editing actions | [analysis/editing_actions.md](./analysis/editing_actions.md) |
| Rewrite policy | [analysis/rewrite_policy.md](./analysis/rewrite_policy.md) |
| Failure taxonomy | [analysis/failure_taxonomy.md](./analysis/failure_taxonomy.md) |
| Case registry | [analysis/failure_cases.json](./analysis/failure_cases.json) |
| Review ledger | [analysis/review_ledger.jsonl](./analysis/review_ledger.jsonl) |
| Regression comparison | [analysis/regression_comparison.md](./analysis/regression_comparison.md) |
| Productization v1 | [analysis/productization_gate_v1.md](./analysis/productization_gate_v1.md) |
| Lexicon taxonomy | [analysis/lexicon_taxonomy.md](./analysis/lexicon_taxonomy.md) |

## Tools

| 用途 | 路径 |
|---|---|
| 项目自检 | `tools/project_doctor.py` |
| Cleanup / drift check | `tools/cleanup_drift_check.py` |
| JSON contract | `tools/schema_check.py` |
| Editing action contract | `tools/editing_action_check.py` |
| Evidence ref contract | `tools/evidence_ref_check.py` |
| 规则型评估器 | `tools/style_evaluator.py` |
| 评估词表 | `tools/style_lexicon.json` |
| Delta v1 | `tools/delta_evaluator.py` |
| Segment Delta | `tools/eder_delta_evaluator.py` |
| 对话窗口分析 | `tools/dialogue_window_analyzer.py` |
| Light harness | `tools/light_harness.py` |
| Source shape | `tools/source_shape_analyzer.py` |
| Corpus tokenizer | `tools/corpus_tokenizer.py` |
| Lexicon taxonomy data | `tools/lexicon_taxonomy.json` |
| Corpus profiler | `tools/corpus_profiler.py` |

## Reports

| 用途 | 路径 |
|---|---|
| 当前候选报告 | `analysis/reports/candidates/round6_codex_full_loop_20260609/` |
| 上一轮候选报告 | `analysis/reports/candidates/round5_auto_prompt_20260608/` |
| Adachi pressure profile | `analysis/reports/corpus_profile_adachi_pressure.md` |
| 第 5 卷 tokenization 报告 | `analysis/reports/tokenization_vol05.md` |
| 「岛村之刃」tokenization 报告 | `analysis/reports/tokenization_vol05_shimamura_blade.md` |
| DeepSeek V4 tokenizer 对照 | `analysis/reports/tokenization_vol05_shimamura_blade_deepseek_v4_flash.md` |

## Corpus Index

| 用途 | 路径 |
|---|---|
| 机器可读卷/章索引 | `novel_index.json` |
| 语料切片说明 | `corpus_slices/README.md` |
| 语料切片配置 | `corpus_slices/slices.json` |

## 卷号映射

| 卷号 | 当前文件 | 原下载文件 |
|---|---|---|
| 第 1 卷 | `data/raw/vol01_第一卷_制服PINPON.txt` | `57157 utf-8.txt` |
| 第 2 卷 | `data/raw/vol02_第二卷_岛村前往健身房.txt` | `72353 utf-8.txt` |
| 第 3 卷 | `data/raw/vol03_第三卷_请挑选一个适合我的巧克力.txt` | `72363 utf-8.txt` |
| 第 4 卷 | `data/raw/vol04_第四卷_樱与春.txt` | `72396 utf-8.txt` |
| 第 5 卷 | `data/raw/vol05_第五卷_岛村之刃.txt` | `72409 utf-8.txt` |
| 第 6 卷 | `data/raw/vol06_第六卷_Bitter_Sweet_Memories.txt` | `81033 utf-8.txt` |
| 第 7 卷 | `data/raw/vol07_第七卷_如果没有在体育馆二楼相遇.txt` | `81043 utf-8.txt` |
| 第 8 卷 | `data/raw/vol08_第八卷_远游.txt` | `99285 utf-8.txt` |

## 第 1 卷

文件：`data/raw/vol01_第一卷_制服PINPON.txt`

| 行号 | 标题 |
|---:|---|
| 3 | 第一卷 制服PINPON |
| 1116 | 第一卷 未来FISHING |
| 2155 | 第一卷 安达QUESTION |
| 3078 | 第一卷 等边TRIANGEL |
| 4429 | 第一卷 女高中生HOLIDAY |
| 5162 | 第一卷 后记 |
| 5179 | 第一卷 插图 |

## 第 2 卷

文件：`data/raw/vol02_第二卷_岛村前往健身房.txt`

| 行号 | 标题 |
|---:|---|
| 3 | 第二卷 岛村 前往健身房 |
| 928 | 第二卷 安达Q |
| 1565 | 第二卷 奇妙的☆安达 |
| 2202 | 第二卷 安达思考中圣诞节进行中 |
| 2903 | 第二卷 岛村思考中圣诞节进行中 |
| 3512 | 第二卷 白色相簿 |
| 4361 | 第二卷 满分的大腿 |
| 4598 | 第二卷 认真的胸部 |
| 4687 | 第二卷 后记 |
| 4712 | 第二卷 插图 |

## 第 3 卷

文件：`data/raw/vol03_第三卷_请挑选一个适合我的巧克力.txt`

| 行号 | 标题 |
|---:|---|
| 3 | 第三卷 序 |
| 24 | 第三卷 第一章「请挑选一个适合我的巧克力」 |
| 553 | 第三卷 第二章「朝往太阳的光辉，香水草」 |
| 1786 | 第三卷 第三章「编织过去的荆棘，古典玫瑰」 |
| 3641 | 第三卷 第四章「以及拥抱圣母的爱，金盏花」 |
| 4316 | 第三卷 第五章「樱——愿望闪耀之时——」 |
| 4569 | 第三卷 后记 |
| 4596 | 第三卷 插图 |

## 第 4 卷

文件：`data/raw/vol04_第四卷_樱与春.txt`

| 行号 | 标题 |
|---:|---|
| 3 | 第四卷 第一章「樱与春」 |
| 756 | 第四卷 第二章「春与月」 |
| 2039 | 第四卷 第三章「月与决心」 |
| 2872 | 第四卷 第四章「决心与友人」 |
| 3611 | 第四卷 第五章「友人与爱」 |
| 5236 | 第四卷 第六章「爱与樱……」 |
| 5447 | 第四卷 后记 |
| 5484 | 第四卷 插图 |

## 第 5 卷

文件：`data/raw/vol05_第五卷_岛村之刃.txt`

| 行号 | 标题 |
|---:|---|
| 3 | 第五卷 if「就算大家很年幼」 |
| 240 | 第五卷 「就算你不求我，我也会去见你」 |
| 483 | 第五卷 第一话「来自蔚蓝」 |
| 2446 | 第五卷 第二话「岛村之刃」 |
| 2865 | 第五卷 第三话「灵魂是共有的？」 |
| 4628 | 第五卷 第四话「安达再起」 |
| 5477 | 第五卷 后记 |
| 5538 | 第五卷 插图 |

## 第 6 卷

文件：`data/raw/vol06_第六卷_Bitter_Sweet_Memories.txt`

| 行号 | 标题 |
|---:|---|
| 3 | 第六卷 「Bitter Sweet Memories」 |
| 360 | 第六卷 第一话「月历的彼方」 |
| 1493 | 第六卷 第二话「故乡的狗」 |
| 2730 | 第六卷 第三话「爱情错综」 |
| 4133 | 第六卷 第四话「飞翔」 |
| 5136 | 第六卷 后记 |
| 5155 | 第六卷 插图 |

## 第 7 卷

文件：`data/raw/vol07_第七卷_如果没有在体育馆二楼相遇.txt`

| 行号 | 标题 |
|---:|---|
| 3 | 第七卷 「如果没有在体育馆二楼相遇」 |
| 186 | 第七卷 第一章「感受著你的笑容」 |
| 817 | 第七卷 「如果安达贯彻最初的风格」 |
| 1010 | 第七卷 第二章「仅需要片刻的安宁」 |
| 2641 | 第七卷 第三章「平凡至极的话语」 |
| 4032 | 第七卷 第四章「许下小小愿望」 |
| 4557 | 第七卷 「就在这个世界之中」 |
| 4946 | 第七卷 后记 |
| 5005 | 第七卷 插图 |

## 第 8 卷

文件：`data/raw/vol08_第八卷_远游.txt`

| 行号 | 标题 |
|---:|---|
| 3 | 第八卷 「远游」 |
| 1066 | 第八卷 「第一次旅行的一角①」 |
| 3619 | 第八卷 「日野与永藤」 |
| 3966 | 第八卷 「小社来访者」 |
| 4193 | 第八卷 「第一次旅行的一角②」 |
| 5374 | 第八卷 「返家」 |
| 5549 | 第八卷 后记 |
| 5574 | 第八卷 插图 |
| 5577 | 第八卷 animate特典 |

## 重点分析切片

| 用途 | 文件 | 起始行 |
|---|---|---:|
| 关系失衡核心段 | `data/raw/vol05_第五卷_岛村之刃.txt` | 2446 |
| 关系错位前置段 | `data/raw/vol05_第五卷_岛村之刃.txt` | 483 |
| 事后反思与重估段 | `data/raw/vol05_第五卷_岛村之刃.txt` | 2865 |
| 主体性恢复与行动段 | `data/raw/vol05_第五卷_岛村之刃.txt` | 4628 |
