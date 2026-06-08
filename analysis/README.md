# 分析产物目录

这里保存后续围绕「岛村之刃」的写作机制分析与生成辅助文件。

## 已完成产物

- `style_analysis.md`：本章情绪张力机制、意识流模式、对话节奏、日常物件与翻译腔分析。
- `transferable_rules.md`：可迁移写作规则。
- `generation_prompt.md`：用于创作原创「安达第一人称意识流短篇」的 prompt。
- `generation_prompt_round3.md`：Round 3 同场景改稿 prompt，强调长篇失控输出与接收端断续理解。
- `generation_prompt_round4.md`：Round 4 长篇候选 prompt，将目标长度拓宽到 6500-8500 字符，并要求日常/高压比例。
- `review_checklist.md`：成稿审稿清单。
- `harness_plan.md`：轻量候选筛选 harness 计划，定义 gate 状态、subagent 分工和用户 review 边界。
- `harness_config.json`：Harness v1 gate 配置。
- `rewrite_plan_protocol.md`：当前产品化 loop 的核心协议；把诊断翻译成一次局部重写任务。
- `project_cleanup_plan.md`：旧候选、旧 prompt、生成报告的保留/归档/待删清单。
- `lexicon_taxonomy.md`：taxonomy 粒度主文档；先定义泛化语言学维度，再映射回项目 gate。
- `productization_gate_v1.md`：Single-kernel tuning lab 产品化方向；消费 taxonomy 映射后的 gate 信号，不重新定义 taxonomy。
- `../skills/novel-gate-harness/SKILL.md`：项目内 skill 草案，用于候选生成、结构 JSON、harness 检测和下一轮决策。
- `../tools/corpus_tokenizer.py`：语料 tokenization 与词表发现工具，默认 `regex`，可选 `jieba`、OpenAI `tiktoken` 和 Hugging Face/DeepSeek tokenizer。
- `../tools/corpus_profiler.py`：语料 profile 与可解释特征权重工具，不做 RAG。
- `../tools/eder_delta_evaluator.py`：实验性片段级 Eder/Cosine Delta 诊断工具，用于定位 daily/pressure 分布。

## 当前主线

当前项目主线是受控局部改稿，而不是继续堆 prompt 或黑箱分类器：

```text
candidate.md + candidate.json
-> gate + segment diagnosis
-> rewrite_plan.json
-> one controlled local rewrite
-> gate again
-> user review
```

`rewrite_plan.json` 未来可由 deterministic planner + agent layer 生成。当前阶段可以人肉生成和执行，但必须保留证据来源。

诊断源分四类：

- `metric`：长度、台词分布、解释标记、结构 JSON 统计。
- `segment_delta`：片段级 daily/pressure/shimamura_view 相对距离。
- `agent_close_reading`：指标无法覆盖的近读风险。
- `user_feedback`：用户审稿结论，优先级最高。

## 当前实验产物

- `../drafts/current.md`：第一轮固定场景测试稿。
- `reports/current.md`：规则型文本风格评估器输出。
- `reports/codex_review.md`：Codex 人工 review。
- `reports/diff.md`：用户与 Codex 对第一轮稿件失败模式的逐句讨论。

## Delta v1

- 已新增 Delta 相对距离评估器。
- Delta v1 将比较生成稿与 `adachi_pressure`、`adachi_daily`、`shimamura_view`、`analysis_docs` 的表层文体距离。
- Delta 只作为趋势观察，不作为质量评分或作者相似度百分比。
- 切片配置：`../corpus_slices/slices.json`
- 推荐命令：`python tools/delta_evaluator.py --draft drafts/current.md --slices corpus_slices/slices.json --output-prefix analysis/reports/delta_current`

## Segment Delta Experiment

- `../tools/eder_delta_evaluator.py` 是当前片段级诊断实验。
- 它使用 reference 片段的字符 n-gram 相对频率、z-score 标准化和 cosine distance。
- 它不替代 Delta v1，不进入质量判断。
- 它的用途是把整篇平均距离拆成局部诊断：哪些片段还偏 `adachi_daily`，哪些片段进入 `adachi_pressure`。
- 推荐命令：`python tools/eder_delta_evaluator.py --draft drafts/candidates/<run_id>/candidate_001.md --slices corpus_slices/slices.json --output-prefix analysis/reports/candidates/<run_id>/candidate_001_eder_delta --segment-size 500 --min-segment-chars 250 --top-features 800`

## Harness v1

- 第一版已实现为已有候选评分器，不自动生成候选。
- Harness 只筛掉明显失败样本，不判定成功。
- 通过 gate 的候选只能进入 `pending_user_review`。
- Subagent 可以生成候选或写 provisional notes，但不能写最终回归结论。
- 可用入口：`python tools/light_harness.py --run-id existing_rounds_audit --candidates drafts/current.md drafts/round2.md drafts/round3.md --slices corpus_slices/slices.json --config analysis/harness_config.json --reports-root analysis/reports/candidates`

## Productization v1

- 第一版定位为 single-kernel tuning lab，不允许任意切换审美内核。
- Gate v1 的第一优先级是解释化泄漏，尤其是岛村过度理解安达。
- 后续候选建议采用 `candidate_001.md` + `candidate_001.json`：Markdown 给人读，JSON 给 harness 识别说话人、回应关系和表层接收词。
- 后续改稿建议采用 `rewrite_plan.json`：规则库归 `harness_config.json`，本次执行单归 rewrite plan。
- taxonomy 粒度以 `lexicon_taxonomy.md` 为准；本节只记录产品 gate 的使用方式。

## Lexicon / Tokenization / Profile

- 主文档：`lexicon_taxonomy.md`。
- Tokenization 报告只发现候选词与 n-gram，不做质量评分：`reports/tokenization_vol05.md/json`、`reports/tokenization_vol05_shimamura_blade.md/json`。
- DeepSeek V4-Flash tokenizer 报告只作模型侧 tokenization 对照：`reports/tokenization_vol05_shimamura_blade_deepseek_v4_flash.md/json`。
- Corpus Profile 比较参照组的 taxonomy/shape/token 特征权重，辅助 gate 调参：`reports/corpus_profile_adachi_pressure.md/json`。
- 边界：不做 RAG，不召回原文，不替代人工 review；词表候选必须经过用户 review 或回归验证后再进入 gate。

## 重点定位

- 核心章节：`../data/raw/vol05_第五卷_岛村之刃.txt`
- 章节标题：第五卷 第二话「岛村之刃」
- 范围：第 2446 行到第 2864 行
- 下一章起点：第 2865 行，第三话「灵魂是共有的？」

## 分析边界

- 不长篇摘录原文。
- 不复刻原文句式。
- 不模仿作者专属表达。
- 只抽取可迁移的机制、节奏、角色关系与审稿标准。
