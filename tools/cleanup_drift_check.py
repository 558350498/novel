from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import project_doctor


ROOT = Path(__file__).resolve().parents[1]
CLEANUP_PLAN = ROOT / "analysis" / "project_cleanup_plan.md"
DEFAULT_RUN_ID = "round6_codex_full_loop_20260609"


@dataclass
class Finding:
    severity: str
    check: str
    path: str
    detail: str

    def to_json(self) -> dict[str, str]:
        return {
            "severity": self.severity,
            "check": self.check,
            "path": self.path,
            "detail": self.detail,
        }


def configure_utf8_stdio() -> None:
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name)
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def project_path(raw_path: str) -> Path:
    path = Path(raw_path.replace("\\", "/"))
    return path if path.is_absolute() else ROOT / path


def display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def clean_table_cell(cell: str) -> str:
    value = cell.strip()
    if value.startswith("`") and value.endswith("`"):
        value = value[1:-1]
    return value.strip()


def extract_table_paths(text: str, heading: str) -> list[str]:
    lines = text.splitlines()
    start = None
    for index, line in enumerate(lines):
        if line.strip() == heading:
            start = index + 1
            break
    if start is None:
        return []

    paths: list[str] = []
    in_table = False
    for line in lines[start:]:
        stripped = line.strip()
        if stripped.startswith("## "):
            break
        if not stripped.startswith("|"):
            continue
        cells = [clean_table_cell(cell) for cell in stripped.strip("|").split("|")]
        if len(cells) < 2:
            continue
        if cells[0] in {"Path", "---"}:
            in_table = True
            continue
        if not in_table:
            continue
        raw_path = cells[0]
        if raw_path and not any(token in raw_path for token in ["pattern", "*"]):
            paths.append(raw_path)
    return paths


def expanded_paths(raw_path: str) -> list[Path]:
    if raw_path.endswith(".md/json"):
        stem = raw_path[:-8]
        return [project_path(stem + ".md"), project_path(stem + ".json")]
    return [project_path(raw_path)]


def check_plan_paths(plan_text: str) -> tuple[list[Finding], dict[str, list[str]]]:
    sections = {
        "active": extract_table_paths(plan_text, "## Keep As Active"),
        "supporting": extract_table_paths(plan_text, "## Keep As Supporting Evidence"),
    }
    findings: list[Finding] = []
    for section, paths in sections.items():
        for raw_path in paths:
            for path in expanded_paths(raw_path):
                if not path.exists():
                    severity = "error" if section == "active" else "warning"
                    findings.append(
                        Finding(
                            severity,
                            f"cleanup_plan_{section}",
                            display(path),
                            f"path listed in project_cleanup_plan.md `{section}` section is missing",
                        )
                    )
    return findings, sections


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def active_run_summary(run_id: str) -> dict[str, Any]:
    candidate_dir = ROOT / "drafts" / "candidates" / run_id
    reports_dir = ROOT / "analysis" / "reports" / "candidates" / run_id
    candidates = sorted(candidate_dir.glob("candidate_*.md"))
    latest_candidate = candidates[-1] if candidates else None
    manifest_path = reports_dir / "manifest.json"
    manifest = load_json(manifest_path) if manifest_path.exists() else {}
    return {
        "run_id": run_id,
        "candidate_dir": display(candidate_dir),
        "reports_dir": display(reports_dir),
        "latest_candidate": display(latest_candidate) if latest_candidate else None,
        "manifest": display(manifest_path) if manifest_path.exists() else None,
        "status_counts": manifest.get("status_counts", {}),
    }


def cleanup_candidates() -> dict[str, list[str]]:
    token_streams = sorted((ROOT / "analysis" / "reports").glob("**/*.tokens.txt"))
    stale_distribution_dirs = sorted((ROOT / "analysis" / "reports" / "candidates").glob("*distribution*"))
    old_round_dirs = [
        path
        for path in sorted((ROOT / "analysis" / "reports" / "candidates").glob("round*"))
        if path.name != DEFAULT_RUN_ID and path.name != "round5_auto_prompt_20260608"
    ]
    return {
        "token_streams_after_confirmation": [display(path) for path in token_streams],
        "stale_distribution_dirs_for_review": [display(path) for path in stale_distribution_dirs],
        "old_round_report_dirs_for_review": [display(path) for path in old_round_dirs],
    }


def build_report(run_id: str, strict_warnings: bool) -> dict[str, Any]:
    plan_text = CLEANUP_PLAN.read_text(encoding="utf-8-sig")
    findings, plan_sections = check_plan_paths(plan_text)
    doctor_report = project_doctor.build_report(run_id)
    for finding in doctor_report["findings"]:
        severity = str(finding["severity"])
        if strict_warnings and severity == "warning":
            severity = "error"
        findings.append(
            Finding(
                severity,
                f"project_doctor:{finding['check']}",
                str(finding["path"]),
                str(finding["detail"]),
            )
        )
    cleanup = cleanup_candidates()
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "run_id": run_id,
        "cleanup_plan": display(CLEANUP_PLAN),
        "strict_warnings": strict_warnings,
        "ok": not any(finding.severity == "error" for finding in findings),
        "error_count": sum(finding.severity == "error" for finding in findings),
        "warning_count": sum(finding.severity == "warning" for finding in findings),
        "active_run": active_run_summary(run_id),
        "cleanup_plan_sections": {key: len(value) for key, value in plan_sections.items()},
        "cleanup_candidates": cleanup,
        "findings": [finding.to_json() for finding in findings],
        "notes": [
            "This check is read-only.",
            "Deletion or archive actions still require explicit user confirmation.",
            "Current candidates, reports, user reviews, protocol docs, and source texts are protected by policy.",
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    active = report["active_run"]
    lines = [
        "# Project Cleanup / Drift Summary",
        "",
        f"- generated_at: `{report['generated_at']}`",
        f"- run_id: `{report['run_id']}`",
        f"- cleanup_plan: `{report['cleanup_plan']}`",
        f"- ok: `{report['ok']}`",
        f"- errors: {report['error_count']}",
        f"- warnings: {report['warning_count']}",
        "",
        "## Active Path",
        "",
        f"- candidate_dir: `{active['candidate_dir']}`",
        f"- reports_dir: `{active['reports_dir']}`",
        f"- latest_candidate: `{active.get('latest_candidate') or ''}`",
        f"- manifest: `{active.get('manifest') or ''}`",
        f"- status_counts: `{json.dumps(active.get('status_counts', {}), ensure_ascii=False)}`",
        "",
        "## Cleanup Plan Coverage",
        "",
        f"- active paths listed: {report['cleanup_plan_sections'].get('active', 0)}",
        f"- supporting paths listed: {report['cleanup_plan_sections'].get('supporting', 0)}",
        "",
        "## Findings",
        "",
    ]
    if report["findings"]:
        for finding in report["findings"]:
            lines.append(f"- `{finding['severity']}` `{finding['check']}` `{finding['path']}`: {finding['detail']}")
    else:
        lines.append("- none")
    lines.extend(["", "## Review-Only Cleanup Candidates", ""])
    for key, values in report["cleanup_candidates"].items():
        lines.append(f"### {key}")
        if values:
            lines.extend(f"- `{value}`" for value in values)
        else:
            lines.append("- none")
        lines.append("")
    lines.extend(["## Notes", ""])
    lines.extend(f"- {note}" for note in report["notes"])
    return "\n".join(lines).rstrip() + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Read-only cleanup and drift check based on analysis/project_cleanup_plan.md.")
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    parser.add_argument("--strict-warnings", action="store_true", help="Treat project_doctor warnings as errors.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of Markdown.")
    parser.add_argument("--output", type=Path, help="Optional output path for the rendered report.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    configure_utf8_stdio()
    args = parse_args(argv)
    report = build_report(args.run_id, args.strict_warnings)
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n" if args.json else render_markdown(report)
    if args.output:
        output = args.output if args.output.is_absolute() else ROOT / args.output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
