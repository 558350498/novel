# 《安达与岛村》文本分析与生成辅助项目进度

## 项目目标

建立一套服务于原创中文短篇的文本分析与生成辅助流程：参考《安达与岛村》第 5 卷「岛村之刃」的关系机制和情绪张力结构，但不复刻原文、不模仿专属句式、不长篇摘抄。最终产出可用的写作 prompt、可迁移规则、审稿清单，以及轻量文本风格评估工具。

## 当前进度

### 当前下一步：六个硬产物初版

项目门面已从 prompt 仓库调整为 `Narrative Mechanism Failure Harness`。下一步不是继续堆 prompt，而是把下面六个硬产物做成可执行、可复盘、可回归的初版：

| 产物 | 当前文件 | 状态 |
|---|---|---|
| Failure taxonomy | `analysis/failure_taxonomy.md` | v0 scaffold，定义可执行失败分类和 case triplet 规则 |
| Case registry | `analysis/failure_cases.json` | v0 scaffold，含 provisional cases 和 `case_id` schema |
| Gate report | `analysis/gate_report_protocol.md` + `analysis/reports/candidates/<run_id>/` | 已有报告输出，新增 artifact contract |
| Rewrite policy | `analysis/rewrite_policy.md` + `analysis/rewrite_plan_protocol.md` | 已有协议，新增 policy 入口 |
| Review ledger | `analysis/review_ledger.jsonl` | v0 schema，等待用户 review 条目 |
| Regression comparison | `analysis/regression_comparison.md` | v0 protocol，正式 regression 仅收 `user_confirmed` case |

硬边界：

- Failure taxonomy 是可执行失败分类，不是泛化文学分类。
- 正式 taxonomy 条目必须绑定 positive / negative / borderline case。
- 正式 regression 只接受 `user_confirmed` case。
- Full candidate 在用户 review 前必须经过多角色 agent review。
- Gate、Delta、agent review 都不能替代用户最终判定。

### 已完成

- 前 8 卷 txt 已按卷号重命名为 `vol01` 到 `vol08`。
- 已创建工程入口 `README.md`。
- 已创建人工章节索引 `INDEX.md`。
- 已创建机器可读索引 `novel_index.json`。
- 已创建分析目录说明 `analysis/README.md`。
- 已创建轻量文本风格评估器 `tools/style_evaluator.py`。
- 已创建评估词表 `tools/style_lexicon.json`。
- 已创建当前待审稿文件 `drafts/current.md`，并写入第一轮固定场景测试稿。
- 已创建评估报告目录 `analysis/reports/`，并生成第一轮自动评估报告 `analysis/reports/current.md`。
- 已生成第一轮 Codex 人工 review：`analysis/reports/codex_review.md`。
- 已生成第一轮差异讨论文档：`analysis/reports/diff.md`。
- 已实现 Delta v1 相对距离评估器：`tools/delta_evaluator.py`。
- 已创建 Delta v1 切片配置：`corpus_slices/slices.json`。
- 已实现 Harness v1：`tools/light_harness.py`、`analysis/harness_config.json`、`analysis/harness_plan.md`。
- 已实现全篇章形状分析：`tools/source_shape_analyzer.py`，输出 `analysis/reports/source_chapter_shape.md/json`。
- 已新增 Round 4 长篇候选 prompt：`analysis/generation_prompt_round4.md`。
- 已确认产品化第一版定位：single-kernel tuning lab，不允许任意切换审美内核。
- 已新增 Gate v1 产品化计划：`analysis/productization_gate_v1.md`，确定候选采用 Markdown 正文 + JSON 结构标注。
- 已将项目初步做成可用 Codex skill：`skills/novel-gate-harness/SKILL.md` 用于候选生成、JSON 结构标注、harness 检测和下一轮决策；`references/project_architecture.md` 记录项目架构；`scripts/run_candidate_gate.py` 提供环境自检和候选 gate wrapper；并已同步到全局 `C:\Users\33625\.codex\skills\novel-gate-harness\`。
- 已新增 corpus tokenizer v1：`tools/corpus_tokenizer.py`，用于词表发现、语料拓展和第 5 卷 tokenization 报告；支持 `regex`，并预留 `jieba`、OpenAI `tiktoken` 与 Hugging Face/DeepSeek tokenizer 可选引擎。
- 已新增泛化词表 taxonomy：`tools/lexicon_taxonomy.json` 与 `analysis/lexicon_taxonomy.md`，将项目 gate 标签映射到语言学维度。
- 已生成第 5 卷与「岛村之刃」核心切片的 tokenization 报告：
  - `analysis/reports/tokenization_vol05.md/json`
  - `analysis/reports/tokenization_vol05_shimamura_blade.md/json`
- 已安装 Hugging Face tokenizer 依赖到项目本地 `.deps/hf-tokenizer2/`，并生成 DeepSeek V4-Flash tokenizer 对照：
  - `analysis/reports/tokenization_vol05_shimamura_blade_deepseek_v4_flash.md/json`
- 已新增 corpus profiler v1：`tools/corpus_profiler.py`，输出可解释特征权重，不做 RAG。
- 已生成 `adachi_pressure` 对照 profile：`analysis/reports/corpus_profile_adachi_pressure.md/json`。
- 已新增 experimental Eder/Cosine segment Delta：`tools/eder_delta_evaluator.py`，用于把整篇 Delta 拆成片段级 daily/pressure/shimamura_view 诊断；该工具只定位问题，不判定质量。
- 已新增 rewrite-plan 产品协议：`analysis/rewrite_plan_protocol.md`，确定 `rewrite_plan.json` 作为 gate/segment diagnosis 到一次局部重写之间的执行单。
- 已新增六个硬产物初版入口：`analysis/failure_taxonomy.md`、`analysis/failure_cases.json`、`analysis/gate_report_protocol.md`、`analysis/rewrite_policy.md`、`analysis/review_ledger.jsonl`、`analysis/regression_comparison.md`。
- 已新增项目清理计划：`analysis/project_cleanup_plan.md`，区分 active、provenance、可归档和确认后可删除的文件类别。
- 已生成四份分析产物：
  - `analysis/style_analysis.md`
  - `analysis/transferable_rules.md`
  - `analysis/generation_prompt.md`
  - `analysis/review_checklist.md`
- 已定位核心素材：
  - 文件：`data/raw/vol05_第五卷_岛村之刃.txt`
  - 核心章：第五卷 第二话「岛村之刃」
  - 范围：第 2446 行到第 2864 行
  - 下一章起点：第 2865 行
- 已确认正文 txt 的实际物理位置在 `data/raw/`，根目录索引中的文件名作为逻辑索引使用。

### 已确认的技术判断

- 本项目不是写文学论文，而是建立可执行的生成约束与审稿流程。
- token/词频统计不是为了替代 LLM 阅读，而是为了把风格机制转成 prompt 约束和 review checklist 指标。
- 不使用模型 BPE token 作为文学分析单位；优先使用中文词、短语、标点、句长、段落长度、对话占比、否定循环等写作单位。
- 高频词表本身价值有限；更重要的是差异高频、功能词、短语、n-gram 和章节对比。
- 简中译文不是纯噪音。它可能丢失或扭曲日文信息，但也提供目标中文读感里的日轻翻译腔。
- 如果后续加入日文原版，它作为上游参考文本校准机制；中文译文和本项目 prompt 作为本地适配层，服务于中文原创短篇。

## 已锁定方向

### 分析策略

- 日文原版如可获得：用于校准关系机制、原始节奏、否定方式和象征强度。
- 中文译文：用于提取中文输出读感、日轻翻译腔、别扭连接词、短句重复和对话口感。
- 最终创作目标：中文原创短篇，不回推日文原文，不复刻作者表达。

### 文本风格评估器设计

先做独立轻量脚本，再考虑 Codex hook。

- 脚本：`tools/style_evaluator.py`
- 词表：`tools/style_lexicon.json`
- 当前待审稿：`drafts/current.md`
- 报告目录：`analysis/reports/`
- 可选 hook：`.codex/hooks.json`，等脚本稳定后再挂到 `Stop`

### 评估模式

- `--mode prompt`：检查写作 prompt 是否存在复刻、照搬句式、长摘抄、象征解释太死、华丽文学腔、结尾解决问题等风险。
- `--mode draft`：检查成稿是否存在情绪表达过度直白、岛村回应过度解释、对话功能过度理性化、日常物件承载不足、翻译腔特征不足、结尾封闭化等风险。

### 多因子原则

文本风格评估采用多指标提示，不做单一阈值裁决。

- 含混因子：否定、犹豫、修正、核心问题低风险化。
- 错位因子：安达问题很轻但背后很重，岛村回答轻且不解释。
- 反刍因子：小事件被反复想，出现否定、在意、自责、再在意的循环。
- 日常物件因子：手机、屏幕、掌心、喉咙、房间、灯、被子、空调声等承载情绪。
- 翻译腔因子：短句、重复、轻微别扭、日轻式连接和回应。
- 未解决因子：结尾只暂时止血，不和解，不给彻底答案。

### 第一轮实验设计

- 第一篇测试稿固定使用 `generation_prompt.md` 中的场景链：烟花祭后、看见岛村和樽见、回家盯手机、短电话、明天见面、掌心薄痛结尾。
- 固定场景的目的，是控制剧情变量，优先测试 prompt、评估器和审稿清单是否能约束目标机制。
- 第一版测试稿已由 Codex 生成，写入 `drafts/current.md`。
- 已运行 `tools/style_evaluator.py --mode draft drafts/current.md --output analysis/reports/current.md`。
- 已完成 Codex 人工 review，并和用户一起把第一轮失败模式写入 `analysis/reports/diff.md`。
- 当前关键结论：第一轮稿件最大问题不是“不够痛”，而是安达过载时仍然太能组织语言，分析层概念泄漏进了小说层。

### Delta 相对距离评估器 v1

Delta 不替代现有 `style_evaluator.py`，只作为相对距离指标使用。它回答的是“生成稿更靠近哪类参照语料”，不回答“像不像作者”“质量是否合格”。

- 工具：`tools/delta_evaluator.py`。
- 配置：`corpus_slices/slices.json`，使用范围引用，不复制原文片段。
- 报告：输出 `analysis/reports/delta_current.json` 和 `analysis/reports/delta_current.md`。
- 特征：第一版使用字符 unigram、字符 bigram、标点频率；句长分布单独报告，不进入主 Delta 距离向量。
- 参照组：
  - `adachi_pressure`：安达高压段，优先使用 `data/raw/vol05_第五卷_岛村之刃.txt` 第 2446 行到第 2864 行前。
  - `adachi_daily`：安达日常但非高压段，当前使用第 5 卷「来自蔚蓝」第 483 行到第 2445 行。
  - `shimamura_view`：岛村视角或岛村平稳叙述段，当前使用第 2 卷「岛村 前往健身房」第 3 行到第 927 行。
  - `analysis_docs`：四份核心分析文档，用于检测生成稿是否靠近分析腔。
  - `drafts`：生成稿，如 `drafts/current.md`。
- 解释原则：Delta 越近只表示表层特征更接近该组参照，不等于更好；如果 Delta 趋势与人工读感冲突，以人工 review 为准，并记录为指标盲区。

### Harness v1

Harness v1 先做轻量文件式候选筛选，不引入 LangChain，不让 LLM 自行打总分。

- 计划文档：`analysis/harness_plan.md`。
- 可用工具：`tools/light_harness.py`。
- gate 配置：`analysis/harness_config.json`。
- 第一版已实现为已有候选评分器，暂不自动生成候选。
- 候选目录：`drafts/candidates/<run_id>/candidate_001.md`。
- 报告目录：`analysis/reports/candidates/<run_id>/`。
- 状态只允许：
  - `failed_auto_gate`
  - `needs_manual_triage`
  - `pending_user_review`
- 自动 gate 只筛掉明显失败样本，不判定成功。
- 通过 gate 的候选只能进入 `pending_user_review`。
- Subagent 可作为候选生产者、盲读记录员或指标复核员；不能作为最终裁判，不能写最终回归结论。
- 最终定性必须等待用户 review。

### Productization v1

第一版产品路线不是通用小说生成器，而是 single-kernel tuning lab：固定一个审美内核，围绕同一作品/同一方向调 gate、词表、语料标签、prompt 和用户反馈记录。

当前已锁定的产品化判断：

- 高参与创作者不要求自己会稳定写文章，但必须作为审美 owner 参与判断。
- Codex 负责执行写作、分析、候选生成和归因。
- 第一版不允许任意切换审美内核，只允许在同一内核下调变量。
- Gate v1 的第一优先级是解释化泄漏，尤其是岛村过度理解安达。
- 候选协议采用 `candidate_001.md` + `candidate_001.json`：正文给人读，JSON 给 harness 识别说话人、回应关系、表层接收词和深层理解风险。
- 改稿协议采用 `rewrite_plan.json`：deterministic planner 记录指标/片段证据，agent layer 只在证据基础上生成一次局部重写任务。
- 诊断源分为 `metric`、`segment_delta`、`agent_close_reading`、`user_feedback`；冲突解释权顺序为 `user_feedback > blocking_metric > segment_delta > agent_close_reading`。
- 对话约束采用执行语义：`blocking_checks`、`rewrite_triggers`、`review_warnings`，不再依赖抽象的 hard/soft/watch 提示词。
- Skill `novel-gate-harness` 已可作为初版 agent workflow；项目内 `skills/novel-gate-harness/` 是源码副本，全局 `C:\Users\33625\.codex\skills\novel-gate-harness\` 是当前可发现安装副本。

### Corpus Tokenization v1

Corpus tokenizer 用于词表发现和语料拓展，不作为质量评分，也不替代人工 review。

当前设计：

- 默认 `regex` 引擎可稳定运行，不依赖外部包。
- 预留 `--engine jieba`，本机安装开源 `jieba` 后可切换。
- 预留 `--engine tiktoken`，本机安装 OpenAI `tiktoken` 后可生成模型侧 tokenization 对照；它不是中文语言学分词。
- 预留 `--engine hf --hf-model deepseek-ai/DeepSeek-V3`，本机安装 `transformers/tokenizers` 并具备模型 tokenizer 文件后可生成 DeepSeek tokenizer 对照；它同样不是中文语言学分词。
- 输出 Markdown 报告、JSON 报告和 token stream。
- `.tokens.txt` token stream 受 `.gitignore` 的 `*.txt` 规则忽略，默认不作为版本化产物。
- 报告重点看高频 token、token n-gram、CJK n-gram 和 candidate phrase seeds。
- 报告已接入 `tools/lexicon_taxonomy.json`，优先按泛化 taxonomy 汇总，再映射回项目 gate。
- 本机当前未安装 `tiktoken`。
- Hugging Face tokenizer 依赖已安装到 `.deps/hf-tokenizer2/`，DeepSeek V4-Flash tokenizer 文件约 `6.37 MB`，已生成核心切片对照报告。
- DeepSeek tokenizer 报告的少数 top token 可能显示 `�`，这是模型 tokenizer byte 片段单 token 解码不完整导致的；taxonomy hits 与 CJK n-gram 仍可读。

当前初步信号：

- 第 5 卷整卷报告显示大量功能词和通用叙述词，只能作为宽背景。
- 「岛村之刃」核心切片更适合做当前 kernel 词表发现。taxonomy hits 显示 `stance_uncertainty` 是最高维度，其次是 `concrete_grounding`、`cognitive_explanation` 和 `affect_intensity`。
- 核心切片的 candidate phrase seeds 已出现 `我希望`、`我不要`、`希望你`、`告诉我`、`想知道`、`我好想` 等候选。
- 这些候选只能作为人工 review 的词表种子，不能直接全部加入 gate。

### Lexicon Taxonomy v1

底层分类使用更泛化的语言学维度，项目 gate 标签只作为映射层：

- `affect_intensity`：情绪与强度。
- `stance_uncertainty`：不确定、否定、修正。
- `cognitive_explanation`：因果、洞察、解释化。
- `dialogic_alignment`：回应、错位、接收端。
- `concrete_grounding`：身体、感官、物件、空间。
- `closure_resolution`：解决、和解、封闭。
- `prompt_boundary`：prompt 边界和复刻风险。

当前不再把 `过载表达`、`接收端错位`、`解释化泄漏`、`日常物件`、`封闭结尾` 当作底层 taxonomy；它们只保留为当前作品的 gate 语言。

### Corpus Profile v1

Corpus profile 用于细致化分析原作参照组，不做 RAG，不召回原文片段，不把统计权重当成质量分。

当前实现：

- 输入 `corpus_slices/slices.json`。
- 对每个参照组生成 taxonomy 密度、句长、对话占比、最长台词、超长台词数、CJK n-gram。
- 以 `adachi_pressure` 为目标组，计算其相对其他参照组的标准化 effect。
- 输出 Markdown 与 JSON：`analysis/reports/corpus_profile_adachi_pressure.md/json`。

当前初步结论：

- 区分 `adachi_pressure` 的最强信号是 `shape.dialogue_ge_200` 和 `shape.dialogue_max`，即超长台词形状，而不是单个情绪词。
- `cognitive_explanation` 在目标组反而低于其他组，说明核心高压不应写成解释化分析。
- `affect_intensity` 略高，但效应不如台词形状强，提示 gate 不应只盯情绪词。
- 这些权重只辅助人工 review 和 gate 调参，不能自动决定候选成功。

## 后续计划

### 第 1 步：Delta v1（已实现初版）

- 已新建 `corpus_slices/README.md` 和 `corpus_slices/slices.json`。
- 已新建独立脚本 `tools/delta_evaluator.py`，不合并进 `tools/style_evaluator.py`。
- 推荐命令：
  - `python tools/delta_evaluator.py --draft drafts/current.md --slices corpus_slices/slices.json --output-prefix analysis/reports/delta_current`
- 第一版只做当前稿对参照组的距离排序，不做多 draft 历史趋势。
- 验证 Markdown 报告包含 `adachi_pressure`、`adachi_daily`、`shimamura_view`、`analysis_docs`，并明确写出“相对指标，不等于质量评分”。
- 验证 JSON 报告包含 draft 路径、feature set、group distances、generated_at。

### 第 2 步：第二轮固定场景改稿

- 保持固定场景链不变。
- 重写或局部增强电话前后片段，让安达出现更明显的过载发话、断句、重复、抢话和语义传达失败。
- 减少完整解释句，避免把 `轻`、`普通`、`真正的问题`、`温和所以痛` 等分析结论写进小说层。
- 生成后继续运行规则型评估器，并结合 `diff.md` 做人工 review。
- 任何新版草稿在用户 review 前只能标记为 `pending user review`；Codex 可以写 provisional review，但不能自行宣布新版更好或写入最终回归结论。

### 第 3 步：调参

- 根据第一篇测试稿和后续 2 到 3 篇草稿的实际报告，调整 `tools/style_lexicon.json` 的词表和阈值。
- 必要时回改 `analysis/generation_prompt.md` 和 `analysis/review_checklist.md`。
- 保留多指标提示，不引入单一总分裁决。
- 第一版继续不引入 MeCab、Sudachi、Jieba 等重型分词。
- 根据 Delta v1 与人工 review 的一致性，决定是否调整切片范围、特征集合或增加历史对比。

### 第 4 步：Harness v1（已实现初版）

- 已实现 `tools/light_harness.py` 和 `analysis/harness_config.json`。
- 第一版只扫描已有候选，不自动调用模型生成候选。
- 汇总 `style_evaluator`、`delta_evaluator` 和台词长度分布。
- 输出候选 gate 报告和 `manifest.json`。
- 不写最终人工结论，只标记 `failed_auto_gate`、`needs_manual_triage` 或 `pending_user_review`。

### 第 5 步：长篇候选与日常段扩展

- 使用 `analysis/generation_prompt_round4.md` 生成 6500-8500 字符候选。
- 候选写入 `drafts/candidates/<run_id>/candidate_001.md`，并配套写入 `candidate_001.json` 结构标注，再交由 harness 筛选。
- 通过 gate 后仍只进入 `pending_user_review`。
- 回归时对照 `analysis/reports/source_chapter_shape.md/json`，同时看日常段和高压段，不只看高潮。

### 第 6 步：Gate 结构层

- 更新 `tools/light_harness.py`，优先读取候选 JSON。
- 让 `岛村回应解释化` 使用结构化 utterances，而不是只依赖 `岛村：` 显式说话人格式。
- JSON 缺失时保留当前启发式文本检查作为 fallback。
- Gate 继续只筛明显失败，不写成功结论。

### 第 7 步：词表迭代

- 基于 `analysis/reports/tokenization_vol05_shimamura_blade.md/json` 提取词表候选。
- 结合 `analysis/reports/corpus_profile_adachi_pressure.md/json` 看哪些 taxonomy/shape 维度真正区分目标组。
- 先将候选分到泛化 taxonomy：`affect_intensity`、`stance_uncertainty`、`cognitive_explanation`、`dialogic_alignment`、`concrete_grounding`、`closure_resolution`。
- 再把 taxonomy 信号映射到项目 gate：过载表达、接收端错位、解释化泄漏、日常物件、封闭结尾、翻译腔。
- 只把经过用户 review 或候选回归验证的词加入 `tools/style_lexicon.json`。
- 避免把全卷高频词直接当成风格本体。

### 第 8 步：考虑 Codex hook

等脚本稳定后，再添加 `.codex/hooks.json`。

hook 设计原则：

- 只在 `drafts/current.md` 存在时运行。
- 不存在就静默退出。
- 默认只输出提醒报告，不阻止正常对话。
- 不在每轮对话里制造噪音。

### 第 9 步：Rewrite Plan 协议落地

- 以 `analysis/rewrite_plan_protocol.md` 为当前协议源。
- 下一步为当前候选 run 生成第一份真实 `rewrite_plan.json`。
- 规则库继续放在 `analysis/harness_config.json`；`rewrite_plan.json` 只记录本次触发项、证据、目标 beat/segments、一次局部改稿任务和禁止事项。
- 当前阶段先采用 human-in-the-loop 执行；未来可接 agent loop 或 function call。
- 自动重写最多一次，重写后重新 gate，并停止于 `failed_auto_gate`、`needs_manual_triage` 或 `pending_user_review`。

### 第 10 步：项目清理

- 以 `analysis/project_cleanup_plan.md` 为清理入口。
- 当前不直接删除历史文件。
- 先确认 `round5_self_prompt_20260608` 是否为用户实验，再决定归档。
- 旧 prompt、早期 round 报告、重复 distribution-check 报告优先归档。
- `.tokens.txt` 大型生成 token stream 可在确认后删除或保持忽略状态。

## 验收标准

- 能快速定位前 8 卷任意章节。
- 能清晰解释「岛村之刃」的情绪张力机制。
- 能把分析转成可执行写作规则。
- prompt 能引导生成原创中文短篇，而不是贴近复刻。
- review checklist 能识别情绪表达过度直白、对话过度理性化、结尾封闭化、比喻过度文学化等失败模式。
- 文本风格评估器能对 prompt 和 draft 分别输出有用的风险提示。
- Delta 报告能显示生成稿相对 `adachi_pressure`、`adachi_daily`、`shimamura_view`、`analysis_docs` 的距离排序，并清楚标注其相对指标属性。
- Harness 能把明显失败候选筛掉，并把幸存候选标记为 `pending_user_review`。
- Segment Delta 能把候选内部的 daily/pressure 分布定位到片段级，但不作为质量评分。
- Rewrite plan 能把诊断证据翻译成一次局部改稿任务，并保留用户最终 review 权限。

## 边界

- 不输出原文长摘抄。
- 不复刻原文句式。
- 不模仿作者专属表达。
- 不把「剑」解释成固定文学符号。
- 不把统计结果当成风格本体。
- 不把中文译文误判为日文原文风格。
- 不把 Delta 距离误用成质量评分、作者相似度百分比或复刻目标。
- 不把 Segment Delta 或 rewrite plan 误用成质量判断。
- 不让 harness、Codex 或 subagent 替代用户最终 review。
