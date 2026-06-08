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
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LEXICON = ROOT / "tools" / "style_lexicon.json"
DEFAULT_TAXONOMY = ROOT / "tools" / "lexicon_taxonomy.json"
PUNCTUATION = set("，。！？；：、“”‘’（）《》〈〉「」『』…—,.!?;:\"'()[]{}<>-")
SENTENCE_SPLIT_RE = re.compile(r"[。！？!?]+")
SPEAKER_RE = re.compile(r"^\s*([^：:「『“”\"']{1,12})[：:]\s*(.*)$")
QUOTE_START_RE = re.compile(r"^\s*[「『“\"']")


class ProfileError(ValueError):
    pass


def resolve_project_path(path: str | Path) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else ROOT / candidate


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def read_text(path: Path) -> str:
    if not path.exists():
        raise ProfileError(f"file not found: {path}")
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
    raise ProfileError(f"unsupported text encoding: {path}")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def read_slice(slice_config: dict[str, Any]) -> str:
    path = resolve_project_path(slice_config["path"])
    text = read_text(path)
    if "start_line" not in slice_config and "end_before_line" not in slice_config:
        return text
    if "start_line" not in slice_config or "end_before_line" not in slice_config:
        raise ProfileError(f"slice must define both start_line and end_before_line: {path}")
    start_line = int(slice_config["start_line"])
    end_before_line = int(slice_config["end_before_line"])
    if start_line < 1 or end_before_line <= start_line:
        raise ProfileError(f"invalid line range for {path}: {start_line}..{end_before_line}")
    lines = text.splitlines()
    return "\n".join(lines[start_line - 1 : end_before_line - 1])


def approx_chars(text: str) -> int:
    return len(re.sub(r"\s+", "", text))


def sentence_lengths(text: str) -> list[int]:
    lengths = []
    for sentence in SENTENCE_SPLIT_RE.split(text):
        compact = re.sub(r"\s+", "", sentence)
        if compact:
            lengths.append(len(compact))
    return lengths


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
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, math.ceil(len(ordered) * q) - 1))
    return float(ordered[index])


def count_terms(text: str, terms: Iterable[str]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for term in terms:
        count = text.count(term)
        if count:
            counts[term] = count
    return counts


def char_ngrams(text: str, n: int) -> Counter[str]:
    chars = [ch for ch in text if "\u4e00" <= ch <= "\u9fff"]
    return Counter("".join(chars[index : index + n]) for index in range(0, max(0, len(chars) - n + 1)))


def top_items(counter: Counter[str], limit: int) -> list[dict[str, int | str]]:
    return [{"item": item, "count": count} for item, count in counter.most_common(limit)]


def taxonomy_term_sets(lexicon: dict[str, Any], taxonomy: dict[str, Any]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for category_id, config in taxonomy.get("categories", {}).items():
        terms: list[str] = []
        for key in config.get("current_lexicon_keys", []):
            value = lexicon.get(key)
            if isinstance(value, list):
                terms.extend(term for term in value if isinstance(term, str))
        result[category_id] = sorted(set(terms), key=lambda item: (-len(item), item))
    return result


def shape_features(text: str) -> dict[str, float]:
    lines = [line for line in text.splitlines() if line.strip()]
    dialogue_lines = [line for line in lines if is_dialogue_line(line)]
    dialogue_lengths = [approx_chars(dialogue_content(line)) for line in dialogue_lines]
    lengths = sentence_lengths(text)
    char_count = approx_chars(text)
    return {
        "shape.char_count": float(char_count),
        "shape.sentence_avg": round(sum(lengths) / len(lengths), 4) if lengths else 0.0,
        "shape.sentence_p90": round(percentile(lengths, 0.9), 4),
        "shape.dialogue_ratio": round(len(dialogue_lines) / len(lines), 4) if lines else 0.0,
        "shape.dialogue_max": float(max(dialogue_lengths) if dialogue_lengths else 0),
        "shape.dialogue_ge_200": float(sum(length >= 200 for length in dialogue_lengths)),
    }


def group_profile(
    group: dict[str, Any],
    lexicon: dict[str, Any],
    taxonomy: dict[str, Any],
    topn: int,
) -> dict[str, Any]:
    texts = [read_slice(slice_config) for slice_config in group["slices"]]
    text = "\n\n".join(texts)
    char_count = max(1, approx_chars(text))
    term_sets = taxonomy_term_sets(lexicon, taxonomy)
    taxonomy_counts = {
        category: count_terms(text, terms)
        for category, terms in term_sets.items()
    }
    taxonomy_features = {
        f"taxonomy.{category}.per_1000": round(sum(hits.values()) * 1000.0 / char_count, 6)
        for category, hits in taxonomy_counts.items()
    }
    cjk_trigrams = char_ngrams(text, 3)
    features = {}
    features.update(taxonomy_features)
    features.update(shape_features(text))
    return {
        "id": group["id"],
        "label": group.get("label", group["id"]),
        "slice_count": len(group["slices"]),
        "metrics": {
            "chars_no_ws": char_count,
            "slice_count": len(group["slices"]),
        },
        "features": features,
        "taxonomy_hits": {
            category: {
                "count": sum(hits.values()),
                "per_1000": round(sum(hits.values()) * 1000.0 / char_count, 6),
                "top_terms": top_items(hits, topn),
            }
            for category, hits in taxonomy_counts.items()
        },
        "top_cjk_trigrams": top_items(cjk_trigrams, topn),
    }


def contrast_weights(profiles: list[dict[str, Any]], target_id: str) -> list[dict[str, Any]]:
    target = next((profile for profile in profiles if profile["id"] == target_id), None)
    if target is None:
        raise ProfileError(f"target group not found: {target_id}")
    others = [profile for profile in profiles if profile["id"] != target_id]
    if not others:
        raise ProfileError("need at least one non-target group for contrast")

    keys = sorted(target["features"])
    rows: list[dict[str, Any]] = []
    for key in keys:
        target_value = float(target["features"].get(key, 0.0))
        other_values = [float(profile["features"].get(key, 0.0)) for profile in others]
        other_mean = sum(other_values) / len(other_values)
        spread_values = [target_value, *other_values]
        spread = statistics.pstdev(spread_values) if len(spread_values) > 1 else 0.0
        effect = (target_value - other_mean) / (spread + 1e-9)
        rows.append({
            "feature": key,
            "target": round(target_value, 6),
            "others_mean": round(other_mean, 6),
            "effect": round(effect, 6),
            "abs_effect": round(abs(effect), 6),
            "direction": "higher_in_target" if effect > 0 else "lower_in_target" if effect < 0 else "flat",
        })
    return sorted(rows, key=lambda item: (-item["abs_effect"], item["feature"]))


def build_report(
    slices_path: Path,
    lexicon_path: Path,
    taxonomy_path: Path,
    target_id: str,
    topn: int,
) -> dict[str, Any]:
    slices = load_json(slices_path)
    lexicon = load_json(lexicon_path)
    taxonomy = load_json(taxonomy_path)
    groups = slices.get("groups")
    if not isinstance(groups, list) or not groups:
        raise ProfileError("slices config must contain groups")
    profiles = [group_profile(group, lexicon, taxonomy, topn) for group in groups]
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "slices_path": display_path(slices_path),
        "lexicon_path": display_path(lexicon_path),
        "taxonomy_path": display_path(taxonomy_path),
        "target_id": target_id,
        "groups": profiles,
        "contrast_weights": contrast_weights(profiles, target_id),
        "notes": [
            "This is a corpus profile, not RAG and not a quality score.",
            "Weights are simple standardized contrasts against non-target groups.",
            "Use weights to decide which dimensions deserve human review or gate tuning.",
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Corpus Profile v1",
        "",
        f"- slices: `{report['slices_path']}`",
        f"- target: `{report['target_id']}`",
        f"- generated: {report['generated_at']}",
        "- boundary: feature weights assist review decisions; they do not judge quality.",
        "",
        "## Contrast Weights",
        "",
        "| rank | feature | direction | target | others mean | effect |",
        "|---:|---|---|---:|---:|---:|",
    ]
    for index, row in enumerate(report["contrast_weights"][:30], start=1):
        lines.append(
            f"| {index} | `{row['feature']}` | {row['direction']} | "
            f"{row['target']} | {row['others_mean']} | {row['effect']} |"
        )

    lines.extend(["", "## Group Taxonomy Profiles", ""])
    for group in report["groups"]:
        lines.extend([
            f"### {group['id']} - {group['label']}",
            "",
            f"- chars: {group['metrics']['chars_no_ws']}",
            "",
            "| taxonomy | count | per 1000 | top terms |",
            "|---|---:|---:|---|",
        ])
        for category, data in group["taxonomy_hits"].items():
            top_terms = "、".join(f"`{item['item']}`×{item['count']}" for item in data["top_terms"][:6]) or "无"
            lines.append(f"| `{category}` | {data['count']} | {data['per_1000']} | {top_terms} |")
        lines.extend([
            "",
            "Top CJK trigrams:",
            "",
            ", ".join(f"`{item['item']}`×{item['count']}" for item in group["top_cjk_trigrams"][:12]),
            "",
        ])

    lines.extend([
        "## How To Use",
        "",
        "- High positive effects mark dimensions unusually strong in the target group.",
        "- High negative effects mark dimensions unusually weak in the target group.",
        "- Convert only reviewed dimensions into gate changes; do not tune solely from this report.",
    ])
    return "\n".join(lines) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build explainable corpus profiles and contrast weights.")
    parser.add_argument("--slices", type=Path, default=Path("corpus_slices/slices.json"), help="Slice config path.")
    parser.add_argument("--lexicon", type=Path, default=DEFAULT_LEXICON, help="Style lexicon path.")
    parser.add_argument("--taxonomy", type=Path, default=DEFAULT_TAXONOMY, help="Lexicon taxonomy path.")
    parser.add_argument("--target-id", default="adachi_pressure", help="Reference group to contrast against others.")
    parser.add_argument("--output-prefix", type=Path, required=True, help="Output path prefix without extension.")
    parser.add_argument("--topn", type=int, default=30, help="Top terms/ngrams to include.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    slices_path = resolve_project_path(args.slices)
    lexicon_path = resolve_project_path(args.lexicon)
    taxonomy_path = resolve_project_path(args.taxonomy)
    output_prefix = resolve_project_path(args.output_prefix)
    try:
        report = build_report(slices_path, lexicon_path, taxonomy_path, args.target_id, args.topn)
    except (ProfileError, OSError, json.JSONDecodeError, KeyError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    json_path = output_prefix.with_suffix(".json")
    markdown_path = output_prefix.with_suffix(".md")
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")
    print(render_markdown(report), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
