from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUN_ID = "round6_codex_full_loop_20260609"
CHECK_DOCS = [
    Path("README.md"),
    Path("INDEX.md"),
    Path("PROJECT_STATUS.md"),
    Path("analysis/README.md"),
    Path("analysis/reports/README.md"),
]
REQUIRED_ACTIVE_PATHS = [
    Path("AGENTS.md"),
    Path(".github/workflows/ci.yml"),
    Path(".github/workflows/cleanup-drift.yml"),
    Path(".github/workflows/trend-report.yml"),
    Path("README.md"),
    Path("INDEX.md"),
    Path("PROJECT_STATUS.md"),
    Path("plans/README.md"),
    Path("plans/current_productization.md"),
    Path("plans/technical_debt.md"),
    Path("plans/taxonomy_triplet_issues.md"),
    Path("analysis/README.md"),
    Path("analysis/reports/README.md"),
    Path("analysis/project_cleanup_plan.md"),
    Path("analysis/artifact_boundary.md"),
    Path("analysis/artifacts_manifest.json"),
    Path("analysis/trend_report_contract.md"),
    Path("analysis/harness_config.json"),
    Path("analysis/failure_taxonomy.md"),
    Path("analysis/failure_cases.json"),
    Path("analysis/gate_report_protocol.md"),
    Path("analysis/rewrite_policy.md"),
    Path("analysis/rewrite_plan_protocol.md"),
    Path("analysis/editing_actions.md"),
    Path("analysis/review_ledger.jsonl"),
    Path("analysis/regression_comparison.md"),
    Path("analysis/productization_gate_v1.md"),
    Path("analysis/lexicon_taxonomy.md"),
    Path("corpus_slices/slices.json"),
    Path("novel_index.json"),
    Path("skills/novel-gate-harness/SKILL.md"),
    Path("skills/novel-gate-harness/references/project_architecture.md"),
    Path("skills/novel-gate-harness/references/editing_actions.md"),
    Path("skills/novel-gate-harness/scripts/run_candidate_gate.py"),
    Path("tools/project_doctor.py"),
    Path("tools/cleanup_drift_check.py"),
    Path("tools/trend_report.py"),
    Path("tools/editing_action_check.py"),
    Path("tools/evidence_ref_check.py"),
    Path("tools/light_harness.py"),
    Path("tools/style_evaluator.py"),
    Path("tools/delta_evaluator.py"),
    Path("tools/eder_delta_evaluator.py"),
    Path("tools/dialogue_window_analyzer.py"),
    Path("tools/source_shape_analyzer.py"),
    Path("tools/corpus_tokenizer.py"),
    Path("tools/corpus_profiler.py"),
]
STALE_ACTIVE_REFERENCES = [
    "drafts/current.md",
    "drafts/round2.md",
    "drafts/round3.md",
    "analysis/generation_prompt.md",
    "analysis/generation_prompt_round3.md",
    "analysis/generation_prompt_round4.md",
    "analysis/reports/current.md",
    "analysis/reports/codex_review.md",
    "analysis/reports/diff.md",
    "analysis/reports/delta_current.md",
    "analysis/reports/source_chapter_shape.md",
    "analysis/reports/candidates/existing_rounds_audit",
    "analysis/reports/candidates/round4_three_versions",
]


def configure_utf8_stdio() -> None:
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name)
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


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


def project_path(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def read_text(path: Path) -> str:
    return project_path(path).read_text(encoding="utf-8-sig")


def load_json(path: Path) -> dict[str, Any]:
    with project_path(path).open("r", encoding="utf-8-sig") as f:
        return json.load(f)


def check_required_paths() -> list[Finding]:
    findings: list[Finding] = []
    for path in REQUIRED_ACTIVE_PATHS:
        if not project_path(path).exists():
            findings.append(Finding("error", "required_path", str(path), "required active path is missing"))
    return findings


def check_run(run_id: str) -> list[Finding]:
    findings: list[Finding] = []
    candidate_dir = Path("drafts/candidates") / run_id
    reports_dir = Path("analysis/reports/candidates") / run_id
    if not project_path(candidate_dir).is_dir():
        findings.append(Finding("error", "active_run", str(candidate_dir), "candidate run directory is missing"))
        return findings
    if not project_path(reports_dir).is_dir():
        findings.append(Finding("error", "active_run", str(reports_dir), "reports run directory is missing"))
        return findings

    manifest_path = reports_dir / "manifest.json"
    if not project_path(manifest_path).exists():
        findings.append(Finding("error", "active_run", str(manifest_path), "manifest is missing"))
    else:
        manifest = load_json(manifest_path)
        if manifest.get("run_id") != run_id:
            findings.append(Finding("error", "active_run", str(manifest_path), f"manifest run_id is {manifest.get('run_id')!r}"))

    for candidate in sorted(project_path(candidate_dir).glob("candidate_*.md")):
        relative_candidate = candidate.relative_to(ROOT)
        companion = candidate.with_suffix(".json")
        stem = candidate.stem
        if not companion.exists():
            findings.append(Finding("error", "candidate_pair", display(candidate), "missing companion JSON"))
        for suffix in ["style.json", "delta.json", "gate.json"]:
            report = project_path(reports_dir) / f"{stem}_{suffix}"
            if not report.exists():
                findings.append(Finding("warning", "candidate_report", str(reports_dir / report.name), f"missing report for {relative_candidate}"))

    return findings


def markdown_targets(text: str) -> list[str]:
    targets: list[str] = []
    for match in re.finditer(r"\[[^\]]+\]\(([^)]+)\)", text):
        target = match.group(1).strip()
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        targets.append(target)
    for match in re.finditer(r"`([^`\n]+)`", text):
        target = match.group(1).strip()
        if "/" in target or "\\" in target:
            targets.append(target)
    return targets


def normalize_target(doc: Path, raw_target: str) -> Path | None:
    target = raw_target.split("#", 1)[0].strip()
    if not target:
        return None
    if " " in target:
        return None
    if any(token in target for token in ["<run_id>", "<active_run_id>", "*.tokens.txt", "round2_*", "round3_*"]):
        return None
    if "/" in target and not re.match(
        r"^(\.?\.?/)?(analysis|candidates|corpus_slices|data|drafts|skills|tools|README|INDEX|PROJECT_STATUS|novel_index)",
        target,
    ):
        return None
    if target.startswith(("./", "../")):
        return (project_path(doc).parent / target).resolve()
    if re.match(r"^[A-Za-z]:", target):
        return Path(target)
    if target.startswith("/"):
        return Path(target)
    if "/" in target or "\\" in target:
        return (ROOT / target).resolve()
    return None


def target_exists(doc: Path, raw_target: str) -> bool:
    target = raw_target.split("#", 1)[0].strip()
    if target.endswith(".md/json"):
        return target_exists(doc, target[:-5]) and target_exists(doc, target[:-8] + ".json")
    if target.endswith(".markdown/json"):
        return target_exists(doc, target[:-5]) and target_exists(doc, target[:-13] + ".json")

    normalized = normalize_target(doc, raw_target)
    if normalized is None:
        return True
    if normalized.exists():
        return True
    if not re.match(r"^[A-Za-z]:", target) and not target.startswith(("/", "./", "../")):
        doc_relative = (project_path(doc).parent / target).resolve()
        if doc_relative.exists():
            return True
    return False


def check_doc_links() -> list[Finding]:
    findings: list[Finding] = []
    for doc in CHECK_DOCS:
        full_doc = project_path(doc)
        if not full_doc.exists():
            continue
        text = read_text(doc)
        for raw_target in markdown_targets(text):
            if not target_exists(doc, raw_target):
                findings.append(Finding("warning", "doc_target", str(doc), f"target does not exist: {raw_target}"))
        if doc != Path("analysis/project_cleanup_plan.md"):
            for stale in STALE_ACTIVE_REFERENCES:
                if stale in text:
                    findings.append(Finding("warning", "stale_reference", str(doc), f"stale active reference: {stale}"))
    return findings


def build_report(run_id: str) -> dict[str, Any]:
    findings = check_required_paths()
    findings.extend(check_run(run_id))
    findings.extend(check_doc_links())
    return {
        "project_root": str(ROOT),
        "run_id": run_id,
        "ok": not any(finding.severity == "error" for finding in findings),
        "error_count": sum(finding.severity == "error" for finding in findings),
        "warning_count": sum(finding.severity == "warning" for finding in findings),
        "findings": [finding.to_json() for finding in findings],
    }


def render_text(report: dict[str, Any]) -> str:
    lines = [
        f"Project doctor for {report['run_id']}",
        f"ok: {report['ok']}",
        f"errors: {report['error_count']}",
        f"warnings: {report['warning_count']}",
    ]
    for finding in report["findings"]:
        lines.append(f"- [{finding['severity']}] {finding['check']} {finding['path']}: {finding['detail']}")
    return "\n".join(lines) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check active project paths and entrypoint doc drift.")
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID, help="Active candidate run id.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text.")
    parser.add_argument("--strict-warnings", action="store_true", help="Treat warnings as a failing exit code.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    configure_utf8_stdio()
    args = parse_args(argv)
    report = build_report(args.run_id)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render_text(report), end="")
    if report["error_count"]:
        return 2
    if args.strict_warnings and report["warning_count"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
