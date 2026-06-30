#!/usr/bin/env python3
"""Validate deployment readiness documentation."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "deployment_readiness_checklist.md"

REQUIRED_SNIPPETS = (
    "make runtime-check",
    "make openapi-check",
    "make route-inventory-check",
    "make phase2-authz-closure",
    "make popia-consent-closure-check",
    "make environment-security-check",
    "Azure Key Vault",
    "AZURE_KEY_VAULT_URL",
    "Release Evidence",
)


@dataclass(frozen=True)
class DeploymentReadinessResult:
    ok: bool
    detail: str


def run_checks() -> list[DeploymentReadinessResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    return [
        DeploymentReadinessResult(
            ok=snippet in text,
            detail=f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
        )
        for snippet in REQUIRED_SNIPPETS
    ]


def main() -> int:
    results = run_checks()
    print("Deployment readiness documentation check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
