#!/usr/bin/env python3
from __future__ import annotations

import ast
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.staging_smoke_evidence_acceptance import ACCEPTED_STATUS, write_status  # noqa: E402

CRITICAL = [
    "scripts/staging_smoke_evidence_acceptance.py",
    "scripts/patch_staging_smoke_evidence_registry.py",
    "scripts/check_staging_smoke_evidence_acceptance.py",
    "tests/unit/test_staging_smoke_evidence_acceptance.py",
]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _entry(text: str, item_id: str) -> str:
    match = re.search(
        rf"(?ms)(^  - id: {re.escape(item_id)}\n.*?)(?=^  - id: |\Z)",
        text,
    )
    if not match:
        raise AssertionError(f"missing registry entry {item_id}")
    return match.group(1)


def main() -> int:
    failures: list[str] = []
    status = write_status()

    print("Staging smoke evidence acceptance check")
    print(f"- INFO status: {status.status}")
    print(f"- INFO workflow: {status.workflow_name}")
    print(f"- INFO run URL: {status.run_url}")
    print(f"- INFO staging URL: {status.staging_base_url}")
    print(f"- INFO SHA: {status.head_sha}")

    if status.status != ACCEPTED_STATUS:
        failures.extend(status.blockers)
    else:
        print("- PASS accepted staging smoke evidence status generated")

    for path in CRITICAL:
        ast.parse(_read(path))
        print(f"- PASS syntax {path}")

    if not os.getenv("SKIP_PYTEST_RECURSION"):
        env = {**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"}
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "-c",
                "pytest.ini",
                "tests/unit/test_staging_smoke_evidence_acceptance.py",
                "-q",
                "--no-cov",
                "--tb=short",
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
            check=False,
        )
        print(result.stdout)
        if result.returncode != 0:
            failures.append("staging smoke evidence unit tests failed")

    ruff = subprocess.run(
        [
            sys.executable,
            "-m",
            "ruff",
            "check",
            *CRITICAL,
            "--select",
            "F821,F401,F811,E402",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )

    if ruff.returncode == 0:
        print("- PASS focused Ruff staging smoke evidence acceptance check")
    else:
        failures.append("focused Ruff failed")
        print(ruff.stdout)

    registry = ROOT / "docs/release/evidence_status_registry.yml"
    if registry.exists() and status.status == ACCEPTED_STATUS:
        text = registry.read_text(encoding="utf-8")
        for item_id in ["STAGING-001", "STAGING-001R"]:
            entry = _entry(text, item_id)
            for required in [
                "proof_status: integration-passing",
                "closure_blocker: none",
                "release_ready: true",
                "blocks_beta: false",
            ]:
                if required not in entry:
                    failures.append(f"{item_id} missing {required}")
            if status.run_id not in entry:
                failures.append(f"{item_id} missing run ID {status.run_id}")
            if status.current_commit not in entry:
                failures.append(f"{item_id} missing commit SHA {status.current_commit}")
            if status.staging_base_url not in entry:
                failures.append(f"{item_id} missing staging URL {status.staging_base_url}")

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("- PASS staging smoke evidence acceptance check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
