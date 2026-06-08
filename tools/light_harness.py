from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ALLOWED_STATUSES = {"failed_auto_gate", "needs_manual_triage", "pending_user_review"}
ALLOWED_SCOPES = {"candidate", "fragment"}
DEFAULT_EXPLANATION_MARKERS = [
    "因为",
    "所以",
    "其实",
    "我的意思是",
    "我想说明",
    "你要理解",
    "我并不是",
    "我之所以",
]


class HarnessError(ValueError):
    pass


def resolve_project_path(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise HarnessError(f"file not found: {path}")
    with path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)


def validate_config(config: dict[str, Any]) -> None:
    statuses = set(config.get("statuses", []))
    if statuses and statuses != ALLOWED_STATUSES:
        raise HarnessError(f"config statuses must be exactly {sorted(ALLOWED_STATUSES)}")
    hard = config.get("hard_fail")
    manual = config.get("manual_triage")
    if not isinstance(hard, dict) or not isinstance(manual, dict):
        raise HarnessError("config must contain hard_fail and manual_triage objects")
    if int(hard.get("min_chars", 0)) <= 0:
        raise HarnessError("hard_fail.min_chars must be a positive integer")


def run_command(command: list[str]) -> None:
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or f"exit code {completed.returncode}"
        raise HarnessError(f"command failed: {' '.join(command)}\n{detail}")


def check_by_label(style_report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {check["label"]: check for check in style_report.get("checks", [])}


def short_dialogue_pct(style_report: dict[str, Any]) -> float:
    bins = style_report.get("metrics", {}).get("dialogue_burst", {}).get("length_bins", {})
    return float(bins.get("1-5", {}).get("pct", 0.0)) + float(bins.get("6-10", {}).get("pct", 0.0))


def dialogue_bin_pct(style_report: dict[str, Any], label: str) -> float:
    bins = style_report.get("metrics", {}).get("dialogue_burst", {}).get("length_bins", {})
    values = bins.get(label, {})
    if not isinstance(values, dict):
        return 0.0
    return float(values.get("pct", 0.0))


def dialogue_pct_sum(style_report: dict[str, Any], labels: list[str]) -> float:
    return sum(dialogue_bin_pct(style_report, label) for label in labels)


def dialogue_distribution_delta(style_report: dict[str, Any], source_bins: dict[str, Any]) -> float:
    labels = ["1-5", "6-10", "11-20", "21-40", "41-80", "81-160", "161-320", "321+"]
    return sum(abs(dialogue_bin_pct(style_report, label) - float(source_bins.get(label, 0.0))) for label in labels)


def approx_chars(text: str) -> int:
    return len(re.sub(r"\s+", "", text))


def load_candidate_structure(candidate: Path) -> dict[str, Any] | None:
    structure_path = candidate.with_suffix(".json")
    if not structure_path.exists():
        return None
    structure = load_json(structure_path)
    structure["_path"] = structure_path
    return structure


def analyze_candidate_structure(structure: dict[str, Any] | None, config: dict[str, Any]) -> dict[str, Any]:
    if structure is None:
        return {"present": False, "path": None, "errors": []}

    errors: list[str] = []
    utterances = structure.get("utterances", [])
    if not isinstance(utterances, list):
        errors.append("candidate JSON field `utterances` must be a list")
        utterances = []

    markers = config.get("manual_triage", {}).get("json_explanation_markers", DEFAULT_EXPLANATION_MARKERS)
    if not isinstance(markers, list):
        markers = DEFAULT_EXPLANATION_MARKERS

    shimamura: list[dict[str, Any]] = []
    adachi: list[dict[str, Any]] = []
    deep_understanding_ids: list[str] = []
    explanation_marker_hits: list[dict[str, Any]] = []
    surface_terms: list[str] = []

    for index, utterance in enumerate(utterances):
        if not isinstance(utterance, dict):
            errors.append(f"utterances[{index}] must be an object")
            continue
        speaker = str(utterance.get("speaker", "")).strip().lower()
        text = str(utterance.get("text", ""))
        if not speaker:
            errors.append(f"utterances[{index}] is missing speaker")
        if not text.strip():
            errors.append(f"utterances[{index}] is missing text")

        if speaker == "adachi":
            adachi.append(utterance)
        if speaker == "shimamura":
            shimamura.append(utterance)
            if utterance.get("deep_understanding") is True:
                deep_understanding_ids.append(str(utterance.get("id", f"utterances[{index}]")))
            raw_surface_terms = utterance.get("surface_terms_received", [])
            if isinstance(raw_surface_terms, list):
                surface_terms.extend(str(term) for term in raw_surface_terms if str(term).strip())
            raw_markers = utterance.get("explanation_markers", [])
            marker_set = {str(marker) for marker in raw_markers if str(marker).strip()} if isinstance(raw_markers, list) else set()
            marker_set.update(marker for marker in markers if marker in text)
            if marker_set:
                explanation_marker_hits.append({
                    "id": str(utterance.get("id", f"utterances[{index}]")),
                    "markers": sorted(marker_set),
                })

    shimamura_lengths = [approx_chars(str(utterance.get("text", ""))) for utterance in shimamura]
    adachi_lengths = [approx_chars(str(utterance.get("text", ""))) for utterance in adachi]
    long_threshold = int(config.get("hard_fail", {}).get("json_adachi_long_utterance_min", 200))

    return {
        "present": True,
        "path": display_path(structure["_path"]) if isinstance(structure.get("_path"), Path) else None,
        "errors": errors,
        "utterance_count": len(utterances),
        "shimamura_utterance_count": len(shimamura),
        "shimamura_avg_len": round(sum(shimamura_lengths) / len(shimamura_lengths), 2) if shimamura_lengths else 0.0,
        "shimamura_max_len": max(shimamura_lengths) if shimamura_lengths else 0,
        "shimamura_surface_terms_count": len(surface_terms),
        "shimamura_surface_terms": sorted(set(surface_terms))[:12],
        "shimamura_deep_understanding_ids": deep_understanding_ids,
        "shimamura_explanation_marker_hits": explanation_marker_hits,
        "adachi_utterance_count": len(adachi),
        "adachi_max_len": max(adachi_lengths) if adachi_lengths else 0,
        "adachi_ge_long_threshold": sum(length >= long_threshold for length in adachi_lengths),
        "adachi_long_threshold": long_threshold,
    }


def evaluate_gate(
    style_report: dict[str, Any],
    delta_report: dict[str, Any],
    config: dict[str, Any],
    candidate_structure: dict[str, Any] | None = None,
    evaluation_scope: str = "candidate",
) -> dict[str, Any]:
    if evaluation_scope not in ALLOWED_SCOPES:
        raise HarnessError(f"scope must be one of {sorted(ALLOWED_SCOPES)}")

    labels = check_by_label(style_report)
    metrics = style_report.get("metrics", {})
    hard = config["hard_fail"]
    manual = config["manual_triage"]
    structure = analyze_candidate_structure(candidate_structure, config)

    hard_fail_reasons: list[str] = []
    manual_triage_reasons: list[str] = []
    suppressed_reasons: list[str] = []

    char_count = int(metrics.get("char_count", 0))
    min_chars = int(hard["min_chars"])
    if evaluation_scope == "candidate" and char_count < min_chars:
        hard_fail_reasons.append(f"文本长度 {char_count} 低于 hard gate 最小值 {min_chars}")
    if evaluation_scope == "fragment":
        manual_triage_reasons.append("片段模式：跳过完整候选长度 hard gate，只做局部机制检查")

    for label in hard.get("risk_checks", []):
        check = labels.get(label)
        if check and check.get("status") == "RISK":
            if label == "过载长台词" and structure.get("adachi_ge_long_threshold", 0) > 0:
                suppressed_reasons.append("JSON 已标出安达长台词，抑制 Markdown `过载长台词` RISK")
            else:
                hard_fail_reasons.append(f"{label} 为 RISK")

    receiver = labels.get("接收端错位", {})
    receiver_count = int(receiver.get("values", {}).get("count", 0))
    has_json_surface_receipt = structure.get("shimamura_surface_terms_count", 0) > 0
    if receiver_count < int(hard.get("receiver_misalignment_min", 1)) and not has_json_surface_receipt:
        hard_fail_reasons.append("无有效接收端错位信号")
    elif receiver_count < int(hard.get("receiver_misalignment_min", 1)) and has_json_surface_receipt:
        suppressed_reasons.append("JSON 已标出岛村表层接收词，抑制 Markdown 接收端错位不足")

    burst = metrics.get("dialogue_burst", {})
    short_pct = short_dialogue_pct(style_report)
    distribution_cfg = manual.get("dialogue_distribution", {})
    distribution_delta = None
    mid_pct = dialogue_pct_sum(style_report, ["11-20", "21-40"])
    if (
        short_pct > float(hard.get("short_dialogue_max_pct_1_10", 75.0))
        and int(burst.get("count_ge_200", 0)) == 0
        and structure.get("adachi_ge_long_threshold", 0) == 0
    ):
        hard_fail_reasons.append(f"短台词 1-10 字占比 {short_pct:.1f}% 且无 >=200 字台词")

    if isinstance(distribution_cfg, dict) and isinstance(distribution_cfg.get("source_bins"), dict):
        source_bins = distribution_cfg["source_bins"]
        distribution_delta = dialogue_distribution_delta(style_report, source_bins)
        short_limit = float(distribution_cfg.get("short_1_10_max_pct", 65.0))
        mid_min = float(distribution_cfg.get("mid_11_40_min_pct", 30.0))
        max_l1_delta = float(distribution_cfg.get("max_l1_pct_delta", 60.0))
        source_label = str(distribution_cfg.get("source", "source"))
        if short_pct > short_limit:
            manual_triage_reasons.append(
                f"台词分布偏短：1-10 字占比 {short_pct:.1f}% 高于 {source_label} 自检上限 {short_limit:.1f}%"
            )
        if mid_pct < mid_min:
            manual_triage_reasons.append(
                f"台词分布中段不足：11-40 字占比 {mid_pct:.1f}% 低于 {source_label} 自检下限 {mid_min:.1f}%"
            )
        if distribution_delta > max_l1_delta:
            manual_triage_reasons.append(
                f"台词分布整体偏离：bins L1 偏差 {distribution_delta:.1f} 高于 {source_label} 自检上限 {max_l1_delta:.1f}"
            )

    if evaluation_scope == "candidate" and structure.get("present") and structure.get("adachi_ge_long_threshold", 0) == 0:
        hard_fail_reasons.append(
            f"JSON 未标出 >= {structure['adachi_long_threshold']} 字的安达过载台词"
        )

    for label in manual.get("warn_checks", []):
        check = labels.get(label)
        if check and check.get("status") == "WARN":
            if label == "岛村回应解释化" and structure.get("present") and not structure.get("errors"):
                suppressed_reasons.append("使用 JSON 岛村 utterance 结构替代 Markdown 说话人格式 WARN")
            else:
                manual_triage_reasons.append(f"{label} 为 WARN")

    if structure.get("errors"):
        manual_triage_reasons.extend(f"candidate JSON 结构问题：{error}" for error in structure["errors"])
    if structure.get("present") and structure.get("shimamura_utterance_count", 0) == 0:
        manual_triage_reasons.append("candidate JSON 未标出岛村 utterance，无法用结构层检查接收端")
    if structure.get("present") and structure.get("shimamura_utterance_count", 0) and structure.get("shimamura_surface_terms_count", 0) == 0:
        manual_triage_reasons.append("candidate JSON 未标出岛村表层接收词")
    if structure.get("shimamura_deep_understanding_ids"):
        manual_triage_reasons.append(
            "candidate JSON 标出岛村 deep_understanding: "
            + ", ".join(structure["shimamura_deep_understanding_ids"])
        )
    if structure.get("shimamura_explanation_marker_hits"):
        marker_ids = ", ".join(hit["id"] for hit in structure["shimamura_explanation_marker_hits"])
        manual_triage_reasons.append(f"candidate JSON 岛村 utterance 含解释标记：{marker_ids}")

    shimamura_avg_warn = float(manual.get("json_shimamura_avg_len_warn", 36.0))
    if structure.get("shimamura_avg_len", 0.0) >= shimamura_avg_warn:
        manual_triage_reasons.append(
            f"candidate JSON 岛村平均台词 {structure['shimamura_avg_len']} 字符，达到 triage 阈值 {shimamura_avg_warn}"
        )

    ranking = delta_report.get("ranking", [])
    expected_first = manual.get("delta_expected_first")
    if ranking:
        first_id = ranking[0].get("id")
        if expected_first and first_id != expected_first:
            manual_triage_reasons.append(f"Delta 第一名为 {first_id}，不是 {expected_first}")

        ranks = {item.get("id"): item.get("rank") for item in ranking}
        analysis_docs_id = manual.get("delta_analysis_docs_id")
        if analysis_docs_id in ranks and expected_first in ranks and ranks[analysis_docs_id] < ranks[expected_first]:
            manual_triage_reasons.append(f"Delta 中 {analysis_docs_id} 比 {expected_first} 更近")

    if hard_fail_reasons:
        status = "failed_auto_gate"
    elif manual_triage_reasons:
        status = "needs_manual_triage"
    else:
        status = "pending_user_review"

    return {
        "status": status,
        "hard_fail_reasons": hard_fail_reasons,
        "manual_triage_reasons": manual_triage_reasons,
        "metrics": {
            "char_count": char_count,
            "evaluation_scope": evaluation_scope,
            "dialogue_ratio": metrics.get("dialogue_ratio", 0.0),
            "max_dialogue_len": burst.get("max_len", 0),
            "dialogue_ge_200": burst.get("count_ge_200", 0),
            "short_dialogue_pct_1_10": round(short_pct, 2),
            "mid_dialogue_pct_11_40": round(mid_pct, 2),
            "dialogue_distribution_l1": round(distribution_delta, 2) if distribution_delta is not None else None,
        },
        "candidate_json": structure,
        "suppressed_reasons": suppressed_reasons,
        "delta_first": ranking[0].get("id") if ranking else None,
        "notes": [
            "Harness v1 only filters obvious failures.",
            "pending_user_review is not a success state.",
            "Final qualitative judgment must wait for user review.",
        ],
    }


def render_gate_markdown(candidate: Path, style_path: Path, delta_path: Path, gate: dict[str, Any]) -> str:
    lines = [
        "# Harness Gate Report",
        "",
        f"- 候选：`{display_path(candidate)}`",
        f"- 状态：`{gate['status']}`",
        f"- 范围：`{gate['metrics']['evaluation_scope']}`",
        f"- Style：`{display_path(style_path)}`",
        f"- Delta：`{display_path(delta_path)}`",
        "",
        "## 自动信号",
        "",
    ]
    for key, value in gate["metrics"].items():
        lines.append(f"- `{key}`: {value}")
    lines.extend(["", "## Candidate JSON", ""])
    candidate_json = gate.get("candidate_json", {})
    if candidate_json.get("present"):
        lines.append(f"- path: `{candidate_json.get('path')}`")
        lines.append(f"- adachi_max_len: {candidate_json.get('adachi_max_len')}")
        lines.append(f"- adachi_ge_long_threshold: {candidate_json.get('adachi_ge_long_threshold')}")
        lines.append(f"- shimamura_utterance_count: {candidate_json.get('shimamura_utterance_count')}")
        lines.append(f"- shimamura_avg_len: {candidate_json.get('shimamura_avg_len')}")
        lines.append(f"- shimamura_surface_terms: {', '.join(candidate_json.get('shimamura_surface_terms', [])) or '无'}")
    else:
        lines.append("- 无 companion JSON，使用 Markdown 启发式检查。")
    lines.extend(["", "## Hard Fail Reasons", ""])
    if gate["hard_fail_reasons"]:
        lines.extend(f"- {reason}" for reason in gate["hard_fail_reasons"])
    else:
        lines.append("- 无")
    lines.extend(["", "## Manual Triage Reasons", ""])
    if gate["manual_triage_reasons"]:
        lines.extend(f"- {reason}" for reason in gate["manual_triage_reasons"])
    else:
        lines.append("- 无")
    lines.extend(["", "## Suppressed Heuristic Reasons", ""])
    if gate["suppressed_reasons"]:
        lines.extend(f"- {reason}" for reason in gate["suppressed_reasons"])
    else:
        lines.append("- 无")
    lines.extend([
        "",
        "## 边界",
        "",
        "- Harness 只筛掉明显失败样本，不判定成功。",
        "- 通过 gate 的候选最多进入 `pending_user_review`。",
        "- 最终定性必须等待用户 review。",
    ])
    return "\n".join(lines) + "\n"


def process_candidate(
    candidate: Path,
    output_dir: Path,
    slices_path: Path,
    config: dict[str, Any],
    evaluation_scope: str,
) -> dict[str, Any]:
    if not candidate.exists():
        raise HarnessError(f"candidate file not found: {candidate}")
    if not candidate.is_file():
        raise HarnessError(f"candidate path is not a file: {candidate}")
    if not candidate.read_bytes().strip():
        raise HarnessError(f"candidate file is empty: {candidate}")

    stem = candidate.stem
    style_md = output_dir / f"{stem}_style.md"
    style_json = output_dir / f"{stem}_style.json"
    delta_prefix = output_dir / f"{stem}_delta"
    delta_md = delta_prefix.with_suffix(".md")
    delta_json = delta_prefix.with_suffix(".json")
    gate_md = output_dir / f"{stem}_gate.md"
    gate_json = output_dir / f"{stem}_gate.json"

    run_command([
        sys.executable,
        str(ROOT / "tools" / "style_evaluator.py"),
        "--mode",
        "draft",
        str(candidate),
        "--output",
        str(style_md),
        "--json-output",
        str(style_json),
    ])
    run_command([
        sys.executable,
        str(ROOT / "tools" / "delta_evaluator.py"),
        "--draft",
        str(candidate),
        "--slices",
        str(slices_path),
        "--output-prefix",
        str(delta_prefix),
    ])

    style_report = load_json(style_json)
    delta_report = load_json(delta_json)
    candidate_structure = load_candidate_structure(candidate)
    gate = evaluate_gate(style_report, delta_report, config, candidate_structure, evaluation_scope)
    gate["candidate_path"] = display_path(candidate)
    gate["reports"] = {
        "style_markdown": display_path(style_md),
        "style_json": display_path(style_json),
        "delta_markdown": display_path(delta_md),
        "delta_json": display_path(delta_json),
        "gate_markdown": display_path(gate_md),
        "gate_json": display_path(gate_json),
    }
    if candidate_structure is not None and isinstance(candidate_structure.get("_path"), Path):
        gate["reports"]["candidate_json"] = display_path(candidate_structure["_path"])
    gate_json.write_text(json.dumps(gate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    gate_md.write_text(render_gate_markdown(candidate, style_md, delta_md, gate), encoding="utf-8")
    return gate


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run lightweight candidate harness over existing drafts.")
    parser.add_argument("--run-id", required=True, help="Run identifier used for reports directory.")
    parser.add_argument("--candidates", nargs="+", type=Path, required=True, help="Candidate draft files to score.")
    parser.add_argument("--slices", type=Path, required=True, help="Delta slices config.")
    parser.add_argument("--config", type=Path, required=True, help="Harness config JSON.")
    parser.add_argument("--reports-root", type=Path, required=True, help="Root directory for candidate reports.")
    parser.add_argument(
        "--scope",
        choices=sorted(ALLOWED_SCOPES),
        default="candidate",
        help="Evaluation scope. Use fragment to skip full-candidate length hard gate.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    slices_path = resolve_project_path(args.slices)
    config_path = resolve_project_path(args.config)
    reports_root = resolve_project_path(args.reports_root)
    output_dir = reports_root / args.run_id

    try:
        if not slices_path.exists():
            raise HarnessError(f"slices file not found: {slices_path}")
        config = load_json(config_path)
        validate_config(config)
        output_dir.mkdir(parents=True, exist_ok=True)
        candidates = [resolve_project_path(candidate) for candidate in args.candidates]
        results = [process_candidate(candidate, output_dir, slices_path, config, args.scope) for candidate in candidates]
    except (HarnessError, OSError, json.JSONDecodeError, UnicodeDecodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    manifest = {
        "run_id": args.run_id,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "slices_path": display_path(slices_path),
        "config_path": display_path(config_path),
        "evaluation_scope": args.scope,
        "reports_dir": display_path(output_dir),
        "status_counts": {status: sum(result["status"] == status for result in results) for status in sorted(ALLOWED_STATUSES)},
        "candidates": results,
        "notes": config.get("notes", []),
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
