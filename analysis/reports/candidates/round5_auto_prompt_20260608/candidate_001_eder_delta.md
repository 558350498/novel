# Experimental Eder/Cosine Delta Segment Report

- 草稿：`drafts\candidates\round5_auto_prompt_20260608\candidate_001.md`
- 切片配置：`corpus_slices\slices.json`
- 生成时间：2026-06-08T21:45:22
- 边界：这是片段级归属诊断，不是质量评分或最终审稿。

## Method

- `distance`: cosine distance over z-scored relative-frequency vectors
- `feature_selection`: top 800 reference character n-grams
- `ngram_range`: [1, 2]
- `segment_size`: 1000
- `min_segment_chars`: 500
- `scaling`: z-score using reference segments only
- `classifier`: nearest reference segment plus group mean-distance ranking
- `excluded_groups`: ['analysis_docs']
- `keep_punctuation`: False

## Segment Counts

- reference total: 48
- draft segments: 5

| group | reference segments |
|---|---:|
| `adachi_daily` | 24 |
| `adachi_pressure` | 7 |
| `shimamura_view` | 17 |

## Aggregate

| rank | group | nearest-neighbor votes | mean nearest distance | mean group distance |
|---:|---|---:|---:|---:|
| 1 | `shimamura_view` | 3 | 0.860111 | 1.016454 |
| 2 | `adachi_daily` | 2 | 0.860277 | 0.989047 |
| 3 | `adachi_pressure` | 0 | - | 0.995724 |

## Draft Segment Assignments

| segment | chars | nearest group | nearest distance | group mean-distance ranking |
|---|---:|---|---:|---|
| `draft_p001` | 1000 | `shimamura_view` | 0.853149 | adachi_daily=0.990803；adachi_pressure=1.000304；shimamura_view=1.012157 |
| `draft_p002` | 1000 | `adachi_daily` | 0.891253 | adachi_daily=0.983541；adachi_pressure=1.000881；shimamura_view=1.020398 |
| `draft_p003` | 1000 | `adachi_daily` | 0.829301 | adachi_daily=0.982344；adachi_pressure=1.005912；shimamura_view=1.019089 |
| `draft_p004` | 1000 | `shimamura_view` | 0.844847 | adachi_daily=0.988256；adachi_pressure=1.011238；shimamura_view=1.012346 |
| `draft_p005` | 1467 | `shimamura_view` | 0.882337 | adachi_pressure=0.960284；adachi_daily=1.000291；shimamura_view=1.018278 |

## Feature Sample

`的`, `我`, `是`, `不`, `一`, `了`, `在`, `这`, `有`, `她`, `就`, `来`, `会`, `到`, `也`, `么`, `那`, `着`, `好`, `说`, `很`, `样`, `起`, `人`, `要`

## Notes

- This is an experimental diagnostic, not a quality score.
- Small reference sets make nearest-neighbor votes unstable; use the output as a triage signal.
- Delta-family metrics should stay subordinate to human review and source-shape checks.
