# Novel Style Mechanism Lab

一个用于中文轻小说文本机制分析与生成式写作审稿的实验项目。

## 目标

本项目不复刻原文，不模仿专属句式，而是抽取可迁移的叙事机制：
- 关系错位
- 第一人称意识流反刍
- 轻回应造成的情绪张力
- 日常物件承载情绪
- 结尾未解决感

## Pipeline

1. 建立章节索引
2. 人工分析目标章节机制
3. 转换为 transferable rules
4. 生成 writing prompt
5. 用 style_evaluator 检查草稿风险
6. 人工 review 漏报/误报
7. 用 diff/review 记录失败模式
8. 用 Delta 相对距离评估观察草稿与参照组的表层距离
9. 迭代 prompt、词表、切片和阈值

## Current Status

- 前 8 卷正文已放入 `data/raw/`，根目录索引用逻辑文件名导航。
- 第 5 卷「岛村之刃」已定位为核心分析对象：第 2446 行到第 2864 行前。
- 四份分析产物已完成：
  - `analysis/style_analysis.md`
  - `analysis/transferable_rules.md`
  - `analysis/generation_prompt.md`
  - `analysis/review_checklist.md`
- 第一轮固定场景测试稿已生成到 `drafts/current.md`。
- 已生成自动评估报告、Codex 人工 review 和 diff 讨论文档。
- Delta v1 已可运行：比较生成稿相对 `adachi_pressure`、`adachi_daily`、`shimamura_view`、`analysis_docs` 的表层文体距离。

## Project Navigation

| 用途 | 入口 |
|---|---|
| 快速定位总表 | [INDEX.md](./INDEX.md) |
| 当前进度与计划 | [PROJECT_STATUS.md](./PROJECT_STATUS.md) |
| 分析产物目录 | [analysis/README.md](./analysis/README.md) |
| 报告目录 | [analysis/reports/README.md](./analysis/reports/README.md) |
| 当前测试稿 | [drafts/current.md](./drafts/current.md) |
| Delta 切片配置 | [corpus_slices/slices.json](./corpus_slices/slices.json) |
| Delta 工具 | [tools/delta_evaluator.py](./tools/delta_evaluator.py) |
| 核心章节 | [data/raw/vol05_第五卷_岛村之刃.txt:2446](./data/raw/vol05_第五卷_岛村之刃.txt#L2446) |

## Usage

规则型评估器：

```powershell
python tools/style_evaluator.py --mode draft drafts/current.md --output analysis/reports/current.md
```

Delta v1 相对距离评估：

```powershell
python tools/delta_evaluator.py --draft drafts/current.md --slices corpus_slices/slices.json --output-prefix analysis/reports/delta_current
```

Delta 只作为相对指标，不作为质量评分、作者相似度百分比或复刻目标。
