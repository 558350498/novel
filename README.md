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
9. 用轻量 harness 筛选候选草稿
10. 用 `md + json` 候选协议增强 gate 可读结构
11. 用 corpus tokenizer 做词表发现和语料拓展
12. 迭代 prompt、词表、切片、阈值和用户反馈记录

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
- Harness v1 已可运行：先做已有候选评分器，只筛明显失败样本，不替代用户 review。
- 全篇章形状分析已可运行，用于把“文本太短”和“日常/高压比例”变成可回归指标。
- Productization v1 已锁定为 single-kernel tuning lab：不做任意风格切换，优先把 gate 调成可靠的失败样本过滤器。
- 下一步候选协议采用 Markdown 正文 + JSON 结构标注，优先解决“岛村回应解释化”无法稳定识别的问题。
- Corpus tokenizer v1 已可运行：当前使用稳定 `regex` fallback，并预留可选 `jieba`、OpenAI `tiktoken` 与 Hugging Face/DeepSeek tokenizer 引擎。

## Project Navigation

| 用途 | 入口 |
|---|---|
| 快速定位总表 | [INDEX.md](./INDEX.md) |
| 当前进度与计划 | [PROJECT_STATUS.md](./PROJECT_STATUS.md) |
| 分析产物目录 | [analysis/README.md](./analysis/README.md) |
| 报告目录 | [analysis/reports/README.md](./analysis/reports/README.md) |
| Harness v1 计划 | [analysis/harness_plan.md](./analysis/harness_plan.md) |
| Harness v1 配置 | [analysis/harness_config.json](./analysis/harness_config.json) |
| Harness v1 工具 | [tools/light_harness.py](./tools/light_harness.py) |
| Gate v1 产品化计划 | [analysis/productization_gate_v1.md](./analysis/productization_gate_v1.md) |
| Novel Gate Harness skill | [skills/novel-gate-harness/SKILL.md](./skills/novel-gate-harness/SKILL.md) |
| Corpus tokenizer | [tools/corpus_tokenizer.py](./tools/corpus_tokenizer.py) |
| Lexicon taxonomy | [analysis/lexicon_taxonomy.md](./analysis/lexicon_taxonomy.md) |
| Corpus profiler | [tools/corpus_profiler.py](./tools/corpus_profiler.py) |
| Adachi pressure corpus profile | [analysis/reports/corpus_profile_adachi_pressure.md](./analysis/reports/corpus_profile_adachi_pressure.md) |
| 第 5 卷 tokenization 报告 | [analysis/reports/tokenization_vol05.md](./analysis/reports/tokenization_vol05.md) |
| 「岛村之刃」tokenization 报告 | [analysis/reports/tokenization_vol05_shimamura_blade.md](./analysis/reports/tokenization_vol05_shimamura_blade.md) |
| 「岛村之刃」DeepSeek V4 tokenizer 报告 | [analysis/reports/tokenization_vol05_shimamura_blade_deepseek_v4_flash.md](./analysis/reports/tokenization_vol05_shimamura_blade_deepseek_v4_flash.md) |
| 全篇章形状分析工具 | [tools/source_shape_analyzer.py](./tools/source_shape_analyzer.py) |
| Round 4 长篇候选 prompt | [analysis/generation_prompt_round4.md](./analysis/generation_prompt_round4.md) |
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

全篇章形状分析：
```powershell
python tools/source_shape_analyzer.py --index novel_index.json --output-prefix analysis/reports/source_chapter_shape
```

Harness v1：
```powershell
python tools/light_harness.py --run-id existing_rounds_audit --candidates drafts/current.md drafts/round2.md drafts/round3.md --slices corpus_slices/slices.json --config analysis/harness_config.json --reports-root analysis/reports/candidates
```

Harness v1 暂不自动生成候选；只把通过自动 gate 的候选标记为 `pending_user_review`。

Corpus tokenizer：
```powershell
python tools/corpus_tokenizer.py --source data/raw/vol05_第五卷_岛村之刃.txt --output-prefix analysis/reports/tokenization_vol05 --engine regex
```

如本机安装 `jieba`，可将 `--engine regex` 改为 `--engine jieba`。
如本机安装 OpenAI `tiktoken`，可使用：

```powershell
python tools/corpus_tokenizer.py --source data/raw/vol05_第五卷_岛村之刃.txt --output-prefix analysis/reports/tokenization_vol05_tiktoken --engine tiktoken --tiktoken-encoding o200k_base
```

`tiktoken` 只用于模型侧 tokenization 对照，不作为中文语言学分词。

如本机安装 `transformers/tokenizers` 并有模型 tokenizer 文件，可使用 DeepSeek tokenizer 对照：

```powershell
python tools/corpus_tokenizer.py --source data/raw/vol05_第五卷_岛村之刃.txt --output-prefix analysis/reports/tokenization_vol05_deepseek --engine hf --hf-model deepseek-ai/DeepSeek-V3
```

DeepSeek tokenizer 同样属于模型侧 tokenization；DeepSeek 写作手感主要来自模型与训练/对齐，不是 tokenizer 单独决定。

当前已安装 Hugging Face tokenizer 依赖到项目本地 `.deps/hf-tokenizer2/`。运行 DeepSeek tokenizer 命令时，需要让 Python 能找到该目录，例如：

```powershell
$env:PYTHONPATH='C:\Users\33625\Documents\novel\.deps\hf-tokenizer2'
```

Corpus profiler：

```powershell
python tools/corpus_profiler.py --slices corpus_slices/slices.json --output-prefix analysis/reports/corpus_profile_adachi_pressure --target-id adachi_pressure
```

Profiler 生成可解释特征权重，不做 RAG、不召回原文、不作为质量评分。
