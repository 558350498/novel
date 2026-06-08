# Lexicon Taxonomy v1

用途：把词表拓展从项目内坏味道标签，改成可泛化的语言学维度，再映射回当前作品的 gate。

## 原则

- 底层 taxonomy 要泛化：能用于不同文本项目。
- 项目 gate 要特化：只服务当前 single-kernel tuning lab。
- 高频词不是风格本体；词表候选必须经过用户 review 或回归验证。
- 分词和 n-gram 只负责发现候选，不直接裁决文学质量。
- OpenAI `tiktoken` 可用于模型侧 tokenization 对照，但不能替代中文词法或话语层分类。
- DeepSeek/Hugging Face tokenizer 也只作为模型侧 tokenization 对照；写作能力主要来自模型和训练/对齐，不来自 tokenizer 本身。单个模型 token 解码时可能出现 byte 片段或 `�`，不能把它当作语言学词。

## 分类

| Taxonomy | 语言学依据 | 当前项目映射 |
|---|---|---|
| `affect_intensity` | LIWC affect；Appraisal attitude/graduation | 过载表达、情绪直白、过度文学化 |
| `stance_uncertainty` | stance markers；tentative；negation；engagement | 含混、自我修正、安达失败传达 |
| `cognitive_explanation` | cognitive process；causation；insight | 解释化泄漏、分析概念泄漏、岛村回应解释化 |
| `dialogic_alignment` | engagement；stance alignment；turn-taking | 接收端错位、只接住表层词 |
| `concrete_grounding` | perceptual/body/object/space grounding | 日常物件承载、身体感承载 |
| `closure_resolution` | discourse closure；narrative resolution；certainty | 封闭结尾、关系过早解决 |
| `prompt_boundary` | instruction boundary；copyright/style constraints | prompt 复刻风险、边界提示 |

机器可读配置见 `../tools/lexicon_taxonomy.json`。

## 为什么不用项目标签做底层分类

`过载表达`、`接收端错位`、`解释化泄漏`、`日常物件`、`封闭结尾` 很适合做当前作品的 gate 语言，但它们不是稳定语言学类别。

例如：

- `过载表达` 应拆成 affect、intensity、repetition、turn length、stance failure。
- `接收端错位` 不是单纯词表，而是 dialogic alignment 和 turn-taking 结构。
- `解释化泄漏` 包含 cognitive/causal/insight 词，也包含叙事层总结行为。
- `日常物件` 属于 concrete grounding，但不同项目可换成身体、空间、感官、职业物件。
- `封闭结尾` 是 discourse-level resolution，不只是几个和解词。

## 使用方式

1. 用 `tools/corpus_tokenizer.py` 生成 tokenization 报告。
2. 看 taxonomy category hits，而不是只看 top tokens。
3. 用 `tools/corpus_profiler.py` 看 taxonomy/shape 维度是否真的区分目标参照组。
4. 把候选词先放入 taxonomy 维度。
5. 再判断它是否应映射到当前 gate。
6. 只有经过用户 review 或候选回归验证后，才加入 `tools/style_lexicon.json`。

## 当前项目映射

当前 kernel 里：

- `affect_intensity` 高，但 `stance_uncertainty` 低：可能太直白、太会表达。
- `cognitive_explanation` 出现在岛村台词中：高优先级 triage。
- `dialogic_alignment` 过准：岛村过度理解，kernel 塌陷。
- `concrete_grounding` 低：日常段不足，爆发缺少承载。
- `closure_resolution` 在结尾高：关系被过早解决。
