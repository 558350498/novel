# Corpus Profile v1

- slices: `corpus_slices\slices.json`
- target: `adachi_pressure`
- generated: 2026-06-08T13:59:18
- boundary: feature weights assist review decisions; they do not judge quality.

## Contrast Weights

| rank | feature | direction | target | others mean | effect |
|---:|---|---|---:|---:|---:|
| 1 | `shape.dialogue_ge_200` | higher_in_target | 1.0 | 0.0 | 2.309401 |
| 2 | `shape.dialogue_max` | higher_in_target | 2898.0 | 108.0 | 2.309115 |
| 3 | `taxonomy.cognitive_explanation.per_1000` | lower_in_target | 2.767417 | 3.622036 | -1.125295 |
| 4 | `shape.char_count` | lower_in_target | 8311.0 | 17815.666667 | -1.08955 |
| 5 | `taxonomy.dialogic_alignment.per_1000` | lower_in_target | 0.0 | 0.063257 | -0.998398 |
| 6 | `shape.sentence_avg` | lower_in_target | 18.7881 | 20.6842 | -0.969158 |
| 7 | `shape.sentence_p90` | lower_in_target | 33.0 | 35.666667 | -0.843274 |
| 8 | `taxonomy.prompt_boundary.per_1000` | lower_in_target | 0.0 | 1.70472 | -0.807001 |
| 9 | `taxonomy.concrete_grounding.per_1000` | lower_in_target | 3.248707 | 5.951008 | -0.691461 |
| 10 | `taxonomy.closure_resolution.per_1000` | lower_in_target | 0.120322 | 0.423228 | -0.589551 |
| 11 | `taxonomy.affect_intensity.per_1000` | higher_in_target | 2.647094 | 1.797044 | 0.47961 |
| 12 | `taxonomy.stance_uncertainty.per_1000` | lower_in_target | 19.010949 | 21.106927 | -0.458941 |
| 13 | `shape.dialogue_ratio` | higher_in_target | 0.2857 | 0.254933 | 0.224727 |

## Group Taxonomy Profiles

### adachi_pressure - 关系失衡核心段

- chars: 8311

| taxonomy | count | per 1000 | top terms |
|---|---:|---:|---|
| `affect_intensity` | 22 | 2.647094 | `喜欢`×11、`痛苦`×5、`嫉妒`×3、`吃醋`×1、`害怕`×1、`崩溃`×1 |
| `stance_uncertainty` | 158 | 19.010949 | `可是`×24、`不要`×22、`没有`×21、`不是`×17、`不会`×10、`可能`×8 |
| `cognitive_explanation` | 23 | 2.767417 | `因为`×11、`所以`×10、`我的意思是`×1、`其实`×1 |
| `dialogic_alignment` | 0 | 0.0 | 无 |
| `concrete_grounding` | 27 | 3.248707 | `电话`×9、`手机`×6、`门`×3、`房间`×2、`枕头`×2、`空调`×2 |
| `closure_resolution` | 1 | 0.120322 | `解决`×1 |
| `prompt_boundary` | 0 | 0.0 | 无 |

Top CJK trigrams:

`我希望`×14, `的事情`×13, `为什么`×13, `我不要`×12, `岛村的`×11, `岛村我`×11, `在一起`×10, `希望你`×10, `游泳池`×10, `可是我`×9, `那个女`×9, `个女生`×9

### adachi_daily - 关系错位前置段

- chars: 28171

| taxonomy | count | per 1000 | top terms |
|---|---:|---:|---|
| `affect_intensity` | 11 | 0.390472 | `喜欢`×4、`不安`×3、`命运`×1、`害怕`×1、`永恒`×1、`痛苦`×1 |
| `stance_uncertainty` | 476 | 16.896809 | `没有`×77、`不是`×46、`不过`×44、`不会`×43、`好像`×40、`应该`×36 |
| `cognitive_explanation` | 72 | 2.55582 | `因为`×36、`所以`×28、`其实`×7、`我并不是`×1 |
| `dialogic_alignment` | 1 | 0.035497 | `太快了`×1 |
| `concrete_grounding` | 89 | 3.159277 | `门`×17、`电话`×16、`窗`×10、`房间`×8、`手指`×6、`风扇`×6 |
| `closure_resolution` | 1 | 0.035497 | `解决`×1 |
| `prompt_boundary` | 2 | 0.070995 | `一模一样`×2 |

Top CJK trigrams:

`的时候`×28, `不知道`×23, `的事情`×18, `烟火大`×17, `火大会`×17, `是因为`×15, `的声音`×15, `自己的`×14, `一起去`×12, `我还是`×12, `的妹妹`×12, `我觉得`×12

### shimamura_view - 岛村平稳叙述段

- chars: 18794

| taxonomy | count | per 1000 | top terms |
|---|---:|---:|---|
| `affect_intensity` | 7 | 0.372459 | `喜欢`×5、`害怕`×2 |
| `stance_uncertainty` | 339 | 18.037672 | `没有`×51、`不过`×30、`不是`×27、`好像`×23、`应该`×22、`不会`×18 |
| `cognitive_explanation` | 75 | 3.990635 | `因为`×38、`所以`×35、`其实`×2 |
| `dialogic_alignment` | 0 | 0.0 | 无 |
| `concrete_grounding` | 50 | 2.660424 | `门`×17、`电话`×8、`房间`×7、`鞋`×5、`手指`×4、`地板`×2 |
| `closure_resolution` | 0 | 0.0 | 无 |
| `prompt_boundary` | 2 | 0.106417 | `一模一样`×2 |

Top CJK trigrams:

`的母亲`×43, `安达的`×39, `达的母`×26, `的时候`×18, `自己的`×18, `的样子`×16, `游泳池`×15, `健身房`×14, `很奇怪`×14, `是因为`×14, `三温暖`×14, `了一下`×13

### analysis_docs - 分析腔参照文档

- chars: 6482

| taxonomy | count | per 1000 | top terms |
|---|---:|---:|---|
| `affect_intensity` | 30 | 4.628201 | `嫉妒`×8、`崩溃`×4、`救赎`×2、`永恒`×2、`深渊`×2、`痛苦`×2 |
| `stance_uncertainty` | 184 | 28.386301 | `不要`×53、`没有`×53、`不是`×35、`只是`×10、`应该`×6、`稍微`×4 |
| `cognitive_explanation` | 28 | 4.319654 | `情绪张力`×6、`机制`×5、`潜台词`×4、`表层问题`×3、`轻回应`×3、`因为`×3 |
| `dialogic_alignment` | 1 | 0.154273 | `我不太懂`×1 |
| `concrete_grounding` | 78 | 12.033323 | `手机`×10、`掌心`×10、`电话`×10、`屏幕`×9、`手指`×8、`喉咙`×6 |
| `closure_resolution` | 8 | 1.234187 | `解决`×5、`安心`×2、`和好`×1 |
| `prompt_boundary` | 32 | 4.936748 | `复刻原文`×5、`原创`×5、`机制`×5、`照搬原文`×3、`可迁移`×3、`不要复刻`×2 |

Top CJK trigrams:

`岛村没`×16, `村没有`×16, `安达的`×13, `岛村的`×11, `不要写`×10, `不要让`×10, `而不是`×9, `要写成`×8, `是岛村`×7, `岛村不`×7, `情绪张`×6, `绪张力`×6

## How To Use

- High positive effects mark dimensions unusually strong in the target group.
- High negative effects mark dimensions unusually weak in the target group.
- Convert only reviewed dimensions into gate changes; do not tune solely from this report.
