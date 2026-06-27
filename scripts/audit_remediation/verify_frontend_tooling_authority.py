#!/usr/bin/env python3
"""Static verifier for Phase 03 frontend/tooling authority wiring."""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_PACKAGE = REPO_ROOT / "app" / "frontend" / "package.json"
ROOT_PACKAGE = REPO_ROOT / "package.json"
FRONTEND_LOCKFILE = REPO_ROOT / "app" / "frontend" / "pnpm-lock.yaml"
FORBIDDEN_LOCKFILES = (
    REPO_ROOT / "package-lock.json",
    REPO_ROOT / "app" / "frontend" / "package-lock.json",
    REPO_ROOT / "yarn.lock",
    REPO_ROOT / "app" / "frontend" / "yarn.lock",
)
REQUIRED_FILES = (
    REPO_ROOT / "docs" / "roadmap" / "execution" / "technical_audit_remediation" / "03_frontend_tooling_authority.md",
    REPO_ROOT / "scripts" / "audit_remediation" / "run_frontend_tooling_authority.py",
    REPO_ROOT / "scripts" / "audit_remediation" / "verify_frontend_tooling_authority.py",
    REPO_ROOT / "scripts" / "audit_remediation" / "verify_frontend_tooling_evidence.py",
    REPO_ROOT / "scripts" / "audit_remediation" / "collect_frontend_tooling_authority_evidence.sh",
    REPO_ROOT / "tests" / "unit" / "audit_remediation" / "test_frontend_tooling_authority.py",
)
REQUIRED_FRONTEND_SCRIPTS = ("env-check", "type-check", "lint", "test")


@dataclass(frozen=True)
class Check:
    name: str
    valid: bool
    detail: str


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def run_checks() -> list[Check]:
    checks: list[Check] = []
    for path in REQUIRED_FILES:
        checks.append(Check(str(path.relative_to(REPO_ROOT)), path.exists(), "present" if path.exists() else "missing"))

    checks.append(Check("root package.json", ROOT_PACKAGE.exists(), "present" if ROOT_PACKAGE.exists() else "missing"))
    checks.append(Check("frontend package.json", FRONTEND_PACKAGE.exists(), "present" if FRONTEND_PACKAGE.exists() else "missing"))
    checks.append(Check("frontend pnpm-lock.yaml", FRONTEND_LOCKFILE.exists(), "present" if FRONTEND_LOCKFILE.exists() else "missing"))

    root_pkg = _load_json(ROOT_PACKAGE) if ROOT_PACKAGE.exists() else {}
    frontend_pkg = _load_json(FRONTEND_PACKAGE) if FRONTEND_PACKAGE.exists() else {}
    root_pm = str(root_pkg.get("packageManager", ""))
    frontend_pm = str(frontend_pkg.get("packageManager", ""))
    checks.append(Check("root packageManager", root_pm.startswith("pnpm@"), root_pm or "missing"))
    checks.append(Check("frontend packageManager", frontend_pm.startswith("pnpm@"), frontend_pm or "missing"))

    scripts = frontend_pkg.get("scripts") if isinstance(frontend_pkg, dict) else {}
    if not isinstance(scripts, dict):
        scripts = {}
    for script in REQUIRED_FRONTEND_SCRIPTS:
        checks.append(Check(f"frontend script {script}", script in scripts, "present" if script in scripts else "missing"))

    for path in FORBIDDEN_LOCKFILES:
        checks.append(Check(str(path.relative_to(REPO_ROOT)), not path.exists(), "absent" if not path.exists() else "forbidden lockfile present"))

    runner_text = (REPO_ROOT / "scripts" / "audit_remediation" / "run_frontend_tooling_authority.py").read_text(encoding="utf-8") if (REPO_ROOT / "scripts" / "audit_remediation" / "run_frontend_tooling_authority.py").exists() else ""
    for snippet in ("pnpm_install_frozen_lockfile", "frontend_env_check", "frontend_type_check", "frontend_lint", "frontend_vitest"):
        checks.append(Check(f"runner step {snippet}", snippet in runner_text, "present" if snippet in runner_text else "missing"))

    return checks


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(list(argv) if argv is not None else None)
    checks = run_checks()
    payload = {"valid": all(check.valid for check in checks), "checks": [asdict(check) for check in checks]}
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        for check in checks:
            print(f"{'PASS' if check.valid else 'FAIL'} {check.name}: {check.detail}")
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
