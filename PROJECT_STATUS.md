# 《安达与岛村》文本分析与生成辅助项目进度

## 项目目标

建立一套服务于原创中文短篇的文本分析与生成辅助流程：参考《安达与岛村》第 5 卷「岛村之刃」的关系机制和情绪张力结构，但不复刻原文、不模仿专属句式、不长篇摘抄。最终产出可用的写作 prompt、可迁移规则、审稿清单，以及轻量文本风格评估工具。

## 当前进度

### 已完成

- 前 8 卷 txt 已按卷号重命名为 `vol01` 到 `vol08`。
- 已创建工程入口 `README.md`。
- 已创建人工章节索引 `INDEX.md`。
- 已创建机器可读索引 `novel_index.json`。
- 已创建分析目录说明 `analysis/README.md`。
- 已创建轻量文本风格评估器 `tools/style_evaluator.py`。
- 已创建评估词表 `tools/style_lexicon.json`。
- 已创建当前待审稿占位文件 `drafts/current.md`。
- 已创建评估报告目录 `analysis/reports/`，并生成占位稿评估报告 `analysis/reports/current.md`。
- 已生成四份分析产物：
  - `analysis/style_analysis.md`
  - `analysis/transferable_rules.md`
  - `analysis/generation_prompt.md`
  - `analysis/review_checklist.md`
- 已定位核心素材：
  - 文件：`vol05_第五卷_岛村之刃.txt`
  - 核心章：第五卷 第二话「岛村之刃」
  - 范围：第 2446 行到第 2864 行
  - 下一章起点：第 2865 行

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
- 第一版测试稿由 Codex 先生成，写入 `drafts/current.md`。
- 生成后立即运行 `tools/style_evaluator.py --mode draft drafts/current.md --output analysis/reports/current.md`。
- 自动报告只作为风险提示；最终判断采用 Codex 人工 review 与用户人工 review 双审。
- 双审关注两类问题：脚本没有抓到但人工觉得不对的失败模式，以及脚本提示但人工认为是误报的指标。

## 后续计划

### 第 1 步：固定场景测试稿

- 用 `generation_prompt.md` 生成一篇固定场景短篇草稿。
- 放入 `drafts/current.md`。
- 运行 `tools/style_evaluator.py --mode draft drafts/current.md --output analysis/reports/current.md`。
- Codex 先基于 `review_checklist.md` 做一轮人工 review。
- 用户再做一轮人工 review。
- 汇总“脚本漏报”“脚本误报”“prompt 执行偏差”“文本本身问题”。

### 第 2 步：调参

- 根据第一篇测试稿和后续 2 到 3 篇草稿的实际报告，调整 `tools/style_lexicon.json` 的词表和阈值。
- 必要时回改 `analysis/generation_prompt.md` 和 `analysis/review_checklist.md`。
- 保留多指标提示，不引入单一总分裁决。
- 第一版继续不引入 MeCab、Sudachi、Jieba 等重型分词。

### 第 3 步：考虑 Codex hook

等脚本稳定后，再添加 `.codex/hooks.json`。

hook 设计原则：

- 只在 `drafts/current.md` 存在时运行。
- 不存在就静默退出。
- 默认只输出提醒报告，不阻止正常对话。
- 不在每轮对话里制造噪音。

## 验收标准

- 能快速定位前 8 卷任意章节。
- 能清晰解释「岛村之刃」的情绪张力机制。
- 能把分析转成可执行写作规则。
- prompt 能引导生成原创中文短篇，而不是贴近复刻。
- review checklist 能识别情绪表达过度直白、对话过度理性化、结尾封闭化、比喻过度文学化等失败模式。
- 文本风格评估器能对 prompt 和 draft 分别输出有用的风险提示。

## 边界

- 不输出原文长摘抄。
- 不复刻原文句式。
- 不模仿作者专属表达。
- 不把「剑」解释成固定文学符号。
- 不把统计结果当成风格本体。
- 不把中文译文误判为日文原文风格。
