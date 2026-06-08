from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


DEFAULT_PROJECT_ROOT = Path(r"C:\Users\33625\Documents\novel")
REQUIRED_RELATIVE_PATHS = [
    Path("tools/light_harness.py"),
    Path("tools/style_evaluator.py"),
    Path("tools/delta_evaluator.py"),
    Path("analysis/harness_config.json"),
    Path("corpus_slices/slices.json"),
]


def resolve_project_root(raw: str | None) -> Path:
    if raw:
        return Path(raw).expanduser().resolve()
    cwd = Path.cwd().resolve()
    if all((cwd / relative).exists() for relative in REQUIRED_RELATIVE_PATHS):
        return cwd
    return DEFAULT_PROJECT_ROOT.resolve()


def display_path(project_root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(project_root))
    except ValueError:
        return str(path)


def validate_project(project_root: Path) -> dict[str, object]:
    missing = [str(relative) for relative in REQUIRED_RELATIVE_PATHS if not (project_root / relative).exists()]
    return {
        "project_root": str(project_root),
        "ok": not missing,
        "missing": missing,
        "required": [str(relative) for relative in REQUIRED_RELATIVE_PATHS],
    }


def resolve_candidate(project_root: Path, candidate: str) -> Path:
    path = Path(candidate)
    if not path.is_absolute():
        path = project_root / path
    return path.resolve()


def infer_candidates(project_root: Path, run_id: str | None) -> list[Path]:
    if not run_id:
        return []
    candidate_dir = project_root / "drafts" / "candidates" / run_id
    return sorted(candidate_dir.glob("candidate_*.md"))


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate and run the novel candidate gate harness.")
    parser.add_argument("--project-root", help="Novel project root. Defaults to cwd if it looks like the project, otherwise the known workspace path.")
    parser.add_argument("--check-only", action="store_true", help="Only verify required project files.")
    parser.add_argument("--run-id", help="Candidate run id under drafts/candidates and analysis/reports/candidates.")
    parser.add_argument("--candidates", nargs="*", help="Candidate Markdown paths. If omitted, infer candidate_*.md from --run-id.")
    parser.add_argument("--reports-root", help="Optional reports root. Defaults to analysis/reports/candidates under the project.")
    parser.add_argument("--scope", choices=["candidate", "fragment"], default="candidate", help="Use fragment to skip full-candidate length hard gate.")
    parser.add_argument("--allow-fragment", action="store_true", help="Alias for --scope fragment.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    project_root = resolve_project_root(args.project_root)
    validation = validate_project(project_root)
    if args.check_only or not validation["ok"]:
        print(json.dumps(validation, ensure_ascii=False, indent=2))
        return 0 if validation["ok"] else 2

    if not args.run_id:
        print("error: --run-id is required unless --check-only is used", file=sys.stderr)
        return 2

    candidates = [resolve_candidate(project_root, candidate) for candidate in (args.candidates or [])]
    if not candidates:
        candidates = infer_candidates(project_root, args.run_id)
    if not candidates:
        print(f"error: no candidate Markdown files found for run id {args.run_id}", file=sys.stderr)
        return 2

    missing_candidates = [display_path(project_root, candidate) for candidate in candidates if not candidate.exists()]
    if missing_candidates:
        print(f"error: candidate file(s) not found: {', '.join(missing_candidates)}", file=sys.stderr)
        return 2

    reports_root = Path(args.reports_root).expanduser() if args.reports_root else project_root / "analysis" / "reports" / "candidates"
    if not reports_root.is_absolute():
        reports_root = project_root / reports_root
    scope = "fragment" if args.allow_fragment else args.scope

    command = [
        sys.executable,
        str(project_root / "tools" / "light_harness.py"),
        "--run-id",
        args.run_id,
        "--candidates",
        *[str(candidate) for candidate in candidates],
        "--slices",
        str(project_root / "corpus_slices" / "slices.json"),
        "--config",
        str(project_root / "analysis" / "harness_config.json"),
        "--reports-root",
        str(reports_root),
        "--scope",
        scope,
    ]
    completed = subprocess.run(command, cwd=project_root, text=True)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
