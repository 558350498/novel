# Experimental Eder/Cosine Delta Segment Report

- 草稿：`drafts\candidates\round5_auto_prompt_20260608\candidate_001.md`
- 切片配置：`corpus_slices\slices.json`
- 生成时间：2026-06-08T21:45:43
- 边界：这是片段级归属诊断，不是质量评分或最终审稿。

## Method

- `distance`: cosine distance over z-scored relative-frequency vectors
- `feature_selection`: top 800 reference character n-grams
- `ngram_range`: [1, 2]
- `segment_size`: 500
- `min_segment_chars`: 250
- `scaling`: z-score using reference segments only
- `classifier`: nearest reference segment plus group mean-distance ranking
- `excluded_groups`: ['analysis_docs']
- `keep_punctuation`: False

## Segment Counts

- reference total: 96
- draft segments: 11

| group | reference segments |
|---|---:|
| `adachi_daily` | 49 |
| `adachi_pressure` | 14 |
| `shimamura_view` | 33 |

## Aggregate

| rank | group | nearest-neighbor votes | mean nearest distance | mean group distance |
|---:|---|---:|---:|---:|
| 1 | `adachi_daily` | 5 | 0.857828 | 0.993468 |
| 2 | `adachi_pressure` | 3 | 0.821037 | 0.994937 |
| 3 | `shimamura_view` | 3 | 0.855579 | 1.011243 |

## Draft Segment Assignments

| segment | chars | nearest group | nearest distance | group mean-distance ranking |
|---|---:|---|---:|---|
| `draft_p001` | 500 | `adachi_daily` | 0.847441 | adachi_daily=0.989557；adachi_pressure=1.004994；shimamura_view=1.012312 |
| `draft_p002` | 500 | `shimamura_view` | 0.876515 | adachi_pressure=0.994666；adachi_daily=0.998139；shimamura_view=1.004261 |
| `draft_p003` | 500 | `adachi_daily` | 0.856766 | adachi_daily=0.992426；shimamura_view=1.006319；adachi_pressure=1.007526 |
| `draft_p004` | 500 | `adachi_daily` | 0.849274 | adachi_daily=0.987168；adachi_pressure=0.991747；shimamura_view=1.020396 |
| `draft_p005` | 500 | `adachi_pressure` | 0.835544 | adachi_daily=0.986733；adachi_pressure=1.003671；shimamura_view=1.015683 |
| `draft_p006` | 500 | `adachi_pressure` | 0.810376 | adachi_daily=0.989858；adachi_pressure=1.003155；shimamura_view=1.011104 |
| `draft_p007` | 500 | `adachi_daily` | 0.846302 | adachi_daily=0.99119；shimamura_view=1.00872；adachi_pressure=1.010271 |
| `draft_p008` | 500 | `shimamura_view` | 0.829226 | adachi_daily=0.993733；adachi_pressure=0.999121；shimamura_view=1.009418 |
| `draft_p009` | 500 | `adachi_pressure` | 0.817190 | adachi_pressure=0.954546；adachi_daily=1.003216；shimamura_view=1.017835 |
| `draft_p010` | 500 | `adachi_daily` | 0.889357 | adachi_daily=0.993726；adachi_pressure=0.996874；shimamura_view=1.011337 |
| `draft_p011` | 467 | `shimamura_view` | 0.860996 | adachi_pressure=0.977731；adachi_daily=1.0024；shimamura_view=1.006285 |

## Feature Sample

`的`, `我`, `是`, `不`, `一`, `了`, `在`, `这`, `有`, `她`, `就`, `来`, `会`, `到`, `也`, `么`, `那`, `着`, `好`, `说`, `很`, `样`, `起`, `人`, `要`

## Notes

- This is an experimental diagnostic, not a quality score.
- Small reference sets make nearest-neighbor votes unstable; use the output as a triage signal.
- Delta-family metrics should stay subordinate to human review and source-shape checks.
