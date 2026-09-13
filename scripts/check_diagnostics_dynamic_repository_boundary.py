#!/usr/bin/env python3
from __future__ import annotations
import subprocess  # nosec B404 — subprocess constants support the controlled wrapper

import ast
from scripts._subprocess import run
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIAGNOSTICS = ROOT / "app/api_v2_routers/diagnostics.py"
BOUNDARY = ROOT / "app/api_v2_deps/diagnostic_repositories.py"

CRITICAL = [
    "app/services/diagnostic_domain_service.py",
    "app/api_v2_routers/diagnostics.py",
    "scripts/check_diagnostics_dynamic_repository_boundary.py",
    "tests/unit/test_diagnostics_dynamic_repository_boundary.py",
]

DISALLOWED_ROUTER_TOKENS = (
    "importlib.import_module",
    "from app.repositories",
    "import app.repositories",
    "app.repositories.",
)

DISALLOWED_ROUTER_CALLS = (
    "LearnerRepository(db)",
    "GuardianRepository(db)",
    "IRTRepository(db)",
    "DiagnosticRepository(db)",
    "KnowledgeGapRepository(db)",
    "ItemBankRepository(db)",
    "DiagnosticSessionRepository(db)",
    "MasteryRepository(db)",
    "_LearnerRepo(db)",
    "_ItemBankRepo(db)",
)


def main() -> int:
    failures: list[str] = []
    print("Diagnostics dynamic repository boundary check")

    diagnostics_source = DIAGNOSTICS.read_text(encoding="utf-8")

    if BOUNDARY.exists():
        failures.append(f"Reflection boundary {BOUNDARY} still exists; must be eliminated.")
    else:
        print(f"- PASS eliminated dynamic reflection shim {BOUNDARY.name}")

    for token in DISALLOWED_ROUTER_TOKENS:
        if token in diagnostics_source:
            failures.append(f"diagnostics.py still contains disallowed token: {token}")
        else:
            print(f"- PASS diagnostics.py excludes {token}")

    for call in DISALLOWED_ROUTER_CALLS:
        if call in diagnostics_source:
            failures.append(f"diagnostics.py still directly constructs/resolves repository: {call}")
        else:
            print(f"- PASS diagnostics.py excludes {call}")

    required_router_tokens = (
        "from app.services.diagnostic_domain_service import",
        "DiagnosticDomainService",
        "get_diagnostic_domain_service",
    )
    for token in required_router_tokens:
        if token in diagnostics_source:
            print(f"- PASS diagnostics.py contains {token}")
        else:
            failures.append(f"diagnostics.py missing required domain service token: {token}")

    for path in CRITICAL:
        ast.parse((ROOT / path).read_text(encoding="utf-8"))
        print(f"- PASS syntax {path}")

    pytest_result = run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-c",
            "pytest.ini",
            "tests/unit/test_diagnostics_dynamic_repository_boundary.py",
            "-q",
            "--no-cov",
            "--tb=short",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    print(pytest_result.stdout)
    if pytest_result.returncode == 0:
        print("- PASS diagnostics dynamic boundary unit tests")
    else:
        failures.append("diagnostics dynamic boundary unit tests failed")

    ruff = run(
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
        print("- PASS focused Ruff diagnostics dynamic boundary check")
    else:
        failures.append("focused Ruff failed")
        print(ruff.stdout)

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("- PASS diagnostics dynamic repository boundary check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
