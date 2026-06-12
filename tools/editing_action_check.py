from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ACTIONS_PATH = ROOT / "analysis" / "editing_actions.md"
ACTION_HEADING_RE = re.compile(r"^###\s+`([^`]+)`\s*$")
ACTION_ID_RE = re.compile(r"^[a-z][a-z0-9_]*$")
ACTION_REF_KEYS = {
    "action_id",
    "editing_action_id",
}
ACTION_LIST_KEYS = {
    "editing_actions",
    "editing_action_ids",
    "recommended_editing_actions",
    "allowed_editing_actions",
}


@dataclass
class Finding:
    severity: str
    path: str
    detail: str

    def to_json(self) -> dict[str, str]:
        return {
            "severity": self.severity,
            "path": self.path,
            "detail": self.detail,
        }


def display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def load_action_ids(path: Path = DEFAULT_ACTIONS_PATH) -> tuple[set[str], list[Finding]]:
    findings: list[Finding] = []
    if not path.exists():
        return set(), [Finding("error", display(path), "editing actions file is missing")]

    action_ids: set[str] = set()
    for line_no, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), start=1):
        match = ACTION_HEADING_RE.match(line)
        if not match:
            continue
        action_id = match.group(1)
        if not ACTION_ID_RE.match(action_id):
            findings.append(Finding("error", f"{display(path)}:{line_no}", f"invalid action_id `{action_id}`"))
        if action_id in action_ids:
            findings.append(Finding("error", f"{display(path)}:{line_no}", f"duplicate action_id `{action_id}`"))
        action_ids.add(action_id)

    if not action_ids:
        findings.append(Finding("error", display(path), "no action headings found"))
    return action_ids, findings


def discover_rewrite_plans() -> list[Path]:
    paths = list((ROOT / "drafts" / "candidates").glob("**/rewrite_plan.json"))
    paths.extend((ROOT / "demo").glob("**/rewrite_plan.json"))
    return sorted(path for path in paths if path.is_file())


def discover_agent_notes() -> list[Path]:
    return sorted((ROOT / "analysis" / "reports" / "candidates").glob("**/agent_*.json"))


def collect_action_refs(value: Any) -> list[str]:
    refs: list[str] = []

    def visit(item: Any, key: str | None = None) -> None:
        if isinstance(item, dict):
            for child_key, child_value in item.items():
                if child_key in ACTION_REF_KEYS and isinstance(child_value, str):
                    refs.append(child_value)
                    continue
                if child_key in ACTION_LIST_KEYS:
                    collect_from_action_list(child_value)
                    continue
                visit(child_value, child_key)
            return
        if isinstance(item, list):
            for child in item:
                visit(child, key)

    def collect_from_action_list(item: Any) -> None:
        if isinstance(item, str):
            refs.append(item)
            return
        if isinstance(item, list):
            for child in item:
                collect_from_action_list(child)
            return
        if isinstance(item, dict):
            for child_key in ACTION_REF_KEYS:
                child_value = item.get(child_key)
                if isinstance(child_value, str):
                    refs.append(child_value)

    visit(value)
    return refs


def declares_rewrite_plan(data: dict[str, Any]) -> bool:
    scope = data.get("rewrite_scope")
    if scope in {"local", "fragment"}:
        return True
    if data.get("allowed_auto_rewrite") is True:
        return True
    if data.get("stop_after_rewrite") is True and data.get("output_candidate"):
        return True
    return False


def validate_action_refs(path: Path, refs: list[str], action_ids: set[str]) -> list[Finding]:
    findings: list[Finding] = []
    for ref in refs:
        if ref not in action_ids:
            findings.append(Finding("error", display(path), f"unknown editing action_id `{ref}`"))
    return findings


def check_rewrite_plan(path: Path, action_ids: set[str]) -> tuple[list[Finding], int]:
    data = load_json(path)
    if not isinstance(data, dict):
        return [Finding("error", display(path), "rewrite_plan must be a JSON object")], 0

    refs = collect_action_refs(data)
    findings = validate_action_refs(path, refs, action_ids)
    if declares_rewrite_plan(data) and not refs:
        findings.append(
            Finding(
                "error",
                display(path),
                "local rewrite plan must reference at least one legal editing action_id",
            )
        )
    return findings, len(refs)


def check_agent_note(path: Path, action_ids: set[str]) -> tuple[list[Finding], int]:
    data = load_json(path)
    refs = collect_action_refs(data)
    return validate_action_refs(path, refs, action_ids), len(refs)


def run_checks() -> dict[str, Any]:
    action_ids, findings = load_action_ids()
    checked_refs = 0
    checked_targets = 1

    for path in discover_rewrite_plans():
        checked_targets += 1
        try:
            plan_findings, ref_count = check_rewrite_plan(path, action_ids)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            plan_findings, ref_count = [Finding("error", display(path), str(exc))], 0
        findings.extend(plan_findings)
        checked_refs += ref_count

    for path in discover_agent_notes():
        checked_targets += 1
        try:
            note_findings, ref_count = check_agent_note(path, action_ids)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            note_findings, ref_count = [Finding("error", display(path), str(exc))], 0
        findings.extend(note_findings)
        checked_refs += ref_count

    return {
        "ok": not any(finding.severity == "error" for finding in findings),
        "action_count": len(action_ids),
        "checked_targets": checked_targets,
        "checked_action_refs": checked_refs,
        "findings": [finding.to_json() for finding in findings],
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate editing action references in rewrite plans and agent notes.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    report = run_checks()
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"Editing action check ok: {report['ok']}")
        print(f"actions: {report['action_count']}, targets: {report['checked_targets']}, refs: {report['checked_action_refs']}")
        for finding in report["findings"]:
            print(f"- [{finding['severity']}] {finding['path']}: {finding['detail']}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
