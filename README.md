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
7. 迭代词表和阈值

## Usage

python tools/style_evaluator.py --mode draft drafts/current.md --output analysis/reports/current.md
