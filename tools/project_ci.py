from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUN_ID = "round6_codex_full_loop_20260609"


def configure_utf8_stdio() -> None:
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name)
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def run_step(name: str, command: list[str]) -> dict[str, Any]:
    env = {
        **os.environ,
        "PYTHONIOENCODING": "utf-8",
        "PYTHONUTF8": "1",
    }
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    return {
        "name": name,
        "command": command,
        "returncode": completed.returncode,
        "ok": completed.returncode == 0,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the local project CI contract.")
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    parser.add_argument("--strict-warnings", action="store_true", help="Treat project_doctor warnings as failures.")
    parser.add_argument("--require-regression-review", action="store_true", help="Require agent_regression_checker contract.")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    configure_utf8_stdio()
    args = parse_args(argv)
    doctor_cmd = [sys.executable, "tools/project_doctor.py", "--run-id", args.run_id]
    if args.strict_warnings:
        doctor_cmd.append("--strict-warnings")

    steps = [
        run_step("project_doctor", doctor_cmd),
        run_step("cleanup_drift_check", [sys.executable, "tools/cleanup_drift_check.py", "--strict-warnings"]),
        run_step("gate_check", [sys.executable, "skills/novel-gate-harness/scripts/run_candidate_gate.py", "--check-only"]),
        run_step("schema_check", [sys.executable, "tools/schema_check.py"]),
        run_step("editing_action_check", [sys.executable, "tools/editing_action_check.py"]),
        run_step("evidence_ref_check", [sys.executable, "tools/evidence_ref_check.py"]),
        run_step("trend_report", [sys.executable, "tools/trend_report.py", "--check-only"]),
        run_step(
            "agent_review_contract",
            [
                sys.executable,
                "tools/agent_review_runner.py",
                "--run-id",
                args.run_id,
                *(["--require-regression"] if args.require_regression_review else []),
            ],
        ),
        run_step("unit_tests", [sys.executable, "-m", "unittest", "discover", "-s", "tests"]),
    ]
    report = {
        "ok": all(step["ok"] for step in steps),
        "run_id": args.run_id,
        "steps": steps,
    }
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"Project CI ok: {report['ok']}")
        for step in steps:
            print(f"\n[{step['name']}] exit={step['returncode']}")
            if step["stdout"]:
                print(step["stdout"])
            if step["stderr"]:
                print(step["stderr"])
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
