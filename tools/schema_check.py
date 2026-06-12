from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ALLOWED_SPEAKERS = {"adachi", "shimamura", "tarumi", "narration", "other"}
ALLOWED_VERDICTS = {"pass", "fail", "mixed", "needs_manual_triage", "defer"}
ALLOWED_AGENT_ROLES = {"agent_gate_auditor", "agent_close_reader", "agent_regression_checker"}


@dataclass
class Finding:
    severity: str
    path: str
    detail: str

    def to_json(self) -> dict[str, str]:
        return {"severity": self.severity, "path": self.path, "detail": self.detail}


def display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)


def add_required(findings: list[Finding], path: Path, data: dict[str, Any], fields: list[str]) -> None:
    for field in fields:
        if field not in data:
            findings.append(Finding("error", display(path), f"missing required field `{field}`"))


def expect_type(findings: list[Finding], path: Path, value: Any, expected: type, field: str) -> bool:
    if not isinstance(value, expected):
        findings.append(Finding("error", display(path), f"`{field}` must be {expected.__name__}"))
        return False
    return True


def check_candidate(path: Path) -> list[Finding]:
    findings: list[Finding] = []
    data = load_json(path)
    if not expect_type(findings, path, data, dict, "$"):
        return findings

    add_required(findings, path, data, ["version", "candidate", "kernel_id", "utterances"])
    utterances = data.get("utterances", [])
    if not expect_type(findings, path, utterances, list, "utterances"):
        return findings

    seen_ids: set[str] = set()
    for index, utterance in enumerate(utterances):
        field = f"utterances[{index}]"
        if not isinstance(utterance, dict):
            findings.append(Finding("error", display(path), f"`{field}` must be object"))
            continue
        add_required(findings, path, utterance, ["id", "speaker", "text"])
        utterance_id = str(utterance.get("id", "")).strip()
        if utterance_id in seen_ids:
            findings.append(Finding("error", display(path), f"duplicate utterance id `{utterance_id}`"))
        if utterance_id:
            seen_ids.add(utterance_id)
        speaker = str(utterance.get("speaker", "")).strip()
        if speaker and speaker not in ALLOWED_SPEAKERS:
            findings.append(Finding("error", display(path), f"`{field}.speaker` has unknown value `{speaker}`"))
        if not str(utterance.get("text", "")).strip():
            findings.append(Finding("error", display(path), f"`{field}.text` must not be empty"))
        for list_field in ["responds_to", "surface_terms_received", "explanation_markers"]:
            if list_field in utterance and not isinstance(utterance[list_field], list):
                findings.append(Finding("error", display(path), f"`{field}.{list_field}` must be list"))
        if "deep_understanding" in utterance and not isinstance(utterance["deep_understanding"], bool):
            findings.append(Finding("error", display(path), f"`{field}.deep_understanding` must be bool"))

    if "scene_beats" in data and not isinstance(data["scene_beats"], list):
        findings.append(Finding("error", display(path), "`scene_beats` must be list"))
    return findings


def check_rewrite_plan(path: Path) -> list[Finding]:
    findings: list[Finding] = []
    data = load_json(path)
    if not expect_type(findings, path, data, dict, "$"):
        return findings
    add_required(findings, path, data, ["version", "run_id", "candidate", "rewrite_scope", "target", "output_candidate"])
    if data.get("rewrite_scope") not in {"local", "fragment", "candidate"}:
        findings.append(Finding("error", display(path), "`rewrite_scope` must be local, fragment, or candidate"))
    if "stop_after_rewrite" in data and not isinstance(data["stop_after_rewrite"], bool):
        findings.append(Finding("error", display(path), "`stop_after_rewrite` must be bool"))
    if "diagnostic_sources" in data and not isinstance(data["diagnostic_sources"], list):
        findings.append(Finding("error", display(path), "`diagnostic_sources` must be list"))
    if "target" in data and not isinstance(data["target"], dict):
        findings.append(Finding("error", display(path), "`target` must be object"))
    return findings


def check_agent_review(path: Path) -> list[Finding]:
    findings: list[Finding] = []
    data = load_json(path)
    if not expect_type(findings, path, data, dict, "$"):
        return findings
    add_required(findings, path, data, ["role", "scope", "candidate_path", "gate_report_path", "claims", "dissent", "recommended_user_questions"])
    role = data.get("role")
    if role not in ALLOWED_AGENT_ROLES:
        findings.append(Finding("error", display(path), f"`role` must be one of {sorted(ALLOWED_AGENT_ROLES)}"))
    if not isinstance(data.get("claims", []), list):
        findings.append(Finding("error", display(path), "`claims` must be list"))
        return findings
    for index, claim in enumerate(data.get("claims", [])):
        field = f"claims[{index}]"
        if not isinstance(claim, dict):
            findings.append(Finding("error", display(path), f"`{field}` must be object"))
            continue
        add_required(findings, path, claim, ["failure_id", "case_id", "span_ref", "claim", "evidence_type", "confidence"])
        if any(word in str(claim.get("claim", "")).lower() for word in ["final verdict", "pass verdict", "fail verdict"]):
            findings.append(Finding("error", display(path), f"`{field}.claim` appears to contain a forbidden final verdict"))
    if not isinstance(data.get("dissent", []), list):
        findings.append(Finding("error", display(path), "`dissent` must be list"))
    if not isinstance(data.get("recommended_user_questions", []), list):
        findings.append(Finding("error", display(path), "`recommended_user_questions` must be list"))
    return findings


def check_ledger(path: Path) -> list[Finding]:
    findings: list[Finding] = []
    required = ["entry_id", "created_at", "reviewer", "artifact_type", "artifact_path", "verdict", "why", "case_ids", "failure_ids", "follow_up"]
    seen_ids: set[str] = set()
    for line_no, raw_line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), start=1):
        if not raw_line.strip():
            continue
        try:
            entry = json.loads(raw_line)
        except json.JSONDecodeError as exc:
            findings.append(Finding("error", f"{display(path)}:{line_no}", f"invalid JSONL: {exc}"))
            continue
        if not isinstance(entry, dict):
            findings.append(Finding("error", f"{display(path)}:{line_no}", "ledger entry must be object"))
            continue
        if entry.get("entry_type") == "ledger_schema":
            continue
        for field in required:
            if field not in entry:
                findings.append(Finding("error", f"{display(path)}:{line_no}", f"missing required field `{field}`"))
        entry_id = str(entry.get("entry_id", "")).strip()
        if entry_id in seen_ids:
            findings.append(Finding("error", f"{display(path)}:{line_no}", f"duplicate entry_id `{entry_id}`"))
        if entry_id:
            seen_ids.add(entry_id)
        if entry.get("verdict") not in ALLOWED_VERDICTS:
            findings.append(Finding("error", f"{display(path)}:{line_no}", f"unknown verdict `{entry.get('verdict')}`"))
        for list_field in ["case_ids", "failure_ids", "follow_up"]:
            if list_field in entry and not isinstance(entry[list_field], list):
                findings.append(Finding("error", f"{display(path)}:{line_no}", f"`{list_field}` must be list"))
    return findings


def check_failure_cases(path: Path) -> list[Finding]:
    findings: list[Finding] = []
    data = load_json(path)
    if not expect_type(findings, path, data, dict, "$"):
        return findings
    cases = data.get("cases", [])
    if not expect_type(findings, path, cases, list, "cases"):
        return findings
    seen_ids: set[str] = set()
    cases_by_failure: dict[str, set[str]] = {}
    required = ["case_id", "failure_id", "case_type", "source_type", "source_path", "span_ref", "expected_gate", "review_status", "evidence_summary", "user_verdict_ref"]
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            findings.append(Finding("error", display(path), f"`cases[{index}]` must be object"))
            continue
        add_required(findings, path, case, required)
        case_id = str(case.get("case_id", "")).strip()
        if case_id in seen_ids:
            findings.append(Finding("error", display(path), f"duplicate case_id `{case_id}`"))
        if case_id:
            seen_ids.add(case_id)
        failure_id = str(case.get("failure_id", "")).strip()
        case_type = case.get("case_type")
        if case_type not in {"positive", "negative", "borderline"}:
            findings.append(Finding("error", display(path), f"`cases[{index}].case_type` is invalid"))
        elif failure_id:
            cases_by_failure.setdefault(failure_id, set()).add(str(case_type))

    required_triplets = data.get("required_triplet_failure_ids", [])
    if required_triplets and not isinstance(required_triplets, list):
        findings.append(Finding("error", display(path), "`required_triplet_failure_ids` must be list"))
        required_triplets = []
    missing_triplets = data.get("missing_case_triplets", [])
    if missing_triplets and not isinstance(missing_triplets, list):
        findings.append(Finding("error", display(path), "`missing_case_triplets` must be list"))
        missing_triplets = []
    missing_triplet_ids = {str(item) for item in missing_triplets}
    required_case_types = {"positive", "negative", "borderline"}
    for failure_id in required_triplets:
        failure_id = str(failure_id)
        present_types = cases_by_failure.get(failure_id, set())
        missing_types = sorted(required_case_types - present_types)
        if missing_types:
            findings.append(
                Finding(
                    "error",
                    display(path),
                    f"`{failure_id}` missing required triplet case type(s): {', '.join(missing_types)}",
                )
            )
        if failure_id in missing_triplet_ids:
            findings.append(
                Finding(
                    "error",
                    display(path),
                    f"`{failure_id}` is required-complete but still listed in missing_case_triplets",
                )
            )
    return findings


def discover_targets() -> list[tuple[str, Path]]:
    targets: list[tuple[str, Path]] = []
    candidate_jsons = [
        path
        for path in sorted((ROOT / "drafts" / "candidates").glob("**/candidate_*.json"))
        if path.stem.removeprefix("candidate_").isdigit()
    ]
    targets.extend(("candidate", path) for path in candidate_jsons)
    targets.extend(("rewrite_plan", path) for path in sorted((ROOT / "drafts" / "candidates").glob("**/rewrite_plan.json")))
    targets.extend(("agent_review", path) for path in sorted((ROOT / "analysis" / "reports" / "candidates").glob("**/agent_*.json")))
    ledger = ROOT / "analysis" / "review_ledger.jsonl"
    if ledger.exists():
        targets.append(("ledger", ledger))
    failure_cases = ROOT / "analysis" / "failure_cases.json"
    if failure_cases.exists():
        targets.append(("failure_cases", failure_cases))
    return targets


def run_checks(targets: list[tuple[str, Path]]) -> list[Finding]:
    findings: list[Finding] = []
    for kind, path in targets:
        try:
            if kind == "candidate":
                findings.extend(check_candidate(path))
            elif kind == "rewrite_plan":
                findings.extend(check_rewrite_plan(path))
            elif kind == "agent_review":
                findings.extend(check_agent_review(path))
            elif kind == "ledger":
                findings.extend(check_ledger(path))
            elif kind == "failure_cases":
                findings.extend(check_failure_cases(path))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            findings.append(Finding("error", display(path), str(exc)))
    return findings


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate project JSON contracts without external dependencies.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    targets = discover_targets()
    findings = run_checks(targets)
    report = {
        "ok": not any(finding.severity == "error" for finding in findings),
        "target_count": len(targets),
        "error_count": sum(finding.severity == "error" for finding in findings),
        "warning_count": sum(finding.severity == "warning" for finding in findings),
        "findings": [finding.to_json() for finding in findings],
    }
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"Schema check ok: {report['ok']}")
        print(f"targets: {report['target_count']}, errors: {report['error_count']}, warnings: {report['warning_count']}")
        for finding in findings:
            print(f"- [{finding.severity}] {finding.path}: {finding.detail}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
