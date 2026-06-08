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
- `productization_gate_v1.md`：Single-kernel tuning lab 产品化方向，定义 `md + json` 候选协议与解释化 gate 优先级。
- `lexicon_taxonomy.md`：泛化语言学 taxonomy，将词表发现维度映射回项目 gate。
- `../skills/novel-gate-harness/SKILL.md`：项目内 skill 草案，用于候选生成、结构 JSON、harness 检测和下一轮决策。
- `../tools/corpus_tokenizer.py`：语料 tokenization 与词表发现工具，默认 `regex`，可选 `jieba`、OpenAI `tiktoken` 和 Hugging Face/DeepSeek tokenizer。
- `../tools/corpus_profiler.py`：语料 profile 与可解释特征权重工具，不做 RAG。

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

## Tokenization v1

- 当前报告：`reports/tokenization_vol05.md/json` 与 `reports/tokenization_vol05_shimamura_blade.md/json`。
- DeepSeek V4-Flash tokenizer 对照：`reports/tokenization_vol05_shimamura_blade_deepseek_v4_flash.md/json`。
- 用途是发现词表候选和语料差异，不做质量评分。
- 本机当前没有安装 `jieba` 或 `tiktoken`；Hugging Face tokenizer 依赖已安装到项目本地 `.deps/hf-tokenizer2/`。
- 报告按 `../tools/lexicon_taxonomy.json` 先汇总泛化语言学类别，再映射回当前 gate 标签。

## Corpus Profile v1

- 当前报告：`reports/corpus_profile_adachi_pressure.md/json`。
- 用途是比较参照组的 taxonomy/shape/token 特征权重，辅助 gate 调参。
- 不做 RAG，不召回原文，不替代人工 review。

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
