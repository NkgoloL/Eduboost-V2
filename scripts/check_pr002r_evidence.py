#!/usr/bin/env python3
"""Verify PR-002R runtime/API contract evidence artifacts."""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    ".github/pull_request_template.md",
    ".github/workflows/openapi-drift.yml",
    ".github/workflows/runtime-contract.yml",
    "Makefile",
    "audits/reports/PR_INTEGRATION_SUMMARY.md",
    "docs/api_versioning_policy.md",
    "docs/error_contract.md",
    "docs/openapi.json",
    "docs/pr/PR-002R_BACKEND_RUNTIME_API_CONTRACT.md",
    "docs/project_status.md",
    "docs/release/PR-002R_EVIDENCE.md",
    "docs/route_inventory.md",
    "docs/testing/pytest_import_path.md",
    "scripts/check_runtime_entrypoints.py",
    "scripts/generate_openapi.py",
    "scripts/generate_route_inventory.py",
    "tests/conftest.py",
    "tests/test_entrypoints.py",
    "tests/test_legacy_route_exclusion.py",
    "tests/unit/test_api_v2_envelope.py",
    "tests/unit/test_check_runtime_entrypoints.py",
    "tests/unit/test_exception_envelopes.py",
    "tests/unit/test_generate_openapi.py",
    "tests/unit/test_generate_route_inventory.py",
    "tests/unit/test_openapi_ci_contract.py",
    "tests/unit/test_pr002r_docs_contract.py",
    "tests/unit/test_pr002r_governance_contract.py",
    "tests/unit/test_pytest_import_path.py",
)

CONTENT_REQUIREMENTS = {
    ".github/pull_request_template.md": (
        "Runtime/API Contract Checklist",
        "make runtime-check",
        "make openapi-check",
        "make route-inventory-check",
        "Security and POPIA Checklist",
    ),
    "docs/pr/PR-002R_BACKEND_RUNTIME_API_CONTRACT.md": (
        "app.api_v2:app",
        "docs/openapi.json",
        "docs/route_inventory.md",
        "scripts/check_runtime_entrypoints.py",
    ),
    "docs/release/PR-002R_EVIDENCE.md": (
        "PR-002R",
        "app.api_v2:app",
        "make runtime-check",
        "make openapi-check",
        "make route-inventory-check",
        "does not approve production or public beta use",
    ),
    "docs/route_inventory.md": (
        "EduBoost V2 Route Inventory",
        "Canonical runtime: `app.api_v2:app`",
        "Legacy route prefixes present in canonical runtime: `no`",
    ),
    "docs/openapi.json": (
        '"/api/v2',
        '"/v2',
    ),
    "docs/testing/pytest_import_path.md": (
        "tests/conftest.py",
        "repository root",
    ),
    "Makefile": (
        "runtime-check:",
        "openapi-check:",
        "route-inventory-check:",
    ),
}


@dataclass(frozen=True)
class EvidenceResult:
    path: str
    ok: bool
    kind: str
    message: str


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def check_required_files() -> list[EvidenceResult]:
    results: list[EvidenceResult] = []

    for path in REQUIRED_FILES:
        exists = (REPO_ROOT / path).exists()
        results.append(
            EvidenceResult(
                path=path,
                ok=exists,
                kind="file",
                message="present" if exists else "missing",
            )
        )

    return results


def check_content_requirements() -> list[EvidenceResult]:
    results: list[EvidenceResult] = []

    for path, needles in CONTENT_REQUIREMENTS.items():
        file_path = REPO_ROOT / path
        if not file_path.exists():
            results.append(
                EvidenceResult(
                    path=path,
                    ok=False,
                    kind="content",
                    message="file missing; content not checked",
                )
            )
            continue

        content = _read(path)
        for needle in needles:
            results.append(
                EvidenceResult(
                    path=path,
                    ok=needle in content,
                    kind="content",
                    message=f"contains {needle!r}" if needle in content else f"missing {needle!r}",
                )
            )

    return results


def check_all() -> list[EvidenceResult]:
    return [*check_required_files(), *check_content_requirements()]


def render_text(results: list[EvidenceResult]) -> str:
    lines = ["PR-002R evidence check"]

    for result in results:
        status = "PASS" if result.ok else "FAIL"
        lines.append(f"- {status} [{result.kind}] {result.path}: {result.message}")

    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify PR-002R evidence artifacts.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    results = check_all()

    if args.json:
        print(json.dumps([asdict(result) for result in results], indent=2, sort_keys=True))
    else:
        print(render_text(results), end="")

    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
