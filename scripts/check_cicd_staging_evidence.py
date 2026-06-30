#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    ".github/workflows/ci-cd.yml",
    ".github/workflows/cluster-d-ci.yml",
    ".github/workflows/release.yml",
    "docker/Dockerfile.api",
    "docker/Dockerfile.frontend",
    "docker-compose.yml",
    "docker-compose.prod.yml",
    "k8s/api-deployment.yml",
    "docs/environment_variables.md",
    "docs/secrets.md",
    "docs/operations/deployment_readiness_checklist.md",
    "docs/operations/deployment_runbook.md",
    "docs/operations/staging_release_gate.md",
    "docs/operations/post_deploy_staging_smoke_checklist.md",
    "scripts/check_environment_security_contract.py",
    "scripts/check_deployment_readiness_docs.py",
    "scripts/check_staging_release_gate.py",
    "scripts/staging_smoke.py",
)


@dataclass(frozen=True)
class Result:
    target: str
    ok: bool
    detail: str


def check_all() -> list[Result]:
    return [Result(p, (ROOT / p).exists(), "present" if (ROOT / p).exists() else "missing") for p in REQUIRED]


def main() -> int:
    results = check_all()
    print("CI/CD staging evidence check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'} {result.target}: {result.detail}")
    return 0 if all(r.ok for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
