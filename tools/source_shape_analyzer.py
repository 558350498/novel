from __future__ import annotations

import argparse
import json
import math
import re
import statistics
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PUNCTUATION = "，。！？；：、“”‘’（）《》〈〉「」『』……,.!?;:\"'()[]{}<>-"
SENTENCE_SPLIT_RE = re.compile(r"[。！？!?]+")
SPEAKER_RE = re.compile(r"^\s*([^：:「『“”\"']{1,12})[：:]\s*(.*)$")
QUOTE_START_RE = re.compile(r"^\s*[「『“\"']")


class SourceShapeError(ValueError):
    pass


def resolve_project_path(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def read_text(path: Path) -> str:
    if not path.exists():
        raise SourceShapeError(f"file not found: {path}")
    data = path.read_bytes()
    if data.startswith((b"\xff\xfe", b"\xfe\xff")):
        return data.decode("utf-16")
    if data.startswith(b"\xef\xbb\xbf"):
        return data.decode("utf-8-sig")
    for encoding in ("utf-8", "gb18030", "utf-16"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise SourceShapeError(f"unsupported text encoding: {path}")


def approx_chars(text: str) -> int:
    return len(re.sub(r"\s+", "", text))


def is_dialogue_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if stripped.startswith(("#", "-", "*", "`")):
        return False
    if QUOTE_START_RE.match(stripped):
        return True
    match = SPEAKER_RE.match(stripped)
    return bool(match and match.group(2).strip())


def dialogue_content(line: str) -> str:
    stripped = line.strip()
    match = SPEAKER_RE.match(stripped)
    if match:
        stripped = match.group(2).strip()
    return stripped.strip("「」『』“”\"' ")


def percentile(values: list[int], q: float) -> float:
    if not values:
        return 0.0
    sorted_values = sorted(values)
    index = min(len(sorted_values) - 1, math.ceil(len(sorted_values) * q) - 1)
    return float(sorted_values[index])


def dialogue_length_bins(lengths: list[int]) -> dict[str, dict[str, float | int]]:
    ranges = [
        ("1-5", 1, 5),
        ("6-10", 6, 10),
        ("11-20", 11, 20),
        ("21-40", 21, 40),
        ("41-80", 41, 80),
        ("81-160", 81, 160),
        ("161-320", 161, 320),
        ("321+", 321, None),
    ]
    bins: dict[str, dict[str, float | int]] = {}
    total = len(lengths)
    for label, low, high in ranges:
        count = sum(length >= low and (high is None or length <= high) for length in lengths)
        bins[label] = {"count": count, "pct": round(count * 100.0 / total, 1) if total else 0.0}
    return bins


def text_shape(text: str) -> dict[str, Any]:
    lines = text.splitlines()
    non_empty = [line for line in lines if line.strip()]
    line_lengths = [approx_chars(line) for line in non_empty]
    dialogue_lines = [line for line in non_empty if is_dialogue_line(line)]
    dialogue_lengths = [approx_chars(dialogue_content(line)) for line in dialogue_lines]
    sentences = [part.strip() for part in SENTENCE_SPLIT_RE.split(text) if part.strip()]
    sentence_lengths = [approx_chars(sentence) for sentence in sentences]
    punctuation = Counter(ch for ch in text if ch in PUNCTUATION)
    char_count = approx_chars(text)

    return {
        "chars_no_ws": char_count,
        "line_count": len(lines),
        "nonempty_lines": len(non_empty),
        "dialogue_lines": len(dialogue_lines),
        "dialogue_ratio": round(len(dialogue_lines) / len(non_empty), 4) if non_empty else 0.0,
        "line_avg": round(sum(line_lengths) / len(line_lengths), 2) if line_lengths else 0.0,
        "line_p90": round(percentile(line_lengths, 0.9), 2),
        "line_max": max(line_lengths) if line_lengths else 0,
        "sentence_count": len(sentence_lengths),
        "sentence_avg": round(sum(sentence_lengths) / len(sentence_lengths), 2) if sentence_lengths else 0.0,
        "sentence_median": round(statistics.median(sentence_lengths), 2) if sentence_lengths else 0.0,
        "sentence_p90": round(percentile(sentence_lengths, 0.9), 2),
        "dialogue_avg": round(sum(dialogue_lengths) / len(dialogue_lengths), 2) if dialogue_lengths else 0.0,
        "dialogue_max": max(dialogue_lengths) if dialogue_lengths else 0,
        "dialogue_ge_40": sum(length >= 40 for length in dialogue_lengths),
        "dialogue_ge_80": sum(length >= 80 for length in dialogue_lengths),
        "dialogue_ge_200": sum(length >= 200 for length in dialogue_lengths),
        "dialogue_bins": dialogue_length_bins(dialogue_lengths),
        "punctuation_per_1000": {
            ch: round(count * 1000.0 / char_count, 2) if char_count else 0.0
            for ch, count in sorted(punctuation.items())
        },
    }


def chapter_text(volume: dict[str, Any], chapter_index: int) -> tuple[str, int]:
    path = ROOT / "data" / "raw" / volume["file"]
    lines = read_text(path).splitlines()
    chapter = volume["chapters"][chapter_index]
    end_before_line = (
        volume["chapters"][chapter_index + 1]["line"]
        if chapter_index + 1 < len(volume["chapters"])
        else len(lines) + 1
    )
    start_line = int(chapter["line"])
    return "\n".join(lines[start_line - 1 : end_before_line - 1]), end_before_line


def build_report(index_path: Path, draft_paths: list[Path]) -> dict[str, Any]:
    index = json.loads(read_text(index_path))
    chapters: list[dict[str, Any]] = []
    for volume in index["volumes"]:
        for chapter_index, chapter in enumerate(volume["chapters"]):
            text, end_before_line = chapter_text(volume, chapter_index)
            item = text_shape(text)
            item.update({
                "volume": volume["volume"],
                "chapter_index": chapter_index + 1,
                "title": chapter["title"],
                "file": str(Path("data") / "raw" / volume["file"]),
                "start_line": chapter["line"],
                "end_before_line": end_before_line,
            })
            chapters.append(item)

    drafts = []
    for draft_path in draft_paths:
        resolved = resolve_project_path(draft_path)
        if resolved.exists():
            item = text_shape(read_text(resolved))
            item["path"] = str(draft_path)
            drafts.append(item)

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "index_path": str(index_path),
        "chapter_count": len(chapters),
        "chapters": chapters,
        "drafts": drafts,
        "notes": [
            "This report records statistics and line ranges only; it does not quote source prose.",
            "Character counts remove whitespace.",
        ],
    }


def find_chapter(report: dict[str, Any], *, volume: int, start_line: int | None = None, chapter_index: int | None = None) -> dict[str, Any] | None:
    for chapter in report["chapters"]:
        if chapter["volume"] != volume:
            continue
        if start_line is not None and chapter["start_line"] == start_line:
            return chapter
        if chapter_index is not None and chapter["chapter_index"] == chapter_index:
            return chapter
    return None


def render_bins(bins: dict[str, dict[str, float | int]]) -> str:
    return "；".join(f"{label}: {values['count']} ({values['pct']}%)" for label, values in bins.items())


def render_markdown(report: dict[str, Any]) -> str:
    v5_second = find_chapter(report, volume=5, start_line=2446)
    v2_second = find_chapter(report, volume=2, chapter_index=2)
    main_chapters = [
        chapter for chapter in report["chapters"]
        if chapter["chars_no_ws"] > 1000 and "后记" not in chapter["title"] and "插图" not in chapter["title"]
    ]
    char_values = [chapter["chars_no_ws"] for chapter in main_chapters]
    median_chars = statistics.median(char_values) if char_values else 0
    mean_chars = sum(char_values) / len(char_values) if char_values else 0.0

    lines = [
        "# 全篇章形状分析报告",
        "",
        f"- 索引：`{report['index_path']}`",
        f"- 生成时间：{report['generated_at']}",
        "- 边界：只记录统计与行号，不摘录正文。",
        "",
        "## 关键回答",
        "",
    ]
    if v5_second:
        lines.append(
            f"- 当前场景参照的第五卷第二话「岛村之刃」：约 `{v5_second['chars_no_ws']}` 个非空白字符，"
            f"行号 `{v5_second['start_line']}` 到 `{v5_second['end_before_line']}` 前。"
        )
    if v2_second:
        lines.append(
            f"- 如果“第二章”指第二卷「安达Q」：约 `{v2_second['chars_no_ws']}` 个非空白字符，"
            f"行号 `{v2_second['start_line']}` 到 `{v2_second['end_before_line']}` 前。"
        )
    lines.extend([
        f"- 主体章节样本数：`{len(main_chapters)}`；中位长度 `{median_chars:.0f}`；平均长度 `{mean_chars:.1f}`。",
        "",
        "## 当前草稿对照",
        "",
        "| 草稿 | 字符数 | 非空行 | 对话占比 | 最长台词 | 台词 >=200 | 台词分布 |",
        "|---|---:|---:|---:|---:|---:|---|",
    ])
    for draft in report["drafts"]:
        lines.append(
            f"| `{draft['path']}` | {draft['chars_no_ws']} | {draft['nonempty_lines']} | "
            f"{draft['dialogue_ratio']:.1%} | {draft['dialogue_max']} | {draft['dialogue_ge_200']} | "
            f"{render_bins(draft['dialogue_bins'])} |"
        )

    lines.extend([
        "",
        "## 重点章节",
        "",
        "| 章节 | 行号 | 字符数 | 非空行 | 对话占比 | 最长台词 | 台词 >=80 | 台词 >=200 |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ])
    focus = [chapter for chapter in report["chapters"] if chapter["volume"] == 5 and chapter["start_line"] in {483, 2446, 2865, 4628}]
    if v2_second:
        focus.insert(0, v2_second)
    for chapter in focus:
        lines.append(
            f"| {chapter['title']} | {chapter['start_line']}-{chapter['end_before_line'] - 1} | "
            f"{chapter['chars_no_ws']} | {chapter['nonempty_lines']} | {chapter['dialogue_ratio']:.1%} | "
            f"{chapter['dialogue_max']} | {chapter['dialogue_ge_80']} | {chapter['dialogue_ge_200']} |"
        )

    lines.extend([
        "",
        "## 解释",
        "",
        "- Round 3 有长台词信号，但总篇幅仍明显低于当前场景参照章节。",
        "- 后续候选应同时覆盖日常/过渡与电话高压，不应只放大高潮段。",
        "- 台词分布用于辅助人工 review，不单独判定文本成败。",
    ])
    return "\n".join(lines) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze source chapter surface shape without quoting prose.")
    parser.add_argument("--index", type=Path, default=Path("novel_index.json"), help="Novel index JSON path.")
    parser.add_argument("--output-prefix", type=Path, required=True, help="Output path prefix without extension.")
    parser.add_argument(
        "--draft",
        action="append",
        type=Path,
        dest="drafts",
        help="Optional draft path to include. Defaults to current, round2, and round3 if present.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    index_path = resolve_project_path(args.index)
    output_prefix = resolve_project_path(args.output_prefix)
    drafts = args.drafts or [Path("drafts/current.md"), Path("drafts/round2.md"), Path("drafts/round3.md")]
    try:
        report = build_report(index_path, drafts)
        markdown = render_markdown(report)
    except (SourceShapeError, OSError, json.JSONDecodeError, KeyError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    json_path = output_prefix.with_suffix(".json")
    markdown_path = output_prefix.with_suffix(".md")
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(markdown, encoding="utf-8")
    print(markdown, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
