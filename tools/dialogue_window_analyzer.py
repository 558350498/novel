from __future__ import annotations

import argparse
import json
import math
from datetime import datetime
from pathlib import Path
from typing import Any

from style_evaluator import dialogue_content, is_dialogue_line, read_text


ROOT = Path(__file__).resolve().parents[1]


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def companion_json(path: Path) -> Path:
    return path.with_suffix(".json")


def resolve_project_path(path: str | Path) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else ROOT / candidate


def percentile(values: list[int], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, math.ceil(len(ordered) * q) - 1))
    return float(ordered[index])


def non_empty_lines(text: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        rows.append(
            {
                "line_no": line_no,
                "text": line,
                "is_dialogue": is_dialogue_line(line),
            }
        )
    return rows


def dialogue_rows(text: str) -> list[dict[str, Any]]:
    rows = non_empty_lines(text)
    indexed: list[dict[str, Any]] = []
    for non_empty_index, row in enumerate(rows):
        if row["is_dialogue"]:
            indexed.append(
                {
                    "line_no": row["line_no"],
                    "non_empty_index": non_empty_index,
                    "text": row["text"],
                    "content": dialogue_content(row["text"]),
                }
            )
    return indexed


def attach_speakers(rows: list[dict[str, Any]], structure: dict[str, Any] | None) -> list[str]:
    if not structure:
        return ["unknown"] * len(rows)
    utterances = structure.get("utterances", [])
    if not isinstance(utterances, list):
        return ["unknown"] * len(rows)
    speakers: list[str] = []
    for index, _row in enumerate(rows):
        if index < len(utterances) and isinstance(utterances[index], dict):
            speakers.append(str(utterances[index].get("speaker", "unknown")).lower())
        else:
            speakers.append("unknown")
    return speakers


def contiguous_runs(rows: list[dict[str, Any]], speakers: list[str]) -> list[list[dict[str, Any]]]:
    runs: list[list[dict[str, Any]]] = []
    current: list[dict[str, Any]] = []
    previous_index: int | None = None
    for row, speaker in zip(rows, speakers):
        item = dict(row)
        item["speaker"] = speaker
        if previous_index is None or row["non_empty_index"] == previous_index + 1:
            current.append(item)
        else:
            if current:
                runs.append(current)
            current = [item]
        previous_index = row["non_empty_index"]
    if current:
        runs.append(current)
    return runs


def slice_text(slices_path: Path, source_slice_id: str) -> tuple[str, dict[str, Any]]:
    data = load_json(slices_path)
    groups = data.get("groups", [])
    for group in groups:
        if group.get("id") != source_slice_id:
            continue
        parts: list[str] = []
        for item in group.get("slices", []):
            path_value = item.get("path")
            if not path_value:
                continue
            source_path = resolve_project_path(path_value)
            lines = read_text(source_path).splitlines()
            start_line = int(item.get("start_line", 1))
            end_before_line = int(item.get("end_before_line", len(lines) + 1))
            parts.append("\n".join(lines[start_line - 1 : end_before_line - 1]))
        return "\n\n".join(parts), group
    raise ValueError(f"source slice id not found: {source_slice_id}")


def source_dialogue_profile(text: str) -> dict[str, Any]:
    rows = dialogue_rows(text)
    runs = contiguous_runs(rows, ["source"] * len(rows))
    utterance_counts = [len(run) for run in runs]
    pair_units = [math.ceil(count / 2) for count in utterance_counts]
    return {
        "dialogue_lines": len(rows),
        "contiguous_dialogue_runs": len(runs),
        "run_utterance_counts": utterance_counts,
        "run_pair_units": pair_units,
        "pair_units_p50": percentile(pair_units, 0.50),
        "pair_units_p75": percentile(pair_units, 0.75),
        "pair_units_p90": percentile(pair_units, 0.90),
        "pair_units_max": max(pair_units, default=0),
    }


def budget_from_profile(
    profile: dict[str, Any],
    configured_preferred: int,
    configured_hard: int,
) -> dict[str, Any]:
    target = max(1, math.ceil(float(profile.get("pair_units_p75", 0.0))))
    warn = max(target + 1, math.ceil(float(profile.get("pair_units_p90", 0.0))))
    source_max = int(profile.get("pair_units_max", 0))
    hard = max(configured_hard, warn + 1, source_max)
    return {
        "pair_units_target": target,
        "pair_units_warn": warn,
        "pair_units_hard": hard,
        "policy": "source_profile_with_configured_hard_floor",
    }


def resolve_budget(args: argparse.Namespace, config: dict[str, Any] | None) -> dict[str, Any]:
    dialogue_window = (
        config.get("manual_triage", {}).get("dialogue_window", {})
        if config
        else {}
    )
    configured_preferred = int(
        args.preferred_pair_units_max
        if args.preferred_pair_units_max is not None
        else dialogue_window.get("preferred_pair_units_max", 2)
    )
    configured_hard = int(
        args.hard_pair_units_max
        if args.hard_pair_units_max is not None
        else dialogue_window.get("hard_pair_units_max", 5)
    )
    source_slice_id = args.source_slice_id or dialogue_window.get("source_slice_id")
    if args.slices and source_slice_id:
        slices_path = resolve_project_path(args.slices)
        text, group = slice_text(slices_path, source_slice_id)
        profile = source_dialogue_profile(text)
        recommended = budget_from_profile(profile, configured_preferred, configured_hard)
        return {
            "budget_source": "source_slice_profile",
            "source_slice_id": source_slice_id,
            "source_label": group.get("label"),
            "preferred_pair_units_max": recommended["pair_units_warn"],
            "hard_pair_units_max": recommended["pair_units_hard"],
            "target_pair_units_max": recommended["pair_units_target"],
            "profile": profile,
            "policy": recommended["policy"],
            "warnings": [],
        }
    if args.slices and not source_slice_id:
        return {
            "budget_source": "missing_source_window_budget",
            "preferred_pair_units_max": configured_preferred,
            "hard_pair_units_max": configured_hard,
            "target_pair_units_max": configured_preferred,
            "profile": None,
            "policy": "warning_only",
            "warnings": ["source slices provided but no source_slice_id was selected"],
        }
    return {
        "budget_source": "config_or_cli_fallback",
        "preferred_pair_units_max": configured_preferred,
        "hard_pair_units_max": configured_hard,
        "target_pair_units_max": configured_preferred,
        "profile": None,
        "policy": "configured_thresholds",
        "warnings": [],
    }


def analyze_windows(
    runs: list[list[dict[str, Any]]],
    speaker: str,
    preferred_pair_units_max: int,
    hard_pair_units_max: int,
) -> list[dict[str, Any]]:
    windows: list[dict[str, Any]] = []
    for run_index, run in enumerate(runs, start=1):
        speaker_positions = [
            index for index, item in enumerate(run) if item.get("speaker") == speaker
        ]
        if not speaker_positions:
            continue
        left = speaker_positions[0]
        right = speaker_positions[-1]
        window = run[left : right + 1]
        utterance_count = len(window)
        pair_units = math.ceil(utterance_count / 2)
        if pair_units > hard_pair_units_max:
            status = "hard_exceeded"
        elif pair_units > preferred_pair_units_max:
            status = "warn"
        else:
            status = "ok"
        windows.append(
            {
                "run_index": run_index,
                "run_dialogue_count": len(run),
                "line_start": window[0]["line_no"],
                "line_end": window[-1]["line_no"],
                "speaker": speaker,
                "speaker_utterance_count": len(speaker_positions),
                "window_utterance_count": utterance_count,
                "pair_units": pair_units,
                "preferred_pair_units_max": preferred_pair_units_max,
                "hard_pair_units_max": hard_pair_units_max,
                "status": status,
                "speakers": [item.get("speaker", "unknown") for item in window],
                "texts": [item["content"] for item in window],
            }
        )
    return windows


def status_for_pair_units(
    pair_units: int,
    preferred_pair_units_max: int,
    hard_pair_units_max: int,
) -> str:
    if pair_units > hard_pair_units_max:
        return "hard_exceeded"
    if pair_units > preferred_pair_units_max:
        return "warn"
    return "ok"


def analyze_alternating_windows(
    runs: list[list[dict[str, Any]]],
    checked_speakers: list[str],
    preferred_pair_units_max: int,
    hard_pair_units_max: int,
) -> list[dict[str, Any]]:
    checked = set(checked_speakers)
    windows: list[dict[str, Any]] = []

    for run_index, run in enumerate(runs, start=1):
        current: list[dict[str, Any]] = []
        chains: list[list[dict[str, Any]]] = []

        def flush() -> None:
            nonlocal current
            if len(current) >= 2:
                chains.append(current)
            current = []

        for item in run:
            speaker = item.get("speaker", "unknown")
            if speaker not in checked:
                flush()
                continue
            if not current:
                current = [item]
                continue
            if speaker != current[-1].get("speaker"):
                current.append(item)
            else:
                flush()
                current = [item]
        flush()

        for chain_index, chain in enumerate(chains, start=1):
            utterance_count = len(chain)
            pair_units = math.ceil(utterance_count / 2)
            windows.append(
                {
                    "run_index": run_index,
                    "chain_index": chain_index,
                    "run_dialogue_count": len(run),
                    "line_start": chain[0]["line_no"],
                    "line_end": chain[-1]["line_no"],
                    "window_type": "dual_alternating",
                    "utterance_count": utterance_count,
                    "pair_units": pair_units,
                    "preferred_pair_units_max": preferred_pair_units_max,
                    "hard_pair_units_max": hard_pair_units_max,
                    "status": status_for_pair_units(
                        pair_units,
                        preferred_pair_units_max,
                        hard_pair_units_max,
                    ),
                    "speakers": [item.get("speaker", "unknown") for item in chain],
                    "texts": [item["content"] for item in chain],
                }
            )
    return windows


def render_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# Dialogue Window Report",
        "",
        f"- draft: `{result['draft']}`",
        f"- candidate_json: `{result.get('candidate_json') or ''}`",
        f"- generated_at: {result['generated_at']}",
        f"- speakers: `{', '.join(result['speakers'])}`",
        f"- preferred_pair_units_max: {result['preferred_pair_units_max']}",
        f"- hard_pair_units_max: {result['hard_pair_units_max']}",
        f"- budget_source: `{result['budget']['budget_source']}`",
        "",
        "## Summary",
        "",
        f"- dialogue_lines: {result['dialogue_lines']}",
        f"- contiguous_dialogue_runs: {result['contiguous_dialogue_runs']}",
        f"- windows_with_checked_speakers: {len(result['windows'])}",
        f"- dual_alternating_windows: {len(result['alternating_windows'])}",
        f"- max_pair_units: {result['max_pair_units']}",
        f"- alternating_max_pair_units: {result['alternating_max_pair_units']}",
        f"- hard_exceeded_count: {result['hard_exceeded_count']}",
        f"- warn_count: {result['warn_count']}",
        f"- single_speaker_hard_exceeded_count: {result['per_detector']['single_speaker']['hard_exceeded_count']}",
        f"- alternating_hard_exceeded_count: {result['per_detector']['dual_alternating']['hard_exceeded_count']}",
        "",
        "## Budget",
        "",
        f"- target_pair_units_max: {result['budget'].get('target_pair_units_max')}",
        f"- preferred_pair_units_max: {result['budget'].get('preferred_pair_units_max')}",
        f"- hard_pair_units_max: {result['budget'].get('hard_pair_units_max')}",
        f"- policy: `{result['budget'].get('policy')}`",
    ]
    if result["budget"].get("source_slice_id"):
        lines.extend(
            [
                f"- source_slice_id: `{result['budget'].get('source_slice_id')}`",
                f"- source_label: `{result['budget'].get('source_label') or ''}`",
            ]
        )
    if result["budget"].get("profile"):
        profile = result["budget"]["profile"]
        lines.extend(
            [
                f"- source_dialogue_lines: {profile['dialogue_lines']}",
                f"- source_contiguous_dialogue_runs: {profile['contiguous_dialogue_runs']}",
                f"- source_pair_units_p75: {profile['pair_units_p75']}",
                f"- source_pair_units_p90: {profile['pair_units_p90']}",
                f"- source_pair_units_max: {profile['pair_units_max']}",
            ]
        )
    for warning in result["budget"].get("warnings", []):
        lines.append(f"- warning: `{warning}`")
    lines.extend(
        [
            "",
        "## Per Speaker",
        "",
        "| speaker | windows | max pair units | hard exceeded | warn |",
        "|---|---:|---:|---:|---:|",
        ]
    )
    for speaker, summary in result["per_speaker"].items():
        lines.append(
            f"| `{speaker}` | {summary['window_count']} | {summary['max_pair_units']} | "
            f"{summary['hard_exceeded_count']} | {summary['warn_count']} |"
        )
    lines.extend(
        [
            "",
        "## Windows",
        "",
            "| speaker | run | lines | window utterances | pair units | status |",
            "|---|---:|---|---:|---:|---|",
        ]
    )
    for window in result["windows"]:
        lines.append(
            f"| `{window['speaker']}` | {window['run_index']} | {window['line_start']}-{window['line_end']} | "
            f"{window['window_utterance_count']} | {window['pair_units']} | `{window['status']}` |"
        )
    lines.extend(
        [
            "",
            "## Dual Alternating Windows",
            "",
            "| run | chain | lines | utterances | pair units | status | speakers |",
            "|---:|---:|---|---:|---:|---|---|",
        ]
    )
    for window in result["alternating_windows"]:
        lines.append(
            f"| {window['run_index']} | {window['chain_index']} | {window['line_start']}-{window['line_end']} | "
            f"{window['utterance_count']} | {window['pair_units']} | `{window['status']}` | "
            f"`{'/'.join(window['speakers'])}` |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This report only localizes dialogue-run shape. It is not a quality score.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--draft", required=True)
    parser.add_argument("--candidate-json")
    parser.add_argument("--speaker", default="shimamura")
    parser.add_argument("--speakers", nargs="+")
    parser.add_argument("--preferred-pair-units-max", type=int)
    parser.add_argument("--hard-pair-units-max", type=int)
    parser.add_argument("--config", default="analysis/harness_config.json")
    parser.add_argument("--slices")
    parser.add_argument("--source-slice-id")
    parser.add_argument("--output-prefix")
    args = parser.parse_args()

    draft_path = resolve_project_path(args.draft).resolve()
    json_path = None
    if args.candidate_json:
        json_path = resolve_project_path(args.candidate_json).resolve()
    else:
        candidate = companion_json(draft_path)
        if candidate.exists():
            json_path = candidate

    config_path = resolve_project_path(args.config) if args.config else None
    config = load_json(config_path) if config_path and config_path.exists() else None
    budget = resolve_budget(args, config)
    preferred_pair_units_max = int(budget["preferred_pair_units_max"])
    hard_pair_units_max = int(budget["hard_pair_units_max"])

    text = read_text(draft_path)
    rows = dialogue_rows(text)
    structure = load_json(json_path) if json_path and json_path.exists() else None
    speakers = attach_speakers(rows, structure)
    runs = contiguous_runs(rows, speakers)
    checked_speakers = [speaker.lower() for speaker in (args.speakers or [args.speaker])]
    windows: list[dict[str, Any]] = []
    per_speaker: dict[str, dict[str, Any]] = {}
    for speaker in checked_speakers:
        speaker_windows = analyze_windows(
            runs,
            speaker,
            preferred_pair_units_max,
            hard_pair_units_max,
        )
        windows.extend(speaker_windows)
        per_speaker[speaker] = {
            "window_count": len(speaker_windows),
            "max_pair_units": max((window["pair_units"] for window in speaker_windows), default=0),
            "hard_exceeded_count": sum(
                window["status"] == "hard_exceeded" for window in speaker_windows
            ),
            "warn_count": sum(window["status"] == "warn" for window in speaker_windows),
        }
    alternating_windows = analyze_alternating_windows(
        runs,
        checked_speakers,
        preferred_pair_units_max,
        hard_pair_units_max,
    )
    windows.sort(key=lambda window: (window["line_start"], window["speaker"]))
    alternating_windows.sort(key=lambda window: (window["line_start"], window["chain_index"]))

    result = {
        "draft": display_path(draft_path),
        "candidate_json": display_path(json_path) if json_path else None,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "speaker": checked_speakers[0] if len(checked_speakers) == 1 else "multiple",
        "speakers": checked_speakers,
        "preferred_pair_units_max": preferred_pair_units_max,
        "hard_pair_units_max": hard_pair_units_max,
        "budget": budget,
        "dialogue_lines": len(rows),
        "contiguous_dialogue_runs": len(runs),
        "windows": windows,
        "alternating_windows": alternating_windows,
        "per_speaker": per_speaker,
        "max_pair_units": max((window["pair_units"] for window in windows), default=0),
        "alternating_max_pair_units": max(
            (window["pair_units"] for window in alternating_windows),
            default=0,
        ),
        "hard_exceeded_count": (
            sum(window["status"] == "hard_exceeded" for window in windows)
            + sum(window["status"] == "hard_exceeded" for window in alternating_windows)
        ),
        "warn_count": (
            sum(window["status"] == "warn" for window in windows)
            + sum(window["status"] == "warn" for window in alternating_windows)
        ),
        "per_detector": {
            "single_speaker": {
                "window_count": len(windows),
                "max_pair_units": max((window["pair_units"] for window in windows), default=0),
                "hard_exceeded_count": sum(
                    window["status"] == "hard_exceeded" for window in windows
                ),
                "warn_count": sum(window["status"] == "warn" for window in windows),
            },
            "dual_alternating": {
                "window_count": len(alternating_windows),
                "max_pair_units": max(
                    (window["pair_units"] for window in alternating_windows),
                    default=0,
                ),
                "hard_exceeded_count": sum(
                    window["status"] == "hard_exceeded" for window in alternating_windows
                ),
                "warn_count": sum(
                    window["status"] == "warn" for window in alternating_windows
                ),
            },
        },
        "alignment": {
            "markdown_dialogue_lines": len(rows),
            "json_utterances": len(structure.get("utterances", [])) if structure else None,
        },
    }

    if args.output_prefix:
        prefix = resolve_project_path(args.output_prefix).resolve()
        prefix.parent.mkdir(parents=True, exist_ok=True)
        prefix.with_suffix(".json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        prefix.with_suffix(".md").write_text(render_markdown(result), encoding="utf-8")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
