#!/usr/bin/env python3
"""Capture local pytest release evidence into docs/release."""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RELEASE_DIR = REPO_ROOT / "docs" / "release"


@dataclass(frozen=True)
class EvidenceRun:
    name: str
    command: list[str]
    output_path: Path
    required_pattern: str


RUNS = {
    "unit": EvidenceRun(
        name="unit",
        command=["pytest", "-c", "pytest.ini", "tests/unit", "-q", "--no-cov"],
        output_path=RELEASE_DIR / "unit_latest_green.txt",
        required_pattern=r"\bpassed\b",
    ),
    "integration": EvidenceRun(
        name="integration",
        command=["pytest", "-c", "pytest.ini", "tests/integration", "-q", "--no-cov"],
        output_path=RELEASE_DIR / "integration_latest_green.txt",
        required_pattern=r"\bpassed\b",
    ),
    "full": EvidenceRun(
        name="full",
        command=["pytest", "-c", "pytest.ini", "-q", "--no-cov"],
        output_path=RELEASE_DIR / "full_pytest_latest_green.txt",
        required_pattern=r"\bpassed\b",
    ),
}


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run(evidence: EvidenceRun) -> int:
    RELEASE_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Running {evidence.name}: {' '.join(evidence.command)}")
    result = subprocess.run(
        evidence.command,
        cwd=REPO_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )

    body = [
        f"# EduBoost release pytest evidence: {evidence.name}",
        f"# Captured at: {_timestamp()}",
        f"# Command: {' '.join(evidence.command)}",
        f"# Return code: {result.returncode}",
        "",
        result.stdout,
    ]
    evidence.output_path.write_text("\n".join(body), encoding="utf-8")
    print(f"Wrote {evidence.output_path}")

    if result.returncode != 0:
        print(f"{evidence.name} pytest command failed", file=sys.stderr)
        return result.returncode or 1

    if re.search(evidence.required_pattern, result.stdout) is None:
        print(f"{evidence.name} evidence did not contain expected pass summary", file=sys.stderr)
        return 1

    return 0


def _validate(path: Path) -> bool:
    if not path.exists():
        print(f"- FAIL [file] {path}: missing")
        return False

    text = path.read_text(encoding="utf-8")
    has_return_zero = "# Return code: 0" in text
    has_passed = re.search(r"\b\d+\s+passed\b", text) is not None
    has_failures = any(token in text for token in (" failed", " errors", "ERROR ", "FAILED "))

    if has_return_zero and has_passed and not has_failures:
        print(f"- PASS [evidence] {path}: green pytest summary present")
        return True

    print(f"- FAIL [evidence] {path}: missing green summary or contains failure markers")
    return False


def validate_all() -> int:
    print("Pytest release evidence validation")
    ok = all(_validate(run.output_path) for run in RUNS.values())
    return 0 if ok else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "scope",
        choices=["unit", "integration", "full", "all", "validate"],
        help="Evidence scope to capture or validate.",
    )
    args = parser.parse_args(argv)

    if args.scope == "validate":
        return validate_all()

    scopes = ["unit", "integration", "full"] if args.scope == "all" else [args.scope]
    for scope in scopes:
        code = _run(RUNS[scope])
        if code != 0:
            return code

    return validate_all() if args.scope == "all" else 0


if __name__ == "__main__":
    raise SystemExit(main())
