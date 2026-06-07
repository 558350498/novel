from __future__ import annotations

import argparse
import json
import math
import re
import statistics
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PUNCTUATION = set("，。！？；：、“”‘’（）《》〈〉「」『』…—,.!?;:\"'()[]{}<>-")
SENTENCE_SPLIT_RE = re.compile(r"[。！？!?]+")


class DeltaError(ValueError):
    pass


@dataclass
class TextStats:
    char_count: int
    sentence_count: int
    sentence_avg: float
    sentence_median: float
    sentence_p90: float


def resolve_project_path(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return ROOT / candidate


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def read_text(path: Path) -> str:
    if not path.exists():
        raise DeltaError(f"file not found: {path}")
    data = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-8", "utf-16"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise DeltaError(f"unsupported text encoding: {path}")


def read_slice(slice_config: dict[str, Any]) -> str:
    if "path" not in slice_config:
        raise DeltaError("slice is missing required field: path")

    path = resolve_project_path(slice_config["path"])
    text = read_text(path)

    has_start = "start_line" in slice_config
    has_end = "end_before_line" in slice_config
    if not has_start and not has_end:
        if not text.strip():
            raise DeltaError(f"empty file: {path}")
        return text
    if has_start != has_end:
        raise DeltaError(f"slice must define both start_line and end_before_line: {path}")

    start_line = int(slice_config["start_line"])
    end_before_line = int(slice_config["end_before_line"])
    if start_line < 1:
        raise DeltaError(f"start_line must be >= 1 for {path}")
    if end_before_line <= start_line:
        raise DeltaError(f"empty slice range for {path}: {start_line}..{end_before_line}")

    lines = text.splitlines()
    selected = lines[start_line - 1 : end_before_line - 1]
    if not selected or not "\n".join(selected).strip():
        raise DeltaError(f"empty slice content for {path}: {start_line}..{end_before_line}")
    return "\n".join(selected)


def load_slices(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise DeltaError(f"slices file not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        config = json.load(f)
    groups = config.get("groups")
    if not isinstance(groups, list) or not groups:
        raise DeltaError("slices config must contain a non-empty groups list")
    return config


def compact_chars(text: str) -> list[str]:
    chars: list[str] = []
    for ch in text:
        if ch.isspace() or ch in PUNCTUATION:
            continue
        chars.append(ch)
    return chars


def char_unigrams(text: str) -> Counter[str]:
    return Counter(compact_chars(text))


def char_bigrams(text: str) -> Counter[str]:
    chars = compact_chars(text)
    return Counter("".join(pair) for pair in zip(chars, chars[1:]))


def punctuation_counts(text: str) -> Counter[str]:
    return Counter(ch for ch in text if ch in PUNCTUATION)


def cosine_distance(left: Counter[str], right: Counter[str]) -> float:
    if not left and not right:
        return 0.0
    if not left or not right:
        return 1.0

    shared = set(left) & set(right)
    dot = sum(left[key] * right[key] for key in shared)
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))
    if left_norm == 0.0 or right_norm == 0.0:
        return 1.0
    similarity = dot / (left_norm * right_norm)
    return max(0.0, min(1.0, 1.0 - similarity))


def feature_vectors(text: str) -> dict[str, Counter[str]]:
    return {
        "char_unigram": char_unigrams(text),
        "char_bigram": char_bigrams(text),
        "punctuation": punctuation_counts(text),
    }


def text_stats(text: str) -> TextStats:
    compact_count = len(re.sub(r"\s+", "", text))
    sentences = [part.strip() for part in SENTENCE_SPLIT_RE.split(text) if part.strip()]
    lengths = [len(re.sub(r"\s+", "", sentence)) for sentence in sentences if sentence.strip()]

    if not lengths:
        return TextStats(
            char_count=compact_count,
            sentence_count=0,
            sentence_avg=0.0,
            sentence_median=0.0,
            sentence_p90=0.0,
        )

    sorted_lengths = sorted(lengths)
    p90_index = min(len(sorted_lengths) - 1, math.ceil(len(sorted_lengths) * 0.9) - 1)
    return TextStats(
        char_count=compact_count,
        sentence_count=len(lengths),
        sentence_avg=sum(lengths) / len(lengths),
        sentence_median=float(statistics.median(lengths)),
        sentence_p90=float(sorted_lengths[p90_index]),
    )


def stats_to_json(stats: TextStats) -> dict[str, float | int]:
    return {
        "char_count": stats.char_count,
        "sentence_count": stats.sentence_count,
        "sentence_avg": round(stats.sentence_avg, 2),
        "sentence_median": round(stats.sentence_median, 2),
        "sentence_p90": round(stats.sentence_p90, 2),
    }


def evaluate_group(draft_features: dict[str, Counter[str]], group: dict[str, Any]) -> dict[str, Any]:
    group_id = group.get("id")
    label = group.get("label", group_id)
    slices = group.get("slices")
    if not group_id:
        raise DeltaError("group is missing required field: id")
    if not isinstance(slices, list) or not slices:
        raise DeltaError(f"group {group_id} must contain a non-empty slices list")

    texts = [read_slice(slice_config) for slice_config in slices]
    merged_text = "\n\n".join(texts)
    group_features = feature_vectors(merged_text)
    distances = {
        feature: cosine_distance(draft_features[feature], group_features[feature])
        for feature in ("char_unigram", "char_bigram", "punctuation")
    }
    delta = sum(distances.values()) / len(distances)

    return {
        "id": group_id,
        "label": label,
        "slice_count": len(slices),
        "distances": {
            "delta": round(delta, 6),
            "char_unigram": round(distances["char_unigram"], 6),
            "char_bigram": round(distances["char_bigram"], 6),
            "punctuation": round(distances["punctuation"], 6),
        },
        "text_stats": stats_to_json(text_stats(merged_text)),
    }


def build_report(draft_path: Path, slices_path: Path, config: dict[str, Any]) -> dict[str, Any]:
    draft_text = read_text(draft_path)
    if not draft_text.strip():
        raise DeltaError(f"empty draft file: {draft_path}")

    draft_features = feature_vectors(draft_text)
    groups = [evaluate_group(draft_features, group) for group in config["groups"]]
    ranking = [
        {
            "rank": index + 1,
            "id": group["id"],
            "label": group["label"],
            "delta": group["distances"]["delta"],
        }
        for index, group in enumerate(sorted(groups, key=lambda item: item["distances"]["delta"]))
    ]

    return {
        "draft_path": display_path(draft_path),
        "slices_path": display_path(slices_path),
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "feature_set": {
            "main_delta": "simple average of cosine distances",
            "blocks": ["char_unigram", "char_bigram", "punctuation"],
            "reported_only": ["sentence_length_stats"],
        },
        "draft_stats": stats_to_json(text_stats(draft_text)),
        "groups": groups,
        "ranking": ranking,
        "notes": [
            "Delta is a relative surface-distance metric.",
            "It is not a quality score, author similarity score, or copying target.",
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Delta v1 相对距离报告",
        "",
        f"- 草稿：`{report['draft_path']}`",
        f"- 切片配置：`{report['slices_path']}`",
        f"- 生成时间：{report['generated_at']}",
        "- 解释边界：Delta 是相对指标，不等于质量评分、作者相似度或复刻目标。",
        "",
        "## 距离排序",
        "",
        "| 排名 | 参照组 | 标签 | Delta |",
        "|---:|---|---|---:|",
    ]

    labels = {group["id"]: group["label"] for group in report["groups"]}
    for item in report["ranking"]:
        lines.append(f"| {item['rank']} | `{item['id']}` | {labels[item['id']]} | {item['delta']:.6f} |")

    lines.extend([
        "",
        "## 分项距离",
        "",
        "| 参照组 | 字符 unigram | 字符 bigram | 标点 | 主 Delta |",
        "|---|---:|---:|---:|---:|",
    ])
    for group in report["groups"]:
        distances = group["distances"]
        lines.append(
            "| "
            f"`{group['id']}` | "
            f"{distances['char_unigram']:.6f} | "
            f"{distances['char_bigram']:.6f} | "
            f"{distances['punctuation']:.6f} | "
            f"{distances['delta']:.6f} |"
        )

    draft_stats = report["draft_stats"]
    lines.extend([
        "",
        "## 句长对照",
        "",
        "| 文本 | 字符数 | 句数 | 平均句长 | 中位句长 | P90 句长 |",
        "|---|---:|---:|---:|---:|---:|",
        (
            "| `draft` | "
            f"{draft_stats['char_count']} | {draft_stats['sentence_count']} | "
            f"{draft_stats['sentence_avg']:.2f} | {draft_stats['sentence_median']:.2f} | "
            f"{draft_stats['sentence_p90']:.2f} |"
        ),
    ])
    for group in report["groups"]:
        stats = group["text_stats"]
        lines.append(
            f"| `{group['id']}` | "
            f"{stats['char_count']} | {stats['sentence_count']} | "
            f"{stats['sentence_avg']:.2f} | {stats['sentence_median']:.2f} | "
            f"{stats['sentence_p90']:.2f} |"
        )

    lines.extend([
        "",
        "## 说明",
        "",
        "- 主 Delta 是字符 unigram、字符 bigram、标点频率三个 cosine distance 的简单平均。",
        "- 句长统计只用于人工观察，不进入主 Delta 距离向量。",
        "- 如果 Delta 排序和人工读感冲突，以人工 review 为准，并把冲突记录为指标盲区。",
    ])
    return "\n".join(lines) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Delta v1 relative surface-distance evaluator.")
    parser.add_argument("--draft", type=Path, required=True, help="Draft file to compare.")
    parser.add_argument("--slices", type=Path, required=True, help="Reference corpus slice config.")
    parser.add_argument("--output-prefix", type=Path, required=True, help="Output path prefix without extension.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    draft_path = resolve_project_path(args.draft)
    slices_path = resolve_project_path(args.slices)
    output_prefix = resolve_project_path(args.output_prefix)

    try:
        config = load_slices(slices_path)
        report = build_report(draft_path, slices_path, config)
        markdown = render_markdown(report)
    except (DeltaError, json.JSONDecodeError, OSError, ValueError) as exc:
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
