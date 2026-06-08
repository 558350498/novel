from __future__ import annotations

import argparse
import json
import math
import re
import statistics
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PUNCTUATION = set("，。！？；：、“”‘’（）《》〈〉「」『』…—,.!?;:\"'()[]{}<>-")


class EderDeltaError(ValueError):
    pass


@dataclass(frozen=True)
class Sample:
    id: str
    group_id: str
    group_label: str
    source: str
    text: str
    kind: str
    index: int


def resolve_project_path(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return ROOT / candidate


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def read_text(path: Path) -> str:
    if not path.exists():
        raise EderDeltaError(f"file not found: {path}")
    data = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-8", "utf-16"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise EderDeltaError(f"unsupported text encoding: {path}")


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise EderDeltaError(f"file not found: {path}")
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def read_slice(slice_config: dict[str, Any]) -> tuple[str, str]:
    if "path" not in slice_config:
        raise EderDeltaError("slice is missing required field: path")

    path = resolve_project_path(slice_config["path"])
    text = read_text(path)
    source = display_path(path)

    has_start = "start_line" in slice_config
    has_end = "end_before_line" in slice_config
    if not has_start and not has_end:
        if not text.strip():
            raise EderDeltaError(f"empty file: {path}")
        return text, source
    if has_start != has_end:
        raise EderDeltaError(f"slice must define both start_line and end_before_line: {path}")

    start_line = int(slice_config["start_line"])
    end_before_line = int(slice_config["end_before_line"])
    if start_line < 1 or end_before_line <= start_line:
        raise EderDeltaError(f"invalid slice range for {path}: {start_line}..{end_before_line}")

    lines = text.splitlines()
    selected = "\n".join(lines[start_line - 1 : end_before_line - 1])
    if not selected.strip():
        raise EderDeltaError(f"empty slice content for {path}: {start_line}..{end_before_line}")
    return selected, f"{source}:{start_line}-{end_before_line - 1}"


def compact_text(text: str, keep_punctuation: bool) -> str:
    chars: list[str] = []
    for ch in text:
        if ch.isspace():
            continue
        if not keep_punctuation and ch in PUNCTUATION:
            continue
        chars.append(ch)
    return "".join(chars)


def split_fixed_segments(text: str, segment_size: int, min_segment_chars: int, keep_punctuation: bool) -> list[str]:
    compact = compact_text(text, keep_punctuation=keep_punctuation)
    if not compact:
        return []
    segments = [compact[index : index + segment_size] for index in range(0, len(compact), segment_size)]
    if len(segments) > 1 and len(segments[-1]) < min_segment_chars:
        segments[-2] += segments[-1]
        segments.pop()
    return [segment for segment in segments if len(segment) >= min_segment_chars]


def char_ngrams(text: str, ngram_min: int, ngram_max: int) -> Counter[str]:
    features: Counter[str] = Counter()
    for size in range(ngram_min, ngram_max + 1):
        if size <= 0 or len(text) < size:
            continue
        features.update(text[index : index + size] for index in range(0, len(text) - size + 1))
    return features


def relative_frequencies(counts: Counter[str], features: list[str]) -> list[float]:
    total = sum(counts.values())
    if total <= 0:
        return [0.0 for _ in features]
    return [(counts.get(feature, 0) / total) * 1000.0 for feature in features]


def zscore_matrix(rows: list[list[float]], mean_rows: list[list[float]]) -> tuple[list[list[float]], list[float], list[float]]:
    if not mean_rows:
        raise EderDeltaError("cannot scale feature matrix without reference rows")
    columns = len(rows[0]) if rows else 0
    means: list[float] = []
    stdevs: list[float] = []
    for column in range(columns):
        values = [row[column] for row in mean_rows]
        mean = sum(values) / len(values)
        stdev = statistics.pstdev(values)
        means.append(mean)
        stdevs.append(stdev if stdev > 0.0 else 1.0)

    scaled = [
        [(value - means[column]) / stdevs[column] for column, value in enumerate(row)]
        for row in rows
    ]
    return scaled, means, stdevs


def cosine_distance(left: list[float], right: list[float]) -> float:
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0.0 and right_norm == 0.0:
        return 0.0
    if left_norm == 0.0 or right_norm == 0.0:
        return 1.0
    dot = sum(l_value * r_value for l_value, r_value in zip(left, right))
    similarity = dot / (left_norm * right_norm)
    return max(0.0, min(2.0, 1.0 - similarity))


def choose_features(reference_counts: list[Counter[str]], top_features: int) -> list[str]:
    merged: Counter[str] = Counter()
    for counts in reference_counts:
        merged.update(counts)
    return [feature for feature, _ in merged.most_common(top_features)]


def build_reference_samples(
    config: dict[str, Any],
    segment_size: int,
    min_segment_chars: int,
    keep_punctuation: bool,
    exclude_groups: set[str],
) -> list[Sample]:
    groups = config.get("groups")
    if not isinstance(groups, list) or not groups:
        raise EderDeltaError("slices config must contain a non-empty groups list")

    samples: list[Sample] = []
    for group in groups:
        group_id = str(group.get("id", "")).strip()
        if not group_id or group_id in exclude_groups:
            continue
        slices = group.get("slices", [])
        if not isinstance(slices, list) or not slices:
            raise EderDeltaError(f"group {group_id} must contain a non-empty slices list")
        label = str(group.get("label", group_id))
        for slice_index, slice_config in enumerate(slices, start=1):
            text, source = read_slice(slice_config)
            segments = split_fixed_segments(text, segment_size, min_segment_chars, keep_punctuation)
            for segment_index, segment in enumerate(segments, start=1):
                samples.append(
                    Sample(
                        id=f"{group_id}_s{slice_index:02d}_p{segment_index:03d}",
                        group_id=group_id,
                        group_label=label,
                        source=source,
                        text=segment,
                        kind="reference",
                        index=segment_index,
                    )
                )
    if not samples:
        raise EderDeltaError("no reference segments were produced")
    return samples


def build_draft_samples(
    draft_path: Path,
    segment_size: int,
    min_segment_chars: int,
    keep_punctuation: bool,
) -> list[Sample]:
    text = read_text(draft_path)
    segments = split_fixed_segments(text, segment_size, min_segment_chars, keep_punctuation)
    if not segments:
        raise EderDeltaError(f"draft produced no segments: {draft_path}")
    return [
        Sample(
            id=f"draft_p{index:03d}",
            group_id="draft",
            group_label="Draft",
            source=display_path(draft_path),
            text=segment,
            kind="draft",
            index=index,
        )
        for index, segment in enumerate(segments, start=1)
    ]


def classify_segments(samples: list[Sample], scaled_rows: dict[str, list[float]]) -> list[dict[str, Any]]:
    reference_samples = [sample for sample in samples if sample.kind == "reference"]
    draft_samples = [sample for sample in samples if sample.kind == "draft"]
    assignments: list[dict[str, Any]] = []
    for draft in draft_samples:
        distances = [
            {
                "sample_id": reference.id,
                "group_id": reference.group_id,
                "group_label": reference.group_label,
                "distance": cosine_distance(scaled_rows[draft.id], scaled_rows[reference.id]),
            }
            for reference in reference_samples
        ]
        distances.sort(key=lambda item: item["distance"])
        group_distances: dict[str, list[float]] = defaultdict(list)
        group_labels: dict[str, str] = {}
        for item in distances:
            group_distances[item["group_id"]].append(item["distance"])
            group_labels[item["group_id"]] = item["group_label"]
        group_summary = [
            {
                "group_id": group_id,
                "group_label": group_labels[group_id],
                "mean_distance": round(sum(values) / len(values), 6),
                "nearest_distance": round(min(values), 6),
                "reference_segments": len(values),
            }
            for group_id, values in group_distances.items()
        ]
        group_summary.sort(key=lambda item: (item["mean_distance"], item["nearest_distance"]))
        assignments.append(
            {
                "draft_segment": draft.id,
                "char_count": len(draft.text),
                "nearest_neighbor": {
                    **distances[0],
                    "distance": round(distances[0]["distance"], 6),
                },
                "group_ranking": group_summary,
            }
        )
    return assignments


def aggregate_assignments(assignments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    votes: Counter[str] = Counter()
    nearest_distances: dict[str, list[float]] = defaultdict(list)
    mean_distances: dict[str, list[float]] = defaultdict(list)
    labels: dict[str, str] = {}

    for assignment in assignments:
        nearest = assignment["nearest_neighbor"]
        votes[nearest["group_id"]] += 1
        labels[nearest["group_id"]] = nearest["group_label"]
        nearest_distances[nearest["group_id"]].append(float(nearest["distance"]))
        for group in assignment["group_ranking"]:
            labels[group["group_id"]] = group["group_label"]
            mean_distances[group["group_id"]].append(float(group["mean_distance"]))

    rows: list[dict[str, Any]] = []
    for group_id in sorted(labels):
        rows.append(
            {
                "group_id": group_id,
                "group_label": labels[group_id],
                "nearest_neighbor_votes": votes[group_id],
                "mean_nearest_distance": round(sum(nearest_distances[group_id]) / len(nearest_distances[group_id]), 6)
                if nearest_distances[group_id]
                else None,
                "mean_group_distance": round(sum(mean_distances[group_id]) / len(mean_distances[group_id]), 6)
                if mean_distances[group_id]
                else None,
            }
        )
    rows.sort(
        key=lambda item: (
            -int(item["nearest_neighbor_votes"]),
            item["mean_group_distance"] if item["mean_group_distance"] is not None else 999.0,
        )
    )
    return rows


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    draft_path = resolve_project_path(args.draft)
    slices_path = resolve_project_path(args.slices)
    config = load_json(slices_path)
    exclude_groups = {group.strip() for group in args.exclude_group if group.strip()}

    reference_samples = build_reference_samples(
        config,
        args.segment_size,
        args.min_segment_chars,
        args.keep_punctuation,
        exclude_groups,
    )
    draft_samples = build_draft_samples(draft_path, args.segment_size, args.min_segment_chars, args.keep_punctuation)
    samples = reference_samples + draft_samples

    counts_by_id = {
        sample.id: char_ngrams(sample.text, args.ngram_min, args.ngram_max)
        for sample in samples
    }
    features = choose_features([counts_by_id[sample.id] for sample in reference_samples], args.top_features)
    if not features:
        raise EderDeltaError("no features selected")

    rows = [relative_frequencies(counts_by_id[sample.id], features) for sample in samples]
    reference_rows = rows[: len(reference_samples)]
    scaled, means, stdevs = zscore_matrix(rows, reference_rows)
    scaled_rows = {sample.id: scaled[index] for index, sample in enumerate(samples)}

    assignments = classify_segments(samples, scaled_rows)
    aggregate = aggregate_assignments(assignments)
    reference_counts = Counter(sample.group_id for sample in reference_samples)

    return {
        "draft_path": display_path(draft_path),
        "slices_path": display_path(slices_path),
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "method": {
            "name": "experimental_cosine_delta_segments",
            "distance": "cosine distance over z-scored relative-frequency vectors",
            "feature_selection": f"top {len(features)} reference character n-grams",
            "ngram_range": [args.ngram_min, args.ngram_max],
            "segment_size": args.segment_size,
            "min_segment_chars": args.min_segment_chars,
            "scaling": "z-score using reference segments only",
            "classifier": "nearest reference segment plus group mean-distance ranking",
            "excluded_groups": sorted(exclude_groups),
            "keep_punctuation": args.keep_punctuation,
        },
        "feature_sample": features[:25],
        "feature_scaling": {
            "feature_count": len(features),
            "zero_variance_features_after_guard": sum(1 for stdev in stdevs if stdev == 1.0),
            "mean_sample": [round(value, 6) for value in means[:10]],
            "stdev_sample": [round(value, 6) for value in stdevs[:10]],
        },
        "reference_segments": {
            "total": len(reference_samples),
            "by_group": dict(sorted(reference_counts.items())),
        },
        "draft_segments": len(draft_samples),
        "aggregate": aggregate,
        "assignments": assignments,
        "notes": [
            "This is an experimental diagnostic, not a quality score.",
            "Small reference sets make nearest-neighbor votes unstable; use the output as a triage signal.",
            "Delta-family metrics should stay subordinate to human review and source-shape checks.",
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Experimental Eder/Cosine Delta Segment Report",
        "",
        f"- 草稿：`{report['draft_path']}`",
        f"- 切片配置：`{report['slices_path']}`",
        f"- 生成时间：{report['generated_at']}",
        "- 边界：这是片段级归属诊断，不是质量评分或最终审稿。", 
        "",
        "## Method",
        "",
    ]
    method = report["method"]
    for key in (
        "distance",
        "feature_selection",
        "ngram_range",
        "segment_size",
        "min_segment_chars",
        "scaling",
        "classifier",
        "excluded_groups",
        "keep_punctuation",
    ):
        lines.append(f"- `{key}`: {method[key]}")

    lines.extend([
        "",
        "## Segment Counts",
        "",
        f"- reference total: {report['reference_segments']['total']}",
        f"- draft segments: {report['draft_segments']}",
        "",
        "| group | reference segments |",
        "|---|---:|",
    ])
    for group_id, count in report["reference_segments"]["by_group"].items():
        lines.append(f"| `{group_id}` | {count} |")

    lines.extend([
        "",
        "## Aggregate",
        "",
        "| rank | group | nearest-neighbor votes | mean nearest distance | mean group distance |",
        "|---:|---|---:|---:|---:|",
    ])
    for index, row in enumerate(report["aggregate"], start=1):
        nearest = row["mean_nearest_distance"]
        group_mean = row["mean_group_distance"]
        lines.append(
            f"| {index} | `{row['group_id']}` | {row['nearest_neighbor_votes']} | "
            f"{nearest if nearest is not None else '-'} | {group_mean if group_mean is not None else '-'} |"
        )

    lines.extend([
        "",
        "## Draft Segment Assignments",
        "",
        "| segment | chars | nearest group | nearest distance | group mean-distance ranking |",
        "|---|---:|---|---:|---|",
    ])
    for assignment in report["assignments"]:
        nearest = assignment["nearest_neighbor"]
        ranking = "；".join(
            f"{item['group_id']}={item['mean_distance']}"
            for item in assignment["group_ranking"][:4]
        )
        lines.append(
            f"| `{assignment['draft_segment']}` | {assignment['char_count']} | "
            f"`{nearest['group_id']}` | {nearest['distance']:.6f} | {ranking} |"
        )

    lines.extend([
        "",
        "## Feature Sample",
        "",
        ", ".join(f"`{feature}`" for feature in report["feature_sample"]),
        "",
        "## Notes",
        "",
    ])
    lines.extend(f"- {note}" for note in report["notes"])
    return "\n".join(lines) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Experimental segment-level cosine Delta evaluator.")
    parser.add_argument("--draft", type=Path, required=True, help="Draft file to compare.")
    parser.add_argument("--slices", type=Path, required=True, help="Reference corpus slice config.")
    parser.add_argument("--output-prefix", type=Path, required=True, help="Output path prefix without extension.")
    parser.add_argument("--segment-size", type=int, default=1000, help="Fixed compact-character segment size.")
    parser.add_argument("--min-segment-chars", type=int, default=500, help="Minimum compact chars for a segment.")
    parser.add_argument("--top-features", type=int, default=800, help="Number of reference n-gram features to keep.")
    parser.add_argument("--ngram-min", type=int, default=1, help="Minimum character n-gram length.")
    parser.add_argument("--ngram-max", type=int, default=2, help="Maximum character n-gram length.")
    parser.add_argument(
        "--exclude-group",
        action="append",
        default=["analysis_docs"],
        help="Reference group to exclude from segment classifier; can be repeated.",
    )
    parser.add_argument(
        "--keep-punctuation",
        action="store_true",
        help="Keep punctuation in segment text and character n-grams.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    output_prefix = resolve_project_path(args.output_prefix)

    try:
        if args.segment_size <= 0:
            raise EderDeltaError("--segment-size must be positive")
        if args.min_segment_chars <= 0:
            raise EderDeltaError("--min-segment-chars must be positive")
        if args.ngram_min <= 0 or args.ngram_max < args.ngram_min:
            raise EderDeltaError("invalid n-gram range")
        report = build_report(args)
        markdown = render_markdown(report)
    except (EderDeltaError, json.JSONDecodeError, OSError, ValueError) as exc:
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
