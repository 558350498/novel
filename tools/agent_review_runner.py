from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_ROLES = ["agent_gate_auditor", "agent_close_reader"]
OPTIONAL_ROLES = ["agent_regression_checker"]
FORBIDDEN_VERDICT_TERMS = ["final verdict", "最终判定", "通过候选", "候选成功"]


def display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)


def validate_review(path: Path, role: str) -> list[str]:
    errors: list[str] = []
    data = load_json(path)
    if data.get("role") != role:
        errors.append(f"{display(path)} role is {data.get('role')!r}, expected {role!r}")
    for field in ["scope", "candidate_path", "gate_report_path", "claims", "dissent", "recommended_user_questions"]:
        if field not in data:
            errors.append(f"{display(path)} missing `{field}`")
    claims = data.get("claims", [])
    if not isinstance(claims, list):
        errors.append(f"{display(path)} `claims` must be list")
        claims = []
    for index, claim in enumerate(claims):
        if not isinstance(claim, dict):
            errors.append(f"{display(path)} claims[{index}] must be object")
            continue
        for field in ["failure_id", "case_id", "span_ref", "claim", "evidence_type", "confidence"]:
            if field not in claim:
                errors.append(f"{display(path)} claims[{index}] missing `{field}`")
        text = str(claim.get("claim", ""))
        for term in FORBIDDEN_VERDICT_TERMS:
            if term in text:
                errors.append(f"{display(path)} claims[{index}] contains forbidden verdict term `{term}`")
    return errors


def run_contract(run_id: str, require_regression: bool) -> dict[str, Any]:
    reports_dir = ROOT / "analysis" / "reports" / "candidates" / run_id
    roles = REQUIRED_ROLES + (OPTIONAL_ROLES if require_regression else [])
    errors: list[str] = []
    reviews: list[dict[str, Any]] = []
    for role in roles:
        path = reports_dir / f"{role}.json"
        if not path.exists():
            errors.append(f"missing review: {display(path)}")
            continue
        role_errors = validate_review(path, role)
        errors.extend(role_errors)
        reviews.append({"role": role, "path": display(path), "ok": not role_errors})
    return {
        "run_id": run_id,
        "reports_dir": display(reports_dir),
        "require_regression": require_regression,
        "ok": not errors,
        "reviews": reviews,
        "errors": errors,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate multi-agent review contract for a candidate run.")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--require-regression", action="store_true", help="Require agent_regression_checker output.")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        report = run_contract(args.run_id, args.require_regression)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"Agent review contract ok: {report['ok']}")
        for review in report["reviews"]:
            print(f"- {review['role']}: {review['path']} ok={review['ok']}")
        for error in report["errors"]:
            print(f"- [error] {error}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
