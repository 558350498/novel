from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
JSON_REF_RE = re.compile(r"^(?P<path>.+\.json)#(?P<pointer>/.*)$")
JSONL_REF_RE = re.compile(r"^(?P<path>.+\.jsonl)#entry_id=(?P<entry_id>[^#]+)$")


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


def project_path(raw_path: str) -> Path:
    candidate = Path(raw_path.replace("\\", "/"))
    return candidate if candidate.is_absolute() else ROOT / candidate


def decode_pointer_token(token: str) -> str:
    return token.replace("~1", "/").replace("~0", "~")


def resolve_json_pointer(data: Any, pointer: str) -> Any:
    current = data
    if not pointer.startswith("/"):
        raise ValueError("JSON pointer must start with /")
    for raw_token in pointer.split("/")[1:]:
        token = decode_pointer_token(raw_token)
        if isinstance(current, dict):
            if token not in current:
                raise KeyError(token)
            current = current[token]
            continue
        if isinstance(current, list):
            try:
                index = int(token)
            except ValueError as exc:
                raise KeyError(token) from exc
            try:
                current = current[index]
            except IndexError as exc:
                raise KeyError(token) from exc
            continue
        raise KeyError(token)
    return current


def validate_json_ref(ref: str) -> list[Finding]:
    findings: list[Finding] = []
    match = JSON_REF_RE.match(ref)
    if not match:
        return [Finding("error", ref, "JSON evidence ref must use <path>.json#/json/pointer")]
    path = project_path(match.group("path"))
    if not path.exists():
        return [Finding("error", ref, "referenced JSON file does not exist")]
    try:
        data = load_json(path)
        resolve_json_pointer(data, match.group("pointer"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, KeyError, ValueError) as exc:
        findings.append(Finding("error", ref, f"JSON pointer does not resolve: {exc}"))
    return findings


def validate_jsonl_ref(ref: str) -> list[Finding]:
    match = JSONL_REF_RE.match(ref)
    if not match:
        return [Finding("error", ref, "JSONL evidence ref must use <path>.jsonl#entry_id=<id>")]
    path = project_path(match.group("path"))
    entry_id = match.group("entry_id")
    if not path.exists():
        return [Finding("error", ref, "referenced JSONL file does not exist")]
    try:
        for line_no, raw_line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), start=1):
            if not raw_line.strip():
                continue
            entry = json.loads(raw_line)
            if isinstance(entry, dict) and entry.get("entry_id") == entry_id:
                return []
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return [Finding("error", ref, f"could not read JSONL ref: {exc}")]
    return [Finding("error", ref, f"entry_id `{entry_id}` not found")]


def validate_evidence_ref(ref: str) -> list[Finding]:
    if ".md#" in ref or ref.endswith(".md"):
        return [Finding("error", ref, "Markdown is a human view, not machine evidence")]
    if ".jsonl#" in ref:
        return validate_jsonl_ref(ref)
    if ".json#" in ref:
        return validate_json_ref(ref)
    return [Finding("error", ref, "evidence ref must point to JSON or JSONL")]


def evidence_refs(item: dict[str, Any]) -> list[str]:
    refs: list[str] = []
    raw_ref = item.get("evidence_ref")
    if isinstance(raw_ref, str) and raw_ref.strip():
        refs.append(raw_ref.strip())
    raw_refs = item.get("evidence_refs")
    if isinstance(raw_refs, list):
        refs.extend(str(ref).strip() for ref in raw_refs if str(ref).strip())
    return refs


def require_refs(path: Path, item: Any, label: str) -> list[Finding]:
    if not isinstance(item, dict):
        return [Finding("error", display(path), f"{label} must be object")]
    refs = evidence_refs(item)
    findings: list[Finding] = []
    if not refs:
        findings.append(Finding("error", display(path), f"{label} missing evidence_ref/evidence_refs"))
    for ref in refs:
        findings.extend(validate_evidence_ref(ref))
    return findings


def check_rewrite_plan(path: Path) -> list[Finding]:
    data = load_json(path)
    if not isinstance(data, dict):
        return [Finding("error", display(path), "rewrite_plan must be object")]
    planner = data.get("planner", {})
    if not isinstance(planner, dict):
        return [Finding("error", display(path), "planner must be object when present")]
    findings: list[Finding] = []
    for field in ["triggered_checks", "segment_signals"]:
        items = planner.get(field, [])
        if items is None:
            continue
        if not isinstance(items, list):
            findings.append(Finding("error", display(path), f"planner.{field} must be list"))
            continue
        for index, item in enumerate(items):
            findings.extend(require_refs(path, item, f"planner.{field}[{index}]"))
    return findings


def check_agent_review(path: Path) -> list[Finding]:
    data = load_json(path)
    if not isinstance(data, dict):
        return [Finding("error", display(path), "agent review must be object")]
    claims = data.get("claims", [])
    if not isinstance(claims, list):
        return [Finding("error", display(path), "claims must be list")]
    findings: list[Finding] = []
    for index, claim in enumerate(claims):
        findings.extend(require_refs(path, claim, f"claims[{index}]"))
    return findings


def check_failure_cases(path: Path) -> list[Finding]:
    data = load_json(path)
    if not isinstance(data, dict):
        return [Finding("error", display(path), "failure_cases must be object")]
    cases = data.get("cases", [])
    if not isinstance(cases, list):
        return [Finding("error", display(path), "cases must be list")]
    findings: list[Finding] = []
    for index, case in enumerate(cases):
        findings.extend(require_refs(path, case, f"cases[{index}]"))
    return findings


def discover_targets() -> list[tuple[str, Path]]:
    targets: list[tuple[str, Path]] = []
    targets.extend(("rewrite_plan", path) for path in sorted((ROOT / "drafts" / "candidates").glob("**/rewrite_plan.json")))
    targets.extend(("agent_review", path) for path in sorted((ROOT / "analysis" / "reports" / "candidates").glob("**/agent_*.json")))
    failure_cases = ROOT / "analysis" / "failure_cases.json"
    if failure_cases.exists():
        targets.append(("failure_cases", failure_cases))
    return targets


def run_checks(targets: list[tuple[str, Path]] | None = None) -> dict[str, Any]:
    targets = discover_targets() if targets is None else targets
    findings: list[Finding] = []
    for kind, path in targets:
        try:
            if kind == "rewrite_plan":
                findings.extend(check_rewrite_plan(path))
            elif kind == "agent_review":
                findings.extend(check_agent_review(path))
            elif kind == "failure_cases":
                findings.extend(check_failure_cases(path))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            findings.append(Finding("error", display(path), str(exc)))
    return {
        "ok": not any(finding.severity == "error" for finding in findings),
        "target_count": len(targets),
        "error_count": sum(finding.severity == "error" for finding in findings),
        "warning_count": sum(finding.severity == "warning" for finding in findings),
        "findings": [finding.to_json() for finding in findings],
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate machine evidence refs in rewrite plans, agent reviews, and failure cases.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    report = run_checks()
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"Evidence ref check ok: {report['ok']}")
        print(f"targets: {report['target_count']}, errors: {report['error_count']}, warnings: {report['warning_count']}")
        for finding in report["findings"]:
            print(f"- [{finding['severity']}] {finding['path']}: {finding['detail']}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
