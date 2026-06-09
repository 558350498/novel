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
        "",
        "## Summary",
        "",
        f"- dialogue_lines: {result['dialogue_lines']}",
        f"- contiguous_dialogue_runs: {result['contiguous_dialogue_runs']}",
        f"- windows_with_checked_speakers: {len(result['windows'])}",
        f"- max_pair_units: {result['max_pair_units']}",
        f"- hard_exceeded_count: {result['hard_exceeded_count']}",
        f"- warn_count: {result['warn_count']}",
        "",
        "## Per Speaker",
        "",
        "| speaker | windows | max pair units | hard exceeded | warn |",
        "|---|---:|---:|---:|---:|",
    ]
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
    parser.add_argument("--preferred-pair-units-max", type=int, default=2)
    parser.add_argument("--hard-pair-units-max", type=int, default=5)
    parser.add_argument("--output-prefix")
    args = parser.parse_args()

    draft_path = (ROOT / args.draft).resolve() if not Path(args.draft).is_absolute() else Path(args.draft)
    json_path = None
    if args.candidate_json:
        json_path = (ROOT / args.candidate_json).resolve() if not Path(args.candidate_json).is_absolute() else Path(args.candidate_json)
    else:
        candidate = companion_json(draft_path)
        if candidate.exists():
            json_path = candidate

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
            args.preferred_pair_units_max,
            args.hard_pair_units_max,
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
    windows.sort(key=lambda window: (window["line_start"], window["speaker"]))

    result = {
        "draft": display_path(draft_path),
        "candidate_json": display_path(json_path) if json_path else None,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "speaker": checked_speakers[0] if len(checked_speakers) == 1 else "multiple",
        "speakers": checked_speakers,
        "preferred_pair_units_max": args.preferred_pair_units_max,
        "hard_pair_units_max": args.hard_pair_units_max,
        "dialogue_lines": len(rows),
        "contiguous_dialogue_runs": len(runs),
        "windows": windows,
        "per_speaker": per_speaker,
        "max_pair_units": max((window["pair_units"] for window in windows), default=0),
        "hard_exceeded_count": sum(window["status"] == "hard_exceeded" for window in windows),
        "warn_count": sum(window["status"] == "warn" for window in windows),
        "alignment": {
            "markdown_dialogue_lines": len(rows),
            "json_utterances": len(structure.get("utterances", [])) if structure else None,
        },
    }

    if args.output_prefix:
        prefix = (ROOT / args.output_prefix).resolve() if not Path(args.output_prefix).is_absolute() else Path(args.output_prefix)
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
