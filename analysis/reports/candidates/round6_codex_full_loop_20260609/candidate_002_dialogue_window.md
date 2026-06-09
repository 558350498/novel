# Dialogue Window Report

- draft: `drafts\candidates\round6_codex_full_loop_20260609\candidate_002.md`
- candidate_json: `drafts\candidates\round6_codex_full_loop_20260609\candidate_002.json`
- generated_at: 2026-06-10T02:00:25
- speakers: `adachi, shimamura`
- preferred_pair_units_max: 2
- hard_pair_units_max: 5
- budget_source: `source_slice_profile`

## Summary

- dialogue_lines: 121
- contiguous_dialogue_runs: 27
- windows_with_checked_speakers: 46
- dual_alternating_windows: 19
- max_pair_units: 7
- alternating_max_pair_units: 7
- hard_exceeded_count: 3
- warn_count: 28
- single_speaker_hard_exceeded_count: 2
- alternating_hard_exceeded_count: 1

## Budget

- target_pair_units_max: 1
- preferred_pair_units_max: 2
- hard_pair_units_max: 5
- policy: `source_profile_with_configured_hard_floor`
- source_slice_id: `adachi_pressure`
- source_label: `关系失衡核心段`
- source_dialogue_lines: 60
- source_contiguous_dialogue_runs: 38
- source_pair_units_p75: 1.0
- source_pair_units_p90: 2.0
- source_pair_units_max: 3

## Per Speaker

| speaker | windows | max pair units | hard exceeded | warn |
|---|---:|---:|---:|---:|
| `adachi` | 23 | 7 | 1 | 8 |
| `shimamura` | 23 | 7 | 1 | 10 |

## Windows

| speaker | run | lines | window utterances | pair units | status |
|---|---:|---|---:|---:|---|
| `shimamura` | 1 | 9-9 | 1 | 1 | `ok` |
| `adachi` | 2 | 15-21 | 4 | 2 | `ok` |
| `shimamura` | 2 | 19-19 | 1 | 1 | `ok` |
| `shimamura` | 3 | 29-29 | 1 | 1 | `ok` |
| `shimamura` | 4 | 45-47 | 2 | 1 | `ok` |
| `adachi` | 5 | 51-51 | 1 | 1 | `ok` |
| `shimamura` | 6 | 63-63 | 1 | 1 | `ok` |
| `adachi` | 6 | 65-65 | 1 | 1 | `ok` |
| `shimamura` | 7 | 69-75 | 4 | 2 | `ok` |
| `adachi` | 7 | 73-73 | 1 | 1 | `ok` |
| `adachi` | 8 | 81-81 | 1 | 1 | `ok` |
| `shimamura` | 9 | 87-93 | 4 | 2 | `ok` |
| `adachi` | 9 | 91-91 | 1 | 1 | `ok` |
| `adachi` | 10 | 99-107 | 5 | 3 | `warn` |
| `shimamura` | 10 | 101-109 | 5 | 3 | `warn` |
| `adachi` | 11 | 149-149 | 1 | 1 | `ok` |
| `shimamura` | 12 | 159-159 | 1 | 1 | `ok` |
| `adachi` | 13 | 165-165 | 1 | 1 | `ok` |
| `adachi` | 14 | 179-187 | 5 | 3 | `warn` |
| `shimamura` | 14 | 181-189 | 5 | 3 | `warn` |
| `adachi` | 15 | 193-209 | 9 | 5 | `warn` |
| `shimamura` | 15 | 195-207 | 7 | 4 | `warn` |
| `shimamura` | 16 | 213-221 | 5 | 3 | `warn` |
| `adachi` | 16 | 215-219 | 3 | 2 | `ok` |
| `adachi` | 17 | 229-237 | 5 | 3 | `warn` |
| `shimamura` | 17 | 231-239 | 5 | 3 | `warn` |
| `adachi` | 18 | 243-255 | 7 | 4 | `warn` |
| `shimamura` | 18 | 245-253 | 5 | 3 | `warn` |
| `shimamura` | 19 | 259-267 | 5 | 3 | `warn` |
| `adachi` | 19 | 261-269 | 5 | 3 | `warn` |
| `shimamura` | 20 | 273-283 | 6 | 3 | `warn` |
| `adachi` | 20 | 277-281 | 3 | 2 | `ok` |
| `adachi` | 21 | 289-289 | 1 | 1 | `ok` |
| `shimamura` | 21 | 291-291 | 1 | 1 | `ok` |
| `adachi` | 22 | 303-315 | 7 | 4 | `warn` |
| `shimamura` | 22 | 305-313 | 5 | 3 | `warn` |
| `shimamura` | 23 | 319-323 | 3 | 2 | `ok` |
| `adachi` | 23 | 321-325 | 3 | 2 | `ok` |
| `shimamura` | 24 | 331-357 | 14 | 7 | `hard_exceeded` |
| `adachi` | 24 | 335-359 | 13 | 7 | `hard_exceeded` |
| `shimamura` | 25 | 363-381 | 10 | 5 | `warn` |
| `adachi` | 25 | 367-383 | 9 | 5 | `warn` |
| `shimamura` | 26 | 387-389 | 2 | 1 | `ok` |
| `adachi` | 26 | 391-391 | 1 | 1 | `ok` |
| `shimamura` | 27 | 397-403 | 4 | 2 | `ok` |
| `adachi` | 27 | 401-401 | 1 | 1 | `ok` |

## Dual Alternating Windows

| run | chain | lines | utterances | pair units | status | speakers |
|---:|---:|---|---:|---:|---|---|
| 2 | 1 | 17-21 | 3 | 2 | `ok` | `adachi/shimamura/adachi` |
| 6 | 1 | 63-65 | 2 | 1 | `ok` | `shimamura/adachi` |
| 7 | 1 | 71-75 | 3 | 2 | `ok` | `shimamura/adachi/shimamura` |
| 9 | 1 | 89-93 | 3 | 2 | `ok` | `shimamura/adachi/shimamura` |
| 10 | 1 | 99-109 | 6 | 3 | `warn` | `adachi/shimamura/adachi/shimamura/adachi/shimamura` |
| 14 | 1 | 179-189 | 6 | 3 | `warn` | `adachi/shimamura/adachi/shimamura/adachi/shimamura` |
| 15 | 1 | 193-209 | 9 | 5 | `warn` | `adachi/shimamura/adachi/shimamura/adachi/shimamura/adachi/shimamura/adachi` |
| 16 | 1 | 213-221 | 5 | 3 | `warn` | `shimamura/adachi/shimamura/adachi/shimamura` |
| 17 | 1 | 229-239 | 6 | 3 | `warn` | `adachi/shimamura/adachi/shimamura/adachi/shimamura` |
| 18 | 1 | 243-255 | 7 | 4 | `warn` | `adachi/shimamura/adachi/shimamura/adachi/shimamura/adachi` |
| 19 | 1 | 259-269 | 6 | 3 | `warn` | `shimamura/adachi/shimamura/adachi/shimamura/adachi` |
| 20 | 1 | 275-283 | 5 | 3 | `warn` | `shimamura/adachi/shimamura/adachi/shimamura` |
| 21 | 1 | 289-291 | 2 | 1 | `ok` | `adachi/shimamura` |
| 22 | 1 | 303-315 | 7 | 4 | `warn` | `adachi/shimamura/adachi/shimamura/adachi/shimamura/adachi` |
| 23 | 1 | 319-325 | 4 | 2 | `ok` | `shimamura/adachi/shimamura/adachi` |
| 24 | 1 | 333-359 | 14 | 7 | `hard_exceeded` | `shimamura/adachi/shimamura/adachi/shimamura/adachi/shimamura/adachi/shimamura/adachi/shimamura/adachi/shimamura/adachi` |
| 25 | 1 | 365-383 | 10 | 5 | `warn` | `shimamura/adachi/shimamura/adachi/shimamura/adachi/shimamura/adachi/shimamura/adachi` |
| 26 | 1 | 389-391 | 2 | 1 | `ok` | `shimamura/adachi` |
| 27 | 1 | 399-403 | 3 | 2 | `ok` | `shimamura/adachi/shimamura` |

## Boundary

This report only localizes dialogue-run shape. It is not a quality score.
