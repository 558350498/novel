# 分析产物目录

这里保存后续围绕「岛村之刃」的写作机制分析与生成辅助文件。

## 已完成产物

- `style_analysis.md`：本章情绪张力机制、意识流模式、对话节奏、日常物件与翻译腔分析。
- `transferable_rules.md`：可迁移写作规则。
- `generation_prompt.md`：用于创作原创「安达第一人称意识流短篇」的 prompt。
- `generation_prompt_round3.md`：Round 3 同场景改稿 prompt，强调长篇失控输出与接收端断续理解。
- `review_checklist.md`：成稿审稿清单。

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
