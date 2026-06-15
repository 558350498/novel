from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FAILURE_IDS = [
    "F006_dialogue_shape_collapse",
    "F008_dialogue_run_overextension",
    "F009_originality_overconstraint",
]
ALLOWED_GATE_STATES = {"failed_auto_gate", "needs_manual_triage", "pending_user_review"}
REQUIRED_METRIC_KEYS = {
    "char_count",
    "short_dialogue_pct_1_10",
    "mid_dialogue_pct_11_40",
    "dialogue_distribution_l1",
    "dialogue_ge_200",
    "max_dialogue_len",
}
REQUIRED_DIALOGUE_WINDOW_KEYS = {
    "present",
    "max_pair_units",
    "alternating_max_pair_units",
    "hard_exceeded_count",
    "warn_count",
}
REQUIRED_FAILURE_SOURCE_KEYS = {"gate_inferred", "case_registry", "ledger"}
REQUIRED_REGRESSION_KEYS = {"agent_regression_checker", "regression_comparison", "present"}

try:
    from tools import evidence_ref_check
except ImportError:  # pragma: no cover
    import evidence_ref_check  # type: ignore


@dataclass
class ContractFinding:
    path: str
    detail: str

    def to_json(self) -> dict[str, str]:
        return {"path": self.path, "detail": self.detail}


def configure_utf8_stdio() -> None:
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name)
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def project_path(raw_path: str | Path) -> Path:
    path = Path(str(raw_path).replace("\\", "/"))
    return path if path.is_absolute() else ROOT / path


def display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    if not path.exists():
        return entries
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        if not raw_line.strip():
            continue
        entry = json.loads(raw_line)
        if isinstance(entry, dict) and entry.get("entry_type") != "ledger_schema":
            entries.append(entry)
    return entries


def git_commit() -> str | None:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError:
        return None
    if completed.returncode != 0:
        return None
    return completed.stdout.strip() or None


def default_output_dir() -> Path:
    manifest_path = ROOT / "analysis" / "artifacts_manifest.json"
    if manifest_path.exists():
        manifest = load_json(manifest_path)
        external_root = manifest.get("external_root")
        if isinstance(external_root, str) and external_root.strip():
            return (ROOT / external_root / "trend").resolve()
    return (ROOT.parent / "novel-reports" / "trend").resolve()


def discover_manifests() -> list[Path]:
    return sorted((ROOT / "analysis" / "reports" / "candidates").glob("*/manifest.json"))


def case_failure_ids_by_run() -> dict[str, set[str]]:
    path = ROOT / "analysis" / "failure_cases.json"
    if not path.exists():
        return {}
    data = load_json(path)
    cases = data.get("cases", []) if isinstance(data, dict) else []
    hits: dict[str, set[str]] = {}
    run_ids = [manifest.parent.name for manifest in discover_manifests()]
    for case in cases:
        if not isinstance(case, dict):
            continue
        failure_id = case.get("failure_id")
        if not isinstance(failure_id, str):
            continue
        refs = case.get("evidence_refs", [])
        haystack = " ".join(
            str(value)
            for value in [
                case.get("source_path", ""),
                case.get("span_ref", ""),
                *(refs if isinstance(refs, list) else []),
            ]
        )
        for run_id in run_ids:
            if run_id in haystack:
                hits.setdefault(run_id, set()).add(failure_id)
    return hits


def ledger_entries_by_run(entries: list[dict[str, Any]], run_id: str) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    for entry in entries:
        artifact_path = str(entry.get("artifact_path", ""))
        if run_id in artifact_path:
            matches.append(entry)
    return matches


def latest_candidate(manifest: dict[str, Any]) -> dict[str, Any]:
    candidates = manifest.get("candidates", [])
    if isinstance(candidates, list) and candidates:
        candidates = [candidate for candidate in candidates if isinstance(candidate, dict)]
        if candidates:
            return candidates[-1]
    return {}


def load_dialogue_window(reports_dir: Path, candidate: dict[str, Any]) -> dict[str, Any]:
    candidate_path = str(candidate.get("candidate_path", ""))
    if not candidate_path:
        return {}
    stem = Path(candidate_path.replace("\\", "/")).stem
    path = reports_dir / f"{stem}_dialogue_window.json"
    if not path.exists():
        return {}
    data = load_json(path)
    return data if isinstance(data, dict) else {}


def gate_inferred_failures(candidate: dict[str, Any], dialogue_window: dict[str, Any]) -> set[str]:
    metrics = candidate.get("metrics", {})
    hits: set[str] = set()
    if isinstance(metrics, dict):
        short_pct = metrics.get("short_dialogue_pct_1_10")
        mid_pct = metrics.get("mid_dialogue_pct_11_40")
        l1 = metrics.get("dialogue_distribution_l1")
        short_fail = isinstance(short_pct, (int, float)) and short_pct > 65.0
        mid_fail = isinstance(mid_pct, (int, float)) and mid_pct < 30.0
        l1_fail = isinstance(l1, (int, float)) and l1 > 60.0
        if short_fail or mid_fail or l1_fail:
            hits.add("F006_dialogue_shape_collapse")
    hard_exceeded = dialogue_window.get("hard_exceeded_count")
    if isinstance(hard_exceeded, (int, float)) and hard_exceeded > 0:
        hits.add("F008_dialogue_run_overextension")
    return hits


def compact_ledger_entry(entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "entry_id": entry.get("entry_id"),
        "created_at": entry.get("created_at"),
        "artifact_type": entry.get("artifact_type"),
        "artifact_path": entry.get("artifact_path"),
        "verdict": entry.get("verdict"),
        "failure_ids": entry.get("failure_ids", []),
        "case_ids": entry.get("case_ids", []),
    }


def status_from_counts(status_counts: Any) -> str | None:
    if not isinstance(status_counts, dict):
        return None
    for status in ["failed_auto_gate", "needs_manual_triage", "pending_user_review"]:
        value = status_counts.get(status)
        if isinstance(value, int) and value > 0:
            return status
    return None


def build_rows(
    manifests: list[Path] | None = None,
    ledger_entries: list[dict[str, Any]] | None = None,
    evidence_ok: bool | None = None,
) -> list[dict[str, Any]]:
    manifests = discover_manifests() if manifests is None else manifests
    ledger_entries = load_jsonl(ROOT / "analysis" / "review_ledger.jsonl") if ledger_entries is None else ledger_entries
    case_hits = case_failure_ids_by_run()
    commit = git_commit()
    if evidence_ok is None:
        evidence_ok = bool(evidence_ref_check.run_checks()["ok"])

    rows: list[dict[str, Any]] = []
    for manifest_path in manifests:
        manifest = load_json(manifest_path)
        if not isinstance(manifest, dict):
            continue
        run_id = str(manifest.get("run_id") or manifest_path.parent.name)
        reports_dir = project_path(str(manifest.get("reports_dir") or display(manifest_path.parent)))
        candidate = latest_candidate(manifest)
        dialogue_window = load_dialogue_window(reports_dir, candidate)
        ledger_matches = ledger_entries_by_run(ledger_entries, run_id)
        ledger_failure_ids = {
            str(failure_id)
            for entry in ledger_matches
            for failure_id in entry.get("failure_ids", [])
            if failure_id
        }
        inferred = gate_inferred_failures(candidate, dialogue_window)
        case_based = case_hits.get(run_id, set())
        all_failure_hits = inferred | case_based | ledger_failure_ids
        metrics = candidate.get("metrics", {}) if isinstance(candidate.get("metrics"), dict) else {}
        regression = {
            "agent_regression_checker": (reports_dir / "agent_regression_checker.json").exists(),
            "regression_comparison": (reports_dir / "regression_comparison.md").exists(),
        }
        regression["present"] = any(regression.values())
        rows.append(
            {
                "version": 1,
                "run_id": run_id,
                "generated_at": manifest.get("generated_at"),
                "harness_commit": commit,
                "reports_dir": display(reports_dir),
                "manifest_path": display(manifest_path),
                "candidate_count": len(manifest.get("candidates", [])) if isinstance(manifest.get("candidates"), list) else 0,
                "latest_candidate": candidate.get("candidate_path"),
                "gate_state": candidate.get("status") or status_from_counts(manifest.get("status_counts", {})),
                "status_counts": manifest.get("status_counts", {}),
                "metrics": {
                    "char_count": metrics.get("char_count"),
                    "short_dialogue_pct_1_10": metrics.get("short_dialogue_pct_1_10"),
                    "mid_dialogue_pct_11_40": metrics.get("mid_dialogue_pct_11_40"),
                    "dialogue_distribution_l1": metrics.get("dialogue_distribution_l1"),
                    "dialogue_ge_200": metrics.get("dialogue_ge_200"),
                    "max_dialogue_len": metrics.get("max_dialogue_len"),
                },
                "delta_first": candidate.get("delta_first"),
                "failure_hits": {failure_id: failure_id in all_failure_hits for failure_id in DEFAULT_FAILURE_IDS},
                "failure_hit_sources": {
                    "gate_inferred": sorted(inferred),
                    "case_registry": sorted(case_based),
                    "ledger": sorted(ledger_failure_ids),
                },
                "dialogue_window": {
                    "present": bool(dialogue_window),
                    "max_pair_units": dialogue_window.get("max_pair_units"),
                    "alternating_max_pair_units": dialogue_window.get("alternating_max_pair_units"),
                    "hard_exceeded_count": dialogue_window.get("hard_exceeded_count"),
                    "warn_count": dialogue_window.get("warn_count"),
                },
                "user_verdicts": [compact_ledger_entry(entry) for entry in ledger_matches],
                "regression_review": regression,
                "evidence_refs_ok": evidence_ok,
            }
        )
    return sorted(rows, key=lambda row: (str(row.get("generated_at") or ""), str(row.get("run_id") or "")))


def require_type(findings: list[ContractFinding], path: str, value: Any, expected: tuple[type, ...], type_name: str) -> bool:
    if not isinstance(value, expected):
        findings.append(ContractFinding(path, f"expected {type_name}, got {type(value).__name__}"))
        return False
    return True


def validate_rows(rows: list[dict[str, Any]]) -> list[ContractFinding]:
    findings: list[ContractFinding] = []
    if not rows:
        findings.append(ContractFinding("rows", "trend report must contain at least one row"))
        return findings

    required_top_level = {
        "version",
        "run_id",
        "generated_at",
        "harness_commit",
        "reports_dir",
        "manifest_path",
        "candidate_count",
        "latest_candidate",
        "gate_state",
        "status_counts",
        "metrics",
        "delta_first",
        "failure_hits",
        "failure_hit_sources",
        "dialogue_window",
        "user_verdicts",
        "regression_review",
        "evidence_refs_ok",
    }
    for index, row in enumerate(rows):
        prefix = f"rows[{index}]"
        missing = sorted(required_top_level - set(row))
        for key in missing:
            findings.append(ContractFinding(f"{prefix}.{key}", "missing required field"))
        if missing:
            continue

        if row.get("version") != 1:
            findings.append(ContractFinding(f"{prefix}.version", "must be 1"))
        require_type(findings, f"{prefix}.run_id", row.get("run_id"), (str,), "string")
        if not str(row.get("run_id", "")).strip():
            findings.append(ContractFinding(f"{prefix}.run_id", "must not be empty"))
        if row.get("generated_at") is not None:
            require_type(findings, f"{prefix}.generated_at", row.get("generated_at"), (str,), "string or null")
        if row.get("harness_commit") is not None:
            require_type(findings, f"{prefix}.harness_commit", row.get("harness_commit"), (str,), "string or null")
        require_type(findings, f"{prefix}.reports_dir", row.get("reports_dir"), (str,), "string")
        require_type(findings, f"{prefix}.manifest_path", row.get("manifest_path"), (str,), "string")
        require_type(findings, f"{prefix}.candidate_count", row.get("candidate_count"), (int,), "integer")
        if row.get("latest_candidate") is not None:
            require_type(findings, f"{prefix}.latest_candidate", row.get("latest_candidate"), (str,), "string or null")
        if row.get("gate_state") is not None:
            if not require_type(findings, f"{prefix}.gate_state", row.get("gate_state"), (str,), "string or null"):
                continue
            if row.get("gate_state") not in ALLOWED_GATE_STATES:
                findings.append(ContractFinding(f"{prefix}.gate_state", f"invalid gate state: {row.get('gate_state')}"))
        require_type(findings, f"{prefix}.status_counts", row.get("status_counts"), (dict,), "object")
        require_type(findings, f"{prefix}.user_verdicts", row.get("user_verdicts"), (list,), "list")
        require_type(findings, f"{prefix}.evidence_refs_ok", row.get("evidence_refs_ok"), (bool,), "boolean")

        metrics = row.get("metrics")
        if require_type(findings, f"{prefix}.metrics", metrics, (dict,), "object"):
            for key in sorted(REQUIRED_METRIC_KEYS - set(metrics)):
                findings.append(ContractFinding(f"{prefix}.metrics.{key}", "missing required metric field"))
            for key in sorted(REQUIRED_METRIC_KEYS & set(metrics)):
                value = metrics[key]
                if value is not None and not isinstance(value, (int, float)):
                    findings.append(ContractFinding(f"{prefix}.metrics.{key}", "must be number or null"))

        failure_hits = row.get("failure_hits")
        if require_type(findings, f"{prefix}.failure_hits", failure_hits, (dict,), "object"):
            missing_hits = sorted(set(DEFAULT_FAILURE_IDS) - set(failure_hits))
            for failure_id in missing_hits:
                findings.append(ContractFinding(f"{prefix}.failure_hits.{failure_id}", "missing required failure hit key"))
            for failure_id in DEFAULT_FAILURE_IDS:
                if failure_id in failure_hits and not isinstance(failure_hits[failure_id], bool):
                    findings.append(ContractFinding(f"{prefix}.failure_hits.{failure_id}", "must be boolean"))

        sources = row.get("failure_hit_sources")
        if require_type(findings, f"{prefix}.failure_hit_sources", sources, (dict,), "object"):
            for key in sorted(REQUIRED_FAILURE_SOURCE_KEYS - set(sources)):
                findings.append(ContractFinding(f"{prefix}.failure_hit_sources.{key}", "missing required source list"))
            for key in sorted(REQUIRED_FAILURE_SOURCE_KEYS & set(sources)):
                values = sources[key]
                if not isinstance(values, list) or not all(isinstance(item, str) for item in values):
                    findings.append(ContractFinding(f"{prefix}.failure_hit_sources.{key}", "must be list of strings"))

        dialogue_window = row.get("dialogue_window")
        if require_type(findings, f"{prefix}.dialogue_window", dialogue_window, (dict,), "object"):
            for key in sorted(REQUIRED_DIALOGUE_WINDOW_KEYS - set(dialogue_window)):
                findings.append(ContractFinding(f"{prefix}.dialogue_window.{key}", "missing required dialogue-window field"))
            if "present" in dialogue_window and not isinstance(dialogue_window["present"], bool):
                findings.append(ContractFinding(f"{prefix}.dialogue_window.present", "must be boolean"))
            for key in sorted((REQUIRED_DIALOGUE_WINDOW_KEYS - {"present"}) & set(dialogue_window)):
                value = dialogue_window[key]
                if value is not None and not isinstance(value, (int, float)):
                    findings.append(ContractFinding(f"{prefix}.dialogue_window.{key}", "must be number or null"))

        regression = row.get("regression_review")
        if require_type(findings, f"{prefix}.regression_review", regression, (dict,), "object"):
            for key in sorted(REQUIRED_REGRESSION_KEYS - set(regression)):
                findings.append(ContractFinding(f"{prefix}.regression_review.{key}", "missing required regression field"))
            for key in sorted(REQUIRED_REGRESSION_KEYS & set(regression)):
                if not isinstance(regression[key], bool):
                    findings.append(ContractFinding(f"{prefix}.regression_review.{key}", "must be boolean"))
    return findings


def yes_no(value: Any) -> str:
    return "yes" if bool(value) else "no"


def value_or_dash(value: Any) -> str:
    if value is None:
        return "-"
    return str(value)


def render_markdown(rows: list[dict[str, Any]], ledger_entries: list[dict[str, Any]], output_dir: Path) -> str:
    generated_at = datetime.now().isoformat(timespec="seconds")
    evidence_ok = all(bool(row.get("evidence_refs_ok")) for row in rows) if rows else False
    lines = [
        "# Candidate Run Trend Summary",
        "",
        f"- generated_at: `{generated_at}`",
        f"- source_repo: `{ROOT}`",
        f"- output_dir: `{output_dir}`",
        f"- rows: {len(rows)}",
        f"- evidence_refs_ok: `{evidence_ok}`",
        "",
        "## Run Table",
        "",
        "| generated_at | run_id | gate_state | F006 | F008 | F009 | user_verdict | regression_review | short% | mid% | L1 | delta_first |",
        "|---|---|---|---|---|---|---|---|---:|---:|---:|---|",
    ]
    for row in rows:
        metrics = row.get("metrics", {})
        failure_hits = row.get("failure_hits", {})
        verdicts = ",".join(str(entry.get("verdict")) for entry in row.get("user_verdicts", [])) or "-"
        lines.append(
            "| "
            + " | ".join(
                [
                    value_or_dash(row.get("generated_at")),
                    f"`{row.get('run_id')}`",
                    value_or_dash(row.get("gate_state")),
                    yes_no(failure_hits.get("F006_dialogue_shape_collapse")),
                    yes_no(failure_hits.get("F008_dialogue_run_overextension")),
                    yes_no(failure_hits.get("F009_originality_overconstraint")),
                    verdicts,
                    yes_no(row.get("regression_review", {}).get("present")),
                    value_or_dash(metrics.get("short_dialogue_pct_1_10")),
                    value_or_dash(metrics.get("mid_dialogue_pct_11_40")),
                    value_or_dash(metrics.get("dialogue_distribution_l1")),
                    value_or_dash(row.get("delta_first")),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Ledger Signals",
            "",
            "| created_at | entry_id | verdict | failure_ids | artifact_path |",
            "|---|---|---|---|---|",
        ]
    )
    for entry in ledger_entries:
        lines.append(
            "| "
            + " | ".join(
                [
                    value_or_dash(entry.get("created_at")),
                    f"`{entry.get('entry_id')}`",
                    value_or_dash(entry.get("verdict")),
                    ", ".join(str(item) for item in entry.get("failure_ids", [])) or "-",
                    f"`{entry.get('artifact_path')}`",
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- This is a derived trend view, not a user verdict.",
            "- Gate and Delta states remain diagnostic only.",
            "- `F009` may appear as a ledger/prompt-policy signal even when no single run row owns it.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(rows: list[dict[str, Any]], ledger_entries: list[dict[str, Any]], output_dir: Path) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = output_dir / "runs.jsonl"
    markdown_path = output_dir / "weekly_summary.md"
    jsonl_path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )
    markdown_path.write_text(render_markdown(rows, ledger_entries, output_dir), encoding="utf-8")
    return {
        "runs_jsonl": str(jsonl_path),
        "weekly_summary": str(markdown_path),
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate candidate-run trend artifacts from manifests and ledger entries.")
    parser.add_argument("--output-dir", type=Path, default=None, help="Directory for runs.jsonl and weekly_summary.md.")
    parser.add_argument("--dry-run", action="store_true", help="Build the trend report without writing files.")
    parser.add_argument("--check-only", action="store_true", help="Validate the trend row contract without writing files.")
    parser.add_argument("--json", action="store_true", help="Emit JSON summary.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    configure_utf8_stdio()
    args = parse_args(argv)
    output_dir = args.output_dir.resolve() if args.output_dir else default_output_dir()
    ledger_entries = load_jsonl(ROOT / "analysis" / "review_ledger.jsonl")
    evidence_report = evidence_ref_check.run_checks()
    rows = build_rows(ledger_entries=ledger_entries, evidence_ok=bool(evidence_report["ok"]))
    contract_findings = validate_rows(rows)
    ok = bool(rows) and bool(evidence_report["ok"]) and not contract_findings
    written: dict[str, str] = {}
    write_enabled = not args.dry_run and not args.check_only
    if ok and write_enabled:
        written = write_outputs(rows, ledger_entries, output_dir)

    report = {
        "ok": ok,
        "dry_run": args.dry_run or args.check_only,
        "check_only": args.check_only,
        "row_count": len(rows),
        "output_dir": str(output_dir),
        "written": written,
        "contract": {
            "ok": not contract_findings,
            "error_count": len(contract_findings),
            "findings": [finding.to_json() for finding in contract_findings],
        },
        "evidence_ref_check": {
            "ok": evidence_report["ok"],
            "target_count": evidence_report["target_count"],
            "error_count": evidence_report["error_count"],
            "warning_count": evidence_report["warning_count"],
        },
        "runs": [row["run_id"] for row in rows],
    }
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"Trend report ok: {report['ok']}")
        print(f"rows: {report['row_count']}")
        print(f"output_dir: {report['output_dir']}")
        print(f"dry_run: {report['dry_run']}")
        print(f"contract_ok: {report['contract']['ok']}")
        for finding in report["contract"]["findings"]:
            print(f"- [contract] {finding['path']}: {finding['detail']}")
        for label, path in written.items():
            print(f"{label}: {path}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
