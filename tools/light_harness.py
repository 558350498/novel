from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ALLOWED_STATUSES = {"failed_auto_gate", "needs_manual_triage", "pending_user_review"}


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


def evaluate_gate(style_report: dict[str, Any], delta_report: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    labels = check_by_label(style_report)
    metrics = style_report.get("metrics", {})
    hard = config["hard_fail"]
    manual = config["manual_triage"]

    hard_fail_reasons: list[str] = []
    manual_triage_reasons: list[str] = []

    char_count = int(metrics.get("char_count", 0))
    min_chars = int(hard["min_chars"])
    if char_count < min_chars:
        hard_fail_reasons.append(f"文本长度 {char_count} 低于 hard gate 最小值 {min_chars}")

    for label in hard.get("risk_checks", []):
        check = labels.get(label)
        if check and check.get("status") == "RISK":
            hard_fail_reasons.append(f"{label} 为 RISK")

    receiver = labels.get("接收端错位", {})
    receiver_count = int(receiver.get("values", {}).get("count", 0))
    if receiver_count < int(hard.get("receiver_misalignment_min", 1)):
        hard_fail_reasons.append("无有效接收端错位信号")

    burst = metrics.get("dialogue_burst", {})
    short_pct = short_dialogue_pct(style_report)
    if (
        short_pct > float(hard.get("short_dialogue_max_pct_1_10", 75.0))
        and int(burst.get("count_ge_200", 0)) == 0
    ):
        hard_fail_reasons.append(f"短台词 1-10 字占比 {short_pct:.1f}% 且无 >=200 字台词")

    for label in manual.get("warn_checks", []):
        check = labels.get(label)
        if check and check.get("status") == "WARN":
            manual_triage_reasons.append(f"{label} 为 WARN")

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
            "dialogue_ratio": metrics.get("dialogue_ratio", 0.0),
            "max_dialogue_len": burst.get("max_len", 0),
            "dialogue_ge_200": burst.get("count_ge_200", 0),
            "short_dialogue_pct_1_10": round(short_pct, 2),
        },
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
        f"- Style：`{display_path(style_path)}`",
        f"- Delta：`{display_path(delta_path)}`",
        "",
        "## 自动信号",
        "",
    ]
    for key, value in gate["metrics"].items():
        lines.append(f"- `{key}`: {value}")
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
    lines.extend([
        "",
        "## 边界",
        "",
        "- Harness 只筛掉明显失败样本，不判定成功。",
        "- 通过 gate 的候选最多进入 `pending_user_review`。",
        "- 最终定性必须等待用户 review。",
    ])
    return "\n".join(lines) + "\n"


def process_candidate(candidate: Path, output_dir: Path, slices_path: Path, config: dict[str, Any]) -> dict[str, Any]:
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
    gate = evaluate_gate(style_report, delta_report, config)
    gate["candidate_path"] = display_path(candidate)
    gate["reports"] = {
        "style_markdown": display_path(style_md),
        "style_json": display_path(style_json),
        "delta_markdown": display_path(delta_md),
        "delta_json": display_path(delta_json),
        "gate_markdown": display_path(gate_md),
        "gate_json": display_path(gate_json),
    }
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
        results = [process_candidate(candidate, output_dir, slices_path, config) for candidate in candidates]
    except (HarnessError, OSError, json.JSONDecodeError, UnicodeDecodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    manifest = {
        "run_id": args.run_id,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "slices_path": display_path(slices_path),
        "config_path": display_path(config_path),
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
