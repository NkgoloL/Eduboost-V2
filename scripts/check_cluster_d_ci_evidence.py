#!/usr/bin/env python3
"""Validate Cluster D CI/deployment/environment evidence."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "scripts/check_environment_security_contract.py",
    "scripts/check_deployment_readiness_docs.py",
    "docs/security/environment_security_contract.md",
    "docs/operations/deployment_readiness_checklist.md",
    "tests/unit/test_environment_security_contract.py",
    "tests/unit/test_deployment_readiness_docs.py",
)

CONTENT_REQUIREMENTS = {
    "Makefile": (
        "environment-security-check:",
        "deployment-readiness-docs-check:",
    ),
    "app/core/config.py": (
        "def is_production(self) -> bool:",
        "AZURE_KEY_VAULT_URL is required when APP_ENV is production",
    ),
    "docs/operations/deployment_readiness_checklist.md": (
        "make popia-consent-closure-check",
        "make environment-security-check",
        "Release Evidence",
    ),
}


@dataclass(frozen=True)
class ClusterDResult:
    category: str
    target: str
    ok: bool
    detail: str


def run_checks() -> list[ClusterDResult]:
    results: list[ClusterDResult] = []

    for rel_path in REQUIRED_FILES:
        path = REPO_ROOT / rel_path
        results.append(
            ClusterDResult(
                "file",
                rel_path,
                path.exists(),
                "present" if path.exists() else "missing",
            )
        )

    for rel_path, snippets in CONTENT_REQUIREMENTS.items():
        path = REPO_ROOT / rel_path
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        for snippet in snippets:
            results.append(
                ClusterDResult(
                    "content",
                    rel_path,
                    snippet in text,
                    f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
                )
            )

    return results


def main() -> int:
    results = run_checks()
    print("Cluster D CI/deployment evidence check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} [{result.category}] {result.target}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
